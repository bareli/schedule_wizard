# Changelog

## 0.15.0: security and reliability fixes

- **Webhook only runs your zones** (#34, #37): the webhook used to switch any switch, light, cover, valve or input_boolean in Home Assistant, including ones that are not zones, and recorded runs for entities that do not exist. It now accepts only zones set up in Schedule Wizard (`404 unknown zone` otherwise, nothing switched or recorded) and refuses to run a disabled zone (`409`). Automations that call the webhook for a zone keep working; calls for other entities stop working.
- **Webhook URL for administrators only, and a New URL button** (#35): non-admin users no longer receive the webhook ID or the notification targets from the panel or the `list_config` service. Settings → More options → Webhook has **New URL**, which replaces the secret; the old URL stops working at once.
- **Webhook errors** (#36): a body that is not a JSON object, a non-text or unknown `action`, or a bad `entity_id` now gets `400` with a short message; unexpected errors return `internal error` instead of Python exception text.
- **Main valve must be a valve** (#40): Settings accepts only an existing switch, valve, light, cover or input_boolean as main valve / pump, checked in the panel and on the server. A main valve of another domain saved earlier (for example a script) is ignored and logged instead of being turned on and off around every run.
- **Calendar runs match whole words in the event title** (#38): a calendar event starts a zone only when its title contains the zone name as a whole word (case does not matter); the description and location no longer count, and a 1 or 2 letter zone name must be the whole title. "Front lawns" or "Storefront" no longer start the zone "Front". If your calendar auto-accepts invitations, use a dedicated calendar for watering.
- **Input limits** (#39): names and labels are capped at 80 characters, at most 200 zones, 200 watering times and 200 plans; the Skip day button in a notification only accepts a real date; history CSV cells that start with `=`, `+`, `-` or `@` are escaped so spreadsheets do not run them.
- **A valve stays under control across a restart** (#54): if a zone was watering when Home Assistant restarted and its switch was not available yet when Schedule Wizard loaded, the run was dropped and the valve could stay open. The run is now kept and the valve is closed at its planned end, or as soon as it reports in if that time has passed.
- **Keyboard focus is kept** (#41): the panel and the card no longer throw keyboard focus back to the top of the page every 5 seconds or after pressing a button; after Water now, focus moves to that zone's Stop.
- **Messages are visible** (#51): errors (for example Save with an empty zone name) and confirmations now show on screen, inside the open dialog when there is one, also in Hebrew and on narrow phones.
- **Deleted plans keep their name in history** (#57) instead of showing an internal id; older rows show "Deleted plan".
- "1 run" instead of "1 runs" in the zone summary, in all 17 languages (#56).
- **Bigger touch targets** (#58): on phones and tablets the week view's Skip day, the panel menu button and text fields are at least 44 px high.
- **Readable colours** (#45, #81): the card's "1 running" pill and past runs in the week view now reach 4.5:1 contrast in light and dark themes; past runs are greyed with a muted colour instead of see-through.
- **Messages in dialogs** (#83): an error now shows right under the dialog title instead of over it, and pressing Save again replaces the message instead of stacking another one.
- **Card** (#84, #85): the card picker describes the card in your language; after Stop, keyboard focus moves to that zone's Water now (and back to Stop after Water now).
- **Screen readers** (#82, #86): no more 1 px sideways scroll in Hebrew on narrow screens; Settings' More options and each option group are announced with their names.
- **Run history kept on shutdown** (#87): a valve closed late (it was unavailable at the run's end) keeps its "completed" row even if Home Assistant stops at that moment, and the row is never written twice.
- **German and other languages** (#88): voice replies say "1 Minute" / "1 Tag" (also English and Hebrew singular), and numbers in notifications use the language's decimal comma, for example "1,5 Std.".
- **Totals include replaced runs** (#89): when Water now replaces a running zone, the minutes the first run watered now count in Reports and the zone summary (rows from before 0.15.0 are left out, they hold the planned length).
- **Reports say the period** (#90): the per-zone columns read "Last 7 days" and "Last 30 days" instead of "7d" / "30d".
- **Rain source check line** (#66): a rain binary sensor now reads "Skips while the sensor is on. Now: off." instead of the weather states; a sensor that reports a number points to the numeric threshold under More options.
- **Schedule Wizard's own sensors are no rain source** (#91): they are left out of the rain source list and refused on save (one saved earlier keeps working).
- **Last watering** (#67): the line above the zones shows when the most recent real watering finished (completed, or stopped after watering some minutes), not a start that was cancelled; a later skip reads "Skipped (rain), today 6:00 AM".
- **Each zone's own start** (#94): in a plan that waters one zone at a time, zone cards and the card show when that zone starts (for example 6:00, 6:10, 6:25 AM), following cycle & soak, instead of the plan's start for every zone.
- **No runs from before a plan existed** (#93): a plan created in the evening no longer shows this morning's run as a past run in This week or the watering calendar.
- The every-N-days "First run" line uses the same time format as the rest of the page ("6:00 AM", #92); the card counts down in whole units like the panel ("in 3d" for 3 days 12 hours, #95); the zone card's button reads "Delete zone" (#96).
- **Hebrew "one minute" by voice**: "השקה את הגינה למשך דקה" and "...דקה אחת" now water for 1 minute instead of the zone's default.
- **Card in German on a narrow phone**: long words such as "Regenverzögerung" wrap inside the zone's text column; at 320 px the minutes field and button move to their own line under the name.
- **Times in plan lists** and in the wizard's Check step use the same clock format as the rest of the page ("6:00 AM" or "6:00") instead of the stored "06:00".
- **Stopped runs from before 0.15.0** (#101): a run stopped in 0.14.x was saved with its planned length, so the Last watering line, day totals, Reports and the zone summary counted it at full length (for example 130 min when 2 min watered). Its minutes are now left out, like replaced runs from before 0.15.0; it still counts as a run.
- **Rain check line stays current** (#102): in Settings the "Now:" under the rain source follows the sensor when you pick it again and when its state changes, without redrawing the form.

## 0.14.0: water every N days, 0 % temperature adjustment skips the run

- **Every N days** (#27): a watering time can repeat every 2 to 30 days from a start date, as an alternative to days of the week. Same time, zone or plan, skips and conditions as before. Pick it in the editor under **Repeat**; lists show "Every 2 days from ... at ...". Runs follow your HA time zone's calendar days, so they keep their clock time across daylight saving changes. Next-run times, the week view, the watering calendar and the next schedule sensor include these runs. Services `add_schedule` / `update_schedule` take `every_n_days` and `start_date` (default today). Existing schedules are unchanged.
- **0 % means no watering** (#26): with the temperature adjustment at 0 %, scheduled and calendar runs of zones and plans are skipped instead of watering 1 minute. History, the event (`message`) and the notification all say "skipped: temperature adjustment 0 % (too cool)" (#31), the notification in your HA language (17 languages); skipped rows no longer show the planned minutes (`skipped_seasonal_zero`, event `schedule_wizard_seasonal_skipped`, notification `skipped_seasonal`). Any factor above 0 % keeps the 1-minute minimum; 0.5 % rounds up to 1 % on both server and panel. The Settings preview says when watering would be skipped, and Min % says "0 = no watering".
- **Cool-day warning** (#29): while the temperature factor is 0 %, Home shows "Scheduled watering paused: too cool" and the week view tags today's and tomorrow's runs "will be skipped (cool)"; past runs skipped this way are marked skipped.
- **Reports** (#32): Skip reasons gained **Temperature** and **Other** tiles, so the skip tiles add up to all skipped runs.
- **Every N days editor** (#30, #33): the date field is now **First watering on**, with a live line "First run: Sat, Oct 3 06:00, then every 2 days" that also says when today's time has already passed. Option "Every 2 to 30 days" and label "Days between waterings"; entering 1 points to Days of the week. Save stays visible at the bottom of long forms on small screens. Percent signs read "0 %" consistently (attached in Hebrew, Arabic and Chinese).
- The watering time editor now shows its errors next to the field (no days picked, N outside 2 to 30, missing start date); the server checks the same rules, and `add_schedule` now rejects an empty `days` list.
- Fixed (#28): an every-N-days schedule whose start date was more than 31 days away showed no next run (zone card, Home, next schedule sensor, watering calendar state, Skip next). The search now starts at the start date.
- Fixed: the panel could stay blank when Home Assistant handed it its data before it finished loading (seen on HA 2026.9).
- Fixed for **Home Assistant 2026.9**: zone and plan devices used two device-registry calls that HA 2026.9 deprecated (`via_device`, `async_get_device`), so their switches, sensors and buttons could fail to load. Zone and plan devices are no longer linked under the hub device (cosmetic); everything else is unchanged and still works down to HA 2024.7.

## 0.13.0: rain forecast, water usage, smarter cycle & soak, resume after restart, 17 languages

- **Rain forecast skip**: skip outdoor zones when your weather forecast expects N mm or more in the next 6 to 48 hours (Settings → More options). New history status `skipped_forecast`.
- **Plans resume after a restart**: a watering plan interrupted by an HA restart or update continues with its next zone if HA is back within 30 minutes; paused plans stay paused. Valves are no longer turned off during HA shutdown, so the running zone finishes its time.
- **Repairs warnings** when a zone switch or a sensor used in Settings is missing, cleared automatically once fixed.
- **Diagnostics download** for bug reports (webhook ID and notify targets redacted).
- **Water usage**: litres per run and per zone, measured by the flow meter (units converted) or estimated from a zone's flow rate. New sensors `sensor.<zone>_water_used` and `sensor.schedule_wizard_water_used` for the Energy dashboard; litres in Reports, history and CSV.
- **Low-flow warning**: a zone that gets under half its usual flow fires `schedule_wizard_low_flow` and a `low_flow` notification.
- **Smarter cycle & soak**: in a watering plan, the next zone waters while one soaks, so plans finish much sooner (can be turned off).
- **Panel in 17 languages**: added Spanish, French, Italian, Dutch, Portuguese, Russian, Ukrainian, Polish, Arabic (right-to-left), Simplified Chinese, Swedish, Danish, Norwegian and Finnish (machine translations, corrections welcome).
- Fixed: Norwegian setup screens never loaded (translation file was `no.json`; Home Assistant uses `nb`).

## 0.12.0: Home Assistant entities, voice control, week view, reminder buttons

- **Entities**: a device per zone (`switch.<zone>_watering`, `sensor.<zone>_time_left`) and per plan (`switch.<plan>_enabled`, `button.<plan>_run_now`), plus `binary_sensor.schedule_wizard_watering`, `switch.schedule_wizard_rain_delay` and `calendar.schedule_wizard_watering_schedule`. Added, renamed and removed live as you edit.
- **Voice (Assist)** in English, German and Hebrew: water a zone (for N minutes), start a plan, stop watering, skip today, pause for N days, ask what's watering. Can be turned off.
- **This week** on Home: upcoming runs for 7 days with skip / undo per run, skip a whole day, water now.
- **Reminders**: optional push N minutes before a run with **Skip today** and **Water now** buttons (HA Companion app).
- New services `skip_next`, `skip_day`, `unskip`, `run_schedule`; new history status `skipped_manual`.

## 0.11.0: simpler panel with a setup wizard

- **Setup wizard**: pick your switches, name the zones, choose days, time and minutes, and the order. It creates the zones, the watering plan and its schedule in one go.
- **New Home tab**: one status card (watering now, paused for rain, or next run), a card per zone with minutes and Water now, Pause for rain for all zones or one zone, Stop watering, recent activity folded away.
- **Four tabs instead of six**: Home, Zones, Programs, Settings. Schedules now show inside their zone or plan; Reports opens from Home.
- **Plain wording**: zones and watering plans instead of valves and cycles; entity IDs only in small print.
- **Settings**: three essentials up front, every other feature in its own "More options" group with a one-line explanation and an On/Off indicator.
- All new text in English, German and Hebrew (right-to-left).

## 0.10.0: panel and card in German and Hebrew, right-to-left layout

- **Panel and Lovelace card translated** into German and Hebrew (#3). The language follows your HA profile; unknown languages fall back to English.
- **Right-to-left layout** for Hebrew: the whole panel and card mirror, entity IDs and times stay readable inside Hebrew text.
- Dates, times and weekdays are formatted in your locale and HA time zone (12/24h per your profile), including the next-run labels.
- Settings save message no longer claims the integration reloads (options apply live since 0.8.0).
- Translation completeness test (`tests/test_i18n.py`).

## 0.9.0: per-valve rain delay, indoor valves, panel menu button

- **Per-valve rain delay** (#4): `set_rain_delay` / `clear_rain_delay` take an optional `entity_id` list. The Dashboard rain delay card has an "Apply to" picker and lists delayed valves with their own Clear button.
- **Indoor valves** (#4): new valve option `rain_exempt`. The global rain delay and rain skip don't apply to indoor valves. Cycles mixing indoor and outdoor valves still run during a global delay, skipping only the outdoor steps (`skipped_rain_delay`).
- **Menu button** in the panel header when the HA sidebar is hidden (narrow screens, desktop app), so you can get back to the rest of Home Assistant (#4).
- Per-step rain and moisture skips inside a cycle now only apply to scheduled and calendar cycles; manually started cycles run every step, matching the docs.
- `schedule_wizard_rain_skipped` and the other skip events now carry a `reason` field; `rain_delay_set` carries `entity_ids` for per-valve delays.

## 0.8.0: cycle & soak, per-valve moisture, schedule conditions, leak detection + 20 bug fixes

### New
- **Cycle & soak** per valve: split long schedule, calendar and cycle runs into chunks (max run) with soak pauses. Dashboard shows the soak countdown; the master valve closes while soaking. New event `schedule_wizard_valve_soaking`.
- **Per-valve moisture sensor**: overrides the global moisture skip for that zone; checked per step inside cycles (wet zone skipped, cycle continues).
- **Schedule conditions**: up to 10 entity/attribute conditions per schedule (`above`, `below`, `equals`, `not_equals`); the run is skipped unless all hold. New event `schedule_wizard_condition_skipped`, notify event `skipped_condition`.
- **Flow sensor leak detection**: leak alert (flow with no valve running) and high-flow alert (above a max while watering), with a delay and optional stop-all + master close. New event `schedule_wizard_leak_detected`, notify event `leak_detected`, Dashboard banner.
- **Stop all** service and Dashboard button.
- Notify events `skipped_moisture` and `skipped_condition`.
- Automated test suite (pytest-homeassistant-custom-component) running in CI.

### Fixed
- Master valve never opened for cycles (#6).
- HA "Configure" dialog wiped all advanced settings made in the panel (#7).
- Rain threshold of 0 made numeric rain sensors skip every schedule; 0 now means "off" as the UI says (#8).
- Saving settings or setting/clearing a rain delay reloaded the integration and cancelled running and paused cycles; options now apply live (#9).
- Stopping a cycle during fail-detection or master pre-open left the valve open forever (#10).
- Paused cycle held the master valve open; stopping a paused cycle never closed it or logged it (#11).
- Calendar events found ahead of time skipped seasonal adjustment, rain skip, moisture skip, fire-time rain delay and overlap checks (#12). Behaviour change: rain and moisture skip now apply to calendar runs too.
- Pending calendar triggers were never cancelled: deleted/moved events still fired (#13).
- All-day calendar events could run a valve for 24 hours; they are now ignored (#14).
- The same valve could be started twice by two triggers in the same minute (#15).
- Next-run times used the server time zone instead of HA's (#16).
- Calendar events could be missed when the poll interval exceeded the lookahead (#17).
- Sensors now belong to a "Schedule Wizard" device, so new installs get `sensor.schedule_wizard_active_runs` / `sensor.schedule_wizard_next_schedule` as documented (#18).
- Panel/card auto-refresh stopped after the element was re-attached (#19).
- A failed refresh on the Settings tab left a permanent error screen (#20).
- Editing a valve's entity deleted the old valve even when adding the new one failed; schedules are now migrated to the new entity (#21).
- Reports 30-day chart bucketed by UTC day (#22).
- Card quick-run minutes reset every 5 seconds (#23).
- Backend minor (#24): webhook `stop` accepted any domain and unbounded durations; dead GET branch removed; `update_options` now requires admin; calendar description parsing only takes minutes (`15 min`, `15 דקות`, or a bare number) instead of the first number; superseded runs are logged; step numbers after resume are correct; `add_schedule` rejects unregistered valves; options-flow entity pickers accept empty values.
- Frontend minor (#25): CSV notes double-escaped and no UTF-8 BOM (Hebrew garbled in Excel); clearing a seasonal field silently disabled seasonal; cycle steps pointing at deleted valves; card errors only in the console; in-place row updates matched by label; seasonal preview requested all states on each keystroke.
- A valve that fails to open is now turned off again.

## 0.7.4 — fix quick-run duration input resetting

- Fixed the per-valve "minutes" box on the Dashboard resetting to the default duration while typing. The 5-second auto-refresh focus guard used `document.activeElement`, which returns the shadow host inside Home Assistant's panel, so the guard never matched and every refresh re-rendered the input. It now walks the shadow-root chain to find the real focused element.
- Quick-run durations are now remembered per valve for the session, so a re-render (after running or stopping a valve) no longer discards the typed value.

## 0.7.3 — fresh README screenshots

- Refreshed all panel screenshots in the README to reflect the new tabs (Cycles, Reports), rain delay button, advanced toggle, and per-valve stats.

## 0.7.2 — Reports tab + README sync + UI spacing

- **New Reports tab** in the panel:
  - 30-day total-minutes-per-day mini bar chart.
  - Per-valve totals: 7d / 30d / lifetime runs and minutes.
  - Per-cycle totals (last 30d): completed / cancelled / skipped / total.
  - Skip reasons summary: rain / moisture / overlap / failed / cancelled.
  - **Export CSV** button: full history download.
- History capacity raised from 100 to 500 entries. Older entries still trimmed FIFO.
- README updated with all v0.6 + v0.7 features (cycles, rain delay, master valve, fail detection, pause/resume, services, events).
- Added bottom margin to header rows (`+ Add` buttons in Valves / Cycles / Schedules) so they don't touch the list below.

## 0.7.1 — fix get_state crash on rain_delay_until

- Fixed `AttributeError: 'dict' object has no attribute 'options'` in the WebSocket `get_state` handler when reading `rain_delay_until`. Reads from the cached options dict instead of trying to access a non-existent `entry` variable.

## 0.7.0 — rain delay, master valve, fail detection, cycle pause/resume, Settings basic/advanced

- **Rain delay** button on Dashboard: pause all schedule + calendar runs for 24h / 48h / 7d, with one-tap clear. New services `set_rain_delay` and `clear_rain_delay`.
- **Master valve / pump** option: a central valve that auto-opens before the first zone runs and auto-closes after the last zone closes. Optional pre-open delay for pump pressurization.
- **Fail-to-open detection**: after issuing a turn-on, verify entity reaches an "on" state within N seconds. If not, log error, fire `schedule_wizard_valve_failed_to_open`, send notification.
- **Cycle pause / resume**: pause an in-progress cycle (current valve closes, remaining steps held) and resume from where it left off. New services `pause_cycle`, `resume_cycle`. New events `cycle_paused`, `cycle_resumed`.
- **Settings: Basic / Advanced split**: Settings tab opens with just calendar fields visible. "Show advanced" reveals rain skip, seasonal, moisture, master valve, fail detection, notifications, cycle overlap.
- New notification event types: `valve_failed`, `rain_delay`.
- "10m" → "10min" everywhere in the dashboard for clarity.
- **Recent activity** groups cycle runs with their valve openings indented under the parent cycle.

## 0.6.4 — fix cycle never starting + blocking I/O

- Fixed: cycle task started eagerly before being added to the active-cycles map (HA 2024.7+ `async_create_task` runs eagerly). The task saw "not in active_cycles" and exited immediately, leaving a phantom step-0 entry. Now adds to the map first, then starts the task.
- Fixed: blocking `open()` on `manifest.json` from the event loop. Version is now read once via the executor and cached.

## 0.6.3 — list_config completeness + cycle skip diagnostics

- `schedule_wizard.list_config` service now also returns `cycles`, `active_cycles`, and `options` (previously missing).
- Cycle steps that are skipped due to missing `entity_id` or zero duration now log a warning with the cycle id, step number, and computed values, making "stuck on step 0" much easier to diagnose.

## 0.6.2 — next opening time per valve

- Dashboard Quick run, Valves tab, and Lovelace card now show the next scheduled opening per valve with time label and countdown (`Next: Wed 06:00 (in 18h)`).
- Computed from direct valve schedules AND schedules targeting a cycle that contains the valve.

## 0.6.1 — clearer seasonal UI

- Seasonal section shows temperature unit (°C or °F) taken from HA config on all threshold labels.
- Added inline explanation of how Low/High/Min%/Max% interact.
- Live preview: reads the configured temperature entity/attribute and shows "current temp → factor → example 10-min schedule length" — updates as you edit fields.

## 0.6.0 — seasonal adjust, moisture skip, overlap guard, valve stats

- **Seasonal adjustment** (temperature-scaled): scales schedule and calendar durations between a low and high temp threshold, clamped to min/max percent. Manual runs unaffected.
- **Soil moisture skip**: skip cron/calendar when moisture sensor ≥ threshold (soil already wet). Independent of rain.
- **Cycle overlap protection**: when off (default), schedule/calendar cycles skip while another cycle is running. Opt-in via `allow_concurrent_cycles`.
- **Per-valve stats** on Valves tab: last run timestamp + status + duration, plus runs / minutes in the last 7 days.
- New events: `schedule_wizard_moisture_skipped`, `schedule_wizard_cycle_skipped_overlap`.
- Schedule/calendar runs whose duration was adjusted record `|seasonal:N%` in the history note.

## 0.5.1 — event bus events

- Fires 5 events on the HA event bus, usable as automation triggers:
  - `schedule_wizard_valve_started`
  - `schedule_wizard_valve_ended`
  - `schedule_wizard_cycle_started`
  - `schedule_wizard_cycle_ended`
  - `schedule_wizard_rain_skipped`
- Each event carries `source` so you can filter schedule / calendar / manual / webhook / cycle triggers in automations.
- README documents event names, data fields, and example automations.

## 0.5.0 — multi-language translations

- 15 new translation files for HA native strings (config flow + options flow + service names/descriptions): Spanish, German, French, Italian, Dutch, Portuguese, Russian, Arabic, Polish, Simplified Chinese, Ukrainian, Swedish, Danish, Norwegian, Finnish.
- Existing English and Hebrew translations extended with all new services (cycles, update_schedule).
- Panel UI text (sidebar tabs, buttons, modals) still English; JavaScript i18n is deferred.

## 0.4.2 — preserve input focus across auto-refresh

- Panel Dashboard and Lovelace card no longer destroy DOM on the 5s auto-refresh when an input/select is focused. Progress bars still update smoothly in place.
- Typing in the minutes number box stays put.

## 0.4.1 — fix Run button + inline progress

- Run buttons in the Lovelace card were always disabled due to `setAttribute("disabled", "false")` being truthy in HTML. Internal `el()` helper now skips boolean-false attributes and emits bare attributes for boolean-true.
- Dashboard Quick run rows now show an inline progress bar + remaining time when a valve is active.
- Lovelace card: per-valve progress bar + remaining time inline in each row.

## 0.4.0 — notifications

- Pick one or more `notify.*` services (e.g. HA Companion mobile app) and choose which events push notifications: `valve_start`, `valve_end`, `cycle_start`, `cycle_end`, `skipped_rain`.
- Panel Settings tab has a new Notifications section with checkbox list of detected notify services + event toggles.
- Options flow (Devices & Services → Schedule Wizard → Configure) also exposes the same fields.
- Notifications are fire-and-forget; failures log a warning but don't block valve actions.

## 0.3.0 — cycles (zone sequencing)

- **Cycles**: new first-class object. Define an ordered list of (valve, duration) steps and run them sequentially as a single program. Perfect for irrigation zone sequencing.
- Services: `add_cycle`, `update_cycle`, `remove_cycle`, `run_cycle`, `stop_cycle`.
- Schedules can now target a cycle instead of a single valve (panel target picker + `cycle_id` field on `add_schedule`).
- Calendar events match cycle names too (summary contains the cycle name → whole cycle fires).
- Panel: new **Cycles** tab with step editor (reorder, add, remove). Dashboard shows active cycles with step progress.
- Rain skip applies to cycle schedules (whole cycle skipped on rain).

## 0.2.4 — edit schedules from the panel

- Schedules tab now has Edit + Enable/Disable + Delete buttons per row.
- New service `schedule_wizard.update_schedule` (patch existing schedule by id; any omitted field unchanged).
- Edit modal patches in place via the new service (no delete + recreate); valve selection is locked while editing.

## 0.2.3 — fix Settings tab input wipe

- 5-second panel auto-refresh no longer re-renders the Settings tab, so typing in the rain-entity / threshold / webhook fields is preserved. Settings re-renders only on tab switch or after Save.

## 0.2.2 — cache-bust panel and card

- Panel `module_url` and Lovelace card resource URL now include `?v=<version>` so browsers always fetch the matching JS after an update. Stops stale UI without manual hard-refresh.

## 0.2.1 — panel rain fields + webhook URL

- Settings tab in the sidebar panel now exposes rain-skip configuration (entity, skip states, attribute, threshold).
- Settings tab now shows the webhook URL with one-click copy.

## 0.2.0 — rain skip, webhook, Lovelace card, Hebrew

- **Rain skip**: options flow now accepts a rain/weather entity + skip states / threshold / attribute. Schedules skip automatically when rain condition is active; history logs `skipped_rain`.
- **Webhook trigger**: integration registers a per-entry webhook. `POST /api/webhook/<id>` with `entity_id` (and optional `duration_minutes`, `action: run|stop`) fires a run or stop.
- **Lovelace card** (`custom:schedule-wizard-card`): compact active runs + quick run/stop widget, auto-registered as a Lovelace module resource.
- **Hebrew translation** (`translations/he.json`) for config flow, options flow, and services.
- Options flow extended with rain configuration fields.
- WebSocket `update_options` command now accepts rain fields.

## 0.1.1 — branding

- Real brand assets: `icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png` (sprinkler + calendar, "Irrigation Schedule").
- Placeholder "SW" text icons replaced.

## 0.1.0 — initial release

- HACS custom integration (in-process Python, works on all HA install types).
- Cron-style schedules per valve (HH:MM + days of week + duration).
- Calendar-driven runs (label match in event summary, minutes in description).
- Auto-close after configured duration.
- Active-run persistence across HA restarts (re-arms timers based on entity state and remaining time).
- Services: `run_valve`, `stop_valve`, `add_valve`, `remove_valve`, `add_schedule`, `remove_schedule`, `list_config`.
- Sensors: `active_runs` (with per-run details) and `next_schedule`.
- Sidebar panel with tabs: Dashboard, Valves, Schedules, Settings (all editable).
- Single-instance config flow + options flow for calendar and defaults.
- Supports `switch`, `valve`, `cover`, `input_boolean`, `light` domains.
- Persistent storage via HA `Store` helper at `<config>/.storage/schedule_wizard.data`.
