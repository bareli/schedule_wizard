# QA project profile: Schedule Wizard

The global QA kit (`~/.claude/qa-kit/`) holds process only. Everything true of THIS product lives here,
in `qa/CLAUDE.md` and `qa/knowledge/`.

## Product

- Name: Schedule Wizard (domain `schedule_wizard`)
- What it does: Home Assistant custom integration (HACS) that runs irrigation zones (valves, switches,
  covers, lights, input_booleans) on recurring schedules and calendar events, with auto-close, rain /
  moisture / forecast / temperature skips, watering plans (cycles with cycle & soak), master valve,
  flow / leak checks, history and reports. Sidebar panel (6 tabs), Lovelace card, entities, voice.
- Owner (rules on UX/ENH decisions): Victor (Bar Eli), repo owner `bareli`.
- Production URL: none. "Production" is each user's own Home Assistant; QA never touches one.
- Deploy: GitHub release → HACS update. A push is not a release.

## Users

Home owners with gardens (many outside Israel; forum users in English and German). Phones and desktops.
Some run HA 2026.9 (latest); minimum HA in hacs.json is 2024.7.

## Locale

Panel and card in 17 languages; owner tests Hebrew (RTL) and English first; German users exist.
Units: minutes, °C/°F, litres. Time zone: the HA time zone (not the server's).

## Stack

Python integration (Store, websocket API, services, config/options flow, calendar, switch, sensor,
binary_sensor, button platforms, webhook, Assist intents); vanilla JS panel and card (`www/`).

## Paths

- Application code (read-only except qa-developer): `custom_components/schedule_wizard/`
- Tests: `tests/` (pytest)
- Build / test: no build; pytest per `CLAUDE.md`.

## Roles

engineer, ux, developer. Security / performance / accessibility on request (no public routes except the
webhook, which uses a random secret id).

## Always in scope

Schedules fire at the right local time and close their valve after the duration, including across HA
restarts; skips (rain, moisture, forecast, temperature) are recorded and never leave a valve open.

## Business outcomes

A run: the target entity turns on, off after N minutes, a history row, events on the bus, sensors update.
A skip: no device change, a history row with the skip reason, a skip event / notification.

## Deliberate behaviour

- "Water now" is never skipped by weather / temperature.
- A temperature factor above 0 % keeps a 1-minute minimum (v0.14.0 decision); exactly 0 % skips.

## Scale target

20 zones, 30 schedules, 10 plans.

## Fix constraints

Root `CLAUDE.md` conventions; client + server validation; 17 panel languages in sync (tests/test_i18n.py);
must keep working on HA 2024.7 through 2026.9.

## Test ID series

`SCH` (schedules incl. every-N-days), `SKIP` (rain / moisture / forecast / temperature), `RUN`, `CAL`,
`ENT` (entities), `PANEL`, `CARD`, `I18N`, `COMPAT`, `UX`.

## Leak terms

- schedule wizard
- schedule_wizard
- schedule-wizard
- bareli/schedule_wizard
