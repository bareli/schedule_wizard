# Reference

All services are visible under **Developer Tools → Actions** with full selectors.

## Services

| Service | Purpose |
| --- | --- |
| `schedule_wizard.run_valve` | Open an entity for `duration_minutes`. Auto-closes when done. |
| `schedule_wizard.stop_valve` | Close an entity now and cancel its timer. |
| `schedule_wizard.add_valve` | Register or update a zone (entity id, label, default duration; optional soak and moisture fields). |
| `schedule_wizard.remove_valve` | Unregister a zone and delete its schedules. |
| `schedule_wizard.add_schedule` | Add a recurring schedule: `time` (or `time_mode` sunrise / sunset with `sun_offset_minutes`), `days` or `every_n_days` (2 to 30) with optional `start_date`, a duration, a zone or a cycle, optional `conditions`. Returns the new id. |
| `schedule_wizard.update_schedule` | Patch a schedule by id. |
| `schedule_wizard.remove_schedule` | Delete a schedule by id. |
| `schedule_wizard.add_cycle` | Create a cycle: an ordered list of `{entity_id, duration_minutes}` steps. |
| `schedule_wizard.update_cycle` | Patch a cycle. |
| `schedule_wizard.remove_cycle` | Delete a cycle and the schedules that point to it. |
| `schedule_wizard.run_cycle` | Start a cycle now; zones run one after another. |
| `schedule_wizard.stop_cycle` | Cancel a running cycle. |
| `schedule_wizard.pause_cycle` | Pause a cycle: the current zone closes and the rest wait. |
| `schedule_wizard.resume_cycle` | Resume a paused cycle. |
| `schedule_wizard.set_rain_delay` | Skip scheduled and calendar runs for N `hours`; all zones, or the `entity_id` list. |
| `schedule_wizard.clear_rain_delay` | Clear the global delay, or only the delay of the `entity_id` list. |
| `schedule_wizard.stop_all` | Stop every zone, soak sequence and cycle, then close the master valve. |
| `schedule_wizard.skip_next` | Skip the next run of a schedule (`schedule_id`, optional `date`). |
| `schedule_wizard.skip_day` | Skip every run on a `date` (default: the rest of today). |
| `schedule_wizard.unskip` | Undo a skip (`schedule_id`, `date`). |
| `schedule_wizard.run_schedule` | Start a schedule's zone or plan now and drop today's scheduled run of it. |
| `schedule_wizard.set_override` | Change one run on a `date` (up to 31 days ahead): a new same-day `time` and/or `percent` (25 to 300). |
| `schedule_wizard.clear_override` | Undo the change of one run (`schedule_id`, `date`). |
| `schedule_wizard.set_boost` | Water `percent` (-50, -30, -20, 10, 20, 30 or 50) more or less on every scheduled run for `days` (1 to 14). |
| `schedule_wizard.clear_boost` | End the boost. |
| `schedule_wizard.apply_tip` | Do what a weather tip suggests (`tip_id`, for example `rain:2026-10-10`). |
| `schedule_wizard.dismiss_tip` | Hide one weather tip. |
| `schedule_wizard.mute_tip` | Stop (or with `muted: false` resume) tips of a `kind`: rain, heat or frost. |
| `schedule_wizard.list_config` | Return zones, schedules, cycles, active runs and recent history as a response. |

Limits: names and labels up to 80 characters; at most 200 zones, 200 watering times and 200 plans. Only `switch`, `valve`, `cover`, `input_boolean` and `light` entities are accepted.

### Examples

Run a zone from a script:

```yaml
service: schedule_wizard.run_valve
data:
  entity_id: switch.front_lawn_valve
  duration_minutes: 15
```

Add a zone and a schedule:

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

Water every other day, starting on a given date:

