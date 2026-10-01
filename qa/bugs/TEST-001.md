# TEST-001 test_next_run_sensor_calendar_and_preview fails while today's sunset run is in progress

| | |
|---|---|
| Type | Bug |
| Severity | low |
| Status | Open |
| Issue | [#97](https://github.com/bareli/schedule_wizard/issues/97) |
| Feature | Tests |
| Test case | SCH |
| Environment | dev copy on 127.0.0.1:8188 (HA 2026.9.4, venv314, copy of haconfig-8173), `feature/v0.15.0` @ `469b9b9` |
| Branch / commit | feature/v0.15.0 @ 469b9b9 |
| Detected by | v0.15.0 verification pass (UX verifier), reproduced by qa-developer |
| Detected | 2026-10-01 |
| Model | sonnet |
| Label | bug |

## Summary

`tests/test_sun_schedule.py::test_next_run_sensor_calendar_and_preview` reads the real clock. While today's Caesarea sunset run (sunset - 15 min, 7 min long) is in progress the calendar entity's state is that ongoing event, and the test expects the next fire: `cal.attributes["start_time"] == expected` fails. Seen in the v0.15.0 full-suite runs around 17:40 local.

## Steps to reproduce

Run the test with the clock inside [sunset - 15 min, sunset - 8 min) in Asia/Jerusalem (e.g. freezegun at that instant).

## Expected

Deterministic: the test freezes an instant away from sunrise and sunset; assertions unchanged.

## Actual

Fails about once a day for 7 minutes (time-of-day dependent).

## Evidence

Test output only (no interface involved).

## Relevant files

`tests/test_sun_schedule.py`

## Handback (qa-developer, 2026-10-01): TEST-001

**Cause, reproduced:** with the clock frozen at 2026-06-10 16:35:30 UTC (Caesarea sunset 16:47, run 16:32-16:39 UTC) the unchanged test fails on `469b9b9`: `assert '2026-06-10 19:32:00' == '2026-06-11 19:32:00'` (the calendar state is the run in progress).

**Fix** (`9c03ee5`, `tests/test_sun_schedule.py`): the test runs on a frozen, ticking clock at noon in Caesarea (`MIDDAY_CAESAREA = 2026-06-10 09:00:30 UTC`, fixture `midday_clock`, same pattern as `fixed_clock`). Assertions unchanged, one added: at noon the next run is this evening's.

**Audit:** no other test reads the real clock with sun times: the cron sun tests fire explicit future instants, the rest of `test_sun_schedule.py` is pure date math, and `test_v015_*` use `fixed_clock`. One other real-clock test changed, because of #93: `test_every_n_days.py::test_calendar_and_week_view` (see #93).

**Verification recipe**
```
Command:  PYTHONPATH=<scratchpad> <scratchpad>/venv314/Scripts/python.exe -c "import win_shim,sys,pytest;sys.exit(pytest.main(['-q','-p','no:cacheprovider','tests/test_sun_schedule.py']))"
Expect:   passes at any time of day. To see the old failure: freeze the old test at 2026-06-10 16:35:30+00:00 on 469b9b9.
          (On the fixed code the old test also passes in that window, because #93 no longer shows a run from before the schedule existed.)
Before:   failed for about 7 minutes around sunset every day.
```

Failing-first: this is a test fix, so the new test passes on `469b9b9` too; the proof is the in-window failure of the old test above.

**Environment (fixed build; no instance left running)**

- Branch `fix/v0.15.0-final` (worktree `<scratchpad>/wt-v15-final`, from `feature/v0.15.0` @ `469b9b9`), fix commits `9c03ee5` + `c88fa13`, records and evidence in the QA commit after them. Not pushed; image links resolve once merged and pushed.
- Instance: `<scratchpad>/haconfig-8188` is left in place, stopped, junction removed (a copy of `haconfig-8173` with port 8188 in `configuration.yaml` and `.storage/http`). Re-link and start: `cmd /c mklink /J <cfg>\custom_components\schedule_wizard <worktree>\custom_components\schedule_wizard`, then `cd <scratchpad> && PYTHONPATH=<scratchpad> venv314/Scripts/python.exe ha_launch.py -c haconfig-8188 --ignore-os-check --skip-pip`. Remove the junction with `cmd /c rmdir` before deleting the copy.
- Data in that copy: zones Front lawn, Herbs, גינה אחורית (`input_boolean.zone_*`); plan "Morning watering" (3 x 10 min, one zone at a time) every 2 days from 2026-10-01, 30 min before sunrise, **created 2026-10-01 18:24 local**; dashboard `/sw-card/0` with the card; history as on 8173 (Herbs completed 17:53-17:54, cancelled 0-min Water now rows, skipped (rain) 17:58). HA language he, Asia/Jerusalem. Login `qa_admin`, password in `qa/fixtures/dev-accounts-8173.json` (same users).
- Proof it is the fixed build: `curl -s http://127.0.0.1:8188/schedule_wizard_panel/panel.js | grep -c rainCheckParts` > 0 and `.../card.js | grep -c "counted down like"` = 1 (both 0 on `469b9b9`).
- Playwright used: `<scratchpad>/final-fixer/shots.mjs before|after [home,card,zones,wizard,rain]` (`HE=1` for he 320x568) with `lib.mjs`, `accounts-8188.json`. The `rain` scenario POSTs `binary_sensor.rain_detector` (off, device_class moisture); it disappears on restart.
- Tests: `tests/test_v015_final.py` (10 tests). All 10 fail on `469b9b9` (file copied into a detached worktree, run alone), all pass on the fix. Full suite: 479 passed on HA 2026.9 (`venv314`), 470 passed + 9 skipped on HA 2026.2 (`venv`). `node --check` clean on panel.js, card.js, i18n.js.

`<scratchpad>` = `C:/Users/barel/AppData/Local/Temp/claude/D--Code-home-assistant-extensions-good-days/f3802ecc-2b66-432d-963d-f0b1f5d18979/scratchpad`.
