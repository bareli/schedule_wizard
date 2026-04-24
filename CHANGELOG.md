# Changelog

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
