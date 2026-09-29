# Schedule Wizard

Calendar and time-driven scheduler for irrigation valves, switches, lights, and covers.

## Features

- Recurring schedules per valve (HH:MM + days of week)
- Calendar-driven runs (event summary contains valve label, description holds duration in minutes)
- Manual run/stop via services
- Auto-close after configured duration
- Cycles (zone sequencing) with pause / resume
- Cycle & soak per valve (split long runs into chunks with soak pauses)
- Rain delay, rain skip, global and per-valve soil moisture skip, schedule conditions
- Seasonal (temperature-based) duration scaling
- Master valve / pump, fail-to-open detection, flow sensor leak detection, stop all
- Sidebar panel + Lovelace card, notifications, webhook, CSV export
- Sensors: active runs count + next scheduled run

## Setup

1. Install via HACS.
2. Add the integration: **Settings → Devices & Services → Add Integration → Schedule Wizard**.
3. Open **Configure** to pick a calendar and adjust defaults.
4. Register valves with the `schedule_wizard.add_valve` service.
5. Add schedules with the `schedule_wizard.add_schedule` service.
6. Run/stop on demand with `schedule_wizard.run_valve` / `schedule_wizard.stop_valve`.

## Calendar event format

- **Summary** must contain the valve label (case-insensitive substring).
- **Description** is the duration: `15 min`, `15 דקות`, or just `15`. Falls back to event length, then to the valve's default. All-day events are ignored.
