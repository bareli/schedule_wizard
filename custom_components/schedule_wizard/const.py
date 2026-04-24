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
CONF_RAIN_ENTITY = "rain_entity"
CONF_RAIN_SKIP_STATES = "rain_skip_states"
CONF_RAIN_ATTRIBUTE = "rain_attribute"
CONF_RAIN_THRESHOLD = "rain_threshold"

CONF_NOTIFY_TARGETS = "notify_targets"
CONF_NOTIFY_EVENTS = "notify_events"

CONF_SEASONAL_ENABLED = "seasonal_enabled"
CONF_SEASONAL_TEMP_ENTITY = "seasonal_temp_entity"
CONF_SEASONAL_TEMP_ATTRIBUTE = "seasonal_temp_attribute"
CONF_SEASONAL_TEMP_LOW = "seasonal_temp_low"
CONF_SEASONAL_TEMP_HIGH = "seasonal_temp_high"
CONF_SEASONAL_MIN_PCT = "seasonal_min_pct"
CONF_SEASONAL_MAX_PCT = "seasonal_max_pct"

CONF_ALLOW_CONCURRENT_CYCLES = "allow_concurrent_cycles"

CONF_MOISTURE_ENTITY = "moisture_entity"
CONF_MOISTURE_ATTRIBUTE = "moisture_attribute"
CONF_MOISTURE_THRESHOLD_SKIP_ABOVE = "moisture_threshold_skip_above"

DEFAULT_RAIN_SKIP_STATES = "rainy,pouring,snowy,lightning-rainy"

NOTIFY_EVENTS = (
    "valve_start",
    "valve_end",
    "cycle_start",
    "cycle_end",
    "skipped_rain",
)

SUPPORTED_DOMAINS = ("switch", "valve", "cover", "input_boolean", "light")

SIGNAL_STATE_CHANGED = f"{DOMAIN}_state_changed"

EVENT_VALVE_STARTED = f"{DOMAIN}_valve_started"
EVENT_VALVE_ENDED = f"{DOMAIN}_valve_ended"
EVENT_CYCLE_STARTED = f"{DOMAIN}_cycle_started"
EVENT_CYCLE_ENDED = f"{DOMAIN}_cycle_ended"
EVENT_RAIN_SKIPPED = f"{DOMAIN}_rain_skipped"
EVENT_CYCLE_SKIPPED_OVERLAP = f"{DOMAIN}_cycle_skipped_overlap"

DAY_BITS = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32, 6: 64}

SERVICE_RUN_VALVE = "run_valve"
SERVICE_STOP_VALVE = "stop_valve"
SERVICE_ADD_VALVE = "add_valve"
SERVICE_REMOVE_VALVE = "remove_valve"
SERVICE_ADD_SCHEDULE = "add_schedule"
SERVICE_UPDATE_SCHEDULE = "update_schedule"
SERVICE_REMOVE_SCHEDULE = "remove_schedule"
SERVICE_ADD_CYCLE = "add_cycle"
SERVICE_UPDATE_CYCLE = "update_cycle"
SERVICE_REMOVE_CYCLE = "remove_cycle"
SERVICE_RUN_CYCLE = "run_cycle"
SERVICE_STOP_CYCLE = "stop_cycle"
SERVICE_LIST = "list_config"
