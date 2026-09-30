"""Assist voice commands (sentence triggers) in English, German and Hebrew.

Every sentence contains a watering word, so these never capture unrelated commands
like "start the vacuum".
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any, Callable, Optional

from homeassistant.core import CALLBACK_TYPE, HomeAssistant

from .const import CONF_RAIN_DELAY_UNTIL, DOMAIN, EVENT_RAIN_DELAY_SET

LOG = logging.getLogger(__name__)

# (language, action) -> sentence templates. {zone} / {plan} / {minutes} / {days} are wildcards.
SENTENCES: dict[tuple[str, str], list[str]] = {
    ("en", "run_zone_minutes"): ["water [the] {zone} for {minutes} minute[s]"],
    ("en", "run_zone"): ["water [the] {zone}"],
    ("en", "run_plan"): ["(start|run) [the] watering plan {plan}", "(start|run) [the] {plan} watering plan"],
    ("en", "stop_all"): ["stop [the] watering", "stop [all] [the] sprinklers", "stop watering everything"],
    ("en", "stop_zone"): ["stop watering [the] {zone}"],
    ("en", "skip_today"): ["skip [the] watering today", "skip today's watering", "no watering today"],
    ("en", "pause_days"): ["pause [the] watering for {days} day[s]"],
    ("en", "status"): ["is [the] watering on", "what is watering [now]", "is anything watering"],
    ("de", "run_zone_minutes"): ["bewässere [den|die|das] {zone} [für] {minutes} minute[n]"],
    ("de", "run_zone"): ["bewässere [den|die|das] {zone}"],
    ("de", "run_plan"): ["starte [den] bewässerungsplan {plan}"],
    ("de", "stop_all"): ["stopp[e] [die] bewässerung", "bewässerung (stoppen|beenden)"],
    ("de", "stop_zone"): ["stopp[e] [die] bewässerung (von|für) [den|die|das] {zone}"],
    ("de", "skip_today"): ["bewässerung heute überspringen", "heute nicht bewässern"],
    ("de", "pause_days"): ["pausiere [die] bewässerung für {days} tag[e]"],
    ("de", "status"): ["läuft [die] bewässerung", "was wird [gerade] bewässert"],
    ("he", "run_zone_minutes"): ["(תשקה|השקה|תשקי) [את] {zone} [למשך] {minutes} דקות", "(תשקה|השקה|תשקי) [את] {zone} [למשך] {minutes} דק"],
    ("he", "run_zone"): ["(תשקה|השקה|תשקי) [את] {zone}"],
    ("he", "run_plan"): ["(הפעל|תפעיל|תפעילי) [את] תוכנית [ה]השקיה {plan}"],
    ("he", "stop_all"): ["(עצור|תעצור|תעצרי) [את] [כל] ההשקיה", "(עצור|תעצור|תעצרי) השקיה"],
    ("he", "stop_zone"): ["(עצור|תעצור|תעצרי) [את] [ה]השקיה [של|ב] {zone}"],
    ("he", "skip_today"): ["(דלג|תדלג|תדלגי) על ההשקיה היום", "בלי השקיה היום"],
    ("he", "pause_days"): ["(השהה|תשהה|תשהי) [את] ההשקיה [ל|למשך] {days} ימים"],
    ("he", "status"): ["מה משקה עכשיו", "האם ההשקיה פועלת"],
}

REPLIES = {
    "en": {
        "started": "Watering {name} for {minutes} minutes.",
        "plan_started": "Starting {name}.",
        "stopped_all": "Watering stopped.",
        "stopped": "Stopped {name}.",
        "skipped": "Skipped {count} run(s) today.",
        "nothing_today": "Nothing else is scheduled today.",
        "paused": "Watering paused for {days} days.",
        "no_zone": "I don't know a zone called {name}.",
        "no_plan": "I don't know a watering plan called {name}.",
        "bad_number": "I didn't catch the number.",
        "idle": "Nothing is watering right now.",
        "running": "Watering: {names}.",
        "failed": "That didn't work: {error}",
    },
    "de": {
        "started": "Bewässere {name} für {minutes} Minuten.",
        "plan_started": "Starte {name}.",
        "stopped_all": "Bewässerung gestoppt.",
        "stopped": "{name} gestoppt.",
        "skipped": "{count} Lauf/Läufe heute übersprungen.",
        "nothing_today": "Heute ist nichts mehr geplant.",
        "paused": "Bewässerung für {days} Tage pausiert.",
        "no_zone": "Ich kenne keine Zone namens {name}.",
        "no_plan": "Ich kenne keinen Bewässerungsplan namens {name}.",
        "bad_number": "Ich habe die Zahl nicht verstanden.",
        "idle": "Gerade wird nichts bewässert.",
        "running": "Bewässert wird: {names}.",
        "failed": "Das hat nicht geklappt: {error}",
    },
    "he": {
        "started": "משקה את {name} למשך {minutes} דקות.",
        "plan_started": "מפעיל את {name}.",
        "stopped_all": "ההשקיה נעצרה.",
        "stopped": "{name} נעצר.",
        "skipped": "דילגתי על {count} השקיות היום.",
        "nothing_today": "אין עוד השקיות מתוכננות להיום.",
        "paused": "ההשקיה מושהית ל־{days} ימים.",
        "no_zone": "אני לא מכיר אזור בשם {name}.",
        "no_plan": "אני לא מכיר תוכנית השקיה בשם {name}.",
        "bad_number": "לא הבנתי את המספר.",
        "idle": "שום דבר לא משקה כרגע.",
        "running": "משקה עכשיו: {names}.",
        "failed": "זה לא הצליח: {error}",
    },
}

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "forty five": 45, "sixty": 60,
    "eins": 1, "ein": 1, "eine": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6, "sieben": 7,
    "acht": 8, "neun": 9, "zehn": 10, "fünfzehn": 15, "zwanzig": 20, "dreißig": 30,
    "אחת": 1, "אחד": 1, "שתיים": 2, "שניים": 2, "שני": 2, "שתי": 2, "שלוש": 3, "שלושה": 3, "ארבע": 4,
    "חמש": 5, "חמישה": 5, "שש": 6, "שבע": 7, "שמונה": 8, "תשע": 9, "עשר": 10, "עשרה": 10,
    "רבע שעה": 15, "חמש עשרה": 15, "עשרים": 20, "חצי שעה": 30, "שלושים": 30,
}

_TRAILING_MINUTES = re.compile(
    r"^(.*?)\s+(?:for\s+|für\s+|למשך\s+)?(\d+|[^\s]+)\s*(?:minutes?|minuten?|דקות|דק׳|דק)$", re.IGNORECASE
)
_ARTICLE = re.compile(r"^(the|den|die|das|dem|ה(?=\S{2,}))\s*", re.IGNORECASE)


def _norm(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[?!.,״\"']", "", text)
    return re.sub(r"\s+", " ", text)


def parse_number(text: Any) -> Optional[int]:
    t = _norm(str(text))
    m = re.search(r"\d+", t)
    if m:
        return int(m.group(0))
    return WORD_NUMBERS.get(t)


def best_match(name: str, items: list[tuple[str, str]]) -> Optional[str]:
    """items: [(key, label)]. Exact, then without a leading article/ה, then containment."""
    n = _norm(name)
    variants = {n, _ARTICLE.sub("", n)}
    for key, label in items:
        if _norm(label) in variants:
            return key
    for key, label in items:
        lab = _norm(label)
        if lab and any(lab in v or (len(v) >= 3 and v in lab) for v in variants):
            return key
    return None


class VoiceCommands:
    def __init__(self, hass: HomeAssistant, entry, data: dict):
        self.hass = hass
        self.entry = entry
        self.data = data
        self._unsubs: list[CALLBACK_TYPE] = []

    @property
    def scheduler(self):
        return self.data["scheduler"]

    @property
    def store(self):
        return self.data["store"]

    async def async_start(self) -> None:
        try:
            from homeassistant.helpers.trigger import async_initialize_triggers, async_validate_trigger_config
        except ImportError:
            LOG.debug("trigger helpers unavailable; voice commands disabled")
            return
        for (lang, action), sentences in SENTENCES.items():
            try:
                conf = await async_validate_trigger_config(
                    self.hass, [{"platform": "conversation", "command": sentences}]
                )
                unsub = await async_initialize_triggers(
                    self.hass, conf, self._make_action(lang, action), DOMAIN,
                    f"{DOMAIN} voice {lang} {action}", LOG.log,
                )
            except Exception as e:  # conversation not loaded, or an older HA
                LOG.debug("voice %s/%s not registered: %s", lang, action, e)
                continue
            if unsub:
                self._unsubs.append(unsub)
        LOG.debug("registered %d voice command groups", len(self._unsubs))

    def async_stop(self) -> None:
        while self._unsubs:
            self._unsubs.pop()()

    def _make_action(self, lang: str, action: str) -> Callable:
        async def _run(run_variables: dict, context=None, **kwargs):
            slots = (run_variables.get("trigger") or {}).get("slots") or {}
            try:
                text = await self.async_handle(lang, action, slots)
            except Exception as e:
                LOG.warning("voice %s failed: %s", action, e)
                text = self._reply(lang, "failed", error=str(e))
            return _conversation_result(text)
        return _run

    def _reply(self, lang: str, key: str, **kw) -> str:
        return REPLIES.get(lang, REPLIES["en"])[key].format(**kw)

    def _zones(self) -> list[tuple[str, str]]:
        return [(v["entity_id"], v.get("label") or v["entity_id"]) for v in self.store.valves]

    def _plans(self) -> list[tuple[str, str]]:
        return [(c["id"], c.get("name") or c["id"]) for c in self.store.cycles]

    async def async_handle(self, lang: str, action: str, slots: dict) -> str:
        sch = self.scheduler
        if action in ("run_zone", "run_zone_minutes", "stop_zone"):
            name = str(slots.get("zone") or "")
            if action == "run_zone":
                # "water the lawn for 10 minutes" can also land here with the minutes inside {zone}.
                m = _TRAILING_MINUTES.match(_norm(name))
                if m and parse_number(m.group(2)):
                    name, action = m.group(1), "run_zone_minutes"
                    slots = {**slots, "minutes": m.group(2)}
            zone = best_match(name, self._zones())
            if action == "stop_zone" and not zone:
                plan = best_match(name, self._plans())
                if plan:
                    await sch.async_stop_cycle(plan)
                    return self._reply(lang, "stopped", name=dict(self._plans())[plan])
            if not zone:
                return self._reply(lang, "no_zone", name=name)
            label = dict(self._zones())[zone]
            if action == "stop_zone":
                await sch.async_stop_valve(zone)
                return self._reply(lang, "stopped", name=label)
            if action == "run_zone_minutes":
                minutes = parse_number(slots.get("minutes"))
                if not minutes:
                    return self._reply(lang, "bad_number")
            else:
                minutes = int((self.store.get_valve(zone) or {}).get("default_duration_min") or 10)
            await sch.async_run_valve(zone, minutes, source="voice")
            return self._reply(lang, "started", name=label, minutes=minutes)
        if action == "run_plan":
            name = str(slots.get("plan") or "")
            plan = best_match(name, self._plans())
            if not plan:
                return self._reply(lang, "no_plan", name=name)
            await sch.async_run_cycle(plan, source="voice")
            return self._reply(lang, "plan_started", name=dict(self._plans())[plan])
        if action == "stop_all":
            await sch.async_stop_all("voice")
            return self._reply(lang, "stopped_all")
        if action == "skip_today":
            occs = await sch.async_skip_day()
            return self._reply(lang, "skipped", count=len(occs)) if occs else self._reply(lang, "nothing_today")
        if action == "pause_days":
            days = parse_number(slots.get("days"))
            if not days or days > 30:
                return self._reply(lang, "bad_number")
            until = int(time.time()) + days * 86400
            self.hass.config_entries.async_update_entry(
                self.entry, options={**self.entry.options, CONF_RAIN_DELAY_UNTIL: until}
            )
            self.hass.bus.async_fire(EVENT_RAIN_DELAY_SET, {"until": until, "hours": days * 24})
            return self._reply(lang, "paused", days=days)
        if action == "status":
            names = [dict(self._zones()).get(e, e) for e in sch.active]
            return self._reply(lang, "running", names=", ".join(names)) if names else self._reply(lang, "idle")
        return self._reply(lang, "failed", error=action)


def _conversation_result(text: str):
    try:
        from homeassistant.helpers.script import ScriptRunResult
        return ScriptRunResult(conversation_response=text, service_response=None, variables={})
    except Exception:
        return None
