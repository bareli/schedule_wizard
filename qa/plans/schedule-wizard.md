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
