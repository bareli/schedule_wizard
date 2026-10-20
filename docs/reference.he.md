# מדריך עזר

כל השירותים מופיעים ב**כלי פיתוח ← פעולות** עם כל הבוררים.

## שירותים

| שירות | מטרה |
| --- | --- |
| `schedule_wizard.run_valve` | פותח ישות למשך `duration_minutes` ונסגר אוטומטית בסוף. |
| `schedule_wizard.stop_valve` | סוגר ישות עכשיו ומבטל את הטיימר שלה. |
| `schedule_wizard.add_valve` | רושם או מעדכן אזור (מזהה ישות, שם, משך ברירת מחדל; אופציונלית שדות ספיגה ולחות). |
| `schedule_wizard.remove_valve` | מסיר אזור ומוחק את לוחות הזמנים שלו. |
| `schedule_wizard.add_schedule` | מוסיף לוח זמנים חוזר: `time` (או `time_mode` של זריחה / שקיעה עם `sun_offset_minutes`), `days` או `every_n_days` (2 עד 30) עם `start_date` אופציונלי, משך, אזור או מחזור, ו-`conditions` אופציונלי. מחזיר את המזהה החדש. |
| `schedule_wizard.update_schedule` | מעדכן לוח זמנים לפי מזהה. |
| `schedule_wizard.remove_schedule` | מוחק לוח זמנים לפי מזהה. |
| `schedule_wizard.add_cycle` | יוצר מחזור: רשימה מסודרת של שלבים `{entity_id, duration_minutes}`. |
| `schedule_wizard.update_cycle` | מעדכן מחזור. |
| `schedule_wizard.remove_cycle` | מוחק מחזור ואת לוחות הזמנים שמצביעים עליו. |
| `schedule_wizard.run_cycle` | מפעיל מחזור עכשיו; האזורים רצים בזה אחר זה. |
| `schedule_wizard.stop_cycle` | מבטל מחזור שרץ. |
| `schedule_wizard.pause_cycle` | משהה מחזור: האזור הנוכחי נסגר והשאר ממתינים. |
| `schedule_wizard.resume_cycle` | ממשיך מחזור מושהה. |
| `schedule_wizard.set_rain_delay` | מדלג על השקיות מתוזמנות ומיומן למשך N שעות (`hours`); כל האזורים, או רשימת `entity_id`. |
| `schedule_wizard.clear_rain_delay` | מנקה את ההשהיה הכללית, או רק את ההשהיה של רשימת `entity_id`. |
| `schedule_wizard.stop_all` | עוצר כל אזור, רצף ספיגה ומחזור, ואז סוגר את הברז הראשי. |
| `schedule_wizard.skip_next` | מדלג על ההשקיה הבאה של לוח זמנים (`schedule_id`, ו-`date` אופציונלי). |
| `schedule_wizard.skip_day` | מדלג על כל ההשקיות בתאריך (`date`, ברירת מחדל: שארית היום). |
| `schedule_wizard.unskip` | מבטל דילוג (`schedule_id`, `date`). |
| `schedule_wizard.run_schedule` | מפעיל עכשיו את האזור או התוכנית של לוח זמנים וגורע ממנו את ההשקיה המתוזמנת של היום. |
| `schedule_wizard.set_override` | משנה השקיה אחת בתאריך (עד 31 ימים קדימה): `time` חדש באותו יום ו/או `percent` (25 עד 300) מהדקות שלה. |
| `schedule_wizard.clear_override` | מבטל את השינוי של השקיה אחת (`schedule_id`, `date`). |
| `schedule_wizard.set_boost` | משקה `percent` (‎-50, ‎-30, ‎-20, 10, 20, 30 או 50) יותר או פחות בכל השקיה מתוזמנת למשך `days` (1 עד 14). |
| `schedule_wizard.clear_boost` | מסיים את התוספת או ההפחתה. |
| `schedule_wizard.apply_tip` | מבצע את מה שטיפ מזג אוויר מציע (`tip_id`, למשל `rain:2026-10-10`). |
| `schedule_wizard.dismiss_tip` | מסתיר טיפ אחד. |
| `schedule_wizard.mute_tip` | עוצר (או עם `muted: false` מחדש) טיפים מסוג `kind`: rain, heat או frost. |
| `schedule_wizard.list_config` | מחזיר כתשובה את האזורים, לוחות הזמנים, המחזורים, ההשקיות הפעילות וההיסטוריה האחרונה. |

