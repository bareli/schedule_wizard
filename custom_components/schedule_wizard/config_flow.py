"""Config and options flow for Schedule Wizard."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

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
    DEFAULT_CALENDAR_LOOKAHEAD,
    DEFAULT_CALENDAR_POLL_SECONDS,
    DEFAULT_DURATION,
    DEFAULT_RAIN_SKIP_STATES,
    DOMAIN,
    NOTIFY_EVENTS,
)


class ScheduleWizardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(title="Schedule Wizard", data={}, options={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ScheduleWizardOptionsFlow(config_entry)


FORM_EMPTY = {
    CONF_CALENDAR_ENTITY: "",
    CONF_RAIN_ENTITY: "",
    CONF_RAIN_SKIP_STATES: "",
    CONF_RAIN_ATTRIBUTE: "",
    CONF_RAIN_THRESHOLD: None,
    CONF_NOTIFY_TARGETS: [],
    CONF_NOTIFY_EVENTS: [],
}


def _suggested(value: Any) -> dict[str, Any]:
    return {"suggested_value": value}


class ScheduleWizardOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        opts = self._entry.options
        if user_input is not None:
            # Merge: this form only covers the basic options; keep everything set in the panel.
            new_options = dict(opts)
            for key, empty in FORM_EMPTY.items():
                new_options[key] = user_input.get(key, empty)
            for key in (CONF_CALENDAR_LOOKAHEAD, CONF_POLL_INTERVAL, CONF_DEFAULT_DURATION):
                if key in user_input:
                    new_options[key] = int(user_input[key])
            return self.async_create_entry(title="", data=new_options)

        schema = vol.Schema({
            vol.Optional(
                CONF_CALENDAR_ENTITY,
                description=_suggested(opts.get(CONF_CALENDAR_ENTITY) or None),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="calendar")
            ),
            vol.Optional(
                CONF_CALENDAR_LOOKAHEAD,
                default=opts.get(CONF_CALENDAR_LOOKAHEAD, DEFAULT_CALENDAR_LOOKAHEAD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=1440, step=1, unit_of_measurement="min")
            ),
            vol.Optional(
                CONF_POLL_INTERVAL,
                default=opts.get(CONF_POLL_INTERVAL, DEFAULT_CALENDAR_POLL_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=10, max=3600, step=10, unit_of_measurement="s")
            ),
            vol.Optional(
                CONF_DEFAULT_DURATION,
                default=opts.get(CONF_DEFAULT_DURATION, DEFAULT_DURATION),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=1440, step=1, unit_of_measurement="min")
            ),
            vol.Optional(
                CONF_RAIN_ENTITY,
                description=_suggested(opts.get(CONF_RAIN_ENTITY) or None),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["weather", "sensor", "binary_sensor"])
            ),
            vol.Optional(
                CONF_RAIN_SKIP_STATES,
                description=_suggested(opts.get(CONF_RAIN_SKIP_STATES, DEFAULT_RAIN_SKIP_STATES)),
            ): selector.TextSelector(),
            vol.Optional(
                CONF_RAIN_ATTRIBUTE,
                description=_suggested(opts.get(CONF_RAIN_ATTRIBUTE) or None),
            ): selector.TextSelector(),
            vol.Optional(
                CONF_RAIN_THRESHOLD,
                description=_suggested(opts.get(CONF_RAIN_THRESHOLD)),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=100, step=0.1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional(
                CONF_NOTIFY_TARGETS,
                description=_suggested(opts.get(CONF_NOTIFY_TARGETS) or []),
            ): selector.TextSelector(
                selector.TextSelectorConfig(multiple=True)
            ),
            vol.Optional(
                CONF_NOTIFY_EVENTS,
                description=_suggested(opts.get(CONF_NOTIFY_EVENTS) or []),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(NOTIFY_EVENTS),
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
