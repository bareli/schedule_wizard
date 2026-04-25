"""Persistent storage for valves, schedules, and run history."""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION

MAX_HISTORY = 500


class WizardStore:
    def __init__(self, hass: HomeAssistant):
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {
            "valves": [],
            "schedules": [],
            "history": [],
            "active_runs": [],
            "cycles": [],
        }
        self._loaded = False

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data:
            self._data["valves"] = data.get("valves", [])
            self._data["schedules"] = data.get("schedules", [])
            self._data["history"] = data.get("history", [])
            self._data["active_runs"] = data.get("active_runs", [])
            self._data["cycles"] = data.get("cycles", [])
        self._loaded = True

    async def async_save(self) -> None:
        await self._store.async_save(self._data)

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

    async def async_set_active_runs(self, runs: list[dict]) -> None:
        self._data["active_runs"] = list(runs)
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
    ) -> dict:
        existing = self.get_valve(entity_id)
        if existing:
            existing.update({
                "label": label,
                "default_duration_min": int(default_duration_min),
                "enabled": bool(enabled),
            })
            await self.async_save()
            return existing
        valve = {
            "entity_id": entity_id,
            "label": label,
            "default_duration_min": int(default_duration_min),
            "enabled": bool(enabled),
            "created_at": int(time.time()),
        }
        self._data["valves"].append(valve)
        await self.async_save()
        return valve

    async def async_remove_valve(self, entity_id: str) -> bool:
        before = len(self._data["valves"])
        self._data["valves"] = [v for v in self._data["valves"] if v["entity_id"] != entity_id]
        self._data["schedules"] = [s for s in self._data["schedules"] if s.get("valve_entity_id") != entity_id]
        if len(self._data["valves"]) != before:
            await self.async_save()
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
    ) -> dict:
        sched = {
            "id": uuid.uuid4().hex[:12],
            "valve_entity_id": valve_entity_id or "",
            "cycle_id": cycle_id or "",
            "name": name,
            "days_mask": int(days_mask),
            "time_hhmm": time_hhmm,
            "duration_min": int(duration_min),
            "enabled": bool(enabled),
            "created_at": int(time.time()),
        }
        self._data["schedules"].append(sched)
        await self.async_save()
        return sched

    async def async_update_schedule(self, schedule_id: str, **fields: Any) -> Optional[dict]:
        sched = self.get_schedule(schedule_id)
        if not sched:
            return None
        for k in ("name", "days_mask", "time_hhmm", "duration_min", "enabled"):
            if k in fields and fields[k] is not None:
                if k in ("days_mask", "duration_min"):
                    sched[k] = int(fields[k])
                elif k == "enabled":
                    sched[k] = bool(fields[k])
                else:
                    sched[k] = fields[k]
        await self.async_save()
        return sched

    async def async_remove_schedule(self, schedule_id: str) -> bool:
        before = len(self._data["schedules"])
        self._data["schedules"] = [s for s in self._data["schedules"] if s["id"] != schedule_id]
        if len(self._data["schedules"]) != before:
            await self.async_save()
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
        await self.async_save()
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
        await self.async_save()
        return cycle

    async def async_remove_cycle(self, cycle_id: str) -> bool:
        before = len(self._data["cycles"])
        self._data["cycles"] = [c for c in self._data["cycles"] if c["id"] != cycle_id]
        self._data["schedules"] = [
            s for s in self._data["schedules"] if s.get("cycle_id") != cycle_id
        ]
        if len(self._data["cycles"]) != before:
            await self.async_save()
            return True
        return False

    async def async_record_run(self, valve_entity_id: str, source: str, duration_min: int, status: str, note: str = "") -> None:
        entry = {
            "valve_entity_id": valve_entity_id,
            "source": source,
            "duration_min": int(duration_min),
            "status": status,
            "note": note,
            "ts": int(time.time()),
        }
        self._data["history"].insert(0, entry)
        if len(self._data["history"]) > MAX_HISTORY:
            self._data["history"] = self._data["history"][:MAX_HISTORY]
        await self.async_save()
