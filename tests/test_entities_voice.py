"""v0.12.0: HA entities, calendar/week, skips, reminders with notification actions, voice."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.schedule_wizard.const import DOMAIN
from custom_components.schedule_wizard.voice import best_match, parse_number

from .conftest import advance, data, is_on, settle, setup_wizard
from .test_scheduler import Z1, Z2, _schedule_now, add_cycle, add_valve, fire_minute, statuses

pytestmark = pytest.mark.usefixtures("zones")


async def test_zone_entities_follow_config(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await settle(hass)
    assert hass.states.get("switch.front_watering").state == "off"
    assert hass.states.get("sensor.front_time_left").state == "0"

    await hass.services.async_call("switch", "turn_on", {"entity_id": "switch.front_watering"}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1)
    assert hass.states.get("switch.front_watering").state == "on"
    assert hass.states.get("binary_sensor.schedule_wizard_watering").state == "on"
    await hass.services.async_call("switch", "turn_off", {"entity_id": "switch.front_watering"}, blocking=True)
    await settle(hass)
    assert not is_on(hass, Z1)
    assert hass.states.get("binary_sensor.schedule_wizard_watering").state == "off"

    dev_reg = dr.async_get(hass)
    assert dev_reg.async_get_device(identifiers={(DOMAIN, f"{entry.entry_id}_zone_{Z1}")})
    await hass.services.async_call(DOMAIN, "remove_valve", {"entity_id": Z1}, blocking=True)
    await settle(hass)
    assert er.async_get(hass).async_get("switch.front_watering") is None
    assert hass.states.get("switch.front_watering") is None
    assert dev_reg.async_get_device(identifiers={(DOMAIN, f"{entry.entry_id}_zone_{Z1}")}) is None


async def test_plan_entities(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    cid = await add_cycle(hass, "Morning", [(Z1, 5)])
    await settle(hass)
    assert hass.states.get("switch.morning_enabled").state == "on"
    await hass.services.async_call("switch", "turn_off", {"entity_id": "switch.morning_enabled"}, blocking=True)
    await settle(hass)
    assert data(hass, entry)["store"].get_cycle(cid)["enabled"] is False
    await hass.services.async_call("switch", "turn_on", {"entity_id": "switch.morning_enabled"}, blocking=True)
    await hass.services.async_call("button", "press", {"entity_id": "button.morning_run_now"}, blocking=True)
    await settle(hass)
    assert cid in data(hass, entry)["scheduler"].active_cycles
    assert is_on(hass, Z1)


async def test_rain_delay_switch(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    ent = "switch.schedule_wizard_rain_delay"
    assert hass.states.get(ent).state == "off"
    await hass.services.async_call("switch", "turn_on", {"entity_id": ent}, blocking=True)
    await settle(hass)
    assert data(hass, entry)["scheduler"]._is_rain_delay_active()
    assert hass.states.get(ent).state == "on"
    await hass.services.async_call("switch", "turn_off", {"entity_id": ent}, blocking=True)
    await settle(hass)
    assert not data(hass, entry)["scheduler"]._is_rain_delay_active()


async def test_calendar_and_week(hass: HomeAssistant, hass_ws_client):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call(
        DOMAIN, "add_schedule",
        {"valve_entity_id": Z1, "time": "06:00", "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], "duration_minutes": 10},
        blocking=True, return_response=True,
    )
    await settle(hass)
    start = dt_util.start_of_local_day() + timedelta(days=1)
    resp = await hass.services.async_call(
        "calendar", "get_events",
        {"entity_id": "calendar.schedule_wizard_watering_schedule", "start_date_time": start.isoformat(),
         "end_date_time": (start + timedelta(days=3)).isoformat()},
        blocking=True, return_response=True,
    )
    events = resp["calendar.schedule_wizard_watering_schedule"]["events"]
    assert len(events) == 3
    assert events[0]["summary"] == "Front"
    assert "Front 10 min" in events[0]["description"]

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    week = (await client.receive_json())["result"]["week"]
    assert 6 <= len(week) <= 7
    assert all(o["target"] == Z1 and o["minutes"] == 10 for o in week)


async def test_skip_day_and_next(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    resp = await hass.services.async_call(DOMAIN, "skip_day", {}, blocking=True, return_response=True)
    assert len(resp["skipped"]) == 1
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert statuses(hass, entry, Z1)[0] == "skipped_manual"
    assert not data(hass, entry)["store"].skips

    sid = data(hass, entry)["store"].schedules[0]["id"]
    resp = await hass.services.async_call(DOMAIN, "skip_next", {"schedule_id": sid}, blocking=True, return_response=True)
    assert resp["skipped"]["schedule_id"] == sid
    assert data(hass, entry)["store"].skips[sid] == [resp["skipped"]["day"]]


async def test_reminder_with_actions(hass: HomeAssistant):
    calls: list[ServiceCall] = []

    async def _notify(call: ServiceCall):
        calls.append(call)

    hass.services.async_register("notify", "mobile_app_phone", _notify)
    entry = await setup_wizard(hass, {"reminder_minutes": 10, "notify_targets": ["mobile_app_phone"]})
    await add_valve(hass, Z1, "Front")
    fire_at = dt_util.now().replace(second=0, microsecond=0) + timedelta(minutes=12)
    day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][fire_at.weekday()]
    await hass.services.async_call(
        DOMAIN, "add_schedule",
        {"valve_entity_id": Z1, "time": fire_at.strftime("%H:%M"), "days": [day], "duration_minutes": 5},
        blocking=True, return_response=True,
    )
    async_fire_time_changed(hass, dt_util.as_utc(fire_at - timedelta(minutes=10)))
    await settle(hass)
    assert len(calls) == 1
    actions = calls[0].data["data"]["actions"]
    assert [a["title"] for a in actions] == ["Skip today", "Water now"]

    hass.bus.async_fire("mobile_app_notification_action", {"action": actions[1]["action"]})
    await settle(hass)
    assert is_on(hass, Z1)
    sid = data(hass, entry)["store"].schedules[0]["id"]
    assert data(hass, entry)["store"].is_skipped(sid, fire_at.date().isoformat())


def test_voice_parsers():
    assert parse_number("10") == 10
    assert parse_number("ten") == 10
    assert parse_number("עשר") == 10
    zones = [("switch.a", "Front lawn"), ("switch.b", "דשא")]
    assert best_match("the front lawn", zones) == "switch.a"
    assert best_match("הדשא", zones) == "switch.b"
    assert best_match("garage", zones) is None


async def test_voice_handler(hass: HomeAssistant):
    entry = await setup_wizard(hass, {"voice_enabled": False})
    await add_valve(hass, Z1, "Front lawn")
    from custom_components.schedule_wizard.voice import VoiceCommands
    voice = VoiceCommands(hass, entry, data(hass, entry))
    assert await voice.async_handle("en", "run_zone", {"zone": "the front lawn for 7 minutes"}) == "Watering Front lawn for 7 minutes."
    await settle(hass)
    assert data(hass, entry)["scheduler"].active[Z1]["duration_min"] == 7
    assert await voice.async_handle("he", "stop_all", {}) == "ההשקיה נעצרה."
    await settle(hass)
    assert not is_on(hass, Z1)
    assert "garage" in await voice.async_handle("en", "run_zone", {"zone": "garage"})


async def test_voice_end_to_end(hass: HomeAssistant):
    pytest.importorskip("hassil")
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "conversation", {})
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front lawn")
    await settle(hass)
    from homeassistant.components import conversation
    result = await conversation.async_converse(hass, "water the front lawn for 5 minutes", None, hass.data.get("context") or __import__("homeassistant.core", fromlist=["Context"]).Context(), language="en")
    await settle(hass)
    speech = result.response.speech["plain"]["speech"]
    assert speech == "Watering Front lawn for 5 minutes."
    assert is_on(hass, Z1)
    result = await conversation.async_converse(hass, "stop the watering", None, __import__("homeassistant.core", fromlist=["Context"]).Context(), language="en")
    await settle(hass)
    assert not is_on(hass, Z1)


async def test_unskip(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    sid = data(hass, entry)["store"].schedules[0]["id"]
    await hass.services.async_call(DOMAIN, "skip_next", {"schedule_id": sid}, blocking=True, return_response=True)
    await hass.services.async_call(DOMAIN, "unskip", {"schedule_id": sid, "date": fire_at.date().isoformat()}, blocking=True)
    await fire_minute(hass, fire_at)
    assert is_on(hass, Z1)


@pytest.mark.parametrize(("lang", "run_text", "reply", "stop_text"), [
    ("de", "Bewässere den Rasen für 6 Minuten", "Bewässere Rasen für 6 Minuten.", "Stoppe die Bewässerung"),
    ("he", "תשקה את הדשא 6 דקות", "משקה את דשא למשך 6 דקות.", "עצור את ההשקיה"),
])
async def test_voice_end_to_end_languages(hass: HomeAssistant, lang, run_text, reply, stop_text):
    pytest.importorskip("hassil")
    from homeassistant.components import conversation
    from homeassistant.core import Context
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "conversation", {})
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Rasen" if lang == "de" else "דשא")
    await settle(hass)
    result = await conversation.async_converse(hass, run_text, None, Context(), language=lang)
    await settle(hass)
    assert result.response.speech["plain"]["speech"] == reply
    assert data(hass, hass.config_entries.async_entries(DOMAIN)[0])["scheduler"].active[Z1]["duration_min"] == 6
    await conversation.async_converse(hass, stop_text, None, Context(), language=lang)
    await settle(hass)
    assert not is_on(hass, Z1)


async def test_run_schedule_now_drops_todays_run(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    sid = data(hass, entry)["store"].schedules[0]["id"]
    await hass.services.async_call(DOMAIN, "run_schedule", {"schedule_id": sid}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1)
    assert data(hass, entry)["store"].is_skipped(sid, fire_at.date().isoformat())
