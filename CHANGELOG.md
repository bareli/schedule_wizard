# Changelog

## 0.7.0 — rain delay, master valve, fail detection, cycle pause/resume, Settings basic/advanced

- **Rain delay** button on Dashboard: pause all schedule + calendar runs for 24h / 48h / 7d, with one-tap clear. New services `set_rain_delay` and `clear_rain_delay`.
- **Master valve / pump** option: a central valve that auto-opens before the first zone runs and auto-closes after the last zone closes. Optional pre-open delay for pump pressurization.
- **Fail-to-open detection**: after issuing a turn-on, verify entity reaches an "on" state within N seconds. If not, log error, fire `schedule_wizard_valve_failed_to_open`, send notification.
- **Cycle pause / resume**: pause an in-progress cycle (current valve closes, remaining steps held) and resume from where it left off. New services `pause_cycle`, `resume_cycle`. New events `cycle_paused`, `cycle_resumed`.
- **Settings: Basic / Advanced split**: Settings tab opens with just calendar fields visible. "Show advanced" reveals rain skip, seasonal, moisture, master valve, fail detection, notifications, cycle overlap.
- New notification event types: `valve_failed`, `rain_delay`.
- "10m" → "10min" everywhere in the dashboard for clarity.
- **Recent activity** groups cycle runs with their valve openings indented under the parent cycle.

## 0.6.4 — fix cycle never starting + blocking I/O

- Fixed: cycle task started eagerly before being added to the active-cycles map (HA 2024.7+ `async_create_task` runs eagerly). The task saw "not in active_cycles" and exited immediately, leaving a phantom step-0 entry. Now adds to the map first, then starts the task.
- Fixed: blocking `open()` on `manifest.json` from the event loop. Version is now read once via the executor and cached.

## 0.6.3 — list_config completeness + cycle skip diagnostics

- `schedule_wizard.list_config` service now also returns `cycles`, `active_cycles`, and `options` (previously missing).
- Cycle steps that are skipped due to missing `entity_id` or zero duration now log a warning with the cycle id, step number, and computed values, making "stuck on step 0" much easier to diagnose.

## 0.6.2 — next opening time per valve

- Dashboard Quick run, Valves tab, and Lovelace card now show the next scheduled opening per valve with time label and countdown (`Next: Wed 06:00 (in 18h)`).
- Computed from direct valve schedules AND schedules targeting a cycle that contains the valve.

## 0.6.1 — clearer seasonal UI

- Seasonal section shows temperature unit (°C or °F) taken from HA config on all threshold labels.
- Added inline explanation of how Low/High/Min%/Max% interact.
- Live preview: reads the configured temperature entity/attribute and shows "current temp → factor → example 10-min schedule length" — updates as you edit fields.

## 0.6.0 — seasonal adjust, moisture skip, overlap guard, valve stats

- **Seasonal adjustment** (temperature-scaled): scales schedule and calendar durations between a low and high temp threshold, clamped to min/max percent. Manual runs unaffected.
- **Soil moisture skip**: skip cron/calendar when moisture sensor ≥ threshold (soil already wet). Independent of rain.
- **Cycle overlap protection**: when off (default), schedule/calendar cycles skip while another cycle is running. Opt-in via `allow_concurrent_cycles`.
- **Per-valve stats** on Valves tab: last run timestamp + status + duration, plus runs / minutes in the last 7 days.
- New events: `schedule_wizard_moisture_skipped`, `schedule_wizard_cycle_skipped_overlap`.
- Schedule/calendar runs whose duration was adjusted record `|seasonal:N%` in the history note.

## 0.5.1 — event bus events

- Fires 5 events on the HA event bus, usable as automation triggers:
  - `schedule_wizard_valve_started`
  - `schedule_wizard_valve_ended`
  - `schedule_wizard_cycle_started`
  - `schedule_wizard_cycle_ended`
  - `schedule_wizard_rain_skipped`
- Each event carries `source` so you can filter schedule / calendar / manual / webhook / cycle triggers in automations.
- README documents event names, data fields, and example automations.

## 0.5.0 — multi-language translations

