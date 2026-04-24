"""Sensor entities for Schedule Wizard."""
from __future__ import annotations

import time
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_STATE_CHANGED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ActiveRunsSensor(entry.entry_id, data["scheduler"], data["store"]),
        NextScheduleSensor(entry.entry_id, data["store"]),
    ])


class ActiveRunsSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Active runs"
    _attr_icon = "mdi:sprinkler"
    _attr_should_poll = False

    def __init__(self, entry_id: str, scheduler, store):
        self._scheduler = scheduler
        self._store = store
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_active_runs"
        self._unsub = None

    @property
    def native_value(self) -> int:
        return len(self._scheduler.active)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        now = int(time.time())
        runs = []
        for run in self._scheduler.active.values():
            runs.append({
                "entity_id": run["entity_id"],
                "source": run["source"],
                "started_at": run["started_at"],
                "ends_at": run["ends_at"],
                "remaining_seconds": max(0, run["ends_at"] - now),
                "duration_min": run["duration_min"],
            })
        return {
            "runs": runs,
            "valves": len(self._store.valves),
            "schedules": len(self._store.schedules),
        }

    async def async_added_to_hass(self) -> None:
        self._unsub = async_dispatcher_connect(
            self.hass, SIGNAL_STATE_CHANGED, self._handle_signal
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()

    @callback
    def _handle_signal(self) -> None:
        self.async_write_ha_state()


class NextScheduleSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Next schedule"
    _attr_icon = "mdi:calendar-clock"
    _attr_should_poll = True

    def __init__(self, entry_id: str, store):
        self._store = store
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_next_schedule"

    @property
    def native_value(self) -> str | None:
        nxt = self._compute_next()
        return nxt["time_label"] if nxt else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        nxt = self._compute_next() or {}
        return {
            "valve_entity_id": nxt.get("valve_entity_id", ""),
            "schedule_id": nxt.get("schedule_id", ""),
            "duration_min": nxt.get("duration_min", 0),
            "fires_in_minutes": nxt.get("fires_in_minutes", -1),
        }

    def _compute_next(self) -> dict | None:
        from datetime import datetime, timedelta
        now = datetime.now()
        best = None
        best_delta = None
        for s in self._store.schedules:
            if not s.get("enabled"):
                continue
            try:
                hh, mm = [int(x) for x in s["time_hhmm"].split(":")]
            except Exception:
                continue
            mask = int(s.get("days_mask", 0))
            for delta_days in range(0, 8):
                check = now + timedelta(days=delta_days)
                bit = 1 << check.weekday()
                if not (mask & bit):
                    continue
                fire = check.replace(hour=hh, minute=mm, second=0, microsecond=0)
                if fire <= now:
                    continue
                delta = fire - now
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best = {
                        "valve_entity_id": s["valve_entity_id"],
                        "schedule_id": s["id"],
                        "duration_min": s["duration_min"],
                        "fires_in_minutes": int(delta.total_seconds() // 60),
                        "time_label": fire.strftime("%a %H:%M"),
                    }
                break
        return best
