"""#68 (UX-013): notification texts in the HA language, worded for people, titled with the zone or plan."""
from __future__ import annotations

import json
import re
from datetime import timedelta
from pathlib import Path

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.schedule_wizard.const import DOMAIN
from custom_components.schedule_wizard.notify_text import NOTIFY_TEXT
from custom_components.schedule_wizard.scheduler import SEASONAL_SKIP_TEXT

from .conftest import advance, settle, setup_wizard
from .test_scheduler import Z1, Z2, add_cycle, add_valve

pytestmark = pytest.mark.usefixtures("zones")

WWW = Path(__file__).resolve().parent.parent / "custom_components" / "schedule_wizard" / "www"
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def _panel_strings() -> dict[str, dict[str, str]]:
    src = (WWW / "i18n.js").read_text(encoding="utf-8")
    return json.loads(re.search(r"/\*JSON-START\*/(.*?)/\*JSON-END\*/", src, re.S).group(1))


# ---------------------------------------------------------------- the table

def test_same_languages_as_the_panel():
    assert set(NOTIFY_TEXT) == set(_panel_strings()) == set(SEASONAL_SKIP_TEXT)


@pytest.mark.parametrize("lang", sorted(NOTIFY_TEXT))
def test_keys_and_placeholders_match_english(lang):
    en = NOTIFY_TEXT["en"]
    assert set(NOTIFY_TEXT[lang]) == set(en)
    for key, text in NOTIFY_TEXT[lang].items():
        assert set(PLACEHOLDER.findall(text)) == set(PLACEHOLDER.findall(en[key])), (lang, key)
        assert text.strip() and "—" not in text, (lang, key)


@pytest.mark.parametrize("lang", sorted(NOTIFY_TEXT))
def test_finished_zone_reads_like_the_panel(lang):
    """The 'watered' notification is the panel's Recent activity sentence."""
    assert NOTIFY_TEXT[lang]["valve_done"] == _panel_strings()[lang]["home.act_watered"]


# ---------------------------------------------------------------- what is sent

@pytest.fixture
def sent(hass: HomeAssistant) -> list[dict]:
    calls: list[dict] = []

    async def _notify(call: ServiceCall):
        calls.append(dict(call.data))

    hass.services.async_register("notify", "phone", _notify)
    return calls


ALL_EVENTS = ["valve_start", "valve_end", "cycle_start", "cycle_end", "skipped_rain", "rain_delay"]


async def _setup(hass, lang: str, **options):
    hass.config.language = lang
    return await setup_wizard(hass, {"notify_targets": ["phone"], "notify_events": ALL_EVENTS, **options})


@pytest.mark.parametrize(("lang", "start", "done", "stopped"), [
    ("en", "Front lawn started, 2 min", "Front lawn watered 2 min", "Front lawn stopped"),
    ("de", "Front lawn gestartet, 2 Min.", "Front lawn: 2 Min. bewässert", "Front lawn gestoppt"),
    ("he", "Front lawn: ההשקיה התחילה, 2 דק׳", "Front lawn: השקיה של 2 דק׳", "Front lawn: ההשקיה הופסקה"),
    ("pt-BR", "Front lawn: rega iniciada, 2 min", "Front lawn regou 2 min", "Front lawn: rega parada"),
    ("ja", "Front lawn started, 2 min", "Front lawn watered 2 min", "Front lawn stopped"),  # not translated: English
])
async def test_zone_start_and_finish(hass: HomeAssistant, sent, lang, start, done, stopped):
    await _setup(hass, lang)
    await add_valve(hass, Z1, "Front lawn")
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 2}, blocking=True)
    await advance(hass, 121)
    await hass.services.async_call(DOMAIN, "run_valve", {"entity_id": Z1, "duration_minutes": 2}, blocking=True)
    await hass.services.async_call(DOMAIN, "stop_valve", {"entity_id": Z1}, blocking=True)
    await settle(hass)
    assert [m["message"] for m in sent] == [start, done, start, stopped]
    # The zone is the title, so a phone does not show the same header ten times.
    assert {m["title"] for m in sent} == {"Front lawn"}
    assert not any("(service)" in m["message"] or "Opened" in m["message"] for m in sent)


