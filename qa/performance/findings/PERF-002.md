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
