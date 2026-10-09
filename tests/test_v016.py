"""v0.16.0: one-off run changes, boost, max zones at once, overlaps, weather tips and the evening digest."""
from __future__ import annotations

from datetime import timedelta

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.schedule_wizard import planner
from custom_components.schedule_wizard.const import DOMAIN

from .conftest import advance, data, is_on, settle, setup_wizard
from .test_scheduler import Z1, Z2, _schedule_now, add_cycle, add_valve, statuses

pytestmark = pytest.mark.usefixtures("zones", "fixed_clock")

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


async def add_schedule(hass, **fields) -> dict:
    resp = await hass.services.async_call(DOMAIN, "add_schedule", fields, blocking=True, return_response=True)
    return resp["schedule"]


async def fire(hass, when) -> None:
    async_fire_time_changed(hass, when)
    await settle(hass)


def active(hass, entry) -> dict:
    return data(hass, entry)["scheduler"].active


# ---------------------------------------------------------------- boost

async def test_boost_scales_a_scheduled_run(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call(DOMAIN, "set_boost", {"percent": 30, "days": 1}, blocking=True)
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=10)
    await fire(hass, fire_at)
    run = active(hass, entry)[Z1]
    assert run["duration_min"] == 13
    assert "|boost:130%" in run["note"]
    await hass.services.async_call(DOMAIN, "clear_boost", {}, blocking=True)
    assert data(hass, entry)["store"].boost == {}


async def test_boost_does_not_change_water_now(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await hass.services.async_call(DOMAIN, "set_boost", {"percent": 50, "days": 2}, blocking=True)
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 10}, blocking=True)
    assert active(hass, entry)[Z1]["duration_min"] == 10


async def test_boost_rejects_odd_percent(hass: HomeAssistant):
    await setup_wizard(hass)
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "set_boost", {"percent": 33}, blocking=True)


async def test_boost_scales_a_plan(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morning", [(Z1, 10), (Z2, 10)])
    await hass.services.async_call(DOMAIN, "set_boost", {"percent": -50, "days": 1}, blocking=True)
    fire_at = await _schedule_now(hass, cycle_id=cid)
    await fire(hass, fire_at)
    assert active(hass, entry)[Z1]["duration_min"] == 5


# ---------------------------------------------------------------- one-off change of a run

async def test_override_moves_the_run_and_scales_it(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    now = dt_util.now().replace(second=0, microsecond=0)
    original = now + timedelta(minutes=10)
    moved = now + timedelta(minutes=2)
    sched = await add_schedule(hass, valve_entity_id=Z1, time=original.strftime("%H:%M"),
                               days=[DAYS[now.weekday()]], duration_minutes=10)
    await hass.services.async_call(DOMAIN, "set_override", {
        "schedule_id": sched["id"], "date": now.date().isoformat(), "time": moved.strftime("%H:%M"), "percent": 50,
    }, blocking=True)
    store = data(hass, entry)["store"]
    week = planner.occurrences(store, data(hass, entry)["options"], dt_util.start_of_local_day(),
                               dt_util.start_of_local_day() + timedelta(days=1))
    occ = next(o for o in week if o["schedule_id"] == sched["id"])
    assert occ["start"] == int(moved.timestamp())
    assert occ["minutes"] == 5 and occ["base_minutes"] == 10
    assert occ["override"] == {"time": moved.strftime("%H:%M"), "pct": 50}

    await fire(hass, moved)
    assert is_on(hass, Z1)
    assert active(hass, entry)[Z1]["duration_min"] == 5
    assert "|once:50%@" in active(hass, entry)[Z1]["note"]
    await advance(hass, 5 * 60 + 5)
    assert not is_on(hass, Z1)
    await fire(hass, original)
    assert not is_on(hass, Z1), "the original time must not fire after the run was moved"
    assert statuses(hass, entry, Z1).count("started") <= 1


async def test_override_checks(hass: HomeAssistant):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    now = dt_util.now()
    sched = await add_schedule(hass, valve_entity_id=Z1, time="23:50", days=[DAYS[now.weekday()]], duration_minutes=5)
    yesterday = (now.date() - timedelta(days=1)).isoformat()
    tomorrow = (now.date() + timedelta(days=1)).isoformat()
    with pytest.raises(HomeAssistantError, match="passed"):
        await hass.services.async_call(DOMAIN, "set_override", {"schedule_id": sched["id"], "date": yesterday}, blocking=True)
    with pytest.raises(HomeAssistantError, match="no run"):
        await hass.services.async_call(DOMAIN, "set_override", {"schedule_id": sched["id"], "date": tomorrow, "percent": 50}, blocking=True)
    earlier = (now - timedelta(minutes=5)).strftime("%H:%M")
    with pytest.raises(HomeAssistantError, match="already passed"):
        await hass.services.async_call(DOMAIN, "set_override", {
            "schedule_id": sched["id"], "date": now.date().isoformat(), "time": earlier,
        }, blocking=True)
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "set_override", {
            "schedule_id": sched["id"], "date": now.date().isoformat(), "percent": 10,
        }, blocking=True)


async def test_override_cleared_and_removed_with_schedule(hass: HomeAssistant):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    now = dt_util.now()
    sched = await add_schedule(hass, valve_entity_id=Z1, time="23:50", days=DAYS, duration_minutes=5)
    day = now.date().isoformat()
    await hass.services.async_call(DOMAIN, "set_override", {"schedule_id": sched["id"], "date": day, "percent": 150}, blocking=True)
    store = data(hass, entry)["store"]
    assert store.get_override(sched["id"], day) == {"time": "", "pct": 150}
    await hass.services.async_call(DOMAIN, "clear_override", {"schedule_id": sched["id"], "date": day}, blocking=True)
    assert store.get_override(sched["id"], day) is None
    await hass.services.async_call(DOMAIN, "set_override", {"schedule_id": sched["id"], "date": day, "percent": 150}, blocking=True)
    await hass.services.async_call(DOMAIN, "remove_schedule", {"schedule_id": sched["id"]}, blocking=True)
    assert store.overrides == {}


# ---------------------------------------------------------------- max zones at once

async def test_second_zone_waits_its_turn(hass: HomeAssistant):
    entry = await setup_wizard(hass, {"max_zones_at_once": 1})
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=2)
    await add_schedule(hass, valve_entity_id=Z2, time=fire_at.strftime("%H:%M"), days=[DAYS[fire_at.weekday()]], duration_minutes=2)
    await fire(hass, fire_at)
    sched = data(hass, entry)["scheduler"]
    assert is_on(hass, Z1) != is_on(hass, Z2), "only one zone may water at a time"
    assert len(sched.queue) == 1
    first, second = (Z1, Z2) if is_on(hass, Z1) else (Z2, Z1)
    await advance(hass, 2 * 60 + 1)
    await advance(hass, 6)
    assert not is_on(hass, first)
    assert is_on(hass, second)
    assert sched.queue == []


