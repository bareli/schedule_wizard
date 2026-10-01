# Live restart checks on the dev instances (learned verifying #54, 2026-10-01)

- **Unavailable valve without hardware:** a YAML `template:` switch whose `state` follows an input_boolean
  ("backing") and whose `availability` follows another input_boolean declared with `initial: false`
  (always `off` after a restart). Merge new input_booleans into the existing `input_boolean:` block:
  a second top-level key silently replaces the zones.
- **A template switch re-adds with its restored state first** (`on` ~200 ms before
  `unavailable`). Schedule Wizard sets up in between, so it sees `on`, not `unavailable`. To get a truly
  missing state at load, start with the switch block absent (keep one dummy template sensor so the
  integration loads) and add it afterwards with `template.reload`.
- **Graceful stop:** WS `call_service homeassistant.stop` (the client sees a connection reset; that is
  expected), wait until no `python.exe` with `haconfig-<port>` in its command line, edit `.storage` only then.
- **HA refuses entity services to unavailable entities** (log: "Referenced entities ... are missing or not
  currently available"); a close command can be lost without any error in Schedule Wizard.
- The recorder (`home-assistant_v2.db`, read-only sqlite, `states` join `states_meta`) gives
  millisecond state order; use it to tell what Schedule Wizard saw at setup.
- `qa/tools/ha_ws.py` truncates replies at 2000 chars: dump full `schedule_wizard/get_state` with your own
  client and `PYTHONIOENCODING=utf-8` (Hebrew names).
- Playwright: log in once and reuse `storageState`; per-context logins race HA's redirect to `/auth/`.
- Clean up after: restore `configuration.yaml`, restart, and remove orphaned registry entries
  (`config/entity_registry/remove`).

## Added 2026-10-01 (v0.15.0 verification pass)

- **Check for a second instance on the same config first.** Two `ha_launch.py -c haconfig-8171` trees were found running
  (the second in recovery mode, port taken, but sharing `.storage` and the log). Kill the extra tree before testing.
- **Long idle WS clients get dropped.** aiohttp answers HA's pings only while `receive()` runs; a script that `sleep`s
  ~2 min on an open connection gets "Cannot write to closing transport". Idle by reading with a timeout instead.
- **Restart from a script: start HA with `Start-Process` and all std handles to DEVNULL.** If the launcher inherits the
  script's stdout pipe, the pipe stays open for the life of HA and `| grep | tee` never returns.
- **Restart without the IDE task:** `homeassistant.stop` via WS, poll `Get-CimInstance` until no `haconfig-<port>` process,
  then `Start-Process` (venv python, `PYTHONPATH=<scratch>`) and wait for `/api/` 401 plus a successful `get_state`.
  An instance started with the Bash tool's background mode dies with the agent; a `Start-Process` one survives.
- **Template switch rows:** `stop_all` / `remove_valve` on a zone whose valve is unavailable leaves a `pending_closes`
  entry (by design since #80). Clear it from `.storage` (HA stopped) when removing test switches.
- **Scale data without YAML:** `input_boolean/create` (`PZ01`..`PZ20`) and `input_boolean/delete` need no restart.

## Added 2026-10-01 (polish batch verification, #87 / #88 / #89)

- **A pending close without YAML:** run a zone, `POST /api/states/input_boolean.zone_<x> {"state":"unavailable"}`, then
  `stop_valve` -> "close ... not delivered" and the entry is in `.storage` at once. `POST ... {"state":"on"}` is the valve
  coming back; the pending close then turns the real input_boolean off.
- **Stop races:** send `homeassistant.stop` on an already-open WS right after the `POST`. Read the real gap from the recorder
  (`events` `schedule_wizard_valve_ended` vs `homeassistant_stop`, ms). `asyncio.sleep(0.02)` on Windows gave ~34 ms
  (timer granularity): use 0 and ~10 ms to land inside a 0-20 ms window.
- **8172 restarts in ~3 s** (stop) + ~3 s (start to `get_state`) with `Start-Process -WindowStyle Hidden` and stdout/stderr
  redirected to scratchpad files.
- **Notification text per language without restarting:** WS `config/core/update {"language":"de"}` changes `hass.config.language`
  live even though `configuration.yaml` sets `language: he`; restore it afterwards. Read the texts with notify target
  `persistent_notification` and WS `persistent_notification/subscribe` (first event lists all current ones).
- **Legacy history rows:** inject only with HA stopped, back the store up first, and remove the row again the same way.
