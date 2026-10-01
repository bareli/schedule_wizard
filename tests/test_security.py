"""Webhook and options hardening (SEC-001..004, SEC-007; issues #34 #35 #36 #37 #40)."""
from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, is_on, settle, setup_wizard

pytestmark = pytest.mark.usefixtures("zones")

Z1, Z2, MASTER = "input_boolean.zone1", "input_boolean.zone2", "input_boolean.master"


async def _add_valve(hass: HomeAssistant, entity_id: str, label: str, **extra) -> None:
    await hass.services.async_call(
        DOMAIN, "add_valve", {"entity_id": entity_id, "label": label, **extra}, blocking=True
    )


async def _post(client, webhook_id: str, body: str):
    resp = await client.post(
        f"/api/webhook/{webhook_id}", data=body, headers={"Content-Type": "application/json"}
    )
    text = await resp.text()
    return resp.status, text


async def _stop_runs(hass: HomeAssistant) -> None:
    await hass.services.async_call(DOMAIN, "stop_all", {}, blocking=True)
    await settle(hass)


# ---------------------------------------------------------------- #34 / #37: configured zones only


async def test_webhook_rejects_unregistered_zone(hass: HomeAssistant, hass_client_no_auth):
    """#34: an entity that is not a zone is neither turned on nor recorded."""
    entry = await setup_wizard(hass)
    client = await hass_client_no_auth()
    wh = data(hass, entry)["webhook_id"]
    store = data(hass, entry)["store"]

    status, text = await _post(client, wh, '{"entity_id": "input_boolean.zone1", "duration_minutes": 5}')
    await settle(hass)
    assert status == 404, text
    assert not is_on(hass, Z1)
    assert store.history == []
    assert data(hass, entry)["scheduler"].active == {}


async def test_webhook_stop_rejects_unregistered_zone(hass: HomeAssistant, hass_client_no_auth):
    """#34: stop of a non-zone entity does not turn it off."""
    entry = await setup_wizard(hass)
    await hass.services.async_call("input_boolean", "turn_on", {"entity_id": Z2}, blocking=True)
    client = await hass_client_no_auth()

    status, text = await _post(client, data(hass, entry)["webhook_id"], '{"entity_id": "input_boolean.zone2", "action": "stop"}')
    assert status == 404, text
    assert is_on(hass, Z2)


async def test_webhook_rejects_missing_entity_without_history(hass: HomeAssistant, hass_client_no_auth):
    """#37: an entity that does not exist writes no history row, registered as a zone or not."""
    entry = await setup_wizard(hass)
    await _add_valve(hass, "switch.gone", "Gone")
    client = await hass_client_no_auth()
    wh = data(hass, entry)["webhook_id"]
    store = data(hass, entry)["store"]

    for body in (
        '{"entity_id": "switch.does_not_exist", "duration_minutes": 1}',
        '{"entity_id": "switch.gone", "duration_minutes": 1}',
    ):
        status, text = await _post(client, wh, body)
        assert status == 404, (body, text)
    await settle(hass)
    assert store.history == []
    assert data(hass, entry)["scheduler"].active == {}


async def test_webhook_rejects_disabled_zone(hass: HomeAssistant, hass_client_no_auth):
    entry = await setup_wizard(hass)
    await _add_valve(hass, Z1, "Front", enabled=False)
    client = await hass_client_no_auth()

    status, text = await _post(client, data(hass, entry)["webhook_id"], '{"entity_id": "input_boolean.zone1"}')
    await settle(hass)
    assert status == 409, text
    assert not is_on(hass, Z1)
    assert data(hass, entry)["store"].history == []


async def test_webhook_runs_and_stops_registered_zone(hass: HomeAssistant, hass_client_no_auth):
    """Existing automations that target a zone keep working."""
    entry = await setup_wizard(hass)
    await _add_valve(hass, Z1, "Front")
    client = await hass_client_no_auth()
    wh = data(hass, entry)["webhook_id"]

    status, text = await _post(client, wh, '{"entity_id": "input_boolean.zone1", "duration_minutes": 5}')
    await settle(hass)
    assert status == 200, text
    assert is_on(hass, Z1)

    status, text = await _post(client, wh, '{"entity_id": "input_boolean.zone1", "action": "stop"}')
    await settle(hass)
    assert status == 200, text
    assert not is_on(hass, Z1)


# ---------------------------------------------------------------- #36: malformed payloads


