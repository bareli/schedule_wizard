"""Constants for Schedule Wizard."""
from __future__ import annotations

DOMAIN = "schedule_wizard"

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.data"

DEFAULT_DURATION = 10
DEFAULT_CALENDAR_LOOKAHEAD = 10
DEFAULT_CALENDAR_POLL_SECONDS = 60

CONF_CALENDAR_ENTITY = "calendar_entity"
CONF_CALENDAR_LOOKAHEAD = "calendar_lookahead_min"
CONF_DEFAULT_DURATION = "default_duration"
CONF_POLL_INTERVAL = "poll_interval"

SUPPORTED_DOMAINS = ("switch", "valve", "cover", "input_boolean", "light")

SIGNAL_STATE_CHANGED = f"{DOMAIN}_state_changed"

DAY_BITS = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32, 6: 64}

SERVICE_RUN_VALVE = "run_valve"
SERVICE_STOP_VALVE = "stop_valve"
SERVICE_ADD_VALVE = "add_valve"
SERVICE_REMOVE_VALVE = "remove_valve"
SERVICE_ADD_SCHEDULE = "add_schedule"
SERVICE_REMOVE_SCHEDULE = "remove_schedule"
SERVICE_LIST = "list_config"