async def test_no_limit_runs_both(hass: HomeAssistant):
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=2)
    await add_schedule(hass, valve_entity_id=Z2, time=fire_at.strftime("%H:%M"), days=[DAYS[fire_at.weekday()]], duration_minutes=2)
    await fire(hass, fire_at)
    assert is_on(hass, Z1) and is_on(hass, Z2)


# ---------------------------------------------------------------- overlaps

async def test_week_marks_overlaps_and_draft_check(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Lawn", [(Z1, 15), (Z2, 20)])
    plan = await add_schedule(hass, cycle_id=cid, time="06:00", days=DAYS)
    herbs = await add_schedule(hass, valve_entity_id=Z2, time="06:05", days=["sun"], duration_minutes=10)
    store, options = data(hass, entry)["store"], data(hass, entry)["options"]
    week = planner.mark_overlaps(planner.occurrences(
        store, options, dt_util.start_of_local_day(), dt_util.start_of_local_day() + timedelta(days=7)))
    clash = [r for r in week if r["schedule_id"] == herbs["id"]]
    assert clash and clash[0]["overlaps"][0]["schedule_id"] == plan["id"]
    lone = [r for r in week if r["schedule_id"] == plan["id"] and DAYS[dt_util.as_local(dt_util.utc_from_timestamp(r["start"])).weekday()] != "sun"]
    assert all(not r["overlaps"] for r in lone)

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/check_conflicts", "time": "06:10", "days_mask": 1,
                            "valve_entity_id": Z1, "minutes": 10})
    res = (await client.receive_json())["result"]
    assert [c["schedule_id"] for c in res["conflicts"]] == [plan["id"]]
    assert res["suggestion"] == "06:35"
    await client.send_json({"id": 2, "type": f"{DOMAIN}/check_conflicts", "time": "07:00", "days_mask": 1,
                            "valve_entity_id": Z1, "minutes": 10})
    assert (await client.receive_json())["result"]["conflicts"] == []
    # Editing the plan's own time never clashes with itself.
    await client.send_json({"id": 3, "type": f"{DOMAIN}/check_conflicts", "time": "06:00", "days_mask": 2,
                            "cycle_id": cid, "schedule_id": plan["id"]})
    assert (await client.receive_json())["result"]["conflicts"] == []


