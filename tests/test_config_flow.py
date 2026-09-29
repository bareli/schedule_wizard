"""Config / options flow tests."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import data, setup_wizard


async def test_options_flow_keeps_panel_settings(hass: HomeAssistant):
    """#7: the Configure dialog used to replace all options with its few fields."""
    entry = await setup_wizard(hass, {
        "master_valve_entity": "switch.pump",
        "seasonal_enabled": True,
        "rain_delay_until": 123,
        "calendar_entity": "calendar.old",
    })
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"calendar_lookahead_min": 15, "poll_interval": 60, "default_duration": 12},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["master_valve_entity"] == "switch.pump"
    assert entry.options["seasonal_enabled"] is True
    assert entry.options["rain_delay_until"] == 123
    assert entry.options["calendar_lookahead_min"] == 15
    # Calendar field left empty in the form clears it.
    assert entry.options["calendar_entity"] == ""
    assert data(hass, entry)["options"]["default_duration"] == 12


async def test_options_flow_submits_without_entities(hass: HomeAssistant):
    """Empty entity selectors must not fail validation."""
    entry = await setup_wizard(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
