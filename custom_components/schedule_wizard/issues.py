"""Raise HA Repairs issues for entities Schedule Wizard depends on but can't find."""
from __future__ import annotations

import re

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

# option key -> what it is used for (shown in the issue text)
OPTION_ENTITIES = {
    "rain_entity": "rain skip",
    "forecast_entity": "rain forecast",
    "moisture_entity": "soil moisture skip",
    "seasonal_temp_entity": "seasonal adjustment",
    "flow_entity": "leak detection",
    "master_valve_entity": "main valve / pump",
    "calendar_entity": "calendar",
}
ISSUES_KEY = f"{DOMAIN}_issues"


def _issue_id(kind: str, entity_id: str) -> str:
    return f"missing_{kind}_{re.sub(r'[^a-z0-9_]', '_', entity_id.lower())}"


@callback
def async_check_entities(hass: HomeAssistant, store, options: dict) -> None:
    wanted: dict[str, dict[str, str]] = {}
    for valve in store.valves:
        wanted[_issue_id("zone", valve["entity_id"])] = {
            "entity_id": valve["entity_id"], "name": valve.get("label") or valve["entity_id"], "what": "zone",
        }
    for key, what in OPTION_ENTITIES.items():
        entity_id = (options.get(key) or "").strip()
        if entity_id:
            wanted[_issue_id(key, entity_id)] = {"entity_id": entity_id, "name": entity_id, "what": what}
    for valve in store.valves:
        entity_id = (valve.get("moisture_entity") or "").strip()
        if entity_id:
            wanted[_issue_id("zone_moisture", entity_id)] = {
                "entity_id": entity_id, "name": entity_id,
                "what": f"soil moisture of {valve.get('label') or valve['entity_id']}",
            }

    open_issues: set[str] = hass.data.setdefault(ISSUES_KEY, set())
    missing = {iid: info for iid, info in wanted.items() if hass.states.get(info["entity_id"]) is None}
    for iid, info in missing.items():
        ir.async_create_issue(
            hass, DOMAIN, iid,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="missing_entity",
            translation_placeholders=info,
        )
        open_issues.add(iid)
    for iid in list(open_issues):
        if iid not in missing:
            ir.async_delete_issue(hass, DOMAIN, iid)
            open_issues.discard(iid)


@callback
def async_clear(hass: HomeAssistant) -> None:
    for iid in list(hass.data.pop(ISSUES_KEY, set())):
        ir.async_delete_issue(hass, DOMAIN, iid)
