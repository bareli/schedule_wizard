"""Persistent storage for valves, schedules, and run history."""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import REPEAT_INTERVAL, REPEAT_WEEKDAYS, SIGNAL_CONFIG_CHANGED, STORAGE_KEY, STORAGE_VERSION

MAX_HISTORY = 500
# History rows, water totals and plan step progress are written at most every SAVE_DELAY seconds
# (PERF-003). Starting or ending a run or a plan is written at once: restart recovery needs it.
SAVE_DELAY = 2

VALVE_EXTRA_FIELDS = (
    "soak_run_min",
    "soak_pause_min",
    "moisture_entity",
    "moisture_attribute",
    "moisture_threshold",
    "rain_exempt",
    "flow_rate_lpm",
)


def _clean_valve_extra(extra: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in VALVE_EXTRA_FIELDS:
        if k not in extra:
            continue
        v = extra[k]
        if k in ("soak_run_min", "soak_pause_min"):
            out[k] = max(0, int(v or 0))
        elif k == "moisture_threshold":
            out[k] = None if v is None or v == "" else float(v)
        elif k == "rain_exempt":
            out[k] = bool(v)
        elif k == "flow_rate_lpm":
            out[k] = None if v is None or v == "" or float(v) <= 0 else float(v)
        else:
            out[k] = (v or "").strip()
    return out


def _clean_conditions(conditions: Optional[list[dict]]) -> list[dict]:
    out = []
    for c in conditions or []:
        entity_id = (c.get("entity_id") or "").strip()
        if not entity_id:
            continue
        out.append({
            "entity_id": entity_id,
            "attribute": (c.get("attribute") or "").strip(),
            "operator": c.get("operator") or "equals",
            "value": "" if c.get("value") is None else str(c.get("value")),
        })
    return out


def _run_keys(runs: list[dict]) -> set:
    return {(r.get("entity_id"), r.get("started_at")) for r in runs}


def _cycle_keys(cycles: list[dict]) -> set:
    return {(c.get("cycle_id"), bool(c.get("paused"))) for c in cycles}


class WizardStore:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {
            "valves": [],
            "schedules": [],
            "history": [],
            "active_runs": [],
            "pending_closes": [],
            "cycles": [],
            "skips": {},
            "cycle_state": {},
            "water_total_l": 0.0,
        }
        self._loaded = False
        self._pending = False

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data:
            self._data["valves"] = data.get("valves", [])
            self._data["schedules"] = data.get("schedules", [])
            for sched in self._data["schedules"]:
                # Schedules saved before 0.14.0 repeat on weekdays.
                sched.setdefault("repeat", REPEAT_WEEKDAYS)
                sched.setdefault("interval_days", 0)
                sched.setdefault("start_date", "")
            self._data["history"] = data.get("history", [])
            self._data["active_runs"] = data.get("active_runs", [])
            self._data["pending_closes"] = data.get("pending_closes", []) or []
            self._data["cycles"] = data.get("cycles", [])
            self._data["skips"] = data.get("skips", {}) or {}
            self._data["cycle_state"] = data.get("cycle_state", {}) or {}
            self._data["water_total_l"] = float(data.get("water_total_l") or 0)
        self._loaded = True

    async def async_save(self) -> None:
        self._pending = False
        await self._store.async_save(self._data)

    def _data_to_save(self) -> dict[str, Any]:
        self._pending = False
        return self._data

    @callback
    def _async_delay_save(self) -> None:
        """Coalesce frequent writes; Home Assistant writes pending data on shutdown."""
        self._pending = True
        self._store.async_delay_save(self._data_to_save, SAVE_DELAY)

    async def async_flush(self) -> None:
        """Write a pending delayed save now (unload or reload)."""
        if self._pending:
            await self.async_save()

    async def _async_save_config(self) -> None:
        """Save after a change to valves, schedules or cycles, and tell entity platforms."""
        await self.async_save()
        async_dispatcher_send(self._hass, SIGNAL_CONFIG_CHANGED)

    # ---- one-off skips: {schedule_id: ["YYYY-MM-DD", ...]} in local dates

    @property
    def skips(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self._data["skips"].items()}

    def is_skipped(self, schedule_id: str, day: str) -> bool:
        return day in self._data["skips"].get(schedule_id, [])

    async def async_add_skip(self, schedule_id: str, day: str) -> None:
        days = self._data["skips"].setdefault(schedule_id, [])
        if day not in days:
            days.append(day)
            days.sort()
            await self._async_save_config()

    async def async_remove_skip(self, schedule_id: str, day: str) -> None:
        days = self._data["skips"].get(schedule_id, [])
        if day in days:
            days.remove(day)
            if not days:
                self._data["skips"].pop(schedule_id, None)
            await self._async_save_config()

    async def async_prune_skips(self, today: str) -> None:
        changed = False
        for sid in list(self._data["skips"]):
            keep = [d for d in self._data["skips"][sid] if d >= today]
            if keep != self._data["skips"][sid]:
                changed = True
                if keep:
                    self._data["skips"][sid] = keep
                else:
                    self._data["skips"].pop(sid)
        if changed:
            await self._async_save_config()

    @property
    def valves(self) -> list[dict]:
        return list(self._data["valves"])

    @property
    def schedules(self) -> list[dict]:
        return list(self._data["schedules"])

    @property
    def history(self) -> list[dict]:
        return list(self._data["history"])

    @property
    def active_runs(self) -> list[dict]:
        return list(self._data["active_runs"])

    @property
    def pending_closes(self) -> list[dict]:
        """Valves whose close command could not be delivered yet (#80)."""
        return list(self._data.get("pending_closes") or [])

    @property
    def water_total_l(self) -> float:
        return float(self._data.get("water_total_l") or 0)

    async def async_add_water(self, entity_id: str, liters: float, run_lpm: Optional[float] = None) -> None:
        """Add litres to a zone and the overall total; learn the zone's normal flow from measured runs."""
        valve = self.get_valve(entity_id)
        if liters > 0:
            self._data["water_total_l"] = round(self.water_total_l + liters, 2)
            if valve is not None:
                valve["water_total_l"] = round(float(valve.get("water_total_l") or 0) + liters, 2)
        if valve is not None and run_lpm is not None and run_lpm > 0:
            avg = valve.get("avg_lpm")
            valve["avg_lpm"] = round(run_lpm if not avg else 0.7 * float(avg) + 0.3 * run_lpm, 2)
            valve["flow_runs"] = int(valve.get("flow_runs") or 0) + 1
        self._async_delay_save()

    @property
    def cycle_state(self) -> dict:
        return dict(self._data.get("cycle_state") or {})

    async def async_set_cycle_state(self, cycles: list[dict]) -> None:
        old = (self._data.get("cycle_state") or {}).get("cycles") or []
        self._data["cycle_state"] = {"saved_at": int(time.time()), "cycles": cycles}
        if _cycle_keys(old) == _cycle_keys(cycles):
            self._async_delay_save()  # only step progress changed
        else:
            await self.async_save()

    async def async_set_active_runs(self, runs: list[dict]) -> None:
        old = self._data["active_runs"]
        self._data["active_runs"] = list(runs)
        if _run_keys(old) == _run_keys(runs):
            self._async_delay_save()
        else:
            await self.async_save()  # a valve opened or closed: must survive a crash

    async def async_set_pending_closes(self, closes: list[dict]) -> None:
        self._data["pending_closes"] = list(closes)
        await self.async_save()

    def get_valve(self, entity_id: str) -> Optional[dict]:
        for v in self._data["valves"]:
            if v["entity_id"] == entity_id:
                return v
        return None

    async def async_upsert_valve(
        self,
        entity_id: str,
        label: str,
        default_duration_min: int,
        enabled: bool = True,
        **extra: Any,
    ) -> dict:
        existing = self.get_valve(entity_id)
        if existing:
            existing.update({
                "label": label,
                "default_duration_min": int(default_duration_min),
                "enabled": bool(enabled),
                **_clean_valve_extra(extra),
            })
            await self._async_save_config()
            return existing
        valve = {
            "entity_id": entity_id,
            "label": label,
            "default_duration_min": int(default_duration_min),
            "enabled": bool(enabled),
            "soak_run_min": 0,
            "soak_pause_min": 0,
            "moisture_entity": "",
            "moisture_attribute": "",
            "moisture_threshold": None,
            "rain_exempt": False,
            "rain_delay_until": 0,
            "flow_rate_lpm": None,
            "water_total_l": 0.0,
            "avg_lpm": None,
            "flow_runs": 0,
            **_clean_valve_extra(extra),
            "created_at": int(time.time()),
        }
        self._data["valves"].append(valve)
        await self._async_save_config()
        return valve

    async def async_set_valves_rain_delay(self, entity_ids: list[str], until: int) -> list[str]:
        """Set (or clear with 0) a per-valve rain delay. Returns the entity_ids that were updated."""
        updated = []
        for entity_id in entity_ids:
            valve = self.get_valve(entity_id)
            if valve is not None:
                valve["rain_delay_until"] = int(until)
                updated.append(entity_id)
        if updated:
            await self._async_save_config()
        return updated

    async def async_remove_valve(self, entity_id: str) -> bool:
        before = len(self._data["valves"])
        self._data["valves"] = [v for v in self._data["valves"] if v["entity_id"] != entity_id]
        self._data["schedules"] = [s for s in self._data["schedules"] if s.get("valve_entity_id") != entity_id]
        if len(self._data["valves"]) != before:
            await self._async_save_config()
            return True
        return False

    def get_schedule(self, schedule_id: str) -> Optional[dict]:
        for s in self._data["schedules"]:
            if s["id"] == schedule_id:
                return s
        return None

    async def async_add_schedule(
        self,
        days_mask: int,
        time_hhmm: str,
        duration_min: int,
        name: str = "",
        enabled: bool = True,
        valve_entity_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        conditions: Optional[list[dict]] = None,
        repeat: str = REPEAT_WEEKDAYS,
        interval_days: int = 0,
        start_date: str = "",
    ) -> dict:
        interval = repeat == REPEAT_INTERVAL
        sched = {
            "id": uuid.uuid4().hex[:12],
            "valve_entity_id": valve_entity_id or "",
            "cycle_id": cycle_id or "",
            "name": name,
            "days_mask": int(days_mask),
            "repeat": REPEAT_INTERVAL if interval else REPEAT_WEEKDAYS,
            "interval_days": int(interval_days) if interval else 0,
            "start_date": start_date if interval else "",
            "time_hhmm": time_hhmm,
            "duration_min": int(duration_min),
            "enabled": bool(enabled),
            "conditions": _clean_conditions(conditions),
            "created_at": int(time.time()),
        }
        self._data["schedules"].append(sched)
        await self._async_save_config()
        return sched

    async def async_update_schedule(self, schedule_id: str, **fields: Any) -> Optional[dict]:
        sched = self.get_schedule(schedule_id)
        if not sched:
            return None
        for k in ("name", "days_mask", "time_hhmm", "duration_min", "enabled", "repeat", "interval_days", "start_date"):
            if k in fields and fields[k] is not None:
                if k in ("days_mask", "duration_min", "interval_days"):
                    sched[k] = int(fields[k])
                elif k == "enabled":
                    sched[k] = bool(fields[k])
                else:
                    sched[k] = fields[k]
        if fields.get("conditions") is not None:
            sched["conditions"] = _clean_conditions(fields["conditions"])
        if sched.get("repeat") != REPEAT_INTERVAL:
            sched["repeat"] = REPEAT_WEEKDAYS
            sched["interval_days"] = 0
            sched["start_date"] = ""
        await self._async_save_config()
        return sched

    async def async_remove_schedule(self, schedule_id: str) -> bool:
        before = len(self._data["schedules"])
        self._data["schedules"] = [s for s in self._data["schedules"] if s["id"] != schedule_id]
        self._data["skips"].pop(schedule_id, None)
        if len(self._data["schedules"]) != before:
            await self._async_save_config()
            return True
        return False

    @property
    def cycles(self) -> list[dict]:
        return list(self._data["cycles"])

    def get_cycle(self, cycle_id: str) -> Optional[dict]:
        for c in self._data["cycles"]:
            if c["id"] == cycle_id:
                return c
        return None

    def get_cycle_by_name(self, name: str) -> Optional[dict]:
        name_l = (name or "").lower().strip()
        if not name_l:
            return None
        for c in self._data["cycles"]:
            if (c.get("name") or "").lower().strip() == name_l:
                return c
        return None

    async def async_add_cycle(self, name: str, steps: list[dict], enabled: bool = True) -> dict:
        cycle = {
            "id": uuid.uuid4().hex[:12],
            "name": name,
            "steps": [
                {
                    "entity_id": s.get("entity_id"),
                    "duration_min": int(s.get("duration_min", 1)),
                }
                for s in steps
            ],
            "enabled": bool(enabled),
            "created_at": int(time.time()),
        }
        self._data["cycles"].append(cycle)
        await self._async_save_config()
        return cycle

    async def async_update_cycle(self, cycle_id: str, **fields: Any) -> Optional[dict]:
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            return None
        if "name" in fields and fields["name"] is not None:
            cycle["name"] = fields["name"]
        if "enabled" in fields and fields["enabled"] is not None:
            cycle["enabled"] = bool(fields["enabled"])
        if "steps" in fields and fields["steps"] is not None:
            cycle["steps"] = [
                {
                    "entity_id": s.get("entity_id"),
                    "duration_min": int(s.get("duration_min", 1)),
                }
                for s in fields["steps"]
            ]
        await self._async_save_config()
        return cycle

    async def async_remove_cycle(self, cycle_id: str) -> bool:
        before = len(self._data["cycles"])
        self._data["cycles"] = [c for c in self._data["cycles"] if c["id"] != cycle_id]
        self._data["schedules"] = [
            s for s in self._data["schedules"] if s.get("cycle_id") != cycle_id
        ]
        if len(self._data["cycles"]) != before:
            await self._async_save_config()
            return True
        return False

    async def async_record_run(
        self, valve_entity_id: str, source: str, duration_min: int, status: str, note: str = "",
        liters: Optional[float] = None, planned_min: Optional[int] = None,
    ) -> None:
        entry = {
            "valve_entity_id": valve_entity_id,
            "source": source,
            "duration_min": int(duration_min),
            "status": status,
            "note": note,
            "ts": int(time.time()),
        }
        # Keep the plan's name with the row so history still reads after the plan is deleted (#57).
        cycle = self.get_cycle(valve_entity_id) if valve_entity_id else None
        if cycle is not None:
            entry["name"] = cycle.get("name", "")
        if (source or "").startswith("cycle:"):
            owner = self.get_cycle(source[6:].split("|")[0])
            if owner is not None:
                entry["plan_name"] = owner.get("name", "")
        if liters is not None:
            entry["liters"] = round(float(liters), 1)
        if planned_min is not None:
            entry["planned_min"] = int(planned_min)
        self._data["history"].insert(0, entry)
        if len(self._data["history"]) > MAX_HISTORY:
            self._data["history"] = self._data["history"][:MAX_HISTORY]
        self._async_delay_save()
