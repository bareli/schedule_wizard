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
