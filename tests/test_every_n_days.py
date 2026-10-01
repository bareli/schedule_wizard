"""#27: schedules that repeat every N days from a start date."""
from __future__ import annotations

from datetime import date, datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.schedule_wizard import planner
from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, settle, setup_wizard
from .test_scheduler import Z1, Z2, add_cycle, add_valve, statuses

pytestmark = pytest.mark.usefixtures("zones")


def interval(n: int, start: str, hhmm: str = "06:00") -> dict:
    return {"repeat": "interval", "interval_days": n, "start_date": start, "time_hhmm": hhmm, "days_mask": 0}


async def add_schedule(hass, **fields) -> dict:
    resp = await hass.services.async_call(DOMAIN, "add_schedule", fields, blocking=True, return_response=True)
    return resp["schedule"]


async def fire_local(hass: HomeAssistant, tz: str, y: int, m: int, d: int, hh: int = 6, mm: int = 0) -> None:
    async_fire_time_changed(hass, dt_util.as_utc(datetime(y, m, d, hh, mm, tzinfo=ZoneInfo(tz))))
    await settle(hass)


def starts(hass, entry) -> int:
    return statuses(hass, entry, Z1).count("started")


# ---------------------------------------------------------------- pure matching

@pytest.mark.parametrize(("start", "n", "day", "expected"), [
    ("2026-12-30", 3, "2026-12-30", True),
    ("2026-12-30", 3, "2026-12-31", False),
    ("2026-12-30", 3, "2027-01-02", True),   # year boundary
    ("2026-12-30", 3, "2027-01-05", True),
    ("2026-01-30", 2, "2026-02-01", True),   # month boundary (31-day January)
    ("2028-02-27", 2, "2028-02-29", True),   # leap day
    ("2028-02-27", 2, "2028-03-02", True),
    ("2028-02-27", 2, "2028-03-01", False),
    ("2026-10-10", 2, "2026-10-08", False),  # before the start date
    ("2026-10-10", 30, "2026-11-09", True),
])
def test_runs_on(start, n, day, expected):
    assert planner.runs_on(interval(n, start), date.fromisoformat(day)) is expected


def test_runs_on_weekdays_and_bad_data():
    assert planner.runs_on({"days_mask": 1}, date(2026, 10, 5))  # Monday
    assert not planner.runs_on({"days_mask": 1}, date(2026, 10, 6))
    assert not planner.runs_on(interval(2, ""), date(2026, 10, 6))
    assert not planner.runs_on(interval(0, "2026-10-06"), date(2026, 10, 6))


@pytest.mark.parametrize(("tz", "start", "after", "expected"), [
    # Israel leaves summer time on 2026-10-25 and enters it on 2027-03-26.
    ("Asia/Jerusalem", "2026-10-23", datetime(2026, 10, 23, 7, 0), datetime(2026, 10, 25, 6, 0)),
    ("Asia/Jerusalem", "2027-03-24", datetime(2027, 3, 24, 7, 0), datetime(2027, 3, 26, 6, 0)),
    # US Eastern leaves summer time on 2026-11-01 and enters it on 2027-03-14.
    ("America/New_York", "2026-10-30", datetime(2026, 10, 30, 7, 0), datetime(2026, 11, 2, 6, 0)),
    ("America/New_York", "2027-03-12", datetime(2027, 3, 12, 7, 0), datetime(2027, 3, 14, 6, 0)),
])
async def test_next_fire_across_dst(hass: HomeAssistant, tz, start, after, expected):
    await hass.config.async_set_time_zone(tz)
    n = (expected.date() - date.fromisoformat(start)).days
    zone = ZoneInfo(tz)
    fire = planner.next_fire(interval(n, start), after.replace(tzinfo=zone))
    assert fire is not None
    assert fire.replace(tzinfo=None) == expected  # same local wall-clock time after the change
    assert fire.utcoffset() == expected.replace(tzinfo=zone).utcoffset()


# ---------------------------------------------------------------- cron loop

@pytest.mark.parametrize(("tz", "start", "days", "runs"), [
    ("Asia/Jerusalem", date(2026, 10, 23), 6, {0, 2, 4, 6}),
    ("America/New_York", date(2026, 10, 30), 7, {0, 3, 6}),
    ("America/New_York", date(2027, 3, 13), 4, {0, 2, 4}),
    ("Asia/Jerusalem", date(2026, 12, 30), 7, {0, 3, 6}),  # crosses the new year
])
async def test_cron_every_n_days_across_dst(hass: HomeAssistant, tz, start, days, runs):
    await hass.config.async_set_time_zone(tz)
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    n = sorted(runs)[1] - sorted(runs)[0]
    await add_schedule(hass, valve_entity_id=Z1, time="06:00", every_n_days=n,
                       start_date=start.isoformat(), duration_minutes=2)
    seen = set()
    for offset in range(days + 1):
        d = start + timedelta(days=offset)
        before = starts(hass, entry)
        # One hour early (what counting 24h periods would do across a DST change) must not fire.
        await fire_local(hass, tz, d.year, d.month, d.day, 5, 0)
        assert starts(hass, entry) == before, f"fired at 05:00 on {d}"
        await fire_local(hass, tz, d.year, d.month, d.day, 6, 0)
        if starts(hass, entry) > before:
            seen.add(offset)
        await fire_local(hass, tz, d.year, d.month, d.day, 6, 5)  # run ends
    assert seen == runs


