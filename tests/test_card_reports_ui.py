"""Frontend regression checks for v0.15.0: card names and layout (#47, #71), Reports semantics and reflow (#48, #49).

cardSections() runs for real under Node (skipped when Node is missing); the rest pins what a static read can see.
Accessibility tree and layout at 320 px need a browser.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.test_i18n import STRINGS

WWW = Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www"
PANEL = (WWW / "panel.js").read_text(encoding="utf-8")
CARD = (WWW / "card.js").read_text(encoding="utf-8")

needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")


def _method(src: str, name: str) -> str:
    """Body of a class method, from its signature to the next method at the same indent."""
    match = re.search(rf"\n  (?:static )?(?:async )?{name}\([^)]*\) {{\n(.*?)\n  }}\n", src, re.S)
    assert match, f"{name} not found"
    return match.group(1)


def _sections(state: dict, config: dict) -> dict:
    """card.js cardSections() under Node, with just enough DOM globals for the module to load."""
    script = (
        "globalThis.HTMLElement = class {};"
        "globalThis.customElements = { get: () => true, define() {} };"
        f"const C = await import({json.dumps((WWW / 'card.js').as_uri())});"
        f"const r = C.cardSections({json.dumps(state)}, {json.dumps(config)});"
        "process.stdout.write(JSON.stringify({"
        " runs: r.runs.map(x => x.entity_id), soaks: r.soaks.map(x => x.entity_id),"
        " showActive: r.showActive, valves: r.valves.map(x => x.entity_id), anyValves: r.anyValves }));"
    )
    out = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, check=True, timeout=30,
    )
    return json.loads(out.stdout.decode("utf-8"))


STATE = {
    "valves": [{"entity_id": "switch.a"}, {"entity_id": "switch.b"}, {"entity_id": "switch.c"}],
    "active": [{"entity_id": "switch.a"}],
    "soaking": [{"entity_id": "switch.c", "phase": "soaking", "owner": "standalone"}],
}


@needs_node
def test_card_running_zone_listed_once():
    """#71: a zone in the running block is not listed again with a second Stop and progress bar."""
    r = _sections(STATE, {})
    assert r["showActive"] is True
    assert r["runs"] == ["switch.a"] and r["soaks"] == ["switch.c"]
    assert r["valves"] == ["switch.b"]


@needs_node
def test_card_without_running_block_keeps_every_zone():
    """#71: with show_active off the list is the only place to stop a zone, so nothing is hidden."""
    r = _sections(STATE, {"show_active": False})
    assert r["showActive"] is False
    assert r["valves"] == ["switch.a", "switch.b", "switch.c"]


@needs_node
def test_card_zone_filter_and_empty_list():
    """#71: the editor clears the zone picker to [] which means every zone, like no list."""
    assert _sections(STATE, {"valves": []})["valves"] == ["switch.b"]
    r = _sections(STATE, {"valves": ["switch.b"]})
    assert r["runs"] == [] and r["soaks"] == [] and r["showActive"] is False
    assert r["valves"] == ["switch.b"]
    assert _sections(STATE, {"valves": ["switch.x"]})["anyValves"] is False


def test_card_inputs_and_buttons_are_named_per_zone():
    """#47: the minutes field and every button carry the zone in their accessible name."""
    row = _method(CARD, "_valveRow")
    assert '"aria-label": this._t("card.minutes_for", { zone: v.label })' in row
    assert '"aria-label": this._t("card.action_for", { action: waterNow, zone: v.label })' in row
    stop = _method(CARD, "_stopButton")
    assert '"aria-label": this._t("card.action_for", { action: text, zone: label })' in stop
    # The minutes field shows its unit next to it (#71).
    assert 'el("label", { class: "mins" }, this._tn("unit.min", { n: minsInput }))' in row
    # Every Stop in the card goes through _stopButton.
    assert CARD.count('class: "stop"') == 1


def test_card_name_starts_with_visible_text():
    """#47: WCAG 2.5.3, the accessible name contains the visible label, in every language."""
    for lang, strings in STRINGS.items():
        assert strings["card.action_for"].startswith("{action}"), lang
        assert "{zone}" in strings["card.minutes_for"], lang


def test_card_uses_panel_words():
    """#71: Water now / Stop watering / Off as in the panel, not Run / Stop / idle."""
    for key in ("common.run", "common.stop", "card.idle"):
        assert f'this._t("{key}")' not in CARD, key
    assert 'this._t("zone.water_now")' in CARD
    assert 'this._t("home.stop_watering")' in CARD
    assert 'this._t("zone.off")' in CARD


def test_card_title_is_a_heading():
    """#47: the card title is a heading, not a div."""
    render = _method(CARD, "_render")
    assert 'el("h2", {}, this._config.title || "Schedule Wizard")' in render


def test_card_has_visual_editor():
    """#71: the card picker offers a visual editor and a stub config instead of YAML only."""
    assert "static async getConfigElement()" in CARD
    assert 'return document.createElement("schedule-wizard-card-editor");' in CARD
    stub = _method(CARD, "getStubConfig")
    assert "title" in stub
    assert 'customElements.define("schedule-wizard-card-editor", ScheduleWizardCardEditor)' in CARD
    schema = _method(CARD, "_schema")
    for field in ("title", "valves", "show_active", "show_quick_run"):
        assert f'name: "{field}"' in schema, field
    assert "include_entities" in schema and "multiple: true" in schema
    assert "preview: true" in CARD


def test_reports_chart_has_text_alternative():
    """#48: the bar chart is an image with a summary name, and the daily values are a table."""
    body = _method(PANEL, "_renderReports")
    assert 'role: "img"' in body
    assert '"aria-label": chartSummary' in body
    assert 'this._t("reports.chart_summary"' in body and 'this._t("reports.chart_none")' in body
    assert 'el("details", { class: "chart-values" }' in body


def test_reports_tables_are_tables():
    """#48: per-zone and per-plan totals are <table> with column and row headers, not span grids."""
    body = _method(PANEL, "_renderReports")
    assert "grid-template-columns:1.4fr" not in body
    assert "grid-template-columns:1.5fr" not in body
    assert body.count("reportTable(") == 3
    assert body.count('el("th", { scope: "row" }') == 3
    helper = re.search(r"\nfunction reportTable\(.*?\n}\n", PANEL, re.S)
    assert helper, "reportTable helper missing"
    assert 'el("table", { class: "report-table" }' in helper.group(0)
    assert 'scope: "col"' in helper.group(0)


def test_reports_tables_wrap_instead_of_overflowing():
    """#49: fixed table layout with wrapping cells, so long German headers stay inside 320 px."""
    css = re.search(r"\.report-table \{(.*?)\}", PANEL, re.S)
    assert css and "table-layout: fixed" in css.group(1) and "width: 100%" in css.group(1)
    cells = re.search(r"\.report-table th, \.report-table td \{(.*?)\}", PANEL, re.S)
    assert cells and "overflow-wrap: anywhere" in cells.group(1)
