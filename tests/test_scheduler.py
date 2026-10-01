"""Scheduler behaviour tests (bug regressions + v0.8.0 features)."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_capture_events

from custom_components.schedule_wizard.const import (
    DOMAIN,
    EVENT_CONDITION_SKIPPED,
    EVENT_LEAK_DETECTED,
    EVENT_MOISTURE_SKIPPED,
    EVENT_RAIN_SKIPPED,
)

from .conftest import FakeCalendar, advance, data, is_on, settle, setup_wizard

pytestmark = pytest.mark.usefixtures("fixed_clock", "zones")

Z1, Z2, Z3, MASTER = (f"input_boolean.{z}" for z in ("zone1", "zone2", "zone3", "master"))


async def add_valve(hass, entity_id, label, **extra):
    await hass.services.async_call(
        DOMAIN, "add_valve", {"entity_id": entity_id, "label": label, **extra}, blocking=True
    )


async def add_cycle(hass, name, steps):
    resp = await hass.services.async_call(
        DOMAIN, "add_cycle",
        {"name": name, "steps": [{"entity_id": e, "duration_minutes": m} for e, m in steps]},
        blocking=True, return_response=True,
    )
    return resp["cycle"]["id"]


def statuses(hass, entry, entity_id=None):
    return [h["status"] for h in data(hass, entry)["store"].history
            if entity_id is None or h["valve_entity_id"] == entity_id]


async def test_manual_run_opens_and_closes(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 2}, blocking=True)
    assert is_on(hass, Z1)
    await advance(hass, 121)
    assert not is_on(hass, Z1)
    assert statuses(hass, entry, Z1)[:2] == ["completed", "started"]


async def test_master_valve_opens_for_cycle(hass: HomeAssistant):
    """#6: master never opened for cycles because the cycle was already in _active_cycles."""
    entry = await setup_wizard(hass, {"master_valve_entity": MASTER})
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 1), (Z2, 1)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert is_on(hass, MASTER)
    assert is_on(hass, Z1)
    await advance(hass, 61)
    assert is_on(hass, Z2) and not is_on(hass, Z1)
    assert is_on(hass, MASTER)
    await advance(hass, 61)
    assert not is_on(hass, Z2)
    assert not is_on(hass, MASTER)
    assert "cycle_completed" in statuses(hass, entry, cid)


