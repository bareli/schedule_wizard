"""Schedule Wizard integration."""
from __future__ import annotations

import logging
import os
import secrets
import time
from typing import Any

import voluptuous as vol

from aiohttp import web

from homeassistant.components import panel_custom, webhook, websocket_api
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
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
    CONF_MOISTURE_ATTRIBUTE,
    CONF_MOISTURE_ENTITY,
    CONF_MOISTURE_THRESHOLD_SKIP_ABOVE,
    CONF_SEASONAL_ENABLED,
    CONF_SEASONAL_MAX_PCT,
    CONF_SEASONAL_MIN_PCT,
    CONF_SEASONAL_TEMP_ATTRIBUTE,
    CONF_SEASONAL_TEMP_ENTITY,
    CONF_SEASONAL_TEMP_HIGH,
    CONF_SEASONAL_TEMP_LOW,
    DEFAULT_CALENDAR_LOOKAHEAD,
    DEFAULT_CALENDAR_POLL_SECONDS,
    DEFAULT_DURATION,
    DEFAULT_RAIN_SKIP_STATES,
    DOMAIN,
    NOTIFY_EVENTS,
    SERVICE_ADD_CYCLE,
    SERVICE_ADD_SCHEDULE,
    SERVICE_ADD_VALVE,
    SERVICE_LIST,
    SERVICE_REMOVE_CYCLE,
    SERVICE_REMOVE_SCHEDULE,
    SERVICE_REMOVE_VALVE,
    SERVICE_RUN_CYCLE,
    SERVICE_RUN_VALVE,
    SERVICE_STOP_CYCLE,
    SERVICE_STOP_VALVE,
    SERVICE_UPDATE_CYCLE,
    SERVICE_UPDATE_SCHEDULE,
    SUPPORTED_DOMAINS,
)
from .scheduler import Scheduler
from .storage import WizardStore

LOG = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

PANEL_URL_PATH = "schedule-wizard"
PANEL_STATIC_URL = "/schedule_wizard_panel"
PANEL_REGISTERED_KEY = f"{DOMAIN}_panel_registered"
WS_COMMANDS_REGISTERED_KEY = f"{DOMAIN}_ws_registered"
CARD_RESOURCE_REGISTERED_KEY = f"{DOMAIN}_card_registered"
CARD_RESOURCE_URL = f"{PANEL_STATIC_URL}/card.js"


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
    vol.Required("label"): cv.string,
    vol.Optional("default_duration_minutes", default=DEFAULT_DURATION): vol.All(int, vol.Range(min=1, max=1440)),
    vol.Optional("enabled", default=True): cv.boolean,
})

SCHEMA_REMOVE_VALVE = vol.Schema({
    vol.Required("entity_id"): _entity_in_supported_domain,
})

SCHEMA_ADD_SCHEDULE = vol.Schema({
    vol.Optional("valve_entity_id"): _entity_in_supported_domain,
    vol.Optional("cycle_id"): cv.string,
    vol.Required("time"): _hhmm,
    vol.Optional("duration_minutes", default=1): vol.All(int, vol.Range(min=1, max=1440)),
    vol.Required("days"): vol.All(cv.ensure_list, [vol.In(["mon", "tue", "wed", "thu", "fri", "sat", "sun"])]),
    vol.Optional("name", default=""): cv.string,
    vol.Optional("enabled", default=True): cv.boolean,
})

