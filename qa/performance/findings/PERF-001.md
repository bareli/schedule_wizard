# PERF-001 get_state sends the whole state (162 KB at scale target) every 5 s per open panel

| | |
|---|---|
| Type | PERFORMANCE RISK |
| Severity | MEDIUM |
| Status | DRAFT - claimed 2026-10-01T10:20Z, not yet filed |
| Issue | [#74](https://github.com/bareli/schedule_wizard/issues/74) |
| Feature | Panel polling, WS `schedule_wizard/get_state` |
| Test case | none (new: PERF series) |
| Environment | dev (8174, HA 2026.9.4, Windows, other HA instances running on the same machine) |
| Branch / commit | main / 208e848 (v0.14.0) |
| Detected by | qa-performance-engineer |
| Detected | 2026-10-01 |
| Model | model:opus (design choice: which parts stay in the poll, how the panel gets the rest) |
| Evidence basis | MEASURED (payload, timings); remote-link impact is ANALYTICAL |

## Summary

The panel polls `schedule_wizard/get_state` every 5 s and each response is 162 KB at the scale target.
Cost on a LAN is small; on a remote link a panel left open pulls about 116 MB/h.

## Observed

The handler (`__init__.py` `_ws_get_state`) returns everything in one message: all valves, schedules,
cycles, the 7-day `week` expansion, `skips`, the full `history[:500]`, `options`, every entity of 5 domains
(`controllable`), every calendar, notify services. Nothing is conditional: the Zones, Programs and Reports
tabs get the same payload, and views that need none of it still pay for it. The timer does not pause for a
hidden browser tab (no `visibilitychange` handling in `panel.js`; analytical, not tested in a backgrounded tab).

## Measurement

Data: scale target created through services, 20 zones (input_boolean), 10 plans x 5 steps, 30 schedules
(20 weekday-daily, 10 every-N-days), history filled to exactly 500 rows (run + stop through services).
HA had 119 states. Warm, loopback.

| Metric | Value |
|---|---|
| get_state message, history empty | 96,146 bytes |
| get_state message, history 500 | 161,965 bytes |
| largest keys (bytes, JSON) | week 72,300; history 70,380; valves 13,900; schedules 8,580; controllable 7,006; cycles 3,820 |
| Browser WS bytes in 60 s, 12 polls | 1,942,082 (matches 12 x 161,840) |
| Derived per open panel | about 32 KB/s, about 116 MB/h, about 2.8 GB/day (arithmetic on the line above) |
| Round trip, 60 requests from a Python client | median 3.7 ms, p95 4.2 ms |
| HA CPU per request (psutil, 60 requests) | 2.3 ms |
| HA CPU, panel open 603 s, Home tab | 1.08 cpu-s = 0.18 % of one core (includes the frontend's own traffic) |
| HA CPU, no panel, 120 s | 0.02 cpu-s = 0.01 % |
| Panel `_refresh` (WS + parse + render) | Home 16.7 ms median, Zones 14.6, Programs 12.8, Reports 7.1 |
| Panel `_render` | Home 6.4 ms median (max 7.5), Zones 3.5, Programs 2.2, Reports 1.3 |
| CDP over 60 s (12 refreshes), Home | Script 8.3 ms, Layout 136 ms, RecalcStyle 25 ms, LayoutCount 12 |
| Long tasks (>50 ms) | 0 in every tab |
| Heap, 10 min, GC forced each minute | 12.42 MB at 0 min, 10.74 MB at 10 min; DOM nodes 3344 constant; listeners 532 constant; live HTMLElement objects 1799, then 1419 constant. No leak. |
| Panel DOM nodes | Home 1158, Zones 689, Programs 474, Reports 289 |
| CSV export of 500 rows | 0.80 ms median |

Not measured: a remote (cloud / mobile-app) link; a real instance with thousands of entities. Evidence
unavailable for both: this machine has no throttled link and the instance has 119 states.

## Baseline

none captured.

## Relevant endpoint / code / SQL

- `custom_components/schedule_wizard/__init__.py` `_ws_get_state` (builds `week`, `history[:500]`, `controllable`, `calendars`, `notify_services` on every call)
- `custom_components/schedule_wizard/www/panel.js` `_init` (`setInterval(..., 5000)`), `_refresh`

## Execution plan

n/a

## Scale implication

At the scale target the poll is 162 KB; 45 % of it is `week` and 43 % is `history`. Both grow with the
target (plans x zones, history cap). Costs on a LAN are small (table above), so this is a risk, not a bug.
It matters on a remote link (cloud relay, mobile app on cellular): a panel left open pulls about 116 MB/h.
`controllable` grows with the user's own entities (every light, switch, cover, valve, input_boolean) and
`states.async_all()` is walked every 5 s; on a real installation that is a different number from the 54
entities here, and it was not measured.

## Likely root cause

One monolithic response polled on a fixed timer; the static or rarely-changing parts (`controllable`,
`calendars`, `notify_services`, `notify_events`, `options`, `history` beyond the newest rows, `week`) are
sent with the live parts (`active`, `soaking`, `flow`, `now`).

## Recommended remediation

Split the response: a light poll (active, active_cycles, soaking, flow, now, newest history rows, a
change counter), and fetch the heavy parts when a view needs them or when the config changes (the store
already dispatches `SIGNAL_CONFIG_CHANGED`). Slow the timer when `document.hidden`. Keep the contract the
card and tests rely on; check `card.js` uses of `get_state` before removing keys.

## Suggested regression

A test that the light poll stays under an agreed size with 20 zones, 10 plans, 30 schedules and 500
history rows, and a panel test that no poll fires while the document is hidden.

## Fix prompt

Fix PERF-001 in Schedule Wizard. Problem: the panel polls `schedule_wizard/get_state` every 5 s and each
response is 162 KB at the scale target (20 zones, 10 plans, 30 schedules, 500 history rows), of which
`week` is 72 KB and `history` 70 KB. Expected: the recurring poll carries only what changes (active runs,
soaking, flow, now, a change counter); heavy and static parts are fetched when needed. Relevant files:
`custom_components/schedule_wizard/__init__.py` (`_ws_get_state`), `www/panel.js` (`_init`, `_refresh`),
`www/card.js` (check its use of get_state), `tests/`. Constraints: keep the card working; 17 panel
languages in sync (tests/test_i18n.py); must work on HA 2024.7 through 2026.9; do not refactor unrelated
code. Acceptance: the poll message is under 20 KB at the scale target; Home, Zones, Programs, Reports
render the same content as before; no poll while the tab is hidden; all existing tests pass.
