"""#59 (ENH-003): start a watering at sunrise or sunset with an offset instead of a clock time."""
from __future__ import annotations

from datetime import date, datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo

import pytest
import voluptuous as vol
from astral import Observer
from astral import sun as astral_sun
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.schedule_wizard import planner
from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, settle, setup_wizard
from .test_scheduler import Z1, add_cycle, add_valve, statuses

pytestmark = pytest.mark.usefixtures("zones")

PLACES = {
    "caesarea": (32.50, 34.89, "Asia/Jerusalem"),
    "berlin": (52.52, 13.40, "Europe/Berlin"),
    "new_york": (40.71, -74.01, "America/New_York"),
    "auckland": (-36.85, 174.76, "Pacific/Auckland"),  # local dates run ahead of UTC dates
    "los_angeles": (34.05, -118.24, "America/Los_Angeles"),  # sunset falls on the next UTC date
    "reykjavik": (64.15, -21.94, "Atlantic/Reykjavik"),
    "helsinki": (60.17, 24.94, "Europe/Helsinki"),
    "tromso": (69.65, 18.96, "Europe/Oslo"),
}


async def at_place(hass: HomeAssistant, place: str) -> ZoneInfo:
    lat, lon, tz = PLACES[place]
    hass.config.latitude = lat
    hass.config.longitude = lon
    hass.config.elevation = 0
    await hass.config.async_set_time_zone(tz)
    return ZoneInfo(tz)


def oracle(place: str, event: str, day: date, offset: int = 0) -> datetime:
    """Independent answer: astral computes the event on the local date of that time zone."""
    lat, lon, tz = PLACES[place]
    func = astral_sun.sunrise if event == "sunrise" else astral_sun.sunset
    when = func(Observer(lat, lon, 0), day, tzinfo=ZoneInfo(tz))
    return (when.astimezone(ZoneInfo("UTC")) + timedelta(minutes=offset)).astimezone(ZoneInfo(tz)).replace(
        second=0, microsecond=0)


def sun(mode: str, offset: int = 0, **extra) -> dict:
    return {"repeat": "weekdays", "days_mask": 127, "time_hhmm": "06:00", "time_mode": mode,
            "sun_offset_min": offset, **extra}


async def add_schedule(hass, **fields) -> dict:
    resp = await hass.services.async_call(DOMAIN, "add_schedule", fields, blocking=True, return_response=True)
    return resp["schedule"]


async def update_schedule(hass, **fields) -> dict:
    resp = await hass.services.async_call(DOMAIN, "update_schedule", fields, blocking=True, return_response=True)
    return resp["schedule"]


async def fire(hass: HomeAssistant, when: datetime) -> None:
    async_fire_time_changed(hass, dt_util.as_utc(when))
    await settle(hass)


# ---------------------------------------------------------------- start time per day

@pytest.mark.parametrize(("place", "event", "day", "offset"), [
    ("caesarea", "sunrise", date(2026, 10, 1), 0),
    ("caesarea", "sunrise", date(2026, 10, 25), -30),   # Israel leaves summer time
    ("caesarea", "sunset", date(2027, 3, 26), 45),      # Israel enters summer time
    ("berlin", "sunrise", date(2026, 10, 25), -60),      # Europe leaves summer time
    ("berlin", "sunrise", date(2027, 3, 28), 15),
    ("new_york", "sunset", date(2026, 11, 1), -20),
    ("auckland", "sunrise", date(2026, 12, 21), 0),
    ("auckland", "sunrise", date(2027, 4, 4), -30),      # NZ leaves summer time
    ("los_angeles", "sunset", date(2026, 6, 21), 30),
])
async def test_fire_at_follows_the_sun(hass: HomeAssistant, place, event, day, offset):
    zone = await at_place(hass, place)
    got = planner.fire_at(sun(event, offset), day, hass)
    assert got is not None
    expected = oracle(place, event, day, offset)
    assert got.astimezone(zone).date() == day
    assert got == expected
    assert planner.fire_hhmm(sun(event, offset), day, hass) == expected.strftime("%H:%M")


async def test_sunrise_moves_with_the_season(hass: HomeAssistant):
    await at_place(hass, "berlin")
    june = planner.fire_at(sun("sunrise"), date(2026, 6, 21), hass)
    december = planner.fire_at(sun("sunrise"), date(2026, 12, 21), hass)
    # Berlin: about 04:43 in June (summer time) and 08:15 in December.
    assert (june.hour, december.hour) == (4, 8)


