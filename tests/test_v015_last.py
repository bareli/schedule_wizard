"""v0.15.0 last batch: schedule times in plan lists / the wizard's Check step use the page's clock format;
the card's zone text wraps inside its column at 320 px. Panel helpers run under Node (skipped without Node)."""

from __future__ import annotations

import json

from .test_v015_ux import CARD, PANEL, WWW, _method, _node, needs_node

I18N_URI = json.dumps((WWW / "i18n.js").as_uri())


@needs_node
def test_schedule_times_use_the_locale_clock():
    script = (
        f"const I = await import({I18N_URI});"
        "const ltr = (x) => String(x);"
        "const t = I.makeT('en');"
        "const hass = { config: { time_zone: 'UTC' }, locale: { language: 'en', time_zone: 'server', time_format: '12' } };"
        "const self = { _hass: hass, _lang: 'en', _t: t, _tn: (k, v) => t(k, v), _sunWhen: () => null,"
        " _daysFromMask: () => 'Every day', _fmtDay: () => 'Oct 3',"
        " _fo: (o) => Object.assign({ hass }, o), _fmtTime: (ts, o) => I.fmtTime(ts, 'en', Object.assign({ hass }, o)) };"
        "globalThis.ltr = ltr;"
        f"self._fmtClock = new Function('hhmm', {json.dumps(_method(PANEL, '_fmtClock'))}).bind(self);"
        f"self._whenNodes = new Function('s', {json.dumps(_method(PANEL, '_whenNodes'))}).bind(self);"
        "process.stdout.write(JSON.stringify(["
        " self._whenNodes({ days_mask: 127, time_hhmm: '06:00' }),"
        " self._whenNodes({ repeat: 'interval', interval_days: 2, start_date: '2026-10-03', time_hhmm: '18:30' }),"
        "]));"
    )
    daily, interval = json.loads(_node(script))
    assert "06:00" not in daily and "6:00" in daily
    assert "18:30" not in interval and "6:30" in interval


def test_card_zone_text_wraps_in_its_column():
    src = (WWW / "card.js").read_text(encoding="utf-8")
    assert ".meta { min-width: 0; overflow-wrap: anywhere; hyphens: auto; }" in src
    assert 'el("div", { class: "meta" }, metaInner)' in src
    assert "@container (max-width: 340px)" in src and "container-type: inline-size" in src
