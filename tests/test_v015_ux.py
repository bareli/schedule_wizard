"""v0.15.0 UX batch: #64 UX-009, #65 UX-010 (+ #71 card), #66 UX-011, #67 UX-012, #69 UX-014, #70 UX-015,
#72 UX-017, #73 UX-018.

Backend parts run in Home Assistant; panel helpers run under Node (skipped without Node); the rest pins what a
static read of panel.js / card.js / i18n.js can see. Layout at 320 px and the dialogs need a browser.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

import pytest
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, settle, setup_wizard
from .test_i18n import STRINGS

pytestmark = pytest.mark.usefixtures("fixed_clock", "zones")

Z1, Z2 = "input_boolean.zone1", "input_boolean.zone2"
WWW = Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www"
PANEL = (WWW / "panel.js").read_text(encoding="utf-8")
CARD = (WWW / "card.js").read_text(encoding="utf-8")
needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")


def _method(src: str, name: str) -> str:
    match = re.search(rf"\n  (?:async )?{name}\([^)]*\) {{\n(.*?)\n  }}\n", src, re.S)
    assert match, f"{name} not found"
    return match.group(1)


def _function(src: str, name: str) -> str:
    match = re.search(rf"\nfunction {name}\([^)]*\) {{\n.*?\n}}\n", src, re.S)
    assert match, f"function {name} not found"
    return match.group(0)


def _node(script: str) -> str:
    out = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, check=True, timeout=30)
    return out.stdout.decode("utf-8")


async def _state(hass, hass_ws_client) -> dict:
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/get_state"})
    msg = await client.receive_json()
    assert msg["success"], msg
    return msg["result"]


async def _daily(hass, entity_id: str, time: str = "06:00") -> str:
    resp = await hass.services.async_call(DOMAIN, "add_schedule", {
        "valve_entity_id": entity_id, "time": time, "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "duration_minutes": 10,
    }, blocking=True, return_response=True)
    return resp["schedule"]["id"]


def _next_six(after) -> int:
    day = dt_util.as_local(after)
    fire = day.replace(hour=6, minute=0, second=0, microsecond=0)
    if fire <= day:
        fire += timedelta(days=1)
    return int(fire.timestamp())


# ---------------------------------------------------------------- #65 UX-010: one next run, skips included


async def test_zone_next_run_skips_a_skipped_day(hass: HomeAssistant, hass_ws_client):
    """Skip next: the zone's next run is the day after, and the skipped run is told with it."""
    await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    sid = await _daily(hass, Z1)
    first = _next_six(dt_util.now())
    valve = (await _state(hass, hass_ws_client))["valves"][0]
    assert valve["next_run"]["fires_at"] == first and valve["next_skip"] is None

    await hass.services.async_call(DOMAIN, "skip_next", {"schedule_id": sid}, blocking=True, return_response=True)
    valve = (await _state(hass, hass_ws_client))["valves"][0]
    assert valve["next_run"]["fires_at"] == first + 86400
    assert valve["next_skip"]["fires_at"] == first and valve["next_skip"]["reason"] == "skipped_manual"


async def test_zone_next_run_waits_out_a_rain_pause(hass: HomeAssistant, hass_ws_client):
    """A 30 h rain pause: an outdoor zone's next run is the first after it; an indoor zone is not paused."""
    await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z2, "label": "Herbs", "rain_exempt": True}, blocking=True)
    await _daily(hass, Z1)
    await _daily(hass, Z2)
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 30}, blocking=True)
    await settle(hass)
    st = await _state(hass, hass_ws_client)
    until = st["rain_delay_until"]
    first = _next_six(dt_util.now())
    front = next(v for v in st["valves"] if v["entity_id"] == Z1)
    herbs = next(v for v in st["valves"] if v["entity_id"] == Z2)
    assert front["next_run"]["fires_at"] == _next_six(dt_util.utc_from_timestamp(until))
    assert front["next_skip"] == {"fires_at": first, "reason": "rain_delay", "until": until, "schedule_id": front["next_run"]["schedule_id"]}
    assert herbs["next_run"]["fires_at"] == first and herbs["next_skip"] is None


