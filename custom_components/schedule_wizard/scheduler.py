"""Scheduler running inside the HA event loop."""
from __future__ import annotations

import asyncio
import logging
import math
import re
import time
from datetime import date, datetime, timedelta
from typing import Any, Callable, Optional

from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_MAX_EXTERNAL_MINUTES,
    DOMAIN,
    EVENT_CONDITION_SKIPPED,
    EVENT_CYCLE_ENDED,
    EVENT_CYCLE_PAUSED,
    EVENT_CYCLE_RESUMED,
    EVENT_CYCLE_SKIPPED_OVERLAP,
    EVENT_CYCLE_STARTED,
    EVENT_LEAK_DETECTED,
    EVENT_LOW_FLOW,
    FLOW_UNIT_TO_LPM,
    LOW_FLOW_MIN_MINUTES,
    LOW_FLOW_MIN_RUNS,
    LOW_FLOW_RATIO,
    EVENT_MOISTURE_SKIPPED,
    EVENT_RAIN_SKIPPED,
    EVENT_SEASONAL_SKIPPED,
    EVENT_VALVE_ENDED,
    EVENT_VALVE_FAILED,
    EVENT_VALVE_SOAKING,
    EVENT_VALVE_STARTED,
    FORECAST_MAX_AGE_SECONDS,
    FORECAST_REFRESH_MINUTES,
    MAX_RUN_MINUTES,
    NOTIFICATION_ACTION_PREFIX,
    RESUME_MAX_GAP_SECONDS,
    SIGNAL_STATE_CHANGED,
    SUPPORTED_DOMAINS,
)
from . import planner
from .notify_text import APP_TITLE, fmt_number, notify_text
from .storage import WizardStore

LOG = logging.getLogger(__name__)

ON_STATES = {"on", "open", "opening", "active"}
# Calendar names shorter than this only match an event whose whole summary is the name (#38).
CALENDAR_MIN_WORD_MATCH = 3
UNAVAILABLE_STATES = {"unavailable", "unknown", ""}

SKIP_EVENTS = {
    "rain": EVENT_RAIN_SKIPPED,
    "forecast": EVENT_RAIN_SKIPPED,
    "rain_delay": EVENT_RAIN_SKIPPED,
    "moisture": EVENT_MOISTURE_SKIPPED,
    "condition": EVENT_CONDITION_SKIPPED,
    "seasonal_zero": EVENT_SEASONAL_SKIPPED,
}
SKIP_TEXT = {
    "rain": "rain active",
    "forecast": "rain forecast",
    "rain_delay": "rain delay active",
    "moisture": "soil moisture above threshold",
    "condition": "schedule condition not met",
    "seasonal_zero": "temperature adjustment 0 % (too cool)",
}
# Same words as the panel's status.skipped_seasonal_zero (tests/test_i18n.py keeps them equal).
SEASONAL_SKIP_TEXT = {
    "en": "skipped: temperature adjustment 0 % (too cool)",
    "de": "übersprungen: Temperaturanpassung 0 % (zu kühl)",
    "he": "דולג: התאמת טמפרטורה 0% (קר מדי)",
    "es": "omitido: ajuste por temperatura 0 % (demasiado fresco)",
    "fr": "ignoré : ajustement à la température 0 % (trop frais)",
    "it": "saltato: regolazione temperatura 0 % (troppo freddo)",
    "nl": "overgeslagen: temperatuuraanpassing 0 % (te koel)",
    "pt": "ignorado: ajuste por temperatura 0 % (demasiado frio)",
    "ru": "пропущено: поправка по температуре 0 % (слишком прохладно)",
    "uk": "пропущено: поправка за температурою 0 % (надто прохолодно)",
    "pl": "pominięto: korekta temperaturowa 0 % (za chłodno)",
    "ar": "تم التخطي: تعديل الحرارة 0% (الجو بارد جدًا)",
    "zh-hans": "已跳过:温度调整 0%(太冷)",
    "sv": "överhoppad: temperaturjustering 0 % (för svalt)",
    "da": "sprunget over: temperaturjustering 0 % (for køligt)",
    "nb": "hoppet over: temperaturjustering 0 % (for kjølig)",
    "fi": "ohitettu: lämpötilasäätö 0 % (liian viileää)",
}
NOTIFY_FOR_SKIP = {"rain_delay": "skipped_rain", "forecast": "skipped_rain", "seasonal_zero": "skipped_seasonal"}


def panel_lang(language: Optional[str]) -> str:
    """HA language code to a key of the panel's language tables (en when not translated)."""
    lang = (language or "en").lower()
    if lang in ("zh", "zh-hans", "zh-cn", "zh-sg"):
        return "zh-hans"
    base = lang.split("-")[0]
    if base in ("no", "nn"):
        base = "nb"
    return base if base in SEASONAL_SKIP_TEXT else "en"


