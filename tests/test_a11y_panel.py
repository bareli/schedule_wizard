"""v0.15.0 panel accessibility: BUG-003 #42, BUG-004 #43, BUG-005 #44, BUG-006 #45, BUG-007 #46, BUG-011 #50,
UX-005 #60, UX-006 #61, UX-007 #62, UX-008 #63, ENH-002 #58, and the #41 note (Stop returns focus to Water now).

Focus, keyboard and screen-reader behaviour need a browser (A11Y-02 .. A11Y-10); these checks pin what a static
read or Node can see: the shared dialog helper, the markup, the colour tokens (contrast computed here from HA's
default theme colours) and the live-region logic run under Node.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

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


# ---------------------------------------------------------------- BUG-003 #42: modal dialogs


def test_every_dialog_goes_through_the_focus_helper():
    """Zone / plan / schedule (_showModal), the run dialog and the wizard all open through _openDialog."""
    for name in ("_showModal", "_openRunModal", "_openWizard"):
        body = _method(PANEL, name)
        assert "this._openDialog(overlay, modal" in body, name
        assert 'addEventListener("keydown"' not in body, f"{name} handles keys itself"
        assert "this._modalRoot.innerHTML" not in body, f"{name} empties the dialog root itself"
    # Nothing else empties the dialog root behind the helper's back (the page would stay inert).
    assert PANEL.count('this._modalRoot.innerHTML = ""') == 3
    assert "this._closeDialog();" in _method(PANEL, "set hass")


def test_dialog_helper_takes_traps_and_returns_focus():
    body = _method(PANEL, "_openDialog")
    # remembers the opener (node and re-render key) before anything changes
    assert body.index("const opener = deepActiveElement();") < body.index("this._modalRoot.appendChild(overlay)")
    assert "const openerKey = captureFocus(app);" in body
    # Escape from anywhere (document listener), Tab and Shift+Tab wrap inside the dialog
    assert 'document.addEventListener("keydown", onKey)' in body
    assert 'e.key === "Escape"' in body and 'e.key !== "Tab"' in body
    assert "items[items.length - 1].focus()" in body and "items[0].focus()" in body
    # the page behind is inert while open, and focus goes back on close
    assert "app.inert = true" in body and "app.inert = false" in body
    assert "opener.focus(" in body and "restoreFocus(app, openerKey)" in body
    assert 'document.removeEventListener("keydown", onKey)' in body
    # focus moves in: the first field, else the first control, else the dialog itself
    assert "target.focus()" in body


def test_generic_dialog_is_named_by_its_title():
    body = _method(PANEL, "_showModal")
    assert '"aria-labelledby": titleId' in body and 'el("h3", { id: titleId }, title)' in body


def test_wizard_step_without_field_focuses_its_heading():
    body = _method(PANEL, "_openWizard")
    assert 'el("h3", { id: "sw-wiz-title", tabindex: "-1" }' in body
    assert 'body.querySelector("input, button") || head.querySelector("h3")' in body
    assert "canClose: () => !wz.saving" in body


# ---------------------------------------------------------------- BUG-004 #43: entity picker by keyboard


def test_entity_rows_are_toggle_buttons_outside_the_search_label():
    body = _method(PANEL, "_openValveModal")
    assert 'el("button", {\n          type: "button", class: "entity-row", "aria-pressed":' in body
    assert 'class: "entity-picker", role: "group", "aria-labelledby": pickerCap' in body
    assert '"aria-labelledby": pickerCap });' in body  # the search box: named by the caption only
    assert "search, picker]" not in body.replace("search, picker, entityErr]", "")
    assert 'el("div", { class: "field" }, [el("span", { id: pickerCap }' in body
    # choosing a row updates in place, so the pressed row keeps the focus
    click = body[body.index('row.addEventListener("click"'):]
    assert "renderPicker()" not in click[:click.index("picker.appendChild(row)")]


# ---------------------------------------------------------------- BUG-005 #44, BUG-006 #45: contrast

HEX = re.compile(r"#([0-9a-fA-F]{6})")


def _rgb(h: str) -> tuple[float, float, float]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _lum(c) -> float:
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2])


def _ratio(a, b) -> float:
    x, y = _lum(a), _lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def _mix(a, b, p):
    return tuple(a[i] * p + b[i] * (1 - p) for i in range(3))


def _over(fg, alpha, bg):
    return _mix(fg, bg, alpha)


# Home Assistant 2026.9 default theme, as measured in BUG-005 / BUG-006.
HA = {"primary": "#009ac7", "success": "#43a047", "danger": "#db4437", "warn": "#ffa600"}
THEMES = {
    "light": {"text": "#212121", "bg": "#fafafa", "card": "#ffffff"},
    "dark": {"text": "#e1e1e1", "bg": "#111111", "card": "#1c1c1c"},
}
TINT = {"primary": (3, 169, 244), "success": (22, 163, 74), "warn": (180, 83, 9)}


def _tokens(css: str, host: str = "panel") -> dict[str, tuple[str, int, str]]:
    """--sw-<name>-text / -fill declared with color-mix: (base token, percent, other colour)."""
    block = re.search(r"@supports \(color: color-mix\(in srgb, red 50%, blue\)\) \{(.*?)\n\}", css, re.S)
    assert block, f"{host}: no color-mix block"
    out = {}
    for name, base, pct, other in re.findall(
        r"--sw-([a-z]+-(?:text|fill)): color-mix\(in srgb, var\(--(?:sw-)?([a-z-]+)[^)]*\) (\d+)%, (var\([^)]*\)\)?|#000)\)",
        block.group(1),
    ):
        out[name] = (base, int(pct), other)
    return out


def test_panel_text_and_fill_colours_reach_4_5_to_1():
    """#44 / #45: coloured text on the card, the page and its own tint; white text on the fills."""
    tok = _tokens(PANEL)
    assert {"primary-text", "success-text", "danger-text", "warn-text", "primary-fill", "success-fill", "danger-fill"} <= set(tok)
    for theme, t in THEMES.items():
        text, bg, card = _rgb(t["text"]), _rgb(t["bg"]), _rgb(t["card"])
        for name in ("primary", "success", "danger", "warn"):
            _, pct, other = tok[f"{name}-text"]
            assert "sw-text" in other, name  # toward the theme's text colour: darker in light, lighter in dark
            colour = _mix(_rgb(HA[name]), text, pct / 100)
            for surface in [bg, card] + ([_over(TINT[name], 0.15, card), _over(TINT[name], 0.15, _over(TINT[name], 0.07, card))] if name in TINT else []):
                assert _ratio(colour, surface) >= 4.5, (theme, name, surface)
        for name in ("primary", "success", "danger"):
            _, pct, other = tok[f"{name}-fill"]
            assert other == "#000"
            assert _ratio((255, 255, 255), _mix(_rgb(HA[name]), (0, 0, 0), pct / 100)) >= 4.5, (theme, name)


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^{re.escape(selector)} \{{([^}}]*)\}}", css)
    assert match, selector
    return match.group(1)