# ---------------------------------------------------------------- weather tips

class FakeWeather:
    """weather.get_forecasts with a daily forecast the test sets per offset from today."""

    def __init__(self, hass: HomeAssistant, entity_id: str = "weather.home"):
        self.entity_id = entity_id
        self.days: dict[int, dict] = {}
        hass.states.async_set(entity_id, "sunny", {"temperature_unit": "°C", "precipitation_unit": "mm"})

        async def _get(call: ServiceCall):
            today = dt_util.start_of_local_day()
            items = [{"datetime": (today + timedelta(days=o, hours=12)).isoformat(), **v} for o, v in sorted(self.days.items())]
            return {self.entity_id: {"forecast": items}}

        hass.services.async_register("weather", "get_forecasts", _get, supports_response=SupportsResponse.ONLY)


async def _tips_setup(hass, **options):
    weather = FakeWeather(hass)
    entry = await setup_wizard(hass, options)
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back", rain_exempt=True)
    await add_schedule(hass, valve_entity_id=Z1, time="06:00", days=DAYS, duration_minutes=10, name="Lawn")
    await add_schedule(hass, valve_entity_id=Z2, time="07:00", days=DAYS, duration_minutes=5, name="Pots")
    return entry, weather


def tomorrow() -> str:
    return (dt_util.now().date() + timedelta(days=1)).isoformat()


async def test_tips_from_the_forecast(hass: HomeAssistant):
    entry, weather = await _tips_setup(hass)
    weather.days[1] = {"temperature": 36, "templow": 1, "precipitation": 8, "precipitation_probability": 80}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    tips = {t["kind"]: t for t in sched.tips()}
    assert set(tips) == {"rain", "heat", "frost"}
    assert all(t["day"] == tomorrow() and not t["today"] for t in tips.values())
    # Rain and frost leave the indoor zone alone; heat counts every run of the day.
    assert [r["name"] for r in tips["rain"]["runs"]] == ["Front"]
    assert [r["name"] for r in tips["frost"]["runs"]] == ["Front"]
    assert len(tips["heat"]["runs"]) == 2 and tips["heat"]["pct"] == 30

    await hass.services.async_call(DOMAIN, "apply_tip", {"tip_id": f"rain:{tomorrow()}"}, blocking=True)
    store = data(hass, entry)["store"]
    lawn = next(s for s in store.schedules if s["name"] == "Lawn")
    assert store.is_skipped(lawn["id"], tomorrow())
    assert "rain" not in {t["kind"] for t in sched.tips()}

    await hass.services.async_call(DOMAIN, "apply_tip", {"tip_id": f"heat:{tomorrow()}"}, blocking=True)
    boost = store.boost
    assert boost["pct"] == 30
    start = dt_util.start_of_local_day(dt_util.now().date() + timedelta(days=1))
    assert boost["from"] == int(start.timestamp()) and boost["until"] == int((start + timedelta(days=1)).timestamp())
    assert "heat" not in {t["kind"] for t in sched.tips()}


async def test_tips_dismiss_mute_and_limits(hass: HomeAssistant):
    entry, weather = await _tips_setup(hass)
    weather.days[1] = {"temperature": 20, "templow": 1, "precipitation": 2, "precipitation_probability": 90}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    assert {t["kind"] for t in sched.tips()} == {"frost"}, "2 mm is under the 5 mm rain setting"
    await hass.services.async_call(DOMAIN, "dismiss_tip", {"tip_id": f"frost:{tomorrow()}"}, blocking=True)
    assert sched.tips() == []

    weather.days[1] = {"temperature": 40, "templow": 15, "precipitation": 20, "precipitation_probability": 30}
    await sched._async_refresh_daily()
    assert {t["kind"] for t in sched.tips()} == {"heat"}, "30 % chance is under the 60 % setting"
    await hass.services.async_call(DOMAIN, "mute_tip", {"kind": "heat"}, blocking=True)
    assert sched.tips() == []
    await hass.services.async_call(DOMAIN, "mute_tip", {"kind": "heat", "muted": False}, blocking=True)
    assert {t["kind"] for t in sched.tips()} == {"heat"}
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "apply_tip", {"tip_id": "wind:2026-01-01"}, blocking=True)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(DOMAIN, "apply_tip", {"tip_id": "rain:2020-01-01"}, blocking=True)


