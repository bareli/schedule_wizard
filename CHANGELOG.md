# Changelog

## 0.1.0 — initial

- Active scheduler add-on (Python + FastAPI + asyncio).
- Cron-style schedules per valve.
- Calendar polling with label match in summary and minutes in description.
- Web UI via HA ingress: dashboard, valves, schedules, settings.
- SQLite persistence at `/data/schedule_wizard.db`.
- Supports `switch`, `valve`, `cover`, `input_boolean`, `light`.