@pytest.mark.parametrize(("selector", "token"), [
    (".tab.active", "--sw-primary-text"),
    (".btn.ghost", "--sw-primary-text"),
    (".link-btn", "--sw-primary-text"),
    (".pill.run", "--sw-primary-text"),
    (".pill.ok", "--sw-success-text"),
    (".pill.pause", "--sw-warn-text"),
    (".badge.warn", "--sw-warn-text"),
    (".wk-run.rain .wk-tag, .wk-tag.warn", "--sw-warn-text"),
    (".btn.danger", "--sw-danger-text"),
    (".field-error", "--sw-danger-text"),
    (".num .water", "--sw-primary-text"),
])
def test_panel_coloured_text_uses_text_tokens(selector, token):
    assert re.search(rf"(?<![-\w])color: var\({token}\)", _rule(PANEL, selector)), selector


@pytest.mark.parametrize("selector", [
    ".btn.primary", '.day-chip[aria-pressed="true"]', ".toast.error", ".toast.ok",
])
def test_panel_white_text_sits_on_a_fill(selector):
    rule = _rule(PANEL, selector)
    assert "color: #fff" in rule and re.search(r"background: var\(--sw-[a-z]+-fill\)", rule), selector


def test_card_colours_use_the_same_tokens():
    tok = _tokens(CARD, "card")
    assert {"primary-text", "danger-text", "primary-fill"} <= set(tok)
    assert "background: var(--sw-primary-fill)" in _rule(CARD, "button.run")
    assert "color: var(--sw-danger-text)" in _rule(CARD, "button.stop")
    assert "color: var(--sw-primary-text)" in _rule(CARD, ".active-runs .name")


