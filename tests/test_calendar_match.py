"""#38 (SEC-005): calendar events match zone labels and plan names as whole words of the summary."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.schedule_wizard.const import DOMAIN
from custom_components.schedule_wizard.scheduler import Scheduler

from .conftest import FakeCalendar, advance, data, setup_wizard

pytestmark = pytest.mark.usefixtures("zones")

Z1, Z2 = "input_boolean.zone1", "input_boolean.zone2"


def _valves(*labels):
    return [{"entity_id": f"switch.v{i}", "label": label} for i, label in enumerate(labels)]


@pytest.mark.parametrize(("label", "summary", "matches"), [
    ("Front lawn", "Front lawn", True),
    ("Front lawn", "front LAWN morning cycle", True),
    ("Front lawn", "Water: Front lawn, 15 min", True),
    ("Front lawn", "Front lawns", False),
    ("Front", "Storefront meeting", False),
    ("Front", "Frontend review", False),
    ("Herbs", "Re: herbs-garden", True),
    ("גינה", "השקיה גינה בוקר", True),
    ("גינה", "גינות", False),
    ("a", "Stuff about a", False),
    ("a", "Lunch with a friend", False),
    ("a", "A", True),
    ("B2", "Call B2 team", False),
    ("B2", " b2 ", True),
    ("Zone (east)", "Water Zone (east) now", True),
])
def test_summary_match(label, summary, matches):
    assert (Scheduler._match_valve(summary, _valves(label)) is not None) is matches


def test_longest_whole_word_label_wins():
    valves = _valves("Lawn", "Back lawn")
    assert Scheduler._match_valve("Back lawn deep soak", valves)["label"] == "Back lawn"
    assert Scheduler._match_valve("Lawn", valves)["label"] == "Lawn"


def test_entity_id_whole_word_only():
    valves = [{"entity_id": "switch.front", "label": "Garden"}]
    assert Scheduler._match_valve("run switch.front", valves) is not None
    assert Scheduler._match_valve("run switch.frontyard", valves) is None


def test_plan_names_whole_word():
    cycles = [{"id": "c1", "name": "Morning"}, {"id": "c2", "name": "AM"}]
    assert Scheduler._match_cycle("Morning watering", cycles)["id"] == "c1"
    assert Scheduler._match_cycle("Good mornings", cycles) is None
    assert Scheduler._match_cycle("Team meeting 9am", cycles) is None
    assert Scheduler._match_cycle("am", cycles)["id"] == "c2"


async def _poll_with(hass, summary, description=""):
    entry = await setup_wizard(hass, {"calendar_entity": "calendar.garden"})
    cal = FakeCalendar(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "a"}, blocking=True)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z2, "label": "Front"}, blocking=True)
    start = dt_util.now().replace(microsecond=0) + timedelta(minutes=5)
    cal.events = [{"summary": summary, "description": description, "start": start.isoformat(),
                   "end": (start + timedelta(minutes=10)).isoformat()}]
    await advance(hass, 61)
    return data(hass, entry)["scheduler"]


async def test_invited_event_with_short_label_does_not_run(hass: HomeAssistant):
    """An outsider's event 'Stuff about a' no longer starts zone 'a'."""
    scheduler = await _poll_with(hass, "Stuff about a")
    assert not scheduler._calendar_pending


async def test_description_is_not_matched(hass: HomeAssistant):
    scheduler = await _poll_with(hass, "Dentist", "Front desk, 15 min")
    assert not scheduler._calendar_pending


async def test_whole_word_event_still_runs(hass: HomeAssistant):
    scheduler = await _poll_with(hass, "Front lawn watering", "10 min")
    assert len(scheduler._calendar_pending) == 1
