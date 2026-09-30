"""Binary sensor: is anything watering right now."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity_base import WizardEntity, hub_device


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([WateringBinarySensor(hass.data[DOMAIN][entry.entry_id], entry.entry_id)])


class WateringBinarySensor(WizardEntity, BinarySensorEntity):
    _attr_translation_key = "watering"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:sprinkler"

    def __init__(self, data: dict, entry_id: str):
        super().__init__(data, entry_id)
        self._attr_unique_id = f"{entry_id}_watering"
        self._attr_device_info = hub_device(entry_id)

    @property
    def is_on(self) -> bool:
        s = self.scheduler
        return bool(s.active or s.soaking or any(not c.get("paused") for c in s.active_cycles.values()))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self.scheduler
        return {
            "zones": sorted(s.active),
            "soaking": sorted(x["entity_id"] for x in s.soaking),
            "plans": sorted(c for c, st in s.active_cycles.items() if not st.get("paused")),
            "paused_plans": sorted(c for c, st in s.active_cycles.items() if st.get("paused")),
        }
