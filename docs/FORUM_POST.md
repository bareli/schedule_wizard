# Forum & Reddit posts

Ready-to-paste drafts for announcing Schedule Wizard. Updated for v0.13.0. Attach `docs/demo.gif` and the screenshots in `docs/screenshots/`.

---

## HA Community Forum: English

**Category:** Third Party Integrations → Custom Integrations
**URL:** https://community.home-assistant.io/c/third-party/custom-components/17

**Title:**
```
[Custom Integration] Schedule Wizard: irrigation scheduler with setup wizard, voice, rain forecast and water tracking
```

**Body:**
```
Hi all,

Schedule Wizard is a free, open-source (MIT) irrigation scheduler for Home Assistant. It works with any switch, valve, light, cover or input_boolean, and has its own sidebar panel, so you don't need to write automations.

**Getting started takes a minute:** a setup wizard asks which switches are your zones, what to call them, which days and time, and whether to water one zone at a time. Done.

**Watering**
- Watering plans (zones one after another) and single-zone schedules, any days, any time
- Calendar-driven runs from any HA calendar
- Cycle & soak for slopes and clay: short bursts with pauses, and while one zone soaks the plan waters the next
- Seasonal adjustment by outdoor temperature
- Plans resume where they left off after an HA restart

**Skipping when it makes sense**
- Rain sensor or weather state, and rain forecast (skip if N mm expected in the next hours)
- Soil moisture, global or per zone
- Rain delay for all zones or one zone; indoor zones (greenhouse, balcony) keep watering
- Per-schedule conditions on any entity

**Safety and insight**
- Main valve / pump support, check that zones really opened
- Flow meter: leak alert when nothing should be watering, high flow while watering (burst pipe), low flow (clogged filter)
- Water used per zone, in litres, ready for the Energy dashboard
- Reports with 30-day chart and CSV export, Repairs warnings when an entity goes missing

**Home Assistant native**
- Entities per zone and plan: water/stop switch, time left, plan on/off, run button, calendar of upcoming runs
- Voice through Assist in English, German and Hebrew: "water the front lawn for 10 minutes", "stop watering", "skip watering today"
- Reminder notification with Skip today / Water now buttons
- This week view with skip and undo per run
- Panel in 17 languages, including right-to-left for Hebrew and Arabic

**Install:** HACS → ⋮ → Custom repositories → `https://github.com/bareli/schedule_wizard` (Integration) → Download → restart → Settings → Devices & Services → Add Integration → Schedule Wizard.

Repo, screenshots, docs: https://github.com/bareli/schedule_wizard

Feedback and issues welcome. Native speakers: corrections to the panel translations are very welcome.
```

---

## HA Community Forum: Hebrew

**קטגוריה:** Third Party Integrations → Custom Integrations

**כותרת:**
```
[Custom Integration] Schedule Wizard: מתזמן השקיה עם אשף הגדרה, שליטה קולית, תחזית גשם ומדידת מים
```

**גוף:**
```
היי לכולם,

Schedule Wizard הוא מתזמן השקיה חינמי וקוד פתוח ל־Home Assistant. עובד עם כל מתג, ברז, תאורה, תריס או input_boolean, ויש לו פאנל משלו בסרגל הצד, בלי לכתוב אוטומציות.

**ההגדרה לוקחת דקה:** אשף שואל אילו מתגים הם אזורי ההשקיה, איך לקרוא להם, באילו ימים ובאיזו שעה, והאם להשקות אזור אחרי אזור. זהו.

**השקיה**
- תוכניות השקיה (אזורים ברצף) ותזמונים לאזור בודד, כל יום וכל שעה
- הפעלה לפי לוח שנה של HA
- השקיה וספיגה למדרונות ואדמה כבדה: פרצים קצרים עם הפסקות, ובזמן שאזור אחד סופג התוכנית משקה את הבא
- התאמה עונתית לפי טמפרטורה
- תוכנית שנקטעה באתחול של HA ממשיכה מאיפה שעצרה

**דילוג כשצריך**
- חיישן גשם או מצב מזג אוויר, וגם תחזית גשם (דילוג אם צפויים X מ״מ בשעות הקרובות)
- לחות קרקע, כללית או לכל אזור
- השהיית גשם לכל האזורים או לאזור אחד; אזורים פנימיים (חממה, מרפסת) ממשיכים להשקות
- תנאים לכל תזמון על כל ישות

**בטיחות ומידע**
- ברז ראשי / משאבה, בדיקה שהברז באמת נפתח
- מד זרימה: התראת דליפה כשלא אמורה להיות השקיה, זרימה גבוהה (צינור פרוץ), זרימה נמוכה (מסנן סתום)
- צריכת מים לכל אזור בליטרים, מוכן ללוח האנרגיה
- דוחות עם גרף 30 יום וייצוא CSV, התראות בתיקונים כשישות נעלמת

**משתלב ב־Home Assistant**
- ישויות לכל אזור ותוכנית: מתג השקיה, זמן שנותר, הפעלה/כיבוי תוכנית, כפתור הפעלה, לוח שנה של ההשקיות הקרובות
- שליטה קולית דרך Assist בעברית, אנגלית וגרמנית: "תשקה את הדשא 10 דקות", "עצור את ההשקיה", "דלג על ההשקיה היום"
- התראת תזכורת עם כפתורי "דילוג היום" ו"השקיה עכשיו"
- תצוגת "השבוע" עם דילוג וביטול לכל השקיה
- הפאנל ב־17 שפות, כולל מימין לשמאל בעברית

**התקנה:** HACS → ⋮ → Custom repositories → `https://github.com/bareli/schedule_wizard` (Integration) → Download → אתחול → הגדרות → מכשירים ושירותים → הוספת אינטגרציה → Schedule Wizard.

קוד, צילומי מסך ותיעוד: https://github.com/bareli/schedule_wizard

אשמח למשוב ולדיווחי באגים.
```

---

## Reddit r/homeassistant

**Title:**
```
I built a free irrigation scheduler for HA: setup wizard, voice control, rain forecast skip, leak alerts and water tracking
```

**Body:**
```
Schedule Wizard is an open-source HACS integration with its own sidebar panel. A 5-step wizard sets up your zones and watering plan, then it handles the rest: rain and forecast skip, soil moisture, cycle & soak (waters the next zone while one soaks), flow-meter leak and low-flow alerts, water used per zone for the Energy dashboard, plans that resume after a restart, Assist voice commands (EN/DE/HE), reminder pushes with Skip / Water now buttons, and native HA entities for every zone and plan. Panel in 17 languages.

GIF and docs: https://github.com/bareli/schedule_wizard
```

---

## X / short

```
Schedule Wizard v0.13 for Home Assistant: irrigation made simple. Setup wizard, rain forecast skip, cycle & soak, leak alerts, water per zone, voice via Assist, 17 languages. Free on HACS. https://github.com/bareli/schedule_wizard
```
