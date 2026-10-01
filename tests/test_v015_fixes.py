"""v0.15.0 regressions: BUG-013 #52, BUG-014 #53, BUG-016 #55, PERF-001 #74, PERF-002 #75, PERF-003 #76, SEC-008 #77."""
from __future__ import annotations

import json
import re
from datetime import timedelta
from pathlib import Path

import pytest
import voluptuous as vol
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import storage
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_capture_events

from custom_components.schedule_wizard.const import DOMAIN, EVENT_VALVE_STARTED

from .conftest import advance, data, is_on, settle, setup_wizard
from .test_scheduler import Z1, Z2, add_valve, statuses

pytestmark = pytest.mark.usefixtures("zones")

STORE_KEY = f"{DOMAIN}.data"
WWW = Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www"
PANEL = (WWW / "panel.js").read_text(encoding="utf-8")


def _method(src: str, name: str) -> str:
    match = re.search(rf"\n  (?:async )?{name}\([^)]*\) {{\n(.*?)\n  }}\n", src, re.S)
    assert match, f"{name} not found"
    return match.group(1)


# ---------------------------------------------------------------- BUG-014 #53: one voice command, one start


@pytest.mark.parametrize(("lang", "label", "text", "minutes"), [
    ("en", "Front lawn", "water front lawn for 2 minutes", 2),
    ("en", "Front lawn", "water the front lawn for 2 minutes", 2),
    ("en", "Front lawn", "water front lawn", 10),
    ("de", "Rasen", "bewässere Rasen für 1 Minuten", 1),
    ("de", "Rasen", "bewässere den Rasen für 3 Minuten", 3),
    ("he", "דשא", "תשקה את הדשא 4 דקות", 4),
])
async def test_voice_starts_zone_once(hass: HomeAssistant, lang, label, text, minutes):
    pytest.importorskip("hassil")
    from homeassistant.components import conversation

    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "conversation", {})
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, label, default_duration_minutes=10)
    await settle(hass)
    started = async_capture_events(hass, EVENT_VALVE_STARTED)

    await conversation.async_converse(hass, text, None, Context(), language=lang)
    await settle(hass)

    assert len(started) == 1, [e.data for e in started]
    assert started[0].data["duration_min"] == minutes
    assert statuses(hass, entry, Z1) == ["started"]
    await hass.services.async_call(DOMAIN, "stop_all", {}, blocking=True)
    await settle(hass)
