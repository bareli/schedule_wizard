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