async def test_cycle_every_n_days(hass: HomeAssistant):
    tz = "Asia/Jerusalem"
    await hass.config.async_set_time_zone(tz)
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 1), (Z2, 1)])
    await add_schedule(hass, cycle_id=cid, time="06:00", every_n_days=2, start_date="2026-11-02")
    for d in (1, 2, 3, 4):
        for mm in (0, 2, 4, 6, 8):  # each step's end timer is armed when the step starts
            await fire_local(hass, tz, 2026, 11, d, 6, mm)
    assert statuses(hass, entry, cid).count("cycle_completed") == 2


# ---------------------------------------------------------------- next run, sensor, calendar, week

async def test_next_run_and_sensor(hass: HomeAssistant, hass_ws_client):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    today = dt_util.now().date()
    sched = await add_schedule(hass, valve_entity_id=Z1, time="06:00", every_n_days=30,
                               start_date=(today - timedelta(days=1)).isoformat(), duration_minutes=7)
    expected = datetime.combine(today + timedelta(days=29), dtime(6, 0), tzinfo=dt_util.get_default_time_zone())

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    result = (await client.receive_json())["result"]
    valve = result["valves"][0]
    assert valve["next_run"]["schedule_id"] == sched["id"]
    assert valve["next_run"]["fires_at"] == int(expected.timestamp())
    assert result["schedules"][0]["repeat"] == "interval"
    assert result["schedules"][0]["interval_days"] == 30

    await async_update_entity(hass, "sensor.schedule_wizard_next_schedule")
    state = hass.states.get("sensor.schedule_wizard_next_schedule")
    assert state.attributes["schedule_id"] == sched["id"]
    assert state.attributes["duration_min"] == 7
    assert abs(state.attributes["fires_in_minutes"] - (expected - dt_util.now()).total_seconds() // 60) <= 1


async def test_next_run_with_distant_start_date(hass: HomeAssistant, hass_ws_client):
    """#28: a start date more than NEXT_RUN_DAYS ahead is still the next run (zone card, sensor, skip next)."""
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    today = dt_util.now().date()
    first = today + timedelta(days=60)
    sched = await add_schedule(hass, valve_entity_id=Z1, time="07:00", every_n_days=7,
                               start_date=first.isoformat(), duration_minutes=5)
    expected = datetime.combine(first, dtime(7, 0), tzinfo=dt_util.get_default_time_zone())
    assert planner.next_fire(sched, dt_util.now()) == expected

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    valve = (await client.receive_json())["result"]["valves"][0]
    assert valve["next_run"] is not None
    assert valve["next_run"]["fires_at"] == int(expected.timestamp())

    await async_update_entity(hass, "sensor.schedule_wizard_next_schedule")
    state = hass.states.get("sensor.schedule_wizard_next_schedule")
    assert state.attributes["schedule_id"] == sched["id"]

    await async_update_entity(hass, "calendar.schedule_wizard_watering_schedule")
    cal = hass.states.get("calendar.schedule_wizard_watering_schedule")
    assert cal.attributes["start_time"] == expected.strftime("%Y-%m-%d %H:%M:%S")

    resp = await hass.services.async_call(DOMAIN, "skip_next", {"schedule_id": sched["id"]},
                                          blocking=True, return_response=True)
    assert resp["skipped"]["day"] == first.isoformat()


async def test_calendar_and_week_view(hass: HomeAssistant, hass_ws_client):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    today = dt_util.now().date()
    await add_schedule(hass, valve_entity_id=Z1, time="06:00", every_n_days=2,
                       start_date=today.isoformat(), duration_minutes=10)
    await settle(hass)
    start = dt_util.start_of_local_day() + timedelta(days=1)
    resp = await hass.services.async_call(
        "calendar", "get_events",
        {"entity_id": "calendar.schedule_wizard_watering_schedule", "start_date_time": start.isoformat(),
         "end_date_time": (start + timedelta(days=6)).isoformat()},
        blocking=True, return_response=True,
    )
    events = resp["calendar.schedule_wizard_watering_schedule"]["events"]
    days = [dt_util.parse_datetime(e["start"]).date() for e in events]
    assert days == [today + timedelta(days=k) for k in (2, 4, 6)]

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    week = (await client.receive_json())["result"]["week"]
    assert sorted({o["day"] for o in week}) == [(today + timedelta(days=k)).isoformat() for k in (0, 2, 4, 6)]


async def test_skip_next_uses_interval(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    today = dt_util.now().date()
    sched = await add_schedule(hass, valve_entity_id=Z1, time="06:00", every_n_days=10,
                               start_date=(today + timedelta(days=12)).isoformat())
    resp = await hass.services.async_call(DOMAIN, "skip_next", {"schedule_id": sched["id"]},
                                          blocking=True, return_response=True)
    assert resp["skipped"]["day"] == (today + timedelta(days=12)).isoformat()
    assert data(hass, entry)["store"].skips[sched["id"]] == [(today + timedelta(days=12)).isoformat()]


# ---------------------------------------------------------------- validation

@pytest.mark.parametrize("fields", [
    {"every_n_days": 1, "start_date": "2026-10-01"},
    {"every_n_days": 31, "start_date": "2026-10-01"},
    {"every_n_days": 2, "start_date": ""},
    {"every_n_days": 2, "start_date": "2026-13-01"},
    {"days": []},
])
async def test_add_schedule_rejects_bad_values(hass: HomeAssistant, fields):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    with pytest.raises((vol.Invalid, HomeAssistantError)):
        await add_schedule(hass, valve_entity_id=Z1, time="06:00", **fields)
    assert not data(hass, hass.config_entries.async_entries(DOMAIN)[0])["store"].schedules


@pytest.mark.parametrize("fields", [
    {},  # neither days nor every_n_days
    {"days": ["mon"], "every_n_days": 2},
    {"days": ["mon"], "start_date": "2026-10-01"},
    {"start_date": "2026-10-01"},
])
async def test_add_schedule_rejects_bad_combinations(hass: HomeAssistant, fields):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    with pytest.raises(HomeAssistantError):
        await add_schedule(hass, valve_entity_id=Z1, time="06:00", **fields)


async def test_start_date_defaults_to_today(hass: HomeAssistant):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    sched = await add_schedule(hass, valve_entity_id=Z1, time="06:00", every_n_days=3)
    assert sched["start_date"] == dt_util.now().date().isoformat()
    assert sched["repeat"] == "interval" and sched["interval_days"] == 3


async def test_update_switches_between_modes(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    sched = await add_schedule(hass, valve_entity_id=Z1, time="06:00", days=["mon", "thu"])
    sid = sched["id"]
    assert sched["repeat"] == "weekdays"

    async def update(**fields):
        resp = await hass.services.async_call(DOMAIN, "update_schedule", {"schedule_id": sid, **fields},
                                              blocking=True, return_response=True)
        return resp["schedule"]

    s = await update(every_n_days=4, start_date="2026-11-01")
    assert (s["repeat"], s["interval_days"], s["start_date"]) == ("interval", 4, "2026-11-01")
    s = await update(start_date="2026-11-03")
    assert (s["interval_days"], s["start_date"]) == (4, "2026-11-03")
    s = await update(every_n_days=5)
    assert (s["interval_days"], s["start_date"]) == (5, "2026-11-03")
    s = await update(name="Lawn")
    assert s["repeat"] == "interval"
    with pytest.raises(vol.Invalid):
        await update(every_n_days=40)
    s = await update(days=["tue"])
    assert (s["repeat"], s["days_mask"], s["interval_days"], s["start_date"]) == ("weekdays", 2, 0, "")
    with pytest.raises(HomeAssistantError):
        await update(start_date="2026-11-03")
    assert data(hass, entry)["store"].get_schedule(sid)["repeat"] == "weekdays"


# ---------------------------------------------------------------- stored data from 0.13

async def test_legacy_schedule_still_weekday_based(hass: HomeAssistant, hass_storage):
    hass_storage[f"{DOMAIN}.data"] = {
        "version": 1, "key": f"{DOMAIN}.data",
        "data": {
            "valves": [{"entity_id": Z1, "label": "Front", "default_duration_min": 10, "enabled": True}],
            "schedules": [{"id": "legacy1", "valve_entity_id": Z1, "cycle_id": "", "name": "",
                           "days_mask": 1, "time_hhmm": "06:00", "duration_min": 3, "enabled": True,
                           "conditions": [], "created_at": 0}],
            "history": [], "cycles": [],
        },
    }
    tz = "Asia/Jerusalem"
    await hass.config.async_set_time_zone(tz)
    entry = await setup_wizard(hass)
    sched = data(hass, entry)["store"].get_schedule("legacy1")
    assert sched["repeat"] == "weekdays"
    await fire_local(hass, tz, 2026, 11, 3)  # Tuesday
    assert starts(hass, entry) == 0
    await fire_local(hass, tz, 2026, 11, 9)  # Monday
    assert starts(hass, entry) == 1
