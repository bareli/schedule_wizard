# PERF-003 Every run step rewrites the whole 130 KB store 4-5 times (about 22 file writes per 5-step plan)

| | |
|---|---|
| Type | PERFORMANCE OPTIMIZATION |
| Severity | LOW |
| Status | DRAFT - claimed 2026-10-01T10:20Z, not yet filed |
| Issue | [#76](https://github.com/bareli/schedule_wizard/issues/76) |
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

## Handback (qa-developer, 2026-10-01): PERF-003 #76

**Reproduced** in the new test at baseline `01d6d10`: one 1-minute valve run made 4 store writes (`assert (6 - 2) <= 2`).

**Fix** (commit `01282ca`, `storage.py` + one line in `__init__.py`). This is the trade-off the record asked to be decided:
- **Delayed** with `Store.async_delay_save` (2 s, `SAVE_DELAY`): history rows, water totals and learned flow, and plan step progress (cycle_state changes where the same plans are active with the same paused flags).
- **Immediate**, as before: any change in *which* runs are active (a valve opens or closes) and *which* plans are active or paused (a plan starts, pauses, resumes or ends). This write also carries any pending rows, so the start row and the open valve reach disk together. Config saves (zones, plans, schedules, skips) are unchanged.
- **Shutdown:** HA's Store writes pending delayed data at `EVENT_HOMEASSISTANT_FINAL_WRITE`. Unload and reload call the new `WizardStore.async_flush()`, so a reload never loads a stale file and a late delayed write cannot overwrite the new entry's data.

**Measured** (tests, mock storage counting writes for `schedule_wizard.data`):
- one 1-minute valve run (start + end): 4 to 2 writes;
- a 5-step plan of 1-minute steps: 28 to 13.

**Residual risk** (hard crash or power cut only, not a clean restart):
- History rows and water totals from the last 2 s can be lost.
- A crash within 2 s after a plan moves to its next step can, on restart, resume from the previous step's state. The valve itself is still on disk and is closed or restored as before.

**Verification recipe**
```
Instance: 127.0.0.1:8183 (or 8170 after merge and restart), qa_admin
Steps:    poll <config>/.storage/schedule_wizard.data mtime every 5 ms (as in the record); run_valve zone_front 1 min,
          wait for the end + 5 s; then run a 5-step plan of 1-minute steps.
Expect:   2 file replacements for the valve run (1 at start, 1 at end); about 13 for the plan (record: 22, mtime coalescing
          undercounts). While the valve runs, the file already lists it in active_runs and has its "started" row.
Restart:  start a 5-min run, restart HA (Developer tools > Restart): the run is restored and closes at its original end;
          a history row written in the last 2 s before the restart is present after it.
Before:   4 replacements per 1-minute run, 22 per 5-step plan.
```

**Regression tests:** `tests/test_v015_fixes.py`:
- `test_valve_run_writes_store_at_most_twice`: 2 writes or fewer. The open run and its row are on disk right after the start, and the end state after it.
- `test_delayed_rows_written_on_unload`: a delayed row is on disk after unload.
The existing restart and resume tests pass: `test_resilience.py` (cycle resume, paused plan survives restart, long downtime), `test_restore_unavailable.py` and `test_scheduler.py::test_restore_active_run_after_restart`.

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
