"""v0.13.0: rain forecast skip, resume cycles after restart, Repairs issues, diagnostics."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import advance, data, is_on, settle, setup_wizard
from .test_scheduler import Z1, Z2, _schedule_now, add_cycle, add_valve, fire_minute, statuses

pytestmark = pytest.mark.usefixtures("zones")


def fake_weather(hass: HomeAssistant, hourly_mm: list[float], unit: str = "mm"):
    hass.states.async_set("weather.home", "cloudy", {"precipitation_unit": unit})
    now = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)

    async def _get(call: ServiceCall):
        if call.data["type"] != "hourly":
            return {"weather.home": {"forecast": []}}
        return {"weather.home": {"forecast": [
            {"datetime": (now + timedelta(hours=i)).isoformat(), "precipitation": mm} for i, mm in enumerate(hourly_mm)
        ]}}

    hass.services.async_register("weather", "get_forecasts", _get, supports_response=SupportsResponse.ONLY)


async def test_forecast_skip_outdoor_only(hass: HomeAssistant):
    fake_weather(hass, [0.5] * 10 + [0] * 30)  # 5 mm in the next 24 h
    entry = await setup_wizard(hass, {"forecast_entity": "weather.home", "forecast_skip_mm": 3, "forecast_hours": 24})
    await settle(hass)
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler.forecast_status["mm"] == 5.0
    await add_valve(hass, Z1, "Lawn")
    await add_valve(hass, Z2, "Greenhouse", rain_exempt=True)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=5)
    await _schedule_now(hass, valve_entity_id=Z2, duration_minutes=5)
    await fire_minute(hass, fire_at)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)
    assert statuses(hass, entry, Z1)[0] == "skipped_forecast"


async def test_forecast_below_threshold_and_inches(hass: HomeAssistant):
    fake_weather(hass, [0.02] * 5, unit="in")  # 0.1 in = 2.54 mm
    entry = await setup_wizard(hass, {"forecast_entity": "weather.home", "forecast_skip_mm": 3})
    await settle(hass)
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler.forecast_status["mm"] == pytest.approx(2.5, abs=0.1)
    assert scheduler._should_skip_for_forecast() is False


async def _restart(hass: HomeAssistant, entry):
    assert await hass.config_entries.async_unload(entry.entry_id)
    await settle(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)


async def test_cycle_resumes_after_restart(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z1)

    await _restart(hass, entry)
    scheduler = data(hass, entry)["scheduler"]
    assert cid in scheduler.active_cycles
    assert is_on(hass, Z1)
    assert "cycle_cancelled" not in statuses(hass, entry, cid)
    await advance(hass, 5 * 60 + 1)
    assert not is_on(hass, Z1)
    assert is_on(hass, Z2)
    await advance(hass, 5 * 60 + 1)
    assert not is_on(hass, Z2)
    assert statuses(hass, entry, cid)[0] == "cycle_completed"


async def test_paused_cycle_survives_restart(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    await hass.services.async_call(DOMAIN, "pause_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    await _restart(hass, entry)
    state = data(hass, entry)["scheduler"].active_cycles[cid]
    assert state["paused"]
    await hass.services.async_call(DOMAIN, "resume_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    assert is_on(hass, Z2)


async def test_cycle_not_resumed_after_long_downtime(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    store = data(hass, entry)["store"]
    old = int(dt_util.utcnow().timestamp()) - 3 * 3600
    store._data["cycle_state"] = {"saved_at": old, "cycles": [{
        "cycle_id": cid, "cycle_name": "Morning", "started_at": old, "step": 1, "total_steps": 2,
        "current_entity": Z1, "source": "schedule", "note": "", "duration_factor": 1.0, "step_ends_at": old + 300,
    }]}
    await store.async_save()
    await _restart(hass, entry)
    assert cid not in data(hass, entry)["scheduler"].active_cycles
    assert not is_on(hass, Z2)
    assert statuses(hass, entry, cid)[0] == "cycle_cancelled"


async def test_missing_entity_repairs_issue(hass: HomeAssistant):
    entry = await setup_wizard(hass, {"rain_entity": "sensor.gone"})
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": "switch.ghost", "label": "Ghost"}, blocking=True)
    await advance(hass, 121)
    reg = ir.async_get(hass)
    ids = {i.issue_id for i in reg.issues.values() if i.domain == DOMAIN}
    assert "missing_zone_switch_ghost" in ids
    assert "missing_rain_entity_sensor_gone" in ids
    assert not any("zone1" in i for i in ids)
    hass.states.async_set("switch.ghost", "off")
    await hass.services.async_call(DOMAIN, "remove_valve", {"entity_id": "switch.ghost"}, blocking=True)
    await settle(hass)
    ids = {i.issue_id for i in reg.issues.values() if i.domain == DOMAIN}
    assert "missing_zone_switch_ghost" not in ids


async def test_diagnostics(hass: HomeAssistant):
    entry = await setup_wizard(hass, {"notify_targets": ["mobile_app_secret_phone"]})
    await add_valve(hass, Z1, "Front")
    from custom_components.schedule_wizard.diagnostics import async_get_config_entry_diagnostics
    diag = await async_get_config_entry_diagnostics(hass, entry)
    assert diag["valves"][0]["entity_id"] == Z1
    assert diag["options"]["notify_targets"] == "**REDACTED**"
    assert diag["entry_data"]["webhook_id"] == "**REDACTED**"
    assert "forecast" in diag


async def test_ha_shutdown_keeps_cycle_for_resume(hass: HomeAssistant):
    from homeassistant.const import EVENT_HOMEASSISTANT_STOP
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 5), (Z2, 5)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    scheduler = data(hass, entry)["scheduler"]
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await settle(hass)
    scheduler.active_cycles[cid]["task"].cancel()  # what HA does to background tasks on shutdown
    await settle(hass)
    store = data(hass, entry)["store"]
    assert [c["cycle_id"] for c in store.cycle_state["cycles"]] == [cid]
    assert [r["entity_id"] for r in store.active_runs] == [Z1]
    assert is_on(hass, Z1)
    assert "cycle_cancelled" not in statuses(hass, entry, cid)