def _is_iso_day(value: str) -> bool:
    """A real calendar date written YYYY-MM-DD."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def seasonal_percent(factor: float) -> int:
    """Factor as the whole percent the panel shows: half rounds up, like JS Math.round (#29)."""
    return int(math.floor(factor * 100 + 0.5 + 1e-9))


class Scheduler:
    def __init__(self, hass: HomeAssistant, store: WizardStore, options: dict):
        self.hass = hass
        self.store = store
        self.options = options
        self._unsub_minute = None
        self._unsub_calendar = None
        self._unsub_flow = None
        self._flow_timer = None
        self._flow_alert: Optional[str] = None
        self._poll_seconds = 0
        self._calendar_entity = ""
        self._active: dict[str, dict] = {}
        self._active_cycles: dict[str, dict] = {}
        self._soak: dict[str, dict] = {}
        self._known_calendar_events: set[str] = set()
        self._calendar_pending: dict[str, tuple[int, Optional[Callable]]] = {}
        self._restore_watch: dict[str, Callable] = {}
        self._master_open = False
        self._master_lock = asyncio.Lock()
        self._unsub_action = None
        self._unsub_forecast = None
        self._forecast: dict[str, Any] = {"mm": None, "updated": 0, "kind": None, "error": None}
        self._stopping = False
        self._unsub_ha_stop = None
        self._flow_last: Optional[tuple[float, float]] = None

    @property
    def active(self) -> dict[str, dict]:
        return self._active

    @property
    def active_cycles(self) -> dict[str, dict]:
        return self._active_cycles

    @property
    def soaking(self) -> list[dict]:
        return [{k: v for k, v in s.items() if k != "task"} for s in self._soak.values()]

    @property
    def flow_status(self) -> dict:
        entity_id = (self.options.get("flow_entity") or "").strip()
        return {
            "entity_id": entity_id,
            "value": self._flow_value() if entity_id else None,
            "alert": self._flow_alert,
        }

    # ------------------------------------------------------------------ lifecycle

    async def async_start(self) -> None:
        self._unsub_minute = async_track_time_change(
            self.hass, self._on_minute, second=0
        )
        self._calendar_entity = self.options.get("calendar_entity") or ""
        self._arm_calendar()
        await self._async_restore_active_runs()
        await self._async_restore_cycles()
        self._arm_flow()
        self._arm_forecast()
        self._unsub_action = self.hass.bus.async_listen(
            "mobile_app_notification_action", self._on_notification_action
        )
        self._unsub_ha_stop = self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._on_ha_stop)
        await self.store.async_prune_skips(dt_util.now().date().isoformat())
        LOG.info("scheduler started (poll every %ss, restored %d active runs)",
                 self._poll_seconds, len(self._active))

    def _arm_calendar(self) -> None:
        if self._unsub_calendar:
            self._unsub_calendar()
        self._poll_seconds = max(10, int(self.options.get("poll_interval") or 60))
        self._unsub_calendar = async_track_time_interval(
            self.hass, self._on_calendar_poll, timedelta(seconds=self._poll_seconds)
        )

    @callback
    def async_options_updated(self) -> None:
        """Apply changed options without reloading, so running cycles survive."""
        if max(10, int(self.options.get("poll_interval") or 60)) != self._poll_seconds:
            self._arm_calendar()
        calendar = self.options.get("calendar_entity") or ""
        if calendar != self._calendar_entity:
            self._calendar_entity = calendar
            self._cancel_calendar_pending()
            self._known_calendar_events = set()
        self._arm_flow()
        self._arm_forecast()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    def _cancel_calendar_pending(self) -> None:
        for _start, unsub in self._calendar_pending.values():
            if unsub:
                unsub()
        self._calendar_pending.clear()

    async def _async_restore_active_runs(self) -> None:
        now = int(time.time())
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
            # The valve's own integration may not have loaded yet (#54): no state, unknown or unavailable.
            available = state is not None and state.state not in UNAVAILABLE_STATES
            is_on = available and state.state in ON_STATES

            if available and remaining <= 0:
                await self._call_service_off(entity_id)
                await self.store.async_record_run(
                    entity_id,
                    run.get("source", "manual"),
                    int(run.get("duration_min", 0)),
                    "expired_during_downtime",
                )
                continue

            if available and not is_on:
                await self.store.async_record_run(
                    entity_id,
                    run.get("source", "manual"),
                    int(run.get("duration_min", 0)),
                    "cancelled_during_downtime",
                )
                continue

            restored = {
                "entity_id": entity_id,
                "started_at": int(run.get("started_at", now - (int(run.get("duration_min", 0)) * 60 - remaining))),
                "ends_at": ends_at,
                "duration_min": int(run.get("duration_min", 0)),
                "source": run.get("source", "manual"),
                "note": run.get("note", "restored"),
            }
            if not available:
                # Keep the run until the valve reports a real state; close it then if it is due.
                restored["await_state"] = True
                restored["close_status"] = "expired_during_downtime" if remaining <= 0 else "completed"
                self._watch_restored(entity_id, restored)
            restored["unsub_close"] = async_call_later(
                self.hass, max(0, remaining), self._make_close_callback(entity_id, restored)
            )
            self._active[entity_id] = restored
        if self._active and (self.options.get("master_valve_entity") or "").strip():
            self._master_open = True
        await self._async_persist_active()
        if self._active:
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    def _watch_restored(self, entity_id: str, run: Optional[dict]) -> None:
        """Wait for the first real state of a valve that was not available when its run was restored.

        With run=None the run is already over: only close the valve if it comes back open.
        """
        self._unwatch_restored(entity_id)

        @callback
        def _changed(event: Event) -> None:
            new = event.data.get("new_state")
            if new is None or new.state in UNAVAILABLE_STATES:
                return
            self._unwatch_restored(entity_id)
            if run is None:
                if new.state in ON_STATES:
                    self.hass.async_create_task(self._call_service_off(entity_id))
                return
            self.hass.async_create_task(self._async_restored_available(entity_id, run, new.state))

        self._restore_watch[entity_id] = async_track_state_change_event(self.hass, [entity_id], _changed)

    def _unwatch_restored(self, entity_id: str) -> None:
        unsub = self._restore_watch.pop(entity_id, None)
        if unsub:
            unsub()

    async def _async_restored_available(self, entity_id: str, run: dict, state: str) -> None:
        if self._active.get(entity_id) is not run or not run.pop("await_state", None):
            return
        if run.pop("close_due", None):
            await self._async_complete(entity_id, run.pop("close_status", "completed"))
            return
        run.pop("close_status", None)
        if state in ON_STATES:
            # Still open: the close timer finishes the run at its original end.
            await self._async_persist_active()
            return
        # The valve came back closed: it was turned off while Home Assistant was down.
        self._active.pop(entity_id, None)
        self._cancel_run_timer(run)
        await self.store.async_record_run(
            entity_id, run.get("source", "manual"), int(run.get("duration_min", 0)), "cancelled_during_downtime",
        )
        await self._async_persist_active()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        self.hass.async_create_task(self._async_master_maybe_close())

    async def _async_persist_active(self) -> None:
        runs = [
            {k: v for k, v in r.items() if k not in ("unsub_close", "starting")}
            for r in self._active.values()
            if not r.get("starting")
        ]
        await self.store.async_set_active_runs(runs)

    @callback
    def _on_ha_stop(self, _event: Event) -> None:
        """HA is shutting down: tasks get cancelled next; leave valves and cycle state for resume."""
        self._unsub_ha_stop = None
        self._stopping = True

    async def async_stop(self) -> None:
        # Shutdown or reload: keep persisted runs and cycles so they resume on the next start.
        self._stopping = True
        for attr in ("_unsub_minute", "_unsub_calendar", "_unsub_flow", "_unsub_action", "_unsub_forecast", "_unsub_ha_stop"):
            unsub = getattr(self, attr)
            if unsub:
                unsub()
                setattr(self, attr, None)
        self._cancel_flow_timer()
        self._cancel_calendar_pending()
        for entity_id in list(self._restore_watch):
            self._unwatch_restored(entity_id)
        for active in list(self._active.values()):
            self._cancel_run_timer(active)
        self._active.clear()
        for soak in list(self._soak.values()):
            task = soak.get("task")
            if soak.get("owner") == "standalone" and task and not task.done():
                task.cancel()
        for cyc in list(self._active_cycles.values()):
            task = cyc.get("task")
            if task and not task.done():
                task.cancel()
        self._active_cycles.clear()

    # ------------------------------------------------------------------ triggers

    @callback
    def _on_minute(self, now: datetime) -> None:
        # Global rain delay is checked per trigger: indoor (rain-exempt) valves still run.
        local = dt_util.as_local(now)
        hhmm = local.strftime("%H:%M")
        today = local.date().isoformat()
        if hhmm == "00:00":
            self.hass.async_create_task(self.store.async_prune_skips(today))
        self._send_due_reminders(local)
        for sched in self.store.schedules:
            if not sched.get("enabled"):
                continue
            # Local calendar date, not elapsed seconds: every-N-days stays on time across DST changes.
            if not planner.runs_on(sched, local.date()):
                continue
            # Clock time, or today's sunrise / sunset plus the offset (#59).
            if planner.fire_hhmm(sched, local.date(), self.hass) != hhmm:
                continue
            ref = f"schedule:{sched['id']}"
            if self.store.is_skipped(sched["id"], today):
                target = planner.schedule_target(self.store, sched)
                LOG.info("skip %s: skipped by user for %s", ref, today)
                self.hass.async_create_task(self.store.async_record_run(
                    (target or {}).get("id") or sched.get("cycle_id") or sched.get("valve_entity_id") or "",
                    "schedule", 0, "skipped_manual", ref,
                ))
                self.hass.async_create_task(self.store.async_remove_skip(sched["id"], today))
                continue
            cycle_id = sched.get("cycle_id") or ""
            if cycle_id:
                self.hass.async_create_background_task(
                    self._async_trigger_cycle(cycle_id, "schedule", ref, sched),
                    f"{DOMAIN}_{ref}",
                )
            elif sched.get("valve_entity_id"):
                self.hass.async_create_background_task(
                    self._async_trigger_valve(
                        sched["valve_entity_id"], int(sched.get("duration_min", 10)),
                        "schedule", ref, sched,
                    ),
                    f"{DOMAIN}_{ref}",
                )

    # ------------------------------------------------------------------ skips / reminders

    async def async_skip_next(self, schedule_id: str) -> Optional[dict]:
        occ = planner.next_occurrence(self.store, self.options, schedule_id)
        if occ:
            await self.store.async_add_skip(schedule_id, occ["day"])
        return occ

    async def async_skip_day(self, day: Optional[str] = None) -> list[dict]:
        now = dt_util.now()
        day = day or now.date().isoformat()
        try:
            day_date = datetime.strptime(day, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError("date must be YYYY-MM-DD") from e
        day_start = dt_util.start_of_local_day(day_date)
        start = max(day_start, now) if day_date == now.date() else day_start
        occs = [
            o for o in planner.occurrences(self.store, self.options, start, day_start + timedelta(days=1))
            if o["day"] == day
        ]
        for occ in occs:
            await self.store.async_add_skip(occ["schedule_id"], day)
        return occs

    async def async_run_schedule_now(self, schedule_id: str, source: str = "manual") -> None:
        """Start a schedule's target right away (no gating), and drop today's pending run of it."""
        sched = self.store.get_schedule(schedule_id)
        target = planner.schedule_target(self.store, sched) if sched else None
        if not target:
            raise ValueError("schedule not found or disabled")
        occ = planner.next_occurrence(self.store, self.options, schedule_id, days=1)
        if occ and occ["day"] == dt_util.now().date().isoformat():
            await self.store.async_add_skip(schedule_id, occ["day"])
        if target["kind"] == "cycle":
            await self.async_run_cycle(target["id"], source=source, note=f"schedule:{schedule_id}")
        else:
            await self.async_run_valve(target["id"], target["minutes"], source=source, note=f"schedule:{schedule_id}")

    def _text(self, key: str, **params: Any) -> str:
        """A notification text in the HA language (#68)."""
        return notify_text(panel_lang(getattr(self.hass.config, "language", "en")), key, **params)

    @callback
    def _send_due_reminders(self, local: datetime) -> None:
        try:
            lead = int(self.options.get("reminder_minutes") or 0)
        except (TypeError, ValueError):
            lead = 0
        if lead <= 0 or not self._notify_targets():
            return
        start = local.replace(second=0, microsecond=0) + timedelta(minutes=lead)
        for occ in planner.occurrences(self.store, self.options, start, start + timedelta(minutes=1)):
            if occ["skip"] in ("skipped_manual", "rain_delay"):
                continue
            self.hass.async_create_task(self._async_send_reminder(occ))

    async def _async_send_reminder(self, occ: dict) -> None:
        when = dt_util.as_local(dt_util.utc_from_timestamp(occ["start"])).strftime("%H:%M")
        body = self._text("reminder_body", name=occ["name"], time=when, n=occ["minutes"])
        key = f"{occ['schedule_id']}_{occ['day']}"
        for target in self._notify_targets():
            data: dict[str, Any] = {"title": self._text("reminder_title"), "message": body}
            if target.startswith("mobile_app_"):
                data["data"] = {
                    "tag": f"schedule_wizard_{key}",
                    "actions": [
                        {"action": f"{NOTIFICATION_ACTION_PREFIX}SKIP_{key}", "title": self._text("reminder_skip")},
                        {"action": f"{NOTIFICATION_ACTION_PREFIX}RUN_{key}", "title": self._text("reminder_run")},
                    ],
                }
            try:
                await self.hass.services.async_call("notify", target, data, blocking=False)
            except Exception as e:
                LOG.warning("reminder to %s failed: %s", target, e)

    async def _on_notification_action(self, event: Event) -> None:
        action = str(event.data.get("action") or "")
        if not action.startswith(NOTIFICATION_ACTION_PREFIX):
            return
        parts = action[len(NOTIFICATION_ACTION_PREFIX):].split("_")
        if len(parts) != 3:
            return
        verb, schedule_id, day = parts
        if not self.store.get_schedule(schedule_id):
            return
        if verb == "SKIP" and not _is_iso_day(day):
            # #39: the event can come from any client; only store real YYYY-MM-DD days.
            LOG.warning("ignored notification action %s: bad day", action[:80])
            return
        try:
            if verb == "SKIP":
                await self.store.async_add_skip(schedule_id, day)
                LOG.info("schedule %s skipped for %s from a notification", schedule_id, day)
            elif verb == "RUN":
                await self.async_run_schedule_now(schedule_id, source="notification")
        except Exception as e:
            LOG.warning("notification action %s failed: %s", action, e)
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    def _is_valve_busy(self, entity_id: str) -> bool:
        return entity_id in self._active or entity_id in self._soak

    def external_cap(self) -> int:
        """#79: the longest run a webhook call or a calendar event may start (minutes)."""
        try:
            cap = int(self.options.get("max_external_minutes") or DEFAULT_MAX_EXTERNAL_MINUTES)
        except (TypeError, ValueError):
            cap = DEFAULT_MAX_EXTERNAL_MINUTES
        return max(1, min(MAX_RUN_MINUTES, cap))

    def _calendar_title(self, summary: str) -> Optional[str]:
        """#78: the part of an event title to match zones against, or None when the keyword is missing."""
        keyword = str(self.options.get("calendar_keyword") or "").strip()
        if not keyword:
            return summary
        if not summary.lower().startswith(keyword.lower()):
            return None
        return summary[len(keyword):].strip()

    async def _async_trigger_valve(
        self, entity_id: str, base_min: int, source: str, ref: str, sched: Optional[dict] = None,
        max_min: Optional[int] = None,
    ) -> None:
        """Gate and start a scheduled/calendar valve run. All checks happen at fire time."""
        try:
            valve = self.store.get_valve(entity_id)
            if not valve or not valve.get("enabled"):
                return
            if self._is_valve_busy(entity_id):
                LOG.debug("skip %s: valve %s already running", ref, entity_id)
                return
            weather = self._valve_weather_reason(valve)
            if weather == "rain_delay_global":
                return
            reason = weather or self._skip_reason(sched, valve=valve)
            if reason:
                self._record_skip(reason, "valve", entity_id, self._entity_label(entity_id),
                                  source, ref, base_min, sched)
                return
            factor = self._seasonal_factor()
            if self._seasonal_skips(factor):
                self._record_skip("seasonal_zero", "valve", entity_id, self._entity_label(entity_id),
                                  source, ref, base_min, sched)
                return
            minutes = self._scale_minutes(base_min, factor)
            note = ref + (f"|seasonal:{seasonal_percent(factor)}%" if factor != 1.0 else "")
            if max_min and minutes > max_min:
                # #79: shortened to the "Longest external run" setting; the note keeps what was asked.
                note += f"|capped:{minutes}"
                minutes = max_min
            if len(self._soak_chunks(entity_id, minutes)) > 1:
                await self._async_run_sequence(entity_id, minutes, source, note, owner="standalone")
            else:
                await self.async_run_valve(entity_id, minutes, source=source, note=note)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            LOG.warning("%s run of %s failed: %s", source, entity_id, e)

    async def _async_trigger_cycle(
        self, cycle_id: str, source: str, ref: str, sched: Optional[dict] = None,
    ) -> None:
        try:
            cycle = self.store.get_cycle(cycle_id)
            if not cycle or not cycle.get("enabled"):
                return
            # Indoor (rain-exempt) steps keep a cycle alive under global rain delay / rain;
            # the outdoor steps are then skipped one by one in _run_cycle_task.
            any_exempt = any(
                self._is_rain_exempt(self.store.get_valve(st.get("entity_id") or ""))
                for st in cycle.get("steps") or []
            )
            if self._is_rain_delay_active() and not any_exempt:
                return
            if cycle_id in self._active_cycles:
                LOG.debug("skip %s: cycle %s already running", ref, cycle_id)
                return
            if self._active_cycles and not self.options.get("allow_concurrent_cycles", False):
                running = next(iter(self._active_cycles.values()))
                LOG.info("skip %s: another cycle is already running (%s)", ref, running.get("cycle_id"))
                await self.store.async_record_run(
                    cycle_id, source, 0, "skipped_overlap",
                    f"{ref}|busy:{running.get('cycle_id')}",
                )
                self.hass.bus.async_fire(EVENT_CYCLE_SKIPPED_OVERLAP, {
                    "cycle_id": cycle_id,
                    "name": cycle.get("name", ""),
                    "source": source,
                    "schedule_id": sched["id"] if sched else "",
                    "busy_with": running.get("cycle_id"),
                })
                return
            reason = self._skip_reason(sched, check_rain=not any_exempt)
            if reason:
                self._record_skip(reason, "cycle", cycle_id, cycle.get("name", cycle_id),
                                  source, ref, 0, sched)
                return
            factor = self._seasonal_factor()
            if self._seasonal_skips(factor):
                self._record_skip("seasonal_zero", "cycle", cycle_id, cycle.get("name", cycle_id),
                                  source, ref, 0, sched)
                return
            note = ref + (f"|seasonal:{seasonal_percent(factor)}%" if factor != 1.0 else "")
            await self.async_run_cycle(cycle_id, source=source, note=note, duration_factor=factor)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            LOG.warning("%s run of cycle %s failed: %s", source, cycle_id, e)

    @staticmethod
    def _is_rain_exempt(valve: Optional[dict]) -> bool:
        return bool(valve and valve.get("rain_exempt"))

    @staticmethod
    def _valve_rain_delay_until(valve: Optional[dict]) -> int:
        try:
            until = int((valve or {}).get("rain_delay_until") or 0)
        except (TypeError, ValueError):
            return 0
        return until if until > int(time.time()) else 0

    def _valve_weather_reason(self, valve: Optional[dict]) -> Optional[str]:
        """Rain gating for one valve: its own delay always; global delay and rain skip unless indoor."""
        if self._valve_rain_delay_until(valve):
            return "rain_delay"
        if self._is_rain_exempt(valve):
            return None
        if self._is_rain_delay_active():
            return "rain_delay_global"
        if self._should_skip_for_rain():
            return "rain"
        if self._should_skip_for_forecast():
            return "forecast"
        return None

    def _skip_reason(
        self, sched: Optional[dict], valve: Optional[dict] = None, check_rain: bool = True,
    ) -> Optional[str]:
        if check_rain and valve is None and self._should_skip_for_rain():
            return "rain"
        if check_rain and valve is None and self._should_skip_for_forecast():
            return "forecast"
        per_valve = self._valve_moisture_skip(valve) if valve else None
        if per_valve is True or (per_valve is None and self._should_skip_for_moisture()):
            return "moisture"
        if sched and not self._conditions_pass(sched.get("conditions") or []):
            return "condition"
        return None

    def _record_skip(
        self, reason: str, kind: str, target: str, name: str, source: str,
        ref: str, duration_min: int, sched: Optional[dict],
    ) -> None:
        LOG.info("skip %s (%s %s): %s", ref, kind, target, SKIP_TEXT[reason])
        self.hass.async_create_task(
            self.store.async_record_run(target, source, duration_min, f"skipped_{reason}", ref)
        )
        payload = {
            "target": target,
            "kind": kind,
            "source": source,
            "schedule_id": sched["id"] if sched else "",
            "reason": reason,
        }
        payload["name" if kind == "cycle" else "label"] = name
        if reason == "seasonal_zero":
            # Same words as the panel history row "<name>: <status>" (#31), in the HA language.
            message = f"{name}: {SEASONAL_SKIP_TEXT[panel_lang(getattr(self.hass.config, 'language', 'en'))]}"
        else:
            message = self._text(f"skip_{reason}", name=name)
        payload["message"] = message
        self.hass.bus.async_fire(SKIP_EVENTS[reason], payload)
        notify_event = NOTIFY_FOR_SKIP.get(reason, f"skipped_{reason}")
        self.hass.async_create_task(self._notify(notify_event, name, message))

    # ------------------------------------------------------------------ calendar

    async def _on_calendar_poll(self, _now: datetime) -> None:
        cal = self.options.get("calendar_entity") or ""
        if not cal:
            return
        lookahead = int(self.options.get("calendar_lookahead_min") or 10)
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
        events = cal_data.get("events", []) or []

        now_ts = int(time.time())
        past_window = max(60, self._poll_seconds + 30)
        valves = [v for v in self.store.valves if v.get("enabled")]
        cycles = [c for c in self.store.cycles if c.get("enabled")]
        new_keys: set[str] = set()

        for ev in events:
            summary = (ev.get("summary") or "").strip()
            start_str = ev.get("start", "")
            if not summary or not isinstance(start_str, str) or "T" not in start_str:
                # All-day events (date only) are ignored: they would run for 24h.
                continue
            end_str = ev.get("end", "")
            description = (ev.get("description") or "").strip()

            try:
                start_ts = self._parse_time(start_str)
            except Exception:
                continue

            if start_ts > now_ts + lookahead * 60:
                continue
            if start_ts < now_ts - past_window:
                continue

            key = f"{summary}|{start_str}"
            new_keys.add(key)
            if key in self._known_calendar_events or key in self._calendar_pending:
                continue

            title = self._calendar_title(summary)
            if not title:
                LOG.debug("calendar event '%s' ignored: no calendar keyword", summary)
                continue
            cycle = self._match_cycle(title, cycles)
            if cycle:
                fire = self._make_calendar_fire(key, "cycle", cycle["id"], 0)
            else:
                valve = self._match_valve(title, valves)
                if not valve:
                    LOG.debug("no valve or cycle match for calendar event '%s'", summary)
                    continue
                duration = self._parse_duration(description, end_str if isinstance(end_str, str) else "", start_ts)
                if duration <= 0:
                    duration = int(valve["default_duration_min"])
                duration = min(duration, MAX_RUN_MINUTES)
                fire = self._make_calendar_fire(key, "valve", valve["entity_id"], duration)

            delay = max(0, start_ts - now_ts)
            if delay == 0:
                self._calendar_pending[key] = (start_ts, None)
                fire(None)
            else:
                self._calendar_pending[key] = (start_ts, async_call_later(self.hass, delay, fire))

        # Events deleted or moved in the calendar: cancel their pending triggers.
        for key, (start_ts, unsub) in list(self._calendar_pending.items()):
            if key not in new_keys and start_ts > now_ts:
                if unsub:
                    unsub()
                self._calendar_pending.pop(key, None)

        self._known_calendar_events = new_keys

    def _make_calendar_fire(self, key: str, kind: str, target: str, duration: int):
        @callback
        def _fire(_now) -> None:
            self._calendar_pending.pop(key, None)
            coro = (
                self._async_trigger_cycle(target, "calendar", key)
                if kind == "cycle"
                else self._async_trigger_valve(target, duration, "calendar", key, max_min=self.external_cap())
            )
            self.hass.async_create_background_task(coro, f"{DOMAIN}_calendar_{key}")
        return _fire

    @staticmethod
    def _summary_has(name: str, summary: str) -> bool:
        """#38: the name as whole words of the summary; a name under 3 characters must be the whole summary."""
        name = (name or "").lower().strip()
        summary = (summary or "").lower().strip()
        if not name:
            return False
        if len(name) < CALENDAR_MIN_WORD_MATCH:
            return name == summary
        return re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", summary) is not None

    @staticmethod
    def _match_cycle(summary: str, cycles: list[dict]) -> Optional[dict]:
        best, best_len = None, 0
        for c in cycles:
            name = (c.get("name") or "").strip()
            if Scheduler._summary_has(name, summary) and len(name) > best_len:
                best, best_len = c, len(name)
        return best

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
            get_tz = getattr(dt_util, "get_default_time_zone", None)
            dt = dt.replace(tzinfo=get_tz() if callable(get_tz) else dt_util.DEFAULT_TIME_ZONE)
        return int(dt.timestamp())

    @staticmethod
    def _parse_duration(description: str, end_str: str, start_ts: int) -> int:
        """Minutes from the description ("15 min", or just "15"), else end - start."""
        if description:
            m = re.search(
                r"(\d{1,4})\s*(?:minutes?|mins?|m\b|דקות|דק)", description, re.IGNORECASE
            )
            if not m:
                m = re.fullmatch(r"\s*(\d{1,4})\s*", description)
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
        best, best_len = None, 0
        for v in valves:
            label = (v.get("label") or "").strip()
            if Scheduler._summary_has(label, summary) and len(label) > best_len:
                best, best_len = v, len(label)
        if best:
            return best
        for v in valves:
            if Scheduler._summary_has(v["entity_id"], summary):
                return v
        return None

    # ------------------------------------------------------------------ notify

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
        for target in self._notify_targets():
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

    # ------------------------------------------------------------------ conditions / sensors

    def _read_numeric(self, entity_id: str, attribute: str = "") -> Optional[float]:
        state = self.hass.states.get(entity_id)
        if not state:
            return None
        try:
            if attribute:
                return float(state.attributes.get(attribute))
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _seasonal_factor(self) -> float:
        if not self.options.get("seasonal_enabled"):
            return 1.0
        entity_id = (self.options.get("seasonal_temp_entity") or "").strip()
        if not entity_id:
            return 1.0
        temp = self._read_numeric(entity_id, (self.options.get("seasonal_temp_attribute") or "").strip())
        if temp is None:
            return 1.0
        try:
            low = float(self.options.get("seasonal_temp_low", 10))
            high = float(self.options.get("seasonal_temp_high", 30))
            min_pct = float(self.options.get("seasonal_min_pct", 50))
            max_pct = float(self.options.get("seasonal_max_pct", 120))
        except (TypeError, ValueError):
            return 1.0
        if high <= low:
            return 1.0
        if temp <= low:
            pct = min_pct
        elif temp >= high:
            pct = max_pct
        else:
            t = (temp - low) / (high - low)
            pct = min_pct + t * (max_pct - min_pct)
        return max(0.0, pct / 100.0)

    @property
    def seasonal_status(self) -> dict[str, Any]:
        """Current temperature factor as the panel shows it, and whether scheduled runs are skipped (#29)."""
        factor = self._seasonal_factor()
        return {"pct": seasonal_percent(factor), "skips": self._seasonal_skips(factor)}

    @staticmethod
    def _seasonal_skips(factor: float) -> bool:
        """A factor shown as 0 % means no watering (#26); any higher factor keeps a 1-minute minimum."""
        return seasonal_percent(factor) <= 0

    @staticmethod
    def _scale_minutes(base: int, factor: float) -> int:
        if factor == 1.0:
            return int(base)
        if Scheduler._seasonal_skips(factor):
            return 0
        return max(1, int(round(base * factor)))

    def _is_rain_delay_active(self) -> int:
        try:
            until = int(self.options.get("rain_delay_until") or 0)
        except (TypeError, ValueError):
            return 0
        if until <= int(time.time()):
            return 0
        return until

    def _should_skip_for_moisture(self) -> bool:
        entity_id = (self.options.get("moisture_entity") or "").strip()
        if not entity_id:
            return False
        value = self._read_numeric(entity_id, (self.options.get("moisture_attribute") or "").strip())
        threshold = self.options.get("moisture_threshold_skip_above")
        if value is None or threshold is None:
            return False
        try:
            return value >= float(threshold)
        except (TypeError, ValueError):
            return False

    def _valve_moisture_skip(self, valve: Optional[dict]) -> Optional[bool]:
        """Per-valve moisture check. None = valve has no own sensor (use global)."""
        if not valve:
            return None
        entity_id = (valve.get("moisture_entity") or "").strip()
        threshold = valve.get("moisture_threshold")
        if not entity_id or threshold is None:
            return None
        value = self._read_numeric(entity_id, (valve.get("moisture_attribute") or "").strip())
        if value is None:
            return False
        try:
            return value >= float(threshold)
        except (TypeError, ValueError):
            return False

    def _should_skip_for_rain(self) -> bool:
        entity_id = (self.options.get("rain_entity") or "").strip()
        if not entity_id:
            return False
        state = self.hass.states.get(entity_id)
        if not state:
            return False
        threshold = self.options.get("rain_threshold")
        attribute = (self.options.get("rain_attribute") or "").strip()
        try:
            thr = float(threshold) if threshold is not None else 0.0
        except (TypeError, ValueError):
            thr = 0.0
        if thr > 0:  # 0 / blank = numeric check disabled
            try:
                raw = state.attributes.get(attribute, 0) if attribute else state.state
                return float(raw) >= thr
            except (TypeError, ValueError):
                if attribute:
                    return False
        skip_states = [s.strip() for s in str(self.options.get("rain_skip_states") or "").split(",") if s.strip()]
        if skip_states:
            return state.state in skip_states
        return False

    def _conditions_pass(self, conditions: list[dict]) -> bool:
        """All conditions must hold. A missing/unavailable entity fails its condition."""
        for cond in conditions:
            if not self._condition_holds(cond):
                return False
        return True

    def _condition_holds(self, cond: dict) -> bool:
        entity_id = (cond.get("entity_id") or "").strip()
        if not entity_id:
            return True
        state = self.hass.states.get(entity_id)
        if not state:
            return False
        attribute = (cond.get("attribute") or "").strip()
        actual = state.attributes.get(attribute) if attribute else state.state
        if actual is None or (not attribute and state.state in UNAVAILABLE_STATES):
            return False
        op = cond.get("operator") or "equals"
        expected = cond.get("value")
        try:
            a, e = float(actual), float(expected)
            numeric = True
        except (TypeError, ValueError):
            numeric = False
        if op == "above":
            return numeric and a > e
        if op == "below":
            return numeric and a < e
        same = (a == e) if numeric else str(actual).strip().lower() == str(expected).strip().lower()
        return same if op == "equals" else not same

    # ------------------------------------------------------------------ valve runs

    async def async_run_valve(
        self,
        entity_id: str,
        duration_min: int,
        source: str = "manual",
        note: str = "",
    ) -> dict:
        domain = entity_id.split(".")[0]
        if domain not in SUPPORTED_DOMAINS:
            raise ValueError(f"unsupported domain: {domain}")
        duration_min = max(1, min(MAX_RUN_MINUTES, int(duration_min)))
        seconds = duration_min * 60

        existing = self._active.pop(entity_id, None)
        self._unwatch_restored(entity_id)
        if existing:
            self._cancel_run_timer(existing)
            if not existing.get("starting"):
                self.hass.async_create_task(self.store.async_record_run(
                    entity_id, existing.get("source", "manual"), existing.get("duration_min", 0),
                    "superseded", existing.get("note", ""),
                ))

        # Reserve the entity before the first await so concurrent triggers see it busy.
        now = int(time.time())
        run = {
            "entity_id": entity_id,
            "started_at": now,
            "ends_at": now + seconds,
            "duration_min": duration_min,
            "source": source,
            "note": note,
            "unsub_close": None,
            "starting": True,
        }
        self._active[entity_id] = run

        try:
            await self._async_master_open()
            await self._call_service_on(entity_id)
            opened = await self._async_verify_opened(entity_id)
        except asyncio.CancelledError:
            if self._active.get(entity_id) is run and not self._stopping:
                self._active.pop(entity_id, None)
                await self._call_service_off(entity_id)
                await self._async_master_maybe_close()
            raise
        except Exception:
            if self._active.get(entity_id) is run:
                self._active.pop(entity_id, None)
                await self._async_master_maybe_close()
            raise

        if self._active.get(entity_id) is not run:
            # Stopped or superseded while starting.
            return run

        if not opened:
            self._active.pop(entity_id, None)
            await self._call_service_off(entity_id)
            label = self._entity_label(entity_id)
            LOG.error("valve %s did not open within %ss", entity_id, self.options.get("fail_detection_seconds", 5))
            self.hass.bus.async_fire(EVENT_VALVE_FAILED, {
                "entity_id": entity_id,
                "label": label,
                "source": source,
                "duration_min": duration_min,
            })
            self.hass.async_create_task(self._notify(
                "valve_failed", label, self._text("valve_failed", zone=label),
            ))
            await self.store.async_record_run(entity_id, source, duration_min, "failed_to_open", note)
            await self._async_master_maybe_close()
            raise RuntimeError(f"valve {entity_id} did not open")

        self._integrate_flow()
        now = int(time.time())
        run.pop("starting", None)
        run["started_at"] = now
        run["ends_at"] = now + seconds
        run["unsub_close"] = async_call_later(self.hass, seconds, self._make_close_callback(entity_id, run))
        await self.store.async_record_run(entity_id, source, duration_min, "started", note)
        await self._async_persist_active()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        self._evaluate_flow()
        LOG.info("started %s for %dm (source=%s)", entity_id, duration_min, source)
        label = self._entity_label(entity_id)
        self.hass.bus.async_fire(EVENT_VALVE_STARTED, {
            "entity_id": entity_id,
            "label": label,
            "source": source,
            "duration_min": duration_min,
            "started_at": now,
            "ends_at": run["ends_at"],
            "note": note,
        })
        self.hass.async_create_task(self._notify(
            "valve_start", label, self._text("valve_start", zone=label, n=duration_min),
        ))
        return run

    @staticmethod
    def _cancel_run_timer(run: dict) -> None:
        unsub = run.pop("unsub_close", None)
        if unsub:
            unsub()

    def _make_close_callback(self, entity_id: str, run: dict):
        async def _fire(_now):
            run["unsub_close"] = None
            if self._active.get(entity_id) is not run:
                return
            if run.get("await_state"):
                # Valve still unavailable since the restart: close it as soon as it reports a state.
                run["close_due"] = True
                await self._async_persist_active()
                return
            await self._async_complete(entity_id, "completed")
        return _fire

    async def _async_complete(self, entity_id: str, status: str, note: str = "") -> None:
        if entity_id in self._active:
            self._integrate_flow()
        active = self._active.pop(entity_id, None)
        if not active:
            return
        self._cancel_run_timer(active)
        if active.get("await_state"):
            # Stopped before the valve came back: still close it once it reports open.
            self._watch_restored(entity_id, None)
        await self._call_service_off(entity_id)
        liters = await self._async_account_water(entity_id, active)
        await self.store.async_record_run(
            entity_id,
            active.get("source", "manual"),
            active.get("duration_min", 0),
            status,
            note or active.get("note", ""),
            liters=liters,
        )
        await self._async_persist_active()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        self._evaluate_flow()
        label = self._entity_label(entity_id)
        self.hass.bus.async_fire(EVENT_VALVE_ENDED, {
            "entity_id": entity_id,
            "label": label,
            "status": status,
            "source": active.get("source", "manual"),
            "duration_min": active.get("duration_min", 0),
            "note": note or active.get("note", ""),
        })
        if status == "completed":
            text = self._text("valve_done", zone=label, n=active.get("duration_min", 0))
        else:
            text = self._text("valve_stopped", zone=label)
        self.hass.async_create_task(self._notify("valve_end", label, text))
        self.hass.async_create_task(self._async_master_maybe_close())

    async def _async_wait_run(self, entity_id: str, run: dict, minutes: int) -> None:
        """Block until `run` ends; close it if the waiting task is cancelled."""
        try:
            await asyncio.sleep(minutes * 60)
        except asyncio.CancelledError:
            if self._active.get(entity_id) is run and not self._stopping:
                await self._async_complete(entity_id, "cancelled")
            raise
        if self._active.get(entity_id) is run:
            await self._async_complete(entity_id, "completed")

    # ------------------------------------------------------------------ soak

    def _soak_chunks(self, entity_id: str, minutes: int) -> list[int]:
        valve = self.store.get_valve(entity_id) or {}
        run_max = int(valve.get("soak_run_min") or 0)
        pause = int(valve.get("soak_pause_min") or 0)
        if run_max <= 0 or pause <= 0 or minutes <= run_max:
            return [minutes]
        count = -(-minutes // run_max)
        base, extra = divmod(minutes, count)
        return [base + (1 if i < extra else 0) for i in range(count)]

    async def _async_run_sequence(
        self, entity_id: str, minutes: int, source: str, note: str, owner: str,
    ) -> None:
        """Run a valve for `minutes`, split into run/soak chunks when configured. Returns when done."""
        chunks = self._soak_chunks(entity_id, minutes)
        if len(chunks) == 1:
            run = await self.async_run_valve(entity_id, minutes, source=source, note=note)
            await self._async_wait_run(entity_id, run, minutes)
            return
        valve = self.store.get_valve(entity_id) or {}
        pause = int(valve.get("soak_pause_min") or 0)
        info = {
            "entity_id": entity_id,
            "owner": owner,
            "source": source,
            "total_min": minutes,
            "chunks": len(chunks),
            "chunk": 0,
            "phase": "starting",
            "resume_at": 0,
            "task": asyncio.current_task(),
        }
        previous = self._soak.get(entity_id)
        if previous and previous.get("owner") == "standalone" and previous.get("task") is not info["task"]:
            task = previous.get("task")
            if task and not task.done():
                task.cancel()
        self._soak[entity_id] = info
        try:
            for i, chunk in enumerate(chunks):
                info.update(chunk=i + 1, phase="running", resume_at=0)
                run = await self.async_run_valve(
                    entity_id, chunk, source=source, note=f"{note}|soak{i + 1}/{len(chunks)}",
                )
                await self._async_wait_run(entity_id, run, chunk)
                if i < len(chunks) - 1:
                    info.update(phase="soaking", resume_at=int(time.time()) + pause * 60)
                    async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
                    self.hass.bus.async_fire(EVENT_VALVE_SOAKING, {
                        "entity_id": entity_id,
                        "label": self._entity_label(entity_id),
                        "chunk": i + 1,
                        "chunks": len(chunks),
                        "resume_at": info["resume_at"],
                        "source": source,
                    })
                    await asyncio.sleep(pause * 60)
        finally:
            if self._soak.get(entity_id) is info:
                self._soak.pop(entity_id, None)
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    # ------------------------------------------------------------------ cycles

    def _has_running_work(self) -> bool:
        if self._active:
            return True
        return any(not c.get("paused") for c in self._active_cycles.values())

    async def async_run_cycle(self, cycle_id: str, source: str = "manual", note: str = "", duration_factor: float = 1.0) -> dict:
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
            "duration_factor": duration_factor,
        }
        self._active_cycles[cycle_id] = state
        task = self.hass.async_create_background_task(
            self._run_cycle_task(cycle, state), f"{DOMAIN}_cycle_{cycle_id}"
        )
        state["task"] = task
        self._persist_cycles()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        LOG.info("started cycle %s (%s), %d steps, source=%s",
                 cycle_id, cycle.get("name"), len(steps), source)
        self.hass.bus.async_fire(EVENT_CYCLE_STARTED, {
            "cycle_id": cycle_id,
            "name": cycle.get("name", ""),
            "source": source,
            "total_steps": len(steps),
            "started_at": state["started_at"],
            "note": note,
        })
        name = cycle.get("name") or cycle_id
        total = sum(self._scale_minutes(int(st.get("duration_min") or 0), duration_factor) for st in steps)
        self.hass.async_create_task(self._notify(
            "cycle_start", name, self._text("cycle_start", plan=name, n=total),
        ))
        return {k: v for k, v in state.items() if k != "task"}

    async def _run_cycle_task(self, cycle: dict, state: dict) -> None:
        cycle_id = cycle["id"]
        steps = cycle.get("steps") or []
        factor = float(state.get("duration_factor", 1.0))
        offset = int(state.get("start_offset", 0))
        source = f"cycle:{cycle_id}"
        automated = state.get("source") in ("schedule", "calendar")
        try:
            plan = self._cycle_plan(cycle_id, steps, factor, offset)
            if self._interleave_enabled() and any(len(p["chunks"]) > 1 for p in plan):
                await self._run_steps_interleaved(cycle_id, plan, state, source, automated)
            else:
                await self._run_steps_sequential(cycle_id, plan, state, source, automated)
            state["current_entity"] = None
            await self.store.async_record_run(
                cycle_id, state.get("source", "manual"), 0,
                "cycle_completed", state.get("note", ""),
            )
            self.hass.bus.async_fire(EVENT_CYCLE_ENDED, {
                "cycle_id": cycle_id,
                "name": cycle.get("name", ""),
                "status": "completed",
                "source": state.get("source", "manual"),
            })
            name = cycle.get("name") or cycle_id
            self.hass.async_create_task(self._notify("cycle_end", name, self._text("cycle_done", plan=name)))
        except asyncio.CancelledError:
            if not state.get("paused") and not self._stopping:
                await self._async_record_cycle_cancelled(cycle_id, cycle.get("name", ""), state)
            raise
        finally:
            if not self._stopping:
                if not state.get("paused") and self._active_cycles.get(cycle_id) is state:
                    self._active_cycles.pop(cycle_id, None)
                self._persist_cycles()
                async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
                self.hass.async_create_task(self._async_master_maybe_close())

    async def _async_record_cycle_cancelled(self, cycle_id: str, name: str, state: dict) -> None:
        await self.store.async_record_run(
            cycle_id, state.get("source", "manual"), 0,
            "cycle_cancelled", state.get("note", ""),
        )
        self.hass.bus.async_fire(EVENT_CYCLE_ENDED, {
            "cycle_id": cycle_id,
            "name": name,
            "status": "cancelled",
            "source": state.get("source", "manual"),
        })
        name = name or cycle_id
        self.hass.async_create_task(self._notify("cycle_end", name, self._text("cycle_stopped", plan=name)))

    @staticmethod
    async def _async_cancel_task(task: Optional[asyncio.Task]) -> None:
        if not task or task.done() or task is asyncio.current_task():
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            LOG.debug("cancelled task raised: %s", e)

    async def async_pause_cycle(self, cycle_id: str) -> None:
        state = self._active_cycles.get(cycle_id)
        if not state or state.get("paused"):
            return
        state["paused"] = True
        state["paused_at_step"] = max(1, int(state.get("step", 0)), int(state.get("max_step") or 0))
        # Cancelling closes the current step valve (see _async_wait_run / async_run_valve).
        await self._async_cancel_task(state.get("task"))
        state["current_entity"] = None
        self._active_cycles[cycle_id] = state
        self._persist_cycles()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        await self._async_master_maybe_close()
        self.hass.bus.async_fire(EVENT_CYCLE_PAUSED, {
            "cycle_id": cycle_id,
            "name": state.get("cycle_name", ""),
            "paused_at_step": state.get("paused_at_step", 0),
        })

    async def async_resume_cycle(self, cycle_id: str) -> None:
        state = self._active_cycles.get(cycle_id)
        if not state or not state.get("paused"):
            return
        cycle = self.store.get_cycle(cycle_id)
        if not cycle:
            self._active_cycles.pop(cycle_id, None)
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
            return
        start_from = int(state.get("paused_at_step", 0))
        steps_full = cycle.get("steps") or []
        remaining_steps = steps_full[start_from:]
        if not remaining_steps:
            self._active_cycles.pop(cycle_id, None)
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
            return
        cycle_resume = {**cycle, "steps": remaining_steps}
        state["paused"] = False
        state["step"] = start_from
        state["total_steps"] = len(steps_full)
        state["start_offset"] = start_from
        self._active_cycles[cycle_id] = state
        task = self.hass.async_create_background_task(
            self._run_cycle_task(cycle_resume, state), f"{DOMAIN}_cycle_{cycle_id}"
        )
        state["task"] = task
        self._persist_cycles()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        self.hass.bus.async_fire(EVENT_CYCLE_RESUMED, {
            "cycle_id": cycle_id,
            "name": cycle.get("name", ""),
            "from_step": start_from + 1,
        })

    async def async_stop_cycle(self, cycle_id: str, note: str = "manual stop") -> None:
        state = self._active_cycles.get(cycle_id)
        if not state:
            return
        if state.get("paused"):
            self._active_cycles.pop(cycle_id, None)
            self._persist_cycles()
            await self._async_record_cycle_cancelled(cycle_id, state.get("cycle_name", ""), state)
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
            await self._async_master_maybe_close()
            return
        await self._async_cancel_task(state.get("task"))
        if self._active_cycles.get(cycle_id) is state:
            self._active_cycles.pop(cycle_id, None)

    async def async_stop_valve(self, entity_id: str) -> None:
        soak = self._soak.get(entity_id)
        if soak and soak.get("owner") == "standalone":
            phase = soak.get("phase")
            await self._async_cancel_task(soak.get("task"))
            if phase == "soaking":
                await self.store.async_record_run(
                    entity_id, soak.get("source", "manual"), 0, "cancelled", "manual stop|soak",
                )
        if entity_id in self._active:
            await self._async_complete(entity_id, "cancelled", "manual stop")
            return
        await self._call_service_off(entity_id)

    async def async_stop_all(self, reason: str = "manual stop") -> None:
        for cycle_id in list(self._active_cycles):
            await self.async_stop_cycle(cycle_id, note=reason)
        for entity_id in list(self._soak):
            await self.async_stop_valve(entity_id)
        for entity_id in list(self._active):
            await self._async_complete(entity_id, "cancelled", reason)
        await self._async_master_maybe_close()

    # ------------------------------------------------------------------ cycle steps

    def _interleave_enabled(self) -> bool:
        return bool(self.options.get("interleave_soak", True))

    def _cycle_plan(self, cycle_id: str, steps: list, factor: float, offset: int) -> list[dict]:
        plan = []
        for i, step in enumerate(steps):
            step_no = offset + i + 1
            entity_id = step.get("entity_id")
            base_duration = int(step.get("duration_min", 1))
            duration = self._scale_minutes(base_duration, factor)
            if not entity_id or duration <= 0:
                LOG.warning(
                    "cycle %s step %d skipped: entity_id=%r duration=%s base=%s factor=%s",
                    cycle_id, step_no, entity_id, duration, base_duration, factor,
                )
                continue
            valve = self.store.get_valve(entity_id) or {}
            plan.append({
                "step_no": step_no, "entity_id": entity_id, "duration": duration,
                "chunks": self._soak_chunks(entity_id, duration),
                "pause": int(valve.get("soak_pause_min") or 0) * 60,
                "ready_at": 0.0, "started": False,
            })
        return plan

    def _mark_step(self, state: dict, p: dict, seconds: int) -> None:
        state["step"] = p["step_no"]
        state["max_step"] = max(int(state.get("max_step") or 0), p["step_no"])
        state["current_entity"] = p["entity_id"]
        state["step_ends_at"] = int(time.time()) + seconds
        self._persist_cycles()
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    def _step_skipped(self, p: dict, state: dict, source: str, automated: bool) -> bool:
        if not automated:
            return False
        valve = self.store.get_valve(p["entity_id"])
        reason = self._valve_weather_reason(valve)
        if reason == "rain_delay_global":
            reason = "rain_delay"
        if not reason and self._valve_moisture_skip(valve):
            reason = "moisture"
        if reason:
            self._record_skip(reason, "valve", p["entity_id"], self._entity_label(p["entity_id"]),
                              source, f"{state.get('note', '')}|step{p['step_no']}", p["duration"], None)
            return True
        return False

    async def _run_steps_sequential(self, cycle_id: str, plan: list, state: dict, source: str, automated: bool) -> None:
        for p in plan:
            if self._active_cycles.get(cycle_id) is not state:
                return
            self._mark_step(state, p, self._sequence_seconds(p["entity_id"], p["duration"]))
            if self._step_skipped(p, state, source, automated):
                continue
            try:
                await self._async_run_sequence(
                    p["entity_id"], p["duration"], source, f"{state.get('note', '')}|step{p['step_no']}", owner="cycle",
                )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                LOG.warning("cycle %s step %d failed: %s", cycle_id, p["step_no"], e)

    async def _run_steps_interleaved(self, cycle_id: str, plan: list, state: dict, source: str, automated: bool) -> None:
        """Cycle & soak across zones: while one zone soaks, water the next one that is ready."""
        waiting: set[str] = set()
        try:
            while any(p["chunks"] for p in plan):
                if self._active_cycles.get(cycle_id) is not state:
                    return
                now = time.time()
                ready = [p for p in plan if p["chunks"] and p["ready_at"] <= now]
                if not ready:
                    wait = min(p["ready_at"] for p in plan if p["chunks"]) - now
                    state["current_entity"] = None
                    async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
                    await asyncio.sleep(max(1.0, wait))
                    continue
                p = ready[0]
                if not p["started"]:
                    p["started"] = True
                    if self._step_skipped(p, state, source, automated):
                        p["chunks"] = []
                        continue
                total = p.get("total_chunks") or len(p["chunks"])
                p["total_chunks"] = total
                chunk = p["chunks"].pop(0)
                done = total - len(p["chunks"])
                self._soak.pop(p["entity_id"], None)
                waiting.discard(p["entity_id"])
                self._mark_step(state, p, chunk * 60)
                try:
                    run = await self.async_run_valve(
                        p["entity_id"], chunk, source=source,
                        note=f"{state.get('note', '')}|step{p['step_no']}|soak{done}/{total}",
                    )
                    await self._async_wait_run(p["entity_id"], run, chunk)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    LOG.warning("cycle %s step %d failed: %s", cycle_id, p["step_no"], e)
                    p["chunks"] = []
                    continue
                if p["chunks"]:
                    p["ready_at"] = time.time() + p["pause"]
                    self._soak[p["entity_id"]] = {
                        "entity_id": p["entity_id"], "owner": "cycle", "source": source,
                        "total_min": p["duration"], "chunks": total, "chunk": done,
                        "phase": "soaking", "resume_at": int(p["ready_at"]), "task": None,
                    }
                    waiting.add(p["entity_id"])
                    async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        finally:
            for entity_id in waiting:
                if (self._soak.get(entity_id) or {}).get("owner") == "cycle":
                    self._soak.pop(entity_id, None)
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    # ------------------------------------------------------------------ cycle persistence / resume

    def _sequence_seconds(self, entity_id: str, minutes: int) -> int:
        chunks = self._soak_chunks(entity_id, minutes)
        pause = int((self.store.get_valve(entity_id) or {}).get("soak_pause_min") or 0)
        return sum(chunks) * 60 + max(0, len(chunks) - 1) * pause * 60

    @callback
    def _persist_cycles(self) -> None:
        if self._stopping:
            return
        keep = ("cycle_id", "cycle_name", "started_at", "step", "total_steps", "current_entity", "source",
                "note", "duration_factor", "paused", "paused_at_step", "start_offset", "step_ends_at", "max_step")
        cycles = [{k: st.get(k) for k in keep} for st in self._active_cycles.values()]
        self.hass.async_create_task(self.store.async_set_cycle_state(cycles))

    async def _async_restore_cycles(self) -> None:
        saved = self.store.cycle_state
        cycles = saved.get("cycles") or []
        if not cycles:
            return
        now = int(time.time())
        saved_at = int(saved.get("saved_at") or now)
        for c in cycles:
            cycle_id = c.get("cycle_id")
            cycle = self.store.get_cycle(cycle_id or "")
            if not cycle or cycle_id in self._active_cycles:
                continue
            state = {k: v for k, v in c.items() if v is not None}
            state.setdefault("duration_factor", 1.0)
            if c.get("paused"):
                self._active_cycles[cycle_id] = state
                continue
            entity = c.get("current_entity")
            run = self._active.get(entity) if entity else None
            if run and run.get("source") != f"cycle:{cycle_id}":
                run = None
            ends = int((run or {}).get("ends_at") or c.get("step_ends_at") or saved_at)
            if run is None and now - ends > RESUME_MAX_GAP_SECONDS:
                LOG.info("not resuming cycle %s: HA was down too long", cycle_id)
                await self.store.async_record_run(
                    cycle_id, c.get("source", "manual"), 0, "cycle_cancelled", "downtime",
                )
                continue
            step = max(0, int(c.get("step") or 0), int(c.get("max_step") or 0))
            rest = (cycle.get("steps") or [])[step:]
            state["start_offset"] = step
            self._active_cycles[cycle_id] = state
            state["task"] = self.hass.async_create_background_task(
                self._resume_cycle_task(cycle, state, rest, entity, run), f"{DOMAIN}_cycle_{cycle_id}"
            )
            LOG.info("resuming cycle %s after restart from step %d", cycle_id, step + 1)
            self.hass.bus.async_fire(EVENT_CYCLE_RESUMED, {
                "cycle_id": cycle_id, "name": cycle.get("name", ""), "from_step": step + 1, "after_restart": True,
            })
        self._persist_cycles()
        if self._active_cycles:
            async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    async def _resume_cycle_task(self, cycle: dict, state: dict, rest: list, entity: Optional[str], run: Optional[dict]) -> None:
        cycle_id = cycle["id"]
        if run is not None and entity:
            try:
                wait = max(0, int(run.get("ends_at", 0)) - int(time.time()))
                await asyncio.sleep(wait)
                while self._active.get(entity) is run and run.get("await_state"):
                    # Valve not back since the restart: its state watcher closes it (#54).
                    await asyncio.sleep(5)
                if self._active.get(entity) is run:
                    await self._async_complete(entity, "completed")
            except asyncio.CancelledError:
                if self._active.get(entity) is run and not self._stopping:
                    await self._async_complete(entity, "cancelled")
                if not state.get("paused") and not self._stopping:
                    await self._async_record_cycle_cancelled(cycle_id, cycle.get("name", ""), state)
                    if self._active_cycles.get(cycle_id) is state:
                        self._active_cycles.pop(cycle_id, None)
                    self._persist_cycles()
                    async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
                raise
        await self._run_cycle_task({**cycle, "steps": rest}, state)

    # ------------------------------------------------------------------ rain forecast

    @property
    def forecast_status(self) -> dict:
        entity_id = (self.options.get("forecast_entity") or "").strip()
        return {"entity_id": entity_id, "mm": self._forecast_mm(), "hours": self._forecast_hours(),
                "updated": self._forecast.get("updated") or None, "error": self._forecast.get("error")}

    def _forecast_hours(self) -> int:
        try:
            return max(1, min(72, int(self.options.get("forecast_hours") or 24)))
        except (TypeError, ValueError):
            return 24

    def _forecast_mm(self) -> Optional[float]:
        if not (self.options.get("forecast_entity") or "").strip():
            return None
        if time.time() - float(self._forecast.get("updated") or 0) > FORECAST_MAX_AGE_SECONDS:
            return None
        return self._forecast.get("mm")

    def _should_skip_for_forecast(self) -> bool:
        try:
            threshold = float(self.options.get("forecast_skip_mm") or 0)
        except (TypeError, ValueError):
            return False
        mm = self._forecast_mm()
        return threshold > 0 and mm is not None and mm >= threshold

    def _arm_forecast(self) -> None:
        if self._unsub_forecast:
            self._unsub_forecast()
            self._unsub_forecast = None
        if not (self.options.get("forecast_entity") or "").strip():
            self._forecast = {"mm": None, "updated": 0, "kind": None, "error": None}
            return
        self._unsub_forecast = async_track_time_interval(
            self.hass, self._async_refresh_forecast, timedelta(minutes=FORECAST_REFRESH_MINUTES)
        )
        self.hass.async_create_task(self._async_refresh_forecast())

    async def _async_refresh_forecast(self, _now=None) -> None:
        entity_id = (self.options.get("forecast_entity") or "").strip()
        if not entity_id:
            return
        hours = self._forecast_hours()
        now = dt_util.utcnow()
        horizon = now + timedelta(hours=hours)
        total = None
        kind = None
        error = None
        for ftype in ("hourly", "daily"):
            try:
                resp = await self.hass.services.async_call(
                    "weather", "get_forecasts", {"entity_id": entity_id, "type": ftype},
                    blocking=True, return_response=True,
                )
                items = ((resp or {}).get(entity_id) or {}).get("forecast") or []
            except Exception as e:
                error = str(e)
                continue
            if not items:
                continue
            span = timedelta(hours=1) if ftype == "hourly" else timedelta(days=1)
            acc = 0.0
            for item in items:
                start = dt_util.parse_datetime(str(item.get("datetime") or ""))
                if start is None:
                    continue
                start = dt_util.as_utc(start)
                if start < horizon and start + span > now:
                    try:
                        acc += float(item.get("precipitation") or 0)
                    except (TypeError, ValueError):
                        pass
            total, kind, error = acc, ftype, None
            break
        if total is not None:
            state = self.hass.states.get(entity_id)
            unit = (state.attributes.get("precipitation_unit") if state else "") or "mm"
            if unit == "in":
                total *= 25.4
            elif unit == "cm":
                total *= 10
            self._forecast = {"mm": round(total, 1), "updated": time.time(), "kind": kind, "error": None}
        else:
            self._forecast = {**self._forecast, "error": error or "no forecast data"}
            LOG.warning("rain forecast from %s unavailable: %s", entity_id, self._forecast["error"])
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)

    # ------------------------------------------------------------------ services / master

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

    async def _async_master_open(self) -> None:
        master = (self.options.get("master_valve_entity") or "").strip()
        if not master:
            return
        async with self._master_lock:
            if self._master_open:
                return
            try:
                await self._call_service_on(master)
            except Exception as e:
                LOG.warning("master valve open failed: %s", e)
                return
            self._master_open = True
            pre = int(self.options.get("master_valve_pre_open_sec") or 0)
            if pre > 0:
                await asyncio.sleep(pre)

    async def _async_master_maybe_close(self) -> None:
        master = (self.options.get("master_valve_entity") or "").strip()
        if not master:
            return
        if self._has_running_work() or self._master_lock.locked():
            return
        self._master_open = False
        await self._call_service_off(master)

    async def _async_verify_opened(self, entity_id: str) -> bool:
        if not self.options.get("fail_detection_enabled"):
            return True
        wait = int(self.options.get("fail_detection_seconds") or 5)
        for _ in range(wait):
            await asyncio.sleep(1)
            state = self.hass.states.get(entity_id)
            if state and state.state in ON_STATES:
                return True
        state = self.hass.states.get(entity_id)
        return bool(state and state.state in ON_STATES)

    # ------------------------------------------------------------------ flow / leak

    def _arm_flow(self) -> None:
        if self._unsub_flow:
            self._unsub_flow()
            self._unsub_flow = None
        self._cancel_flow_timer()
        self._flow_alert = None
        entity_id = (self.options.get("flow_entity") or "").strip()
        if not entity_id:
            return
        self._unsub_flow = async_track_state_change_event(self.hass, [entity_id], self._on_flow_change)
        self._flow_last = None
        self._integrate_flow()
        self._evaluate_flow()

    def _cancel_flow_timer(self) -> None:
        if self._flow_timer:
            self._flow_timer()
            self._flow_timer = None

    @callback
    def _on_flow_change(self, _event: Event) -> None:
        self._integrate_flow()
        self._evaluate_flow()

    def _flow_value(self) -> Optional[float]:
        entity_id = (self.options.get("flow_entity") or "").strip()
        if not entity_id:
            return None
        return self._read_numeric(entity_id, (self.options.get("flow_attribute") or "").strip())

    def _flow_shown(self, value: Optional[float], entity_id: str) -> str:
        """Flow reading for a notification: number and the sensor's unit (#68)."""
        state = self.hass.states.get(entity_id) if entity_id else None
        unit = str((state.attributes.get("unit_of_measurement") if state else "") or "").strip()
        return f"{fmt_number(value)} {unit}".strip()

    def _flow_lpm(self) -> Optional[float]:
        """Flow in litres per minute, converted from the sensor's unit (L/min assumed if unknown)."""
        value = self._flow_value()
        if value is None:
            return None
        state = self.hass.states.get((self.options.get("flow_entity") or "").strip())
        unit = str((state.attributes.get("unit_of_measurement") if state else "") or "").strip().lower()
        return max(0.0, value * FLOW_UNIT_TO_LPM.get(unit, 1.0))

    @callback
    def _integrate_flow(self) -> None:
        """Attribute water since the last sample to the zones running in that interval."""
        if not (self.options.get("flow_entity") or "").strip():
            self._flow_last = None
            return
        now = time.time()
        if self._flow_last is not None:
            last_ts, last_lpm = self._flow_last
            running = [r for r in self._active.values() if not r.get("starting")]
            if running and last_lpm > 0 and now > last_ts:
                share = last_lpm * (now - last_ts) / 60 / len(running)
                for r in running:
                    r["liters"] = r.get("liters", 0.0) + share
                    r["measured"] = True
                    if len(running) > 1:
                        r["shared"] = True
        lpm = self._flow_lpm()
        self._flow_last = (now, lpm) if lpm is not None else None

    async def _async_account_water(self, entity_id: str, run: dict) -> Optional[float]:
        """Litres for a finished run: measured by the flow sensor, else estimated from the zone's flow rate."""
        if run.get("starting"):
            return None
        elapsed_min = max(0.0, (time.time() - float(run.get("started_at") or time.time())) / 60)
        valve = self.store.get_valve(entity_id) or {}
        measured = bool(run.get("measured")) and (self.options.get("flow_entity") or "").strip()
        if measured:
            liters = float(run.get("liters") or 0)
        elif valve.get("flow_rate_lpm"):
            liters = float(valve["flow_rate_lpm"]) * elapsed_min
        else:
            return None
        run_lpm = None
        if measured and not run.get("shared") and elapsed_min >= LOW_FLOW_MIN_MINUTES:
            run_lpm = liters / elapsed_min
            avg = valve.get("avg_lpm")
            if avg and int(valve.get("flow_runs") or 0) >= LOW_FLOW_MIN_RUNS and run_lpm < LOW_FLOW_RATIO * float(avg):
                label = self._entity_label(entity_id)
                LOG.warning("low flow on %s: %.1f L/min, usually %.1f", entity_id, run_lpm, float(avg))
                self.hass.bus.async_fire(EVENT_LOW_FLOW, {
                    "entity_id": entity_id, "label": label,
                    "lpm": round(run_lpm, 1), "expected_lpm": round(float(avg), 1),
                })
                self.hass.async_create_task(self._notify(
                    "low_flow", label,
                    self._text("low_flow", zone=label, lpm=fmt_number(run_lpm), avg=fmt_number(avg)),
                ))
                run_lpm = None  # don't learn from an abnormal run
        await self.store.async_add_water(entity_id, liters, run_lpm)
        return liters

    def _flow_violation(self) -> Optional[str]:
        value = self._flow_value()
        if value is None:
            return None
        try:
            if self._active:
                limit = float(self.options.get("flow_max_running") or 0)
                return "high_flow" if limit > 0 and value > limit else None
            limit = float(self.options.get("flow_leak_threshold") or 0)
            return "leak" if limit > 0 and value > limit else None
        except (TypeError, ValueError):
            return None

    @callback
    def _evaluate_flow(self) -> None:
        if not (self.options.get("flow_entity") or "").strip():
            return
        kind = self._flow_violation()
        if kind is None:
            self._cancel_flow_timer()
            if self._flow_alert:
                self._flow_alert = None
                async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
            return
        if self._flow_alert == kind or self._flow_timer:
            return
        delay = max(5, int(self.options.get("flow_delay_sec") or 60))
        self._flow_timer = async_call_later(self.hass, delay, self._on_flow_timer)

    async def _on_flow_timer(self, _now) -> None:
        self._flow_timer = None
        kind = self._flow_violation()
        if kind is None or self._flow_alert == kind:
            return
        self._flow_alert = kind
        value = self._flow_value()
        entity_id = (self.options.get("flow_entity") or "").strip()
        running = sorted(self._active)
        LOG.warning("flow alert %s: %s = %s (running: %s)", kind, entity_id, value, running)
        stop_all = bool(self.options.get("flow_stop_all"))
        self.hass.bus.async_fire(EVENT_LEAK_DETECTED, {
            "kind": kind,
            "flow_entity": entity_id,
            "value": value,
            "running": running,
            "stopped_all": stop_all,
        })
        await self.store.async_record_run(
            entity_id, "flow", 0, "leak_detected" if kind == "leak" else "high_flow",
            f"value:{value}" + (f"|running:{','.join(running)}" if running else ""),
        )
        shown = self._flow_shown(value, entity_id)
        message = (
            self._text("leak", value=shown)
            if kind == "leak"
            else self._text("high_flow", value=shown, zones=", ".join(self._entity_label(e) for e in running))
        )
        if stop_all:
            message += " " + self._text("stopped_all")
        self.hass.async_create_task(self._notify("leak_detected", APP_TITLE, message))
        async_dispatcher_send(self.hass, SIGNAL_STATE_CHANGED)
        if stop_all:
            await self.async_stop_all(kind)
            if (self.options.get("master_valve_entity") or "").strip():
                self._master_open = False
                await self._call_service_off(self.options["master_valve_entity"].strip())