async def test_offset_past_midnight_stays_on_its_day(hass: HomeAssistant):
    """Reykjavik in June: sunrise near 03:00, 3 h earlier would be the day before; it runs at 00:00."""
    day = date(2026, 6, 21)
    await at_place(hass, "reykjavik")
    assert planner.fire_at(sun("sunrise", -180), day, hass) == datetime.combine(day, dtime(0, 0), tzinfo=ZoneInfo("Atlantic/Reykjavik"))
    # Helsinki: sunset near 22:50, 3 h later would be the next day; it runs at 23:59.
    await at_place(hass, "helsinki")
    assert planner.fire_at(sun("sunset", 180), day, hass) == datetime.combine(day, dtime(23, 59), tzinfo=ZoneInfo("Europe/Helsinki"))


async def test_no_sunrise_no_run(hass: HomeAssistant):
    """Polar night: no sunrise, so no start that day and no next run within the search window."""
    await at_place(hass, "tromso")
    assert planner.fire_at(sun("sunrise"), date(2026, 12, 21), hass) is None
    start = datetime(2026, 12, 1, 12, 0, tzinfo=ZoneInfo("Europe/Oslo"))
    assert planner.next_fire(sun("sunrise"), start, hass=hass) is None
    # The clock-time schedules there are not affected.
    assert planner.next_fire(sun("clock"), start, hass=hass) is not None


def test_clock_schedules_unchanged_without_hass():
    """Legacy schedules (no time_mode) keep their clock time."""
    legacy = {"repeat": "weekdays", "days_mask": 127, "time_hhmm": "06:30"}
    assert planner.time_mode(legacy) == "clock"
    assert planner.fire_hhmm(legacy, date(2026, 10, 1)) == "06:30"
    assert planner.fire_at(sun("sunrise"), date(2026, 10, 1)) is None


# ---------------------------------------------------------------- cron loop

@pytest.mark.parametrize(("place", "first"), [
    ("berlin", date(2026, 10, 24)),       # across the end of summer time
    ("caesarea", date(2027, 3, 25)),      # across the start of summer time
])
async def test_cron_waters_at_sunrise_offset(hass: HomeAssistant, place, first):
    await at_place(hass, place)
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_schedule(hass, valve_entity_id=Z1, time_mode="sunrise", sun_offset_minutes=-30,
                       days=["mon", "tue", "wed", "thu", "fri", "sat", "sun"], duration_minutes=2)
    for k in range(3):
        day = first + timedelta(days=k)
        when = oracle(place, "sunrise", day, -30)
        before = statuses(hass, entry, Z1).count("started")
        await fire(hass, when - timedelta(minutes=1))
        assert statuses(hass, entry, Z1).count("started") == before, f"early on {day}"
        await fire(hass, when)
        assert statuses(hass, entry, Z1).count("started") == before + 1, f"no run on {day} at {when}"
        await fire(hass, when + timedelta(minutes=3))  # run ends


async def test_cron_every_n_days_at_sunset(hass: HomeAssistant):
    await at_place(hass, "caesarea")
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, "input_boolean.zone2", "Back")
    cid = await add_cycle(hass, "Evening", [(Z1, 1), ("input_boolean.zone2", 1)])
    await add_schedule(hass, cycle_id=cid, time_mode="sunset", sun_offset_minutes=10,
                       every_n_days=2, start_date="2026-11-02")
    for d in (2, 3, 4):
        day = date(2026, 11, d)
        when = oracle("caesarea", "sunset", day, 10)
        for mm in (0, 2, 4, 6):
            await fire(hass, when + timedelta(minutes=mm))
    assert statuses(hass, entry, cid).count("cycle_completed") == 2


# ---------------------------------------------------------------- services

