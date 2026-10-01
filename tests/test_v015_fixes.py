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


# ---------------------------------------------------------------- BUG-016 #55: zone minutes 0 / empty


async def test_add_valve_rejects_zero_minutes_and_keeps_value(hass: HomeAssistant):
    """Server side: 0 or 1441 minutes is refused and the stored value stays."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front", default_duration_minutes=45)
    for bad in (0, -5, 1441):
        with pytest.raises(vol.Invalid):
            await add_valve(hass, Z1, "Front", default_duration_minutes=bad)
    assert data(hass, entry)["store"].get_valve(Z1)["default_duration_min"] == 45


def test_zone_editor_validates_minutes_inline():
    """Panel: no silent fallback to 10; an inline error under Minutes per run and the dialog stays open."""
    body = _method(PANEL, "_openValveModal")
    assert "|| 10;" not in body
    assert 'id: "sw-valve-duration-err"' in body
    save = body[body.index("this._showModal("):]
    check = save.index("minutesValue(durInput.value)")
    assert save.index('this._t("valves.err_duration")', check) < save.index('this._callService("add_valve"')
    assert "return false;" in save[check:save.index('this._callService("add_valve"')]
    assert "default_duration_minutes: duration," in save


def test_schedule_editor_validates_minutes_inline():
    body = _method(PANEL, "_openScheduleModal")
    assert "parseInt(durInput.value, 10) || 10" not in body
    assert 'id: "sw-sched-duration-err"' in body
    assert 'setErr(durErr, durInput, this._t("valves.err_duration"))' in body


def test_minutes_value_rules():
    """The panel's minutesValue() under Node: whole minutes 1 to 1440, else null."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    fn = re.search(r"\nfunction minutesValue\(raw\) \{\n.*?\n\}\n", PANEL, re.S)
    assert fn, "minutesValue() not found in panel.js"
    cases = ["0", "", " ", "-5", "2000", "1441", "1.5", "abc", "1", "45", "1440"]
    script = fn.group(0) + f"process.stdout.write(JSON.stringify({json.dumps(cases)}.map(minutesValue)));"
    out = subprocess.run(["node", "-e", script], capture_output=True, check=True, timeout=30)
    assert json.loads(out.stdout) == [None] * 8 + [1, 45, 1440]


# ---------------------------------------------------------------- PERF-002 #75: calendar range not capped


async def test_calendar_returns_every_occurrence_in_range(hass: HomeAssistant):
    await setup_wizard(hass)
    every_day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for i in range(20):
        zone = f"switch.zone_{i:02d}"
        await add_valve(hass, zone, f"Zone {i:02d}")
        await hass.services.async_call(
            DOMAIN, "add_schedule",
            {"valve_entity_id": zone, "time": f"{4 + i // 6:02d}:{(i % 6) * 10:02d}", "days": every_day,
             "duration_minutes": 5},
            blocking=True,
        )
    await settle(hass)
    start = dt_util.start_of_local_day() + timedelta(days=1)
    resp = await hass.services.async_call(
        "calendar", "get_events",
        {"entity_id": "calendar.schedule_wizard_watering_schedule", "start_date_time": start.isoformat(),
         "end_date_time": (start + timedelta(days=62)).isoformat()},
        blocking=True, return_response=True,
    )
    events = resp["calendar.schedule_wizard_watering_schedule"]["events"]
    assert len(events) == 20 * 62
    days = sorted({e["start"][:10] for e in events})
    assert len(days) == 62
    assert days[-1] == (start + timedelta(days=61)).date().isoformat()