def test_no_inline_text_in_raw_theme_colours():
    assert not re.search(r'style: "color:var\(--sw-(success|warn|danger|primary)\)', PANEL)


# ---------------------------------------------------------------- BUG-007 #46: condition rows


def test_condition_fields_are_named_with_their_row():
    body = _method(PANEL, "_openScheduleModal")
    rows = body[body.index("const renderConditions"):body.index("renderConditions();\n")]
    assert 'const named = (key) => this._t("sched.cond_field", { field: this._t(key), n });' in rows
    for key in ("sched.cond_entity", "common.attribute_optional", "sched.cond_operator", "sched.cond_value"):
        assert f'"aria-label": named("{key}")' in rows, key
    assert 'el("select", { "aria-label": named("sched.cond_operator") })' in rows
    assert '"aria-label": this._t("sched.remove_condition_n", { n })' in rows


@needs_node
def test_condition_names_read_well():
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        "const out = {};"
        "for (const l of ['en', 'he', 'de']) { const t = I.makeT(l);"
        " out[l] = [t('sched.cond_field', { field: t('sched.cond_operator'), n: 2 }), t('sched.remove_condition_n', { n: 2 })]; }"
        "process.stdout.write(JSON.stringify(out));"
    )
    got = json.loads(_node(script))
    assert got["en"] == ["Comparison, condition 2", "Remove condition 2"]
    assert got["de"] == ["Vergleich, Bedingung 2", "Bedingung 2 entfernen"]
    assert got["he"] == ["השוואה, תנאי 2", "הסרת תנאי 2"]


# ---------------------------------------------------------------- BUG-011 #50: groups and progress bars


def test_groups_are_named_by_their_caption():
    sched = _method(PANEL, "_openScheduleModal")
    assert '"aria-labelledby": daysCap' in sched and 'el("span", { id: daysCap }' in sched
    assert 'role: "group", "aria-labelledby": condCap' in sched
    wiz = _method(PANEL, "_openWizard")
    assert 'class: "days", role: "group", "aria-labelledby": daysCap' in wiz
    assert 'class: "list", role: "group", "aria-labelledby": minsCap' in wiz
    settings = _method(PANEL, "_renderSettings")
    assert 'role: "group", "aria-labelledby": targetsCap' in settings
    assert 'role: "group", "aria-labelledby": eventsCap' in settings
    plan = _method(PANEL, "_openCycleModal")
    assert 'role: "group", "aria-labelledby": stepsCap' in plan


def test_progress_bars_are_named_and_kept_current():
    status = _method(PANEL, "_statusCard")
    assert 'role: "progressbar",\n        "aria-label": this._named(this._t("home.watering_now")' in status
    zone = _method(PANEL, "_zoneCard")
    assert 'role: "progressbar", "aria-label": this._named(this._t("zone.watering"), v.label)' in zone
    assert 'bar.setAttribute("aria-valuenow"' in _method(PANEL, "_updateInPlace")


# ---------------------------------------------------------------- UX-005 #60: inline validation errors