SCHEMA_ADD_CYCLE = vol.Schema({
    vol.Required("name"): cv.string,
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
    vol.Optional("name"): cv.string,
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

SCHEMA_REMOVE_SCHEDULE = vol.Schema({
    vol.Required("schedule_id"): cv.string,
})

SCHEMA_UPDATE_SCHEDULE = vol.Schema({
    vol.Required("schedule_id"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("time"): _hhmm,
    vol.Optional("duration_minutes"): vol.All(int, vol.Range(min=1, max=1440)),
    vol.Optional("days"): vol.All(cv.ensure_list, [vol.In(["mon", "tue", "wed", "thu", "fri", "sat", "sun"])]),
    vol.Optional("enabled"): cv.boolean,
})

DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _days_to_mask(days: list[str]) -> int:
    mask = 0
    for d in days:
        mask |= 1 << DAY_NAMES.index(d)
    return mask


def _integration_version() -> str:
    try:
        import json
        with open(os.path.join(os.path.dirname(__file__), "manifest.json"), "r") as f:
            return json.load(f).get("version", "0")
    except Exception:
        return "0"


async def _async_register_panel(hass: HomeAssistant) -> None:
    if hass.data.get(PANEL_REGISTERED_KEY):
        return
    panel_dir = os.path.join(os.path.dirname(__file__), "www")
    if os.path.isdir(panel_dir):
        await hass.http.async_register_static_paths([
            StaticPathConfig(PANEL_STATIC_URL, panel_dir, False)
        ])
    version = _integration_version()
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
            version = _integration_version()
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

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_state"})
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

        valves_enriched = []
        for v in store.valves:
            entry = dict(v)
            entry["stats"] = per_valve_stats.get(v["entity_id"], {
                "last_run": None, "last_completed": None,
                "runs_7d": 0, "total_min_7d": 0,
            })
            valves_enriched.append(entry)

        connection.send_result(msg["id"], {
            "valves": valves_enriched,
            "schedules": store.schedules,
            "cycles": store.cycles,
            "active": active,
            "active_cycles": active_cycles,
            "history": store.history[:30],
            "options": options,
            "controllable": controllable,
            "calendars": calendars,
            "notify_services": notify_services,
            "notify_events": list(NOTIFY_EVENTS),
            "webhook_id": data.get("webhook_id", ""),
            "now": int(time.time()),
        })

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
    })
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
        new_options = dict(entry.options)
        for key in (
            CONF_CALENDAR_ENTITY, CONF_CALENDAR_LOOKAHEAD, CONF_POLL_INTERVAL, CONF_DEFAULT_DURATION,
            CONF_RAIN_ENTITY, CONF_RAIN_SKIP_STATES, CONF_RAIN_ATTRIBUTE, CONF_RAIN_THRESHOLD,
            CONF_NOTIFY_TARGETS, CONF_NOTIFY_EVENTS,
            CONF_SEASONAL_ENABLED, CONF_SEASONAL_TEMP_ENTITY, CONF_SEASONAL_TEMP_ATTRIBUTE,
            CONF_SEASONAL_TEMP_LOW, CONF_SEASONAL_TEMP_HIGH,
            CONF_SEASONAL_MIN_PCT, CONF_SEASONAL_MAX_PCT,
            CONF_ALLOW_CONCURRENT_CYCLES,
            CONF_MOISTURE_ENTITY, CONF_MOISTURE_ATTRIBUTE, CONF_MOISTURE_THRESHOLD_SKIP_ABOVE,
        ):
            if key in msg:
                new_options[key] = msg[key]
        hass_inner.config_entries.async_update_entry(entry, options=new_options)
        connection.send_result(msg["id"], {"options": new_options})

    websocket_api.async_register_command(hass, _ws_get_state)
    websocket_api.async_register_command(hass, _ws_update_options)
    hass.data[WS_COMMANDS_REGISTERED_KEY] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = WizardStore(hass)
    await store.async_load()

    options = {
        CONF_CALENDAR_ENTITY: entry.options.get(CONF_CALENDAR_ENTITY, ""),
        CONF_CALENDAR_LOOKAHEAD: entry.options.get(CONF_CALENDAR_LOOKAHEAD, DEFAULT_CALENDAR_LOOKAHEAD),
        CONF_POLL_INTERVAL: entry.options.get(CONF_POLL_INTERVAL, DEFAULT_CALENDAR_POLL_SECONDS),
        CONF_DEFAULT_DURATION: entry.options.get(CONF_DEFAULT_DURATION, DEFAULT_DURATION),
        CONF_RAIN_ENTITY: entry.options.get(CONF_RAIN_ENTITY, ""),
        CONF_RAIN_SKIP_STATES: entry.options.get(CONF_RAIN_SKIP_STATES, DEFAULT_RAIN_SKIP_STATES),
        CONF_RAIN_ATTRIBUTE: entry.options.get(CONF_RAIN_ATTRIBUTE, ""),
        CONF_RAIN_THRESHOLD: entry.options.get(CONF_RAIN_THRESHOLD, None),
        CONF_NOTIFY_TARGETS: entry.options.get(CONF_NOTIFY_TARGETS, []),
        CONF_NOTIFY_EVENTS: entry.options.get(CONF_NOTIFY_EVENTS, []),
        CONF_SEASONAL_ENABLED: entry.options.get(CONF_SEASONAL_ENABLED, False),
        CONF_SEASONAL_TEMP_ENTITY: entry.options.get(CONF_SEASONAL_TEMP_ENTITY, ""),
        CONF_SEASONAL_TEMP_ATTRIBUTE: entry.options.get(CONF_SEASONAL_TEMP_ATTRIBUTE, ""),
        CONF_SEASONAL_TEMP_LOW: entry.options.get(CONF_SEASONAL_TEMP_LOW, 10),
        CONF_SEASONAL_TEMP_HIGH: entry.options.get(CONF_SEASONAL_TEMP_HIGH, 30),
        CONF_SEASONAL_MIN_PCT: entry.options.get(CONF_SEASONAL_MIN_PCT, 50),
        CONF_SEASONAL_MAX_PCT: entry.options.get(CONF_SEASONAL_MAX_PCT, 120),
        CONF_ALLOW_CONCURRENT_CYCLES: entry.options.get(CONF_ALLOW_CONCURRENT_CYCLES, False),
        CONF_MOISTURE_ENTITY: entry.options.get(CONF_MOISTURE_ENTITY, ""),
        CONF_MOISTURE_ATTRIBUTE: entry.options.get(CONF_MOISTURE_ATTRIBUTE, ""),
        CONF_MOISTURE_THRESHOLD_SKIP_ABOVE: entry.options.get(CONF_MOISTURE_THRESHOLD_SKIP_ABOVE, None),
        "calendar_entity": entry.options.get(CONF_CALENDAR_ENTITY, ""),
        "calendar_lookahead_min": entry.options.get(CONF_CALENDAR_LOOKAHEAD, DEFAULT_CALENDAR_LOOKAHEAD),
        "poll_interval": entry.options.get(CONF_POLL_INTERVAL, DEFAULT_CALENDAR_POLL_SECONDS),
        "default_duration": entry.options.get(CONF_DEFAULT_DURATION, DEFAULT_DURATION),
        "rain_entity": entry.options.get(CONF_RAIN_ENTITY, ""),
        "rain_skip_states": entry.options.get(CONF_RAIN_SKIP_STATES, DEFAULT_RAIN_SKIP_STATES),
        "rain_attribute": entry.options.get(CONF_RAIN_ATTRIBUTE, ""),
        "rain_threshold": entry.options.get(CONF_RAIN_THRESHOLD, None),
        "notify_targets": entry.options.get(CONF_NOTIFY_TARGETS, []),
        "notify_events": entry.options.get(CONF_NOTIFY_EVENTS, []),
        "seasonal_enabled": entry.options.get(CONF_SEASONAL_ENABLED, False),
        "seasonal_temp_entity": entry.options.get(CONF_SEASONAL_TEMP_ENTITY, ""),
        "seasonal_temp_attribute": entry.options.get(CONF_SEASONAL_TEMP_ATTRIBUTE, ""),
        "seasonal_temp_low": entry.options.get(CONF_SEASONAL_TEMP_LOW, 10),
        "seasonal_temp_high": entry.options.get(CONF_SEASONAL_TEMP_HIGH, 30),
        "seasonal_min_pct": entry.options.get(CONF_SEASONAL_MIN_PCT, 50),
        "seasonal_max_pct": entry.options.get(CONF_SEASONAL_MAX_PCT, 120),
        "allow_concurrent_cycles": entry.options.get(CONF_ALLOW_CONCURRENT_CYCLES, False),
        "moisture_entity": entry.options.get(CONF_MOISTURE_ENTITY, ""),
        "moisture_attribute": entry.options.get(CONF_MOISTURE_ATTRIBUTE, ""),
        "moisture_threshold_skip_above": entry.options.get(CONF_MOISTURE_THRESHOLD_SKIP_ABOVE, None),
    }

    scheduler = Scheduler(hass, store, options)
    await scheduler.async_start()

    webhook_id = entry.data.get("webhook_id")
    if not webhook_id:
        webhook_id = secrets.token_hex(16)
        hass.config_entries.async_update_entry(entry, data={**entry.data, "webhook_id": webhook_id})

    async def _webhook_handler(hass_inner: HomeAssistant, wh_id: str, request: web.Request) -> web.Response:
        try:
            if request.method == "POST":
                try:
                    payload = await request.json()
                except Exception:
                    payload = dict(await request.post())
            else:
                payload = dict(request.query)
            action = (payload.get("action") or "run").strip().lower()
            entity_id = payload.get("entity_id")
            if not entity_id:
                return web.json_response({"error": "entity_id required"}, status=400)
            if action == "stop":
                await scheduler.async_stop_valve(entity_id)
                return web.json_response({"ok": True, "action": "stop", "entity_id": entity_id})
            duration = payload.get("duration_minutes")
            if duration is None:
                valve = store.get_valve(entity_id)
                duration = valve["default_duration_min"] if valve else int(options[CONF_DEFAULT_DURATION])
            await scheduler.async_run_valve(entity_id, int(duration), source="webhook")
            return web.json_response({"ok": True, "action": "run", "entity_id": entity_id, "duration_minutes": int(duration)})
        except Exception as e:
            LOG.exception("webhook handler failed: %s", e)
            return web.json_response({"error": str(e)}, status=500)

    try:
        webhook.async_register(hass, DOMAIN, "Schedule Wizard", webhook_id, _webhook_handler)
    except ValueError:
        webhook.async_unregister(hass, webhook_id)
        webhook.async_register(hass, DOMAIN, "Schedule Wizard", webhook_id, _webhook_handler)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "store": store,
        "scheduler": scheduler,
        "options": options,
        "webhook_id": webhook_id,
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
        await store.async_upsert_valve(
            call.data["entity_id"],
            call.data["label"],
            int(call.data.get("default_duration_minutes", DEFAULT_DURATION)),
            bool(call.data.get("enabled", True)),
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
        mask = _days_to_mask(call.data["days"])
        sched = await store.async_add_schedule(
            valve_entity_id=valve_entity_id or None,
            cycle_id=cycle_id or None,
            days_mask=mask,
            time_hhmm=call.data["time"],
            duration_min=int(call.data.get("duration_minutes", 1)),
            name=call.data.get("name", ""),
            enabled=bool(call.data.get("enabled", True)),
        )
        return {"schedule": sched}

    async def _svc_add_cycle(call: ServiceCall) -> ServiceResponse:
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
        if "days" in call.data:
            fields["days_mask"] = _days_to_mask(call.data["days"])
        if "enabled" in call.data:
            fields["enabled"] = bool(call.data["enabled"])
        sched = await store.async_update_schedule(call.data["schedule_id"], **fields)
        if sched is None:
            raise HomeAssistantError("schedule not found")
        return {"schedule": sched}

    async def _svc_list(call: ServiceCall) -> ServiceResponse:
        return {
            "valves": store.valves,
            "schedules": store.schedules,
            "active": [
                {k: v for k, v in run.items() if k != "unsub_close"}
                for run in scheduler.active.values()
            ],
            "history": store.history[:20],
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
    hass.services.async_register(
        DOMAIN, SERVICE_LIST, _svc_list, supports_response=SupportsResponse.ONLY
    )

    _async_register_ws_commands(hass)
    await _async_register_panel(hass)
    await _async_register_card_resource(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        await data["scheduler"].async_stop()
        wh_id = data.get("webhook_id")
        if wh_id:
            try:
                webhook.async_unregister(hass, wh_id)
            except Exception:
                pass

    if not hass.data.get(DOMAIN):
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
