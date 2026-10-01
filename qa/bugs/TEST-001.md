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
