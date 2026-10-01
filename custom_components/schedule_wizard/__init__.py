"""Schedule Wizard integration."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import time
from collections import deque
from typing import Any

import voluptuous as vol

from aiohttp import web

from homeassistant.components import panel_custom, webhook, websocket_api
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, Platform
from homeassistant.core import CoreState, HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_call_later
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    INTERVAL_MAX_DAYS,
    INTERVAL_MIN_DAYS,
    REPEAT_INTERVAL,
    REPEAT_WEEKDAYS,
    CONF_CALENDAR_ENTITY,
    CONF_CALENDAR_LOOKAHEAD,
    CONF_DEFAULT_DURATION,
    CONF_NOTIFY_EVENTS,
    CONF_NOTIFY_TARGETS,
    CONF_POLL_INTERVAL,
    CONF_RAIN_ATTRIBUTE,
    CONF_RAIN_ENTITY,
    CONF_RAIN_SKIP_STATES,
    CONF_RAIN_THRESHOLD,
    CONF_ALLOW_CONCURRENT_CYCLES,
    CONF_FAIL_DETECTION_ENABLED,
    CONF_FAIL_DETECTION_SECONDS,
    CONF_MASTER_VALVE_ENTITY,
    CONF_MASTER_VALVE_PRE_OPEN_SEC,
    CONF_MOISTURE_ATTRIBUTE,
    CONF_MOISTURE_ENTITY,
    CONF_MOISTURE_THRESHOLD_SKIP_ABOVE,
    CONF_RAIN_DELAY_UNTIL,
    CONF_SEASONAL_ENABLED,
    CONF_SEASONAL_MAX_PCT,
    CONF_SEASONAL_MIN_PCT,
    CONF_SEASONAL_TEMP_ATTRIBUTE,
    CONF_SEASONAL_TEMP_ENTITY,
    CONF_SEASONAL_TEMP_HIGH,
    CONF_SEASONAL_TEMP_LOW,
    CONF_FLOW_ATTRIBUTE,
    CONF_FLOW_DELAY_SEC,
    CONF_FLOW_ENTITY,
    CONF_FLOW_LEAK_THRESHOLD,
    CONF_FLOW_MAX_RUNNING,
    CONF_FLOW_STOP_ALL,
    CONF_FORECAST_ENTITY,
    CONF_FORECAST_HOURS,
    CONF_FORECAST_SKIP_MM,
    CONF_INTERLEAVE_SOAK,
    CONF_REMINDER_MINUTES,
    CONF_VOICE_ENABLED,
    CONDITION_OPERATORS,
    DEFAULT_DURATION,
    DEFAULT_OPTIONS,
    DOMAIN,
    EVENT_RAIN_DELAY_SET,
    MAX_RUN_MINUTES,
    NOTIFY_EVENTS,
    SERVICE_ADD_CYCLE,
    SERVICE_ADD_SCHEDULE,
    SERVICE_ADD_VALVE,
    SERVICE_CLEAR_RAIN_DELAY,
    SERVICE_LIST,
    SERVICE_PAUSE_CYCLE,
    SERVICE_RAIN_DELAY,
    SERVICE_REMOVE_CYCLE,
    SERVICE_REMOVE_SCHEDULE,
    SERVICE_REMOVE_VALVE,
    SERVICE_RESUME_CYCLE,
    SERVICE_RUN_CYCLE,
    SERVICE_RUN_VALVE,
    SERVICE_SKIP_DAY,
    SERVICE_SKIP_NEXT,
    SERVICE_RUN_SCHEDULE,
    SERVICE_STOP_ALL,
    SERVICE_UNSKIP,
    SERVICE_STOP_CYCLE,
    SERVICE_STOP_VALVE,
    SERVICE_UPDATE_CYCLE,
    SERVICE_UPDATE_SCHEDULE,
    SIGNAL_CONFIG_CHANGED,
    SUPPORTED_DOMAINS,
)
from . import issues, planner
from .scheduler import Scheduler
from .storage import WizardStore
from .voice import VoiceCommands
from .const import MAX_CYCLES, MAX_NAME_LENGTH, MAX_SCHEDULES, MAX_TEXT_LENGTH, MAX_VALVES

NAME = vol.All(cv.string, vol.Length(max=MAX_NAME_LENGTH, msg=f"at most {MAX_NAME_LENGTH} characters"))
TEXT = vol.All(cv.string, vol.Length(max=MAX_TEXT_LENGTH, msg=f"at most {MAX_TEXT_LENGTH} characters"))

LOG = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR, Platform.SWITCH, Platform.BUTTON, Platform.BINARY_SENSOR, Platform.CALENDAR,
]

PANEL_URL_PATH = "schedule-wizard"
PANEL_STATIC_URL = "/schedule_wizard_panel"
PANEL_REGISTERED_KEY = f"{DOMAIN}_panel_registered"
WS_COMMANDS_REGISTERED_KEY = f"{DOMAIN}_ws_registered"
CARD_RESOURCE_REGISTERED_KEY = f"{DOMAIN}_card_registered"
CARD_RESOURCE_URL = f"{PANEL_STATIC_URL}/card.js"
# Webhook flood limits (SEC-008): calls per minute per entry, and the window in which a repeat of the
# same action for the same zone is answered without acting again.
WEBHOOK_MAX_PER_MINUTE = 30
WEBHOOK_REPEAT_SECONDS = 2
# get_state keys that change while watering; a poll that sends the last `rev` gets only these (PERF-001).
LIVE_STATE_KEYS = (
    "active", "active_cycles", "soaking", "flow", "forecast", "seasonal", "water_total_l", "rain_delay_until", "now",
)


def _state_rev(state: dict[str, Any]) -> str:
    """Fingerprint of get_state without the live keys and the per-second next-run countdowns."""
    heavy = {k: v for k, v in state.items() if k not in LIVE_STATE_KEYS}
    heavy["valves"] = [
        {**v, "next_run": {k: x for k, x in v["next_run"].items() if k != "in_seconds"} if v.get("next_run") else None}
        for v in heavy.get("valves") or []
    ]
    raw = json.dumps(heavy, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _entity_in_supported_domain(value: str) -> str:
    value = cv.entity_id(value)
    domain = value.split(".")[0]
    if domain not in SUPPORTED_DOMAINS:
        raise vol.Invalid(f"unsupported domain {domain}")
    return value


def _hhmm(value: str) -> str:
    if not isinstance(value, str) or ":" not in value:
        raise vol.Invalid("time must be HH:MM")
    h, m = value.split(":", 1)
    try:
        hi, mi = int(h), int(m)
    except ValueError:
        raise vol.Invalid("time must be HH:MM")
    if not (0 <= hi < 24 and 0 <= mi < 60):
        raise vol.Invalid("time out of range")
    return f"{hi:02d}:{mi:02d}"


SCHEMA_RUN = vol.Schema({
    vol.Required("entity_id"): _entity_in_supported_domain,
    vol.Optional("duration_minutes"): vol.All(int, vol.Range(min=1, max=1440)),
})

SCHEMA_STOP = vol.Schema({
    vol.Required("entity_id"): _entity_in_supported_domain,
})

SCHEMA_ADD_VALVE = vol.Schema({
    vol.Required("entity_id"): _entity_in_supported_domain,
    vol.Required("label"): NAME,
    vol.Optional("default_duration_minutes", default=DEFAULT_DURATION): vol.All(int, vol.Range(min=1, max=1440)),
    vol.Optional("enabled", default=True): cv.boolean,
    vol.Optional("soak_run_minutes"): vol.All(int, vol.Range(min=0, max=1440)),
    vol.Optional("soak_pause_minutes"): vol.All(int, vol.Range(min=0, max=1440)),
    vol.Optional("moisture_entity"): vol.Any(cv.entity_id, ""),
    vol.Optional("moisture_attribute"): TEXT,
    vol.Optional("moisture_threshold"): vol.Any(vol.Coerce(float), None),
    vol.Optional("rain_exempt"): cv.boolean,
    vol.Optional("flow_rate_lpm"): vol.Any(vol.All(vol.Coerce(float), vol.Range(min=0, max=10000)), None),
})

VALVE_FIELD_MAP = {
    "soak_run_minutes": "soak_run_min",
    "soak_pause_minutes": "soak_pause_min",
    "moisture_entity": "moisture_entity",
    "moisture_attribute": "moisture_attribute",
    "moisture_threshold": "moisture_threshold",
    "rain_exempt": "rain_exempt",
    "flow_rate_lpm": "flow_rate_lpm",
}

SCHEMA_CONDITIONS = vol.All(cv.ensure_list, [vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("attribute", default=""): TEXT,
    vol.Optional("operator", default="equals"): vol.In(CONDITION_OPERATORS),
    vol.Required("value"): vol.Any(TEXT, vol.Coerce(float)),
})], vol.Length(max=10))

SCHEMA_REMOVE_VALVE = vol.Schema({
    vol.Required("entity_id"): _entity_in_supported_domain,
})

SCHEMA_ADD_SCHEDULE = vol.Schema({
    vol.Optional("valve_entity_id"): _entity_in_supported_domain,
    vol.Optional("cycle_id"): cv.string,
    vol.Required("time"): _hhmm,
    vol.Optional("duration_minutes", default=1): vol.All(int, vol.Range(min=1, max=1440)),
vol.Optional("days"): vol.All(cv.ensure_list, [vol.In(["mon", "tue", "wed", "thu", "fri", "sat", "sun"])], vol.Length(min=1, msg="pick at least one day")),
    vol.Optional("every_n_days"): vol.All(vol.Coerce(int), vol.Range(min=INTERVAL_MIN_DAYS, max=INTERVAL_MAX_DAYS, msg="every_n_days must be 2 to 30")),
    vol.Optional("start_date"): cv.date,
    vol.Optional("name", default=""): NAME,
    vol.Optional("enabled", default=True): cv.boolean,
    vol.Optional("conditions"): SCHEMA_CONDITIONS,
})

SCHEMA_ADD_CYCLE = vol.Schema({
    vol.Required("name"): NAME,
    vol.Required("steps"): vol.All(
        cv.ensure_list,
        [vol.Schema({
            vol.Required("entity_id"): _entity_in_supported_domain,
            vol.Required("duration_minutes"): vol.All(int, vol.Range(min=1, max=1440)),
        })],
        vol.Length(min=1, max=64),
    ),
    vol.Optional("enabled", default=True): cv.boolean,
})

SCHEMA_UPDATE_CYCLE = vol.Schema({
    vol.Required("cycle_id"): cv.string,
    vol.Optional("name"): NAME,
    vol.Optional("steps"): vol.All(
        cv.ensure_list,
        [vol.Schema({
            vol.Required("entity_id"): _entity_in_supported_domain,
            vol.Required("duration_minutes"): vol.All(int, vol.Range(min=1, max=1440)),
        })],
        vol.Length(min=1, max=64),
    ),
    vol.Optional("enabled"): cv.boolean,
})

SCHEMA_REMOVE_CYCLE = vol.Schema({
    vol.Required("cycle_id"): cv.string,
})

SCHEMA_RUN_CYCLE = vol.Schema({
    vol.Required("cycle_id"): cv.string,
})

SCHEMA_STOP_CYCLE = vol.Schema({
    vol.Required("cycle_id"): cv.string,
})

SCHEMA_RAIN_DELAY = vol.Schema({
    vol.Required("hours"): vol.All(vol.Any(int, float), vol.Range(min=0.5, max=720)),
    vol.Optional("entity_id"): vol.All(cv.ensure_list, [_entity_in_supported_domain]),
})

SCHEMA_CLEAR_RAIN_DELAY = vol.Schema({
    vol.Optional("entity_id"): vol.All(cv.ensure_list, [_entity_in_supported_domain]),
})

SCHEMA_NO_ARGS = vol.Schema({})

SCHEMA_SKIP_NEXT = vol.Schema({
    vol.Required("schedule_id"): cv.string,
})

SCHEMA_SKIP_DAY = vol.Schema({
    vol.Optional("date"): cv.date,
})

SCHEMA_UNSKIP = vol.Schema({
    vol.Required("schedule_id"): cv.string,
    vol.Required("date"): cv.date,
})

SCHEMA_PAUSE_RESUME_CYCLE = vol.Schema({
    vol.Required("cycle_id"): cv.string,
})

SCHEMA_REMOVE_SCHEDULE = vol.Schema({
    vol.Required("schedule_id"): cv.string,
})

SCHEMA_UPDATE_SCHEDULE = vol.Schema({
    vol.Required("schedule_id"): cv.string,
    vol.Optional("name"): NAME,
    vol.Optional("time"): _hhmm,
    vol.Optional("duration_minutes"): vol.All(int, vol.Range(min=1, max=1440)),
vol.Optional("days"): vol.All(cv.ensure_list, [vol.In(["mon", "tue", "wed", "thu", "fri", "sat", "sun"])], vol.Length(min=1, msg="pick at least one day")),
    vol.Optional("every_n_days"): vol.All(vol.Coerce(int), vol.Range(min=INTERVAL_MIN_DAYS, max=INTERVAL_MAX_DAYS, msg="every_n_days must be 2 to 30")),
    vol.Optional("start_date"): cv.date,
    vol.Optional("enabled"): cv.boolean,
    vol.Optional("conditions"): SCHEMA_CONDITIONS,
})

DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

OPTION_KEYS = tuple(k for k in DEFAULT_OPTIONS if k != CONF_RAIN_DELAY_UNTIL)


def _build_options(entry: ConfigEntry) -> dict[str, Any]:
    options = {k: entry.options.get(k, default) for k, default in DEFAULT_OPTIONS.items()}
    master = options.get(CONF_MASTER_VALVE_ENTITY)
    if master and (not isinstance(master, str) or master.strip().split(".")[0] not in SUPPORTED_DOMAINS):
        # Saved before #40: never call a service of another domain (script, automation...) on it.
        LOG.warning("ignoring main valve %s: not a %s entity", master, ", ".join(SUPPORTED_DOMAINS))
        options[CONF_MASTER_VALVE_ENTITY] = ""
    return options


@callback
def _async_register_webhook(hass: HomeAssistant, webhook_id: str, handler) -> None:
    try:
        webhook.async_register(hass, DOMAIN, "Schedule Wizard", webhook_id, handler)
    except ValueError:
        webhook.async_unregister(hass, webhook_id)
        webhook.async_register(hass, DOMAIN, "Schedule Wizard", webhook_id, handler)


def _repeat_fields(data: dict, current: dict | None = None) -> dict[str, Any]:
    """Validate days / every_n_days / start_date of add_schedule or update_schedule (#27)."""
    has_days = "days" in data
    has_n = "every_n_days" in data
    if has_days and has_n:
        raise HomeAssistantError("provide either days or every_n_days, not both")
    if has_days:
        if "start_date" in data:
            raise HomeAssistantError("start_date only applies with every_n_days")
        return {"repeat": REPEAT_WEEKDAYS, "days_mask": _days_to_mask(data["days"])}
    interval_now = bool(current) and current.get("repeat") == REPEAT_INTERVAL
    if has_n or ("start_date" in data and interval_now):
        start = data.get("start_date")
        if start is None and interval_now and current.get("start_date"):
            start_s = current["start_date"]
        else:
            start_s = (start or dt_util.now().date()).isoformat()
        out: dict[str, Any] = {"repeat": REPEAT_INTERVAL, "start_date": start_s}
        out["interval_days"] = int(data["every_n_days"]) if has_n else int(current.get("interval_days") or 0)
        return out
    if "start_date" in data:
        raise HomeAssistantError("start_date only applies with every_n_days")
    if current is None:
        raise HomeAssistantError("either days or every_n_days is required")
    return {}


def _days_to_mask(days: list[str]) -> int:
    mask = 0
    for d in days:
        mask |= 1 << DAY_NAMES.index(d)
    return mask


_INTEGRATION_VERSION_CACHE: str | None = None


def _integration_version_sync() -> str:
    try:
        import json
        with open(os.path.join(os.path.dirname(__file__), "manifest.json"), "r") as f:
            return json.load(f).get("version", "0")
    except Exception:
        return "0"


async def _integration_version(hass: HomeAssistant) -> str:
    global _INTEGRATION_VERSION_CACHE
    if _INTEGRATION_VERSION_CACHE is None:
        _INTEGRATION_VERSION_CACHE = await hass.async_add_executor_job(_integration_version_sync)
    return _INTEGRATION_VERSION_CACHE


async def _async_register_panel(hass: HomeAssistant) -> None:
    if hass.data.get(PANEL_REGISTERED_KEY):
        return
    panel_dir = os.path.join(os.path.dirname(__file__), "www")
    if os.path.isdir(panel_dir):
        await hass.http.async_register_static_paths([
            StaticPathConfig(PANEL_STATIC_URL, panel_dir, False)
        ])
    version = await _integration_version(hass)
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="schedule-wizard-panel",
        frontend_url_path=PANEL_URL_PATH,
        module_url=f"{PANEL_STATIC_URL}/panel.js?v={version}",
        sidebar_title="Schedule Wizard",
        sidebar_icon="mdi:sprinkler-variant",
        require_admin=False,
        config={},
    )
    hass.data[PANEL_REGISTERED_KEY] = True