def test_zone_dialog_errors_are_inline():
    body = _method(PANEL, "_openValveModal")
    for err in ("sw-valve-label-err", "sw-valve-entity-err", "sw-valve-flow-err"):
        assert f'fieldError("{err}")' in body, err
    save = body[body.index("this._showModal("):]
    before_call = save[:save.index('this._callService("add_valve"')]
    assert "check(!label.trim(), labelErr, labelInput" in before_call
    assert "check(!chosen, entityErr, picker" in before_call
    assert "check(flowBad, flowErr, flowRateInput" in before_call
    # focus the first invalid field; the toast stays as a second signal (v0.14.1)
    assert "invalid[0][0].focus();" in before_call and 'this._toast(invalid[0][1], "error")' in before_call
    assert '"aria-required": "true"' in body


def test_plan_dialog_errors_are_inline():
    body = _method(PANEL, "_openCycleModal")
    assert 'fieldError("sw-plan-name-err")' in body and 'fieldError("sw-plan-steps-err")' in body
    assert "setFieldError(nameErr, nameInput" in body and "setFieldError(stepsErr, stepsWrap" in body
    assert "invalid[0][0].focus();" in body and 'this._toast(invalid[0][1], "error")' in body


@needs_node
def test_set_field_error_marks_and_clears():
    """aria-invalid + aria-describedby on a field; a group is only described (aria-invalid does not apply)."""
    fake = (
        "const mk = (role) => { const a = role ? { role } : {}; return { hidden: true, textContent: '', id: 'e1',"
        " getAttribute: (k) => (k in a ? a[k] : null), setAttribute: (k, v) => { a[k] = String(v); },"
        " removeAttribute: (k) => { delete a[k]; }, attrs: a }; };"
        "const el = () => ({});"
    )
    script = fake + _function(PANEL, "setFieldError") + (
        "const err = mk(); const input = mk(); const group = mk('group'); const err2 = mk();"
        "setFieldError(err, input, 'Zone name required');"
        "setFieldError(err2, group, 'Pick a switch or valve');"
        "const a = [err.hidden, err.textContent, { ...input.attrs }, { ...group.attrs }];"
        "setFieldError(err, input, '');"
        "a.push(err.hidden, { ...input.attrs });"
        "process.stdout.write(JSON.stringify(a));"
    )
    got = json.loads(_node(script))
    assert got == [
        False, "Zone name required", {"aria-invalid": "true", "aria-describedby": "e1"},
        {"role": "group", "aria-describedby": "e1"}, True, {},
    ]


# ---------------------------------------------------------------- UX-006 #61: tabs


def test_tabs_follow_the_aria_tabs_pattern():
    body = _method(PANEL, "_render")
    assert 'tabindex: selected ? "0" : "-1"' in body
    assert '"aria-controls": "sw-tabpanel"' in body and 'id: `sw-tab-${key}`' in body
    assert 'role: "tabpanel", id: "sw-tabpanel", "aria-labelledby": `sw-tab-${this._tab}`' in body
    assert 'const next = this._rtl ? "ArrowLeft" : "ArrowRight";' in body
    assert 'e.key === "Home"' in body and 'e.key === "End"' in body
    assert "onKeydown: onTabKey" in body


# ---------------------------------------------------------------- UX-007 #62: distinct names


def test_repeated_controls_name_what_they_act_on():
    zone = _method(PANEL, "_zoneCard")
    assert '"aria-label": this._named(this._t("zone.water_now"), v.label)' in zone
    assert '"aria-label": this._named(this._t("zone.less"), v.label)' in zone
    assert '"aria-label": this._named(this._t("zone.more"), v.label)' in zone
    assert '"aria-labelledby": titleId' in zone
    assert '"aria-label": this._named(this._t("week.skip_day"), info.full)' in _method(PANEL, "_weekCard")
    row = _method(PANEL, "_schedRow")
    assert '"aria-label": this._named(this._t("common.enabled"), what)' in row
    assert '"aria-label": this._named(text, planName)' in _method(PANEL, "_planCard")
    assert 'this._t("card.action_for", { action, zone: name })' in _method(PANEL, "_named")