async def test_no_rain_tip_while_the_forecast_skip_is_on(hass: HomeAssistant):
    entry, weather = await _tips_setup(hass, forecast_entity="weather.home", forecast_skip_mm=3)
    weather.days[1] = {"temperature": 20, "templow": 10, "precipitation": 12, "precipitation_probability": 90}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    assert sched.tips() == []


async def test_fahrenheit_forecast_is_converted(hass: HomeAssistant):
    entry, weather = await _tips_setup(hass)
    hass.states.async_set("weather.home", "sunny", {"temperature_unit": "°F", "precipitation_unit": "in"})
    weather.days[1] = {"temperature": 100, "templow": 50, "precipitation": 0.5}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    day = sched.weather_days["days"][tomorrow()]
    assert day["max_c"] == pytest.approx(37.8, abs=0.1)
    assert day["mm"] == pytest.approx(12.7, abs=0.1)
    assert {t["kind"] for t in sched.tips()} == {"heat", "rain"}


async def test_tips_off(hass: HomeAssistant):
    entry, weather = await _tips_setup(hass, tips_enabled=False)
    weather.days[1] = {"temperature": 40, "templow": 0, "precipitation": 20}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    assert sched.tips() == []


# ---------------------------------------------------------------- evening digest

async def test_digest_actions_and_follow_up(hass: HomeAssistant):
    calls: list[ServiceCall] = []

    async def _notify(call: ServiceCall):
        calls.append(call)

    hass.services.async_register("notify", "mobile_app_phone", _notify)
    entry, weather = await _tips_setup(hass, notify_targets=["mobile_app_phone"], notify_events=["tips"])
    weather.days[1] = {"temperature": 20, "templow": 12, "precipitation": 9, "precipitation_probability": 90}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    day = tomorrow()
    await sched._async_send_digest(day)
    await settle(hass)
    assert len(calls) == 1
    sent = calls[0].data
    assert "9" in sent["message"] and sent["data"]["tag"] == f"schedule_wizard_tips_{day}"
    actions = [a["action"] for a in sent["data"]["actions"]]
    assert actions == [f"SCHEDULE_WIZARD_TIP_RAIN_{day.replace('-', '')}"]

    await sched._async_send_digest(day)
    await settle(hass)
    assert len(calls) == 1, "one digest per day"

    # A forged or malformed action changes nothing.
    hass.bus.async_fire("mobile_app_notification_action", {"action": "SCHEDULE_WIZARD_TIP_RAIN_2026"})
    hass.bus.async_fire("mobile_app_notification_action", {"action": "SCHEDULE_WIZARD_TIP_WIND_" + day.replace("-", "")})
    await settle(hass)
    store = data(hass, entry)["store"]
    lawn = next(s for s in store.schedules if s["name"] == "Lawn")
    assert not store.is_skipped(lawn["id"], day)

    hass.bus.async_fire("mobile_app_notification_action", {"action": actions[0]})
    await settle(hass)
    assert store.is_skipped(lawn["id"], day)

    # The tip is gone (acted on): the sent notification is cleared.
    await sched._async_refresh_daily()
    await settle(hass)
    assert calls[-1].data["message"] == "clear_notification"
    assert calls[-1].data["data"]["tag"] == f"schedule_wizard_tips_{day}"


async def test_digest_needs_the_tips_event(hass: HomeAssistant):
    calls: list[ServiceCall] = []

    async def _notify(call: ServiceCall):
        calls.append(call)

    hass.services.async_register("notify", "mobile_app_phone", _notify)
    entry, weather = await _tips_setup(hass, notify_targets=["mobile_app_phone"], notify_events=["valve_start"])
    weather.days[1] = {"temperature": 20, "templow": 12, "precipitation": 9}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    await sched._async_send_digest(tomorrow())
    await settle(hass)
    assert calls == []


async def test_daily_forecast_retried_soon_after_an_empty_answer(hass: HomeAssistant):
    """Weather entities load after this integration at startup: an empty forecast is fetched again in 2 min."""
    entry, weather = await _tips_setup(hass)
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    assert sched.weather_days["days"] == {}
    weather.days[1] = {"temperature": 36, "templow": 15, "precipitation": 0}
    await advance(hass, 125)
    assert tomorrow() in sched.weather_days["days"]


