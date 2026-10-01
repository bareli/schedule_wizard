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


# ---------------------------------------------------------------- BUG-013 #52: actual minutes of a stopped run


async def test_stopped_run_records_actual_minutes(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front", default_duration_minutes=10)
    scheduler = data(hass, entry)["scheduler"]
    store = data(hass, entry)["store"]

    # Stopped after a few seconds: nothing worth a minute.
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1}, blocking=True)
    await hass.services.async_call(DOMAIN, "stop_valve", {"entity_id": Z1}, blocking=True)
    await settle(hass)
    row = store.history[0]
    assert row["status"] == "cancelled"
    assert row["duration_min"] == 0
    assert row["planned_min"] == 10

    # Stopped after 2 min 10 s.
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1}, blocking=True)
    scheduler.active[Z1]["started_at"] -= 130
    await hass.services.async_call(DOMAIN, "stop_valve", {"entity_id": Z1}, blocking=True)
    await settle(hass)
    row = store.history[0]
    assert (row["status"], row["duration_min"], row["planned_min"]) == ("cancelled", 2, 10)

    # Replaced after 4 minutes by a new run of the same zone.
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1}, blocking=True)
    scheduler.active[Z1]["started_at"] -= 240
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 3}, blocking=True)
    await settle(hass)
    superseded = next(h for h in store.history if h["status"] == "superseded")
    assert (superseded["duration_min"], superseded["planned_min"]) == (4, 10)
    await hass.services.async_call(DOMAIN, "stop_all", {}, blocking=True)
    await settle(hass)

    # A run that finished keeps its planned length.
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 1}, blocking=True)
    await advance(hass, 61)
    row = store.history[0]
    assert (row["status"], row["duration_min"]) == ("completed", 1)
    assert "planned_min" not in row

    # The zone line "N runs / M min last 7 days" adds what really watered.
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    stats = next(v for v in (await client.receive_json())["result"]["valves"] if v["entity_id"] == Z1)["stats"]
    assert stats["total_min_7d"] == 0 + 2 + 1 + 0  # the last stop_all row is under a minute too


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


# ---------------------------------------------------------------- PERF-003 #76: coalesced store writes


def _writes() -> int:
    mock = storage.Store._async_write_data
    return sum(1 for c in mock.call_args_list if c.args[0].key == STORE_KEY)


async def test_valve_run_writes_store_at_most_twice(hass: HomeAssistant, hass_storage):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await advance(hass, 5)
    before = _writes()

    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 1}, blocking=True)
    await settle(hass)
    # The open valve is on disk at once (restart recovery), with its history row.
    saved = hass_storage[STORE_KEY]["data"]
    assert [r["entity_id"] for r in saved["active_runs"]] == [Z1]
    assert saved["history"][0]["status"] == "started"

    await advance(hass, 61)
    await advance(hass, 5)
    assert not is_on(hass, Z1)
    assert _writes() - before <= 2
    saved = hass_storage[STORE_KEY]["data"]
    assert saved["active_runs"] == []
    assert [h["status"] for h in saved["history"][:2]] == ["completed", "started"]
    assert statuses(hass, entry, Z1)[:2] == ["completed", "started"]


async def test_delayed_rows_written_on_unload(hass: HomeAssistant, hass_storage):
    """A history row still waiting for the delayed write is on disk once the entry unloads (reload, shutdown)."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    store = data(hass, entry)["store"]
    await store.async_record_run(Z1, "manual", 0, "skipped_manual", "pending row")
    assert all(h.get("note") != "pending row" for h in hass_storage[STORE_KEY]["data"]["history"])
    assert await hass.config_entries.async_unload(entry.entry_id)
    await settle(hass)
    assert hass_storage[STORE_KEY]["data"]["history"][0]["note"] == "pending row"


# ---------------------------------------------------------------- SEC-008 #77: webhook flood limits


async def _post(client, webhook_id: str, body: dict):
    resp = await client.post(f"/api/webhook/{webhook_id}", json=body)
    return resp.status, await resp.json(), resp.headers


async def test_webhook_repeat_is_not_run_twice(hass: HomeAssistant, hass_client_no_auth):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    client = await hass_client_no_auth()
    wh = data(hass, entry)["webhook_id"]
    started = async_capture_events(hass, EVENT_VALVE_STARTED)

    first = await _post(client, wh, {"entity_id": Z1, "duration_minutes": 5})
    second = await _post(client, wh, {"entity_id": Z1, "duration_minutes": 5})
    await settle(hass)
    assert first[0] == 200 and "duplicate" not in first[1]
    assert second[0] == 200 and second[1]["duplicate"] is True
    assert len(started) == 1
    assert "superseded" not in statuses(hass, entry, Z1)

    # A different action is not a repeat.
    status, _body, _h = await _post(client, wh, {"entity_id": Z1, "action": "stop"})
    await settle(hass)
    assert status == 200 and not is_on(hass, Z1)


async def test_webhook_rate_limited_per_minute(hass: HomeAssistant, hass_client_no_auth):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    client = await hass_client_no_auth()
    wh = data(hass, entry)["webhook_id"]

    for i in range(30):
        status, _body, _h = await _post(client, wh, {"entity_id": "input_boolean.not_a_zone", "n": i})
        assert status == 404
    status, body, headers = await _post(client, wh, {"entity_id": Z1, "duration_minutes": 5})
    await settle(hass)
    assert status == 429, body
    assert int(headers["Retry-After"]) >= 1
    assert not is_on(hass, Z1)
    assert data(hass, entry)["store"].history == []