```yaml
- service: schedule_wizard.add_schedule
  data:
    valve_entity_id: switch.front_lawn_valve
    time: "06:00"
    duration_minutes: 10
    every_n_days: 2
    start_date: "2026-10-05"
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

## Entities

Every zone and every plan gets its own device. They appear, rename and disappear as you edit zones and plans.

| Entity | What it does |
| --- | --- |
| `switch.<zone>_watering` | On while the zone waters. On = water for its default minutes, off = stop. |
| `sensor.<zone>_time_left` | Minutes left (0 when idle). |
| `sensor.<zone>_water_used` | Litres used (total increasing). |
| `switch.<plan>_enabled` | Plan on/off. Off = its schedules do not run. |
| `button.<plan>_run_now` | Start the plan now. |
| `binary_sensor.schedule_wizard_watering` | On while anything waters. |
| `switch.schedule_wizard_rain_delay` | On while the rain delay is active. On = pause for 24 h. |
| `calendar.schedule_wizard_watering_schedule` | Upcoming runs, shown in the Home Assistant calendar. |
| `sensor.schedule_wizard_active_runs` | Count of running zones; attribute `runs` lists them. |
| `sensor.schedule_wizard_next_schedule` | Label of the next scheduled run; attributes include `valve_entity_id`, `cycle_id`, `schedule_id`, `duration_min`, `fires_in_minutes`. |
| `sensor.schedule_wizard_water_used` | Total litres. |

Installs from before v0.8.0 may keep the older ids `sensor.active_runs` and `sensor.next_schedule`.

## Events

The integration fires these events on the Home Assistant event bus. The `source` field tells how a run started (`schedule`, `calendar`, `manual`, `service`, `webhook`, `cycle:<id>`).

| Event | When |
| --- | --- |
| `schedule_wizard_valve_started` | A zone opens. |
| `schedule_wizard_valve_ended` | A zone closes (`status`: `completed` or `cancelled`). |
| `schedule_wizard_cycle_started` | A cycle begins. |
| `schedule_wizard_cycle_ended` | A cycle finishes or is cancelled. |
| `schedule_wizard_rain_skipped` | A run was skipped because of rain. |
| `schedule_wizard_moisture_skipped` | A run was skipped because the soil is wet. |
| `schedule_wizard_condition_skipped` | A schedule's conditions were not met. |
| `schedule_wizard_seasonal_skipped` | A run was skipped: temperature adjustment 0 %. |
| `schedule_wizard_valve_soaking` | A cycle-and-soak run paused between chunks. |
| `schedule_wizard_leak_detected` | Flow alert (`kind`: `leak` or `high_flow`). |
| `schedule_wizard_low_flow` | A zone got much less water than usual. |
| `schedule_wizard_valve_failed_to_open` | Fail-to-open check triggered. |
| `schedule_wizard_rain_delay_set` | Rain delay set or cleared. |
| `schedule_wizard_cycle_skipped_overlap` | A scheduled cycle was skipped while another ran. |

### Example automations

```yaml
alias: "Irrigation: log cycle completion"
trigger:
  - platform: event
    event_type: schedule_wizard_cycle_ended
action:
  - service: system_log.write
    data:
      message: >
        Cycle {{ trigger.event.data.name }} ended with status
        {{ trigger.event.data.status }} (source: {{ trigger.event.data.source }})
```

```yaml
alias: "Alert on cancelled valve"
trigger:
  - platform: event
    event_type: schedule_wizard_valve_ended
    event_data:
      status: cancelled
action:
  - service: notify.mobile_app_my_phone
    data:
      title: "Irrigation"
      message: "{{ trigger.event.data.label }} was cancelled mid-run"
```

## Options

| Key | Default | Description |
| --- | --- | --- |
| `calendar_entity` | none | Calendar entity to poll. |
| `calendar_lookahead_min` | 10 | Minutes ahead to scan for matching events. |
| `poll_interval` | 60 | Calendar poll interval in seconds (10 to 3600). |
| `calendar_keyword` | none | Only events whose title starts with this word water. Up to 40 characters. |
| `max_external_minutes` | 120 | Longest run a calendar event or webhook call may start (1 to 1440). |
| `default_duration` | 10 | Default run length when a zone has none. |
| `rain_entity` | none | Weather, sensor or binary_sensor for rain. |
| `rain_skip_states` | `rainy,pouring,snowy,lightning-rainy` | Skip when the state matches any of these. |
| `rain_attribute` | none | Attribute to read instead of the state. |
| `rain_threshold` | none | Numeric threshold. Skip when at or above it. Blank or 0 is off. |
| `flow_entity` | none | Flow sensor for leak detection. |
| `flow_leak_threshold` | 0 | Leak alert when flow is above this with nothing watering. 0 is off. |
| `flow_max_running` | 0 | High-flow alert above this while watering. 0 is off. |
| `flow_delay_sec` | 60 | The condition must last this long before alerting. |
| `flow_stop_all` | false | On an alert, stop all watering and close the master valve. |

## Languages

The panel and card follow your Home Assistant profile language: English, Deutsch, עברית, Español, Français, Italiano, Nederlands, Português, Русский, Українська, Polski, العربية, 简体中文, Svenska, Dansk, Norsk bokmål and Suomi. Hebrew and Arabic switch the whole panel and card to right-to-left. Other languages fall back to English. English, German and Hebrew are reviewed; the others are machine translations, so corrections are welcome.
