# PERF-003 Every run step rewrites the whole 130 KB store 4-5 times (about 22 file writes per 5-step plan)

| | |
|---|---|
| Type | PERFORMANCE OPTIMIZATION |
| Severity | LOW |
| Status | DRAFT - claimed 2026-10-01T10:20Z, not yet filed |
| Issue | |
| Feature | Store persistence in `storage.py`, `scheduler.py` |
| Test case | none (new: PERF series; related series RUN) |
| Environment | dev (8174, HA 2026.9.4, Windows) |
| Branch / commit | main / 208e848 (v0.14.0) |
| Detected by | qa-performance-engineer |
| Detected | 2026-10-01 |
| Model | model:opus (changing persistence timing touches restart recovery, which is the product's always-in-scope path) |
| Evidence basis | MEASURED (writes, size, CPU); flash wear is ANALYTICAL |

## Summary

Each valve start and end rewrites the whole store file several times: 4 file writes per 1-minute valve
run, 22 per 5-step plan at 500 history rows.

## Observed

`WizardStore.async_save()` calls `Store.async_save(self._data)` immediately and everything is one file,
including `history` (500 rows). These call it directly: `async_record_run`, `async_set_active_runs`,
`async_set_cycle_state`, `async_add_water`. One valve run start = `async_record_run` +
`async_set_active_runs`; one end = `async_add_water` + `async_record_run` + `async_set_active_runs`;
each cycle step also calls `_persist_cycles`.

## Measurement

History at 500 rows, store file 130,810 bytes. Method: poll `.storage/schedule_wizard.data` mtime every
5 ms from a Python process and count changes (mtime coalescing can undercount, so these are lower bounds).

| Scenario | File replacements | Bytes written |
|---|---|---|
| 1 valve, 1-minute run | 4 (2 at start, 2 at end) | about 0.52 MB |
| 1 plan of 5 steps x 1 minute, 315 s window | 22 | about 2.9 MB |

HA CPU for the 315 s plan window: 1.34 cpu-s (0.43 % of one core), includes everything HA did. Offline
`json.dumps` of the store: 0.31 ms median. So CPU cost is small; the cost is write volume.

Evidence unavailable for SD-card wear or slow-storage latency: this machine has an SSD and nothing else
was measured.

## Baseline

none captured.

## Relevant endpoint / code / SQL

- `custom_components/schedule_wizard/storage.py` `async_save`, `async_record_run`, `async_set_active_runs`, `async_set_cycle_state`, `async_add_water`
- `custom_components/schedule_wizard/scheduler.py` `async_run_valve`, `_async_complete`, `_persist_cycles`

## Execution plan

n/a

## Scale implication

For a day where all 10 plans (5 steps) and 20 single zones run once: about 10 x 22 + 20 x 4 = 300 writes,
about 39 MB (arithmetic from the measured 22 and 4 writes at 131 KB). Small; bounded by the 500-row
history cap. Matters only on small SD-card hosts; not a user-visible slowdown here.

## Likely root cause

State that can be reconstructed (`active_runs`, `cycle_state`) is persisted with the same immediate,
whole-file write as history rows.

## Recommended remediation

Use `Store.async_delay_save` (1 to 2 s) for history and `water_total_l` writes so one start or end
collapses into one write. Keep `active_runs` and `cycle_state` immediate, or flush on
`EVENT_HOMEASSISTANT_STOP`, because restart recovery depends on them. Needs a decision on that trade.

## Suggested regression

One valve start plus one end issues no more than 2 store writes; a restart mid-run still restores the run.

## Fix prompt

Fix PERF-003 in Schedule Wizard. Problem: each valve start and end rewrites the whole store several
times (4 file writes per 1-minute valve run, 22 per 5-step plan at 500 history rows). Expected: history
and water-total writes are coalesced (`async_delay_save`), while `active_runs` and `cycle_state` still
survive a restart mid-run. Files: `custom_components/schedule_wizard/storage.py`, `scheduler.py`,
`tests/`. Constraints: runs must still be restored and closed after a restart (the product's always-in-scope
rule); HA 2024.7 through 2026.9. Acceptance: one valve start plus end causes at most 2 store writes
(count with a patched `Store.async_save` / `async_delay_save` in a test); restart-recovery tests pass.
