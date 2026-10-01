# UX verification recipes (learned verifying #64-#73, 2026-10-01)

- **Prove a wizard-made schedule fires** without waiting for sunrise: a second wizard run with one zone, a set time
  2-3 min ahead, 1 min. Watch `state_changed` + `schedule_wizard_*` events over WS (read with a timeout, see
  live-restart-checks.md). A rain source that is currently rainy turns the fire into a skip: set it dry first.
- **Rain sources without hardware:** `POST /api/states/weather.home {"state":"rainy"}`,
  `sensor.rain_today` (`device_class: precipitation`), `binary_sensor.rain_detector` (`device_class: moisture`).
  They vanish on restart; `DELETE /api/states/<id>` afterwards.
- **A foreign switch for picker tests:** `POST /api/states/switch.garden_pump` shows up in `get_state.controllable`
  (no registry entry, so not "own"). Proves own switches are filtered while normal switches stay, and the order.
- **First weekday:** dispatch `hass-first-weekday-select` (detail `"monday"`) on `home-assistant`. HA saves the whole
  locale (including `language`) to user data `language`, which then overrides the `selectedLanguage` localStorage
  that `lib.mjs` sets. Restore with `frontend/set_user_data key=language value=null` (null was the original on 8173).
- **Card text:** the card's shadow root holds a `<style>`; read screenshots or `ha-card` innerText, not textContent.
- **Wizard / editor day chips:** in the time editor the first `select` is the target (zone / plan); pick the Repeat
  select by `option[value=weekdays]`. In the plan card `.times .btn.small` is Skip next, Edit time, Delete time.
- **History cannot be cleaned** through the API: rows created by a verification stay (they also feed the
  "Last watering" line and Reports counts of later runs on the same instance).
- **Bash heredocs with backticks** (Markdown code spans) must be quoted (`<<'EOF'`); long Hebrew comment bodies were
  safer through the Write tool.

## Added 2026-10-01 (final batch verification, #66 #67 #91-#97)

- **Rain check line reads states as they were when Settings rendered.** POST the test state (binary_sensor on, weather rainy)
  *before* opening the panel, or re-selecting the source still shows the old "Now:". A state that changes while Settings is
  open is not reflected until the page re-renders.
- **A skip row on demand:** set `rain_entity` to a binary_sensor that is `on`, `add_schedule` for a spare zone at now+2 min on
  today's weekday, wait for `schedule_wizard_rain_skipped` over WS (about 2 min), then `remove_schedule` and clear `rain_entity`.
- **A saved own rain source (#91):** only reachable through `.storage/core.config_entries` with HA stopped (the server refuses
  new ones). Back the file up first; the option is cleared again with `update_options rain_entity ""`.
- **8172 history has `cancelled` rows without `planned_min`** (written before #52 by an older build, holding the planned
  length): they inflate "Last watering" / day totals (130 min on 2026-10-01). Do not read that number as a regression of new code.

## Added 2026-10-01 (verify #98-#102 on 8172)

- **Playwright over the panel:** the panel's own text is in a shadow root; read `.tabs` `getRootNode().children` `innerText`. The Home tab holds Recent activity and Reports (toggle button "Reports"); Plans, Zones, Settings are tabs 2, 1, 3. `qa/tools` WS helper needs the venv python (aiohttp), not `py -3`.
- **`node x.mjs` with `python -` before it in one command hangs** reading stdin; always `</dev/null`.
- **Wizard walk:** Plans -> "+ New watering plan": the last dialog button on step 4 is "Save plan" (a single zone creates a zone time, not a plan). Stop at Check and press Cancel.
- **Voice end state:** WS `conversation/process {text, language}` then `get_state.active[].duration_min`; stop with `call_service schedule_wizard.stop_all`.
- **Legacy `cancelled` rows without `planned_min`** already exist in the 8172 store (10 rows, 128 min), enough to check #101 without editing `.storage`.