@pytest.mark.parametrize("body", [
    "[1, 2]",
    '"abc"',
    "5",
    "null",
    '{"entity_id": "input_boolean.zone1", "action": 123}',
    '{"entity_id": "input_boolean.zone1", "action": "explode"}',
    '{"entity_id": ["input_boolean.zone1"]}',
    '{"entity_id": "input_boolean.zone1", "duration_minutes": Infinity}',
    '{"entity_id": "input_boolean.zone1", "duration_minutes": "ten"}',
])
async def test_webhook_malformed_payload_is_400(hass: HomeAssistant, hass_client_no_auth, body):
    entry = await setup_wizard(hass)
    await _add_valve(hass, Z1, "Front")
    client = await hass_client_no_auth()

    status, text = await _post(client, data(hass, entry)["webhook_id"], body)
    await settle(hass)
    assert status == 400, text
    assert "attribute" not in text and "Traceback" not in text
    assert not is_on(hass, Z1)
    await _stop_runs(hass)


async def test_webhook_internal_error_is_generic(hass: HomeAssistant, hass_client_no_auth):
    entry = await setup_wizard(hass)
    await _add_valve(hass, Z1, "Front")
    client = await hass_client_no_auth()
    scheduler = data(hass, entry)["scheduler"]

    async def _boom(*_a, **_kw):
        raise RuntimeError("secret detail /config/.storage")

    scheduler.async_run_valve = _boom
    status, text = await _post(client, data(hass, entry)["webhook_id"], '{"entity_id": "input_boolean.zone1"}')
    assert status == 500
    assert "secret detail" not in text


# ---------------------------------------------------------------- #35: webhook id admin only, rotation


async def _ws(client, msg_id: int, payload: dict) -> dict:
    await client.send_json({"id": msg_id, **payload})
    return await client.receive_json()


async def test_get_state_hides_webhook_from_non_admin(
    hass: HomeAssistant, hass_ws_client, hass_read_only_access_token,
):
    entry = await setup_wizard(hass, {"notify_targets": ["mobile_app_phone"]})
    wh = data(hass, entry)["webhook_id"]

    user = await hass_ws_client(hass, hass_read_only_access_token)
    msg = await _ws(user, 1, {"type": f"{DOMAIN}/get_state"})
    assert msg["success"], msg
    assert msg["result"]["webhook_id"] == ""
    assert "notify_targets" not in msg["result"]["options"]
    assert wh not in str(msg["result"])
    # The shared runtime options were not stripped for everyone else.
    assert data(hass, entry)["options"]["notify_targets"] == ["mobile_app_phone"]

    admin = await hass_ws_client(hass)
    msg = await _ws(admin, 1, {"type": f"{DOMAIN}/get_state"})
    assert msg["result"]["webhook_id"] == wh
    assert msg["result"]["options"]["notify_targets"] == ["mobile_app_phone"]


async def test_rotate_webhook_requires_admin(hass: HomeAssistant, hass_ws_client, hass_read_only_access_token):
    entry = await setup_wizard(hass)
    wh = data(hass, entry)["webhook_id"]
    user = await hass_ws_client(hass, hass_read_only_access_token)
    msg = await _ws(user, 1, {"type": f"{DOMAIN}/rotate_webhook"})
    assert not msg["success"]
    assert msg["error"]["code"] == "unauthorized"
    assert data(hass, entry)["webhook_id"] == wh


async def test_rotate_webhook(hass: HomeAssistant, hass_ws_client, hass_client_no_auth):
    entry = await setup_wizard(hass)
    await _add_valve(hass, Z1, "Front")
    old = data(hass, entry)["webhook_id"]
    admin = await hass_ws_client(hass)
    client = await hass_client_no_auth()

    msg = await _ws(admin, 1, {"type": f"{DOMAIN}/rotate_webhook"})
    assert msg["success"], msg
    new = msg["result"]["webhook_id"]
    assert new and new != old and len(new) == 32
    assert data(hass, entry)["webhook_id"] == new
    assert entry.data["webhook_id"] == new

    # Old URL no longer reaches the handler (HA answers unknown ids with an empty 200).
    status, text = await _post(client, old, '{"entity_id": "input_boolean.zone1", "duration_minutes": 5}')
    await settle(hass)
    assert status == 200 and text == ""
    assert not is_on(hass, Z1)

    status, text = await _post(client, new, '{"entity_id": "input_boolean.zone1", "duration_minutes": 5}')
    await settle(hass)
    assert status == 200, text
    assert is_on(hass, Z1)
    await _stop_runs(hass)

    # The new id survives a reload.
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert data(hass, entry)["webhook_id"] == new


