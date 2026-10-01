"""Static checks for the frontend translations in www/i18n.js."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

WWW = Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www"
PLACEHOLDER = re.compile(r"\{(\w+)\}")
# this._t("key", ...), this._tn("key", ...) or t("key", ...) with a string-literal key.
KEY_REF = re.compile(r"(?:\b_tn?|(?<![\w$.])t)\(\s*\"([^\"]+)\"\s*[,)]")


def _strings() -> dict[str, dict[str, str]]:
    src = (WWW / "i18n.js").read_text(encoding="utf-8")
    match = re.search(r"/\*JSON-START\*/(.*?)/\*JSON-END\*/", src, re.S)
    assert match, "JSON markers missing in i18n.js"
    return json.loads(match.group(1))


STRINGS = _strings()
EN = STRINGS["en"]


def test_expected_languages_present():
    assert {"en", "de", "he"} <= set(STRINGS)


@pytest.mark.parametrize("lang", sorted(STRINGS))
def test_same_keys_as_english(lang):
    keys = set(STRINGS[lang])
    assert keys - set(EN) == set(), f"{lang}: extra keys"
    assert set(EN) - keys == set(), f"{lang}: missing keys"


@pytest.mark.parametrize("filename", ["panel.js", "card.js"])
def test_referenced_keys_exist(filename):
    src = (WWW / filename).read_text(encoding="utf-8")
    refs = set(KEY_REF.findall(src))
    assert refs, f"no translation keys found in {filename}"
    missing = sorted(k for k in refs if k not in EN)
    assert not missing, f"{filename} references unknown keys: {missing}"


@pytest.mark.parametrize("lang", sorted(STRINGS))
def test_placeholders_match_english(lang):
    bad = {
        key: (sorted(set(PLACEHOLDER.findall(value))), sorted(set(PLACEHOLDER.findall(EN[key]))))
        for key, value in STRINGS[lang].items()
        if key in EN and set(PLACEHOLDER.findall(value)) != set(PLACEHOLDER.findall(EN[key]))
    }
    assert not bad, f"{lang}: placeholder mismatch {bad}"


@pytest.mark.parametrize("lang", sorted(STRINGS))
def test_no_em_dash(lang):
    offenders = [key for key, value in STRINGS[lang].items() if "—" in value]
    assert not offenders, f"{lang}: em-dash in {offenders}"


@pytest.mark.parametrize("lang", sorted(STRINGS))
def test_values_are_non_empty_strings(lang):
    bad = [key for key, value in STRINGS[lang].items() if not isinstance(value, str) or not value.strip()]
    assert not bad, f"{lang}: empty values {bad}"


def test_seasonal_skip_text_matches_panel():
    """#31: the skip notification uses the same words as the panel's history status, in every language."""
    from custom_components.schedule_wizard.scheduler import SEASONAL_SKIP_TEXT

    assert set(SEASONAL_SKIP_TEXT) == set(STRINGS)
    for lang, text in SEASONAL_SKIP_TEXT.items():
        assert text == STRINGS[lang]["status.skipped_seasonal_zero"], lang
        assert STRINGS[lang]["event.skipped_seasonal"].lower() == text.lower(), lang
