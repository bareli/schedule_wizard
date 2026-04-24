# Schedule Wizard

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

Home Assistant **custom integration** that runs a scheduler for irrigation valves, switches, lights, and covers. Triggers entities on recurring schedules or from calendar events, then auto-closes after the configured duration. Works on every HA install type (HAOS, Supervised, Container, Core).

## Features

- Recurring schedules per valve (HH:MM + days of week + duration)
- Calendar-driven runs (event summary contains valve label, description holds duration in minutes)
- Manual run / stop via services
- Auto-close on duration expiry
- Sensors: active runs count, next scheduled run
- Domain-aware: `switch`, `valve`, `cover`, `input_boolean`, `light`
- Persistent state via HA's `Store` helper (no SQLite, no external DB)

## Install via HACS

1. HACS → Integrations → ⋮ → **Custom repositories** → add `https://github.com/bareli/schedule_wizard` as **Integration**.
2. Search **Schedule Wizard** in HACS, install.
3. Restart Home Assistant.
4. **Settings → Devices & Services → Add Integration → Schedule Wizard**.
5. Open **Configure** to pick a calendar and adjust defaults.

## Manual install

Copy `custom_components/schedule_wizard/` into `<config>/custom_components/`, restart HA, then add the integration from the UI.

## Options

| Key                       | Default | Description                                          |
| ------------------------- | ------- | ---------------------------------------------------- |
| `calendar_entity`         | (none)  | HA calendar to poll. Optional.                       |
| `calendar_lookahead_min`  | 10      | Minutes ahead to scan for matching events.           |
| `poll_interval`           | 60      | Calendar poll interval in seconds (10–3600).         |
| `default_duration`        | 10      | Default run duration (minutes).                      |

Edit any time via **Configure** on the integration card.

## Services

| Service                          | What it does                                                              |
| -------------------------------- | ------------------------------------------------------------------------- |
| `schedule_wizard.run_valve`      | Open an entity for `duration_minutes`. Auto-closes when done.             |
| `schedule_wizard.stop_valve`     | Close an entity now. Cancels any active timer.                            |
| `schedule_wizard.add_valve`      | Register a valve (entity_id + label + default duration).                  |
| `schedule_wizard.remove_valve`   | Unregister a valve and delete its schedules.                              |
| `schedule_wizard.add_schedule`   | Add a recurring schedule (time + days + duration).                        |
| `schedule_wizard.remove_schedule`| Delete a schedule by id.                                                  |
| `schedule_wizard.list_config`    | Return valves, schedules, active runs, recent history (response service). |

All services are also visible under **Developer Tools → Actions** with selectors.

## Sensors

- `sensor.schedule_wizard_active_runs` — count of currently running valves; attributes contain per-run details.
- `sensor.schedule_wizard_next_schedule` — friendly label of the next scheduled run; attributes contain `valve_entity_id`, `schedule_id`, `duration_min`, `fires_in_minutes`.

## Calendar event format

- **Summary** must contain the valve label (case-insensitive substring match). Example for label `Front lawn`:
  - `Front lawn` ✓
  - `Front Lawn morning cycle` ✓
  - `Garden zone 1` ✗
- **Description**: minutes to run. First integer is used. If empty, falls back to event duration (end − start), then to the valve's default duration.
- **Start time** triggers the run. Events scheduled within the lookahead window are caught on the next poll.

## Examples

Run a valve from a script:
```yaml
service: schedule_wizard.run_valve
data:
  entity_id: switch.front_lawn_valve
  duration_minutes: 15
```

Add a valve, then a schedule:
```yaml
- service: schedule_wizard.add_valve
  data:
    entity_id: switch.front_lawn_valve
    label: Front lawn
    default_duration_minutes: 12

- service: schedule_wizard.add_schedule
  data:
    valve_entity_id: switch.front_lawn_valve
    time: "06:30"
    duration_minutes: 12
    days: [mon, wed, fri]
```

## Notes

- Persistent data lives in `<config>/.storage/schedule_wizard.data`.
- HA restart mid-run: timer state is in memory, so a valve already opened will stay opened until you stop it manually or the next schedule fires. Future versions may persist active runs.
- This repo also contains an older add-on variant under `rootfs/`, `Dockerfile`, `config.yaml`. Those files are not used by the integration and can be ignored or deleted from a fork before HACS submission.
