"""#78 (SEC-009) calendar keyword, #79 (SEC-010) longest webhook / calendar run."""
from __future__ import annotations

import json
from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import FakeCalendar, advance, data, settle, setup_wizard

pytestmark = pytest.mark.usefixtures("zones")

Z1, Z2 = "input_boolean.zone1", "input_boolean.zone2"


async def _add_valve(hass, entity_id, label, **extra):
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": entity_id, "label": label, **extra}, blocking=True)


async def _calendar(hass, options: dict, summary: str, minutes: int = 10, description: str = ""):
    entry = await setup_wizard(hass, {"calendar_entity": "calendar.garden", **options})
    cal = FakeCalendar(hass)
    await _add_valve(hass, Z1, "Front lawn")
    start = dt_util.now().replace(microsecond=0) + timedelta(minutes=5)
    cal.events = [{"summary": summary, "description": description, "start": start.isoformat(),
                   "end": (start + timedelta(minutes=minutes)).isoformat()}]
    await advance(hass, 61)
    return entry


# ---------------------------------------------------------------- #78 calendar keyword

@pytest.mark.parametrize(("keyword", "summary", "runs"), [
    ("", "Front lawn", True),                      # no keyword: as before
    ("water:", "Front lawn", False),               # an invited event without the keyword
    ("water:", "Meeting about the Front lawn", False),
    ("water:", "water: Front lawn", True),
    ("water:", "Water:Front lawn", True),          # any case, space optional
    ("water:", "water: Back yard", False),         # keyword, but no zone named
])
async def test_calendar_keyword(hass: HomeAssistant, keyword, summary, runs):
    entry = await _calendar(hass, {"calendar_keyword": keyword}, summary)
    assert bool(data(hass, entry)["scheduler"]._calendar_pending) is runs


async def test_calendar_keyword_option_validated(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/update_options", "calendar_keyword": "  water:  "})
    msg = await client.receive_json()
    assert msg["success"], msg
    assert data(hass, entry)["options"]["calendar_keyword"] == "water:"
    await client.send_json({"id": 2, "type": f"{DOMAIN}/update_options", "calendar_keyword": "x" * 41})
    assert not (await client.receive_json())["success"]


# ---------------------------------------------------------------- #79 longest external run

async def _post(client, webhook_id: str, body: dict):
    resp = await client.post(f"/api/webhook/{webhook_id}", data=json.dumps(body),
                             headers={"Content-Type": "application/json"})
    return resp.status, await resp.json()


async def test_webhook_run_capped_at_default(hass: HomeAssistant, hass_client_no_auth):
    entry = await setup_wizard(hass)
    await _add_valve(hass, Z1, "Front lawn")
    client = await hass_client_no_auth()
    status, body = await _post(client, data(hass, entry)["webhook_id"], {"entity_id": Z1, "duration_minutes": 300})
    assert status == 200
    assert body["duration_minutes"] == 120 and body["shortened_from"] == 300
    run = data(hass, entry)["scheduler"].active[Z1]
    assert run["duration_min"] == 120
    started = data(hass, entry)["store"].history[0]
    assert (started["status"], started["duration_min"], started["note"]) == ("started", 120, "capped:300")


async def test_webhook_within_cap_unchanged(hass: HomeAssistant, hass_client_no_auth):
    entry = await setup_wizard(hass, {"max_external_minutes": 30})
    await _add_valve(hass, Z1, "Front lawn")
    client = await hass_client_no_auth()
    status, body = await _post(client, data(hass, entry)["webhook_id"], {"entity_id": Z1, "duration_minutes": 30})
    assert status == 200 and body["duration_minutes"] == 30 and "shortened_from" not in body
    assert data(hass, entry)["store"].history[0]["note"] == ""
    status, body = await _post(client, data(hass, entry)["webhook_id"], {"entity_id": Z2, "duration_minutes": 31})
    assert status == 404  # not a zone: unchanged


async def test_manual_runs_not_capped(hass: HomeAssistant):
    entry = await setup_wizard(hass, {"max_external_minutes": 30})
    await _add_valve(hass, Z1, "Front lawn")
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 300}, blocking=True)
    assert data(hass, entry)["scheduler"].active[Z1]["duration_min"] == 300


async def test_calendar_run_capped(hass: HomeAssistant):
    entry = await _calendar(hass, {"max_external_minutes": 45}, "Front lawn", minutes=300)
    await advance(hass, 5 * 60)
    run = data(hass, entry)["scheduler"].active[Z1]
    assert run["duration_min"] == 45
    assert run["note"].endswith("|capped:300")
    assert data(hass, entry)["store"].history[0]["note"].endswith("|capped:300")


async def test_calendar_run_within_cap(hass: HomeAssistant):
    entry = await _calendar(hass, {}, "Front lawn", minutes=20)
    await advance(hass, 5 * 60)
    run = data(hass, entry)["scheduler"].active[Z1]
    assert run["duration_min"] == 20 and "capped" not in run["note"]


async def test_cap_option_validated(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    assert data(hass, entry)["options"]["max_external_minutes"] == 120
    client = await hass_ws_client(hass)
    for i, bad in enumerate((0, 1441, "abc"), start=1):
        await client.send_json({"id": i, "type": f"{DOMAIN}/update_options", "max_external_minutes": bad})
        assert not (await client.receive_json())["success"], bad
    await client.send_json({"id": 9, "type": f"{DOMAIN}/update_options", "max_external_minutes": 240})
    assert (await client.receive_json())["success"]
    await settle(hass)
    assert data(hass, entry)["options"]["max_external_minutes"] == 240
