"""v0.15.0 final batch: #66 (rain check line per source type), #67 (Last watering), #91 (own sensors are no rain
source), #92 (First run time format), #93 (no runs before a schedule existed), #94 (each zone's own start in a
plan), #95 (card "in N d" rounding), #96 (Delete zone).

Backend parts run in Home Assistant; panel and card helpers run under Node (skipped without Node).
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.schedule_wizard import planner
from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, setup_wizard
from .test_i18n import STRINGS
from .test_v015_ux import CARD, PANEL, WWW, _function, _method, _node, _state, needs_node

pytestmark = pytest.mark.usefixtures("fixed_clock", "zones")

Z1, Z2, Z3 = "input_boolean.zone1", "input_boolean.zone2", "input_boolean.zone3"
I18N_URI = json.dumps((WWW / "i18n.js").as_uri())


# ---------------------------------------------------------------- #66: the check line says the rule in use


@needs_node
def test_rain_check_line_follows_the_source_type():
    """A binary sensor skips while "on", whatever the weather states list holds (the server's rule)."""
    script = (
        f"const I = await import({I18N_URI});"
        "const t = I.makeT('en');"
        "const ltr = (x) => String(x);"
        + _function(PANEL, "rainRules").replace("DEFAULT_RAIN_STATES", '"rainy,pouring,snowy,lightning-rainy"')
        + _function(PANEL, "rainCheckParts")
        + "const line = (st, r) => rainCheckParts(st, r, (k, v) => I.tnodes(t(k), v), t).join('');"
        "const dflt = rainRules(undefined, '', '');"
        "process.stdout.write(JSON.stringify(["
        " line({ entity_id: 'binary_sensor.rain', state: 'off' }, dflt),"
        " line({ entity_id: 'binary_sensor.rain', state: 'on' }, rainRules(undefined, '', '2')),"
        " line({ entity_id: 'weather.home', state: 'rainy' }, dflt),"
        " line({ entity_id: 'sensor.rain_today', state: '0.4' }, dflt),"
        " line({ entity_id: 'sensor.rain_today', state: '0.4' }, rainRules(undefined, '', '2')),"
        " line({ entity_id: 'weather.home', state: 'sunny', attributes: { precipitation: 3 } }, rainRules(undefined, 'precipitation', '2')),"
        " line({ entity_id: 'weather.home', state: 'sunny' }, rainRules(undefined, '', '2')),"
        "]));"
    )
    assert json.loads(_node(script)) == [
        "Skips while the sensor is on. Now: off.",
        "Skips while the sensor is on. Now: on.",
        "Skips when the state is rainy, pouring, snowy, lightning-rainy. Now: rainy.",
        "Skips when the state is rainy, pouring, snowy, lightning-rainy. Now: 0.4. "
        + STRINGS["en"]["set.rain_check_numeric"],
        "Skips at 2 or more. Now: 0.4.",
        "Skips at 2 or more. Now: 3.",
        # A word is never compared with the threshold (server: float() fails, the states list decides).
        "Skips when the state is rainy, pouring, snowy, lightning-rainy. Now: sunny.",
    ]
    assert "rainCheckParts(st, r," in _method(PANEL, "_rainPicker")


# ---------------------------------------------------------------- #67: the last real watering, said once


def _last_line(now: int, history: list[dict]) -> str:
    fns = {name: _method(PANEL, name) for name in ("_lastWateringLine", "_wateredTotal", "_watered", "_relWhen")}
    args = {"_relWhen": "ts", "_wateredTotal": "rows", "_watered": "h", "_lastWateringLine": ""}
    script = (
        f"const I = await import({I18N_URI});"
        "globalThis.I18N = I;"
        "globalThis.el = (tag, attrs, text) => text;"
        "globalThis.isSkipStatus = (s) => String(s || '').startsWith('skipped_');"
        "globalThis.dayNum = (key) => Math.round(Date.UTC(...key.split('-').map((x, i) => i === 1 ? x - 1 : +x)) / 86400000);"
        "const hass = { config: { time_zone: 'UTC' }, locale: { language: 'en', time_zone: 'server' } };"
        "const self = { _t: I.makeT('en'), _hass: hass, _lang: 'en', _isPlanId: (id) => !String(id).includes('.'),"
        " _fmtTime: (ts) => I.fmtTime(ts, 'en', { hass, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }),"
        " _fmtDate: () => 'Mon', _statusLabel: (s) => I.makeT('en')('status.' + s) };"
        + "".join(f"self.{n} = new Function({args[n]!r}, {json.dumps(b)}).bind(self);" for n, b in fns.items())
        + f"self._state = {{ now: {now}, history: {json.dumps(history)} }};"
        "process.stdout.write(JSON.stringify(self._lastWateringLine()));"
    )
    return json.loads(_node(script))


D = 1781078400  # 2026-06-10 08:00 UTC


@needs_node
def test_last_watering_is_the_last_real_one():
    """Verifier's case: a 12:55 start was cancelled before watering; the only watering ended 17:54; rain at 17:58."""
    history = [
        {"valve_entity_id": "z.f", "status": "skipped_rain", "ts": D + 9 * 3600 + 58 * 60, "duration_min": 1},
        {"valve_entity_id": "z.f", "status": "cancelled", "ts": D + 9 * 3600 + 57 * 60, "duration_min": 0},
        {"valve_entity_id": "z.f", "status": "started", "ts": D + 9 * 3600 + 56 * 60, "duration_min": 10},
        {"valve_entity_id": "z.h", "status": "completed", "ts": D + 9 * 3600 + 54 * 60, "duration_min": 1},
        {"valve_entity_id": "z.h", "status": "started", "ts": D + 9 * 3600 + 53 * 60, "duration_min": 1},
        {"valve_entity_id": "z.f", "status": "cancelled", "ts": D + 4 * 3600 + 56 * 60, "duration_min": 0},
        {"valve_entity_id": "z.f", "status": "started", "ts": D + 4 * 3600 + 55 * 60, "duration_min": 10},
    ]
    assert _last_line(D + 10 * 3600, history) == "Last watering: today 17:54, 1 zone · 1 min · Skipped (rain), today 17:58"


@needs_node
def test_last_watering_counts_a_stopped_run_that_watered():
    """Water now at 07:00 stopped after 3 min, then a plan run replaced after 4 min: both watered; 0 min did not."""
    history = [
        {"valve_entity_id": "z.b", "status": "superseded", "ts": D + 3600, "duration_min": 0, "planned_min": 10},
        {"valve_entity_id": "z.a", "status": "superseded", "ts": D + 1800, "duration_min": 4, "planned_min": 10},
        {"valve_entity_id": "z.a", "status": "cancelled", "ts": D - 3600 + 180, "duration_min": 3, "planned_min": 10},
        {"valve_entity_id": "plan1", "status": "cycle_cancelled", "ts": D + 3700, "duration_min": 0},
    ]
    assert _last_line(D + 7200, history) == "Last watering: today 08:30, 1 zone · 7 min"


# ---------------------------------------------------------------- #91: own sensors are no rain source


async def test_own_entities_are_no_rain_source(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    await hass.async_block_till_done()
    own = {e.entity_id for e in er.async_get(hass).entities.values() if e.platform == DOMAIN}
    own_sensors = sorted(e for e in own if e.split(".")[0] in ("sensor", "binary_sensor") and hass.states.get(e))
    assert own_sensors, "the integration should have created sensors"
    state = await _state(hass, hass_ws_client)
    assert set(own_sensors) <= set(state["own_entities"])

    client = await hass_ws_client(hass)

    async def save(value):
        await client.send_json_auto_id({"type": f"{DOMAIN}/update_options", "rain_entity": value})
        return await client.receive_json()

    for entity_id in own_sensors:
        msg = await save(entity_id)
        assert not msg["success"], entity_id
        assert "rain_entity" in msg["error"]["message"] and "Schedule Wizard" in msg["error"]["message"]
    assert not entry.options.get("rain_entity")
    hass.states.async_set("binary_sensor.rain", "off")
    assert (await save("binary_sensor.rain"))["success"], "a foreign rain sensor still saves"

    # An own sensor saved before 0.15.0 is kept: saving it unchanged is allowed.
    hass.config_entries.async_update_entry(entry, options={**entry.options, "rain_entity": own_sensors[0]})
    assert (await save(own_sensors[0]))["success"]

    picker = _method(PANEL, "_rainPicker")
    assert "this._state.own_entities" in picker and "!own.has(id) || id === cur" in picker


# ---------------------------------------------------------------- #92: First run in the page's time format


@needs_node
def test_first_run_time_uses_the_page_formatter():
    body = _method(PANEL, "_fmtClock")
    script = (
        f"const I = await import({I18N_URI});"
        "const make = (lang, tf) => { const hass = { locale: { language: lang, time_format: tf }, config: { time_zone: 'Asia/Jerusalem' } };"
        " const self = { _fmtTime: (ts, o) => I.fmtTime(ts, lang, Object.assign({ hass }, o)) };"
        f" return new Function('hhmm', {json.dumps(body)}).bind(self); }};"
        "process.stdout.write(JSON.stringify([make('en', '12')('06:00'), make('en', '12')('18:05'), make('de', '24')('06:00')]));"
    )
    # Intl puts a narrow no-break space before AM / PM.
    assert [x.replace(chr(0x202F), " ") for x in json.loads(_node(script))] == ["6:00 AM", "6:05 PM", "6:00"]  # de: same as every other time on its page
    first = _method(PANEL, "_firstRunNodes")
    assert "this._fmtClock(hhmm)" in first and "ltr(hhmm)" not in first


# ---------------------------------------------------------------- #93: no runs before the schedule existed


async def test_week_has_no_run_from_before_the_schedule(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    now = dt_util.now()
    assert now.hour >= 2, "fixed_clock is 10:00 local"
    earlier = (now - timedelta(hours=2)).strftime("%H:%M")
    resp = await hass.services.async_call(DOMAIN, "add_schedule", {
        "valve_entity_id": Z1, "time": earlier, "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "duration_minutes": 10,
    }, blocking=True, return_response=True)
    sid = resp["schedule"]["id"]
    today = now.date().isoformat()

    week = [o for o in (await _state(hass, hass_ws_client))["week"] if o["schedule_id"] == sid]
    assert week and today not in [o["day"] for o in week], "created at 10:00: the 08:00 run today never happened"
    assert week[0]["day"] == (now.date() + timedelta(days=1)).isoformat()
    # The calendar entity reads the same occurrences.
    occs = planner.occurrences(data(hass, entry)["store"], {}, dt_util.start_of_local_day(),
                               dt_util.start_of_local_day() + timedelta(days=2), limit=None)
    assert today not in [o["day"] for o in occs if o["schedule_id"] == sid]

    # A schedule that existed this morning keeps its past run in the week.
    data(hass, entry)["store"].get_schedule(sid)["created_at"] = int((now - timedelta(days=1)).timestamp())
    week = [o for o in (await _state(hass, hass_ws_client))["week"] if o["schedule_id"] == sid]
    assert week[0]["day"] == today


# ---------------------------------------------------------------- #94: each zone's own start in a plan


async def _plan(hass, steps) -> str:
    for e in {e for e, _ in steps}:
        await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": e, "label": e[-5:]}, blocking=True)
    resp = await hass.services.async_call(DOMAIN, "add_cycle", {
        "name": "Morning", "steps": [{"entity_id": e, "duration_minutes": m} for e, m in steps],
    }, blocking=True, return_response=True)
    cid = resp["cycle"]["id"]
    await hass.services.async_call(DOMAIN, "add_schedule", {
        "cycle_id": cid, "time": "06:00", "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
    }, blocking=True, return_response=True)
    return cid


async def test_zone_cards_show_each_zones_own_start(hass: HomeAssistant, hass_ws_client):
    """One at a time: Front 06:00, Herbs 06:10, Back 06:25 (the real order and lengths)."""
    await setup_wizard(hass)
    await _plan(hass, [(Z1, 10), (Z2, 15), (Z3, 5)])
    valves = {v["entity_id"]: v["next_run"] for v in (await _state(hass, hass_ws_client))["valves"]}
    start = valves[Z1]["plan_starts_at"]
    assert dt_util.as_local(dt_util.utc_from_timestamp(start)).strftime("%H:%M") == "06:00"
    assert [valves[z]["fires_at"] - start for z in (Z1, Z2, Z3)] == [0, 600, 1500]
    assert [valves[z]["duration_min"] for z in (Z1, Z2, Z3)] == [10, 15, 5]
    assert valves[Z2]["in_seconds"] - valves[Z1]["in_seconds"] in (599, 600, 601)


async def test_zone_start_follows_cycle_and_soak(hass: HomeAssistant):
    """Soak 5 min on / 10 min off on Front: interleaved, Herbs waters during Front's soak; sequential, after it."""
    entry = await setup_wizard(hass)
    cid = await _plan(hass, [(Z1, 10), (Z2, 10)])
    store = data(hass, entry)["store"]
    scheduler = data(hass, entry)["scheduler"]
    store.get_valve(Z1).update(soak_run_min=5, soak_pause_min=10)
    assert scheduler.zone_start_offsets(cid) == {Z1: 0, Z2: 300}
    scheduler.options["interleave_soak"] = False
    assert scheduler.zone_start_offsets(cid) == {Z1: 0, Z2: 1200}


# ---------------------------------------------------------------- #95: card counts down like the panel


@needs_node
def test_card_relative_time_floors():
    script = (
        f"const I = await import({I18N_URI});"
        "const t = I.makeT('en');"
        + _function(CARD, "fmtIn")
        + "process.stdout.write(JSON.stringify([3.5 * 86400, 86400 * 1.99, 23 * 3600 + 3540, 90 * 60, 59 * 60 + 50, 30, 0]"
        ".map((s) => fmtIn(t, s))));"
    )
    assert json.loads(_node(script)) == ["in 3d", "in 1d", "in 23h", "in 1h", "in 59m", "in 1m", "in 0m"]


# ---------------------------------------------------------------- #96: Delete zone


def test_zone_card_says_delete_zone():
    card = _method(PANEL, "_zoneAdminCard")
    assert 'this._t("zones.delete")' in card and '"common.delete"' not in card
    assert STRINGS["en"]["zones.delete"] == "Delete zone"
    assert STRINGS["de"]["zones.delete"] == "Zone löschen"
    assert STRINGS["he"]["zones.delete"] == "מחיקת האזור"
    for lang, strings in STRINGS.items():
        assert strings["zones.delete"] != strings["common.delete"], lang