async def test_options_update_keeps_running_cycle(hass: HomeAssistant):
    """#9: saving options used to reload the entry and cancel running cycles."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 1), (Z2, 1)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    scheduler = data(hass, entry)["scheduler"]

    hass.config_entries.async_update_entry(entry, options={**entry.options, "notify_targets": ["x"]})
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 1}, blocking=True)
    await settle(hass)

    assert data(hass, entry)["scheduler"] is scheduler
    assert cid in scheduler.active_cycles
    assert data(hass, entry)["options"]["notify_targets"] == ["x"]
    assert scheduler._is_rain_delay_active()
    await advance(hass, 61)
    assert is_on(hass, Z2)


async def test_stop_cycle_during_fail_detection_closes_valve(hass: HomeAssistant):
    """#10: stopping in the verify window left the valve open with no timer."""
    entry = await setup_wizard(hass, {"fail_detection_enabled": True, "fail_detection_seconds": 5})
    await add_valve(hass, Z1, "Front")
    cid = await add_cycle(hass, "Morning", [(Z1, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    # input_boolean turns on instantly, but the verify loop still sleeps 1s before checking.
    assert is_on(hass, Z1)
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler.active[Z1].get("starting")
    await hass.services.async_call(DOMAIN, "stop_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert not is_on(hass, Z1)
    assert Z1 not in scheduler.active
    assert cid not in scheduler.active_cycles


async def test_pause_closes_master_and_stop_after_pause_records(hass: HomeAssistant):
    """#11: paused cycle held master open; stopping a paused cycle never closed it."""
    entry = await setup_wizard(hass, {"master_valve_entity": MASTER})
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert is_on(hass, MASTER) and is_on(hass, Z1)

    await hass.services.async_call(DOMAIN, "pause_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler.active_cycles[cid]["paused"]
    assert not is_on(hass, Z1)
    assert not is_on(hass, MASTER)

    await hass.services.async_call(DOMAIN, "resume_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert is_on(hass, MASTER) and is_on(hass, Z2)

    await hass.services.async_call(DOMAIN, "pause_cycle", {"cycle_id": cid}, blocking=True)
    await hass.services.async_call(DOMAIN, "stop_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert cid not in scheduler.active_cycles
    assert statuses(hass, entry, cid)[0] == "cycle_cancelled"
    assert not is_on(hass, MASTER)


async def test_rain_threshold_zero_does_not_skip(hass: HomeAssistant):
    """#8: threshold 0 made every numeric reading (even 0 mm) skip."""
    entry = await setup_wizard(hass, {"rain_entity": "sensor.rain_mm", "rain_threshold": 0})
    hass.states.async_set("sensor.rain_mm", "0.0")
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler._should_skip_for_rain() is False
    hass.config_entries.async_update_entry(entry, options={**entry.options, "rain_threshold": 2})
    await settle(hass)
    hass.states.async_set("sensor.rain_mm", "3")
    assert scheduler._should_skip_for_rain() is True


async def _schedule_now(hass, **fields):
    """Add a schedule for the current minute + 1 and fire the minute tick."""
    fire_at = dt_util.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
    day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][fire_at.weekday()]
    await hass.services.async_call(
        DOMAIN, "add_schedule",
        {"time": fire_at.strftime("%H:%M"), "days": [day], **fields},
        blocking=True, return_response=True,
    )
    return fire_at


async def fire_minute(hass, fire_at):
    from pytest_homeassistant_custom_component.common import async_fire_time_changed
    async_fire_time_changed(hass, dt_util.as_utc(fire_at))
    await settle(hass)


async def test_duplicate_schedules_same_minute_run_once(hass: HomeAssistant):
    """#15: two triggers in the same minute both started the valve."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    await fire_minute(hass, fire_at)
    assert is_on(hass, Z1)
    assert statuses(hass, entry, Z1).count("started") == 1


async def test_schedule_condition_skips(hass: HomeAssistant):
    """v0.8.0 schedule conditions."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    hass.states.async_set("binary_sensor.pool_cover", "on")
    events = async_capture_events(hass, EVENT_CONDITION_SKIPPED)
    fire_at = await _schedule_now(
        hass, valve_entity_id=Z1, duration_minutes=5,
        conditions=[{"entity_id": "binary_sensor.pool_cover", "operator": "equals", "value": "off"}],
    )
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert statuses(hass, entry, Z1)[0] == "skipped_condition"
    assert len(events) == 1


async def test_condition_numeric_passes(hass: HomeAssistant):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    hass.states.async_set("sensor.temp", "31", {"forecast_high": 35})
    fire_at = await _schedule_now(
        hass, valve_entity_id=Z1, duration_minutes=5,
        conditions=[
            {"entity_id": "sensor.temp", "operator": "above", "value": 25},
            {"entity_id": "sensor.temp", "attribute": "forecast_high", "operator": "below", "value": 40},
        ],
    )
    await fire_minute(hass, fire_at)
    assert is_on(hass, Z1)


async def test_per_valve_moisture_overrides_global(hass: HomeAssistant):
    """v0.8.0 per-valve moisture: wet zone skipped, dry zone runs, global ignored for zone with own sensor."""
    entry = await setup_wizard(hass, {"moisture_entity": "sensor.global_moist", "moisture_threshold_skip_above": 50})
    hass.states.async_set("sensor.global_moist", "10")
    hass.states.async_set("sensor.bed_moist", "70")
    await add_valve(hass, Z1, "Bed", moisture_entity="sensor.bed_moist", moisture_threshold=60)
    await add_valve(hass, Z2, "Lawn")
    events = async_capture_events(hass, EVENT_MOISTURE_SKIPPED)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    await _schedule_now(hass, valve_entity_id=Z2, duration_minutes=5)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)
    assert statuses(hass, entry, Z1)[0] == "skipped_moisture"
    assert len(events) == 1


async def test_per_valve_moisture_skips_cycle_step(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    hass.states.async_set("sensor.bed_moist", "70")
    await add_valve(hass, Z1, "Bed", moisture_entity="sensor.bed_moist", moisture_threshold=60)
    await add_valve(hass, Z2, "Lawn")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    fire_at = await _schedule_now(hass, cycle_id=cid)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)
    assert "skipped_moisture" in statuses(hass, entry, Z1)


async def test_manual_cycle_ignores_moisture(hass: HomeAssistant):
    await setup_wizard(hass)
    hass.states.async_set("sensor.bed_moist", "70")
    await add_valve(hass, Z1, "Bed", moisture_entity="sensor.bed_moist", moisture_threshold=60)
    cid = await add_cycle(hass, "Morning", [(Z1, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1)


async def test_soak_splits_scheduled_run(hass: HomeAssistant):
    """v0.8.0 cycle-and-soak: 10 min with max 4 / pause 3 -> 4,3,3 with pauses."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Slope", soak_run_minutes=4, soak_pause_minutes=3)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=10)
    await fire_minute(hass, fire_at)
    scheduler = data(hass, entry)["scheduler"]
    assert is_on(hass, Z1)
    assert scheduler.active[Z1]["duration_min"] == 4
    await advance(hass, 4 * 60 + 1)
    assert not is_on(hass, Z1)
    assert scheduler.soaking[0]["phase"] == "soaking"
    await advance(hass, 3 * 60 + 1)
    assert is_on(hass, Z1)
    assert scheduler.active[Z1]["duration_min"] == 3
    await advance(hass, 3 * 60 + 1)
    await advance(hass, 3 * 60 + 1)
    assert is_on(hass, Z1)
    await advance(hass, 3 * 60 + 1)
    assert not is_on(hass, Z1)
    assert not scheduler.soaking
    assert statuses(hass, entry, Z1).count("completed") == 3


async def test_stop_valve_during_soak_pause(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Slope", soak_run_minutes=2, soak_pause_minutes=5)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=6)
    await fire_minute(hass, fire_at)
    await advance(hass, 121)
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler.soaking and scheduler.soaking[0]["phase"] == "soaking"
    await hass.services.async_call(DOMAIN, "stop_valve", {"entity_id": Z1}, blocking=True)
    await settle(hass)
    assert not scheduler.soaking
    await advance(hass, 5 * 60 + 1)
    assert not is_on(hass, Z1)


async def test_calendar_event_gated_at_fire_time(hass: HomeAssistant):
    """#12: calendar events scheduled ahead skipped rain/moisture checks and seasonal."""
    entry = await setup_wizard(hass, {
        "calendar_entity": "calendar.garden",
        "rain_entity": "weather.home",
    })
    cal = FakeCalendar(hass)
    hass.states.async_set("weather.home", "sunny")
    await add_valve(hass, Z1, "Front")
    events = async_capture_events(hass, EVENT_RAIN_SKIPPED)
    start = dt_util.now().replace(microsecond=0) + timedelta(minutes=5)
    cal.events = [{"summary": "Front", "start": start.isoformat(), "end": (start + timedelta(minutes=10)).isoformat()}]
    await advance(hass, 61)  # calendar poll
    scheduler = data(hass, entry)["scheduler"]
    assert len(scheduler._calendar_pending) == 1
    hass.states.async_set("weather.home", "rainy")
    await advance(hass, 5 * 60 + 1)
    assert not is_on(hass, Z1)
    assert len(events) == 1
    assert statuses(hass, entry, Z1)[0] == "skipped_rain"


async def test_calendar_all_day_event_ignored(hass: HomeAssistant):
    """#14: all-day events ran the valve for 24h."""
    entry = await setup_wizard(hass, {"calendar_entity": "calendar.garden"})
    cal = FakeCalendar(hass)
    await add_valve(hass, Z1, "Front")
    today = dt_util.now().date()
    cal.events = [{"summary": "Front lawn party", "start": today.isoformat(), "end": (today + timedelta(days=1)).isoformat()}]
    await advance(hass, 61)
    assert not data(hass, entry)["scheduler"]._calendar_pending
    assert not is_on(hass, Z1)


async def test_calendar_deleted_event_cancelled(hass: HomeAssistant):
    """#13: pending calendar triggers were never cancelled."""
    entry = await setup_wizard(hass, {"calendar_entity": "calendar.garden"})
    cal = FakeCalendar(hass)
    await add_valve(hass, Z1, "Front")
    start = dt_util.now().replace(microsecond=0) + timedelta(minutes=5)
    cal.events = [{"summary": "Front", "start": start.isoformat(), "end": (start + timedelta(minutes=10)).isoformat()}]
    await advance(hass, 61)
    scheduler = data(hass, entry)["scheduler"]
    assert len(scheduler._calendar_pending) == 1
    cal.events = []
    await advance(hass, 61)
    assert not scheduler._calendar_pending
    await advance(hass, 5 * 60)
    assert not is_on(hass, Z1)


def test_parse_duration():
    from custom_components.schedule_wizard.scheduler import Scheduler
    assert Scheduler._parse_duration("Zone 2, 15 min", "", 0) == 15
    assert Scheduler._parse_duration("20", "", 0) == 20
    assert Scheduler._parse_duration("Zone 2", "", 0) == 0
    assert Scheduler._parse_duration("השקיה 12 דקות", "", 0) == 12


async def test_leak_detection_idle(hass: HomeAssistant):
    """v0.8.0 flow sensor: flow with no valve running raises a leak alert after the delay."""
    entry = await setup_wizard(hass, {
        "flow_entity": "sensor.flow", "flow_leak_threshold": 0.5, "flow_delay_sec": 30,
        "master_valve_entity": MASTER, "flow_stop_all": True,
    })
    events = async_capture_events(hass, EVENT_LEAK_DETECTED)
    hass.states.async_set("sensor.flow", "2.0")
    await settle(hass)
    assert not events
    await advance(hass, 31)
    assert len(events) == 1
    assert events[0].data["kind"] == "leak"
    assert data(hass, entry)["scheduler"].flow_status["alert"] == "leak"
    hass.states.async_set("sensor.flow", "0")
    await settle(hass)
    assert data(hass, entry)["scheduler"].flow_status["alert"] is None


async def test_high_flow_while_running_stops_all(hass: HomeAssistant):
    entry = await setup_wizard(hass, {
        "flow_entity": "sensor.flow", "flow_max_running": 20, "flow_delay_sec": 10, "flow_stop_all": True,
    })
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 10}, blocking=True)
    hass.states.async_set("sensor.flow", "12")
    await advance(hass, 11)
    assert is_on(hass, Z1)
    hass.states.async_set("sensor.flow", "45")
    await settle(hass)
    await advance(hass, 11)
    assert not is_on(hass, Z1)
    assert "high_flow" in statuses(hass, entry)


async def test_stop_all(hass: HomeAssistant):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    await add_valve(hass, Z3, "Side")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z3, "duration_minutes": 10}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1) and is_on(hass, Z3)
    await hass.services.async_call(DOMAIN, "stop_all", {}, blocking=True)
    await settle(hass)
    assert not is_on(hass, Z1) and not is_on(hass, Z3)


async def test_add_schedule_requires_registered_valve(hass: HomeAssistant):
    from homeassistant.exceptions import HomeAssistantError
    await setup_wizard(hass)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN, "add_schedule",
            {"valve_entity_id": Z1, "time": "06:00", "days": ["mon"], "duration_minutes": 5},
            blocking=True, return_response=True,
        )


async def test_webhook_rejects_unsupported_domain(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    from homeassistant.components import webhook as webhook_component

    handlers_key = getattr(webhook_component, "_HANDLERS", "webhook")  # HassKey on newer HA
    registered = hass.data[handlers_key][data(hass, entry)["webhook_id"]]
    handler = registered["handler"] if isinstance(registered, dict) else registered.handler  # dataclass on newer HA

    class Req:
        method = "POST"

        async def json(self):
            return {"entity_id": "climate.living_room", "action": "stop"}

    resp = await handler(hass, data(hass, entry)["webhook_id"], Req())
    assert resp.status == 400


async def test_calendar_delayed_event_applies_seasonal(hass: HomeAssistant):
    """#12: seasonal factor was only applied when the event started exactly at poll time."""
    entry = await setup_wizard(hass, {
        "calendar_entity": "calendar.garden",
        "seasonal_enabled": True, "seasonal_temp_entity": "sensor.temp",
        "seasonal_temp_low": 10, "seasonal_temp_high": 30, "seasonal_min_pct": 50, "seasonal_max_pct": 150,
    })
    hass.states.async_set("sensor.temp", "35")
    cal = FakeCalendar(hass)
    await add_valve(hass, Z1, "Front")
    start = dt_util.now().replace(microsecond=0) + timedelta(minutes=3)
    cal.events = [{"summary": "Front", "start": start.isoformat(), "end": start.isoformat(), "description": "10 min"}]
    await advance(hass, 61)
    await advance(hass, 3 * 60)
    assert is_on(hass, Z1)
    assert data(hass, entry)["scheduler"].active[Z1]["duration_min"] == 15


async def test_restore_active_run_after_restart(hass: HomeAssistant, hass_storage):
    import time
    now = int(time.time())
    hass_storage[f"{DOMAIN}.data"] = {
        "version": 1, "key": f"{DOMAIN}.data",
        "data": {
            "valves": [{"entity_id": Z1, "label": "Front", "default_duration_min": 10, "enabled": True}],
            "schedules": [], "history": [], "cycles": [],
            "active_runs": [{"entity_id": Z1, "started_at": now - 60, "ends_at": now + 120,
                             "duration_min": 3, "source": "manual", "note": ""}],
        },
    }
    await hass.services.async_call("input_boolean", "turn_on", {"entity_id": Z1}, blocking=True)
    entry = await setup_wizard(hass)
    assert Z1 in data(hass, entry)["scheduler"].active
    await advance(hass, 121)
    assert not is_on(hass, Z1)
    assert statuses(hass, entry, Z1)[0] == "completed"


async def test_per_valve_rain_delay(hass: HomeAssistant):
    """#4: rain delay for individual valves."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Garden")
    await add_valve(hass, Z2, "Greenhouse")
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 24, "entity_id": [Z1]}, blocking=True)
    store = data(hass, entry)["store"]
    assert store.get_valve(Z1)["rain_delay_until"] > 0
    assert not data(hass, entry)["scheduler"]._is_rain_delay_active()
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    await _schedule_now(hass, valve_entity_id=Z2, duration_minutes=5)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)
    assert statuses(hass, entry, Z1)[0] == "skipped_rain_delay"
    await hass.services.async_call(DOMAIN, "clear_rain_delay", {"entity_id": Z1}, blocking=True)
    assert store.get_valve(Z1)["rain_delay_until"] == 0


async def test_rain_delay_unregistered_valve_rejected(hass: HomeAssistant):
    from homeassistant.exceptions import HomeAssistantError
    await setup_wizard(hass)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 24, "entity_id": [Z3]}, blocking=True)


async def test_indoor_valve_ignores_global_delay_and_rain(hass: HomeAssistant):
    """#4: indoor valves keep running under a global rain delay and rain skip."""
    entry = await setup_wizard(hass, {"rain_entity": "weather.home"})
    hass.states.async_set("weather.home", "rainy")
    await add_valve(hass, Z1, "Garden")
    await add_valve(hass, Z2, "Greenhouse", rain_exempt=True)
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 24}, blocking=True)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    await _schedule_now(hass, valve_entity_id=Z2, duration_minutes=5)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)


async def test_mixed_cycle_under_global_delay(hass: HomeAssistant):
    """#4: a cycle with indoor and outdoor steps runs only the indoor steps during a rain delay."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Garden")
    await add_valve(hass, Z2, "Greenhouse", rain_exempt=True)
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 24}, blocking=True)
    fire_at = await _schedule_now(hass, cycle_id=cid)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)
    assert statuses(hass, entry, Z1)[0] == "skipped_rain_delay"


async def test_outdoor_cycle_under_global_delay_skipped(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Garden")
    cid = await add_cycle(hass, "Morning", [(Z1, 5)])
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 24}, blocking=True)
    fire_at = await _schedule_now(hass, cycle_id=cid)
    await fire_minute(hass, fire_at)
    assert cid not in data(hass, entry)["scheduler"].active_cycles
    assert not is_on(hass, Z1)
