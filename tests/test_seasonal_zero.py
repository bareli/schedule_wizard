"""#26: a temperature (seasonal) factor of 0 % skips the run instead of watering 1 minute."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_capture_events

from .conftest import FakeCalendar, advance, data, is_on, settle, setup_wizard
from .test_scheduler import Z1, Z2, _schedule_now, add_cycle, add_valve, fire_minute, statuses

pytestmark = pytest.mark.usefixtures("zones")

SEASONAL_SKIPPED = "schedule_wizard_seasonal_skipped"
SEASONAL = {
    "seasonal_enabled": True, "seasonal_temp_entity": "sensor.temp",
    "seasonal_temp_low": 20, "seasonal_temp_high": 30, "seasonal_min_pct": 0, "seasonal_max_pct": 100,
}


async def test_zone_skipped_at_zero_percent(hass: HomeAssistant):
    sent: list[dict] = []

    async def _notify(call: ServiceCall):
        sent.append(dict(call.data))

    hass.services.async_register("notify", "phone", _notify)
    entry = await setup_wizard(hass, {**SEASONAL, "notify_targets": ["phone"], "notify_events": ["skipped_seasonal"]})
    hass.states.async_set("sensor.temp", "17.2")
    await add_valve(hass, Z1, "Front")
    events = async_capture_events(hass, SEASONAL_SKIPPED)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=10)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert Z1 not in data(hass, entry)["scheduler"].active
    hist = data(hass, entry)["store"].history[0]
    assert hist["status"] == "skipped_seasonal_zero"
    assert hist["duration_min"] == 10
    assert len(events) == 1
    assert events[0].data["reason"] == "seasonal_zero"
    assert events[0].data["source"] == "schedule"
    # #31: one wording for history, event text and notification.
    assert sent and sent[0]["message"] == "Front: skipped: temperature adjustment 0 % (too cool)"
    assert events[0].data["message"] == sent[0]["message"]


async def test_cycle_skipped_at_zero_percent(hass: HomeAssistant):
    entry = await setup_wizard(hass, SEASONAL)
    hass.states.async_set("sensor.temp", "15")
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 10), (Z2, 10)])
    events = async_capture_events(hass, SEASONAL_SKIPPED)
    fire_at = await _schedule_now(hass, cycle_id=cid)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1) and not is_on(hass, Z2)
    assert cid not in data(hass, entry)["scheduler"].active_cycles
    assert statuses(hass, entry, cid)[0] == "skipped_seasonal_zero"
    assert len(events) == 1 and events[0].data["kind"] == "cycle"


async def test_calendar_run_skipped_at_zero_percent(hass: HomeAssistant):
    entry = await setup_wizard(hass, {**SEASONAL, "calendar_entity": "calendar.garden"})
    hass.states.async_set("sensor.temp", "10")
    cal = FakeCalendar(hass)
    await add_valve(hass, Z1, "Front")
    events = async_capture_events(hass, SEASONAL_SKIPPED)
    start = dt_util.now().replace(microsecond=0) + timedelta(minutes=3)
    cal.events = [{"summary": "Front", "start": start.isoformat(), "end": start.isoformat(), "description": "10 min"}]
    await advance(hass, 61)
    await advance(hass, 3 * 60)
    assert not is_on(hass, Z1)
    assert statuses(hass, entry, Z1)[0] == "skipped_seasonal_zero"
    assert events and events[0].data["source"] == "calendar"


async def test_small_factor_keeps_one_minute(hass: HomeAssistant):
    """3 % of 10 min rounds to 0 min: still waters the 1-minute minimum (only 0 % skips)."""
    entry = await setup_wizard(hass, SEASONAL)
    hass.states.async_set("sensor.temp", "20.3")  # 3 %
    await add_valve(hass, Z1, "Front")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=10)
    await fire_minute(hass, fire_at)
    assert is_on(hass, Z1)
    assert data(hass, entry)["scheduler"].active[Z1]["duration_min"] == 1


async def test_manual_run_not_scaled(hass: HomeAssistant):
    """Water now is never scaled or skipped by the temperature adjustment."""
    await setup_wizard(hass, SEASONAL)
    hass.states.async_set("sensor.temp", "5")
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call("schedule_wizard", "run_valve", {"entity_id": Z1, "duration_minutes": 4}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1)


async def test_half_percent_rounds_like_the_panel(hass: HomeAssistant):
    """#29: 0.5 % shows as 1 % in the panel (Math.round), so it must water 1 minute, not skip."""
    entry = await setup_wizard(hass, {**SEASONAL, "seasonal_min_pct": 0.5})
    hass.states.async_set("sensor.temp", "15")  # at or below low: factor = Min % = 0.5 %
    await add_valve(hass, Z1, "Front")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=10)
    await fire_minute(hass, fire_at)
    assert is_on(hass, Z1)
    assert data(hass, entry)["scheduler"].active[Z1]["duration_min"] == 1


async def test_get_state_reports_current_factor(hass: HomeAssistant, hass_ws_client):
    """#29: the panel gets the current factor and whether scheduled runs are skipped."""
    await setup_wizard(hass, SEASONAL)
    client = await hass_ws_client(hass)

    async def seasonal() -> dict:
        await client.send_json_auto_id({"type": "schedule_wizard/get_state"})
        return (await client.receive_json())["result"]["seasonal"]

    hass.states.async_set("sensor.temp", "10")
    assert await seasonal() == {"pct": 0, "skips": True}
    hass.states.async_set("sensor.temp", "20.3")
    assert await seasonal() == {"pct": 3, "skips": False}
    hass.states.async_set("sensor.temp", "25")
    assert await seasonal() == {"pct": 50, "skips": False}


async def test_skip_notification_in_ha_language(hass: HomeAssistant):
    """#31 / #33: the skip notification and event text follow the HA language, same words as the panel."""
    sent: list[dict] = []

    async def _notify(call: ServiceCall):
        sent.append(dict(call.data))

    hass.services.async_register("notify", "phone", _notify)
    hass.config.language = "de"
    await setup_wizard(hass, {**SEASONAL, "notify_targets": ["phone"], "notify_events": ["skipped_seasonal"]})
    hass.states.async_set("sensor.temp", "10")
    await add_valve(hass, Z1, "Front")
    events = async_capture_events(hass, SEASONAL_SKIPPED)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=10)
    await fire_minute(hass, fire_at)
    assert sent and sent[0]["message"] == "Front: übersprungen: Temperaturanpassung 0 % (zu kühl)"
    assert events[0].data["message"] == sent[0]["message"]