def test_zone_card_and_status_card_use_the_same_next_run():
    """The zone card line comes from next_run / next_skip; the status card skips skipped and paused runs too."""
    assert "let nextLine = this._zoneNextLine(v);" in _method(PANEL, "_zoneCard")
    line = _method(PANEL, "_zoneNextLine")
    assert "v.next_skip" in line and '"home.next_zone_skipped"' in line and '"home.next_zone_paused"' in line
    status = _method(PANEL, "_statusCard")
    assert 'r.skip !== "skipped_manual" && r.skip !== "rain_delay"' in status


@needs_node
def test_zone_next_line_reads_well():
    body = _method(PANEL, "_zoneNextLine")
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        "const self = { _t: I.makeT('en'), _fmtWhen: (ts) => ({ 100: 'Fri 6:00 AM', 200: 'Mon 6:00 AM', 150: 'Sat 1:00 PM' })[ts] };"
        f"const fn = new Function('v', {json.dumps(body)});"
        "const nr = { fires_at: 200, duration_min: 10 };"
        "process.stdout.write(JSON.stringify(["
        " fn.call(self, { next_run: nr, next_skip: null }),"
        " fn.call(self, { next_run: nr, next_skip: { fires_at: 100, reason: 'skipped_manual', until: 0 } }),"
        " fn.call(self, { next_run: nr, next_skip: { fires_at: 100, reason: 'rain_delay', until: 150 } }),"
        " fn.call(self, { next_run: null, next_skip: { fires_at: 100, reason: 'skipped_manual', until: 0 } }),"
        " fn.call(self, { next_run: null, next_skip: null }),"
        "]));"
    )
    assert json.loads(_node(script)) == [
        "Next: Mon 6:00 AM · 10 min",
        "Skipped Fri 6:00 AM. Next: Mon 6:00 AM · 10 min",
        "Paused until Sat 1:00 PM. Next: Mon 6:00 AM · 10 min",
        "Skipped Fri 6:00 AM. Nothing else planned",
        "No schedule yet",
    ]


@needs_node
def test_card_next_line_tells_the_skip():
    """#71 leftover: the Lovelace card's next-run line says what was skipped, like the panel."""
    body = _method(CARD, "_nextRunLine")
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        "const fmtIn = (t, s) => t('time.in_d', { n: Math.round(s / 86400) });"
        "const self = { _t: I.makeT('en'), _when: (ts) => ({ 100: 'Fri 6:00 AM', 200: 'Mon 6:00 AM' })[ts] };"
        f"const fn = new Function('fmtIn', 'v', {json.dumps(body)});"
        "const nr = { fires_at: 200, in_seconds: 259200 };"
        "process.stdout.write(JSON.stringify(["
        " fn.call(self, fmtIn, { next_run: nr }),"
        " fn.call(self, fmtIn, { next_run: nr, next_skip: { fires_at: 100, reason: 'skipped_manual' } }),"
        "]));"
    )
    assert json.loads(_node(script)) == ["Next: Mon 6:00 AM (in 3d)", "Skipped Fri 6:00 AM. Next: Mon 6:00 AM (in 3d)"]
    assert "const nextLine = active ? null : this._nextRunLine(v);" in _method(CARD, "_valveRow")


# ---------------------------------------------------------------- #67 UX-012: who started it, what happened


async def test_water_now_by_a_person_is_manual(hass: HomeAssistant):
    """The panel / card call run_valve as a logged-in user: source "manual"; an automation stays "service"."""
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z2, "label": "Back"}, blocking=True)
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 5}, blocking=True,
                                   context=Context(user_id="a-person"))
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z2, "duration_minutes": 5}, blocking=True)
    await settle(hass)
    active = data(hass, entry)["scheduler"].active
    assert active[Z1]["source"] == "manual"
    assert active[Z2]["source"] == "service"
    assert STRINGS["en"]["source.manual"] == "manual (Water now)"
    assert STRINGS["he"]["source.manual"] == "ידני (השקה עכשיו)"


