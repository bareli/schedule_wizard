"""Sensor entities for Schedule Wizard."""
from __future__ import annotations

import time
from typing import Any

from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_STATE_CHANGED
from .entity_base import WizardEntity, hub_device, track_zones, zone_device

SCAN_INTERVAL = timedelta(seconds=30)


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
    track_zones(hass, entry, data, async_add_entities, lambda key, v: [ZoneTimeLeftSensor(data, entry.entry_id, key)])


def _device_info(entry_id: str):
    return hub_device(entry_id)


class ZoneTimeLeftSensor(WizardEntity, SensorEntity):
    """Minutes left for a zone (0 when idle). Polled every 30 s while it counts down."""

    _attr_translation_key = "zone_time_left"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:timer-sand"
    _attr_should_poll = True

    def __init__(self, data: dict, entry_id: str, zone: str):
        super().__init__(data, entry_id)
        self._zone = zone
        self._attr_unique_id = f"{entry_id}_zone_{zone}_time_left"
        valve = self.store.get_valve(zone) or {"entity_id": zone}
        self._attr_device_info = zone_device(entry_id, valve)

    @property
    def available(self) -> bool:
        return self.store.get_valve(self._zone) is not None

    @property
    def native_value(self) -> int:
        run = self.scheduler.active.get(self._zone)
        if not run or run.get("starting"):
            return 0
        return max(0, -(-(int(run.get("ends_at", 0)) - int(time.time())) // 60))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        soak = next((x for x in self.scheduler.soaking if x.get("entity_id") == self._zone), None)
        return {
            "valve_entity_id": self._zone,
            "soaking": bool(soak and soak.get("phase") == "soaking"),
            "resumes_at": soak.get("resume_at") if soak else None,
        }


class ActiveRunsSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Active runs"
    _attr_icon = "mdi:sprinkler"
    _attr_should_poll = False

    def __init__(self, entry_id: str, scheduler, store):
        self._scheduler = scheduler
        self._store = store
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_active_runs"
        self._attr_device_info = _device_info(entry_id)
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
        self._attr_device_info = _device_info(entry_id)

    @property
    def native_value(self) -> str | None:
        nxt = self._compute_next()
        return nxt["time_label"] if nxt else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        nxt = self._compute_next() or {}
        return {
            "valve_entity_id": nxt.get("valve_entity_id", ""),
            "cycle_id": nxt.get("cycle_id", ""),
            "schedule_id": nxt.get("schedule_id", ""),
            "duration_min": nxt.get("duration_min", 0),
            "fires_in_minutes": nxt.get("fires_in_minutes", -1),
        }

    def _compute_next(self) -> dict | None:
        from datetime import timedelta
        now = dt_util.now()
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
                        "valve_entity_id": s.get("valve_entity_id", ""),
                        "cycle_id": s.get("cycle_id", ""),
                        "schedule_id": s["id"],
                        "duration_min": s["duration_min"],
                        "fires_in_minutes": int(delta.total_seconds() // 60),
                        "time_label": fire.strftime("%a %H:%M"),
                    }
                break
        return best
