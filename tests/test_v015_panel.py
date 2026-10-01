"""Panel parts of #59 (sunrise / sunset editor), #78 (calendar keyword) and #79 (longest external run).

Static reads of panel.js plus the real makeT() under Node (skipped when Node is missing).
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


def _method(name: str) -> str:
    match = re.search(rf"\n  (?:async )?{name}\([^)]*\) {{\n(.*?)\n  }}\n", PANEL, re.S)
    assert match, f"{name} not found"
    return match.group(1)


def test_schedule_editor_sends_sun_fields():
    body = _method("_openScheduleModal")
    for needle in ('value: "sunrise"', 'value: "sunset"', 'value: "clock"', "time_mode: timeMode",
                   "sun_offset_minutes: signedOffset(off)", "schedule_wizard/preview_schedule",
                   'this._t("sched.err_offset")', "...timing,"):
        assert needle in body, needle
    # A sunrise schedule never sends an empty clock time (the server would reject it).
    assert "out.time = time" in body


def test_zone_change_keeps_sun_time():
    """Moving watering times to another zone re-creates them with the same start rule."""
    assert "...timePayload(s)," in PANEL
    assert "sun_offset_minutes: parseInt(s.sun_offset_min, 10) || 0" in PANEL


def test_settings_send_and_check_external_options():
    body = _method("_renderSettings")
    for needle in ("calendar_keyword: calKeywordInput.value.trim()", "max_external_minutes: maxExtValue()",
                   'this._t("set.cal_keyword_err")', 'this._t("set.max_external_err")', "externalCheck()",
                   'maxlength: "40"'):
        assert needle in body, needle


def test_activity_shows_shortened_runs():
    assert "this._cappedLabel(h.note)" in _method("_activityItem")


def _t(lang: str, key: str, args: dict) -> str:
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        f"process.stdout.write(I.makeT({json.dumps(lang)})({json.dumps(key)}, {json.dumps(args)}));"
    )
    out = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True,
                         encoding="utf-8", check=True)
    return out.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize(("lang", "key", "args", "expected"), [
    ("en", "sched.before_sunrise", {"n": 30}, "30 min before sunrise"),
    ("de", "sched.after_sunset", {"n": 15}, "15 Min. nach Sonnenuntergang"),
    ("he", "sched.before_sunrise", {"n": 30}, "30 דק׳ לפני הזריחה"),
    ("en", "home.act_capped", {"n": 300}, "shortened from 300 min"),
])
def test_new_strings(lang, key, args, expected):
    assert _t(lang, key, args) == expected
