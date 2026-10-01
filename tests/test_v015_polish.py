"""v0.15.0 polish batch: ENH-002 #58 and BUG-006 #45 (reopened), BUG-020 .. BUG-029.

Backend parts run in Home Assistant; card focus, the card picker text and the Reports totals run under Node
(skipped without Node); the rest pins what a static read of panel.js / card.js / i18n.js can see. Layout,
scrolling and the toasts at 320 px need a browser (see the issues' handbacks).
"""

from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from homeassistant.core import HomeAssistant

from custom_components.schedule_wizard.const import DOMAIN
from custom_components.schedule_wizard.notify_text import NOTIFY_TEXT, fmt_number
from custom_components.schedule_wizard.voice import REPLIES

from .conftest import advance, data, settle, setup_wizard
from .test_a11y_panel import HA, THEMES, TINT, _mix, _over, _ratio, _rgb, _rule, _tokens
from .test_i18n import STRINGS
from .test_unavailable_close import V, _history, _run, _setup, _state

WWW = Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www"
PANEL = (WWW / "panel.js").read_text(encoding="utf-8")
CARD = (WWW / "card.js").read_text(encoding="utf-8")
needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")

Z1 = "input_boolean.zone1"


def _method(src: str, name: str) -> str:
    match = re.search(rf"\n  (?:async )?{name}\([^)]*\) {{\n(.*?)\n  }}\n", src, re.S)
    assert match, f"{name} not found"
    return match.group(1)


def _node(script: str) -> str:
    out = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, check=True, timeout=30)
    return out.stdout.decode("utf-8")


def _coarse() -> str:
    match = re.search(r"@media \(pointer: coarse\) \{(.*?)\n\}", PANEL, re.S)
    assert match, "no touch rules"
    return match.group(1)


# ---------------------------------------------------------------- ENH-002 #58 (reopened): 44 px on touch


def test_week_skip_day_is_44px_high_on_touch():
    """`.wk-head .btn { min-height: 24px }` (0,2,0) beat the touch rule `.btn` (0,1,0)."""
    rule = re.search(r"(?m)^  ([^{]*)\{ min-height: 44px; \}", _coarse())
    assert rule and ".wk-head .btn" in [x.strip() for x in rule.group(1).split(",")]


def test_menu_button_and_text_fields_are_44px_on_touch():
    block = _coarse()
    assert ".menu-btn { min-width: 44px; min-height: 44px; }" in block
    fields = re.search(r"(\.app input[^{]*)\{ min-height: 44px; \}", block, re.S)
    assert fields, "text fields not raised on touch"
    sel = fields.group(1)
    for part in ('.app input:not([type="checkbox"])', ".app select", ".app textarea", ".modal input", ".modal select"):
        assert part in sel, part


# ---------------------------------------------------------------- BUG-006 #45 (reopened): card running pill


def test_card_running_pill_reaches_4_5_to_1():
    tok = _tokens(CARD, "card")
    assert "success-text" in tok
    _, pct, other = tok["success-text"]
    assert "primary-text-color" in other
    assert "color: var(--sw-success-text)" in _rule(CARD, ".pill.ok")
    assert "#15803d" not in CARD
    for theme, t in THEMES.items():
        colour = _mix(_rgb(HA["success"]), _rgb(t["text"]), pct / 100)
        surface = _over(TINT["success"], 0.15, _rgb(t["card"]))
        assert _ratio(colour, surface) >= 4.5, theme


# ---------------------------------------------------------------- BUG-020: past runs in the week view


def test_past_runs_are_muted_not_transparent():
    rule = _rule(PANEL, ".wk-run.past")
    assert "opacity" not in rule
    assert "color: var(--sw-muted)" in rule
    # HA default secondary text on the card: light #727272 / white, dark #9b9b9b / #1c1c1c.
    assert _ratio(_rgb("#727272"), _rgb(THEMES["light"]["card"])) >= 4.5
    assert _ratio(_rgb("#9b9b9b"), _rgb(THEMES["dark"]["card"])) >= 4.5


# ---------------------------------------------------------------- BUG-021: live region and RTL scroll


def test_visually_hidden_has_no_negative_margin_and_an_inset():
    rule = _rule(PANEL, ".sr-only")
    assert "margin: -1px" not in rule and "margin: 0" in rule
    assert "top: 0" in rule and "left: 0" in rule
    assert "clip-path: inset(50%)" in rule


