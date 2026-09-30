"""Shared helpers for entity platforms: devices, and zone/plan entities that follow the stored config."""
from __future__ import annotations

from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_CONFIG_CHANGED, SIGNAL_STATE_CHANGED


def hub_device(entry_id: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Schedule Wizard",
        manufacturer="Schedule Wizard",
        entry_type=DeviceEntryType.SERVICE,
    )


def zone_identifier(entry_id: str, entity_id: str) -> tuple[str, str]:
    return (DOMAIN, f"{entry_id}_zone_{entity_id}")


def plan_identifier(entry_id: str, cycle_id: str) -> tuple[str, str]:
    return (DOMAIN, f"{entry_id}_plan_{cycle_id}")


def zone_device(entry_id: str, valve: dict) -> DeviceInfo:
    return DeviceInfo(
        identifiers={zone_identifier(entry_id, valve["entity_id"])},
        name=valve.get("label") or valve["entity_id"],
        manufacturer="Schedule Wizard",
        model="Zone",
        via_device=(DOMAIN, entry_id),
        entry_type=DeviceEntryType.SERVICE,
    )


def plan_device(entry_id: str, cycle: dict) -> DeviceInfo:
    return DeviceInfo(
        identifiers={plan_identifier(entry_id, cycle["id"])},
        name=cycle.get("name") or cycle["id"],
        manufacturer="Schedule Wizard",
        model="Watering plan",
        via_device=(DOMAIN, entry_id),
        entry_type=DeviceEntryType.SERVICE,
    )


class WizardEntity(Entity):
    """Base: refreshes on scheduler state changes and on config changes."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, data: dict, entry_id: str):
        self._data = data
        self._entry_id = entry_id

    @property
    def scheduler(self):
        return self._data["scheduler"]

    @property
    def store(self):
        return self._data["store"]

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_STATE_CHANGED, self._refresh))
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_CONFIG_CHANGED, self._refresh))

    @callback
    def _refresh(self) -> None:
        self.async_write_ha_state()


class ItemTracker:
    """Adds entities for new zones/plans and removes them (and their device) when deleted."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
        items: Callable[[], dict[str, dict]],
        factory: Callable[[str, dict], list[Entity]],
        identifier: Callable[[str, str], tuple[str, str]],
        device_name: Callable[[dict], str],
    ):
        self.hass = hass
        self.entry = entry
        self._add = async_add_entities
        self._items = items
        self._factory = factory
        self._identifier = identifier
        self._device_name = device_name
        self._entities: dict[str, list[Entity]] = {}

    @callback
    def async_start(self) -> None:
        self._sync()
        self.entry.async_on_unload(async_dispatcher_connect(self.hass, SIGNAL_CONFIG_CHANGED, self._sync))

    @callback
    def _sync(self) -> None:
        current = self._items()
        new: list[Entity] = []
        for key, item in current.items():
            if key not in self._entities:
                ents = self._factory(key, item)
                self._entities[key] = ents
                new.extend(ents)
            else:
                self._rename_device(key, item)
        if new:
            self._add(new)
        for key in [k for k in self._entities if k not in current]:
            ents = self._entities.pop(key)
            self.hass.async_create_task(self._async_remove(key, ents))

    @callback
    def _rename_device(self, key: str, item: dict) -> None:
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get_device(identifiers={self._identifier(self.entry.entry_id, key)})
        name = self._device_name(item)
        if device and device.name != name:
            dev_reg.async_update_device(device.id, name=name)

    async def _async_remove(self, key: str, ents: list[Entity]) -> None:
        ent_reg = er.async_get(self.hass)
        for ent in ents:
            if ent.entity_id and ent_reg.async_get(ent.entity_id):
                ent_reg.async_remove(ent.entity_id)
            elif ent.hass is not None:
                await ent.async_remove()
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get_device(identifiers={self._identifier(self.entry.entry_id, key)})
        if device and not er.async_entries_for_device(ent_reg, device.id, include_disabled_entities=True):
            dev_reg.async_remove_device(device.id)


def zones_by_id(data: dict) -> Callable[[], dict[str, dict]]:
    return lambda: {v["entity_id"]: v for v in data["store"].valves}


def plans_by_id(data: dict) -> Callable[[], dict[str, dict]]:
    return lambda: {c["id"]: c for c in data["store"].cycles}


def track_zones(hass, entry, data, async_add_entities, factory) -> None:
    ItemTracker(
        hass, entry, async_add_entities, zones_by_id(data), factory, zone_identifier,
        lambda v: v.get("label") or v["entity_id"],
    ).async_start()


def track_plans(hass, entry, data, async_add_entities, factory) -> None:
    ItemTracker(
        hass, entry, async_add_entities, plans_by_id(data), factory, plan_identifier,
        lambda c: c.get("name") or c["id"],
    ).async_start()


def remaining_seconds(scheduler, entity_id: str, now: float) -> int:
    run = scheduler.active.get(entity_id)
    if run and not run.get("starting"):
        return max(0, int(run.get("ends_at", 0) - now))
    return 0


def zone_state(scheduler, entity_id: str) -> dict[str, Any]:
    run = scheduler.active.get(entity_id)
    soak = next((s for s in scheduler.soaking if s.get("entity_id") == entity_id), None)
    return {"run": run, "soak": soak}
