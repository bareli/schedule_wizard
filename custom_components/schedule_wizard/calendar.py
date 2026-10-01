"""Calendar entity showing upcoming watering runs (read-only)."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import planner
from .const import DOMAIN
from .entity_base import WizardEntity, hub_device

MAX_RANGE_DAYS = 62
SKIP_SUFFIX = {
    "skipped_manual": "skipped",
    "rain_delay": "paused for rain",
    "partial_rain_delay": "outdoor zones paused for rain",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([WateringCalendar(hass.data[DOMAIN][entry.entry_id], entry.entry_id)])


def _to_event(occ: dict) -> CalendarEvent:
    zones = ", ".join(f"{z['label']} {z['minutes']} min" for z in occ["zones"])
    summary = occ["name"]
    if occ["skip"]:
        summary = f"{summary} ({SKIP_SUFFIX.get(occ['skip'], occ['skip'])})"
    return CalendarEvent(
        start=dt_util.as_local(dt_util.utc_from_timestamp(occ["start"])),
        end=dt_util.as_local(dt_util.utc_from_timestamp(occ["end"])),
        summary=summary,
        description=zones,
        uid=f"{occ['schedule_id']}_{occ['day']}",
    )


class WateringCalendar(WizardEntity, CalendarEntity):
    _attr_translation_key = "schedule"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, data: dict, entry_id: str):
        super().__init__(data, entry_id)
        self._attr_unique_id = f"{entry_id}_calendar"
        self._attr_device_info = hub_device(entry_id)

    @property
    def event(self) -> CalendarEvent | None:
        now = dt_util.now()
        occs = planner.occurrences(self.store, self.scheduler.options, now - timedelta(hours=24), planner.lookahead_end(self.store, now))
        current = next((o for o in occs if o["end"] > now.timestamp()), None)
        return _to_event(current) if current else None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        end_date = min(end_date, start_date + timedelta(days=MAX_RANGE_DAYS))
        # Include runs that started before start_date but are still going. No cap: the range is (PERF-002).
        occs = planner.occurrences(
            self.store, self.scheduler.options, start_date - timedelta(days=1), end_date, limit=None,
        )
        start_ts = start_date.timestamp()
        return [_to_event(o) for o in occs if o["end"] > start_ts]
