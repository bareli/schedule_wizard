# Plan: Schedule Wizard (v0.14.0 risk-based)

IDs are stable forever.

## SCH: schedules
- SCH-01 Weekday schedule still fires at its local time and closes after the duration (regression).
- SCH-02 Every N days: create in the panel (Repeat → Every N days, N, start date); fires on start date and every N days after; not on other days.
- SCH-03 Every N days validation: N outside 2..30, empty / invalid start date, no days picked (weekday mode) → inline error in the panel AND server rejection (services add_schedule / update_schedule with every_n_days, start_date, days).
- SCH-04 Next run: per-zone next run, `sensor.schedule_wizard_next_schedule`, week view and `calendar.schedule_wizard_watering_schedule` include every-N-days runs (month boundary).
- SCH-05 Stored 0.13 schedules load unchanged as weekday schedules; editing one keeps its days.
- SCH-06 Lists / summaries read "Every N days from <date> at <time>" in he / en / de.

## SKIP: temperature adjustment
- SKIP-01 Temperature adjustment Min % = 0 and temperature ≤ low → scheduled zone run and plan run are skipped; history "skipped (temperature 0 %)", event `schedule_wizard_seasonal_skipped`; no device turned on.
- SKIP-02 Factor > 0 % (e.g. 3 % of 10 min) still waters 1 minute (deliberate).
- SKIP-03 "Water now" is never skipped.
- SKIP-04 Settings preview tells the user watering will be skipped at 0 %.

## ENT / COMPAT
- ENT-01 HA 2026.9: zone / plan devices and their switches, sensors, buttons load with no errors in the log; renaming / removing a zone updates / removes its device.
- COMPAT-01 Panel loads on HA 2026.9 (blank-panel fix).

## Full product (cycle 2026-10-01, after v0.14.0)

### SETUP / PANEL
- SETUP-01 First-run setup wizard (zones, first watering time); reopening it later.
- PANEL-01 Six tabs load (Home, Zones, Programs, Reports, Settings + week view); 5 s auto-refresh keeps typing and focus.
- PANEL-02 Zone add / edit / delete (entity change, label, default minutes, rain exempt, moisture, soak), validation both sides.
- PANEL-03 Programs (plans / cycles): steps, reorder, pause / resume / stop, overlap protection.
- PANEL-04 Reports: 30-day chart (local-day buckets), skip tiles, per-plan table, CSV export.
- PANEL-05 Settings: basics + every "More options" group saves live without cancelling running cycles.

### RUN / CAL
- RUN-01 Water now (zone, plan) with auto-close; stop; master valve opens / closes around runs.
- RUN-02 Restart recovery: a run in progress across an HA restart is closed on time (or resumed per design).
- RUN-03 Fail-to-open detection; flow sensor / leak alert.
- CAL-01 Calendar-driven runs (summary contains label, description minutes); all-day events ignored; event removed → pending run cancelled.

### SKIP (existing)
- SKIP-05 Rain skip (weather states / numeric threshold), rain delay (global + per-zone), forecast skip, moisture skip, schedule conditions; each recorded with its reason, no device change.

### ENT / VOICE / WEBHOOK / NOTIFY
- ENT-02 All entities: zone switch + time left + water used, plan switch + run-now button, watering binary sensor, rain-delay switch (+ until), calendar, active runs / next schedule sensors; names in the HA language.
- VOICE-01 Assist intents en / he / de: water a zone N minutes, start plan, stop, skip today, pause N days, what's watering.
- HOOK-01 Webhook start / stop with entity and minutes; wrong id 404 / unsupported domain rejected.
- NOTIFY-01 Notifications per event type, translated; known: rain / moisture / forecast skip notifications English-only (v0.14.1 candidate).

### I18N / MOBILE / CARD
- I18N-02 en / he (RTL) / de across the panel; plural forms ("1 runs" known bug).
- MOBILE-01 320x568 every tab; forms reachable; no horizontal scroll.
- CARD-01 Lovelace card: zones, quick run (minutes input stable), next run, errors.

## v0.16.0 (cycle 2026-10-09)

### TIP: weather tips
- TIP-01 Tips card shows rain / heat / frost for today (runs still to come) and tomorrow from the daily forecast: numbers, units (°C / °F), runs named, litres or minutes saved, forecast source.
- TIP-02 Apply each tip: rain skips the day's outdoor runs; frost skips outdoor runs before 10:00; heat waters +X % that day only (boost); the tip disappears; the user can undo (week run Undo skip, boost Cancel).
- TIP-03 Not now (dismiss), Don't suggest (mute) and Settings "Suggest again"; tips off; thresholds saved and applied; no rain tip while the automatic rain-forecast skip is on.
- TIP-04 Evening digest: notify event "Weather tips" + a target; at the digest time one notification; mobile action buttons; a TIP action event applies the tip; forged / malformed actions change nothing; a forecast change replaces or clears the notification.
- TIP-05 After an HA restart the forecast (and tips) appear within minutes, not after 30.

### BOOST / ONCE: temporary changes
- BOOST-01 Water more / less chooser (+20..-30 %, 1-7 days) → banner; scheduled and calendar runs scaled; Water now not scaled; End now / Cancel.
- ONCE-01 Run dialog "This time only": new time the same day and/or percent; week shows "changed for this day"; the run fires only at the new time with the new minutes; Undo change; time already passed today and dates beyond 31 days refused.

### WEEK / CONF / QUEUE
- WEEK-01 Week list: estimated minutes arrow (temperature today / tomorrow, boost), litres per day, weather line, likely-skipped rain tag, overlap tag, "+ Add" on an empty day opens the editor with that weekday.
- WEEK-02 Timeline view: day chips, a lane per zone, runs far apart get their own axis, overlaps red, a bar opens the run dialog; RTL mirrored; 320 px.
- CONF-01 Schedule editor warns about runs at the same time (add and edit, zone and plan, weekdays and every N days, sunrise) with a "Move to" suggestion; saving still allowed.
- QUEUE-01 Zones at once = 1: overlapping scheduled runs wait their turn and then start; Water now never waits; status card says who is waiting; give-up after 3 h records skipped_overlap.

### REP / TZ / ZONE
- REP-01 Reports: "Skips saved N min and about X L" over 30 days.
- TZ-01 Browser time zone different from HA's: Home, Zones, Plans, schedule editor, week list, timeline and run dialog all show HA's clock; a note says so.
- ZONE-01 Zone card on the Zones tab while the zone waters says "Watering now, X left", not "no runs last 7 days".