# ---------------------------------------------------------------- BUG-022: toasts


def test_one_toast_at_a_time_and_under_the_dialog_title():
    body = _method(PANEL, "_toast")
    assert "host.replaceChildren(t);" in body
    assert "children.length >= 3" not in body
    assert "head.after(host)" in body
    rule = _rule(PANEL, ".modal .toast-host")
    assert "position: sticky" in rule and "top: 0" in rule
    assert "top: calc(12px" not in rule


# ---------------------------------------------------------------- BUG-023: card picker text


@needs_node
@pytest.mark.parametrize("lang", ["en", "de", "he"])
def test_card_picker_description_is_translated(lang):
    script = (
        "globalThis.HTMLElement = class {};"
        "globalThis.customElements = { get: () => undefined, define() {} };"
        "globalThis.window = { customCards: [] };"
        f"globalThis.document = {{ querySelector: () => ({{ hass: {{ language: {json.dumps(lang)} }} }}) }};"
        f"await import({json.dumps((WWW / 'card.js').as_uri())});"
        "const c = window.customCards.find(x => x.type === 'schedule-wizard-card');"
        "process.stdout.write(JSON.stringify({ ...c }));"
    )
    card = json.loads(_node(script))
    assert card["description"] == STRINGS[lang]["card.picker_description"]
    assert "quick run" not in card["description"]


def test_card_picker_description_in_every_language():
    texts = {lang: s["card.picker_description"] for lang, s in STRINGS.items()}
    assert len(texts) == 17
    for lang, text in texts.items():
        assert STRINGS[lang]["zone.water_now"] in text, lang  # the card's own button word


# ---------------------------------------------------------------- BUG-024: card focus after Stop


def _focus_helpers() -> str:
    names = ["deepActiveElement", "rowKey", "focusDesc", "focusables", "focusId", "captureFocus", "restoreFocus"]
    parts = [re.search(r'\nconst FOCUSABLE = "[^"]*";\n', CARD).group(0)]
    for name in names:
        match = re.search(rf"\nfunction {name}\([^)]*\) {{\n.*?\n}}\n", CARD, re.S)
        assert match, name
        parts.append(match.group(0))
    return "".join(parts)


@needs_node
@pytest.mark.parametrize(("before", "after", "want"), [
    ("button.stop", "button.run", "Water now"),   # Stop -> that zone's Water now
    ("button.run", "button.stop", "Stop watering"),  # Water now -> that zone's Stop
])
def test_card_focus_moves_between_stop_and_water_now(before, after, want):
    labels = {"button.stop": "Stop watering", "button.run": "Water now"}
    script = (
        "globalThis.document = { activeElement: null };"
        "const mk = (tag, cls, text, row) => { const n = { tagName: tag, className: cls, textContent: text, disabled: false,"
        " shadowRoot: null, getAttribute: () => null, closest: () => row, focus() { document.activeElement = n; },"
        " matches(sel) { if (sel.includes(',')) return true; const [t, c] = sel.split('.');"
        " return t.toUpperCase() === tag && (!c || cls.split(' ').includes(c)); } }; return n; };"
        "const row = { getAttribute: (k) => (k === 'data-entity' ? 'z.front' : null) };"
        "const other = { getAttribute: (k) => (k === 'data-entity' ? 'z.back' : null) };"
        "const page = (cls, text) => { const list = [mk('INPUT', '', '', row), mk('BUTTON', cls, text, row),"
        " mk('INPUT', '', '', other), mk('BUTTON', 'run', 'Water now', other)];"
        " return { list, root: { contains: () => true, querySelectorAll: () => list } }; };"
        + _focus_helpers() +
        f"const a = page({json.dumps(before.split('.')[1])}, {json.dumps(labels[before])});"
        "a.list[1].focus();"
        "const key = captureFocus(a.root);"
        f"const b = page({json.dumps(after.split('.')[1])}, {json.dumps(labels[after])});"
        "restoreFocus(b.root, key);"
        "const f = document.activeElement;"
        "process.stdout.write(JSON.stringify({ tag: f.tagName, text: f.textContent, same: f === b.list[1] }));"
    )
    got = json.loads(_node(script))
    assert got == {"tag": "BUTTON", "text": want, "same": True}


