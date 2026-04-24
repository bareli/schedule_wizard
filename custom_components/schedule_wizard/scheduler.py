"""Scheduler running inside the HA event loop."""
from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from .const import (
    DAY_BITS,
    SIGNAL_STATE_CHANGED,
    SUPPORTED_DOMAINS,
)
from .storage import WizardStore

LOG = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, hass: HomeAssistant, store: WizardStore, options: dict):
        self.hass = hass
        self.store = store
        self.options = options
        self._unsub_minute = None
        self._unsub_calendar = None
        self._active: dict[str, dict] = {}
        self._active_cycles: dict[str, dict] = {}
        self._known_calendar_events: set[str] = set()

    @property
    def active(self) -> dict[str, dict]:
        return self._active

    @property
    def active_cycles(self) -> dict[str, dict]:
        return self._active_cycles

    async def async_start(self) -> None:
        self._unsub_minute = async_track_time_change(
            self.hass, self._on_minute, second=0
        )
        poll = int(self.options.get("poll_interval", 60))
        self._unsub_calendar = async_track_time_interval(
            self.hass, self._on_calendar_poll, timedelta(seconds=max(10, poll))
        )
        await self._async_restore_active_runs()
        LOG.info("scheduler started (poll every %ss, restored %d active runs)",
                 poll, len(self._active))

    async def _async_restore_active_runs(self) -> None:
        now = int(time.time())
        on_states = {"on", "open", "opening", "active"}
        for run in self.store.active_runs:
            entity_id = run.get("entity_id")
            if not entity_id:
                continue
            try:
                ends_at = int(run.get("ends_at", 0))
            except (TypeError, ValueError):
                continue
            remaining = ends_at - now
            state = self.hass.states.get(entity_id)
            is_on = bool(state and state.state in on_states)

            if remaining <= 0:
                if is_on:
                    await self._call_service_off(entity_id)
                await self.store.async_record_run(
                    entity_id,
                    run.get("source", "manual"),
                    int(run.get("duration_min", 0)),
                    "expired_during_downtime",
                )
                continue

            if not is_on:
                await self.store.async_record_run(
                    entity_id,
                    run.get("source", "manual"),
                    int(run.get("duration_min", 0)),
                    "cancelled_during_downtime",
                )
                continue

            unsub = async_call_later(self.hass, remaining, self._make_close_callback(entity_id))
            self._active[entity_id] = {
                "entity_id": entity_id,
                "started_at": int(run.get("started_at", now - (run.get("duration_min", 0) * 60 - remaining))),
                "ends_at": ends_at,
                "duration_min": int(run.get("duration_min", 0)),
                "source": run.get("source", "manual"),
                "note": run.get("note", "restored"),
                "unsub_close": unsub,
            }
        await self._async_persist_active()
        if self._active:
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    async def _async_persist_active(self) -> None:
        runs = [
            {k: v for k, v in r.items() if k != "unsub_close"}
            for r in self._active.values()
        ]
        await self.store.async_set_active_runs(runs)

    async def async_stop(self) -> None:
        if self._unsub_minute:
            self._unsub_minute()
            self._unsub_minute = None
        if self._unsub_calendar:
            self._unsub_calendar()
            self._unsub_calendar = None
        for active in list(self._active.values()):
            unsub = active.get("unsub_close")
            if unsub:
                unsub()
        self._active.clear()
        for cyc in list(self._active_cycles.values()):
            task = cyc.get("task")
            if task and not task.done():
                task.cancel()
        self._active_cycles.clear()

    @callback
    def _on_minute(self, now: datetime) -> None:
        local = dt_util.as_local(now)
        weekday = local.weekday()
        bit = DAY_BITS[weekday]
        hhmm = local.strftime("%H:%M")
        for sched in self.store.schedules:
            if not sched.get("enabled"):
                continue
            if not (int(sched.get("days_mask", 0)) & bit):
                continue
            if sched.get("time_hhmm") != hhmm:
                continue

            cycle_id = sched.get("cycle_id") or ""
            if cycle_id:
                cycle = self.store.get_cycle(cycle_id)
                if not cycle or not cycle.get("enabled"):
                    continue
                if cycle_id in self._active_cycles:
                    LOG.debug("skip schedule %s: cycle %s already running", sched["id"], cycle_id)
                    continue
                if self._should_skip_for_rain():
                    LOG.info("skip schedule %s (cycle): rain condition active", sched["id"])
                    self.hass.async_create_task(
                        self.store.async_record_run(
                            cycle_id, "schedule", 0,
                            "skipped_rain", f"schedule:{sched['id']}"
                        )
                    )
                    self.hass.async_create_task(self._notify(
                        "skipped_rain",
                        "Schedule Wizard",
                        f"Skipped cycle {cycle.get('name', cycle_id)} — rain active",
                    ))
                    continue
                self.hass.async_create_task(
                    self.async_run_cycle(cycle_id, source="schedule", note=f"schedule:{sched['id']}")
                )
                continue

            valve_entity = sched.get("valve_entity_id")
            valve = self.store.get_valve(valve_entity) if valve_entity else None
            if not valve or not valve.get("enabled"):
                continue
            if valve_entity in self._active:
                LOG.debug("skip schedule %s: valve %s already running", sched["id"], valve_entity)
                continue
            if self._should_skip_for_rain():
                LOG.info("skip schedule %s: rain condition active", sched["id"])
                self.hass.async_create_task(
                    self.store.async_record_run(
                        valve_entity, "schedule", int(sched.get("duration_min", 10)),
                        "skipped_rain", f"schedule:{sched['id']}"
                    )
                )
                self.hass.async_create_task(self._notify(
                    "skipped_rain",
                    "Schedule Wizard",
                    f"Skipped {self._entity_label(valve_entity)} — rain active",
                ))
                continue
            self.hass.async_create_task(
                self.async_run_valve(
                    valve_entity,
                    int(sched.get("duration_min", 10)),
                    source="schedule",
                    note=f"schedule:{sched['id']}",
                )
            )

    async def _on_calendar_poll(self, _now: datetime) -> None:
        cal = self.options.get("calendar_entity") or ""
        if not cal:
            return
        lookahead = int(self.options.get("calendar_lookahead_min", 10))
        try:
            response = await self.hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": cal,
                    "duration": {"minutes": lookahead},
                },
                blocking=True,
                return_response=True,
            )
        except Exception as e:
            LOG.warning("calendar get_events failed: %s", e)
            return

        cal_data = (response or {}).get(cal) or {}
        events = cal_data.get("events", [])
        if not events:
            return

        now_ts = int(time.time())
        valves = [v for v in self.store.valves if v.get("enabled")]
        new_keys: set[str] = set()

        for ev in events:
            summary = (ev.get("summary") or "").strip()
            if not summary:
                continue
            start_str = ev.get("start", "")
            end_str = ev.get("end", "")
            description = (ev.get("description") or "").strip()

            try:
                start_ts = self._parse_time(start_str)
            except Exception:
                continue

            if start_ts > now_ts + lookahead * 60:
                continue
            if start_ts < now_ts - 60:
                continue

            key = f"{summary}|{start_str}"
            new_keys.add(key)
            if key in self._known_calendar_events:
                continue

            cycles = [c for c in self.store.cycles if c.get("enabled")]
            cycle = self._match_cycle(summary, cycles)
            if cycle:
                if cycle["id"] in self._active_cycles:
                    continue
                delay = max(0, start_ts - now_ts)
                if delay == 0:
                    self.hass.async_create_task(
                        self.async_run_cycle(cycle["id"], source="calendar", note=key)
                    )
                else:
                    async_call_later(self.hass, delay, self._make_cycle_callback(cycle["id"], key))
                continue

            valve = self._match_valve(summary, valves)
            if not valve:
                LOG.debug("no valve or cycle match for calendar event '%s'", summary)
                continue

            duration = self._parse_duration(description, end_str, start_ts)
            if duration <= 0:
                duration = int(valve["default_duration_min"])

            if valve["entity_id"] in self._active:
                continue

            delay = max(0, start_ts - now_ts)
            if delay == 0:
                self.hass.async_create_task(
                    self.async_run_valve(valve["entity_id"], duration, source="calendar", note=key)
                )
            else:
                async_call_later(self.hass, delay, self._make_calendar_callback(valve["entity_id"], duration, key))

        self._known_calendar_events = new_keys

    @staticmethod
    def _match_cycle(summary: str, cycles: list[dict]) -> Optional[dict]:
        s = summary.lower()
        best, best_len = None, 0
        for c in cycles:
            name = (c.get("name") or "").lower().strip()
            if name and name in s and len(name) > best_len:
                best, best_len = c, len(name)
        return best

    def _make_cycle_callback(self, cycle_id: str, key: str):
        async def _fire(_now):
            if cycle_id in self._active_cycles:
                return
            await self.async_run_cycle(cycle_id, source="calendar", note=key)
        return _fire

    def _make_calendar_callback(self, entity_id: str, duration: int, key: str):
        async def _fire(_now):
            if entity_id in self._active:
                return
            await self.async_run_valve(entity_id, duration, source="calendar", note=key)
        return _fire

    @staticmethod
    def _parse_time(value: str) -> int:
        if not value:
            raise ValueError("empty")
        v = value.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(v)
        except ValueError:
            dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
        if dt.tzinfo is None:
            tz = getattr(dt_util, "get_default_time_zone", None)
            tz = tz() if callable(tz) else getattr(dt_util, "DEFAULT_TIME_ZONE", None)
            if tz is None:
                from datetime import timezone as _tz
                tz = _tz.utc
            dt = dt.replace(tzinfo=tz)
        return int(dt.timestamp())

    @staticmethod
    def _parse_duration(description: str, end_str: str, start_ts: int) -> int:
        if description:
            m = re.search(r"\b(\d{1,4})\b", description)
            if m:
                return int(m.group(1))
        if end_str:
            try:
                end_ts = Scheduler._parse_time(end_str)
                diff = (end_ts - start_ts) // 60
                if diff > 0:
                    return int(diff)
            except Exception:
                pass
        return 0

    @staticmethod
    def _match_valve(summary: str, valves: list[dict]) -> Optional[dict]:
        s = summary.lower()
        best, best_len = None, 0
        for v in valves:
            label = (v.get("label") or "").lower().strip()
            if label and label in s and len(label) > best_len:
                best, best_len = v, len(label)
        if best:
            return best
        for v in valves:
            if v["entity_id"].lower() in s:
                return v
        return None

    def _notify_targets(self) -> list[str]:
        targets = self.options.get("notify_targets") or []
        if isinstance(targets, str):
            targets = [t.strip() for t in targets.split(",") if t.strip()]
        return [t for t in targets if isinstance(t, str) and t]

    def _notify_events_enabled(self) -> set[str]:
        evs = self.options.get("notify_events") or []
        if isinstance(evs, str):
            evs = [e.strip() for e in evs.split(",") if e.strip()]
        return set(evs)

    async def _notify(self, event: str, title: str, message: str) -> None:
        if event not in self._notify_events_enabled():
            return
        targets = self._notify_targets()
        if not targets:
            return
        for target in targets:
            try:
                await self.hass.services.async_call(
                    "notify", target,
                    {"title": title, "message": message},
                    blocking=False,
                )
            except Exception as e:
                LOG.warning("notify %s failed: %s", target, e)

    def _entity_label(self, entity_id: str) -> str:
        valve = self.store.get_valve(entity_id)
        if valve and valve.get("label"):
            return valve["label"]
        state = self.hass.states.get(entity_id)
        if state and state.attributes.get("friendly_name"):
            return state.attributes["friendly_name"]
        return entity_id

    def _should_skip_for_rain(self) -> bool:
        entity_id = (self.options.get("rain_entity") or "").strip()
        if not entity_id:
            return False
        state = self.hass.states.get(entity_id)
        if not state:
            return False
        threshold = self.options.get("rain_threshold")
        attribute = (self.options.get("rain_attribute") or "").strip()
        if attribute and threshold is not None:
            try:
                value = float(state.attributes.get(attribute, 0))
                return value >= float(threshold)
            except (TypeError, ValueError):
                return False
        if threshold is not None:
            try:
                value = float(state.state)
                return value >= float(threshold)
            except (TypeError, ValueError):
                pass
        skip_states = [s.strip() for s in str(self.options.get("rain_skip_states", "")).split(",") if s.strip()]
        if skip_states:
            return state.state in skip_states
        return False

    async def async_run_valve(
        self,
        entity_id: str,
        duration_min: int,
        source: str = "manual",
        note: str = "",
    ) -> None:
        domain = entity_id.split(".")[0]
        if domain not in SUPPORTED_DOMAINS:
            raise ValueError(f"unsupported domain: {domain}")
        duration_min = max(1, int(duration_min))
        seconds = duration_min * 60

        existing = self._active.get(entity_id)
        if existing:
            unsub = existing.get("unsub_close")
            if unsub:
                unsub()
            self._active.pop(entity_id, None)

        await self._call_service_on(entity_id)
        ends_at = int(time.time()) + seconds

        unsub = async_call_later(self.hass, seconds, self._make_close_callback(entity_id))
        self._active[entity_id] = {
            "entity_id": entity_id,
            "started_at": int(time.time()),
            "ends_at": ends_at,
            "duration_min": duration_min,
            "source": source,
            "note": note,
            "unsub_close": unsub,
        }
        await self.store.async_record_run(entity_id, source, duration_min, "started", note)
        await self._async_persist_active()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        LOG.info("started %s for %dm (source=%s)", entity_id, duration_min, source)
        label = self._entity_label(entity_id)
        self.hass.async_create_task(self._notify(
            "valve_start",
            "Schedule Wizard",
            f"Opened {label} for {duration_min} min ({source})",
        ))

    def _make_close_callback(self, entity_id: str):
        async def _fire(_now):
            await self._async_complete(entity_id, "completed")
        return _fire

    async def _async_complete(self, entity_id: str, status: str, note: str = "") -> None:
        active = self._active.pop(entity_id, None)
        if not active:
            return
        await self._call_service_off(entity_id)
        await self.store.async_record_run(
            entity_id,
            active.get("source", "manual"),
            active.get("duration_min", 0),
            status,
            note or active.get("note", ""),
        )
        await self._async_persist_active()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        label = self._entity_label(entity_id)
        self.hass.async_create_task(self._notify(
            "valve_end",
            "Schedule Wizard",
            f"Closed {label} ({status})",
        ))

    async def async_run_cycle(self, cycle_id: str, source: str = "manual", note: str = "") -> dict:
        cycle = self.store.get_cycle(cycle_id)
        if not cycle:
            raise ValueError("cycle not found")
        if not cycle.get("enabled") and source != "manual":
            raise ValueError("cycle disabled")
        steps = cycle.get("steps") or []
        if not steps:
            raise ValueError("cycle has no steps")

        if cycle_id in self._active_cycles:
            await self.async_stop_cycle(cycle_id, note="superseded")

        state = {
            "cycle_id": cycle_id,
            "cycle_name": cycle.get("name", ""),
            "started_at": int(time.time()),
            "step": 0,
            "total_steps": len(steps),
            "current_entity": None,
            "source": source,
            "note": note,
        }
        task = self.hass.async_create_task(self._run_cycle_task(cycle, state))
        state["task"] = task
        self._active_cycles[cycle_id] = state
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        LOG.info("started cycle %s (%s), %d steps, source=%s",
                 cycle_id, cycle.get("name"), len(steps), source)
        self.hass.async_create_task(self._notify(
            "cycle_start",
            "Schedule Wizard",
            f"Cycle started: {cycle.get('name', cycle_id)} — {len(steps)} steps ({source})",
        ))
        return {k: v for k, v in state.items() if k != "task"}

    async def _run_cycle_task(self, cycle: dict, state: dict) -> None:
        cycle_id = cycle["id"]
        current_entity: Optional[str] = None
        steps = cycle.get("steps") or []
        try:
            for i, step in enumerate(steps):
                if cycle_id not in self._active_cycles:
                    return
                entity_id = step.get("entity_id")
                duration = int(step.get("duration_min", 1))
                if not entity_id or duration <= 0:
                    continue
                self._active_cycles[cycle_id]["step"] = i + 1
                self._active_cycles[cycle_id]["current_entity"] = entity_id
                async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
                try:
                    await self.async_run_valve(
                        entity_id, duration,
                        source=f"cycle:{cycle_id}",
                        note=f"{state.get('note','')}|step{i+1}",
                    )
                except Exception as e:
                    LOG.warning("cycle %s step %d failed: %s", cycle_id, i + 1, e)
                    continue
                current_entity = entity_id
                try:
                    await asyncio.sleep(duration * 60)
                except asyncio.CancelledError:
                    raise
                current_entity = None
            await self.store.async_record_run(
                cycle_id, state.get("source", "manual"), 0,
                "cycle_completed", state.get("note", ""),
            )
            self.hass.async_create_task(self._notify(
                "cycle_end",
                "Schedule Wizard",
                f"Cycle completed: {cycle.get('name', cycle_id)}",
            ))
        except asyncio.CancelledError:
            if current_entity:
                try:
                    await self.async_stop_valve(current_entity)
                except Exception as e:
                    LOG.warning("stop step valve failed: %s", e)
            await self.store.async_record_run(
                cycle_id, state.get("source", "manual"), 0,
                "cycle_cancelled", state.get("note", ""),
            )
            self.hass.async_create_task(self._notify(
                "cycle_end",
                "Schedule Wizard",
                f"Cycle cancelled: {cycle.get('name', cycle_id)}",
            ))
        finally:
            self._active_cycles.pop(cycle_id, None)
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    async def async_stop_cycle(self, cycle_id: str, note: str = "manual stop") -> None:
        state = self._active_cycles.get(cycle_id)
        if not state:
            return
        task: Optional[asyncio.Task] = state.get("task")
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._active_cycles.pop(cycle_id, None)

    async def async_stop_valve(self, entity_id: str) -> None:
        active = self._active.get(entity_id)
        if active:
            unsub = active.get("unsub_close")
            if unsub:
                unsub()
            await self._async_complete(entity_id, "cancelled", "manual stop")
            return
        await self._call_service_off(entity_id)

    async def _call_service_on(self, entity_id: str) -> None:
        domain = entity_id.split(".")[0]
        service = "open_cover" if domain == "cover" else (
            "open_valve" if domain == "valve" else "turn_on"
        )
        await self.hass.services.async_call(domain, service, {"entity_id": entity_id}, blocking=True)

    async def _call_service_off(self, entity_id: str) -> None:
        domain = entity_id.split(".")[0]
        service = "close_cover" if domain == "cover" else (
            "close_valve" if domain == "valve" else "turn_off"
        )
        try:
            await self.hass.services.async_call(domain, service, {"entity_id": entity_id}, blocking=True)
        except Exception as e:
            LOG.warning("close %s failed: %s", entity_id, e)
