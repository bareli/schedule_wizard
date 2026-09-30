"""Buttons: run a watering plan now."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity_base import WizardEntity, plan_device, track_plans


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    track_plans(hass, entry, data, async_add_entities, lambda key, c: [PlanRunButton(data, entry.entry_id, key)])


class PlanRunButton(WizardEntity, ButtonEntity):
    _attr_translation_key = "plan_run"
    _attr_icon = "mdi:play-circle-outline"

    def __init__(self, data: dict, entry_id: str, cycle_id: str):
        super().__init__(data, entry_id)
        self._cycle_id = cycle_id
        self._attr_unique_id = f"{entry_id}_plan_{cycle_id}_run"
        cycle = self.store.get_cycle(cycle_id) or {"id": cycle_id}
        self._attr_device_info = plan_device(entry_id, cycle)

    @property
    def available(self) -> bool:
        return self.store.get_cycle(self._cycle_id) is not None

    async def async_press(self) -> None:
        await self.scheduler.async_run_cycle(self._cycle_id, source="entity")