מגבלות: שמות עד 80 תווים; לכל היותר 200 אזורים, 200 זמני השקיה ו-200 תוכניות. מתקבלות רק ישויות מסוג `switch`, `valve`, `cover`, `input_boolean` ו-`light`.

### דוגמאות

הפעלת אזור מסקריפט:

```yaml
service: schedule_wizard.run_valve
data:
  entity_id: switch.front_lawn_valve
  duration_minutes: 15
```

הוספת אזור ולוח זמנים:

```yaml
- service: schedule_wizard.add_valve
  data:
    entity_id: switch.front_lawn_valve
    label: Front lawn
    default_duration_minutes: 12

- service: schedule_wizard.add_schedule
  data:
    valve_entity_id: switch.front_lawn_valve
    time: "06:30"
    duration_minutes: 12
    days: [mon, wed, fri]
```

השקיה כל יומיים, החל מתאריך מסוים:

```yaml
- service: schedule_wizard.add_schedule
  data:
    valve_entity_id: switch.front_lawn_valve
    time: "06:00"
    duration_minutes: 10
    every_n_days: 2
    start_date: "2026-10-05"
```

קבלת המזהה של לוח הזמנים החדש במשתנה תשובה:

```yaml
- service: schedule_wizard.add_schedule
  data:
    valve_entity_id: switch.front_lawn_valve
    time: "19:00"
    duration_minutes: 8
    days: [tue, thu]
  response_variable: created
- service: system_log.write
  data:
    message: "New schedule id: {{ created.schedule.id }}"
```

## ישויות { #entities }

לכל אזור ולכל תוכנית יש מכשיר משלו. הישויות מופיעות, משנות שם ונעלמות לפי העריכה של האזורים והתוכניות.

| ישות | מה היא עושה |
| --- | --- |
| `switch.<zone>_watering` | דלוק בזמן שהאזור משקה. הדלקה משקה את דקות ברירת המחדל, כיבוי עוצר. |
| `sensor.<zone>_time_left` | דקות שנותרו (0 במנוחה). |
| `sensor.<zone>_water_used` | ליטרים שנצרכו (סכום עולה). |
| `switch.<plan>_enabled` | תוכנית דולקת או כבויה. כבויה: לוחות הזמנים שלה לא רצים. |
| `button.<plan>_run_now` | מפעיל את התוכנית עכשיו. |
| `binary_sensor.schedule_wizard_watering` | דלוק בזמן שמשהו משקה. |
| `switch.schedule_wizard_rain_delay` | דלוק בזמן שהשהיית גשם פעילה. הדלקה משהה ל-24 שעות. |
| `calendar.schedule_wizard_watering_schedule` | ההשקיות הקרובות, ביומן של Home Assistant. |
| `sensor.schedule_wizard_active_runs` | מספר האזורים שמשקים; התכונה `runs` מפרטת אותם. |
| `sensor.schedule_wizard_next_schedule` | תווית ההשקיה המתוזמנת הבאה; התכונות כוללות `valve_entity_id`, `cycle_id`, `schedule_id`, `duration_min`, `fires_in_minutes`. |
| `sensor.schedule_wizard_water_used` | סך הליטרים. |

התקנות שקדמו לגרסה 0.8.0 עשויות לשמור על המזהים הישנים `sensor.active_runs` ו-`sensor.next_schedule`.

## אירועים

האינטגרציה שולחת את האירועים האלה לפס האירועים של Home Assistant. השדה `source` מציין איך ההשקיה התחילה (`schedule`, `calendar`, `manual`, `service`, `webhook`, `cycle:<id>`).

