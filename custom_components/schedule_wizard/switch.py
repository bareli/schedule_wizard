"""Switches: water a zone, enable a watering plan, global rain delay."""
from __future__ import annotations

import time
from datetime import timedelta
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_RAIN_DELAY_UNTIL, DOMAIN, EVENT_RAIN_DELAY_SET
from .entity_base import WizardEntity, hub_device, plan_device, track_plans, track_zones, zone_device
from . import planner

SCAN_INTERVAL = timedelta(seconds=30)
RAIN_DELAY_HOURS = 24


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RainDelaySwitch(data, entry)])
    track_zones(hass, entry, data, async_add_entities, lambda key, v: [ZoneWateringSwitch(data, entry.entry_id, key)])
    track_plans(hass, entry, data, async_add_entities, lambda key, c: [PlanEnabledSwitch(data, entry.entry_id, key)])


class ZoneWateringSwitch(WizardEntity, SwitchEntity):
    """On while the zone waters (including soak pauses). Turn on = water for its default minutes."""

    _attr_translation_key = "zone_watering"
    _attr_icon = "mdi:sprinkler-variant"

    def __init__(self, data: dict, entry_id: str, zone: str):
        super().__init__(data, entry_id)
        self._zone = zone
        self._attr_unique_id = f"{entry_id}_zone_{zone}_watering"
        valve = self.store.get_valve(zone) or {"entity_id": zone}
        self._attr_device_info = zone_device(entry_id, valve)

    @property
    def available(self) -> bool:
        return self.store.get_valve(self._zone) is not None

    @property
    def is_on(self) -> bool:
        return self._zone in self.scheduler.active or any(
            s.get("entity_id") == self._zone for s in self.scheduler.soaking
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        run = self.scheduler.active.get(self._zone) or {}
        valve = self.store.get_valve(self._zone) or {}
        return {
            "valve_entity_id": self._zone,
            "default_minutes": valve.get("default_duration_min"),
            "ends_at": run.get("ends_at"),
            "source": run.get("source"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        valve = self.store.get_valve(self._zone) or {}
        minutes = int(valve.get("default_duration_min") or self.scheduler.options.get("default_duration") or 10)
        await self.scheduler.async_run_valve(self._zone, minutes, source="entity")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.scheduler.async_stop_valve(self._zone)


class PlanEnabledSwitch(WizardEntity, SwitchEntity):
    """A watering plan's on/off: off means its schedules don't run."""

    _attr_translation_key = "plan_enabled"
    _attr_icon = "mdi:calendar-check"

    def __init__(self, data: dict, entry_id: str, cycle_id: str):
        super().__init__(data, entry_id)
        self._cycle_id = cycle_id
        self._attr_unique_id = f"{entry_id}_plan_{cycle_id}_enabled"
        cycle = self.store.get_cycle(cycle_id) or {"id": cycle_id}
        self._attr_device_info = plan_device(entry_id, cycle)

    @property
    def available(self) -> bool:
        return self.store.get_cycle(self._cycle_id) is not None

    @property
    def is_on(self) -> bool:
        return bool((self.store.get_cycle(self._cycle_id) or {}).get("enabled"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        occ = next(
            (o for o in planner.occurrences(self.store, self.scheduler.options, dt_util.now(), dt_util.now() + timedelta(days=8))
             if o["kind"] == "cycle" and o["target"] == self._cycle_id),
            None,
        )
        state = self.scheduler.active_cycles.get(self._cycle_id)
        return {
            "cycle_id": self._cycle_id,
            "next_run": _iso(occ["start"]) if occ else None,
            "running": bool(state and not state.get("paused")),
            "paused": bool(state and state.get("paused")),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.store.async_update_cycle(self._cycle_id, enabled=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.store.async_update_cycle(self._cycle_id, enabled=False)


class RainDelaySwitch(WizardEntity, SwitchEntity):
    """On while the global rain delay is active. Turn on = pause for 24 hours."""

    _attr_translation_key = "rain_delay"
    _attr_icon = "mdi:weather-pouring"
    _attr_should_poll = True

    def __init__(self, data: dict, entry: ConfigEntry):
        super().__init__(data, entry.entry_id)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_rain_delay"
        self._attr_device_info = hub_device(entry.entry_id)

    @property
    def is_on(self) -> bool:
        return bool(self.scheduler._is_rain_delay_active())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        until = self.scheduler._is_rain_delay_active()
        return {"until": _iso(until) if until else None}

    async def _set(self, until: int, hours: float) -> None:
        self.hass.config_entries.async_update_entry(
            self._entry, options={**self._entry.options, CONF_RAIN_DELAY_UNTIL: until}
        )
        self.hass.bus.async_fire(EVENT_RAIN_DELAY_SET, {"until": until, "hours": hours})

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set(int(time.time()) + RAIN_DELAY_HOURS * 3600, RAIN_DELAY_HOURS)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set(0, 0)



def _iso(ts: int) -> str:
    return dt_util.as_local(dt_util.utc_from_timestamp(ts)).isoformat()
