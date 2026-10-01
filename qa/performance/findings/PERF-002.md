# PERF-002 Calendar entity silently truncates events at 500 occurrences: 62-day request stops after 24 days at scale target

| | |
|---|---|
| Type | SCALABILITY RISK (a cap that the scale target reaches; the effect is missing data, not slowness) |
| Severity | MEDIUM |
| Status | DRAFT - claimed 2026-10-01T10:20Z, not yet filed |
| Issue | [#75](https://github.com/bareli/schedule_wizard/issues/75) |
| Feature | `calendar.schedule_wizard_watering_schedule`, `planner.occurrences` |
| Test case | none (new: PERF series; related series CAL) |
| Environment | dev (8174, HA 2026.9.4) |
| Branch / commit | main / 208e848 (v0.14.0) |
| Detected by | qa-performance-engineer |
| Detected | 2026-10-01 |
| Model | model:sonnet (fix and acceptance can be stated exactly, see Fix prompt) |
| Evidence basis | MEASURED |

## Summary

`planner.occurrences` caps at 500 results, so with 20 daily schedules the calendar entity returns events
for only 24 of 62 requested days.

## Observed

`planner.occurrences(..., limit=500)` sorts all occurrences by start time and returns the first 500.
`WateringCalendar.async_get_events` clamps the range to 62 days and relies on that function, so with many
daily schedules the later days are dropped without any signal.

## Measurement

Data as in PERF-001 (20 zones, 10 plans, 30 schedules, 20 of them daily). REST
`GET /api/calendars/calendar.schedule_wizard_watering_schedule?start=<now>&end=<now+62d>` on 2026-10-01:

- 470 events returned (after the entity's own `end > start` filter), HTTP round trip 30.0 ms
- first event 2026-10-02, last event 2026-10-25, 24 distinct days of the 62 requested

An HA calendar month view asks for about 5 to 6 weeks, so the last 1 to 2 weeks of that view would be
empty (analytical: the UI view itself was not opened).

Offline timing of the function with a stub store loaded from the instance's store file, 50 runs: 7 days
0.76 ms median; look-ahead window used by `calendar.event` 2.91 ms median (returns 500, capped); 62 days
5.12 ms median (500, capped). These are fast; the cap, not the cost, is the finding.

## Baseline

none captured.

## Relevant endpoint / code / SQL

- `custom_components/schedule_wizard/planner.py` `occurrences` (`limit: int = 500`, `return out[:limit]`)
- `custom_components/schedule_wizard/calendar.py` `async_get_events`, `MAX_RANGE_DAYS = 62`

## Execution plan

n/a

## Scale implication

Occurrences in a range are about (daily schedules) x (days). 20 daily schedules reach 500 in 25 days;
any user with more than about 8 daily schedules (8 x 62 = 496) loses the tail of a 62-day request. The
scale target (30 schedules) reaches it sooner.

## Likely root cause

A fixed result cap applied after the sort, shared by callers that need the complete range (calendar
view) and callers that only need the nearest few (reminders, next-run).

## Recommended remediation

Keep the cap for callers that want the nearest N; `async_get_events` should pass a limit large enough
for its range (30 schedules x 62 days = 1,860) or none. Do not raise the default used by `get_state`.

## Suggested regression

20 daily schedules, `async_get_events` over 62 days returns 20 x 62 events and the last is on day 62;
repeat with 30 schedules.

## Fix prompt

Fix PERF-002 in Schedule Wizard. Problem: `calendar.py` `async_get_events` returns at most 500 events
because `planner.occurrences` caps at `limit=500`; with 20 daily schedules a 62-day request ends on day 24.
Expected: every occurrence inside the requested range (max 62 days) is returned. Reproduce: create 20
zones and 20 daily schedules, GET `/api/calendars/calendar.schedule_wizard_watering_schedule` for 62 days,
count distinct days. Files: `custom_components/schedule_wizard/calendar.py`, `planner.py`, `tests/`.
Constraints: do not change the default limit used by `get_state` or reminders; do not refactor unrelated
code. Acceptance: 62-day request with 20 daily schedules returns 20 x 62 events (plus any run still going
at the start); add the regression test; existing tests pass.

## Handback (qa-developer, 2026-10-01): PERF-002 #75

**Reproduced** in the new test at baseline `01d6d10`: 20 daily schedules over 62 days returned 480 events (`assert 480 == 1240`).

**Fix** (commit `5ec87d7`):
- `planner.occurrences(..., limit=None)` returns everything. The default 500 is unchanged for `get_state`, next-run, reminders and the calendar `event` property.
- `calendar.py` `async_get_events` passes `limit=None`. Its range is still clamped to `MAX_RANGE_DAYS = 62`. With `MAX_SCHEDULES = 200` that is at most about 12,600 occurrences.

**Verification recipe**
```
Account:  qa_admin (REST token), 127.0.0.1:8183 or 8170 after merge and restart
Data:     20 zones with one daily schedule each (the PERF-001 scale data does this)
Request:  GET /api/calendars/calendar.schedule_wizard_watering_schedule?start=<tomorrow 00:00>&end=<+62 days>
Expect:   20 x 62 = 1240 events, 62 distinct days, the last on day 62 (plus any run still going at start).
Before:   470-500 events, ending on day 24.
```

**Regression test:** `tests/test_v015_fixes.py::test_calendar_returns_every_occurrence_in_range` (20 daily schedules, `calendar.get_events` for 62 days: 1240 events, 62 days, last day = start + 61).

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