def test_activity_has_a_day_filter_and_day_totals():
    card = _method(PANEL, "_activityCard")
    assert 'seg("yesterday", this._t("act.yesterday"))' in card
    assert '"aria-pressed": filter === key ? "true" : "false"' in card
    assert "this._wateredTotal(dayRows)" in card
    assert 'el("details"' not in card, "activity must not hide behind a collapsed summary"
    assert 'isSkipStatus(h.status) ? "skip" : null' in _method(PANEL, "_activityItem")
    assert "const last = this._lastWateringLine();" in _method(PANEL, "_renderHome")


@needs_node
def test_last_watering_line_reads_well():
    """ "Last watering: yesterday 06:00, 2 zones · 25 min · Skipped today 06:00: skipped (rain)". """
    fns = {name: _method(PANEL, name) for name in ("_lastWateringLine", "_wateredTotal", "_relWhen")}
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        # new Function() bodies see globals only: the module helpers they use go on globalThis.
        "globalThis.I18N = I;"
        "globalThis.el = (tag, attrs, text) => text;"
        "globalThis.isSkipStatus = (s) => String(s || '').startsWith('skipped_');"
        "globalThis.dayNum = (key) => Math.round(Date.UTC(...key.split('-').map((x, i) => i === 1 ? x - 1 : +x)) / 86400000);"
        "const hass = { config: { time_zone: 'UTC' }, locale: { language: 'en', time_zone: 'server' } };"
        "const self = { _t: I.makeT('en'), _hass: hass, _isPlanId: (id) => !String(id).includes('.'),"
        " _fmtTime: (ts) => I.fmtTime(ts, 'en', { hass, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }),"
        " _fmtDate: () => 'Mon', _statusLabel: (s) => I.makeT('en')('status.' + s) };"
        + "".join(f"self.{n} = new Function({'ts' if n == '_relWhen' else 'rows' if n == '_wateredTotal' else ''!r}, "
                  f"{json.dumps(b)}).bind(self);" for n, b in fns.items())
        + "const D = 1781078400;"  # 2026-06-10 08:00 UTC
        "self._state = { now: D + 3600, history: ["
        " { valve_entity_id: 'z.a', status: 'skipped_rain', ts: D - 7200, duration_min: 0 },"
        " { valve_entity_id: 'z.b', status: 'completed', ts: D - 86400 - 3600 + 900, duration_min: 15 },"
        " { valve_entity_id: 'z.a', status: 'completed', ts: D - 86400 - 7200 + 600, duration_min: 10 },"
        " { valve_entity_id: 'z.a', status: 'started', ts: D - 86400 - 7200, duration_min: 10 },"
        "] };"
        "process.stdout.write(JSON.stringify(self._lastWateringLine()));"
    )
    assert json.loads(_node(script)) == "Last watering: yesterday 06:00, 2 zones · 25 min · Skipped today 06:00: skipped (rain)"


# ---------------------------------------------------------------- #70 UX-015: own entities are no zones


async def test_pickers_and_add_valve_skip_own_entities(hass: HomeAssistant, hass_ws_client):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    await hass.async_block_till_done()
    own = sorted(e.entity_id for e in er.async_get(hass).entities.values() if e.platform == DOMAIN and e.domain == "switch")
    assert own, "the integration should have created its switches"
    ids = [c["entity_id"] for c in (await _state(hass, hass_ws_client))["controllable"]]
    assert Z1 in ids and Z2 in ids
    assert not set(own) & set(ids)
    with pytest.raises(Exception, match="cannot be a zone"):
        await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": own[0], "label": "Loop"}, blocking=True)
    assert [v["entity_id"] for v in data(hass, entry)["store"].valves] == [Z1]


# ---------------------------------------------------------------- #66 UX-011: rain source and notify names


