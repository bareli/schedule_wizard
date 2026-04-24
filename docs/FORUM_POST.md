# Forum & Reddit posts

Ready-to-paste drafts for promoting Schedule Wizard. Pick whichever channel.

---

## HA Community Forum — English

**Category:** Third Party Integrations → Custom Integrations
**URL:** https://community.home-assistant.io/c/third-party/custom-components/17

**Title:**
```
[Custom Integration] Schedule Wizard — calendar/time-driven scheduler for irrigation & more
```

**Body:**
```
Hi all,

Just released **Schedule Wizard**, a HACS-installable custom integration that handles cron-style and calendar-driven schedules for any switch/valve/light/cover, with auto-close after a configured duration.

**Why:**
Built-in automations can fire a valve on a schedule, but don't cleanly handle: auto-close after N minutes, a unified "what's running / next" view, per-calendar-event duration, or restart-recovery (leaving the valve open forever after a reboot). Schedule Wizard handles all of those in one integration with its own sidebar UI.

**What's in it:**
- Recurring schedules (HH:MM + days of week + duration) per valve.
- Calendar-driven runs (event summary contains the valve label, description holds minutes).
- Auto-close, with timer recovery across HA restarts.
- Rain skip (weather entity or numeric sensor threshold).
- Webhook trigger for external systems.
- Optional Lovelace card (`custom:schedule-wizard-card`) for dashboard embedding.
- Two sensors: `active_runs` + `next_schedule`.
- Sidebar panel with four editable tabs (Dashboard / Valves / Schedules / Settings).
- Hebrew and English translations out of the box.

**Supported domains:** `switch`, `valve`, `cover`, `input_boolean`, `light` (cover/valve use the correct `open_*` / `close_*` services).

**Install (HACS custom repo, while awaiting default listing):**
1. HACS → ⋮ → Custom repositories
2. URL: `https://github.com/bareli/schedule_wizard`
3. Type: Integration → Add
4. Search "Schedule Wizard" in HACS → Download → restart HA
5. Settings → Devices & Services → + Add Integration → Schedule Wizard

Repo, screenshots, docs: https://github.com/bareli/schedule_wizard

Feedback and issues welcome. Cheers.
```

---

## HA Community Forum — Hebrew

**קטגוריה:** Third Party Integrations → Custom Integrations

**כותרת:**
```
[Custom Integration] Schedule Wizard – מתזמן השקיה/חשמל לפי זמן ויומן
```

**גוף ההודעה:**
```
שלום לכולם,

שחררתי אינטגרציה חדשה בשם **Schedule Wizard** — מתזמן חוזר (שעה + ימי שבוע) + מופעל מאירועי יומן, עם סגירה אוטומטית לאחר משך קצוב. מותקן דרך HACS (כרגע custom repo, PR פתוח ל־default).

**למה:**
האוטומציות הרגילות ב-HA יכולות לפתוח שסתום בלוח זמנים, אבל אין טיפול נקי ב: סגירה אוטומטית לאחר N דקות, תצוגה מאוחדת "מה רץ / מה הבא", משך לאירוע מתוך תיאור אירוע היומן, והתאוששות מהפעלה מחדש (שסתום נשאר פתוח לנצח אחרי ריסטרט). Schedule Wizard מטפל בכל אלה באינטגרציה אחת עם פאנל ייעודי בסיידבר.

**מה יש בפנים:**
- לוחות זמנים חוזרים לכל שסתום (שעה + ימי שבוע + משך).
- הפעלה מיומן (סיכום האירוע מכיל את התווית של השסתום, התיאור מכיל מספר דקות).
- סגירה אוטומטית, עם שחזור טיימרים אחרי ריסטרט של HA.
- דילוג בגשם (דרך ישות מזג אוויר או סף מספרי מחיישן).
- הפעלה דרך Webhook ממערכות חיצוניות.
- כרטיס Lovelace (`custom:schedule-wizard-card`) להטמעה בדשבורד.
- שני חיישנים: `active_runs` + `next_schedule`.
- פאנל סיידבר עם ארבע לשוניות ניתנות לעריכה (דשבורד / שסתומים / לוחות זמנים / הגדרות).
- תרגום לעברית מובנה.

**דומיינים נתמכים:** `switch`, `valve`, `cover`, `input_boolean`, `light`.

**התקנה (כ-custom repo, עד שייכנס ל-HACS default):**
1. HACS → ⋮ → Custom repositories
2. URL: `https://github.com/bareli/schedule_wizard`
3. Type: Integration → Add
4. חיפוש "Schedule Wizard" בתוך HACS → Download → Restart HA
5. Settings → Devices & Services → + Add Integration → Schedule Wizard

ריפו + צילומי מסך + תיעוד: https://github.com/bareli/schedule_wizard

פידבק וצ'קים בלוקאלי יתקבלו בברכה.
```

---

## Reddit r/homeassistant

**URL:** https://reddit.com/r/homeassistant/submit

**Title:**
```
Released Schedule Wizard — HACS integration for calendar/time-driven valve & switch scheduling
```

**Body:**
```
Just published a custom integration for anyone using HA for irrigation, outdoor lighting, pool pumps, or anything that needs "open for N minutes" with auto-close and restart recovery.

**Key points:**
- Cron-style schedules + calendar-driven runs in one place
- Auto-close, survives HA restarts (re-arms remaining timer, not "always on forever")
- Skip runs when it's raining (weather entity or sensor threshold)
- Webhook for external triggers
- Bundled Lovelace card + sidebar panel
- Works on HAOS, Supervised, Container, Core

**Repo:** https://github.com/bareli/schedule_wizard

**Install (while HACS default PR is pending):**
HACS → Custom repositories → add `https://github.com/bareli/schedule_wizard` as Integration.

Feedback welcome. Open issues if anything breaks.
```

---

## Reddit r/homeautomation

Same body as `r/homeassistant` works. Adjust title to mention Home Assistant explicitly since this sub isn't HA-only.

---

## X / Twitter / Mastodon

```
Shipped Schedule Wizard — @home_assistant HACS integration for calendar/time-driven schedules with auto-close, restart recovery, rain skip & webhook triggers.

Irrigation, outdoor lights, pool pumps — anything that needs "open for N minutes" and then close.

github.com/bareli/schedule_wizard
```

(280 char limit OK.)

---

## Do's & Don'ts when posting

- **Do** link the GitHub repo. First thing people want.
- **Do** mention HACS-installable. Removes friction.
- **Do** show the panel screenshot or a GIF in the top of the post if the platform allows.
- **Don't** cross-post within 24 hours (HA forum moderators frown).
- **Don't** ask for upvotes.
- **Don't** promote in unrelated subs.