# ---------------------------------------------------------------- BUG-025: Settings groups named


def test_settings_details_groups_are_named():
    settings = _method(PANEL, "_renderSettings")
    assert 'el("details", { class: "more", "aria-labelledby": moreCap })' in settings
    assert 'el("summary", { id: moreCap }, this._t("set.more"))' in settings
    group = _method(PANEL, "_optGroup")
    assert 'el("details", { class: "opt-group", "aria-labelledby": titleId })' in group
    assert 'el("strong", { id: titleId,' in group


# ---------------------------------------------------------------- BUG-026: pending close and HA stopping


async def test_pending_close_end_row_is_saved_with_the_close(hass: HomeAssistant):
    """Every write of the store either still has the pending close or already has the end row."""
    entry, fake = await _setup(hass)
    store = data(hass, entry)["store"]
    await _run(hass)
    hass.states.async_set(V, "unavailable")
    await advance(hass, 61)
    assert [p["entity_id"] for p in store.pending_closes] == [V]

    writes: list[dict] = []
    real_save = store._store.async_save

    async def spy(payload):
        writes.append(copy.deepcopy({
            "pending": [p["entity_id"] for p in payload.get("pending_closes") or []],
            "history": [h["status"] for h in payload["history"] if h["valve_entity_id"] == V],
        }))
        await real_save(payload)

    store._store.async_save = spy
    hass.states.async_set(V, "on")  # back, still physically open
    await settle(hass)
    assert _state(hass) == "off", "valve left open"
    assert writes, "the close was never saved"
    for write in writes:
        assert V in write["pending"] or "completed" in write["history"], writes
    assert _history(hass, entry) == ["completed", "started"], "lost or doubled end row"
    assert store.pending_closes == []


async def test_pending_close_done_while_stopping_keeps_one_end_row(hass: HomeAssistant):
    """HA stops (the stop flag is set) just as the close succeeds: the entry still leaves storage with its row."""
    entry, fake = await _setup(hass)
    store = data(hass, entry)["store"]
    scheduler = data(hass, entry)["scheduler"]
    await _run(hass)
    hass.states.async_set(V, "unavailable")
    await advance(hass, 61)
    scheduler._stopping = True
    hass.states.async_set(V, "on")
    await settle(hass)
    assert _state(hass) == "off"
    assert store.pending_closes == [], "a done close would be retried and recorded again on the next start"
    assert _history(hass, entry) == ["completed", "started"]
    scheduler._stopping = False


# ---------------------------------------------------------------- BUG-027: singular and decimal comma


def test_voice_says_one_minute_and_one_day():
    for lang, minute, day in (
        ("en", "Watering Rasen for 1 minute.", "Watering paused for 1 day."),
        ("de", "Bewässere Rasen für 1 Minute.", "Bewässerung für 1 Tag pausiert."),
        ("he", "משקה את Rasen למשך דקה אחת.", "ההשקיה מושהית ליום אחד."),
    ):
        assert REPLIES[lang]["started_one"].format(name="Rasen") == minute
        assert REPLIES[lang]["paused_one"] == day
    assert set(REPLIES["de"]) == set(REPLIES["en"]) == set(REPLIES["he"])


async def test_voice_reply_for_one_minute_in_german(hass: HomeAssistant, zones):
    from custom_components.schedule_wizard.voice import VoiceCommands

    entry = await setup_wizard(hass, {"voice_enabled": False})
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Rasen"}, blocking=True)
    voice = VoiceCommands(hass, entry, data(hass, entry))
    assert await voice.async_handle("de", "run_zone_minutes", {"zone": "Rasen", "minutes": "1"}) == "Bewässere Rasen für 1 Minute."
    assert await voice.async_handle("de", "run_zone_minutes", {"zone": "Rasen", "minutes": "5"}) == "Bewässere Rasen für 5 Minuten."
    assert await voice.async_handle("de", "pause_days", {"days": "1"}) == "Bewässerung für 1 Tag pausiert."
    await hass.services.async_call(DOMAIN, "stop_all", {}, blocking=True)
    await settle(hass)