async def test_rain_source_must_exist(hass: HomeAssistant, hass_ws_client):
    """A typed rain source that does not exist is refused (it used to save and never skip)."""
    entry = await setup_wizard(hass)
    client = await hass_ws_client(hass)

    async def save(value):
        await client.send_json_auto_id({"type": f"{DOMAIN}/update_options", "rain_entity": value})
        return await client.receive_json()

    msg = await save("banana")
    assert not msg["success"] and "rain_entity" in msg["error"]["message"]
    assert not (await save("weather.nowhere"))["success"]
    hass.states.async_set("binary_sensor.rain", "off")
    assert (await save("binary_sensor.rain"))["success"]
    assert entry.options["rain_entity"] == "binary_sensor.rain"
    hass.states.async_remove("binary_sensor.rain")
    assert (await save("binary_sensor.rain"))["success"], "an unchanged source that went missing must not block saving"
    assert (await save(""))["success"]


async def test_rain_binary_sensor_on_skips(hass: HomeAssistant):
    entry = await setup_wizard(hass, {"rain_entity": "binary_sensor.rain"})
    scheduler = data(hass, entry)["scheduler"]
    hass.states.async_set("binary_sensor.rain", "off")
    assert scheduler._should_skip_for_rain() is False
    hass.states.async_set("binary_sensor.rain", "on")
    assert scheduler._should_skip_for_rain() is True


async def test_notify_targets_have_readable_names(hass: HomeAssistant, hass_ws_client):
    async def _noop(call):
        return None

    for name in ("mobile_app_pixel_8", "persistent_notification", "send_message", "telegram_family"):
        hass.services.async_register("notify", name, _noop)
    MockConfigEntry(domain="mobile_app", title="Pixel 8", data={"device_name": "Pixel 8"}).add_to_hass(hass)
    await setup_wizard(hass)
    info = {i["service"]: i for i in (await _state(hass, hass_ws_client))["notify_targets_info"]}
    assert info["mobile_app_pixel_8"] == {"service": "mobile_app_pixel_8", "kind": "mobile", "name": "Pixel 8"}
    assert info["persistent_notification"]["kind"] == "persistent_notification"
    assert info["send_message"]["kind"] == "send_message"
    assert info["telegram_family"] == {"service": "telegram_family", "kind": "other", "name": "telegram family"}
    assert STRINGS["en"]["notify.mobile"] == "Phone: {name}"


def test_settings_rain_source_is_a_picker_with_a_check():
    settings = _method(PANEL, "_renderSettings")
    assert "this._rainPicker(opts.rain_entity" in settings
    assert "rain_entity: rainPicker.value()" in settings
    assert 'el("input", { type: "text", dir: "ltr", placeholder: this._t("settings.rain_entity_ph")' not in settings
    picker = _method(PANEL, "_rainPicker")
    assert 'el("optgroup"' in picker and '"set.rain_check_missing"' in picker and "rainWouldSkip(st, r)" in picker
    assert "iso(this._notifyLabel(info))" in settings


@needs_node
def test_rain_check_matches_the_server_rules():
    script = (
        _function(PANEL, "rainRules").replace("DEFAULT_RAIN_STATES", '"rainy,pouring,snowy,lightning-rainy"')
        + _function(PANEL, "rainWouldSkip")
        + "const r = rainRules(undefined, '', '');"
        "const num = rainRules('', '', '2');"
        "process.stdout.write(JSON.stringify(["
        " rainWouldSkip({ entity_id: 'weather.home', state: 'rainy' }, r),"
        " rainWouldSkip({ entity_id: 'weather.home', state: 'sunny' }, r),"
        " rainWouldSkip({ entity_id: 'binary_sensor.rain', state: 'on' }, r),"
        " rainWouldSkip({ entity_id: 'sensor.rain_mm', state: '2.5' }, num),"
        " rainWouldSkip({ entity_id: 'sensor.rain_mm', state: '1' }, num),"
        "]));"
    )
    assert json.loads(_node(script)) == [True, False, True, True, False]


# ---------------------------------------------------------------- #69 UX-014: one set of plan controls


def test_plan_card_has_one_edit_and_delete_per_thing():
    plan = _method(PANEL, "_planCard")
    assert '"common.disable"' not in plan and '"common.enable"' not in plan
    assert 'this._t("plans.edit")' in plan and 'this._t("plans.delete")' in plan
    assert 'el("h3", { class: "times-h", id: timesTitleId }, this._t("plans.times"))' in plan
    row = _method(PANEL, "_schedRow")
    assert 'this._t("sched.edit_time")' in row and 'this._t("sched.delete_time")' in row
    assert 'this._t("common.edit")' not in row and 'this._t("common.delete")' not in row
    for name in ("_openScheduleModal", "_openCycleModal", "_openValveModal"):
        body = _method(PANEL, name)
        assert 'this._switchField(this._t("common.enabled")' in body, name
        assert 'el("input", { type: "checkbox" });\n    enabledInput' not in body, name