# ---------------------------------------------------------------- #40: master valve validation


@pytest.mark.parametrize("value", ["script.qa_not_a_valve", "climate.living_room", "switch.does_not_exist", "not an id"])
async def test_update_options_rejects_bad_master_valve(hass: HomeAssistant, hass_ws_client, value):
    entry = await setup_wizard(hass)
    hass.states.async_set("script.qa_not_a_valve", "off")
    hass.states.async_set("climate.living_room", "heat")
    admin = await hass_ws_client(hass)
    msg = await _ws(admin, 1, {"type": f"{DOMAIN}/update_options", "master_valve_entity": value})
    assert not msg["success"], msg
    await hass.async_block_till_done()
    assert entry.options.get("master_valve_entity", "") == ""
    assert data(hass, entry)["options"]["master_valve_entity"] == ""


@pytest.mark.parametrize("value", [MASTER, "", None])
async def test_update_options_accepts_master_valve(hass: HomeAssistant, hass_ws_client, value):
    entry = await setup_wizard(hass)
    admin = await hass_ws_client(hass)
    msg = await _ws(admin, 1, {"type": f"{DOMAIN}/update_options", "master_valve_entity": value})
    assert msg["success"], msg
    await hass.async_block_till_done()
    assert (data(hass, entry)["options"]["master_valve_entity"] or "") == (value or "")


async def test_unchanged_missing_master_valve_does_not_block_save(hass: HomeAssistant, hass_ws_client):
    """A master valve whose device is gone must not lock the admin out of saving Settings."""
    entry = await setup_wizard(hass, {"master_valve_entity": "switch.pump_gone"})
    admin = await hass_ws_client(hass)
    msg = await _ws(admin, 1, {
        "type": f"{DOMAIN}/update_options", "master_valve_entity": "switch.pump_gone", "default_duration": 7,
    })
    assert msg["success"], msg
    await hass.async_block_till_done()
    assert data(hass, entry)["options"]["default_duration"] == 7


async def test_stored_master_valve_of_wrong_domain_is_never_called(hass: HomeAssistant):
    """Options saved before the fix with a script as master valve: the script is not run."""
    calls = []

    async def _script_on(call):
        calls.append(call)

    hass.services.async_register("script", "turn_on", _script_on)
    hass.services.async_register("script", "turn_off", _script_on)
    entry = await setup_wizard(hass, {"master_valve_entity": "script.qa_not_a_valve"})
    await _add_valve(hass, Z1, "Front")
    assert entry.options["master_valve_entity"] == "script.qa_not_a_valve"  # stored data untouched

    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 1}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1)
    await _stop_runs(hass)
    assert calls == []


# ---------------------------------------------------------------- #35 (reopened): list_config service


async def test_list_config_hides_notify_targets_from_non_admin(
    hass: HomeAssistant, hass_ws_client, hass_read_only_access_token,
):
    from homeassistant.core import Context

    entry = await setup_wizard(hass, {"notify_targets": ["mobile_app_phone"]})
    wh = data(hass, entry)["webhook_id"]

    user = await hass_ws_client(hass, hass_read_only_access_token)
    msg = await _ws(user, 1, {
        "type": "call_service", "domain": DOMAIN, "service": "list_config",
        "service_data": {}, "return_response": True,
    })
    assert msg["success"], msg
    resp = msg["result"]["response"]
    assert "notify_targets" not in resp["options"]
    assert wh not in str(resp)

    admin = await hass_ws_client(hass)
    msg = await _ws(admin, 1, {
        "type": "call_service", "domain": DOMAIN, "service": "list_config",
        "service_data": {}, "return_response": True,
    })
    assert msg["result"]["response"]["options"]["notify_targets"] == ["mobile_app_phone"]

    # Automations / scripts (no user) keep the full options; shared options untouched.
    resp = await hass.services.async_call(
        DOMAIN, "list_config", {}, blocking=True, return_response=True, context=Context(),
    )
    assert resp["options"]["notify_targets"] == ["mobile_app_phone"]
    assert data(hass, entry)["options"]["notify_targets"] == ["mobile_app_phone"]
