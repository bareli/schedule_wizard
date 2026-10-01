"""Fixtures for Schedule Wizard tests."""
from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.schedule_wizard.const import DOMAIN

ZONES = ("zone1", "zone2", "zone3", "master")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def no_frontend():
    """Panel + Lovelace registration need the frontend package; not under test."""
    with (
        patch("custom_components.schedule_wizard._async_register_panel", AsyncMock()),
        patch("custom_components.schedule_wizard._async_register_card_resource", AsyncMock()),
    ):
        yield


class FakeCalendar:
    """Stands in for calendar.get_events."""

    def __init__(self, hass: HomeAssistant, entity_id: str = "calendar.garden"):
        self.entity_id = entity_id
        self.events: list[dict] = []

        async def _get_events(call: ServiceCall):
            return {self.entity_id: {"events": list(self.events)}}

        hass.services.async_register(
            "calendar", "get_events", _get_events, supports_response=SupportsResponse.ONLY
        )


# 10:00:30 in the test time zone (US/Pacific, summer time): 30 s before a minute starts, far from midnight.
FIXED_INSTANT = "2026-06-10 17:00:30+00:00"


@pytest.fixture
def fixed_clock():
    """Start the clock at a fixed instant and let it run (flake fix).

    Tests that schedule "the next minute" (_schedule_now) failed about 1 run in 6 when the real clock crossed
    a minute between computing that minute and firing it: two schedules got different minutes, or the real
    minute tick ran before the schedule existed. From a fixed :30 instant no minute starts during a test.
    """
    import freezegun

    with freezegun.freeze_time(FIXED_INSTANT, tick=True):
        yield


@pytest.fixture
async def zones(hass: HomeAssistant):
    assert await async_setup_component(
        hass, "input_boolean", {"input_boolean": {z: {} for z in ZONES}}
    )
    await hass.async_block_till_done()


async def setup_wizard(hass: HomeAssistant, options: dict | None = None) -> MockConfigEntry:
    # Frontend-only dependencies are marked loaded so setup doesn't pull hass_frontend.
    hass.config.components.update({"frontend", "panel_custom", "lovelace"})
    assert await async_setup_component(hass, "calendar", {})
    entry = MockConfigEntry(domain=DOMAIN, title="Schedule Wizard", data={}, options=options or {})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def data(hass: HomeAssistant, entry: MockConfigEntry) -> dict:
    return hass.data[DOMAIN][entry.entry_id]


async def settle(hass: HomeAssistant, rounds: int = 25) -> None:
    """Let background tasks (not awaited by block_till_done) make progress."""
    for _ in range(rounds):
        await asyncio.sleep(0)
        await hass.async_block_till_done()


async def advance(hass: HomeAssistant, seconds: float) -> None:
    """Fire every timer (including asyncio.sleep) due within `seconds` from now."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=seconds))
    await settle(hass)


def is_on(hass: HomeAssistant, entity_id: str) -> bool:
    return hass.states.get(entity_id).state == "on"
