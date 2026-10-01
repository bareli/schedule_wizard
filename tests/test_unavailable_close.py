"""#80 (BUG-019) and #54 (BUG-015): a close sent to an unavailable valve is not done."""
from __future__ import annotations

import time

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import advance, data, settle, setup_wizard

V = "switch.qa_late_valve"
V2 = "switch.qa_other_valve"
MASTER = "switch.qa_master"


class FakeSwitches:
    """switch.turn_on / turn_off like HA: a call to a missing or unavailable entity is dropped."""

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.calls: list[tuple[str, str]] = []
        self.raise_next_off = 0
        self.register()

    def register(self) -> None:
        self.hass.services.async_register("switch", "turn_on", self._on)
        self.hass.services.async_register("switch", "turn_off", self._off)

    def _targets(self, call: ServiceCall) -> list[str]:
        ids = call.data["entity_id"]
        return [ids] if isinstance(ids, str) else list(ids)

    def _set(self, call: ServiceCall, verb: str, value: str) -> None:
        for entity_id in self._targets(call):
            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unavailable", "unknown"):
                self.calls.append(("refused", entity_id))
                continue
            self.calls.append((verb, entity_id))
            self.hass.states.async_set(entity_id, value)

    async def _on(self, call: ServiceCall) -> None:
        self._set(call, "on", "on")

    async def _off(self, call: ServiceCall) -> None:
        if self.raise_next_off:
            self.raise_next_off -= 1
            self.calls.append(("error", self._targets(call)[0]))
            raise HomeAssistantError("device did not answer")
        self._set(call, "off", "off")


async def _setup(hass: HomeAssistant, options: dict | None = None):
    for entity_id in (V, V2, MASTER):
        hass.states.async_set(entity_id, "off")
    entry = await setup_wizard(hass, options)
    fake = FakeSwitches(hass)  # after setup: the switch platform registers the real services
    for entity_id, label in ((V, "Late"), (V2, "Other")):
        await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": entity_id, "label": label}, blocking=True)
    return entry, fake


def _history(hass, entry, entity_id=V) -> list[str]:
    return [h["status"] for h in data(hass, entry)["store"].history if h["valve_entity_id"] == entity_id]


def _state(hass, entity_id=V) -> str:
    return hass.states.get(entity_id).state


async def _run(hass, entity_id=V, minutes=1):
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": entity_id, "duration_minutes": minutes}, blocking=True)
    await settle(hass)
    assert _state(hass, entity_id) == "on"


async def test_run_ends_while_unavailable_closes_when_back(hass: HomeAssistant):
    """#80: the valve drops out before the end; the refused close is not recorded as completed."""
    entry, fake = await _setup(hass)
    await _run(hass)
    hass.states.async_set(V, "unavailable")
    await advance(hass, 61)
    assert _history(hass, entry) == ["started"], "close to an unavailable valve recorded as done"
    scheduler = data(hass, entry)["scheduler"]
    assert scheduler.pending_close == [V]
    assert [p["entity_id"] for p in data(hass, entry)["store"].pending_closes] == [V]
    hass.states.async_set(V, "on")  # back, still physically open
    await settle(hass)
    assert _state(hass) == "off", "valve left open after it came back"
    assert _history(hass, entry) == ["completed", "started"]
    assert scheduler.pending_close == []
    assert data(hass, entry)["store"].pending_closes == []


async def test_restored_stale_on_then_unavailable_closes_when_back(hass: HomeAssistant, hass_storage):
    """#54 reopened: restored `on` at load, unavailable ms later, still unavailable at the run's end."""
    now = int(time.time())
    hass_storage[f"{DOMAIN}.data"] = {
        "version": 1, "key": f"{DOMAIN}.data",
        "data": {
            "valves": [{"entity_id": V, "label": "Late", "default_duration_min": 10, "enabled": True}],
            "schedules": [], "history": [], "cycles": [],
            "active_runs": [{"entity_id": V, "started_at": now - 60, "ends_at": now + 120,
                             "duration_min": 3, "source": "schedule", "note": ""}],
        },
    }
    hass.states.async_set(V, "on")  # the entity re-adds with its restored state first
    entry = await setup_wizard(hass)
    FakeSwitches(hass)
    assert V in data(hass, entry)["scheduler"].active
    hass.states.async_set(V, "unavailable")
    await advance(hass, 130)
    assert _history(hass, entry) == [], "close to an unavailable valve recorded as done"
    hass.states.async_set(V, "on")
    await settle(hass)
    assert _state(hass) == "off", "valve left open after it came back"
    assert _history(hass, entry) == ["completed"]
    assert V not in data(hass, entry)["scheduler"].active


