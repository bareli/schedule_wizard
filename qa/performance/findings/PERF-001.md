# PERF-001 get_state sends the whole state (162 KB at scale target) every 5 s per open panel

| | |
|---|---|
| Type | PERFORMANCE RISK |
| Severity | MEDIUM |
| Status | CLOSED - VERIFIED 2026-10-01 on feature/v0.15.0 @ d6d4f4e (8171), [verdict](https://github.com/bareli/schedule_wizard/issues/74#issuecomment-5933134446) |
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

## Handback (qa-developer, 2026-10-01): PERF-001 #74

**Design** (commit `9900139`, `__init__.py` + `www/panel.js` `_refresh` only):
- `schedule_wizard/get_state` always adds `rev`: a 16-hex fingerprint of everything except the live keys and the per-second next-run countdowns (`valves[].next_run.in_seconds`). The live keys are `active`, `active_cycles`, `soaking`, `flow`, `forecast`, `seasonal`, `water_total_l`, `rain_delay_until` and `now`.
- A call with `"rev": "<last rev>"` that still matches gets only the live keys plus `rev` and `"unchanged": true`.
- Any other change sends the full state again: a zone, plan or watering time saved, a history row, an entity state in `controllable`, options, skips, or the week view.
- A call without `rev` gets the full state exactly as before, plus `rev`. That covers the Lovelace card, which I did not touch (owned by the card fixer), and older cached panels.
- Panel `_refresh`:
  - sends its last `rev`;
  - merges a live-only answer into the state it holds (same `stateSig`, so the focus and render logic is unchanged);
  - returns early while `document.hidden`, so a background tab does not poll. The next 5 s tick after the tab becomes visible refreshes.

**Measured**
- Test harness at the scale target (20 zones, 10 plans x 5 steps, 30 schedules (20 daily, 10 every-2-days), 500 history rows, one zone running): full answer 160,934 bytes; poll with an unchanged rev 484 bytes.
- On 8183 (small data): 5,723 bytes full, 348 bytes live.

Not changed:
- The server still builds and fingerprints the full state on every poll. CPU stays where the finder measured it (about 2-3 ms); only the transfer is cut.
- A light or switch that changes state anywhere in HA changes `controllable`, so the next poll after it is a full one.
- The card still polls the full state.

**Verification recipe**
```
Account:  qa_admin, WS on 127.0.0.1:8183 (or 8170 after merge and restart)
Steps:    {"type":"schedule_wizard/get_state"} -> note result.rev; again with "rev": <that value>.
Expect:   2nd result has exactly active, active_cycles, flow, forecast, now, rain_delay_until, rev, seasonal, soaking,
          unchanged (true), water_total_l. No history/week/valves. Size a few hundred bytes. After any zone or schedule save
          the old rev gets the full state again with a new rev.
Browser:  panel open, DevTools > Network > WS: one full get_state frame, then ~0.3-0.5 KB frames every 5 s. Switch to another
          browser tab for 30 s: no get_state frames. Home, Zones, Programs and Reports render the same as before.
Before:   every frame was the full state (162 KB at the scale target); there was no rev, and a hidden tab polled.
```

**Regression tests:** `tests/test_v015_fixes.py::test_get_state_poll_sends_live_part_only` (500 rows, 8 schedules, a running zone: light poll under 20,000 bytes, heavy keys absent, a change resends everything) and `test_panel_poll_uses_rev_and_pauses_when_hidden` (static check of `_refresh`).

**Environment (fixed build)**

- Branch `fix/v0.15.0-backend` (worktree `<scratchpad>/wt-v15-backend`), based on `main` @ `01d6d10`. Not merged, not pushed. One commit per issue: `78f1b8c` #53, `5ec87d7` #75, `683702c` #55, `652542b` #52, `01282ca` #76, `b134c94` #77, `9900139` #74.
- Standing instances 8170-8172 still serve the baseline. Python changes need the orchestrator to merge and restart HA; panel changes need a hard reload (Ctrl+F5). The manifest version is unchanged, so the `?v=` cache-buster does not change.
- Fixer's instance: `http://127.0.0.1:8183`, HA 2026.9.4 (`venv314`). Config `<scratchpad>/haconfig-8183` is a copy of `haconfig-8170` (`.storage` taken 2026-10-01 15:09; port 8183 also set in `.storage/http`; schedule_wizard history, active runs and plan state cleared). `custom_components/schedule_wizard` is a junction to the worktree. Seeded through services: Front lawn (`input_boolean.zone_front`, 10 min), four Water now runs stopped after about 3 s each, and Herbs (`input_boolean.zone_herbs`, 45 min). I stopped the instance before handing back.
- Start (own background task): `cd <scratchpad> && PYTHONPATH=<scratchpad> <scratchpad>/venv314/Scripts/python.exe ha_launch.py -c <scratchpad>/haconfig-8183 --ignore-os-check --skip-pip`.
- Login: `qa_admin`; the password is in `qa/fixtures/dev-accounts-8170.json`. A copy with base 8183 is at `<scratchpad>/dev-accounts-8183.json`; refresh the token with `qa/tools/ha_login.py`.
- One-string fixed-build check: WS `{"type":"schedule_wizard/get_state"}` returns a `rev` key on the fixed build and has no `rev` on the baseline. For the panel: `curl -s http://127.0.0.1:8183/schedule_wizard_panel/panel.js | grep -c sw-valve-duration-err` gives 1 on the fixed build and 0 on the baseline.
- Playwright: `cd ~/.claude/qa-playwright && node <scratchpad>/v15_after.mjs`. It logs in, opens Reports and saves the after images.
- Removal: `cmd /c rmdir <scratchpad>\haconfig-8183\custom_components\schedule_wizard` (removes only the junction), then `rm -rf <scratchpad>/haconfig-8183`.
- Tests: `tests/test_v015_fixes.py` has 18 cases. All 18 were copied into a detached worktree at `01d6d10` and run alone in venv314: 13 failed and 5 passed. The 5 that passed are positive controls: the server refuses `add_valve` minutes 0/-5/1441, and three voice phrasings already started once ("water the front lawn for 2 minutes", "water front lawn", Hebrew). After the fix, all 18 pass. Each intermediate commit passes its own tests. Full suite: venv (HA 2026.2.3) 269 passed, 9 skipped (hassil missing there, so the voice tests skip); venv314 (HA 2026.9.4) 278 passed. `node --check` passes for panel.js and i18n.js.
