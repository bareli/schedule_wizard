# Schedule Wizard

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Validate](https://github.com/bareli/schedule_wizard/actions/workflows/validate.yml/badge.svg)](https://github.com/bareli/schedule_wizard/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Home Assistant **custom integration** that runs a scheduler for irrigation valves, switches, lights, and covers. Triggers entities on recurring schedules or from calendar events, auto-closes after the configured duration, survives HA restarts. Works on every HA install type (HAOS, Supervised, Container, Core).

## Why

Built-in automations can fire a valve on a schedule, but:

- No built-in duration guard that auto-closes after N minutes.
- No unified view of *"which valve runs next, which is running now."*
- Calendar-driven watering needs per-event minutes; no clean template for that.
- Restarting HA mid-cycle leaves the valve open forever.

Schedule Wizard handles all of the above in one integration with its own sidebar UI.

## Features

- Recurring schedules per valve: HH:MM + any subset of weekdays + duration.
- Calendar-driven runs: event summary matches a valve label, description holds minutes.
- Manual run / stop from the sidebar panel or services.
- Auto-close after configured duration.
- **Active runs persist across HA restarts** — re-arms remaining timers based on entity state.
- Two sensors: `active_runs` (with per-run details) and `next_schedule`.
- Sidebar panel with editable tabs: Dashboard, Valves, Schedules, Settings.
- Single-instance config flow + options flow for HA-native configuration.
- Domain-aware: `switch`, `valve`, `cover`, `input_boolean`, `light` (cover/valve use `open_*` / `close_*`, others use `turn_on` / `turn_off`).
- Persistent storage via HA's `Store` helper (no SQLite, no external DB).

## Install

### Via HACS (recommended)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/bareli/schedule_wizard` as **Integration**.
2. Search **Schedule Wizard** in HACS → Download.
3. Restart Home Assistant.
4. **Settings → Devices & Services → + Add Integration → Schedule Wizard**.

### Manual

1. Copy `custom_components/schedule_wizard/` into `<config>/custom_components/`.
2. Restart HA.
3. Add the integration from the UI (step 4 above).

Minimum HA version: **2024.7.0**.

## Using the panel

After install, a **Schedule Wizard** entry appears in the sidebar (sprinkler icon). Four tabs:

- **Dashboard** — active runs with live progress bars, quick run/stop per valve, recent history.
- **Valves** — add / edit / delete valves. Pick any supported HA entity, set its label (used for calendar matching) and default duration.
- **Schedules** — recurring rules: pick a valve, time, days, duration.
- **Settings** — calendar entity, lookahead window, poll interval, default duration. All editable here; no need to visit the Configure dialog.

Options flow (Settings → Devices & Services → Schedule Wizard → Configure) writes the same values — use whichever you prefer.

## Options

| Key                       | Default | Description                                            |
| ------------------------- | ------- | ------------------------------------------------------ |
| `calendar_entity`         | (none)  | HA calendar entity to poll. Optional.                  |
| `calendar_lookahead_min`  | 10      | Minutes ahead to scan for matching events.             |
| `poll_interval`           | 60      | Calendar poll interval in seconds (10–3600).           |
| `default_duration`        | 10      | Default run duration when a valve has none set.        |

## Calendar event format

- **Summary** must contain the valve label (case-insensitive substring match). Example for label `Front lawn`:
  - `Front lawn` ✓
  - `Front Lawn morning cycle` ✓
  - `Garden zone 1` ✗
- **Description**: minutes to run. First integer wins. Falls back to event duration (end − start), then to the valve's default duration.
- **Start time** triggers the run. Events within the lookahead window are caught on the next poll.

## Services

| Service                           | Purpose                                                                   |
| --------------------------------- | ------------------------------------------------------------------------- |
| `schedule_wizard.run_valve`       | Open an entity for `duration_minutes`. Auto-closes when done.             |
| `schedule_wizard.stop_valve`      | Close an entity now. Cancels any active timer.                            |
| `schedule_wizard.add_valve`       | Register a valve (entity_id + label + default duration).                  |
| `schedule_wizard.remove_valve`    | Unregister a valve and delete its schedules.                              |
| `schedule_wizard.add_schedule`    | Add a recurring schedule (time + days + duration). Returns new schedule.  |
| `schedule_wizard.remove_schedule` | Delete a schedule by id.                                                  |
| `schedule_wizard.list_config`     | Return valves, schedules, active runs, recent history (response service). |

All services are visible under **Developer Tools → Actions** with full selectors.

### Examples

Run a valve from a script:

```yaml
service: schedule_wizard.run_valve
data:
  entity_id: switch.front_lawn_valve
  duration_minutes: 15
```

Stop:

```yaml
service: schedule_wizard.stop_valve
data:
  entity_id: switch.front_lawn_valve
```

Add a valve and a schedule:

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

Capture the new schedule id with a response variable:

```yaml
- service: schedule_wizard.add_schedule
  data:
    valve_entity_id: switch.front_lawn_valve
    time: "19:00"
    duration_minutes: 8
    days: [tue, thu]
  response_variable: created
- service: system_log.write
  data:
    message: "New schedule id: {{ created.schedule.id }}"
```

## Sensors

- `sensor.schedule_wizard_active_runs` — integer count of currently running valves; attributes include a `runs` array with `entity_id`, `source`, `started_at`, `ends_at`, `remaining_seconds`, `duration_min`.
- `sensor.schedule_wizard_next_schedule` — friendly label of the next scheduled run (e.g. `"Mon 06:30"`); attributes include `valve_entity_id`, `schedule_id`, `duration_min`, `fires_in_minutes`.

Use them to build custom Lovelace cards or drive automations that react to scheduler state.

## Restart behavior

On HA restart, the scheduler re-reads active runs from storage and checks each entity:

| Entity state    | Remaining time  | Action                                  |
| --------------- | --------------- | --------------------------------------- |
| ON / open       | > 0 seconds     | Re-arm auto-close for remaining time.   |
| ON / open       | ≤ 0 seconds     | Close immediately, log as expired.      |
| OFF / closed    | any             | Drop run, log as cancelled.             |

## Troubleshooting

- **Integration won't load.** Check `Settings → System → Logs`, filter `schedule_wizard`. Min HA version is 2024.7.
- **Calendar events don't fire.** Verify calendar entity is selected in Settings tab. Check event summary contains the valve label *exactly* (case-insensitive substring). Enable debug logging:
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.schedule_wizard: debug
  ```
- **Valve stays on after restart.** Expected if `active_runs` storage was lost (fresh install) or entity was manually turned off during downtime. Normal runs persist.
- **"Unsupported domain"** from service call. Only `switch`, `valve`, `cover`, `input_boolean`, `light` are allowed.

## Contributing

Issues + PRs welcome at [github.com/bareli/schedule_wizard](https://github.com/bareli/schedule_wizard).

## License

MIT — see [LICENSE](LICENSE).