- 15 new translation files for HA native strings (config flow + options flow + service names/descriptions): Spanish, German, French, Italian, Dutch, Portuguese, Russian, Arabic, Polish, Simplified Chinese, Ukrainian, Swedish, Danish, Norwegian, Finnish.
- Existing English and Hebrew translations extended with all new services (cycles, update_schedule).
- Panel UI text (sidebar tabs, buttons, modals) still English; JavaScript i18n is deferred.

## 0.4.2 — preserve input focus across auto-refresh

- Panel Dashboard and Lovelace card no longer destroy DOM on the 5s auto-refresh when an input/select is focused. Progress bars still update smoothly in place.
- Typing in the minutes number box stays put.

## 0.4.1 — fix Run button + inline progress

- Run buttons in the Lovelace card were always disabled due to `setAttribute("disabled", "false")` being truthy in HTML. Internal `el()` helper now skips boolean-false attributes and emits bare attributes for boolean-true.
- Dashboard Quick run rows now show an inline progress bar + remaining time when a valve is active.
- Lovelace card: per-valve progress bar + remaining time inline in each row.

## 0.4.0 — notifications

- Pick one or more `notify.*` services (e.g. HA Companion mobile app) and choose which events push notifications: `valve_start`, `valve_end`, `cycle_start`, `cycle_end`, `skipped_rain`.
- Panel Settings tab has a new Notifications section with checkbox list of detected notify services + event toggles.
- Options flow (Devices & Services → Schedule Wizard → Configure) also exposes the same fields.
- Notifications are fire-and-forget; failures log a warning but don't block valve actions.

## 0.3.0 — cycles (zone sequencing)

- **Cycles**: new first-class object. Define an ordered list of (valve, duration) steps and run them sequentially as a single program. Perfect for irrigation zone sequencing.
- Services: `add_cycle`, `update_cycle`, `remove_cycle`, `run_cycle`, `stop_cycle`.
- Schedules can now target a cycle instead of a single valve (panel target picker + `cycle_id` field on `add_schedule`).
- Calendar events match cycle names too (summary contains the cycle name → whole cycle fires).
- Panel: new **Cycles** tab with step editor (reorder, add, remove). Dashboard shows active cycles with step progress.
- Rain skip applies to cycle schedules (whole cycle skipped on rain).

## 0.2.4 — edit schedules from the panel

- Schedules tab now has Edit + Enable/Disable + Delete buttons per row.
- New service `schedule_wizard.update_schedule` (patch existing schedule by id; any omitted field unchanged).
- Edit modal patches in place via the new service (no delete + recreate); valve selection is locked while editing.

## 0.2.3 — fix Settings tab input wipe

- 5-second panel auto-refresh no longer re-renders the Settings tab, so typing in the rain-entity / threshold / webhook fields is preserved. Settings re-renders only on tab switch or after Save.

## 0.2.2 — cache-bust panel and card

- Panel `module_url` and Lovelace card resource URL now include `?v=<version>` so browsers always fetch the matching JS after an update. Stops stale UI without manual hard-refresh.

## 0.2.1 — panel rain fields + webhook URL

- Settings tab in the sidebar panel now exposes rain-skip configuration (entity, skip states, attribute, threshold).
- Settings tab now shows the webhook URL with one-click copy.

## 0.2.0 — rain skip, webhook, Lovelace card, Hebrew

- **Rain skip**: options flow now accepts a rain/weather entity + skip states / threshold / attribute. Schedules skip automatically when rain condition is active; history logs `skipped_rain`.
- **Webhook trigger**: integration registers a per-entry webhook. `POST /api/webhook/<id>` with `entity_id` (and optional `duration_minutes`, `action: run|stop`) fires a run or stop.
- **Lovelace card** (`custom:schedule-wizard-card`): compact active runs + quick run/stop widget, auto-registered as a Lovelace module resource.
- **Hebrew translation** (`translations/he.json`) for config flow, options flow, and services.
- Options flow extended with rain configuration fields.
- WebSocket `update_options` command now accepts rain fields.

## 0.1.1 — branding

- Real brand assets: `icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png` (sprinkler + calendar, "Irrigation Schedule").
- Placeholder "SW" text icons replaced.

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
