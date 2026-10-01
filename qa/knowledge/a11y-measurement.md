# Accessibility measurement traps (learned verifying #42-#50, 2026-10-01)

- **Contrast must include `opacity`.** Computed `color` + composited `background-color` ignores ancestor
  `opacity`. `.wk-run.past` is drawn at 0.55: its text measured 6.5:1 without opacity and 2.45:1 with it.
  Blend each opacity group over its backdrop before computing the ratio.
- **`color-mix()` colours:** read them by painting the computed value onto a 1x1 canvas and reading the
  pixel; string parsing of `color(srgb ...)` is fragile.
- **Playwright `ariaSnapshot` nesting can mislead.** It showed the Reports "Daily values" table indented
  under the chart's `role=img` (which would make it presentational). CDP `Accessibility.getFullAXTree`
  showed it is a sibling in a `<details>` group. Settle "is it hidden from AT" with CDP, not the snapshot.
- **The card lives in shadow roots.** `querySelectorAll("schedule-wizard-card button.run")` never matches
  across the shadow boundary; query inside the shadow root (or with a bare selector on the card page).
  The card on `/sw-card/0` needs about 4 s after load before its buttons exist.
- **RTL overflow goes right of `scrollWidth` too:** check the page scroll range (`scrollLeft` clamped
  between -1000 and 1000), not only elements with `right > viewport`. A `.sr-only` element with
  `margin:-1px` and no inset gives 1 px of scroll in RTL only.
- A test entity for keyboard-only "add zone" checks: WS `input_boolean/create` (name "QA a11y verify"),
  then `remove_valve` + `input_boolean/delete` afterwards. Every real input_boolean on 8172 is already a zone.
- `unskip` needs both `schedule_id` and `date`; the pending skips are in `get_state` → `skips`.
- **Card picker (HA 2026.9):** the card registers `preview: true`, so Edit dashboard -> Add card -> "By card" shows a live
  preview and never the `description`. Read the description from `window.customCards`. The dialog opens on "By entity";
  click the "By card" tab (`getByRole("tab", { name: /by card|לפי כרטיס|nach karte/i })`).
- **Card at 320 in German:** the zone-name column shrinks to ~51 px and long sub-lines (`Regenverzögerung`) run under the
  minutes field (seen 2026-10-01, not filed). Check de, not only en / he, when judging the card at 320.
