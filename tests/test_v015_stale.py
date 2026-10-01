"""v0.15.0 last fixes: BUG-037 (stopped runs from before 0.15.0 in watered totals), BUG-038 (the Settings rain
check line follows Home Assistant's current states).

Backend parts run in Home Assistant; panel parts run under Node (skipped without Node).
"""

from __future__ import annotations

import json
import re

from homeassistant.core import HomeAssistant

from custom_components.schedule_wizard.const import DOMAIN

from .conftest import data, setup_wizard
from .test_v015_final import D, _last_line
from .test_v015_ux import PANEL, WWW, _function, _method, _node, needs_node

Z1 = "input_boolean.zone1"


# ---------------------------------------------------------------- BUG-037: legacy stopped runs


async def test_zone_totals_leave_out_legacy_stopped_runs(hass: HomeAssistant, hass_ws_client, zones):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    store = data(hass, entry)["store"]
    await store.async_record_run(Z1, "manual", 6, "completed")
    await store.async_record_run(Z1, "manual", 2, "cancelled", planned_min=10)
    # Written by 0.14.x: the planned length, not what watered (no planned_min).
    await store.async_record_run(Z1, "manual", 120, "cancelled")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/get_state"})
    stats = (await client.receive_json())["result"]["valves"][0]["stats"]
    assert stats["runs_7d"] == 3  # still a run, as before
    assert stats["total_min_7d"] == 8  # 6 + 2; the legacy row's 120 is left out


@needs_node
def test_reports_leave_out_legacy_stopped_runs():
    body = re.search(r"\n    history\.forEach\(h => \{\n(.*?)\n    \}\);\n", _method(PANEL, "_renderReports"), re.S)
    assert body, "Reports history loop not found"
    now = 1_790_000_000
    history = [
        {"valve_entity_id": "z.a", "status": "cancelled", "duration_min": 2, "planned_min": 10, "ts": now - 3600},
        {"valve_entity_id": "z.a", "status": "cancelled", "duration_min": 120, "ts": now - 3600},  # 0.14.x
        {"valve_entity_id": "z.a", "status": "completed", "duration_min": 6, "ts": now - 3500},
    ]
    script = (
        f"const I18N = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        f"const history = {json.dumps(history)}; const now = {now}; const day = 86400;"
        "const inWindow = (ts, days) => ts >= (now - days * day);"
        "const cyclesById = {}; const valveStats = {}; const cycleStats = {}; const dailyMin = {};"
        "const skipReasons = { skipped_rain: 0, skipped_moisture: 0, skipped_overlap: 0, skipped_seasonal_zero: 0,"
        " skipped_other: 0, failed_to_open: 0, cancelled: 0 };"
        "const water = {}; let water30 = 0; let historyWater = false;"
        "const self = { _hass: { locale: { time_zone: 'server' }, config: { time_zone: 'UTC' } } };"
        f"(function () {{ history.forEach(h => {{\n{body.group(1)}\n    }}); }}).call(self);"
        "const s = valveStats['z.a'];"
        "process.stdout.write(JSON.stringify({ runs_7d: s.runs_7d, min_7d: s.min_7d, min_30d: s.min_30d,"
        " min_total: s.min_total, daily: Object.values(dailyMin).reduce((a, b) => a + b, 0) }));"
    )
    assert json.loads(_node(script)) == {"runs_7d": 3, "min_7d": 8, "min_30d": 8, "min_total": 8, "daily": 8}


@needs_node
def test_last_watering_leaves_out_legacy_stopped_runs():
    """Dev case: 2 min watered, a 0.14.x stopped row holding the planned 120 min must not add to it."""
    history = [
        {"valve_entity_id": "z.a", "status": "cancelled", "ts": D + 600, "duration_min": 2, "planned_min": 10},
        {"valve_entity_id": "z.b", "status": "cancelled", "ts": D + 1200, "duration_min": 120},
    ]
    assert _last_line(D + 7200, history) == "Last watering: today 08:10, 1 zone · 2 min"


# ---------------------------------------------------------------- BUG-038: rain check line is current

DOM_STUB = (
    "class N { constructor(tag, attrs, kids) { this.attrs = Object.assign({}, attrs); this.kids = [];"
    " this.className = (attrs && attrs.class) || ''; this.value = ''; this.isConnected = true; this.listeners = {};"
    " this.replaced = 0; [].concat(kids || []).forEach(k => this.kids.push(k)); }"
    " appendChild(c) { this.kids.push(c); } replaceChildren(...c) { this.kids = c; this.replaced++; }"
    " get innerHTML() { return this.kids.map(k => typeof k === 'string' ? k : k.innerHTML).join(''); }"
    " addEventListener(e, f) { this.listeners[e] = f; } setAttribute(k, v) { this.attrs[k] = v; } }"
    "globalThis.document = { createElement: (tag) => new N(tag) };"
)


@needs_node
def test_rain_check_line_follows_current_states():
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        "const t = I.makeT('en');"
        + _function(PANEL, "rainRules").replace("DEFAULT_RAIN_STATES", '"rainy,pouring"')
        + _function(PANEL, "rainWouldSkip")
        + _function(PANEL, "rainCheckParts")
        + DOM_STUB
        + "Object.assign(globalThis, { el: (tag, attrs, kids) => new N(tag, attrs, kids), ltr: (x) => String(x),"
        " optLabel: (a) => a, fieldError: () => new N('span'), setFieldError: () => {}, uid: (p) => p + '1',"
        " RAIN_DOMAINS: ['weather', 'sensor', 'binary_sensor'], rainRules, rainWouldSkip, rainCheckParts });"
        "const mk = (rain, other) => ({ states: {"
        " 'binary_sensor.rain': { entity_id: 'binary_sensor.rain', state: rain, attributes: {} },"
        " 'binary_sensor.other': { entity_id: 'binary_sensor.other', state: other, attributes: {} } } });"
        "const self = { _t: t, _tn: (k, v) => I.tnodes(t(k), v), _hass: mk('off', 'off'), _state: {},"
        " _rainPickers: new Set() };"
        "self._rainPicker = new Function('current', 'rules', 'label', "
        + json.dumps(_method(PANEL, "_rainPicker"))
        + ").bind(self);"
        "self._refreshRainChecks = new Function("
        + json.dumps(_method(PANEL, "_refreshRainChecks"))
        + ").bind(self);"
        "const p = self._rainPicker('binary_sensor.rain', () => rainRules(undefined, '', ''));"
        "const line = p.node.kids[3];"
        "const out = [line.innerHTML];"
        "self._hass = mk('on', 'on'); self._refreshRainChecks(); out.push(line.innerHTML);"
        "const n = line.replaced; self._refreshRainChecks(); out.push(line.replaced - n);"
        "p.select.value = 'binary_sensor.other'; p.select.listeners.change();"
        "out.push(line.innerHTML.includes('Now: on'));"
        "p.node.isConnected = false; self._refreshRainChecks(); out.push(self._rainPickers.size);"
        "process.stdout.write(JSON.stringify(out));"
    )
    got = json.loads(_node(script))
    assert got[0] == "Skips while the sensor is on. Now: off."
    assert got[1].startswith("Skips while the sensor is on. Now: on.")  # a state change while Settings is open
    assert got[2] == 0  # unchanged text: the line is not rewritten (no repeated announcement)
    assert got[3] is True  # re-selecting reads the current state, not the one from when Settings was drawn
    assert got[4] == 0  # a picker that left the page is dropped