@pytest.mark.parametrize(("lang", "want"), [
    ("de", "1,5"), ("fr", "1,5"), ("ru", "1,5"), ("nb", "1,5"), ("fi", "1,5"),
    ("en", "1.5"), ("he", "1.5"), ("zh-hans", "1.5"), ("ar", "1.5"),
])
def test_numbers_use_the_language_decimal_separator(lang, want):
    assert lang in NOTIFY_TEXT
    assert fmt_number(1.5, lang) == want
    assert fmt_number(24.0, lang) == "24"


async def test_rain_pause_notification_in_german_has_a_decimal_comma(hass: HomeAssistant, zones):
    sent: list[dict] = []

    async def _notify(call):
        sent.append(dict(call.data))

    hass.services.async_register("notify", "phone", _notify)
    hass.config.language = "de"
    await setup_wizard(hass, {"notify_targets": ["phone"], "notify_events": ["rain_delay"]})
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Rasen"}, blocking=True)
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 1.5}, blocking=True)
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 1.5, "entity_id": [Z1]}, blocking=True)
    assert [m["message"] for m in sent] == [
        "Bewässerung für 1,5 Std. pausiert (Regen)",
        "Rasen: Bewässerung für 1,5 Std. pausiert (Regen)",
    ]


# ---------------------------------------------------------------- BUG-028: superseded minutes in totals


async def test_zone_totals_include_superseded_minutes(hass: HomeAssistant, hass_ws_client, zones):
    entry = await setup_wizard(hass)
    await hass.services.async_call(DOMAIN, "add_valve", {"entity_id": Z1, "label": "Front"}, blocking=True)
    store = data(hass, entry)["store"]
    await store.async_record_run(Z1, "manual", 4, "superseded", planned_min=10)
    await store.async_record_run(Z1, "manual", 6, "completed")
    await store.async_record_run(Z1, "manual", 2, "cancelled", planned_min=5)
    # Written before 0.15.0: the planned length, not what watered (no planned_min); left out.
    await store.async_record_run(Z1, "webhook", 1440, "superseded")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/get_state"})
    msg = await client.receive_json()
    stats = msg["result"]["valves"][0]["stats"]
    assert stats["runs_7d"] == 2  # a superseded run is not a run of its own
    assert stats["total_min_7d"] == 12  # but its 4 watered minutes count


@needs_node
def test_reports_totals_include_superseded_minutes():
    body = re.search(r"\n    history\.forEach\(h => \{\n(.*?)\n    \}\);\n", _method(PANEL, "_renderReports"), re.S)
    assert body, "Reports history loop not found"
    now = 1_790_000_000
    history = [
        {"valve_entity_id": "z.a", "status": "superseded", "duration_min": 4, "planned_min": 10, "ts": now - 3600},
        {"valve_entity_id": "z.a", "status": "superseded", "duration_min": 1440, "ts": now - 3600},  # before 0.15.0
        {"valve_entity_id": "z.a", "status": "completed", "duration_min": 6, "ts": now - 3500},
        {"valve_entity_id": "z.a", "status": "cancelled", "duration_min": 2, "ts": now - 20 * 86400},
        {"valve_entity_id": "z.a", "status": "started", "duration_min": 10, "ts": now - 3600},
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
        "process.stdout.write(JSON.stringify({ runs_7d: s.runs_7d, min_7d: s.min_7d, runs_30d: s.runs_30d,"
        " min_30d: s.min_30d, min_total: s.min_total, daily: Object.values(dailyMin).reduce((a, b) => a + b, 0) }));"
    )
    got = json.loads(_node(script))
    assert got == {"runs_7d": 1, "min_7d": 10, "runs_30d": 2, "min_30d": 12, "min_total": 12, "daily": 12}


# ---------------------------------------------------------------- BUG-029: Reports period in words


def test_reports_columns_say_the_period():
    assert STRINGS["en"]["reports.col_7d"] == "Last 7 days"
    assert STRINGS["en"]["reports.col_30d"] == "Last 30 days"
    assert STRINGS["de"]["reports.col_7d"] == "Letzte 7 Tage"
    old = {"7d", "30d", "7 d", "30 d", "7 T.", "30 T.", "7 j", "30 j", "7 g", "30 g", "7 pv", "30 pv", "7 дн.", "30 дн."}
    for lang, s in STRINGS.items():
        assert "7" in s["reports.col_7d"] and "30" in s["reports.col_30d"], lang
        assert s["reports.col_7d"] not in old and s["reports.col_30d"] not in old, lang