async def test_stop_on_unavailable_valve_closes_when_back(hass: HomeAssistant):
    entry, fake = await _setup(hass)
    await _run(hass, minutes=10)
    hass.states.async_set(V, "unavailable")
    await hass.services.async_call(DOMAIN, "stop_valve", {"entity_id": V}, blocking=True)
    await settle(hass)
    assert V not in data(hass, entry)["scheduler"].active
    assert _history(hass, entry) == ["started"]
    hass.states.async_set(V, "on")
    await settle(hass)
    assert _state(hass) == "off", "stopped valve left open after it came back"
    assert _history(hass, entry) == ["cancelled", "started"]


async def test_pending_close_survives_restart(hass: HomeAssistant):
    entry, fake = await _setup(hass)
    await _run(hass)
    hass.states.async_set(V, "unavailable")
    await advance(hass, 61)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await settle(hass)
    fake.register()
    hass.states.async_set(V, "on")
    await settle(hass)
    assert _state(hass) == "off", "pending close lost across the restart"
    assert _history(hass, entry) == ["completed", "started"]
    assert data(hass, entry)["scheduler"].pending_close == []
    assert data(hass, entry)["store"].pending_closes == []


async def test_pending_close_valve_back_off_is_done(hass: HomeAssistant):
    """Owner policy: a first real state of `off` is trusted as closed."""
    entry, fake = await _setup(hass)
    await _run(hass)
    hass.states.async_set(V, "unavailable")
    await advance(hass, 61)
    hass.states.async_set(V, "off")
    await settle(hass)
    assert ("off", V) not in fake.calls
    assert _history(hass, entry) == ["completed", "started"]
    assert data(hass, entry)["scheduler"].pending_close == []


async def test_master_valve_unavailable_closes_when_back(hass: HomeAssistant):
    entry, fake = await _setup(hass, {"master_valve_entity": MASTER})
    await _run(hass)
    assert _state(hass, MASTER) == "on"
    hass.states.async_set(MASTER, "unavailable")
    await advance(hass, 61)
    assert _state(hass) == "off"
    hass.states.async_set(MASTER, "on")
    await settle(hass)
    assert _state(hass, MASTER) == "off", "master valve left open after it came back"


async def test_refused_close_on_available_valve_is_retried(hass: HomeAssistant):
    entry, fake = await _setup(hass)
    await _run(hass)
    fake.raise_next_off = 1
    await advance(hass, 61)
    assert _state(hass) == "on"
    assert _history(hass, entry) == ["started"]
    await advance(hass, 61)
    assert _state(hass) == "off", "refused close never retried"
    assert _history(hass, entry) == ["completed", "started"]


async def test_plan_step_unavailable_plan_continues_and_valve_closed(hass: HomeAssistant):
    entry, fake = await _setup(hass)
    resp = await hass.services.async_call(
        DOMAIN, "add_cycle",
        {"name": "Morning", "steps": [{"entity_id": V, "duration_minutes": 1}, {"entity_id": V2, "duration_minutes": 1}]},
        blocking=True, return_response=True,
    )
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": resp["cycle"]["id"]}, blocking=True)
    await settle(hass)
    assert _state(hass) == "on"
    hass.states.async_set(V, "unavailable")
    await advance(hass, 61)
    assert _state(hass, V2) == "on", "plan did not go on to the next zone"
    hass.states.async_set(V, "on")
    await settle(hass)
    assert _state(hass) == "off", "plan step valve left open after it came back"
    assert _history(hass, entry)[0] == "completed"
    await advance(hass, 61)
    assert _state(hass, V2) == "off"