# ---------------------------------------------------------------- #41 note: Stop returns to Water now


def test_stop_names_water_now_as_its_successor():
    zone = _method(PANEL, "_zoneCard")
    assert '"data-focus-id": `water:${id}`, "data-refocus": `stop:${id}`' in zone
    assert '"data-focus-id": `stop:${id}`, "data-refocus": `water:${id}`' in zone
    assert 'refocus: n.getAttribute("data-refocus") || ""' in _function(PANEL, "captureFocus")
    restore = _function(PANEL, "restoreFocus")
    assert restore.index("find(key.self) || successor ||") < restore.index("key.rowNear")


# ---------------------------------------------------------------- UX-008 #63: one stable live region


def test_live_region_is_persistent_and_outside_the_page():
    init = _method(PANEL, "_init")
    assert 'this._liveRoot = el("div", { class: "sr-only", role: "status", "aria-live": "polite" });' in init
    assert "this.appendChild(this._liveRoot);" in init
    assert '"aria-live": "polite"' not in _method(PANEL, "_statusCard")
    refresh = _method(PANEL, "_refresh")
    assert refresh.index("this._announceChanges(prev, this._state);") < refresh.index("this._render();")


@needs_node
def test_announcements_only_on_start_stop_and_rain():
    """Run _announceChanges() under Node: start, stop, rain on / off; a countdown tick says nothing."""
    body = _method(PANEL, "_announceChanges")
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        "const said = [];"
        "const self = { _liveRoot: {}, _t: I.makeT('en'), _fmtWhen: () => 'Fri 1:07 PM', _say: (m) => said.push(m) };"
        f"const fn = new Function('prev', 'cur', {json.dumps(body)});"
        "const valves = [{ entity_id: 'z.front', label: 'Front lawn' }];"
        "const run = { entity_id: 'z.front', started_at: 1000, ends_at: 1600 };"
        "const s = (now, active, rain) => ({ now, valves, active, rain_delay_until: rain || 0 });"
        "fn.call(self, null, s(1000, [run]));"                     # first state: nothing
        "fn.call(self, s(1000, []), s(1005, [run]));"              # started
        "fn.call(self, s(1005, [run]), s(1010, [run]));"           # countdown tick: nothing
        "fn.call(self, s(1010, [run]), s(1015, []));"              # stopped
        "fn.call(self, s(1015, []), s(1020, [], 90000));"          # rain pause on
        "fn.call(self, s(1020, [], 90000), s(1025, [], 90000));"   # still paused: nothing
        "fn.call(self, s(1025, [], 90000), s(1030, [], 0));"       # rain pause ended
        "process.stdout.write(JSON.stringify(said));"
    )
    assert json.loads(_node(script)) == [
        ["Front lawn: watering started, 10 min"],
        ["Front lawn: watering stopped"],
        ["No outdoor watering until Fri 1:07 PM"],
        ["Rain pause ended"],
    ]


# ---------------------------------------------------------------- ENH-002 #58: target size


def test_small_controls_are_at_least_24px_and_44px_on_touch():
    assert "min-height: 24px;" in _rule(PANEL, ".btn")
    assert "min-height: 24px;" in _rule(PANEL, ".link-btn")
    assert "min-height: 24px;" in _rule(PANEL, ".wk-head .btn")
    assert "height: 24px;" in _rule(PANEL, ".switch")
    coarse = re.search(r"@media \(pointer: coarse\) \{(.*?)\n\}", PANEL, re.S)
    assert coarse, "no touch rules"
    block = coarse.group(1)
    assert re.search(r"\.btn, \.link-btn, \.tab, \.day-chip[^{]*\{ min-height: 44px; \}", block)
    assert ".stepper button { width: 44px; height: 44px; }" in block
    assert ".switch::before" in block
    assert "min-height: 24px;" in _rule(CARD, "button")
    assert "@media (pointer: coarse) { button { min-height: 44px; min-width: 44px; } }" in CARD
