# התקנה

גרסת Home Assistant מינימלית: **2024.7.0**.

## התקנה עם HACS (מומלץ)

=== "חיפוש ב-HACS"

    1. פותחים את **HACS** ומחפשים **Schedule Wizard**.
    2. נכנסים לאינטגרציה ולוחצים **Download**.

=== "מאגר מותאם אישית (אם החיפוש לא מוצא)"

    1. ב-HACS: ⋮ ← **Custom repositories**.
    2. מוסיפים את `https://github.com/bareli/schedule_wizard` בקטגוריה **Integration**.
    3. מחפשים **Schedule Wizard** ב-HACS ולוחצים **Download**.

אחר כך:

1. **מפעילים מחדש את Home Assistant.**
2. נכנסים אל **הגדרות ← מכשירים ושירותים ← הוספת אינטגרציה ← Schedule Wizard**.
3. ערך **Schedule Wizard** (עם סמל ממטרה) מופיע בסרגל הצד. פותחים אותו ומתחילים באשף ההגדרה.

## התקנה ידנית

1. מעתיקים את התיקייה `custom_components/schedule_wizard/` מהמאגר אל `<config>/custom_components/`.
2. מפעילים מחדש את Home Assistant.
3. מוסיפים את האינטגרציה מהממשק, כמו בצעד 2 למעלה.

## כדאי לדעת

- אפשר להוסיף רק מופע אחד.
- כרטיס Lovelace נרשם אוטומטית, אין צורך להוסיף משאב ידנית.
- הנתונים נשמרים בקובץ `<config>/.storage/schedule_wizard.data` כ-JSON רגיל, ולכן הם נכללים בכל גיבוי מלא של Home Assistant.