def test_plans_have_one_name():
    assert STRINGS["en"]["tab.programs"] == "Plans"
    assert STRINGS["de"]["tab.programs"] == "Pläne"
    assert STRINGS["he"]["tab.programs"] in STRINGS["he"]["plans.title"]


# ---------------------------------------------------------------- #72 UX-017: the user's week


@needs_node
def test_week_starts_where_the_user_week_starts():
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        "const h = (language, first_weekday) => ({ locale: { language, first_weekday } });"
        "process.stdout.write(JSON.stringify(["
        " I.weekOrder(h('he', 'language')), I.weekOrder(h('en', 'language')), I.weekOrder(h('de', 'language')),"
        " I.weekOrder(h('he', 'monday')), I.weekOrder(h('de', 'saturday')), I.weekOrder({ language: 'en-GB' }),"
        "]));"
    )
    sun, mon, sat = [6, 0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5, 6], [5, 6, 0, 1, 2, 3, 4]
    assert json.loads(_node(script)) == [sun, sun, mon, mon, sat, mon]


def test_day_buttons_follow_the_week_order_on_one_line():
    assert "this._weekOrder().forEach((i) => {" in _method(PANEL, "_openScheduleModal")
    assert "this._weekOrder().forEach((i) => {" in _method(PANEL, "_openWizard")
    assert "this._weekOrder()\n      .filter(i => mask & DAY_BITS[i])" in _method(PANEL, "_daysFromMask")
    assert ".days { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr));" in PANEL
    assert "h.locale.first_weekday" in _method(PANEL, "_applyLang")


# ---------------------------------------------------------------- #64 UX-009 and #73 UX-018: the wizard


def test_wizard_offers_every_n_days_sun_and_rain():
    wiz = _method(PANEL, "_openWizard")
    assert '["interval", t("sched.repeat_interval")]' in wiz
    assert '["sunrise", t("sched.mode_sunrise")], ["sunset", t("sched.mode_sunset")]' in wiz
    assert "{ every_n_days: intervalValue(), start_date: startValue() }" in wiz
    assert "time_mode: wz.timeMode, sun_offset_minutes: signedOffset()" in wiz
    assert "...when, duration_minutes" in wiz and wiz.count("...when,") == 3
    assert 'this._rainPicker("",' in wiz and 't("wiz.rain_q")' in wiz and '"schedule_wizard/update_options", rain_entity: rain' in wiz


def test_wizard_step_count_does_not_change():
    wiz = _method(PANEL, "_openWizard")
    assert 'const stepKeys = () => ["pick", "when", "plan", "check"];' in wiz
    assert "wz.picked.some(isNew)" not in wiz


def test_no_native_confirm_dialogs():
    assert not re.search(r"(?<![\w.])confirm\(", PANEL), "use this._confirm(), not the browser's confirm()"
    stop = _method(PANEL, "_statusCard")
    assert 'await this._confirm(this._t("dash.stop_all_confirm"), this._t("home.stop_watering"), { focusConfirm: true })' in stop
    helper = _method(PANEL, "_confirm")
    assert "this._openDialog(overlay, modal" in helper and 'role: "alertdialog"' in helper


def test_wording_points():
    en = STRINGS["en"]
    assert "500" not in en["reports.based_on"]
    assert not en["set.g_overlap_d"].startswith("Off")
    assert en["set.ev_skipped_seasonal"] == "Skipped (too cool)"
    admin = _method(PANEL, "_zoneAdminCard")
    assert "ltr(v.entity_id)" not in admin
    assert '(stats.last_run ? this._t("valves.week_none") : "")' in admin
    assert 'this._t("reports.runs", { n: runs })' in _method(PANEL, "_renderReports")
