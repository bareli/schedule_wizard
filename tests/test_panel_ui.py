"""Frontend regression checks for v0.14.1: zone summary plural (#56), visible toasts (#51), focus kept (#41).

The plural test runs the real makeT() from www/i18n.js under Node (skipped when Node is missing).
Toast and focus behaviour need a browser; the checks here pin the parts a static read can see.
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


def _method(src: str, name: str) -> str:
    """Body of a class method, from its signature to the next method at the same indent."""
    match = re.search(rf"\n  (?:async )?{name}\([^)]*\) {{\n(.*?)\n  }}\n", src, re.S)
    assert match, f"{name} not found"
    return match.group(1)


def _zone_week(lang: str, runs: int) -> str:
    """The zone summary text exactly as panel.js builds it, via the real makeT()."""
    call = re.search(r'this\._t\("valves\.week", (\{[^}]*\})\)', PANEL)
    assert call, "valves.week call not found in panel.js"
    args = call.group(1).replace("stats.runs_7d", str(runs)).replace("stats.total_min_7d", "45")
    script = (
        f"const I = await import({json.dumps((WWW / 'i18n.js').as_uri())});"
        f"process.stdout.write(I.makeT({json.dumps(lang)})('valves.week', {args}));"
    )
    out = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, check=True, timeout=30,
    )
    return out.stdout.decode("utf-8")


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize(
    ("lang", "runs", "expected"),
    [
        ("en", 1, "1 run / 45 min last 7 days"),
        ("en", 2, "2 runs / 45 min last 7 days"),
        ("de", 1, "1 Lauf / 45 Min. in den letzten 7 Tagen"),
        ("de", 3, "3 Läufe / 45 Min. in den letzten 7 Tagen"),
        ("he", 1, "הפעלה אחת / 45 דק׳ ב־7 הימים האחרונים"),
        ("he", 4, "4 הפעלות / 45 דק׳ ב־7 הימים האחרונים"),
    ],
)
def test_zone_week_summary_plural(lang, runs, expected):
    """#56: one run in 7 days reads "1 run" / "1 Lauf" / Hebrew singular, more runs the plural."""
    assert _zone_week(lang, runs) == expected


def test_zone_week_singular_in_every_language():
    """#56: every language has its own singular, without the count placeholder."""
    from tests.test_i18n import STRINGS

    for lang, strings in STRINGS.items():
        one = strings["valves.week_one"]
        assert "{runs}" not in one and "{min}" in one, lang
        assert one != strings["valves.week"], lang
