"""v0.13.0: water usage, low-flow alert, interleaved cycle & soak."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_capture_events, async_fire_time_changed

from custom_components.schedule_wizard.const import DOMAIN, EVENT_LOW_FLOW

from .conftest import data, is_on, settle, setup_wizard
from .test_scheduler import Z1, Z2, add_cycle, add_valve

pytestmark = pytest.mark.usefixtures("zones")


async def tick(hass: HomeAssistant, freezer, seconds: float) -> None:
    """Move the (frozen) clock and fire due timers, in small steps so chained timers fire in order."""
    step = 10.0
    left = float(seconds)
    while left > 0:
        dt = min(step, left)
        freezer.tick(timedelta(seconds=dt))
        async_fire_time_changed(hass)
        await settle(hass, 6)
        left -= dt


async def run(hass, entity_id, minutes):
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": entity_id, "duration_minutes": minutes}, blocking=True)
    await settle(hass)


async def test_water_measured_by_flow_sensor(hass: HomeAssistant, freezer):
    hass.states.async_set("sensor.flow", "10", {"unit_of_measurement": "L/min"})
    entry = await setup_wizard(hass, {"flow_entity": "sensor.flow"})
    await add_valve(hass, Z1, "Front")
    await run(hass, Z1, 3)
    await tick(hass, freezer, 181)
    assert not is_on(hass, Z1)
    store = data(hass, entry)["store"]
    last = next(h for h in store.history if h["status"] == "completed")
    assert last["liters"] == pytest.approx(30, abs=1)
    assert store.get_valve(Z1)["water_total_l"] == pytest.approx(30, abs=1)
    assert store.get_valve(Z1)["avg_lpm"] == pytest.approx(10, abs=0.5)
    assert float(hass.states.get("sensor.front_water_used").state) == pytest.approx(30, abs=1)
    assert float(hass.states.get("sensor.schedule_wizard_water_used").state) == pytest.approx(30, abs=1)


async def test_water_unit_conversion(hass: HomeAssistant, freezer):
    hass.states.async_set("sensor.flow", "0.6", {"unit_of_measurement": "m³/h"})  # 10 L/min
    entry = await setup_wizard(hass, {"flow_entity": "sensor.flow"})
    await add_valve(hass, Z1, "Front")
    await run(hass, Z1, 2)
    await tick(hass, freezer, 121)
    assert data(hass, entry)["store"].get_valve(Z1)["water_total_l"] == pytest.approx(20, abs=1)


async def test_water_estimated_from_zone_rate(hass: HomeAssistant, freezer):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front", flow_rate_lpm=12)
    await run(hass, Z1, 2)
    await tick(hass, freezer, 121)
    assert data(hass, entry)["store"].get_valve(Z1)["water_total_l"] == pytest.approx(24, abs=1)


async def test_low_flow_alert(hass: HomeAssistant, freezer):
    hass.states.async_set("sensor.flow", "3", {"unit_of_measurement": "L/min"})
    entry = await setup_wizard(hass, {"flow_entity": "sensor.flow"})
    await add_valve(hass, Z1, "Front")
    valve = data(hass, entry)["store"].get_valve(Z1)
    valve.update(avg_lpm=10.0, flow_runs=5)
    events = async_capture_events(hass, EVENT_LOW_FLOW)
    await run(hass, Z1, 3)
    await tick(hass, freezer, 181)
    assert len(events) == 1
    assert events[0].data["expected_lpm"] == 10.0
    assert valve["avg_lpm"] == 10.0  # not learned from the bad run


async def test_interleaved_cycle_and_soak(hass: HomeAssistant, freezer):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Slope", soak_run_minutes=2, soak_pause_minutes=3)
    await add_valve(hass, Z2, "Lawn")
    cid = await add_cycle(hass, "Morning", [(Z1, 4), (Z2, 2)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    scheduler = data(hass, entry)["scheduler"]
    assert is_on(hass, Z1)                      # t=0: Slope chunk 1
    await tick(hass, freezer, 125)
    assert not is_on(hass, Z1) and is_on(hass, Z2)  # t=2: Slope soaks, Lawn runs
    assert scheduler.soaking[0]["entity_id"] == Z1
    await tick(hass, freezer, 120)
    assert not is_on(hass, Z2) and not is_on(hass, Z1)  # t=4: waiting for Slope's soak to end
    await tick(hass, freezer, 60)
    assert is_on(hass, Z1)                      # t=5: Slope chunk 2
    await tick(hass, freezer, 125)
    assert not is_on(hass, Z1)
    assert cid not in scheduler.active_cycles
    assert not scheduler.soaking


async def test_sequential_when_interleave_off(hass: HomeAssistant, freezer):
    await setup_wizard(hass, {"interleave_soak": False})
    await add_valve(hass, Z1, "Slope", soak_run_minutes=2, soak_pause_minutes=3)
    await add_valve(hass, Z2, "Lawn")
    cid = await add_cycle(hass, "Morning", [(Z1, 4), (Z2, 2)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    await tick(hass, freezer, 125)
    assert not is_on(hass, Z1) and not is_on(hass, Z2)  # Slope soaks, Lawn waits its turn
