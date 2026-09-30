"""Diagnostics download (Settings → Devices & Services → Schedule Wizard → ⋮ → Download diagnostics)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {"webhook_id", "notify_targets"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    data = hass.data[DOMAIN][entry.entry_id]
    store = data["store"]
    scheduler = data["scheduler"]
    from . import _integration_version

    return {
        "version": await _integration_version(hass),
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "options": async_redact_data(dict(data["options"]), TO_REDACT),
        "valves": store.valves,
        "schedules": store.schedules,
        "cycles": store.cycles,
        "skips": store.skips,
        "active": [{k: v for k, v in r.items() if k != "unsub_close"} for r in scheduler.active.values()],
        "active_cycles": [{k: v for k, v in r.items() if k != "task"} for r in scheduler.active_cycles.values()],
        "soaking": scheduler.soaking,
        "flow": scheduler.flow_status,
        "forecast": scheduler.forecast_status,
        "voice_enabled": data.get("voice") is not None,
        "history": store.history[:100],
    }