async def _async_register_card_resource(hass: HomeAssistant) -> None:
    if hass.data.get(CARD_RESOURCE_REGISTERED_KEY):
        return
    try:
        from homeassistant.components.lovelace.resources import ResourceStorageCollection
        lovelace = hass.data.get("lovelace")
        if lovelace and getattr(lovelace, "resources", None):
            resources: ResourceStorageCollection = lovelace.resources
            if resources.store and resources.store.key and not resources.loaded:
                await resources.async_load()
            version = await _integration_version(hass)
            target_url = f"{CARD_RESOURCE_URL}?v={version}"
            items = list(resources.async_items())
            stale = [r for r in items if r.get("url", "").startswith(CARD_RESOURCE_URL) and r.get("url") != target_url]
            for r in stale:
                await resources.async_delete_item(r["id"])
            existing = [r for r in resources.async_items() if r.get("url") == target_url]
            if not existing:
                await resources.async_create_item({"res_type": "module", "url": target_url})
    except Exception as e:
        LOG.debug("card resource auto-register skipped: %s", e)
    hass.data[CARD_RESOURCE_REGISTERED_KEY] = True


def _async_register_ws_commands(hass: HomeAssistant) -> None:
    if hass.data.get(WS_COMMANDS_REGISTERED_KEY):
        return

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_state", vol.Optional("rev"): str})
    @websocket_api.async_response
    async def _ws_get_state(hass_inner, connection, msg):
        domain_data = hass_inner.data.get(DOMAIN, {})
        if not domain_data:
            connection.send_error(msg["id"], "not_loaded", "integration not loaded")
            return
        entry_id = next(iter(domain_data))
        data = domain_data[entry_id]
        store = data["store"]
        scheduler = data["scheduler"]
        options = data["options"]

        controllable = []
        calendars = []
        for s in hass_inner.states.async_all():
            if s.domain in SUPPORTED_DOMAINS:
                controllable.append({
                    "entity_id": s.entity_id,
                    "domain": s.domain,
                    "friendly_name": s.attributes.get("friendly_name", s.entity_id),
                    "state": s.state,
                })
            elif s.domain == "calendar":
                calendars.append({
                    "entity_id": s.entity_id,
                    "friendly_name": s.attributes.get("friendly_name", s.entity_id),
                })
        controllable.sort(key=lambda x: x["friendly_name"].lower())
        calendars.sort(key=lambda x: x["friendly_name"].lower())

        active = [
            {k: v for k, v in r.items() if k != "unsub_close"}
            for r in scheduler.active.values()
        ]
        active_cycles = [
            {k: v for k, v in r.items() if k != "task"}
            for r in scheduler.active_cycles.values()
        ]

        notify_services = sorted(list((hass_inner.services.async_services().get("notify") or {}).keys()))
        try:
            temp_unit = hass_inner.config.units.temperature_unit
        except Exception:
            temp_unit = "°"

        history = store.history
        now_ts = int(time.time())
        week_ago = now_ts - 7 * 24 * 3600
        per_valve_stats: dict[str, dict] = {}
        for h in history:
            vid = h.get("valve_entity_id")
            if not vid:
                continue
            s = per_valve_stats.setdefault(vid, {
                "last_run": None,
                "last_completed": None,
                "runs_7d": 0,
                "total_min_7d": 0,
            })
            if s["last_run"] is None or h["ts"] > s["last_run"]["ts"]:
                s["last_run"] = {
                    "ts": h["ts"], "status": h.get("status", ""),
                    "duration_min": h.get("duration_min", 0), "source": h.get("source", ""),
                }
            if h.get("status") == "completed" and (s["last_completed"] is None or h["ts"] > s["last_completed"]["ts"]):
                s["last_completed"] = {
                    "ts": h["ts"], "duration_min": h.get("duration_min", 0),
                    "source": h.get("source", ""),
                }
            if h["ts"] >= week_ago and h.get("status") in ("completed", "cancelled"):
                s["runs_7d"] += 1
                s["total_min_7d"] += int(h.get("duration_min", 0))

        from datetime import timedelta as _td
        schedules_snapshot = store.schedules
        cycles_snapshot = store.cycles
        cycles_by_id = {c["id"]: c for c in cycles_snapshot}
        now_dt = dt_util.now()

        def _next_run_for(valve_id: str) -> dict | None:
            best = None
            for s in schedules_snapshot:
                if not s.get("enabled"):
                    continue
                duration_for_valve = 0
                matches = False
                if s.get("valve_entity_id") == valve_id:
                    matches = True
                    duration_for_valve = int(s.get("duration_min", 0) or 0)
                elif s.get("cycle_id"):
                    cyc = cycles_by_id.get(s["cycle_id"])
                    if cyc and cyc.get("enabled"):
                        for step in (cyc.get("steps") or []):
                            if step.get("entity_id") == valve_id:
                                matches = True
                                duration_for_valve = int(step.get("duration_min", 0) or 0)
                                break
                if not matches:
                    continue
                fire = planner.next_fire(s, now_dt)
                if fire is None:
                    continue
                delta_sec = int((fire - now_dt).total_seconds())
                if best is None or delta_sec < best["in_seconds"]:
                    best = {
                        "fires_at": int(fire.timestamp()),
                        "in_seconds": delta_sec,
                        "time_label": fire.strftime("%a %H:%M"),
                        "duration_min": duration_for_valve,
                        "schedule_id": s["id"],
                        "cycle_id": s.get("cycle_id") or "",
                    }
            return best

        valves_enriched = []
        for v in store.valves:
            entry = dict(v)
            entry["stats"] = per_valve_stats.get(v["entity_id"], {
                "last_run": None, "last_completed": None,
                "runs_7d": 0, "total_min_7d": 0,
            })
            entry["next_run"] = _next_run_for(v["entity_id"])
            valves_enriched.append(entry)

        is_admin = bool(connection.user and connection.user.is_admin)
        if not is_admin:
            # Secrets for admins only (#35): the webhook id and the notify targets (device names).
            options = {k: v for k, v in options.items() if k != CONF_NOTIFY_TARGETS}

        state = {
            "valves": valves_enriched,
            "schedules": store.schedules,
            "cycles": store.cycles,
            "active": active,
            "active_cycles": active_cycles,
            "soaking": scheduler.soaking,
            "flow": scheduler.flow_status,
            "forecast": scheduler.forecast_status,
            "seasonal": scheduler.seasonal_status,
            "water_total_l": store.water_total_l,
            "week": planner.occurrences(
                store, options, dt_util.start_of_local_day(), dt_util.start_of_local_day() + _td(days=7),
            ),
            "skips": store.skips,
            "history": store.history[:500],
            "options": options,
            "controllable": controllable,
            "calendars": calendars,
            "notify_services": notify_services,
            "notify_events": list(NOTIFY_EVENTS),
            "temperature_unit": temp_unit,
            "rain_delay_until": options.get(CONF_RAIN_DELAY_UNTIL, 0),
            "webhook_id": data.get("webhook_id", "") if is_admin else "",
            "now": int(time.time()),
        }
        rev = _state_rev(state)
        if msg.get("rev") == rev:
            # Nothing but the live part changed since this client's last full copy (PERF-001).
            connection.send_result(msg["id"], {**{k: state[k] for k in LIVE_STATE_KEYS}, "rev": rev, "unchanged": True})
            return
        connection.send_result(msg["id"], {**state, "rev": rev})

    @websocket_api.websocket_command({
        vol.Required("type"): f"{DOMAIN}/update_options",
        vol.Optional(CONF_CALENDAR_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_CALENDAR_LOOKAHEAD): vol.All(int, vol.Range(min=1, max=1440)),
        vol.Optional(CONF_POLL_INTERVAL): vol.All(int, vol.Range(min=10, max=3600)),
        vol.Optional(CONF_DEFAULT_DURATION): vol.All(int, vol.Range(min=1, max=1440)),
        vol.Optional(CONF_RAIN_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_RAIN_SKIP_STATES): vol.Any(str, None),
        vol.Optional(CONF_RAIN_ATTRIBUTE): vol.Any(str, None),
        vol.Optional(CONF_RAIN_THRESHOLD): vol.Any(float, int, None),
        vol.Optional(CONF_NOTIFY_TARGETS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_NOTIFY_EVENTS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_SEASONAL_ENABLED): cv.boolean,
        vol.Optional(CONF_SEASONAL_TEMP_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_SEASONAL_TEMP_ATTRIBUTE): vol.Any(str, None),
        vol.Optional(CONF_SEASONAL_TEMP_LOW): vol.Any(float, int, None),
        vol.Optional(CONF_SEASONAL_TEMP_HIGH): vol.Any(float, int, None),
        vol.Optional(CONF_SEASONAL_MIN_PCT): vol.Any(float, int, None),
        vol.Optional(CONF_SEASONAL_MAX_PCT): vol.Any(float, int, None),
        vol.Optional(CONF_ALLOW_CONCURRENT_CYCLES): cv.boolean,
        vol.Optional(CONF_MOISTURE_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_MOISTURE_ATTRIBUTE): vol.Any(str, None),
        vol.Optional(CONF_MOISTURE_THRESHOLD_SKIP_ABOVE): vol.Any(float, int, None),
        vol.Optional(CONF_MASTER_VALVE_ENTITY): vol.Any(None, "", _entity_in_supported_domain),
        vol.Optional(CONF_MASTER_VALVE_PRE_OPEN_SEC): vol.All(int, vol.Range(min=0, max=600)),
        vol.Optional(CONF_FAIL_DETECTION_ENABLED): cv.boolean,
        vol.Optional(CONF_FAIL_DETECTION_SECONDS): vol.All(int, vol.Range(min=1, max=120)),
        vol.Optional(CONF_FLOW_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_FLOW_ATTRIBUTE): vol.Any(str, None),
        vol.Optional(CONF_FLOW_LEAK_THRESHOLD): vol.Any(float, int, None),
        vol.Optional(CONF_FLOW_MAX_RUNNING): vol.Any(float, int, None),
        vol.Optional(CONF_FLOW_DELAY_SEC): vol.All(int, vol.Range(min=5, max=3600)),
        vol.Optional(CONF_FLOW_STOP_ALL): cv.boolean,
        vol.Optional(CONF_REMINDER_MINUTES): vol.All(int, vol.Range(min=0, max=720)),
        vol.Optional(CONF_VOICE_ENABLED): cv.boolean,
        vol.Optional(CONF_FORECAST_ENTITY): vol.Any(str, None),
        vol.Optional(CONF_FORECAST_SKIP_MM): vol.Any(float, int, None),
        vol.Optional(CONF_FORECAST_HOURS): vol.All(int, vol.Range(min=1, max=72)),
        vol.Optional(CONF_INTERLEAVE_SOAK): cv.boolean,
    })
    @websocket_api.require_admin
    @websocket_api.async_response
    async def _ws_update_options(hass_inner, connection, msg):
        domain_data = hass_inner.data.get(DOMAIN, {})
        if not domain_data:
            connection.send_error(msg["id"], "not_loaded", "integration not loaded")
            return
        entry_id = next(iter(domain_data))
        entry = hass_inner.config_entries.async_get_entry(entry_id)
        if not entry:
            connection.send_error(msg["id"], "no_entry", "entry not found")
            return
        master = msg.get(CONF_MASTER_VALVE_ENTITY)
        if master and master != entry.options.get(CONF_MASTER_VALVE_ENTITY) and hass_inner.states.get(master) is None:
            # An unchanged master valve that has since gone missing must not block saving (#40).
            connection.send_error(msg["id"], "invalid_format", f"main valve {master} not found")
            return
        new_options = dict(entry.options)
        for key in OPTION_KEYS:
            if key in msg:
                new_options[key] = msg[key]
        hass_inner.config_entries.async_update_entry(entry, options=new_options)
        connection.send_result(msg["id"], {"options": new_options})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/rotate_webhook"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def _ws_rotate_webhook(hass_inner, connection, msg):
        """Replace the webhook id; the old URL stops working at once (#35)."""
        domain_data = hass_inner.data.get(DOMAIN, {})
        if not domain_data:
            connection.send_error(msg["id"], "not_loaded", "integration not loaded")
            return
        entry_id = next(iter(domain_data))
        entry = hass_inner.config_entries.async_get_entry(entry_id)
        if not entry:
            connection.send_error(msg["id"], "no_entry", "entry not found")
            return
        data = domain_data[entry_id]
        old_id = data.get("webhook_id")
        new_id = secrets.token_hex(16)
        if old_id:
            try:
                webhook.async_unregister(hass_inner, old_id)
            except Exception:
                pass
        _async_register_webhook(hass_inner, new_id, data["webhook_handler"])
        data["webhook_id"] = new_id
        hass_inner.config_entries.async_update_entry(entry, data={**entry.data, "webhook_id": new_id})
        connection.send_result(msg["id"], {"webhook_id": new_id})

    websocket_api.async_register_command(hass, _ws_get_state)
    websocket_api.async_register_command(hass, _ws_update_options)
    websocket_api.async_register_command(hass, _ws_rotate_webhook)
    hass.data[WS_COMMANDS_REGISTERED_KEY] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = WizardStore(hass)
    await store.async_load()

    options = _build_options(entry)

    scheduler = Scheduler(hass, store, options)
    await scheduler.async_start()

    webhook_id = entry.data.get("webhook_id")
    if not webhook_id:
        webhook_id = secrets.token_hex(16)
        hass.config_entries.async_update_entry(entry, data={**entry.data, "webhook_id": webhook_id})

    webhook_calls: deque[float] = deque()
    webhook_last: dict[tuple, float] = {}

    async def _webhook_handler(hass_inner: HomeAssistant, wh_id: str, request: web.Request) -> web.Response:
        try:
            now_mono = time.monotonic()
            while webhook_calls and now_mono - webhook_calls[0] >= 60:
                webhook_calls.popleft()
            if len(webhook_calls) >= WEBHOOK_MAX_PER_MINUTE:
                retry = max(1, int(60 - (now_mono - webhook_calls[0])) + 1)
                return web.json_response(
                    {"error": "too many requests"}, status=429, headers={"Retry-After": str(retry)},
                )
            webhook_calls.append(now_mono)

            def _repeat(key: tuple) -> bool:
                """True when the same action for the same zone was done moments ago; else claim it now."""
                for old in [k for k, t in webhook_last.items() if now_mono - t >= WEBHOOK_REPEAT_SECONDS]:
                    webhook_last.pop(old, None)
                if key in webhook_last:
                    return True
                webhook_last[key] = now_mono
                return False

            async def _act(key: tuple, call) -> None:
                try:
                    await call
                except BaseException:
                    webhook_last.pop(key, None)  # a failed action may be retried at once
                    raise

            try:
                payload = await request.json()
            except Exception:
                payload = dict(await request.post())
            if not isinstance(payload, dict):
                return web.json_response({"error": "invalid payload"}, status=400)
            action = payload.get("action") or "run"
            if not isinstance(action, str) or action.strip().lower() not in ("run", "stop"):
                return web.json_response({"error": "action must be run or stop"}, status=400)
            action = action.strip().lower()
            entity_id = payload.get("entity_id")
            if not entity_id:
                return web.json_response({"error": "entity_id required"}, status=400)
            try:
                entity_id = _entity_in_supported_domain(entity_id)
            except vol.Invalid:
                return web.json_response({"error": "invalid entity_id"}, status=400)
            # Only zones set up in Schedule Wizard (#34); runs only while their entity exists (#37).
            valve = store.get_valve(entity_id)
            if not valve:
                return web.json_response({"error": "unknown zone"}, status=404)
            if action == "stop":
                if _repeat(("stop", entity_id)):
                    return web.json_response({"ok": True, "action": "stop", "entity_id": entity_id, "duplicate": True})
                await _act(("stop", entity_id), scheduler.async_stop_valve(entity_id))
                return web.json_response({"ok": True, "action": "stop", "entity_id": entity_id})
            if hass_inner.states.get(entity_id) is None:
                return web.json_response({"error": "unknown zone"}, status=404)
            if not valve.get("enabled", True):
                return web.json_response({"error": "zone disabled"}, status=409)
            duration = payload.get("duration_minutes")
            if duration is None:
                duration = valve["default_duration_min"]
            try:
                duration = max(1, min(MAX_RUN_MINUTES, int(duration)))
            except (TypeError, ValueError, OverflowError):
                return web.json_response({"error": "duration_minutes must be an integer"}, status=400)
            if _repeat(("run", entity_id, duration)):
                return web.json_response({
                    "ok": True, "action": "run", "entity_id": entity_id, "duration_minutes": duration, "duplicate": True,
                })
            await _act(("run", entity_id, duration), scheduler.async_run_valve(entity_id, duration, source="webhook"))
            return web.json_response({"ok": True, "action": "run", "entity_id": entity_id, "duration_minutes": duration})
        except Exception:
            LOG.exception("webhook handler failed")
            return web.json_response({"error": "internal error"}, status=500)

    _async_register_webhook(hass, webhook_id, _webhook_handler)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "store": store,
        "scheduler": scheduler,
        "options": options,
        "webhook_id": webhook_id,
        "webhook_handler": _webhook_handler,
    }

    async def _svc_run(call: ServiceCall) -> None:
        entity_id = call.data["entity_id"]
        duration = call.data.get("duration_minutes")
        if duration is None:
            valve = store.get_valve(entity_id)
            duration = valve["default_duration_min"] if valve else int(options[CONF_DEFAULT_DURATION])
        try:
            await scheduler.async_run_valve(entity_id, int(duration), source="service")
        except Exception as e:
            raise HomeAssistantError(str(e)) from e

    async def _svc_stop(call: ServiceCall) -> None:
        await scheduler.async_stop_valve(call.data["entity_id"])

    async def _svc_add_valve(call: ServiceCall) -> None:
        extra = {dst: call.data[src] for src, dst in VALVE_FIELD_MAP.items() if src in call.data}
        if not store.get_valve(call.data["entity_id"]) and len(store.valves) >= MAX_VALVES:
            raise HomeAssistantError(f"at most {MAX_VALVES} zones")
        await store.async_upsert_valve(
            call.data["entity_id"],
            call.data["label"],
            int(call.data.get("default_duration_minutes", DEFAULT_DURATION)),
            bool(call.data.get("enabled", True)),
            **extra,
        )

    async def _svc_remove_valve(call: ServiceCall) -> None:
        await store.async_remove_valve(call.data["entity_id"])
        await scheduler.async_stop_valve(call.data["entity_id"])

    async def _svc_add_schedule(call: ServiceCall) -> ServiceResponse:
        valve_entity_id = call.data.get("valve_entity_id")
        cycle_id = call.data.get("cycle_id")
        if not valve_entity_id and not cycle_id:
            raise HomeAssistantError("either valve_entity_id or cycle_id is required")
        if valve_entity_id and cycle_id:
            raise HomeAssistantError("provide exactly one of valve_entity_id or cycle_id")
        if cycle_id and not store.get_cycle(cycle_id):
            raise HomeAssistantError("cycle not found")
        if valve_entity_id and not store.get_valve(valve_entity_id):
            raise HomeAssistantError("valve not registered: add it with add_valve first")
        if len(store.schedules) >= MAX_SCHEDULES:
            raise HomeAssistantError(f"at most {MAX_SCHEDULES} watering times")
        repeat = _repeat_fields(call.data)
        sched = await store.async_add_schedule(
            valve_entity_id=valve_entity_id or None,
            cycle_id=cycle_id or None,
            days_mask=repeat.get("days_mask", 0),
            repeat=repeat["repeat"],
            interval_days=repeat.get("interval_days", 0),
            start_date=repeat.get("start_date", ""),
            time_hhmm=call.data["time"],
            duration_min=int(call.data.get("duration_minutes", 1)),
            name=call.data.get("name", ""),
            enabled=bool(call.data.get("enabled", True)),
            conditions=call.data.get("conditions"),
        )
        return {"schedule": sched}

    async def _svc_add_cycle(call: ServiceCall) -> ServiceResponse:
        if len(store.cycles) >= MAX_CYCLES:
            raise HomeAssistantError(f"at most {MAX_CYCLES} plans")
        steps = [
            {"entity_id": s["entity_id"], "duration_min": int(s["duration_minutes"])}
            for s in call.data["steps"]
        ]
        cycle = await store.async_add_cycle(
            name=call.data["name"],
            steps=steps,
            enabled=bool(call.data.get("enabled", True)),
        )
        return {"cycle": cycle}

    async def _svc_update_cycle(call: ServiceCall) -> ServiceResponse:
        fields: dict[str, Any] = {}
        if "name" in call.data:
            fields["name"] = call.data["name"]
        if "enabled" in call.data:
            fields["enabled"] = bool(call.data["enabled"])
        if "steps" in call.data:
            fields["steps"] = [
                {"entity_id": s["entity_id"], "duration_min": int(s["duration_minutes"])}
                for s in call.data["steps"]
            ]
        cycle = await store.async_update_cycle(call.data["cycle_id"], **fields)
        if cycle is None:
            raise HomeAssistantError("cycle not found")
        return {"cycle": cycle}

    async def _svc_remove_cycle(call: ServiceCall) -> None:
        cycle_id = call.data["cycle_id"]
        await scheduler.async_stop_cycle(cycle_id, note="removed")
        await store.async_remove_cycle(cycle_id)

    async def _svc_run_cycle(call: ServiceCall) -> None:
        try:
            await scheduler.async_run_cycle(call.data["cycle_id"], source="service")
        except Exception as e:
            raise HomeAssistantError(str(e)) from e

    async def _svc_stop_cycle(call: ServiceCall) -> None:
        await scheduler.async_stop_cycle(call.data["cycle_id"])

    async def _svc_stop_all(call: ServiceCall) -> None:
        await scheduler.async_stop_all()

    async def _svc_skip_next(call: ServiceCall) -> ServiceResponse:
        if not store.get_schedule(call.data["schedule_id"]):
            raise HomeAssistantError("schedule not found")
        occ = await scheduler.async_skip_next(call.data["schedule_id"])
        return {"skipped": occ}

    async def _svc_skip_day(call: ServiceCall) -> ServiceResponse:
        day = call.data.get("date")
        try:
            occs = await scheduler.async_skip_day(day.isoformat() if day else None)
        except ValueError as e:
            raise HomeAssistantError(str(e)) from e
        return {"skipped": occs}

    async def _svc_run_schedule(call: ServiceCall) -> None:
        try:
            await scheduler.async_run_schedule_now(call.data["schedule_id"], source="manual")
        except Exception as e:
            raise HomeAssistantError(str(e)) from e

    async def _svc_unskip(call: ServiceCall) -> None:
        await store.async_remove_skip(call.data["schedule_id"], call.data["date"].isoformat())

    async def _svc_rain_delay(call: ServiceCall) -> None:
        hours = float(call.data["hours"])
        until_ts = int(time.time()) + int(hours * 3600)
        entity_ids = call.data.get("entity_id")
        if entity_ids:
            await _async_valve_rain_delay(entity_ids, until_ts, hours)
            return
        new_options = dict(entry.options)
        new_options[CONF_RAIN_DELAY_UNTIL] = until_ts
        hass.config_entries.async_update_entry(entry, options=new_options)
        hass.bus.async_fire(EVENT_RAIN_DELAY_SET, {"until": until_ts, "hours": hours})
        await scheduler._notify("rain_delay", "Schedule Wizard", f"Rain delay set for {hours}h")

    async def _async_valve_rain_delay(entity_ids: list[str], until_ts: int, hours: float) -> None:
        missing = [e for e in entity_ids if not store.get_valve(e)]
        if missing:
            raise HomeAssistantError(f"valve not registered: {', '.join(missing)}")
        await store.async_set_valves_rain_delay(entity_ids, until_ts)
        hass.bus.async_fire(EVENT_RAIN_DELAY_SET, {"until": until_ts, "hours": hours, "entity_ids": entity_ids})
        labels = ", ".join(scheduler._entity_label(e) for e in entity_ids)
        text = f"Rain delay set for {hours}h: {labels}" if until_ts else f"Rain delay cleared: {labels}"
        await scheduler._notify("rain_delay", "Schedule Wizard", text)

    async def _svc_clear_rain_delay(call: ServiceCall) -> None:
        entity_ids = call.data.get("entity_id")
        if entity_ids:
            await _async_valve_rain_delay(entity_ids, 0, 0)
            return
        new_options = dict(entry.options)
        new_options[CONF_RAIN_DELAY_UNTIL] = 0
        hass.config_entries.async_update_entry(entry, options=new_options)
        hass.bus.async_fire(EVENT_RAIN_DELAY_SET, {"until": 0, "hours": 0})
        await scheduler._notify("rain_delay", "Schedule Wizard", "Rain delay cleared")

    async def _svc_pause_cycle(call: ServiceCall) -> None:
        await scheduler.async_pause_cycle(call.data["cycle_id"])

    async def _svc_resume_cycle(call: ServiceCall) -> None:
        await scheduler.async_resume_cycle(call.data["cycle_id"])

    async def _svc_remove_schedule(call: ServiceCall) -> None:
        await store.async_remove_schedule(call.data["schedule_id"])

    async def _svc_update_schedule(call: ServiceCall) -> ServiceResponse:
        fields: dict[str, Any] = {}
        if "name" in call.data:
            fields["name"] = call.data["name"]
        if "time" in call.data:
            fields["time_hhmm"] = call.data["time"]
        if "duration_minutes" in call.data:
            fields["duration_min"] = int(call.data["duration_minutes"])
        current = store.get_schedule(call.data["schedule_id"])
        if current is None:
            raise HomeAssistantError("schedule not found")
        fields.update(_repeat_fields(call.data, current))
        if "enabled" in call.data:
            fields["enabled"] = bool(call.data["enabled"])
        if "conditions" in call.data:
            fields["conditions"] = call.data["conditions"]
        sched = await store.async_update_schedule(call.data["schedule_id"], **fields)
        if sched is None:
            raise HomeAssistantError("schedule not found")
        return {"schedule": sched}

    async def _svc_list(call: ServiceCall) -> ServiceResponse:
        list_options = options
        user_id = call.context.user_id
        if user_id:
            # Calls with a user context: notify targets (device names) for admins only (#35).
            user = await hass.auth.async_get_user(user_id)
            if user is None or not user.is_admin:
                list_options = {k: v for k, v in options.items() if k != CONF_NOTIFY_TARGETS}
        return {
            "valves": store.valves,
            "schedules": store.schedules,
            "cycles": store.cycles,
            "active": [
                {k: v for k, v in run.items() if k != "unsub_close"}
                for run in scheduler.active.values()
            ],
            "active_cycles": [
                {k: v for k, v in r.items() if k != "task"}
                for r in scheduler.active_cycles.values()
            ],
            "soaking": scheduler.soaking,
            "flow": scheduler.flow_status,
            "history": store.history[:20],
            "options": list_options,
        }

    hass.services.async_register(DOMAIN, SERVICE_RUN_VALVE, _svc_run, schema=SCHEMA_RUN)
    hass.services.async_register(DOMAIN, SERVICE_STOP_VALVE, _svc_stop, schema=SCHEMA_STOP)
    hass.services.async_register(DOMAIN, SERVICE_ADD_VALVE, _svc_add_valve, schema=SCHEMA_ADD_VALVE)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_VALVE, _svc_remove_valve, schema=SCHEMA_REMOVE_VALVE)
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_SCHEDULE, _svc_add_schedule,
        schema=SCHEMA_ADD_SCHEDULE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_SCHEDULE, _svc_remove_schedule, schema=SCHEMA_REMOVE_SCHEDULE)
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_SCHEDULE, _svc_update_schedule,
        schema=SCHEMA_UPDATE_SCHEDULE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_CYCLE, _svc_add_cycle,
        schema=SCHEMA_ADD_CYCLE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_CYCLE, _svc_update_cycle,
        schema=SCHEMA_UPDATE_CYCLE,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_CYCLE, _svc_remove_cycle, schema=SCHEMA_REMOVE_CYCLE)
    hass.services.async_register(DOMAIN, SERVICE_RUN_CYCLE, _svc_run_cycle, schema=SCHEMA_RUN_CYCLE)
    hass.services.async_register(DOMAIN, SERVICE_STOP_CYCLE, _svc_stop_cycle, schema=SCHEMA_STOP_CYCLE)
    hass.services.async_register(DOMAIN, SERVICE_STOP_ALL, _svc_stop_all, schema=SCHEMA_NO_ARGS)
    hass.services.async_register(
        DOMAIN, SERVICE_SKIP_NEXT, _svc_skip_next, schema=SCHEMA_SKIP_NEXT,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SKIP_DAY, _svc_skip_day, schema=SCHEMA_SKIP_DAY,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_UNSKIP, _svc_unskip, schema=SCHEMA_UNSKIP)
    hass.services.async_register(DOMAIN, SERVICE_RUN_SCHEDULE, _svc_run_schedule, schema=SCHEMA_SKIP_NEXT)
    hass.services.async_register(DOMAIN, SERVICE_RAIN_DELAY, _svc_rain_delay, schema=SCHEMA_RAIN_DELAY)
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_RAIN_DELAY, _svc_clear_rain_delay, schema=SCHEMA_CLEAR_RAIN_DELAY)
    hass.services.async_register(DOMAIN, SERVICE_PAUSE_CYCLE, _svc_pause_cycle, schema=SCHEMA_PAUSE_RESUME_CYCLE)
    hass.services.async_register(DOMAIN, SERVICE_RESUME_CYCLE, _svc_resume_cycle, schema=SCHEMA_PAUSE_RESUME_CYCLE)
    hass.services.async_register(
        DOMAIN, SERVICE_LIST, _svc_list, supports_response=SupportsResponse.ONLY
    )

    _async_register_ws_commands(hass)
    await _async_register_panel(hass)
    await _async_register_card_resource(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await _async_sync_voice(hass, entry)
    _async_setup_issue_checks(hass, entry)
    return True


ISSUE_CHECK_DELAY = 120


@callback
def _async_setup_issue_checks(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Check for missing entities 2 minutes after HA is up (slow integrations), then on every change."""
    data = hass.data[DOMAIN][entry.entry_id]
    ready = {"on": False}

    @callback
    def _check(*_args) -> None:
        if ready["on"] and hass.data.get(DOMAIN, {}).get(entry.entry_id) is data:
            issues.async_check_entities(hass, data["store"], data["options"])

    @callback
    def _first(*_args) -> None:
        ready["on"] = True
        _check()

    @callback
    def _started(*_args) -> None:
        entry.async_on_unload(async_call_later(hass, ISSUE_CHECK_DELAY, _first))

    if hass.state is CoreState.running:
        _started()
    else:
        entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _started))
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_CONFIG_CHANGED, _check))
    data["check_issues"] = _check


async def _async_sync_voice(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Start or stop Assist sentences to match the voice_enabled option."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not data:
        return
    want = bool(data["options"].get(CONF_VOICE_ENABLED, True))
    voice: VoiceCommands | None = data.get("voice")
    if want and voice is None:
        voice = VoiceCommands(hass, entry, data)
        data["voice"] = voice
        await voice.async_start()
    elif not want and voice is not None:
        voice.async_stop()
        data["voice"] = None


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply option changes in place. A reload would cancel running cycles."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not data:
        return
    data["options"].clear()
    data["options"].update(_build_options(entry))
    data["scheduler"].async_options_updated()
    await _async_sync_voice(hass, entry)
    if data.get("check_issues"):
        data["check_issues"]()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        if data.get("voice"):
            data["voice"].async_stop()
        await data["scheduler"].async_stop()
        await data["store"].async_flush()
        wh_id = data.get("webhook_id")
        if wh_id:
            try:
                webhook.async_unregister(hass, wh_id)
            except Exception:
                pass

    if not hass.data.get(DOMAIN):
        issues.async_clear(hass)
        for svc in (
            SERVICE_RUN_VALVE,
            SERVICE_STOP_VALVE,
            SERVICE_ADD_VALVE,
            SERVICE_REMOVE_VALVE,
            SERVICE_ADD_SCHEDULE,
            SERVICE_UPDATE_SCHEDULE,
            SERVICE_REMOVE_SCHEDULE,
            SERVICE_ADD_CYCLE,
            SERVICE_UPDATE_CYCLE,
            SERVICE_REMOVE_CYCLE,
            SERVICE_RUN_CYCLE,
            SERVICE_STOP_CYCLE,
            SERVICE_STOP_ALL,
            SERVICE_SKIP_NEXT,
            SERVICE_SKIP_DAY,
            SERVICE_UNSKIP,
            SERVICE_RUN_SCHEDULE,
            SERVICE_RAIN_DELAY,
            SERVICE_CLEAR_RAIN_DELAY,
            SERVICE_PAUSE_CYCLE,
            SERVICE_RESUME_CYCLE,
            SERVICE_LIST,
        ):
            if hass.services.has_service(DOMAIN, svc):
                hass.services.async_remove(DOMAIN, svc)
        if hass.data.pop(PANEL_REGISTERED_KEY, False):
            try:
                async_remove_panel(hass, PANEL_URL_PATH)
            except Exception as e:
                LOG.debug("panel remove failed: %s", e)
    return True