async def test_add_and_update_sun_schedule(hass: HomeAssistant):
    await at_place(hass, "caesarea")
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    sched = await add_schedule(hass, valve_entity_id=Z1, time_mode="sunrise", sun_offset_minutes=-45,
                               days=["mon"], duration_minutes=5)
    assert (sched["time_mode"], sched["sun_offset_min"], sched["time_hhmm"]) == ("sunrise", -45, "06:00")

    sched = await update_schedule(hass, schedule_id=sched["id"], sun_offset_minutes=20)
    assert (sched["time_mode"], sched["sun_offset_min"]) == ("sunrise", 20)
    sched = await update_schedule(hass, schedule_id=sched["id"], time_mode="sunset")
    assert (sched["time_mode"], sched["sun_offset_min"]) == ("sunset", 20)
    # A clock time alone switches back to a clock time and drops the offset.
    sched = await update_schedule(hass, schedule_id=sched["id"], time="05:15")
    assert (sched["time_mode"], sched["sun_offset_min"], sched["time_hhmm"]) == ("clock", 0, "05:15")
    sched = await update_schedule(hass, schedule_id=sched["id"], time_mode="sunrise")
    assert (sched["time_mode"], sched["sun_offset_min"], sched["time_hhmm"]) == ("sunrise", 0, "05:15")

    clock = await add_schedule(hass, valve_entity_id=Z1, time="07:00", days=["tue"], duration_minutes=5)
    assert (clock["time_mode"], clock["sun_offset_min"]) == ("clock", 0)


async def test_sun_schedule_validation(hass: HomeAssistant):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    with pytest.raises(HomeAssistantError, match="time is required"):
        await add_schedule(hass, valve_entity_id=Z1, days=["mon"], duration_minutes=5)
    with pytest.raises(HomeAssistantError, match="sun_offset_minutes only applies"):
        await add_schedule(hass, valve_entity_id=Z1, time="06:00", sun_offset_minutes=10, days=["mon"])
    with pytest.raises(vol.Invalid):
        await add_schedule(hass, valve_entity_id=Z1, time_mode="sunrise", sun_offset_minutes=181, days=["mon"])
    with pytest.raises(vol.Invalid):
        await add_schedule(hass, valve_entity_id=Z1, time_mode="dawn", days=["mon"])
    clock = await add_schedule(hass, valve_entity_id=Z1, time="06:00", days=["mon"], duration_minutes=5)
    with pytest.raises(HomeAssistantError, match="sun_offset_minutes only applies"):
        await update_schedule(hass, schedule_id=clock["id"], sun_offset_minutes=5)


# ---------------------------------------------------------------- next run, sensor, calendar, preview

async def test_next_run_sensor_calendar_and_preview(hass: HomeAssistant, hass_ws_client):
    zone = await at_place(hass, "caesarea")
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    sched = await add_schedule(hass, valve_entity_id=Z1, time_mode="sunset", sun_offset_minutes=-15,
                               days=["mon", "tue", "wed", "thu", "fri", "sat", "sun"], duration_minutes=7)
    now = dt_util.now()
    expected = planner.next_fire(sched, now, hass=hass)
    assert expected is not None
    today = now.astimezone(zone).date()
    assert expected in (oracle("caesarea", "sunset", today, -15), oracle("caesarea", "sunset", today + timedelta(days=1), -15))

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/get_state"})
    result = (await client.receive_json())["result"]
    assert result["valves"][0]["next_run"]["fires_at"] == int(expected.timestamp())
    assert result["schedules"][0]["time_mode"] == "sunset"
    week = [o for o in result["week"] if o["schedule_id"] == sched["id"]]
    assert week and all(datetime.fromtimestamp(o["start"], zone).strftime("%H:%M")
                        == oracle("caesarea", "sunset", date.fromisoformat(o["day"]), -15).strftime("%H:%M") for o in week)

    await async_update_entity(hass, "sensor.schedule_wizard_next_schedule")
    state = hass.states.get("sensor.schedule_wizard_next_schedule")
    assert state.attributes["schedule_id"] == sched["id"]

    await async_update_entity(hass, "calendar.schedule_wizard_watering_schedule")
    cal = hass.states.get("calendar.schedule_wizard_watering_schedule")
    assert cal.attributes["start_time"] == expected.strftime("%Y-%m-%d %H:%M:%S")

    await client.send_json({"id": 2, "type": f"{DOMAIN}/preview_schedule", "time_mode": "sunset",
                            "sun_offset_minutes": -15, "days_mask": 127, "count": 3})
    preview = (await client.receive_json())["result"]["next"]
    assert len(preview) == 3
    assert preview[0] == int(expected.timestamp())
    assert preview[1] - preview[0] in range(23 * 3600, 25 * 3600)

    await client.send_json({"id": 3, "type": f"{DOMAIN}/preview_schedule", "time_mode": "sunrise",
                            "sun_offset_minutes": 500})
    assert not (await client.receive_json())["success"]