async def test_plan_start_and_finish(hass: HomeAssistant, sent):
    await _setup(hass, "de")
    await add_valve(hass, Z1, "Front")
    await add_valve(hass, Z2, "Back")
    cid = await add_cycle(hass, "Morgen", [(Z1, 1), (Z2, 2)])
    await hass.services.async_call(DOMAIN, "run_cycle", {"cycle_id": cid}, blocking=True)
    await settle(hass)
    await advance(hass, 61)
    await advance(hass, 121)
    plan = [m for m in sent if m["title"] == "Morgen"]
    assert [m["message"] for m in plan] == ["Morgen gestartet, 3 Min.", "Morgen beendet"]


async def test_rain_pause_texts(hass: HomeAssistant, sent):
    await _setup(hass, "en")
    await add_valve(hass, Z1, "Front lawn")
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 24}, blocking=True)
    await hass.services.async_call(DOMAIN, "clear_rain_delay", {}, blocking=True)
    await hass.services.async_call(DOMAIN, "set_rain_delay", {"hours": 1.5, "entity_id": [Z1]}, blocking=True)
    await hass.services.async_call(DOMAIN, "clear_rain_delay", {"entity_id": [Z1]}, blocking=True)
    assert [m["message"] for m in sent] == [
        "Watering paused for 24 h (rain)",
        "Rain pause ended for all zones",
        "Front lawn: watering paused for 1.5 h (rain)",
        "Rain pause ended: Front lawn",
    ]


async def test_rain_skip_in_hebrew(hass: HomeAssistant, sent):
    await _setup(hass, "he", rain_entity="weather.home")
    hass.states.async_set("weather.home", "rainy")
    await add_valve(hass, Z1, "Front lawn")
    fire_at = dt_util.now().replace(second=0, microsecond=0) + timedelta(minutes=2)
    day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][fire_at.weekday()]
    await hass.services.async_call(DOMAIN, "add_schedule", {
        "valve_entity_id": Z1, "time": fire_at.strftime("%H:%M"), "days": [day], "duration_minutes": 5,
    }, blocking=True)
    async_fire_time_changed(hass, dt_util.as_utc(fire_at))
    await settle(hass)
    assert sent == [{"title": "Front lawn", "message": "Front lawn: דולג, יורד גשם"}]


async def test_reminder_in_finnish(hass: HomeAssistant):
    calls: list[ServiceCall] = []

    async def _notify(call: ServiceCall):
        calls.append(call)

    hass.services.async_register("notify", "mobile_app_phone", _notify)
    hass.config.language = "fi"
    await setup_wizard(hass, {"reminder_minutes": 10, "notify_targets": ["mobile_app_phone"]})
    await add_valve(hass, Z1, "Etupiha")
    fire_at = dt_util.now().replace(second=0, microsecond=0) + timedelta(minutes=12)
    day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][fire_at.weekday()]
    await hass.services.async_call(DOMAIN, "add_schedule", {
        "valve_entity_id": Z1, "time": fire_at.strftime("%H:%M"), "days": [day], "duration_minutes": 5,
    }, blocking=True)
    async_fire_time_changed(hass, dt_util.as_utc(fire_at - timedelta(minutes=10)))
    await settle(hass)
    assert len(calls) == 1
    assert calls[0].data["title"] == "Kastelu pian"
    assert calls[0].data["message"] == f"Etupiha alkaa klo {fire_at.strftime('%H:%M')} (5 min)."
    assert [a["title"] for a in calls[0].data["data"]["actions"]] == ["Ohita tänään", "Kastele nyt"]
