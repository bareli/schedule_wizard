"""#39 (SEC-006): bounded service input and a validated notification skip day."""
from __future__ import annotations

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, settle, setup_wizard

pytestmark = pytest.mark.usefixtures("zones")

Z1, Z2, Z3 = "input_boolean.zone1", "input_boolean.zone2", "input_boolean.zone3"
OK, LONG = "x" * 80, "x" * 81


async def _call(hass, service, payload, response=False):
    return await hass.services.async_call(DOMAIN, service, payload, blocking=True, return_response=response)


async def _cycle(hass, name="Morning"):
    resp = await _call(hass, "add_cycle", {"name": name, "steps": [{"entity_id": Z1, "duration_minutes": 1}]}, True)
    return resp["cycle"]["id"]


async def _schedule(hass, **extra):
    resp = await _call(hass, "add_schedule", {"valve_entity_id": Z1, "time": "06:00", "days": ["mon"], **extra}, True)
    return resp["schedule"]["id"]


async def test_label_and_name_length(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await _call(hass, "add_valve", {"entity_id": Z1, "label": OK})
    with pytest.raises(vol.Invalid):
        await _call(hass, "add_valve", {"entity_id": Z2, "label": LONG})
    with pytest.raises(vol.Invalid):
        await _call(hass, "add_valve", {"entity_id": Z1, "label": "y" * 200000})
    assert data(hass, entry)["store"].get_valve(Z1)["label"] == OK
    assert data(hass, entry)["store"].get_valve(Z2) is None

    cid = await _cycle(hass, OK)
    with pytest.raises(vol.Invalid):
        await _cycle(hass, LONG)
    with pytest.raises(vol.Invalid):
        await _call(hass, "update_cycle", {"cycle_id": cid, "name": LONG})

    sid = await _schedule(hass, name=OK)
    with pytest.raises(vol.Invalid):
        await _schedule(hass, name=LONG)
    with pytest.raises(vol.Invalid):
        await _call(hass, "update_schedule", {"schedule_id": sid, "name": LONG})


async def test_condition_and_attribute_length(hass: HomeAssistant):
    await setup_wizard(hass)
    await _call(hass, "add_valve", {"entity_id": Z1, "label": "Front"})
    with pytest.raises(vol.Invalid):
        await _call(hass, "add_valve", {"entity_id": Z1, "label": "Front", "moisture_attribute": "a" * 256})
    with pytest.raises(vol.Invalid):
        await _schedule(hass, conditions=[{"entity_id": "sensor.x", "value": "v" * 256}])
    with pytest.raises(vol.Invalid):
        await _schedule(hass, conditions=[{"entity_id": "sensor.x", "attribute": "a" * 256, "value": "1"}])
    await _schedule(hass, conditions=[{"entity_id": "sensor.x", "attribute": "a" * 255, "value": 12.5}])


async def test_count_caps(hass: HomeAssistant, monkeypatch):
    import custom_components.schedule_wizard as sw

    monkeypatch.setattr(sw, "MAX_VALVES", 2, raising=False)
    monkeypatch.setattr(sw, "MAX_SCHEDULES", 1, raising=False)
    monkeypatch.setattr(sw, "MAX_CYCLES", 1, raising=False)
    entry = await setup_wizard(hass)
    await _call(hass, "add_valve", {"entity_id": Z1, "label": "One"})
    await _call(hass, "add_valve", {"entity_id": Z2, "label": "Two"})
    with pytest.raises(HomeAssistantError):
        await _call(hass, "add_valve", {"entity_id": Z3, "label": "Three"})
    await _call(hass, "add_valve", {"entity_id": Z1, "label": "One renamed"})  # editing is not adding
    assert [v["label"] for v in data(hass, entry)["store"].valves] == ["One renamed", "Two"]

    await _schedule(hass)
    with pytest.raises(HomeAssistantError):
        await _schedule(hass)
    await _cycle(hass)
    with pytest.raises(HomeAssistantError):
        await _cycle(hass, "Evening")


async def test_existing_long_label_still_loads(hass: HomeAssistant, hass_storage):
    label = "L" * 500
    hass_storage[f"{DOMAIN}.data"] = {
        "version": 1, "key": f"{DOMAIN}.data",
        "data": {"valves": [{"entity_id": Z1, "label": label, "default_duration_min": 10, "enabled": True}],
                 "schedules": [], "history": [], "cycles": [], "active_runs": []},
    }
    entry = await setup_wizard(hass)
    assert data(hass, entry)["store"].get_valve(Z1)["label"] == label


@pytest.mark.parametrize(("day", "stored"), [
    ("2099-01-31", True),
    ("2099-02-30", False),
    ("20990131", False),
    ("junk", False),
    ("9999-99-99", False),
    ("2099-1-5", False),
])
async def test_notification_skip_day_validated(hass: HomeAssistant, day, stored):
    entry = await setup_wizard(hass)
    await _call(hass, "add_valve", {"entity_id": Z1, "label": "Front"})
    sid = await _schedule(hass)
    hass.bus.async_fire("mobile_app_notification_action", {"action": f"SCHEDULE_WIZARD_SKIP_{sid}_{day}"})
    await settle(hass)
    assert data(hass, entry)["store"].is_skipped(sid, day) is stored
    assert (sid in data(hass, entry)["store"].skips) is stored
