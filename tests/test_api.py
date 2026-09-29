"""WebSocket API and sensor tests."""
from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import setup_wizard

pytestmark = pytest.mark.usefixtures("zones")


async def test_get_state_includes_new_fields(hass: HomeAssistant, hass_ws_client):
    await setup_wizard(hass, {"flow_entity": "sensor.flow"})
    hass.states.async_set("sensor.flow", "1.5")
    await hass.services.async_call(
        DOMAIN, "add_valve",
        {"entity_id": "input_boolean.zone1", "label": "Front", "soak_run_minutes": 5, "soak_pause_minutes": 10},
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN, "add_schedule",
        {"valve_entity_id": "input_boolean.zone1", "time": "06:00", "days": ["mon", "thu"], "duration_minutes": 10},
        blocking=True, return_response=True,
    )
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    msg = await client.receive_json()
    assert msg["success"], msg
    result = msg["result"]
    assert result["soaking"] == []
    assert result["flow"] == {"entity_id": "sensor.flow", "value": 1.5, "alert": None}
    valve = result["valves"][0]
    assert valve["soak_run_min"] == 5 and valve["soak_pause_min"] == 10
    assert valve["next_run"]["time_label"].endswith("06:00")
    assert result["schedules"][0]["conditions"] == []


async def test_update_options_requires_admin(hass: HomeAssistant, hass_ws_client, hass_read_only_access_token):
    await setup_wizard(hass)
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/update_options", "default_duration": 5})
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "unauthorized"


async def test_update_options_applies_in_place(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    scheduler = hass.data[DOMAIN][entry.entry_id]["scheduler"]
    client = await hass_ws_client(hass)
    await client.send_json({
        "id": 1, "type": f"{DOMAIN}/update_options",
        "poll_interval": 120, "flow_entity": "sensor.flow", "flow_leak_threshold": 0.3,
    })
    msg = await client.receive_json()
    assert msg["success"], msg
    await hass.async_block_till_done()
    assert hass.data[DOMAIN][entry.entry_id]["scheduler"] is scheduler
    assert scheduler._poll_seconds == 120
    assert scheduler.options["flow_leak_threshold"] == 0.3
    assert scheduler._unsub_flow is not None


async def test_sensor_entity_ids(hass: HomeAssistant):
    await setup_wizard(hass)
    assert hass.states.get("sensor.schedule_wizard_active_runs") is not None
    assert hass.states.get("sensor.schedule_wizard_next_schedule") is not None


async def test_panel_payloads_accepted(hass: HomeAssistant, hass_ws_client):
    """Payloads captured from panel.js v0.8.0 (valve modal, schedule modal, settings save)."""
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {
        "entity_id": "input_boolean.zone1", "label": "Front lawn", "default_duration_minutes": 10,
        "enabled": True, "soak_run_minutes": 4, "soak_pause_minutes": 3,
        "moisture_entity": "sensor.m1", "moisture_attribute": "", "moisture_threshold": 40,
    }, blocking=True)
    await hass.services.async_call(DOMAIN, "add_valve", {
        "entity_id": "input_boolean.zone2", "label": "Back", "default_duration_minutes": 5,
        "enabled": True, "soak_run_minutes": 0, "soak_pause_minutes": 0,
        "moisture_entity": "", "moisture_attribute": "", "moisture_threshold": None,
    }, blocking=True)
    resp = await hass.services.async_call(DOMAIN, "add_schedule", {
        "valve_entity_id": "input_boolean.zone1", "time": "06:00", "days": ["mon", "thu"],
        "duration_minutes": 10, "name": "Morning", "enabled": True,
        "conditions": [{"entity_id": "sensor.temp", "attribute": "", "operator": "above", "value": "12"}],
    }, blocking=True, return_response=True)
    sid = resp["schedule"]["id"]
    await hass.services.async_call(DOMAIN, "update_schedule", {
        "schedule_id": sid, "name": "Morning", "time": "06:00", "duration_minutes": 10,
        "days": ["mon", "thu"], "enabled": True,
        "conditions": [
            {"entity_id": "sensor.temp", "attribute": "", "operator": "above", "value": "12"},
            {"entity_id": "input_boolean.vacation", "attribute": "", "operator": "equals", "value": "off"},
        ],
    }, blocking=True, return_response=True)
    store = hass.data[DOMAIN][entry.entry_id]["store"]
    assert len(store.get_schedule(sid)["conditions"]) == 2
    valve = store.get_valve("input_boolean.zone1")
    assert (valve["soak_run_min"], valve["soak_pause_min"], valve["moisture_threshold"]) == (4, 3, 40.0)
    assert store.get_valve("input_boolean.zone2")["moisture_threshold"] is None

    client = await hass_ws_client(hass)
    await client.send_json({
        "id": 1, "type": f"{DOMAIN}/update_options",
        "calendar_entity": "", "calendar_lookahead_min": 10, "poll_interval": 60, "default_duration": 10,
        "rain_entity": "", "rain_skip_states": "", "rain_attribute": "", "rain_threshold": None,
        "notify_targets": [], "notify_events": [], "seasonal_enabled": False,
        "seasonal_temp_entity": "sensor.temp", "seasonal_temp_attribute": "",
        "seasonal_temp_low": 10, "seasonal_temp_high": 30, "seasonal_min_pct": 50, "seasonal_max_pct": 120,
        "allow_concurrent_cycles": False, "moisture_entity": "", "moisture_attribute": "",
        "moisture_threshold_skip_above": None, "master_valve_entity": "", "master_valve_pre_open_sec": 0,
        "fail_detection_enabled": False, "fail_detection_seconds": 5,
        "flow_entity": "sensor.flow", "flow_attribute": "", "flow_leak_threshold": 0.5,
        "flow_max_running": 20, "flow_delay_sec": 60, "flow_stop_all": True,
    })
    msg = await client.receive_json()
    assert msg["success"], msg
