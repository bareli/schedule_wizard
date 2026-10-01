"""#54 (BUG-015, RUN-02): a run restored after a restart whose valve is not available yet."""
from __future__ import annotations

import time

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import advance, data, setup_wizard

V = "switch.qa_late_valve"


def _storage(ends_in: int) -> dict:
    now = int(time.time())
    return {
        "version": 1, "key": f"{DOMAIN}.data",
        "data": {
            "valves": [{"entity_id": V, "label": "Late", "default_duration_min": 10, "enabled": True}],
            "schedules": [], "history": [], "cycles": [],
            "active_runs": [{"entity_id": V, "started_at": now - 60, "ends_at": now + ends_in,
                             "duration_min": 3, "source": "schedule", "note": ""}],
        },
    }


def _mock_off(hass):
    """After setup: the switch platform registers the real switch services."""
    return async_mock_service(hass, "switch", "turn_off")


def _history(hass, entry) -> list[str]:
    return [h["status"] for h in data(hass, entry)["store"].history if h["valve_entity_id"] == V]


async def test_restore_valve_missing_at_setup_closes_at_end(hass: HomeAssistant, hass_storage):
    """Valve integration loads after Schedule Wizard; the valve comes up still open."""
    hass_storage[f"{DOMAIN}.data"] = _storage(120)
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    assert V in data(hass, entry)["scheduler"].active
    hass.states.async_set(V, "on")
    await advance(hass, 60)
    assert not off, "closed before the run's end"
    assert V in data(hass, entry)["scheduler"].active
    await advance(hass, 130)
    assert len(off) == 1 and off[0].data["entity_id"] == V
    assert _history(hass, entry) == ["completed"]
    assert V not in data(hass, entry)["scheduler"].active
    assert data(hass, entry)["store"].active_runs == []


async def test_restore_valve_unavailable_at_setup_closes_at_end(hass: HomeAssistant, hass_storage):
    hass_storage[f"{DOMAIN}.data"] = _storage(120)
    hass.states.async_set(V, "unavailable")
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    hass.states.async_set(V, "on")
    await advance(hass, 130)
    assert len(off) == 1
    assert _history(hass, entry) == ["completed"]


async def test_restore_valve_back_after_end_closes_immediately(hass: HomeAssistant, hass_storage):
    """Still unavailable when the run ends: close as soon as the valve reports a state."""
    hass_storage[f"{DOMAIN}.data"] = _storage(120)
    hass.states.async_set(V, "unknown")
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    await advance(hass, 130)
    assert not off
    assert V in data(hass, entry)["scheduler"].active, "run dropped while the valve was unavailable"
    hass.states.async_set(V, "on")
    await advance(hass, 1)
    assert len(off) == 1
    assert _history(hass, entry) == ["completed"]


async def test_restore_expired_run_valve_unavailable(hass: HomeAssistant, hass_storage):
    """Run ended during the downtime and the valve is not loaded yet: close it when it appears."""
    hass_storage[f"{DOMAIN}.data"] = _storage(-30)
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    await advance(hass, 1)
    assert not off
    hass.states.async_set(V, "on")
    await advance(hass, 1)
    assert len(off) == 1
    assert _history(hass, entry) == ["expired_during_downtime"]


async def test_restore_valve_comes_back_closed(hass: HomeAssistant, hass_storage):
    """Valve reports off once loaded: closed during the downtime, one terminal row, no timer left."""
    hass_storage[f"{DOMAIN}.data"] = _storage(120)
    hass.states.async_set(V, "unavailable")
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    hass.states.async_set(V, "off")
    await advance(hass, 1)
    assert V not in data(hass, entry)["scheduler"].active
    assert _history(hass, entry) == ["cancelled_during_downtime"]
    await advance(hass, 130)
    assert not off
    assert _history(hass, entry) == ["cancelled_during_downtime"]


async def test_restore_stopped_while_unavailable_still_closes(hass: HomeAssistant, hass_storage):
    """Stop pressed before the valve came back: it is closed when it reports open."""
    hass_storage[f"{DOMAIN}.data"] = _storage(120)
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    await hass.services.async_call(DOMAIN, "stop_valve", {"entity_id": V}, blocking=True)
    calls_after_stop = len(off)
    assert V not in data(hass, entry)["scheduler"].active
    hass.states.async_set(V, "on")
    await advance(hass, 1)
    assert len(off) == calls_after_stop + 1
    assert _history(hass, entry) == ["cancelled"]


async def test_restore_plan_step_waits_for_valve(hass: HomeAssistant, hass_storage):
    """A plan's current zone is restored unavailable and still unavailable at its end: the plan waits, then closes it."""
    now = int(time.time())
    stored = _storage(120)
    stored["data"]["cycles"] = [{"id": "c1", "name": "Morning", "enabled": True,
                                 "steps": [{"entity_id": V, "duration_min": 3}]}]
    stored["data"]["active_runs"][0]["source"] = "cycle:c1"
    stored["data"]["cycle_state"] = {"saved_at": now - 5, "cycles": [{
        "cycle_id": "c1", "cycle_name": "Morning", "started_at": now - 60, "step": 1, "total_steps": 1,
        "current_entity": V, "source": "schedule", "note": "", "duration_factor": 1.0, "step_ends_at": now + 120,
    }]}
    hass_storage[f"{DOMAIN}.data"] = stored
    entry = await setup_wizard(hass)
    off = _mock_off(hass)
    await advance(hass, 130)
    assert not off
    assert "c1" in data(hass, entry)["scheduler"].active_cycles
    hass.states.async_set(V, "on")
    await advance(hass, 10)
    assert len(off) == 1
    history = [h["status"] for h in data(hass, entry)["store"].history]
    assert history[:2] == ["cycle_completed", "completed"]
    assert "c1" not in data(hass, entry)["scheduler"].active_cycles