async def test_stored_tip_and_override_dates_are_bounded(hass: HomeAssistant):
    """Any signed-in user can call these services: far-off dates must not grow the stored data."""
    await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    sched = await add_schedule(hass, valve_entity_id=Z1, time="23:50", days=DAYS, duration_minutes=5)
    far = (dt_util.now().date() + timedelta(days=200)).isoformat()
    with pytest.raises(HomeAssistantError, match="within"):
        await hass.services.async_call(DOMAIN, "set_override", {"schedule_id": sched["id"], "date": far, "percent": 50}, blocking=True)
    with pytest.raises(HomeAssistantError, match="no such tip"):
        await hass.services.async_call(DOMAIN, "dismiss_tip", {"tip_id": f"rain:{far}"}, blocking=True)


# ---------------------------------------------------------------- QA cycle 2026-10-09 regressions

async def test_heat_tip_without_a_current_tip_changes_nothing(hass: HomeAssistant):
    """SEC-011 / BUG-041: a forged heat tip (service or notification action) must not replace the boost."""
    entry, weather = await _tips_setup(hass)
    weather.days[1] = {"temperature": 20, "templow": 12, "precipitation": 0}
    sched = data(hass, entry)["scheduler"]
    await sched._async_refresh_daily()
    await hass.services.async_call(DOMAIN, "set_boost", {"percent": 50, "days": 3}, blocking=True)
    before = data(hass, entry)["store"].boost
    later = (dt_util.now().date() + timedelta(days=20)).isoformat()
    with pytest.raises(HomeAssistantError, match="nothing to change"):
        await hass.services.async_call(DOMAIN, "apply_tip", {"tip_id": f"heat:{later}"}, blocking=True)
    hass.bus.async_fire("mobile_app_notification_action", {"action": "SCHEDULE_WIZARD_TIP_HEAT_" + later.replace("-", "")})
    await settle(hass)
    assert data(hass, entry)["store"].boost == before
    with pytest.raises(HomeAssistantError, match="within"):
        await hass.services.async_call(DOMAIN, "set_boost", {"percent": 50, "start_date": "9999-12-31"}, blocking=True)


async def test_no_second_watering_by_moving_todays_finished_run(hass: HomeAssistant):
    """BUG-042: today's run already started at its time; moving it later would water twice."""
    entry = await setup_wizard(hass)
    await add_valve(hass, Z1, "Front")
    now = dt_util.now()
    earlier = now - timedelta(minutes=5)
    sched = await add_schedule(hass, valve_entity_id=Z1, time=earlier.strftime("%H:%M"),
                               days=[DAYS[now.weekday()]], duration_minutes=1)
    later = (now + timedelta(minutes=30)).strftime("%H:%M")
    with pytest.raises(HomeAssistantError, match="already started"):
        await hass.services.async_call(DOMAIN, "set_override", {
            "schedule_id": sched["id"], "date": now.date().isoformat(), "time": later,
        }, blocking=True)
    assert data(hass, entry)["store"].overrides == {}


async def test_waiting_run_survives_a_reload(hass: HomeAssistant):
    """BUG-043: a run waiting for a free slot waits again after a restart / reload and then waters."""
    entry = await setup_wizard(hass, {"max_zones_at_once": 1})
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    fire_at = await _schedule_now(hass, valve_entity_id=Z1, duration_minutes=2)
    await add_schedule(hass, valve_entity_id=Z2, time=fire_at.strftime("%H:%M"), days=[DAYS[fire_at.weekday()]], duration_minutes=2)
    await fire(hass, fire_at)
    waiting = Z2 if is_on(hass, Z1) else Z1
    assert [q["target"] for q in data(hass, entry)["store"].queue] == [waiting]

    assert await hass.config_entries.async_reload(entry.entry_id)
    await settle(hass)
    assert [q["target"] for q in data(hass, entry)["scheduler"].queue] == [waiting]
    assert not is_on(hass, waiting)
    await advance(hass, 2 * 60 + 1)
    await advance(hass, 6)
    assert is_on(hass, waiting)
    assert data(hass, entry)["store"].queue == []


def test_panel_fixes_in_source():
    """BUG-039, BUG-040, UX-021: focus kept after Move to, overlap not by colour only, isolated units."""
    from pathlib import Path

    src = (Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www" / "panel.js").read_text(encoding="utf-8")
    assert "timeInput.focus();" in src and "sched.conflict_moved" in src
    assert r'(x.clash ? "\u26a0\ufe0e " : "")' in src
    assert "return lri(this._isF()" in src and "return fsi(l < 999.5" in src
