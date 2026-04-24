# Changelog

## 0.1.0 — initial release

- HACS custom integration (in-process Python, works on all HA install types).
- Cron-style schedules per valve (HH:MM + days of week + duration).
- Calendar-driven runs (label match in event summary, minutes in description).
- Auto-close after configured duration.
- Active-run persistence across HA restarts (re-arms timers based on entity state and remaining time).
- Services: `run_valve`, `stop_valve`, `add_valve`, `remove_valve`, `add_schedule`, `remove_schedule`, `list_config`.
- Sensors: `active_runs` (with per-run details) and `next_schedule`.
- Sidebar panel with tabs: Dashboard, Valves, Schedules, Settings (all editable).
- Single-instance config flow + options flow for calendar and defaults.
- Supports `switch`, `valve`, `cover`, `input_boolean`, `light` domains.
- Persistent storage via HA `Store` helper at `<config>/.storage/schedule_wizard.data`.
