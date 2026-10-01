"""#57 (BUG-018): history rows keep a plan's name, so they still read after the plan is deleted."""
from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import advance, data, settle, setup_wizard

pytestmark = pytest.mark.usefixtures("zones")

Z1 = "input_boolean.zone1"


async def test_deleted_plan_rows_keep_its_name(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    resp = await hass.services.async_call(
        DOMAIN, "add_cycle", {"name": "QAE gone", "steps": [{"entity_id": Z1, "duration_minutes": 5}]},
        blocking=True, return_response=True,
    )
    cid = resp["cycle"]["id"]
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    await advance(hass, 60)
    await hass.services.async_call(DOMAIN, "stop_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    await hass.services.async_call(DOMAIN, "remove_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)

    store = data(hass, entry)["store"]
    assert store.get_cycle(cid) is None
    plan_rows = [h for h in store.history if h["valve_entity_id"] == cid]
    step_rows = [h for h in store.history if h["source"].startswith(f"cycle:{cid}")]
    assert plan_rows and step_rows
    assert {h["status"] for h in plan_rows} == {"cycle_cancelled"}
    assert all(h["name"] == "QAE gone" for h in plan_rows)
    assert all(h["plan_name"] == "QAE gone" for h in step_rows)
    assert all("name" not in h for h in step_rows), "zone rows are named by their zone, not the plan"


async def test_zone_rows_unchanged(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 1}, blocking=True)
    await advance(hass, 61)
    for h in data(hass, entry)["store"].history:
        assert "name" not in h and "plan_name" not in h