| אירוע | מתי |
| --- | --- |
| `schedule_wizard_valve_started` | אזור נפתח. |
| `schedule_wizard_valve_ended` | אזור נסגר (`status`: ‏`completed` או `cancelled`). |
| `schedule_wizard_cycle_started` | מחזור מתחיל. |
| `schedule_wizard_cycle_ended` | מחזור מסתיים או מבוטל. |
| `schedule_wizard_rain_skipped` | השקיה דולגה בגלל גשם. |
| `schedule_wizard_moisture_skipped` | השקיה דולגה כי האדמה רטובה. |
| `schedule_wizard_condition_skipped` | התנאים של לוח זמנים לא התקיימו. |
| `schedule_wizard_seasonal_skipped` | השקיה דולגה: ההתאמה לטמפרטורה היא 0 אחוז. |
| `schedule_wizard_valve_soaking` | השקיה וספיגה נעצרה בין מקטעים. |
| `schedule_wizard_leak_detected` | התראת זרימה (`kind`: ‏`leak` או `high_flow`). |
| `schedule_wizard_low_flow` | אזור קיבל הרבה פחות מים מהרגיל. |
| `schedule_wizard_valve_failed_to_open` | בדיקת הפתיחה זיהתה כשל. |
| `schedule_wizard_rain_delay_set` | השהיית גשם הופעלה או נוקתה. |
| `schedule_wizard_cycle_skipped_overlap` | מחזור מתוזמן דולג בזמן שמחזור אחר רץ. |

### דוגמאות לאוטומציות

```yaml
alias: "Irrigation: log cycle completion"
trigger:
  - platform: event
    event_type: schedule_wizard_cycle_ended
action:
  - service: system_log.write
    data:
      message: >
        Cycle {{ trigger.event.data.name }} ended with status
        {{ trigger.event.data.status }} (source: {{ trigger.event.data.source }})
```

```yaml
alias: "Alert on cancelled valve"
trigger:
  - platform: event
    event_type: schedule_wizard_valve_ended
    event_data:
      status: cancelled
action:
  - service: notify.mobile_app_my_phone
    data:
      title: "Irrigation"
      message: "{{ trigger.event.data.label }} was cancelled mid-run"
```

## אפשרויות

| מפתח | ברירת מחדל | תיאור |
| --- | --- | --- |
| `calendar_entity` | אין | ישות היומן לבדיקה. |
| `calendar_lookahead_min` | 10 | כמה דקות קדימה לחפש אירועים מתאימים. |
| `poll_interval` | 60 | תדירות בדיקת היומן בשניות (10 עד 3600). |
| `calendar_keyword` | אין | רק אירועים שהכותרת שלהם מתחילה במילה הזו משקים. עד 40 תווים. |
| `max_external_minutes` | 120 | ההשקיה הארוכה ביותר שאירוע ביומן או קריאת webhook יכולים להפעיל (1 עד 1440). |
| `default_duration` | 10 | משך ברירת מחדל כשלאזור אין משך משלו. |
| `rain_entity` | אין | ישות מזג אוויר, חיישן או binary_sensor לגשם. |
| `rain_skip_states` | `rainy,pouring,snowy,lightning-rainy` | מדלגים כשהמצב תואם אחד מאלה. |
| `rain_attribute` | אין | תכונה לקריאה במקום המצב. |
| `rain_threshold` | אין | סף מספרי. מדלגים כשהערך שווה לו או גבוה ממנו. ריק או 0 כבוי. |
| `flow_entity` | אין | חיישן זרימה לזיהוי דליפה. |
| `flow_leak_threshold` | 0 | התראת דליפה כשהזרימה מעל הערך הזה ואין השקיה. 0 כבוי. |
| `flow_max_running` | 0 | התראת זרימה גבוהה מעל הערך הזה בזמן השקיה. 0 כבוי. |
| `flow_delay_sec` | 60 | התנאי צריך להימשך כל כך הרבה שניות לפני התראה. |
| `flow_stop_all` | false | בהתראה, לעצור את כל ההשקיה ולסגור את הברז הראשי. |

## שפות

הלוח והכרטיס פועלים בשפה של פרופיל המשתמש ב-Home Assistant: אנגלית, גרמנית, עברית, ספרדית, צרפתית, איטלקית, הולנדית, פורטוגזית, רוסית, אוקראינית, פולנית, ערבית, סינית מפושטת, שוודית, דנית, נורווגית (בוקמול) ופינית. בעברית ובערבית כל הלוח והכרטיס עוברים לתצוגה מימין לשמאל. שפות אחרות חוזרות לאנגלית. אנגלית, גרמנית ועברית נבדקו; השאר תורגמו במכונה, ותיקונים יתקבלו בברכה.
