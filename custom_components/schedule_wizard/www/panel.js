const I18N = await import(new URL("./i18n.js" + new URL(import.meta.url).search, import.meta.url).href);

const STYLES = `
:root, :host {
  --sw-bg: var(--primary-background-color, #f5f7fa);
  --sw-card: var(--card-background-color, #fff);
  --sw-text: var(--primary-text-color, #1f2933);
  --sw-muted: var(--secondary-text-color, #6b7280);
  --sw-primary: var(--primary-color, #03a9f4);
  --sw-border: var(--divider-color, #e5e7eb);
  --sw-danger: var(--error-color, #dc2626);
  --sw-success: var(--success-color, #16a34a);
  --sw-warn: var(--warning-color, #b45309);
  /* Text and fills derived from the theme colours (BUG-005, BUG-006): HA's default tokens are too light for
     text (#009ac7 on white is 3.1:1, #ffa600 1.9:1). Text mixes toward the theme's text colour, so it gets
     darker in a light theme and lighter in a dark one; fills under white text mix toward black. */
  --sw-primary-text: var(--sw-primary);
  --sw-success-text: var(--sw-success);
  --sw-danger-text: var(--sw-danger);
  --sw-warn-text: var(--sw-warn);
  --sw-primary-fill: var(--sw-primary);
  --sw-success-fill: var(--sw-success);
  --sw-danger-fill: var(--sw-danger);
}
@supports (color: color-mix(in srgb, red 50%, blue)) {
  :root, :host {
    --sw-primary-text: color-mix(in srgb, var(--sw-primary) 65%, var(--sw-text));
    --sw-success-text: color-mix(in srgb, var(--sw-success) 60%, var(--sw-text));
    --sw-danger-text: color-mix(in srgb, var(--sw-danger) 70%, var(--sw-text));
    --sw-warn-text: color-mix(in srgb, var(--sw-warn) 40%, var(--sw-text));
    --sw-primary-fill: color-mix(in srgb, var(--sw-primary) 75%, #000);
    --sw-success-fill: color-mix(in srgb, var(--sw-success) 75%, #000);
    --sw-danger-fill: color-mix(in srgb, var(--sw-danger) 80%, #000);
  }
}
* { box-sizing: border-box; }
.app {
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px;
  color: var(--sw-text);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
}
.topbar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.topbar h1 { margin: 0; font-size: 22px; font-weight: 500; }
.title-wrap { display: flex; align-items: center; gap: 4px; }
.menu-btn {
  background: transparent; border: none; padding: 8px; margin-inline-start: -8px;
  cursor: pointer; color: var(--sw-text); border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
}
.menu-btn:hover { background: var(--sw-border); }
.menu-btn svg { width: 24px; height: 24px; fill: currentColor; }
.tabs {
  display: flex; gap: 2px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--sw-border);
  overflow-x: auto; scrollbar-width: none;
}
.tab {
  flex: 0 0 auto;
  background: transparent; border: none;
  padding: 10px 14px; cursor: pointer;
  color: var(--sw-muted); font: inherit; font-weight: 500;
  border-bottom: 2px solid transparent; white-space: nowrap;
}
.tab.active { color: var(--sw-primary-text); border-bottom-color: var(--sw-primary); }
.card {
  background: var(--sw-card);
  border: 1px solid var(--sw-border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.card h2 { margin: 0 0 12px; font-size: 16px; font-weight: 500; }
.section-h { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; margin: 4px 0 10px; }
.section-h h2 { margin: 0; font-size: 18px; font-weight: 500; }
.row-between { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.list { display: flex; flex-direction: column; gap: 8px; }
.empty { color: var(--sw-muted); font-style: italic; padding: 8px 0; }
.empty-state { text-align: center; padding: 32px 16px; display: grid; gap: 12px; justify-items: center; }
.empty-state h2 { font-size: 20px; margin: 0; }
.empty-state p { margin: 0; max-width: 460px; }
.item {
  display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: center;
  padding: 10px 12px; border: 1px solid var(--sw-border); border-radius: 8px; background: var(--sw-bg);
}
.name { font-weight: 500; font-size: 15px; }
.sub { color: var(--sw-muted); font-size: 12px; }
.small { font-size: 13px; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.btn {
  min-height: 24px;
  padding: 7px 14px; border: 1px solid var(--sw-border);
  background: var(--sw-card); color: var(--sw-text);
  border-radius: 999px; cursor: pointer; font: inherit; font-size: 14px; font-weight: 500;
  transition: all 0.15s;
}
.btn:hover:not(:disabled) { border-color: var(--sw-primary); color: var(--sw-primary-text); }
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.btn.primary { background: var(--sw-primary-fill); color: #fff; border-color: var(--sw-primary-fill); }
.btn.primary:hover:not(:disabled) { filter: brightness(1.1); color: #fff; }
.btn.danger { color: var(--sw-danger-text); border-color: var(--sw-danger); background: transparent; }
.btn.danger:hover:not(:disabled) { background: var(--sw-danger-fill); border-color: var(--sw-danger-fill); color: #fff; }
.btn.ghost { border-color: transparent; background: transparent; color: var(--sw-primary-text); padding-inline: 8px; }
.btn.small { padding: 4px 10px; font-size: 12px; }
.link-btn { min-height: 24px; background: none; border: none; color: var(--sw-primary-text); cursor: pointer; font: inherit; font-size: 13px; padding: 4px 0; text-decoration: underline; }
button:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible { outline: 2px solid var(--sw-primary); outline-offset: 2px; }
.field { display: block; margin-bottom: 12px; }
.field > span {
  display: block; font-size: 12px; font-weight: 600;
  margin-bottom: 4px; color: var(--sw-muted);
}
.field input, .field select, .field textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--sw-border);
  border-radius: 8px;
  background: var(--sw-card);
  color: var(--sw-text);
  font: inherit;
}
.field input[type="checkbox"] { width: auto; }
.field-error { color: var(--sw-danger-text); font-size: 12px; margin-top: 4px; }
.field input[aria-invalid="true"] { border-color: var(--sw-danger); }
/* Pinned to the physical top left with no negative margin (BUG-021): with margin -1px and no inset its static
   position in RTL sat 1 px past the right edge and scrolled the page sideways. */
.sr-only {
  position: absolute; top: 0; left: 0; width: 1px; height: 1px; padding: 0; margin: 0;
  overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; border: 0;
}
.modal [hidden] { display: none !important; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.progress-wrap { height: 8px; background: var(--sw-border); border-radius: 999px; overflow: hidden; }
.progress-bar { height: 100%; background: var(--sw-primary); border-radius: inherit; transition: width 0.5s linear; }
.pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 500;
  background: var(--sw-border); color: var(--sw-muted); white-space: nowrap;
}
.pill.run { background: rgba(3,169,244,0.15); color: var(--sw-primary-text); }
.pill.pause { background: rgba(180,83,9,0.15); color: var(--sw-warn-text); }
.pill.ok { background: rgba(22,163,74,0.15); color: var(--sw-success-text); }
.pill.idle { background: transparent; border: 1px solid var(--sw-border); }
.status { display: grid; gap: 12px; }
.status-row { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; }
.status-title { font-size: 20px; font-weight: 500; margin: 6px 0 2px; overflow-wrap: anywhere; }
.status.rain { border-color: var(--sw-warn); background: rgba(180,83,9,0.07); }
.rain-chooser { display: grid; gap: 8px; padding-top: 12px; border-top: 1px solid var(--sw-border); }
.rain-chooser select { padding: 6px 8px; border: 1px solid var(--sw-border); border-radius: 8px; background: var(--sw-card); color: var(--sw-text); font: inherit; max-width: 100%; }
.zones { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; margin-bottom: 14px; }
.zone { display: grid; gap: 10px; align-content: start; margin-bottom: 0; }
.zone.running { border-color: var(--sw-primary); }
.zone-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.zone-head strong { font-weight: 500; font-size: 16px; min-width: 0; overflow-wrap: anywhere; }
.stepper { display: inline-flex; align-items: center; border: 1px solid var(--sw-border); border-radius: 999px; }
.stepper button { border: 0; background: none; color: var(--sw-text); width: 32px; height: 34px; font-size: 18px; cursor: pointer; border-radius: 999px; font-family: inherit; }
.stepper button:hover { color: var(--sw-primary-text); }
.stepper-val { min-width: 58px; text-align: center; font-variant-numeric: tabular-nums; font-size: 14px; }
details > summary { cursor: pointer; font-weight: 500; }
.log { list-style: none; padding: 0; margin: 12px 0 0; display: grid; gap: 8px; font-size: 14px; }
.log li { display: flex; justify-content: space-between; gap: 12px; }
.log .when { color: var(--sw-muted); white-space: nowrap; font-size: 12px; }
.log .kids { color: var(--sw-muted); font-size: 12px; margin-inline-start: 14px; }
.admin-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap; }
.admin-body { display: grid; gap: 8px; margin-top: 10px; }
.sched-row {
  display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 8px 10px; border: 1px solid var(--sw-border); border-radius: 8px; background: var(--sw-bg);
  font-variant-numeric: tabular-nums;
}
.switch { width: 42px; height: 24px; border-radius: 999px; background: var(--sw-border); border: 0; position: relative; cursor: pointer; flex: 0 0 auto; }
.switch::after { content: ""; position: absolute; inset-block-start: 3px; inset-inline-start: 3px; width: 18px; height: 18px; border-radius: 50%; background: #fff; transition: inset-inline-start .15s; }
.switch[aria-checked="true"] { background: var(--sw-primary-fill); }
.switch[aria-checked="true"]::after { inset-inline-start: 21px; }
.chain { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 14px; }
.chain .sep { color: var(--sw-muted); }
.muted { color: var(--sw-muted); }
bdi { unicode-bidi: isolate; }
.num { text-align: end; }
.num .water { display: block; color: var(--sw-primary-text); font-size: 12px; }
.report-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 13px; font-variant-numeric: tabular-nums; }
.report-table th, .report-table td {
  padding: 6px 4px; border-bottom: 1px solid var(--sw-border); text-align: start; vertical-align: top;
  overflow-wrap: anywhere; hyphens: auto;
}
.report-table thead th { font-size: 12px; font-weight: 600; color: var(--sw-muted); }
.report-table tbody th { font-weight: 400; }
.report-table .num { text-align: end; }
.chart-values { margin-top: 8px; }
.chart-values .report-table { margin-top: 6px; }
.badge {
  display: inline-block; margin-inline-start: 6px; padding: 1px 6px;
  border-radius: 4px; font-size: 11px; font-weight: 500;
  background: var(--sw-border); color: var(--sw-muted); vertical-align: middle;
}
.badge.warn { background: rgba(180,83,9,0.15); color: var(--sw-warn-text); }
.wk-wrap { container-type: inline-size; }
.week { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; }
.wk-day { display: grid; gap: 6px; align-content: start; min-width: 0; padding: 8px; border: 1px solid var(--sw-border); border-radius: 10px; background: var(--sw-bg); }
.wk-day.today { border-color: var(--sw-primary); }
.wk-head { display: flex; justify-content: space-between; align-items: center; gap: 4px; flex-wrap: wrap; }
.wk-head strong { font-weight: 500; font-size: 14px; margin-inline-end: 4px; }
.wk-head .btn { padding: 2px 6px; font-size: 12px; min-height: 24px; }
.wk-runs { display: flex; flex-direction: column; gap: 6px; }
.wk-run {
  display: grid; gap: 1px; width: 100%; text-align: start; cursor: pointer;
  padding: 6px 8px; border: 1px solid var(--sw-border); border-radius: 8px;
  background: var(--sw-card); color: var(--sw-text); font: inherit; font-size: 13px;
}
.wk-run:hover { border-color: var(--sw-primary); }
.wk-run .t { font-weight: 600; font-variant-numeric: tabular-nums; }
.wk-run .n { overflow-wrap: anywhere; }
/* Past runs: muted text, not opacity (BUG-020): they are still buttons, and opacity took the text under 4.5:1. */
.wk-run.past { color: var(--sw-muted); }
.wk-run.skipped .t, .wk-run.skipped .n { text-decoration: line-through; color: var(--sw-muted); }
.wk-run.rain { border-color: var(--sw-warn); background: rgba(180,83,9,0.07); }
.wk-tag { font-size: 11px; font-weight: 500; color: var(--sw-muted); }
.wk-run.rain .wk-tag, .wk-tag.warn { color: var(--sw-warn-text); }
.times { display: grid; gap: 8px; padding-inline-start: 10px; border-inline-start: 3px solid var(--sw-border); }
.times-h { margin: 4px 0 0; font-size: 13px; font-weight: 600; color: var(--sw-muted); }
.seg { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 8px; }
.seg .btn[aria-pressed="true"] { background: var(--sw-primary-fill); border-color: var(--sw-primary-fill); color: #fff; }
.act-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.act-head h2 { margin: 0; }
.act-day { margin: 10px 0 0; font-size: 13px; font-weight: 600; display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.act-day .muted { font-weight: 400; }
.log li.skip > div:first-child { color: var(--sw-muted); }
.last-line { margin: -4px 0 12px; font-size: 14px; }
.check-line { font-size: 12px; margin: 4px 0 0; line-height: 1.45; }
.check-line.warn { color: var(--sw-danger-text); }
.switch-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.voice-ex { margin: 4px 0 12px; padding-inline-start: 20px; display: grid; gap: 4px; font-size: 14px; font-style: italic; }
@container (max-width: 860px) {
  .week { grid-template-columns: 1fr; }
  .wk-day { grid-template-columns: minmax(96px, 22%) 1fr; align-items: start; }
  .wk-head { flex-direction: column; align-items: flex-start; }
  .wk-runs { flex-direction: row; flex-wrap: wrap; }
  .wk-run { flex: 1 1 150px; width: auto; }
}
.alert-banner {
  padding: 12px 14px; margin-bottom: 14px; border-radius: 10px;
  background: var(--sw-danger-fill); color: #fff; font-weight: 600;
}
/* One row of seven at 320 px too (UX-017), in the order the user's week runs. */
.days { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 4px; max-width: 420px; }
.day-chip {
  min-width: 0; height: 36px; padding: 0 2px; border: 1px solid var(--sw-border);
  border-radius: 999px; cursor: pointer; font: inherit; font-size: 13px; font-weight: 500;
  background: var(--sw-card); color: var(--sw-text);
}
.day-chip[aria-pressed="true"] { background: var(--sw-primary-fill); border-color: var(--sw-primary-fill); color: #fff; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
  padding: 8px;
}
.modal {
  background: var(--sw-card); color: var(--sw-text); border-radius: 12px; padding: 20px;
  max-width: 460px; width: calc(100% - 32px);
  max-height: 85vh; overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.modal h3 { margin: 0 0 14px; font-size: 18px; font-weight: 500; }
.modal-actions {
  display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px;
  margin-top: 14px; padding-top: 12px;
  border-top: 1px solid var(--sw-border);
}
/* Save stays reachable in long forms on small screens. */
.modal > .modal-actions {
  position: sticky; bottom: -20px; z-index: 1;
  margin-bottom: -20px; padding-bottom: 20px; background: var(--sw-card);
}
.modal.wizard { max-width: 560px; padding: 0; display: flex; flex-direction: column; overflow: hidden; }
.wiz-head { padding: 16px 20px; border-bottom: 1px solid var(--sw-border); display: grid; gap: 8px; }
.wiz-head h3 { margin: 0; font-size: 20px; }
.wiz-steps { display: flex; gap: 6px; }
.wiz-steps i { flex: 1; height: 4px; border-radius: 999px; background: var(--sw-border); }
.wiz-steps i.on { background: var(--sw-primary); }
.wiz-body { padding: 16px 20px; display: grid; gap: 12px; align-content: start; overflow-y: auto; flex: 1 1 auto; }
.wiz-body p { margin: 0; }
.wiz-foot { padding: 12px 20px; border-top: 1px solid var(--sw-border); display: flex; justify-content: space-between; gap: 8px; }
.wiz-list { display: grid; gap: 8px; }
.check { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border: 1px solid var(--sw-border); border-radius: 10px; cursor: pointer; }
.check input { width: 18px; height: 18px; flex: 0 0 auto; margin: 0; }
.check .sub { font-size: 12px; }
.zmin { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.choice { display: grid; gap: 8px; }
.choice button { text-align: start; border: 1px solid var(--sw-border); background: var(--sw-card); color: var(--sw-text); border-radius: 10px; padding: 12px; display: grid; gap: 2px; cursor: pointer; font: inherit; }
.choice button[aria-pressed="true"] { border-color: var(--sw-primary); background: rgba(3,169,244,0.12); }
.choice small { color: var(--sw-muted); }
.summary { background: var(--sw-bg); border-radius: 10px; padding: 12px 14px; font-size: 14px; display: grid; gap: 4px; }
.entity-picker {
  max-height: 280px; overflow-y: auto;
  border: 1px solid var(--sw-border); border-radius: 8px;
}
.entity-row {
  width: 100%; padding: 8px 10px; cursor: pointer; text-align: start;
  border: 0; border-bottom: 1px solid var(--sw-border); border-radius: 0;
  background: transparent; color: var(--sw-text); font: inherit;
  display: flex; justify-content: space-between; gap: 10px;
}
.entity-row:focus-visible { outline-offset: -2px; }
.entity-row:last-child { border-bottom: none; }
.entity-row:hover { background: var(--sw-bg); }
.entity-row[aria-pressed="true"] { background: rgba(3,169,244,0.12); box-shadow: inset 3px 0 0 var(--sw-primary); }
.domain {
  font-size: 11px; padding: 2px 6px;
  border-radius: 4px; background: var(--sw-primary-fill);
  color: #fff; text-transform: uppercase; white-space: nowrap;
}
.cond-row { display: grid; grid-template-columns: 1.4fr 1fr 0.9fr 0.8fr auto; gap: 6px; align-items: center; padding: 4px 0; }
.cond-row input, .cond-row select {
  width: 100%; padding: 6px 8px; border: 1px solid var(--sw-border); border-radius: 6px;
  background: var(--sw-card); color: var(--sw-text); font: inherit; font-size: 13px;
}
.opt-group { border-top: 1px solid var(--sw-border); padding: 12px 0; }
.opt-group:last-child { padding-bottom: 0; }
.opt-group > summary { list-style: none; display: grid; grid-template-columns: 1fr auto; gap: 2px 12px; align-items: center; }
.opt-group > summary::-webkit-details-marker { display: none; }
.opt-group > summary p { margin: 0; grid-column: 1; font-size: 13px; color: var(--sw-muted); font-weight: 400; }
.opt-group > summary .pill { grid-row: 1 / span 2; grid-column: 2; }
.opt-body { padding-top: 12px; }
.opt-body > p.muted { font-size: 12px; margin: 0 0 10px; line-height: 1.45; }
details.more > summary { font-size: 16px; }
.check-wrap { display: flex; flex-wrap: wrap; gap: 6px; }
.check-wrap label { display: flex; gap: 6px; align-items: center; font-size: 13px; padding: 4px 8px; border: 1px solid var(--sw-border); border-radius: 999px; cursor: pointer; }
.toast-host {
  position: fixed; bottom: calc(20px + env(safe-area-inset-bottom, 0px)); inset-inline: 0;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding-inline: 16px; z-index: 200; pointer-events: none;
}
/* In a dialog the message sits in the flow right under the title (BUG-022): clear of the title and of Save /
   Cancel, and it stays in view (sticky) when the form is scrolled. */
.modal .toast-host { position: sticky; top: 0; bottom: auto; inset-inline: auto; padding-inline: 0; margin-bottom: 10px; z-index: 2; }
.modal.wizard > .toast-host { margin: 0; padding: 10px 20px 0; }
.modal .toast { max-width: 100%; }
/* A field focused after Save is scrolled clear of that message, with its caption in view. */
.modal input, .modal select, .modal textarea, .modal .entity-row { scroll-margin-top: 84px; }
.toast {
  max-width: min(560px, 100%);
  padding: 10px 16px; background: var(--sw-text); color: var(--sw-bg);
  border-radius: 18px; font-size: 14px; line-height: 1.4; text-align: center;
  overflow-wrap: anywhere; box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.toast.error { background: var(--sw-danger-fill); color: #fff; }
.toast.ok { background: var(--sw-success-fill); color: #fff; }
pre { background: var(--sw-bg); padding: 10px; border-radius: 6px; font-size: 12px; overflow-x: auto; }
@media (max-width: 540px) {
  .field-row { grid-template-columns: 1fr; }
  .item { grid-template-columns: 1fr; }
  .cond-row { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .app { padding: 12px; }
  .tab { flex: 1 1 auto; padding: 10px 6px; font-size: 14px; }
  .modal { width: 100%; max-height: calc(100vh - 16px); }
  .wiz-head, .wiz-body, .wiz-foot { padding-inline: 14px; }
  .status-title { font-size: 18px; }
}
/* Touch screens: 44 px targets (ENH-002); the switch keeps its look and gets a larger invisible hit area. */
@media (pointer: coarse) {
  .btn, .link-btn, .tab, .day-chip, .wk-run, .entity-row, .check-wrap label, .wk-head .btn { min-height: 44px; }
  .btn.small, .wk-head .btn { min-width: 44px; }
  .menu-btn { min-width: 44px; min-height: 44px; }
  .app input:not([type="checkbox"]):not([type="radio"]):not([type="range"]), .app select, .app textarea,
  .modal input:not([type="checkbox"]):not([type="radio"]):not([type="range"]), .modal select, .modal textarea { min-height: 44px; }
  .stepper button { width: 44px; height: 44px; }
  .switch::before { content: ""; position: absolute; inset: -10px -2px; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
`;

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
// Entities a rain source can be (server: RAIN_SOURCE_DOMAINS).
const RAIN_DOMAINS = ["weather", "sensor", "binary_sensor"];
const DEFAULT_RAIN_STATES = "rainy,pouring,snowy,lightning-rainy";

// The rain details in use, as the server reads them (scheduler._should_skip_for_rain).
function rainRules(statesRaw, attribute, thresholdRaw) {
  const thr = parseFloat(String(thresholdRaw == null ? "" : thresholdRaw).trim());
  return {
    states: String(statesRaw == null ? DEFAULT_RAIN_STATES : statesRaw).split(",").map(x => x.trim()).filter(Boolean),
    attribute: String(attribute || "").trim(),
    threshold: isNaN(thr) ? 0 : thr,
  };
}

// Whether this state counts as rain right now, same rules as the server (UX-011 inline check).
function rainWouldSkip(st, r) {
  if (!st) return false;
  if (r.threshold > 0) {
    const raw = r.attribute ? (st.attributes || {})[r.attribute] : st.state;
    const n = parseFloat(raw);
    if (!isNaN(n)) return n >= r.threshold;
    if (r.attribute) return false;
  }
  if (r.states.includes(st.state)) return true;
  return String(st.entity_id || "").startsWith("binary_sensor.") && st.state === "on";
}
// The check line under the rain source, in the words of the rule the server applies to this source (#66):
// a number against the threshold, a binary sensor while "on", a weather or text state against the states list
// (with a hint when a number can never match it). tn(key, vars) gives nodes, t(key) text.
function rainCheckParts(st, r, tn, t) {
  const domain = String(st.entity_id || "").split(".")[0];
  const raw = r.attribute ? (st.attributes || {})[r.attribute] : st.state;
  const numeric = raw !== undefined && raw !== null && raw !== "" && !isNaN(Number(raw));
  if (r.threshold > 0 && (r.attribute || numeric)) {
    return tn("set.rain_check_threshold", { n: r.threshold, state: ltr(raw === undefined || raw === null ? "" : raw) });
  }
  const now = ltr(st.state);
  if (domain === "binary_sensor") return tn("set.rain_check_on", { state: now });
  const parts = tn("set.rain_check_states", { states: ltr(r.states.join(", ")), state: now });
  if (numeric && !r.states.includes(String(st.state))) parts.push(" ", t("set.rain_check_numeric"));
  return parts;
}
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];
// Largest sunrise / sunset offset in minutes (server: const.SUN_OFFSET_MAX).
const SUN_OFFSET_MAX = 180;

// Reports tables (BUG-009, BUG-010): header cells scoped to their column; fixed layout so long words wrap
// inside the column instead of widening the page.
function reportTable(firstWidth, headers) {
  const tbody = el("tbody");
  const table = el("table", { class: "report-table" }, [
    el("colgroup", {}, headers.map((h, i) => el("col", i ? {} : { style: `width:${firstWidth}` }))),
    el("thead", {}, el("tr", {}, headers.map((h, i) => el("th", i ? { scope: "col", class: "num" } : { scope: "col" }, h)))),
    tbody,
  ]);
  return { table, tbody };
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const k of Object.keys(attrs)) {
    const v = attrs[k];
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") {
      node.addEventListener(k.slice(2).toLowerCase(), v);
    } else if (v === false || v === undefined || v === null) {
      // skip: boolean-false / nullish
    } else if (v === true) {
      node.setAttribute(k, "");
    } else {
      node.setAttribute(k, v);
    }
  }
  (Array.isArray(children) ? children : [children]).forEach((c) => {
    if (c === null || c === undefined || c === false) return;
    node.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  });
  return node;
}

function fmtRemaining(secs) {
  if (secs <= 0) return "0:00";
  const m = Math.floor(secs / 60);
  const s = String(secs % 60).padStart(2, "0");
  return `${m}:${s}`;
}

function fmtDelayLeft(t, left) {
  return left < 3600 ? t("time.short_m", { n: Math.round(left / 60) })
    : left < 86400 ? t("time.short_h", { n: Math.round(left / 3600) })
      : t("time.short_d", { n: Math.round(left / 86400) });
}

// Isolate technical tokens (entity ids, services) so bidi text does not reorder them.
function ltr(text) {
  return el("bdi", { dir: "ltr" }, String(text == null ? "" : text));
}

// Isolate user-provided labels (direction auto-detected).
function iso(text) {
  return el("bdi", {}, String(text == null ? "" : text));
}

// Plain-text label for <option> (no child nodes allowed): isolate label and entity id with Unicode isolates.
function optLabel(label, entityId) {
  return `\u2068${label}\u2069 (\u2066${entityId}\u2069)`;
}

// Join text/node parts with a separator, skipping empty parts.
function joinParts(parts, sep = " • ") {
  const out = [];
  parts.filter(p => p !== null && p !== undefined && p !== "").forEach((p, i) => {
    if (i) out.push(sep);
    if (Array.isArray(p)) out.push(...p); else out.push(p);
  });
  return out;
}

function valveDelayUntil(v, now) {
  const until = parseInt((v && v.rain_delay_until) || 0, 10) || 0;
  return until > (now || 0) ? until : 0;
}

function deepActiveElement() {
  let node = document.activeElement;
  while (node && node.shadowRoot && node.shadowRoot.activeElement) {
    node = node.shadowRoot.activeElement;
  }
  return node;
}

// Focus across re-renders (#41): a control is identified by what it is (tag, role, label, text) and the
// zone row it sits in, plus its index among equals; its replacement gets focus back after the rebuild.
const FOCUSABLE = "button, input, select, textarea, summary, a[href], [tabindex]";

function rowKey(n) {
  const row = n.closest("[data-entity], [data-soak]");
  return row ? (row.getAttribute("data-entity") || row.getAttribute("data-soak")) : "";
}

function focusDesc(n) {
  const field = n.tagName === "INPUT" || n.tagName === "SELECT" || n.tagName === "TEXTAREA";
  return [
    n.tagName, n.getAttribute("role") || "", n.getAttribute("aria-label") || "", n.getAttribute("type") || "",
    field ? "" : (n.textContent || "").trim().slice(0, 80),
    rowKey(n),
  ].join("|");
}

function focusables(root) {
  return Array.from(root.querySelectorAll(FOCUSABLE)).filter(n => !n.disabled);
}

function focusId(all, n) {
  const desc = focusDesc(n);
  return { desc, nth: all.filter(x => focusDesc(x) === desc).indexOf(n) };
}

// The focused control plus fallbacks for when it is gone or disabled after the rebuild (Water now becomes
// Stop): its neighbours in the same zone row, the same slot in that row, its neighbours on the page.
function captureFocus(root) {
  const n = deepActiveElement();
  if (!root || !n || n === root || !root.contains(n) || !n.matches(FOCUSABLE)) return null;
  const all = focusables(root);
  const pos = all.indexOf(n);
  const row = rowKey(n);
  const inRow = row ? all.filter(x => rowKey(x) === row) : [];
  const rowPos = inRow.indexOf(n);
  const near = (list, i) => [list[i + 1], list[i - 1]].filter(Boolean).map(x => focusId(all, x));
  return {
    pos, row, rowPos, self: focusId(all, n), rowNear: row ? near(inRow, rowPos) : [], near: near(all, pos),
    // A control can name its successor (Stop names its zone's Water now): data-refocus -> data-focus-id.
    refocus: n.getAttribute("data-refocus") || "",
  };
}

function restoreFocus(root, key) {
  if (!root || !key) return;
  const all = focusables(root);
  const find = (id) => {
    const same = all.filter(x => focusDesc(x) === id.desc);
    return same[id.nth] || same[0];
  };
  const inRow = key.row ? all.filter(x => rowKey(x) === key.row) : [];
  const successor = key.refocus ? all.find(x => x.getAttribute("data-focus-id") === key.refocus) : null;
  const target = find(key.self) || successor || key.rowNear.map(find).find(Boolean) ||
    (inRow.length ? inRow[Math.min(key.rowPos, inRow.length - 1)] : null) ||
    key.near.map(find).find(Boolean) || (all.length ? all[Math.min(key.pos, all.length - 1)] : null);
  if (target) target.focus({ preventScroll: true });
}

function focusInside(root) {
  const n = deepActiveElement();
  return !!(root && n && n !== root && root.contains(n));
}

let uidSeq = 0;

// A unique element id, for aria-labelledby / aria-describedby pairs built per render.
function uid(prefix) {
  uidSeq += 1;
  return `${prefix}-${uidSeq}`;
}

// Controls a Tab press can reach inside a dialog: enabled, rendered (not in a hidden or display:none part).
function tabbables(root) {
  return Array.from(root.querySelectorAll(FOCUSABLE)).filter(n => !n.disabled && n.tabIndex >= 0 &&
    !n.closest("[hidden]") && n.getClientRects().length > 0);
}

// Inline field errors (UX-005): the message sits under its field, which is marked invalid and points to it.
// A group (role="group", e.g. the entity list) is only described by it: aria-invalid does not apply to groups.
function fieldError(id) {
  return el("div", { class: "field-error", id, role: "alert", hidden: true });
}

function setFieldError(node, input, msg) {
  node.textContent = msg || "";
  node.hidden = !msg;
  if (!input) return;
  const group = input.getAttribute("role") === "group";
  if (msg) {
    if (!group) input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", node.id);
  } else {
    input.removeAttribute("aria-invalid");
    input.removeAttribute("aria-describedby");
  }
}

// State without the fields that change on every poll, to tell a real change from a clock tick.
function stateSig(st) {
  return JSON.stringify(st, (k, v) => (k === "now" || k === "in_seconds" ? undefined : v));
}

// A full rebuild still happens this often while focus is inside, so relative times stay current.
const FOCUSED_RERENDER_MS = 60000;

function daysFromMaskNames(mask) {
  return DAYS.filter((_, i) => mask & DAY_BITS[i]);
}

// Service fields that recreate a stored schedule's repeat rule.
function repeatPayload(s) {
  return s.repeat === "interval"
    ? { every_n_days: s.interval_days, start_date: s.start_date }
    : { days: daysFromMaskNames(s.days_mask) };
}

// Service fields that recreate a stored schedule's start time: clock, or sunrise / sunset + offset (#59).
function timePayload(s) {
  const mode = s.time_mode === "sunrise" || s.time_mode === "sunset" ? s.time_mode : "clock";
  return mode === "clock"
    ? { time: s.time_hhmm }
    : { time: s.time_hhmm, time_mode: mode, sun_offset_minutes: parseInt(s.sun_offset_min, 10) || 0 };
}

// Today's date (YYYY-MM-DD) in Home Assistant's time zone.
function todayKey(hass) {
  return I18N.dayKey(Date.now() / 1000, hass);
}

function isSkipStatus(status) {
  return String(status || "").startsWith("skipped_");
}

// Current "HH:MM" (24 h) in the same time zone as todayKey().
function nowHHMM(hass) {
  const tz = hass && hass.config && hass.config.time_zone;
  const local = hass && hass.locale && hass.locale.time_zone === "local";
  const opts = { hour: "2-digit", minute: "2-digit", hourCycle: "h23" };
  if (tz && !local) opts.timeZone = tz;
  try {
    return new Intl.DateTimeFormat("en-GB", opts).format(new Date());
  } catch (e) {
    delete opts.timeZone;
    return new Intl.DateTimeFormat("en-GB", opts).format(new Date());
  }
}

// "YYYY-MM-DD" day arithmetic on the calendar (no time zone involved).
function dayNum(key) {
  const [y, m, d] = String(key).split("-").map(Number);
  return Math.round(Date.UTC(y, m - 1, d) / 86400000);
}

function dayFromNum(n) {
  return new Date(n * 86400000).toISOString().slice(0, 10);
}

// Whole minutes 1 to 1440 as typed, or null (BUG-016: 0 and empty used to become 10).
function minutesValue(raw) {
  const text = String(raw).trim();
  const n = Number(text);
  return text !== "" && Number.isInteger(n) && n >= 1 && n <= 1440 ? n : null;
}

const INTERVAL_MIN = 2;
const INTERVAL_MAX = 30;

// Minutes stepper: 1-minute steps up to 10, then 5-minute steps; clamped to 1-1440.
function stepMinutes(value, dir) {
  const v = parseInt(value, 10) || 1;
  const n = dir > 0
    ? (v < 10 ? v + 1 : (Math.floor(v / 5) + 1) * 5)
    : (v <= 10 ? v - 1 : (Math.ceil(v / 5) - 1) * 5);
  return Math.min(1440, Math.max(1, n));
}

class ScheduleWizardPanel extends HTMLElement {
  constructor() {
    super();
    this._initialized = false;
    this._state = null;
    this._tab = "home";
    this._view = null;
    this._refreshTimer = null;
    this._modalRoot = null;
    this._quickDur = {};
    this._editing = false;
    this._narrow = false;
    this._rainTarget = "";
    this._rainOpen = false;
    this._actFilter = "week";
    this._moreOpen = false;
    this._openGroups = new Set();
    this._dialog = null;
  }

  set hass(hass) {
    this._hass = hass;
    const langChanged = this._applyLang();
    if (!this._initialized) this._init();
    else {
      this._syncMenuButton();
      if (langChanged) {
        this._closeDialog();
        if (this._state) this._render();
      }
    }
  }

  _applyLang() {
    const h = this._hass;
    const lang = I18N.resolveLang(h);
    const rtl = I18N.isRtl(h, lang);
    const loc = h && h.locale
      ? [h.locale.language, h.locale.time_format, h.locale.time_zone, h.locale.first_weekday].join("|")
      : (h && h.language) || "";
    const key = `${lang}|${rtl}|${loc}`;
    if (key === this._langKey) return false;
    const first = this._langKey === undefined;
    this._langKey = key;
    this._lang = lang;
    this._rtl = rtl;
    this._t = I18N.makeT(lang);
    return !first;
  }

  _tn(key, vars) {
    return I18N.tnodes(this._t(key), vars);
  }

  // Day indexes (0 = Monday) in the order the user's week runs (UX-017).
  _weekOrder() {
    return I18N.weekOrder(this._hass);
  }

  _fo(extra) {
    return Object.assign({ hass: this._hass }, extra || {});
  }

  _fmtDT(ts, opts) { return I18N.fmtDateTime(ts, this._lang, this._fo(opts)); }
  _fmtTime(ts, opts) { return I18N.fmtTime(ts, this._lang, this._fo(opts)); }
  _fmtDate(ts, opts) { return I18N.fmtDate(ts, this._lang, this._fo(opts)); }
  // A "HH:MM" clock time in the same words as every other time on the page ("6:00 AM" / "6:00") (#92).
  _fmtClock(hhmm) {
    const [h, m] = String(hhmm || "").split(":").map(Number);
    if (isNaN(h) || isNaN(m)) return String(hhmm || "");
    return this._fmtTime(Date.UTC(2024, 0, 1, h, m) / 1000, { timeZone: "UTC", hour: "numeric", minute: "2-digit" });
  }
  _fmtNum(n, digits) { return I18N.fmtNumber(n, this._lang, this._fo({ maximumFractionDigits: digits || 0, minimumFractionDigits: digits || 0 })); }

  // Litres below 1000, cubic metres (1 decimal) from there on.
  _fmtLiters(liters) {
    const l = Math.max(0, Number(liters) || 0);
    return l < 999.5 ? this._t("water.l", { n: this._fmtNum(l) }) : this._t("water.m3", { n: this._fmtNum(l / 1000, 1) });
  }

  _fmtLpm(lpm) { return this._t("water.lpm", { n: this._fmtNum(lpm, Number(lpm) < 10 ? 1 : 0) }); }

  // Weekday + time for the coming week, full date beyond that.
  _fmtWhen(ts) {
    const now = (this._state && this._state.now) || Math.floor(Date.now() / 1000);
    if (ts - now < 6 * 86400) return `${this._fmtDate(ts, { weekday: "short" })} ${this._fmtTime(ts)}`;
    return this._fmtDT(ts, { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
  }

  _arrow() { return this._rtl ? "←" : "→"; }

  // Chevrons sit in an LTR isolate so bidi mirroring never applies; the glyph is picked per direction.
  _chevron(forward) {
    const right = forward !== this._rtl;
    return el("bdi", { class: "sep", dir: "ltr", "aria-hidden": "true" }, right ? "›" : "‹");
  }

  _chainSep() { return this._chevron(true); }

  _applyDir(node) {
    if (!node) return;
    node.setAttribute("dir", this._rtl ? "rtl" : "ltr");
    node.setAttribute("lang", this._lang);
  }

  _statusLabel(code) {
    const c = String(code || "");
    return c && this._t.has("status." + c) ? this._t("status." + c) : c;
  }

  _sourceLabel(code, planName) {
    const c = String(code || "");
    if (c.startsWith("cycle:")) {
      return this._t("source.cycle", { name: this._planName(c.slice(6).split("|")[0], planName) });
    }
    return c && this._t.has("source." + c) ? this._t("source." + c) : c;
  }

  // History rows keep a plan's id; zones are entity ids (always with a dot) (#57).
  _isPlanId(id) {
    return !!id && !String(id).includes(".");
  }

  // The plan's current name, else the name stored with the history row, else "Deleted plan" (#57).
  _planName(id, stored) {
    const cycle = ((this._state && this._state.cycles) || []).find(x => x.id === id);
    if (cycle) return cycle.name;
    return stored || this._t("home.deleted_plan");
  }

  _daysFromMask(mask) {
    if ((mask & 127) === 127) return this._t("sched.every_day");
    const names = this._weekOrder()
      .filter(i => mask & DAY_BITS[i])
      .map(i => I18N.weekdayShort(i, this._lang, this._fo()));
    return names.join(", ") || this._t("sched.no_days");
  }

  // "YYYY-MM-DD" (a local calendar date) formatted without shifting it through a time zone.
  _fmtDay(day) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(day || ""));
    if (!m) return String(day || "");
    const ts = Date.UTC(+m[1], +m[2] - 1, +m[3], 12) / 1000;
    return I18N.fmtDate(ts, this._lang, { hass: this._hass, timeZone: "UTC", year: "numeric", month: "short", day: "numeric" });
  }

  // "30 min before sunrise" for a sunrise / sunset schedule (#59), else null.
  _sunWhen(s) {
    const mode = s.time_mode;
    if (mode !== "sunrise" && mode !== "sunset") return null;
    const off = parseInt(s.sun_offset_min, 10) || 0;
    if (!off) return this._t(`sched.at_${mode}`);
    return this._t(`sched.${off < 0 ? "before" : "after"}_${mode}`, { n: Math.abs(off) });
  }

  _whenNodes(s) {
    const sunWhen = this._sunWhen(s);
    if (sunWhen) {
      return s.repeat === "interval"
        ? this._tn("sched.every_n_sun", { n: s.interval_days, date: this._fmtDay(s.start_date), when: sunWhen })
        : this._tn("sched.days_sun", { days: this._daysFromMask(s.days_mask), when: sunWhen });
    }
    if (s.repeat === "interval") {
      return this._tn("sched.every_n_at", { n: s.interval_days, date: this._fmtDay(s.start_date), time: ltr(s.time_hhmm) });
    }
    return this._tn("sched.days_at", { days: this._daysFromMask(s.days_mask), time: ltr(s.time_hhmm) });
  }

  _valveName(id) {
    const v = ((this._state && this._state.valves) || []).find(x => x.entity_id === id);
    return v ? iso(v.label) : ltr(id);
  }

  set narrow(v) {
    this._narrow = !!v;
    if (this._initialized) this._syncMenuButton();
  }

  _showMenuButton() {
    return !!this._narrow || !!(this._hass && this._hass.dockedSidebar === "always_hidden");
  }

  _syncMenuButton() {
    const btn = this.querySelector(".menu-btn");
    if (btn) btn.style.display = this._showMenuButton() ? "" : "none";
  }

  _menuButton() {
    const btn = el("button", {
      class: "menu-btn",
      type: "button",
      "aria-label": this._t("common.menu"),
      title: this._t("common.menu"),
      style: this._showMenuButton() ? null : "display:none;",
      onClick: () => this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true })),
    });
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS(ns, "path");
    path.setAttribute("d", "M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z");
    svg.appendChild(path);
    btn.appendChild(svg);
    return btn;
  }
  set route(v) { this._route = v; }
  set panel(v) { this._panel = v; }

  connectedCallback() {
    // Home Assistant can set properties before this element is upgraded (the module first awaits
    // i18n.js); such own properties hide the setters, so re-apply them through the setters.
    ["panel", "route", "narrow", "hass"].forEach((prop) => {
      if (Object.prototype.hasOwnProperty.call(this, prop)) {
        const value = this[prop];
        delete this[prop];
        this[prop] = value;
      }
    });
    if (this._hass && !this._initialized) {
      this._init();
    } else if (this._initialized && !this._refreshTimer) {
      this._refresh();
      this._refreshTimer = setInterval(() => this._refresh(), 5000);
    }
    if (this._dialog) document.addEventListener("keydown", this._dialog.onKey);
  }

  disconnectedCallback() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer);
      this._refreshTimer = null;
    }
    if (this._dialog) document.removeEventListener("keydown", this._dialog.onKey);
  }

  _init() {
    this._initialized = true;
    const style = el("style");
    style.textContent = STYLES;
    this.appendChild(style);
    const app = el("div", { class: "app", id: "app" });
    this.appendChild(app);
    this._modalRoot = el("div", { id: "modal-root" });
    this.appendChild(this._modalRoot);
    this._toastRoot = el("div", { class: "toast-host", role: "status" });
    this.appendChild(this._toastRoot);
    // One persistent live region outside the re-rendered page (UX-008): run start / stop and rain pause only.
    this._liveRoot = el("div", { class: "sr-only", role: "status", "aria-live": "polite" });
    this.appendChild(this._liveRoot);
    this.addEventListener("focusin", (ev) => {
      const t = ev.target;
      this._editing = !!(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT"));
    });
    this.addEventListener("focusout", () => { this._editing = false; });
    this._refresh();
    this._refreshTimer = setInterval(() => this._refresh(), 5000);
  }

  async _refresh() {
    if (document.hidden && this._state) return; // no polling in a background tab (PERF-001)
    try {
      // With the last rev the server answers only the live part when nothing else changed (PERF-001).
      const prev = this._state;
      const res = await this._hass.callWS(prev && prev.rev
        ? { type: "schedule_wizard/get_state", rev: prev.rev }
        : { type: "schedule_wizard/get_state" });
      const { unchanged, ...fresh } = res;
      this._state = unchanged && prev ? { ...prev, ...fresh } : fresh;
      this._stateSig = stateSig(this._state);
      this._announceChanges(prev, this._state);
      if (this._hadError) {
        this._hadError = false;
        this._render();
        return;
      }
      if (this._tab === "settings") return;
      const focused = deepActiveElement();
      const focusedHere = focused && this.contains(focused) &&
        (focused.tagName === "INPUT" || focused.tagName === "TEXTAREA" || focused.tagName === "SELECT");
      if (this._editing || focusedHere || this.querySelector("input:focus, textarea:focus, select:focus")) {
        this._updateInPlace();
        return;
      }
      // Nothing but the clock moved and the user is on a control here: update numbers, keep the DOM (#41).
      if (this._stateSig === this._renderedSig && Date.now() - this._renderedAt < FOCUSED_RERENDER_MS &&
        focusInside(this.querySelector("#app"))) {
        this._updateInPlace();
        return;
      }
      this._render();
    } catch (e) {
      this._hadError = true;
      this._renderError(e);
    }
  }

  // Live countdowns and progress bars, without replacing inputs that may have focus.
  _updateInPlace() {
    const st = this._state;
    const now = st.now;
    const active = st.active || [];
    this.querySelectorAll("#app [data-left]").forEach(n => {
      const r = active.find(a => a.entity_id === n.getAttribute("data-left"));
      if (r) n.textContent = fmtRemaining(Math.max(0, r.ends_at - now));
    });
    this.querySelectorAll("#app .progress-bar").forEach(b => {
      const host = b.closest("[data-entity]");
      if (!host) return;
      const r = active.find(a => a.entity_id === host.getAttribute("data-entity"));
      if (!r) return;
      const total = Math.max(1, r.ends_at - r.started_at);
      const remaining = Math.max(0, r.ends_at - now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      b.style.width = `${pct}%`;
      const bar = b.parentElement;
      if (bar && bar.getAttribute("role") === "progressbar") bar.setAttribute("aria-valuenow", String(Math.round(pct)));
    });
    this.querySelectorAll("#app [data-soak]").forEach(n => {
      const s = (st.soaking || []).find(x => x.entity_id === n.getAttribute("data-soak") && x.phase === "soaking");
      if (s) n.textContent = fmtRemaining(Math.max(0, (parseInt(s.resume_at, 10) || 0) - now));
    });
  }

  _renderError(e) {
    const app = this.querySelector("#app");
    if (!app) return;
    this._applyDir(this);
    app.innerHTML = "";
    app.appendChild(el("div", { class: "card" }, [
      el("h2", {}, "Schedule Wizard"),
      el("div", { class: "muted" }, this._t("app.load_failed", { error: e.message || e.code || this._t("common.unknown") })),
    ]));
  }

  // Toasts live inside the panel, where the .toast styles apply (#51); errors are alerts and stay longer.
  // An error raised while a dialog is open goes inside it (the dialog stays open on errors), so assistive
  // tech that honours aria-modal still hears it; anything else stays on the panel and outlives a closing dialog.
  // One message at a time, the newest replaces the last; in a dialog it sits right under the title (BUG-022).
  _toast(msg, kind = "") {
    const host = this._toastRoot;
    if (!host) return;
    const error = kind === "error";
    const dialog = error && this._modalRoot && this._modalRoot.querySelector('[aria-modal="true"]');
    if (dialog) {
      const head = Array.from(dialog.children).find(c => c !== host && (c.tagName === "H3" || c.classList.contains("wiz-head")));
      if (head) { if (head.nextSibling !== host) head.after(host); } else if (host.parentNode !== dialog) dialog.prepend(host);
    } else if (host.parentNode !== this) {
      this.appendChild(host);
    }
    const t = el("div", { class: "toast " + kind, role: error ? "alert" : null }, msg);
    this._applyDir(t);
    host.replaceChildren(t);
    setTimeout(() => t.remove(), error ? 6000 : 2800);
  }

  _fmtAgo(secs) {
    if (secs < 60) return this._t("time.ago_s", { n: secs });
    const m = Math.floor(secs / 60);
    if (m < 60) return this._t("time.ago_m", { n: m });
    const h = Math.floor(m / 60);
    if (h < 24) return this._t("time.ago_h", { n: h });
    const d = Math.floor(h / 24);
    return this._t("time.ago_d", { n: d });
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("schedule_wizard", service, data);
      this._toast(this._t("common.done"), "ok");
      this._refresh();
      return true;
    } catch (e) {
      this._toast(e.message || String(e), "error");
      return false;
    }
  }

  async _confirmDelete(message, service, data) {
    if (!await this._confirm(message, this._t("common.delete"))) return;
    this._callService(service, data);
  }

  // In-page confirmation (UX-018: the browser's own confirm dialog is unstyled and outside the panel's language
  // and direction). Resolves true on the confirm button, false on Cancel, Escape or a click outside.
  // opts.focusConfirm: start on the confirm button (Stop watering: one more tap in an emergency); otherwise
  // Cancel has the focus, so Enter on a delete does not delete.
  _confirm(message, confirmLabel, opts = {}) {
    return new Promise((resolve) => {
      let done = false;
      const finish = (ok) => {
        if (done) return;
        done = true;
        close();
        resolve(ok);
      };
      const titleId = uid("sw-confirm");
      const modal = el("div", { class: "modal", role: "alertdialog", "aria-modal": "true", "aria-labelledby": titleId });
      modal.appendChild(el("h3", { id: titleId }, message));
      const cancel = el("button", { class: "btn", type: "button", onClick: () => finish(false) }, this._t("common.cancel"));
      const ok = el("button", { class: opts.danger === false ? "btn primary" : "btn danger", type: "button", onClick: () => finish(true) }, confirmLabel);
      modal.appendChild(el("div", { class: "modal-actions" }, [cancel, ok]));
      const overlay = el("div", { class: "modal-overlay" }, modal);
      let close = () => {};
      const observer = new MutationObserver(() => {
        // Closed from outside (Escape, overlay click, another dialog): count as Cancel.
        if (!modal.isConnected) { observer.disconnect(); if (!done) { done = true; resolve(false); } }
      });
      close = this._openDialog(overlay, modal, { focus: () => (opts.focusConfirm ? ok : cancel) });
      observer.observe(this._modalRoot, { childList: true });
    });
  }

  // An on/off field drawn as the same switch the lists use (UX-014: the editors had a bare checkbox for the
  // property the list shows as a switch). onChange(value) runs on every toggle.
  _switchField(label, initial, onChange) {
    let on = !!initial;
    const labelId = uid("sw-switch");
    const sw = el("button", {
      type: "button", class: "switch", role: "switch", "aria-checked": on ? "true" : "false", "aria-labelledby": labelId,
      onClick: () => { on = !on; sw.setAttribute("aria-checked", on ? "true" : "false"); if (onChange) onChange(on); },
    });
    return el("div", { class: "switch-row" }, [el("span", { id: labelId }, label), sw]);
  }

  // "Water now: Front lawn": the visible text first (WCAG 2.5.3), then what it acts on, so repeated buttons
  // differ by name (UX-007).
  _named(action, name) {
    return this._t("card.action_for", { action, zone: name });
  }

  // Announce what changed between two polls (UX-008): a zone starting or stopping, a rain pause starting
  // or ending. Countdowns and anything else are not announced. Nothing is said for the first state.
  _announceChanges(prev, cur) {
    if (!this._liveRoot || !prev || !cur) return;
    const label = (id) => {
      const v = (cur.valves || prev.valves || []).find(x => x.entity_id === id);
      return v ? v.label : id;
    };
    const before = new Set((prev.active || []).map(a => a.entity_id));
    const after = new Set((cur.active || []).map(a => a.entity_id));
    const msgs = [];
    (cur.active || []).forEach((a) => {
      if (before.has(a.entity_id)) return;
      const n = Math.max(1, Math.round(((a.ends_at || 0) - (a.started_at || 0)) / 60));
      msgs.push(this._t("live.started", { zone: label(a.entity_id), n }));
    });
    (prev.active || []).forEach((a) => {
      if (!after.has(a.entity_id)) msgs.push(this._t("live.stopped", { zone: label(a.entity_id) }));
    });
    const rain = (st) => {
      const until = parseInt(st.rain_delay_until || 0, 10) || 0;
      return until > (st.now || 0) ? until : 0;
    };
    const r0 = rain(prev);
    const r1 = rain(cur);
    if (r1 && r1 !== r0) msgs.push(this._t("home.rain_until", { when: this._fmtWhen(r1) }));
    else if (r0 && !r1) msgs.push(this._t("live.rain_cleared"));
    if (msgs.length) this._say(msgs);
  }

  _say(msgs) {
    const host = this._liveRoot;
    host.replaceChildren(...msgs.map((m) => {
      const line = el("div", {}, m);
      this._applyDir(line);
      return line;
    }));
  }

  // Modal dialogs (BUG-003): focus moves into the dialog, Tab and Shift+Tab stay inside, Escape closes from
  // anywhere, the page behind is inert, and on close focus returns to the control that opened the dialog,
  // or to its replacement when a re-render replaced it meanwhile. Returns the close function.
  // opts.canClose(): false blocks Escape / overlay click (wizard while saving); opts.focus(): initial target.
  _openDialog(overlay, modal, opts = {}) {
    this._closeDialog();
    const app = this.querySelector("#app");
    const opener = deepActiveElement();
    const openerKey = captureFocus(app);
    const canClose = opts.canClose || (() => true);
    modal.setAttribute("tabindex", "-1");
    const onKey = (e) => {
      if (this._dialog !== handle) return;
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        if (canClose()) close();
        return;
      }
      if (e.key !== "Tab") return;
      const items = tabbables(modal);
      if (!items.length) { e.preventDefault(); modal.focus(); return; }
      const i = items.indexOf(deepActiveElement());
      if (e.shiftKey && i <= 0) { e.preventDefault(); items[items.length - 1].focus(); }
      else if (!e.shiftKey && (i === -1 || i === items.length - 1)) { e.preventDefault(); items[0].focus(); }
    };
    const close = () => {
      if (this._dialog !== handle) return;
      this._dialog = null;
      document.removeEventListener("keydown", onKey);
      if (app) app.inert = false;
      this._modalRoot.innerHTML = "";
      this._editing = false;
      if (opener && opener.isConnected && !opener.disabled) opener.focus({ preventScroll: true });
      else restoreFocus(app, openerKey);
    };
    const handle = { close, onKey };
    this._dialog = handle;
    overlay.addEventListener("click", (e) => { if (e.target === overlay && canClose()) close(); });
    this._modalRoot.innerHTML = "";
    this._applyDir(overlay);
    this._modalRoot.appendChild(overlay);
    if (app) app.inert = true;
    document.addEventListener("keydown", onKey);
    // opts.focus() may move the focus itself and return null (the wizard draws its first step).
    const target = opts.focus ? opts.focus()
      : tabbables(modal).find(n => /^(INPUT|SELECT|TEXTAREA)$/.test(n.tagName)) || tabbables(modal)[0] || modal;
    if (target) target.focus();
    return close;
  }

  _closeDialog() {
    if (this._dialog) this._dialog.close();
    else if (this._modalRoot) this._modalRoot.innerHTML = "";
  }

  _render() {
    const app = this.querySelector("#app");
    if (!app || !this._state) return;
    this._applyDir(this);
    this._applyDir(app);
    const focusKey = captureFocus(app);
    this._renderedSig = this._stateSig;
    this._renderedAt = Date.now();
    app.innerHTML = "";

    app.appendChild(el("div", { class: "topbar" }, [
      el("div", { class: "title-wrap" }, [this._menuButton(), el("h1", {}, "Schedule Wizard")]),
    ]));

    // ARIA tabs pattern (UX-006): one Tab stop (the selected tab), arrow keys (mirrored in RTL), Home and End
    // move and select; every tab controls the single tab panel, which is named by the selected tab.
    const TABS = ["home", "zones", "programs", "settings"];
    const tabs = el("div", { class: "tabs", role: "tablist" });
    const onTabKey = (e) => {
      const i = TABS.indexOf(this._tab);
      const next = this._rtl ? "ArrowLeft" : "ArrowRight";
      const prev = this._rtl ? "ArrowRight" : "ArrowLeft";
      let j = null;
      if (e.key === next) j = (i + 1) % TABS.length;
      else if (e.key === prev) j = (i - 1 + TABS.length) % TABS.length;
      else if (e.key === "Home") j = 0;
      else if (e.key === "End") j = TABS.length - 1;
      if (j === null) return;
      e.preventDefault();
      this._tab = TABS[j];
      this._view = null;
      this._render();
      const tab = this.querySelector(`#sw-tab-${TABS[j]}`);
      if (tab) tab.focus();
    };
    TABS.forEach((key) => {
      const selected = this._tab === key;
      tabs.appendChild(el("button", {
        class: "tab" + (selected ? " active" : ""),
        role: "tab",
        id: `sw-tab-${key}`,
        "aria-selected": selected ? "true" : "false",
        "aria-controls": "sw-tabpanel",
        tabindex: selected ? "0" : "-1",
        onClick: () => { this._tab = key; this._view = null; this._render(); },
        onKeydown: onTabKey,
      }, this._t("tab." + key)));
    });
    app.appendChild(tabs);

    const content = el("div", { role: "tabpanel", id: "sw-tabpanel", "aria-labelledby": `sw-tab-${this._tab}` });
    app.appendChild(content);

    switch (this._tab) {
      case "home":
        if (this._view === "reports") this._renderReports(content);
        else this._renderHome(content);
        break;
      case "zones": this._renderZones(content); break;
      case "programs": this._renderPrograms(content); break;
      case "settings": this._renderSettings(content); break;
    }
    restoreFocus(app, focusKey);
  }

  _flowBanner(root) {
    const flow = this._state.flow || {};
    if (!flow.alert) return;
    root.appendChild(el("div", { class: "alert-banner", role: "alert" },
      flow.alert === "leak"
        ? this._t("dash.flow_leak")
        : flow.alert === "high_flow"
          ? this._t("dash.flow_high")
          : this._t("dash.flow_other", { alert: flow.alert })
    ));
  }

  // ---------- Home ----------

  _renderHome(root) {
    const st = this._state;
    const valves = st.valves || [];
    this._flowBanner(root);

    if (!valves.length) {
      root.appendChild(el("div", { class: "card empty-state" }, [
        el("h2", {}, this._t("home.setup_title")),
        el("p", { class: "muted" }, this._t("home.setup_text")),
        el("button", { class: "btn primary", onClick: () => this._openWizard() }, this._t("home.setup_start")),
      ]));
      return;
    }

    root.appendChild(this._statusCard());

    const now = st.now;
    const delayed = valves.filter(v => valveDelayUntil(v, now));
    if (delayed.length) {
      const dCard = el("div", { class: "card list" });
      delayed.forEach((v) => {
        const lbl = fmtDelayLeft(this._t, valveDelayUntil(v, now) - now);
        dCard.appendChild(el("div", { class: "row-between" }, [
          el("div", { class: "small" }, this._tn("dash.valve_delayed", { valve: iso(v.label), left: lbl })),
          el("button", {
            class: "btn small",
            onClick: () => this._callService("clear_rain_delay", { entity_id: [v.entity_id] }),
          }, this._t("common.clear")),
        ]));
      });
      root.appendChild(dCard);
    }

    root.appendChild(el("div", { class: "section-h" }, [
      el("h2", {}, this._t("home.your_zones")),
      el("button", { class: "btn ghost", onClick: () => this._openWizard() }, this._t("home.new_plan")),
    ]));
    const last = this._lastWateringLine();
    if (last) root.appendChild(last);
    const grid = el("div", { class: "zones" });
    valves.forEach(v => grid.appendChild(this._zoneCard(v)));
    root.appendChild(grid);

    root.appendChild(this._weekCard());
    root.appendChild(this._activityCard());
  }

  // ---------- This week ----------

  _weekRuns() {
    return Array.isArray(this._state.week) ? this._state.week : [];
  }

  // The 7 local day keys ("YYYY-MM-DD") starting today, in the formatter time zone.
  _weekDays() {
    const [y, m, d] = I18N.dayKey(this._state.now, this._hass).split("-").map(Number);
    return Array.from({ length: 7 }, (_, i) => new Date(Date.UTC(y, m - 1, d + i)).toISOString().slice(0, 10));
  }

  _dayInfo(key) {
    const [y, m, d] = String(key).split("-").map(Number);
    const ts = Date.UTC(y, m - 1, d, 12) / 1000;
    const wd = I18N.weekdayShort((new Date(ts * 1000).getUTCDay() + 6) % 7, this._lang, this._fo());
    const date = this._fmtDate(ts, { day: "numeric", month: "numeric", timeZone: "UTC" });
    const idx = this._weekDays().indexOf(key);
    const name = idx === 0 ? this._t("week.today") : idx === 1 ? this._t("week.tomorrow") : wd;
    return { name, wd, date, full: `${wd} ${date}`, idx };
  }

  // Next upcoming occurrence of a schedule in the week view (skipped or not).
  _nextOccOf(scheduleId) {
    const now = this._state.now;
    return this._weekRuns().find(r => r.schedule_id === scheduleId && r.start > now) || null;
  }

  _isSkipped(scheduleId, day) {
    const list = ((this._state.skips || {})[scheduleId]) || [];
    return Array.isArray(list) && list.includes(day);
  }

  // Temperature factor at 0 % right now: today's and tomorrow's upcoming runs will be skipped (#29).
  _coolSkip(r) {
    const s = this._state.seasonal;
    if (!s || !s.skips || r.skip || r.start <= this._state.now) return false;
    const idx = this._weekDays().indexOf(r.day);
    return idx === 0 || idx === 1;
  }

  // A past run that history recorded as skipped at 0 % (the week view only predicts manual skips).
  _coolSkipped(r) {
    if (r.skip || r.start > this._state.now) return false;
    const note = "schedule:" + r.schedule_id;
    return (this._state.history || []).some(h => h.status === "skipped_seasonal_zero" && h.note === note
      && h.ts >= r.start - 60 && h.ts < r.start + 120);
  }

  _skipTag(r) {
    if (r.skip === "skipped_manual") return el("span", { class: "wk-tag" }, this._t("week.skipped"));
    if (r.skip === "rain_delay") return el("span", { class: "wk-tag" }, this._t("week.rain"));
    if (r.skip === "partial_rain_delay") return el("span", { class: "wk-tag warn" }, this._t("week.partial_rain"));
    if (this._coolSkip(r)) return el("span", { class: "wk-tag warn" }, this._t("week.cool_skip"));
    if (this._coolSkipped(r)) return el("span", { class: "wk-tag" }, this._t("week.skipped"));
    return null;
  }

  _weekCard() {
    const now = this._state.now;
    const runs = this._weekRuns();
    const card = el("section", { class: "card wk-wrap" }, [el("h2", {}, this._t("week.title"))]);
    if (!runs.length) {
      card.appendChild(el("div", { class: "empty-state", style: "padding:8px;" }, [
        el("p", { class: "muted" }, this._t("week.empty")),
        el("button", { class: "btn primary", onClick: () => this._openWizard() }, this._t("home.new_plan")),
      ]));
      return card;
    }
    const grid = el("div", { class: "week" });
    this._weekDays().forEach((key, i) => {
      const info = this._dayInfo(key);
      const dayRuns = runs.filter(r => r.day === key);
      const canSkip = dayRuns.some(r => r.start > now && r.skip !== "skipped_manual");
      const head = el("div", { class: "wk-head" }, [
        el("div", {}, [el("strong", {}, info.name), el("span", { class: "sub" }, i < 2 ? info.full : info.date)]),
        canSkip ? el("button", {
          class: "btn ghost small",
          title: this._t("week.skip_day_title", { day: info.full }),
          "aria-label": this._named(this._t("week.skip_day"), info.full),
          onClick: async () => {
            if (!await this._confirm(this._t("week.skip_day_confirm", { day: info.full }), this._t("week.skip_day"), { danger: false })) return;
            this._callService("skip_day", { date: key });
          },
        }, this._t("week.skip_day")) : null,
      ]);
      const list = el("div", { class: "wk-runs" });
      if (!dayRuns.length) list.appendChild(el("div", { class: "muted small" }, this._t("week.no_runs")));
      dayRuns.forEach(r => {
        const cls = ["wk-run"];
        if (r.end < now) cls.push("past");
        if (r.skip === "skipped_manual" || this._coolSkipped(r)) cls.push("skipped");
        else if (r.skip === "rain_delay") cls.push("rain");
        list.appendChild(el("button", { type: "button", class: cls.join(" "), onClick: () => this._openRunModal(r) }, [
          el("span", { class: "t" }, this._fmtTime(r.start)),
          el("span", { class: "n" }, [iso(r.name), " · ", el("span", { style: "white-space:nowrap;" }, this._t("unit.min", { n: r.minutes }))]),
          this._skipTag(r),
        ]));
      });
      grid.appendChild(el("div", { class: "wk-day" + (i === 0 ? " today" : "") }, [head, list]));
    });
    card.appendChild(grid);
    return card;
  }

  _openRunModal(r) {
    const now = this._state.now;
    const info = this._dayInfo(r.day);
    const next = this._nextOccOf(r.schedule_id);
    const isNext = !!next && next.start === r.start;
    let close = () => {};
    const act = (service, data) => async () => { if (await this._callService(service, data)) close(); };

    const modal = el("div", { class: "modal", role: "dialog", "aria-modal": "true", "aria-labelledby": "sw-run-title" });
    modal.appendChild(el("h3", { id: "sw-run-title" }, iso(r.name)));
    modal.appendChild(el("div", { class: "muted small" }, joinParts([
      `${info.name === info.wd ? info.full : `${info.name}, ${info.full}`}, ${this._fmtTime(r.start)}`,
      this._t("unit.min", { n: r.minutes }),
    ])));
    const tag = this._skipTag(r);
    if (tag) modal.appendChild(el("div", { style: "margin-top:6px;" }, tag));
    const zones = el("div", { class: "list", style: "margin-top:12px;" }, [
      el("div", { class: "sub", style: "font-weight:600;" }, this._t("week.zones")),
    ]);
    (r.zones || []).forEach(z => zones.appendChild(el("div", { class: "zmin small" }, [
      el("span", { style: "min-width:0;" }, [iso(z.label || z.entity_id), z.indoor ? el("span", { class: "badge" }, this._t("valves.badge_indoor")) : null]),
      el("span", { class: "muted" }, this._t("unit.min", { n: z.minutes })),
    ])));
    modal.appendChild(zones);

    const actions = [el("button", { class: "btn", onClick: () => close() }, this._t("common.close"))];
    if (r.skip === "skipped_manual") {
      actions.push(el("button", { class: "btn", onClick: act("unskip", { schedule_id: r.schedule_id, date: r.day }) }, this._t("week.undo_skip")));
    } else if (isNext) {
      actions.push(el("button", { class: "btn", onClick: act("skip_next", { schedule_id: r.schedule_id }) }, this._t("week.skip_run")));
    }
    if (info.idx === 0 && r.start > now) {
      // Starts it now and drops today's scheduled run, same as the reminder's Water now.
      const water = act("run_schedule", { schedule_id: r.schedule_id });
      actions.push(el("button", { class: "btn primary", onClick: water }, this._t("zone.water_now")));
    }
    modal.appendChild(el("div", { class: "modal-actions" }, actions));

    const overlay = el("div", { class: "modal-overlay" }, modal);
    close = this._openDialog(overlay, modal, { focus: () => actions[actions.length - 1] });
  }

  _statusCard() {
    const st = this._state;
    const now = st.now;
    const active = st.active || [];
    const cycles = st.active_cycles || [];
    const soaking = st.soaking || [];
    const valves = st.valves || [];
    const rainUntil = parseInt(st.rain_delay_until || 0, 10) || 0;
    const card = el("section", { class: "card status" });

    let pill;
    let title;
    const subs = [];
    const actions = [];
    let progress = null;
    let extra = null;

    const stopAllBtn = () => el("button", {
      class: "btn danger",
      onClick: async () => {
        if (!await this._confirm(this._t("dash.stop_all_confirm"), this._t("home.stop_watering"), { focusConfirm: true })) return;
        this._callService("stop_all", {});
      },
    }, this._t("home.stop_watering"));
    const pauseBtn = (c) => el("button", {
      class: "btn",
      onClick: () => this._callService("pause_cycle", { cycle_id: c.cycle_id }),
    }, this._t("cycle.pause"));
    const planStep = (c) => this._tn("home.plan_step", { plan: iso(c.cycle_name || c.cycle_id), step: c.step, total: c.total_steps });
    const cycleOf = (r) => cycles.find(c => c.current_entity === r.entity_id) ||
      (String(r.source || "").startsWith("cycle:") ? cycles.find(c => c.cycle_id === r.source.slice(6).split("|")[0]) : null);
    const runningCycle = cycles.find(c => !c.paused);
    const pausedCycle = cycles.find(c => c.paused);
    const soakIdle = soaking.filter(s => s.phase === "soaking" && !active.some(r => r.entity_id === s.entity_id));

    if (active.length) {
      const r = active[0];
      card.setAttribute("data-entity", r.entity_id);
      const cyc = cycleOf(r);
      const remaining = Math.max(0, r.ends_at - now);
      const total = Math.max(1, r.ends_at - r.started_at);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      pill = el("span", { class: "pill run" }, this._t("home.watering_now"));
      title = this._tn("home.zone_left", {
        zone: this._valveName(r.entity_id),
        time: el("span", { "data-left": r.entity_id }, fmtRemaining(remaining)),
      });
      const soak = soaking.find(s => s.entity_id === r.entity_id && s.phase === "running");
      const chunk = soak && soak.chunks > 1 ? this._t("run.chunk", { chunk: soak.chunk, chunks: soak.chunks }) : null;
      subs.push(joinParts([cyc ? planStep(cyc) : this._t("home.started_by", { source: this._sourceLabel(r.source) }), chunk]));
      if (active.length > 1) subs.push(this._t("home.more_running", { n: active.length - 1 }));
      progress = el("div", {
        class: "progress-wrap", role: "progressbar",
        "aria-label": this._named(this._t("home.watering_now"), this._valveName(r.entity_id).textContent),
        "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(Math.round(pct)),
      }, el("div", { class: "progress-bar", style: `width:${pct}%` }));
      if (cyc && !cyc.paused) actions.push(pauseBtn(cyc));
      actions.push(stopAllBtn());
    } else if (runningCycle) {
      const c = runningCycle;
      const s = soaking.find(x => x.phase === "soaking" && x.entity_id === c.current_entity);
      if (s) {
        pill = el("span", { class: "pill run" }, this._t("zone.soaking"));
        title = this._tn("home.soak_resumes", {
          zone: this._valveName(s.entity_id),
          time: el("span", { "data-soak": s.entity_id }, fmtRemaining(Math.max(0, (parseInt(s.resume_at, 10) || 0) - now))),
        });
      } else {
        pill = el("span", { class: "pill run" }, this._t("home.watering_now"));
        title = [iso(c.cycle_name || c.cycle_id)];
      }
      subs.push(planStep(c));
      actions.push(pauseBtn(c), stopAllBtn());
    } else if (pausedCycle) {
      const c = pausedCycle;
      pill = el("span", { class: "pill pause" }, this._t("home.paused"));
      title = this._tn("home.plan_paused", { plan: iso(c.cycle_name || c.cycle_id) });
      subs.push(this._t("home.plan_paused_at", { step: c.paused_at_step || c.step, total: c.total_steps }));
      actions.push(
        el("button", { class: "btn primary", onClick: () => this._callService("resume_cycle", { cycle_id: c.cycle_id }) }, this._t("cycle.resume")),
        el("button", { class: "btn danger", onClick: () => this._callService("stop_cycle", { cycle_id: c.cycle_id }) }, this._t("common.stop")),
      );
    } else if (soakIdle.length) {
      const s = soakIdle[0];
      pill = el("span", { class: "pill run" }, this._t("zone.soaking"));
      title = this._tn("home.soak_resumes", {
        zone: this._valveName(s.entity_id),
        time: el("span", { "data-soak": s.entity_id }, fmtRemaining(Math.max(0, (parseInt(s.resume_at, 10) || 0) - now))),
      });
      subs.push(this._t("home.soak_part", { chunk: s.chunk, chunks: s.chunks }));
      actions.push(el("button", {
        class: "btn danger",
        onClick: () => this._callService("stop_valve", { entity_id: s.entity_id }),
      }, this._t("home.stop_watering")));
    } else if (rainUntil > now) {
      card.classList.add("rain");
      pill = el("span", { class: "pill pause" }, this._t("home.paused_rain"));
      title = [this._t("home.rain_until", { when: this._fmtWhen(rainUntil) })];
      subs.push(this._t("dash.rain_delay_active", { left: fmtDelayLeft(this._t, rainUntil - now) }));
      if (valves.some(v => v.rain_exempt)) subs.push(this._t("home.indoor_still"));
      actions.push(el("button", {
        class: "btn",
        onClick: () => this._callService("clear_rain_delay", {}),
      }, this._t("home.resume_now")));
    } else {
      const cool = !!(st.seasonal && st.seasonal.skips);
      pill = cool
        ? el("span", { class: "pill pause" }, this._t("home.cool_paused"))
        : el("span", { class: "pill ok" }, this._t("home.all_good"));
      const wk = this._weekRuns().find(r => r.start > now && r.skip !== "skipped_manual" && r.skip !== "rain_delay");
      const next = wk ? null : this._nextOverall();
      if (wk) {
        title = this._tn("home.next", { name: iso(wk.name), when: this._fmtWhen(wk.start) });
        const zones = wk.zones || [];
        subs.push(wk.kind === "cycle"
          ? joinParts([
            joinParts(zones.map(z => iso(z.label || z.entity_id)), ", "),
            this._t("home.total_min", { n: wk.minutes }),
          ], " · ")
          : this._t("unit.min", { n: wk.minutes }));
        if (wk.skip === "rain_delay") subs.push(this._t("week.rain"));
        else if (wk.skip === "partial_rain_delay") subs.push(this._t("week.partial_rain"));
        else if (this._coolSkip(wk)) subs.push(this._t("week.cool_skip"));
      } else if (next) {
        const nr = next.next_run;
        const cycle = nr.cycle_id ? (st.cycles || []).find(c => c.id === nr.cycle_id) : null;
        title = this._tn("home.next", {
          name: iso(cycle ? cycle.name : next.label),
          when: this._fmtWhen(parseInt(nr.fires_at, 10)),
        });
        if (cycle) {
          const steps = cycle.steps || [];
          subs.push(joinParts([
            joinParts(steps.map(x => this._valveName(x.entity_id)), ", "),
            this._t("home.total_min", { n: steps.reduce((a, x) => a + (x.duration_min || 0), 0) }),
          ], " · "));
        } else {
          subs.push(this._t("unit.min", { n: nr.duration_min }));
        }
      } else {
        title = [this._t("home.nothing_planned")];
        subs.push(this._t("home.nothing_planned_hint"));
      }
      actions.push(el("button", {
        class: "btn",
        "aria-expanded": this._rainOpen ? "true" : "false",
        onClick: () => { this._rainOpen = !this._rainOpen; this._render(); },
      }, this._t("home.pause_rain")));
      if (this._rainOpen) extra = this._rainChooser();
    }

    const flow = st.flow || {};
    if (flow.entity_id) {
      const flowVal = (flow.value === null || flow.value === undefined) ? this._t("common.unavailable") : String(flow.value);
      subs.push(this._t("dash.flow_value", { value: flowVal }));
    }

    card.appendChild(el("div", { class: "status-row" }, [
      el("div", { style: "min-width:0;" }, [
        pill,
        el("div", { class: "status-title" }, title),
        ...subs.map(s => el("div", { class: "muted small" }, s)),
      ]),
      el("div", { class: "actions" }, actions),
    ]));
    if (progress) card.appendChild(progress);
    if (extra) card.appendChild(extra);
    return card;
  }

  _nextOverall() {
    let best = null;
    (this._state.valves || []).forEach(v => {
      if (!v.next_run) return;
      const ts = parseInt(v.next_run.fires_at, 10) || 0;
      if (!ts) return;
      if (v.next_run.schedule_id && this._isSkipped(v.next_run.schedule_id, I18N.dayKey(ts, this._hass))) return;
      if (!best || ts < (parseInt(best.next_run.fires_at, 10) || 0)) best = v;
    });
    return best;
  }

  _rainChooser() {
    const valves = this._state.valves || [];
    if (this._rainTarget && !valves.some(v => v.entity_id === this._rainTarget)) this._rainTarget = "";
    const targetSel = el("select", { "aria-label": this._t("home.rain_only_zone") });
    targetSel.appendChild(el("option", { value: "" }, this._t("dash.all_valves")));
    valves.forEach((v) => {
      const opt = el("option", { value: v.entity_id }, v.label || v.entity_id);
      if (v.entity_id === this._rainTarget) opt.selected = true;
      targetSel.appendChild(opt);
    });
    targetSel.value = this._rainTarget;
    targetSel.addEventListener("change", () => { this._rainTarget = targetSel.value; });
    const setDelay = async (hours) => {
      const target = this._rainTarget;
      if (target && !(this._state.valves || []).some(v => v.entity_id === target)) {
        this._rainTarget = "";
        this._toast(this._t("dash.valve_gone"), "error");
        this._render();
        return;
      }
      this._rainOpen = false;
      this._rainTarget = "";
      if (!await this._callService("set_rain_delay", target ? { hours, entity_id: [target] } : { hours })) {
        this._rainOpen = true;
        this._rainTarget = target;
        this._render();
      }
    };
    return el("div", { class: "rain-chooser" }, [
      el("div", { class: "row-between" }, [
        el("span", { class: "small" }, this._t("home.rain_for")),
        el("div", { class: "actions" }, [
          el("button", { class: "btn small", onClick: () => setDelay(24) }, this._t("time.short_h", { n: 24 })),
          el("button", { class: "btn small", onClick: () => setDelay(48) }, this._t("time.short_h", { n: 48 })),
          el("button", { class: "btn small", onClick: () => setDelay(168) }, this._t("time.short_d", { n: 7 })),
        ]),
      ]),
      el("label", { class: "row-between small" }, [el("span", {}, this._t("home.rain_only_zone")), targetSel]),
      el("p", { class: "muted small", style: "margin:0;" }, this._t("dash.rain_hint")),
    ]);
  }

  _zoneCard(v) {
    const st = this._state;
    const now = st.now;
    const id = v.entity_id;
    const active = (st.active || []).find(r => r.entity_id === id);
    const soak = active ? null : (st.soaking || []).find(s => s.entity_id === id && s.phase === "soaking");
    const rainUntil = parseInt(st.rain_delay_until || 0, 10) || 0;
    const paused = !!valveDelayUntil(v, now) || (rainUntil > now && !v.rain_exempt);

    let pill;
    if (active) pill = el("span", { class: "pill run" }, this._t("zone.watering"));
    else if (soak) pill = el("span", { class: "pill run" }, this._t("zone.soaking"));
    else if (paused) pill = el("span", { class: "pill pause" }, this._t("zone.paused"));
    else pill = el("span", { class: "pill idle" }, this._t("zone.off"));

    let nextLine = this._zoneNextLine(v);
    if (v.rain_exempt) nextLine += " · " + this._t("zone.indoor_suffix");

    const titleId = uid("sw-zone");
    const card = el("article", { class: "card zone" + (active ? " running" : ""), "data-entity": id, "aria-labelledby": titleId }, [
      el("div", { class: "zone-head" }, [
        el("strong", { id: titleId }, [iso(v.label), v.enabled ? "" : " " + this._t("common.disabled_tag")]),
        pill,
      ]),
      el("div", { class: "sub small" }, nextLine),
    ]);

    if (active) {
      const remaining = Math.max(0, active.ends_at - now);
      const total = Math.max(1, active.ends_at - active.started_at);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      card.appendChild(el("div", {
        class: "progress-wrap", role: "progressbar", "aria-label": this._named(this._t("zone.watering"), v.label),
        "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(Math.round(pct)),
      }, el("div", { class: "progress-bar", style: `width:${pct}%` })));
      card.appendChild(el("div", { class: "actions" }, [
        el("button", {
          class: "btn danger", "aria-label": this._named(this._t("common.stop"), v.label),
          "data-focus-id": `stop:${id}`, "data-refocus": `water:${id}`,
          onClick: () => this._callService("stop_valve", { entity_id: id }),
        }, this._t("common.stop")),
        el("span", { class: "muted small" }, this._tn("run.left", { time: el("span", { "data-left": id }, fmtRemaining(remaining)) })),
      ]));
    } else if (soak) {
      const ownerCycle = soak.owner === "cycle"
        ? (st.active_cycles || []).find(c => c.current_entity === id)
        : null;
      card.appendChild(el("div", { class: "actions" }, [
        ownerCycle
          ? el("button", { class: "btn danger", onClick: () => this._callService("stop_cycle", { cycle_id: ownerCycle.cycle_id }) }, this._t("run.stop_cycle"))
          : el("button", {
            class: "btn danger", "aria-label": this._named(this._t("common.stop"), v.label), "data-refocus": `water:${id}`,
            onClick: () => this._callService("stop_valve", { entity_id: id }),
          }, this._t("common.stop")),
        el("span", { class: "muted small" }, this._tn("home.resumes_in", {
          time: el("span", { "data-soak": id }, fmtRemaining(Math.max(0, (parseInt(soak.resume_at, 10) || 0) - now))),
        })),
      ]));
    } else {
      const cur = () => Math.min(1440, Math.max(1, parseInt(this._quickDur[id] ?? v.default_duration_min, 10) || v.default_duration_min || 10));
      const val = el("span", { class: "stepper-val", "aria-live": "polite" }, this._t("unit.min", { n: cur() }));
      const change = (dir) => {
        const n = stepMinutes(cur(), dir);
        this._quickDur[id] = n;
        val.textContent = this._t("unit.min", { n });
      };
      card.appendChild(el("div", { class: "actions" }, [
        el("span", { class: "stepper" }, [
          el("button", { type: "button", "aria-label": this._named(this._t("zone.less"), v.label), title: this._t("zone.less"), onClick: () => change(-1) }, "−"),
          val,
          el("button", { type: "button", "aria-label": this._named(this._t("zone.more"), v.label), title: this._t("zone.more"), onClick: () => change(1) }, "+"),
        ]),
        el("button", {
          class: "btn primary",
          "aria-label": this._named(this._t("zone.water_now"), v.label),
          "data-focus-id": `water:${id}`, "data-refocus": `stop:${id}`,
          onClick: () => this._callService("run_valve", { entity_id: id, duration_minutes: cur() }),
        }, this._t("zone.water_now")),
      ]));
    }
    return card;
  }

  // The zone's next run that will really water, from the server (UX-010): the same source as the status card,
  // so a skipped day or a rain pause shows here too, with the run it drops.
  _zoneNextLine(v) {
    const nr = v.next_run && parseInt(v.next_run.fires_at, 10) ? v.next_run : null;
    const skip = v.next_skip && parseInt(v.next_skip.fires_at, 10) ? v.next_skip : null;
    const when = nr ? this._fmtWhen(parseInt(nr.fires_at, 10)) : "";
    const n = nr ? nr.duration_min : 0;
    if (skip && skip.reason === "rain_delay" && parseInt(skip.until, 10)) {
      const until = this._fmtWhen(parseInt(skip.until, 10));
      return nr ? this._t("home.next_zone_paused", { until, when, n }) : this._t("home.zone_paused_only", { until });
    }
    if (skip) {
      const day = this._fmtWhen(parseInt(skip.fires_at, 10));
      return nr ? this._t("home.next_zone_skipped", { day, when, n }) : this._t("home.zone_skipped_only", { day });
    }
    return nr ? this._t("home.next_zone", { when, n }) : this._t("home.no_schedule");
  }

  // "today 6:00", "yesterday 6:00", else "Mon 6:00" (UX-012).
  _relWhen(ts) {
    const today = I18N.dayKey(this._state.now, this._hass);
    const day = I18N.dayKey(ts, this._hass);
    const time = this._fmtTime(ts);
    if (day === today) return this._t("act.today_at", { time });
    if (dayNum(day) === dayNum(today) - 1) return this._t("act.yesterday_at", { time });
    return `${this._fmtDate(ts, { weekday: "short" })} ${time}`;
  }

  // A zone row that really watered (#67): completed, or stopped / replaced after watering some minutes.
  _watered(h) {
    if (this._isPlanId(h.valve_entity_id)) return false;
    if (h.status === "completed") return true;
    return (h.status === "cancelled" || h.status === "superseded") && (parseInt(h.duration_min, 10) || 0) > 0;
  }

  // Zones and minutes watered in a list of history rows: "3 zones · 30 min" (UX-012).
  _wateredTotal(rows) {
    const done = rows.filter(h => this._watered(h));
    if (!done.length) return "";
    const zones = new Set(done.map(h => h.valve_entity_id)).size;
    const min = done.reduce((a, h) => a + (parseInt(h.duration_min, 10) || 0), 0);
    return this._t("act.total", { zones: this._t("act.zones", { n: zones }), min: this._t("unit.min", { n: min }) });
  }

  // One line above the zones that answers "did it water?" (UX-012): when the most recent watering finished (#67:
  // a start that never watered is not one), what that day watered, and a skip that came after it.
  _lastWateringLine() {
    const hist = this._state.history || [];
    const latest = (rows) => rows.reduce((a, h) => (!a || h.ts > a.ts ? h : a), null);
    const last = latest(hist.filter(h => this._watered(h)));
    const parts = [];
    if (last) {
      const day = I18N.dayKey(last.ts, this._hass);
      const rows = hist.filter(h => I18N.dayKey(h.ts, this._hass) === day);
      parts.push(this._t("act.last_watering", { when: this._relWhen(last.ts), total: this._wateredTotal(rows) }));
    }
    const skip = latest(hist.filter(h => isSkipStatus(h.status)));
    if (skip && (!last || skip.ts > last.ts)) {
      // "Skipped (rain), today 6:00 AM": the status already says skipped, so it is said once.
      const reason = String(this._statusLabel(skip.status) || "");
      parts.push(this._t("act.last_skipped", { when: this._relWhen(skip.ts), reason: reason.charAt(0).toLocaleUpperCase(this._lang) + reason.slice(1) }));
    }
    return parts.length ? el("p", { class: "last-line" }, parts.join(" · ")) : null;
  }

  // Recent activity by day, with a total per day; Today / Yesterday / 7 days in one click (UX-012).
  _activityCard() {
    const st = this._state;
    const history = st.history || [];
    const today = I18N.dayKey(st.now, this._hass);
    const yesterday = dayFromNum(dayNum(today) - 1);
    const weekStart = dayFromNum(dayNum(today) - 6);
    const filter = this._actFilter;
    const inFilter = (day) => (filter === "today" ? day === today : filter === "yesterday" ? day === yesterday : day >= weekStart);
    const titleId = uid("sw-activity");
    const seg = (key, label) => el("button", {
      class: "btn small", type: "button", "aria-pressed": filter === key ? "true" : "false",
      onClick: () => { this._actFilter = key; this._render(); },
    }, label);
    const card = el("section", { class: "card", "aria-labelledby": titleId }, [
      el("div", { class: "act-head" }, [
        el("h2", { id: titleId }, this._t("dash.recent")),
        el("button", { class: "btn", onClick: () => { this._view = "reports"; this._render(); } }, this._t("home.reports")),
      ]),
    ]);
    if (!history.length) {
      card.appendChild(el("div", { class: "empty" }, this._t("dash.no_history")));
      return card;
    }
    card.appendChild(el("div", { class: "seg", role: "group", "aria-label": this._t("act.show") }, [
      seg("today", this._t("week.today")), seg("yesterday", this._t("act.yesterday")), seg("week", this._t("act.week")),
    ]));
    // A zone run that has finished is told by its finish row; its "started" row is noise (UX-012).
    const ended = new Set();
    const rows = history.filter((h) => {
      const id = h.valve_entity_id;
      if (h.status === "started" && !this._isPlanId(id) && ended.has(id)) return false;
      if (h.status !== "started") ended.add(id);
      return true;
    });
    const days = [];
    rows.forEach((h) => {
      const day = I18N.dayKey(h.ts, this._hass);
      if (!inFilter(day)) return;
      let d = days.find(x => x.day === day);
      if (!d) { d = { day, rows: [] }; days.push(d); }
      d.rows.push(h);
    });
    if (!days.length) {
      card.appendChild(el("div", { class: "empty" }, this._t("act.none")));
      return card;
    }
    days.forEach(({ day, rows: dayRows }) => {
      const label = day === today ? this._t("week.today") : day === yesterday ? this._t("act.yesterday")
        : this._fmtDate(dayRows[0].ts, { weekday: "short", day: "numeric", month: "short" });
      const total = this._wateredTotal(dayRows);
      card.appendChild(el("h3", { class: "act-day" }, [el("span", {}, label), total ? el("span", { class: "muted" }, total) : null]));
      const ul = el("ul", { class: "log" });
      this._groupHistory(dayRows).slice(0, 40).forEach(g => ul.appendChild(this._activityItem(g)));
      card.appendChild(ul);
    });
    return card;
  }

  _activitySentence(h) {
    const plan = this._isPlanId(h.valve_entity_id);
    const name = plan ? iso(this._planName(h.valve_entity_id, h.name)) : this._valveName(h.valve_entity_id);
    if (!plan && h.status === "completed") return this._tn("home.act_watered", { zone: name, n: h.duration_min });
    return this._tn("home.act_status", { name, status: this._statusLabel(h.status) });
  }

  // "shortened from 300 min" when a webhook or calendar run was cut to the longest external run (#79).
  _cappedLabel(note) {
    const m = /(?:^|\|)capped:(\d+)/.exec(String(note || ""));
    return m ? this._t("home.act_capped", { n: Number(m[1]) }) : null;
  }

  _activityItem(g) {
    const h = g.entry;
    const left = el("div", { style: "min-width:0;" }, [
      el("div", {}, [...this._activitySentence(h), h.liters > 0 ? " · " + this._fmtLiters(h.liters) : null]),
      el("div", { class: "sub" }, joinParts([this._sourceLabel(h.source, h.plan_name), this._cappedLabel(h.note)])),
    ]);
    if (g.kind === "cycle") {
      (g.children || []).filter(c => c.status !== "started").forEach(c => {
        left.appendChild(el("div", { class: "kids" }, joinParts([
          this._valveName(c.valve_entity_id),
          isSkipStatus(c.status) ? null : this._t("unit.min", { n: c.duration_min }),
          this._statusLabel(c.status),
          c.liters > 0 ? this._fmtLiters(c.liters) : null,
        ])));
      });
    }
    // Skipped rows read lighter than runs (UX-012); the day is in the heading above.
    return el("li", { class: isSkipStatus(h.status) ? "skip" : null }, [
      left,
      el("span", { class: "when" }, this._fmtTime(h.ts)),
    ]);
  }

  _groupHistory(history) {
    const used = new Set();
    const out = [];
    for (let i = 0; i < history.length; i++) {
      if (used.has(i)) continue;
      const h = history[i];
      if (this._isPlanId(h.valve_entity_id)) {
        const cycleId = h.valve_entity_id;
        const children = [];
        for (let j = i + 1; j < history.length; j++) {
          if (used.has(j)) continue;
          const c = history[j];
          if (c.valve_entity_id === cycleId) break;
          if (c.source && c.source.startsWith(`cycle:${cycleId}`)) {
            children.push(c);
            used.add(j);
          }
        }
        out.push({ kind: "cycle", entry: h, children });
      } else {
        out.push({ kind: "valve", entry: h });
      }
      used.add(i);
    }
    return out;
  }

  // ---------- Zones ----------

  _renderZones(root) {
    const valves = this._state.valves || [];
    root.appendChild(el("div", { class: "section-h" }, [
      el("h2", {}, this._t("tab.zones")),
      el("button", { class: "btn primary", onClick: () => this._openWizard() }, this._t("zones.add")),
    ]));
    if (!valves.length) {
      root.appendChild(el("div", { class: "card empty-state" }, [
        el("p", { class: "muted" }, this._t("zones.empty")),
        el("button", { class: "btn primary", onClick: () => this._openWizard() }, this._t("home.setup_start")),
      ]));
    } else {
      valves.forEach(v => root.appendChild(this._zoneAdminCard(v)));
    }
    root.appendChild(el("button", { class: "link-btn", onClick: () => this._openValveModal(null) }, this._t("zones.manual")));
  }

  _zoneAdminCard(v) {
    const st = this._state;
    const stats = v.stats || {};
    let lastLine = this._t("valves.never_run");
    if (stats.last_run) {
      const ago = Math.max(0, st.now - stats.last_run.ts);
      lastLine = joinParts([
        this._t("valves.last", { ago: this._fmtAgo(ago) }),
        // A skipped run did not water: no planned minutes next to it (#31).
        isSkipStatus(stats.last_run.status) ? null : this._t("unit.min", { n: stats.last_run.duration_min }),
        this._statusLabel(stats.last_run.status),
      ]).join("");
    }
    // "Never run" already says there were no runs this week (UX-018).
    const week = stats.runs_7d
      ? this._t("valves.week", { n: stats.runs_7d, runs: stats.runs_7d, min: stats.total_min_7d })
      : (stats.last_run ? this._t("valves.week_none") : "");
    const badges = [];
    if (v.rain_exempt) badges.push(el("span", { class: "badge", title: this._t("valves.badge_indoor_title") }, this._t("valves.badge_indoor")));
    if ((v.soak_run_min || 0) > 0 && (v.soak_pause_min || 0) > 0) {
      badges.push(el("span", { class: "badge", title: this._t("valves.badge_soak_title") }, this._t("valves.badge_soak", { run: v.soak_run_min, pause: v.soak_pause_min })));
    }
    if (v.moisture_entity) badges.push(el("span", { class: "badge", title: v.moisture_entity }, this._t("valves.badge_moisture")));
    const vDelay = valveDelayUntil(v, st.now);
    if (vDelay) {
      badges.push(el("span", { class: "badge", title: this._t("valves.badge_delay_title") }, this._t("valves.badge_delay", { until: this._fmtWhen(vDelay) })));
    }

    const titleId = uid("sw-zone-admin");
    const card = el("article", { class: "card", "aria-labelledby": titleId }, [
      el("div", { class: "admin-head" }, [
        el("div", { style: "min-width:0;" }, [
          el("div", { class: "name" }, [el("span", { id: titleId }, iso(v.label)), v.enabled ? "" : " " + this._t("common.disabled_tag"), ...badges]),
          // The entity id is in Edit zone; here it was jargon on the screen gardeners use most (UX-018).
          el("div", { class: "sub", title: v.entity_id }, this._t("zones.min_per_run", { n: v.default_duration_min })),
          el("div", { class: "sub" }, week ? lastLine + " • " + week : lastLine),
          (v.water_total_l || 0) > 0 ? el("div", { class: "sub" }, this._t("valves.water_used", { amount: this._fmtLiters(v.water_total_l) })
            + (v.avg_lpm > 0 ? " · " + this._t("valves.usually_lpm", { lpm: this._fmtLpm(v.avg_lpm) }) : "")) : null,
        ]),
        el("div", { class: "actions" }, [
          el("button", { class: "btn small", "aria-label": this._named(this._t("zones.edit"), v.label), onClick: () => this._openValveModal(v) }, this._t("zones.edit")),
          el("button", {
            class: "btn danger small",
            "aria-label": this._named(this._t("zones.delete"), v.label),
            onClick: () => this._confirmDelete(this._t("valves.delete_confirm", { name: v.label }), "remove_valve", { entity_id: v.entity_id }),
          }, this._t("zones.delete")),
        ]),
      ]),
    ]);

    const body = el("div", { class: "admin-body" });
    const own = (st.schedules || []).filter(s => s.valve_entity_id === v.entity_id);
    own.forEach(s => body.appendChild(this._schedRow(s, true, v.label)));
    const plans = (st.cycles || []).filter(c => (c.steps || []).some(x => x.entity_id === v.entity_id));
    plans.forEach(c => {
      const times = (st.schedules || []).filter(s => s.cycle_id === c.id);
      const when = times.length
        ? joinParts(times.map(s => this._whenNodes(s)), "; ")
        : [this._t("zones.plan_no_times")];
      body.appendChild(el("div", { class: "sub small" }, this._tn("zones.in_plan", { plan: iso(c.name), when: el("span", {}, when) })));
    });
    if (!own.length && !plans.length) body.appendChild(el("div", { class: "muted small" }, this._t("zones.no_times")));
    body.appendChild(el("div", {}, el("button", {
      class: "btn ghost",
      "aria-label": this._named(this._t("zones.add_time"), v.label),
      onClick: () => this._openScheduleModal(null, { kind: "valve", id: v.entity_id }),
    }, this._t("zones.add_time"))));
    card.appendChild(body);
    return card;
  }

  _schedRow(s, withDuration, ownerName) {
    const condCount = Array.isArray(s.conditions) ? s.conditions.length : 0;
    const main = [...this._whenNodes(s)];
    if (withDuration) main.push(" · " + this._t("unit.min", { n: s.duration_min }));
    if (!s.enabled) main.push(" " + this._t("common.disabled_tag"));
    // "Front lawn, Mon, Wed at 06:00": which schedule a control acts on (UX-007).
    const what = [s.name || ownerName, el("span", {}, this._whenNodes(s)).textContent].filter(Boolean).join(", ");
    const toggle = el("button", {
      class: "switch",
      role: "switch",
      "aria-checked": s.enabled ? "true" : "false",
      "aria-label": this._named(this._t("common.enabled"), what),
      title: this._t(s.enabled ? "common.disable" : "common.enable"),
      onClick: () => this._callService("update_schedule", { schedule_id: s.id, enabled: !s.enabled }),
    });
    const skipped = this._nextSkippedDay(s);
    let skipBtn = null;
    if (skipped) {
      skipBtn = el("button", {
        class: "btn small",
        "aria-label": this._named(this._t("common.undo"), what),
        onClick: () => this._callService("unskip", { schedule_id: s.id, date: skipped }),
      }, this._t("common.undo"));
    } else if (this._schedActive(s)) {
      skipBtn = el("button", {
        class: "btn small",
        "aria-label": this._named(this._t("sched.skip_next"), what),
        onClick: () => this._callService("skip_next", { schedule_id: s.id }),
      }, this._t("sched.skip_next"));
    }
    return el("div", { class: "sched-row" }, [
      el("div", { style: "min-width:0;" }, [
        el("div", {}, [
          ...main,
          condCount ? el("span", { class: "badge" }, condCount === 1 ? this._t("sched.conditions_one") : this._t("sched.conditions_other", { n: condCount })) : null,
          skipped ? el("span", { class: "badge warn" }, this._t("sched.next_skipped")) : null,
        ]),
        s.name && s.name !== ownerName ? el("div", { class: "sub" }, iso(s.name)) : null,
      ]),
      el("div", { class: "actions" }, [
        skipBtn,
        toggle,
        el("button", { class: "btn small", "aria-label": this._named(this._t("sched.edit_time"), what), onClick: () => this._openScheduleModal(s) }, this._t("sched.edit_time")),
        el("button", {
          class: "btn danger small",
          "aria-label": this._named(this._t("sched.delete_time"), what),
          onClick: () => this._confirmDelete(this._t("sched.delete_confirm"), "remove_schedule", { schedule_id: s.id }),
        }, this._t("sched.delete_time")),
      ]),
    ]);
  }

  // Whether a schedule and its target are enabled, so it has upcoming runs.
  _schedActive(s) {
    if (!s.enabled) return false;
    if (s.cycle_id) return !!(this._state.cycles || []).find(c => c.id === s.cycle_id && c.enabled);
    return !!(this._state.valves || []).find(v => v.entity_id === s.valve_entity_id && v.enabled);
  }

  // Day of the schedule's next run when that run is skipped by the user, else null.
  _nextSkippedDay(s) {
    if (!this._schedActive(s)) return null;
    const next = this._nextOccOf(s.id);
    if (next) return next.skip === "skipped_manual" ? next.day : null;
    const today = this._weekDays()[0];
    const future = (((this._state.skips || {})[s.id]) || []).filter(d => d > today).sort();
    return future.length ? future[0] : null;
  }

  _openValveModal(existing) {
    let chosen = existing ? existing.entity_id : "";
    let label = existing ? existing.label : "";
    let duration = existing ? existing.default_duration_min : (this._state.options.default_duration || 10);
    let enabled = existing ? !!existing.enabled : true;

    const labelInput = el("input", { type: "text", maxlength: "80", value: label, placeholder: this._t("valves.label_ph"), "aria-required": "true" });
    const labelErr = fieldError("sw-valve-label-err");
    labelInput.addEventListener("input", () => { label = labelInput.value; if (label.trim()) setFieldError(labelErr, labelInput, ""); });

    const durInput = el("input", { type: "number", min: "1", max: "1440", value: String(duration) });
    const durErr = el("div", { class: "field-error", id: "sw-valve-duration-err", role: "alert", hidden: true });
    const setDurErr = (msg) => {
      durErr.textContent = msg || "";
      durErr.hidden = !msg;
      if (msg) { durInput.setAttribute("aria-invalid", "true"); durInput.setAttribute("aria-describedby", durErr.id); }
      else { durInput.removeAttribute("aria-invalid"); durInput.removeAttribute("aria-describedby"); }
    };
    durInput.addEventListener("input", () => { if (minutesValue(durInput.value) !== null) setDurErr(""); });
    durInput.setAttribute("aria-required", "true");

    const enabledField = this._switchField(this._t("common.enabled"), enabled, (on) => { enabled = on; });

    const rainExemptInput = el("input", { type: "checkbox" });
    rainExemptInput.checked = !!(existing && existing.rain_exempt);

    // Keyboard-operable entity list (BUG-004): each row is a toggle button; the list is a named group and sits
    // outside the search field's label, so the search box is named by the caption alone.
    const pickerCap = uid("sw-entity-cap");
    const search = el("input", { type: "text", placeholder: this._t("valves.search_ph"), "aria-labelledby": pickerCap });
    const picker = el("div", { class: "entity-picker", role: "group", "aria-labelledby": pickerCap });
    const entityErr = fieldError("sw-valve-entity-err");
    const renderPicker = () => {
      const q = search.value.trim().toLowerCase();
      picker.innerHTML = "";
      const filtered = this._state.controllable.filter((e) =>
        !q || e.entity_id.toLowerCase().includes(q) || e.friendly_name.toLowerCase().includes(q)
      );
      if (!filtered.length) {
        picker.appendChild(el("div", { class: "empty", style: "padding:10px;" }, this._t("valves.no_matches")));
      }
      filtered.forEach((e) => {
        const row = el("button", {
          type: "button", class: "entity-row", "aria-pressed": chosen === e.entity_id ? "true" : "false",
        }, [
          el("span", {}, [
            el("span", { style: "display:block;font-weight:600" }, iso(e.friendly_name)),
            el("span", { class: "muted", style: "display:block;font-size:12px" }, ltr(e.entity_id)),
          ]),
          el("span", { class: "domain" }, e.domain),
        ]);
        row.addEventListener("click", () => {
          chosen = e.entity_id;
          if (!label.trim()) { label = e.friendly_name; labelInput.value = label; setFieldError(labelErr, labelInput, ""); }
          // Update in place: rebuilding the list would drop the focus from the pressed row.
          picker.querySelectorAll(".entity-row").forEach(r => r.setAttribute("aria-pressed", r === row ? "true" : "false"));
          setFieldError(entityErr, picker, "");
        });
        picker.appendChild(row);
      });
    };
    search.addEventListener("input", renderPicker);
    renderPicker();

    const soakRunInput = el("input", { type: "number", min: "0", max: "1440", value: String(existing ? (existing.soak_run_min || 0) : 0) });
    const soakPauseInput = el("input", { type: "number", min: "0", max: "1440", value: String(existing ? (existing.soak_pause_min || 0) : 0) });
    const vMoistEntity = el("input", { type: "text", dir: "ltr", placeholder: "sensor.zone_moisture", value: String((existing && existing.moisture_entity) || "") });
    const vMoistAttr = el("input", { type: "text", maxlength: "255", placeholder: this._t("common.moisture_attr_ph"), value: String((existing && existing.moisture_attribute) || "") });
    const vMoistThrRaw = (existing && existing.moisture_threshold !== null && existing.moisture_threshold !== undefined) ? String(existing.moisture_threshold) : "";
    const vMoistThreshold = el("input", { type: "number", min: "0", max: "100", step: "0.5", value: vMoistThrRaw });

    const flowRateRaw = (existing && existing.flow_rate_lpm !== null && existing.flow_rate_lpm !== undefined) ? String(existing.flow_rate_lpm) : "";
    const flowRateInput = el("input", { type: "number", min: "0", max: "10000", step: "any", inputmode: "decimal", value: flowRateRaw });
    const flowErr = fieldError("sw-valve-flow-err");
    flowRateInput.addEventListener("input", () => setFieldError(flowErr, flowRateInput, ""));

    const hasAdvanced = !!(existing && ((existing.soak_run_min || 0) > 0 || (existing.soak_pause_min || 0) > 0 || existing.moisture_entity || flowRateRaw));
    const advBody = el("div", { style: hasAdvanced ? "" : "display:none;" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("valves.flow_rate")), flowRateInput, flowErr]),
      el("p", { class: "muted", style: "font-size:12px;margin:-6px 0 12px;" }, [
        this._t("valves.flow_rate_hint"),
        existing && existing.avg_lpm > 0 ? el("br") : null,
        existing && existing.avg_lpm > 0 ? this._t("valves.usual_flow", { lpm: this._fmtLpm(existing.avg_lpm) }) : null,
      ]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, this._t("valves.soak_run")), soakRunInput]),
        el("label", { class: "field" }, [el("span", {}, this._t("valves.soak_pause")), soakPauseInput]),
      ]),
      el("p", { class: "muted", style: "font-size:12px;margin:-6px 0 12px;" }, this._t("valves.soak_hint")),
      el("label", { class: "field" }, [el("span", {}, this._t("valves.moisture_sensor")), vMoistEntity]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, this._t("common.attribute_optional")), vMoistAttr]),
        el("label", { class: "field" }, [el("span", {}, this._t("common.skip_when_gte")), vMoistThreshold]),
      ]),
    ]);
    const advToggle = el("button", { class: "btn small", type: "button", "aria-expanded": hasAdvanced ? "true" : "false" }, this._t(hasAdvanced ? "common.hide_advanced" : "common.show_advanced"));
    advToggle.addEventListener("click", () => {
      const hidden = advBody.style.display === "none";
      advBody.style.display = hidden ? "" : "none";
      advToggle.setAttribute("aria-expanded", hidden ? "true" : "false");
      advToggle.textContent = this._t(hidden ? "common.hide_advanced" : "common.show_advanced");
    });

    const fields = [
      el("label", { class: "field" }, [el("span", {}, this._t("valves.label")), labelInput, labelErr]),
      el("div", { class: "field" }, [el("span", { id: pickerCap }, this._t("valves.search")), search, picker, entityErr]),
      el("label", { class: "field" }, [el("span", {}, this._t("valves.default_duration")), durInput, durErr]),
      enabledField,
      el("label", { class: "field" }, [el("span", {}, this._t("valves.indoor")), rainExemptInput]),
      el("div", { class: "field", style: "padding-top:10px;border-top:1px solid var(--sw-border);" }, [advToggle]),
      advBody,
    ];

    this._showModal(this._t(existing ? "valves.edit_title" : "valves.add_title"), fields, async () => {
      // Every problem is shown next to its field; focus goes to the first one, the toast repeats it (UX-005).
      const invalid = [];
      const check = (bad, node, input, msg, focusTarget) => {
        setFieldError(node, input, bad ? msg : "");
        if (bad) invalid.push([focusTarget || input, msg]);
      };
      check(!label.trim(), labelErr, labelInput, this._t("valves.label_required"));
      check(!chosen, entityErr, picker, this._t("valves.pick_entity"), picker.querySelector(".entity-row") || search);
      const duration = minutesValue(durInput.value);
      if (duration === null || durInput.validity.badInput) {
        setDurErr(this._t("valves.err_duration"));
        invalid.push([durInput, this._t("valves.err_duration")]);
      } else {
        setDurErr("");
      }
      const clampMin = (input) => Math.min(1440, Math.max(0, parseInt(input.value, 10) || 0));
      const thrRaw = vMoistThreshold.value.trim();
      const thr = thrRaw === "" ? null : parseFloat(thrRaw);
      const flowRaw = flowRateInput.value.trim();
      const flowRate = flowRaw === "" ? null : parseFloat(flowRaw);
      const flowBad = flowRateInput.validity.badInput || (flowRaw !== "" && (isNaN(flowRate) || flowRate <= 0 || flowRate > 10000));
      if (flowBad && advBody.style.display === "none") advToggle.click();
      check(flowBad, flowErr, flowRateInput, this._t("valves.flow_rate_invalid"));
      if (invalid.length) {
        invalid[0][0].focus();
        this._toast(invalid[0][1], "error");
        return false;
      }
      const ok = await this._callService("add_valve", {
        entity_id: chosen,
        label: label.trim(),
        default_duration_minutes: duration,
        enabled,
        rain_exempt: rainExemptInput.checked,
        soak_run_minutes: clampMin(soakRunInput),
        soak_pause_minutes: clampMin(soakPauseInput),
        moisture_entity: vMoistEntity.value.trim(),
        moisture_attribute: vMoistAttr.value.trim(),
        moisture_threshold: (thr === null || isNaN(thr)) ? null : thr,
        flow_rate_lpm: flowRate,
      });
      if (ok && existing && existing.entity_id !== chosen) {
        const oldSchedules = (this._state.schedules || []).filter(s => s.valve_entity_id === existing.entity_id);
        for (const s of oldSchedules) {
          const payload = {
            valve_entity_id: chosen,
            ...timePayload(s),
            ...repeatPayload(s),
            duration_minutes: s.duration_min,
            name: s.name || "",
            enabled: !!s.enabled,
          };
          if (Array.isArray(s.conditions)) payload.conditions = s.conditions;
          if (!await this._callService("add_schedule", payload)) {
            this._toast(this._t("valves.migration_failed", { name: existing.label }), "error");
            return false;
          }
        }
        await this._callService("remove_valve", { entity_id: existing.entity_id });
      }
      return ok;
    });
  }

  // ---------- Programs (watering plans) ----------

  _renderPrograms(root) {
    const st = this._state;
    const cycles = st.cycles || [];
    root.appendChild(el("div", { class: "section-h" }, [
      el("h2", {}, this._t("plans.title")),
      el("button", { class: "btn primary", onClick: () => this._openWizard() }, this._t("home.new_plan")),
    ]));
    if (!cycles.length) {
      root.appendChild(el("div", { class: "card empty-state" }, [
        el("p", { class: "muted" }, this._t("plans.empty")),
        el("button", { class: "btn primary", onClick: () => this._openWizard() }, this._t("home.new_plan")),
      ]));
    } else {
      cycles.forEach(c => root.appendChild(this._planCard(c)));
    }

    const valveIds = new Set((st.valves || []).map(v => v.entity_id));
    const cycleIds = new Set(cycles.map(c => c.id));
    const orphans = (st.schedules || []).filter(s => s.cycle_id ? !cycleIds.has(s.cycle_id) : !valveIds.has(s.valve_entity_id));
    if (orphans.length) {
      const card = el("div", { class: "card" }, [
        el("h2", {}, this._t("plans.orphans")),
        el("p", { class: "muted small", style: "margin:0 0 8px;" }, this._t("plans.orphans_hint")),
      ]);
      const list = el("div", { class: "list" });
      orphans.forEach(s => list.appendChild(el("div", { class: "sched-row" }, [
        el("div", {}, [...this._whenNodes(s), " · ", ltr(s.cycle_id || s.valve_entity_id)]),
        el("button", {
          class: "btn danger small",
          onClick: () => this._confirmDelete(this._t("sched.delete_confirm"), "remove_schedule", { schedule_id: s.id }),
        }, this._t("common.delete")),
      ])));
      card.appendChild(list);
      root.appendChild(card);
    }

    root.appendChild(el("button", { class: "link-btn", onClick: () => this._openCycleModal(null) }, this._t("plans.manual")));
  }

  _planCard(c) {
    const st = this._state;
    const ac = (st.active_cycles || []).find(a => a.cycle_id === c.id);
    const steps = c.steps || [];
    const totalMin = steps.reduce((a, s) => a + (s.duration_min || 0), 0);
    const head = [iso(c.name || c.id), c.enabled ? "" : " " + this._t("common.disabled_tag")];
    let pill = null;
    let statusLine = null;
    if (ac && ac.paused) {
      pill = el("span", { class: "pill pause" }, this._t("home.paused"));
      statusLine = this._t("home.plan_paused_at", { step: ac.paused_at_step || ac.step, total: ac.total_steps });
    } else if (ac) {
      pill = el("span", { class: "pill run" }, this._t("zone.watering"));
      statusLine = this._t("plans.zone_of", { step: ac.step, total: ac.total_steps });
    }

    const planName = c.name || c.id;
    const btn = (cls, text, onClick) => el("button", { class: cls, "aria-label": this._named(text, planName), onClick }, text);
    const actions = [];
    if (!ac) {
      actions.push(btn("btn primary small", this._t("plans.run_now"), () => this._callService("run_cycle", { cycle_id: c.id })));
    } else {
      actions.push(ac.paused
        ? btn("btn primary small", this._t("cycle.resume"), () => this._callService("resume_cycle", { cycle_id: c.id }))
        : btn("btn small", this._t("cycle.pause"), () => this._callService("pause_cycle", { cycle_id: c.id })));
      actions.push(btn("btn danger small", this._t("common.stop"), () => this._callService("stop_cycle", { cycle_id: c.id })));
    }
    // One set of plan controls, labelled as plan controls (UX-014); turning the whole plan off is in Edit plan.
    actions.push(
      btn("btn small", this._t("plans.edit"), () => this._openCycleModal(c)),
      btn("btn danger small", this._t("plans.delete"), () => this._confirmDelete(this._t("cycles.delete_confirm", { name: c.name }), "remove_cycle", { cycle_id: c.id })),
    );

    const chain = el("div", { class: "chain" });
    steps.forEach((s, i) => {
      if (i) chain.appendChild(this._chainSep());
      chain.appendChild(el("span", {}, [this._valveName(s.entity_id), " (" + this._t("unit.min", { n: s.duration_min }) + ")"]));
    });

    // The plan (name, zones, its controls) on top; its watering times below as their own indented group with
    // their own words, so no two controls on the card look alike (UX-014).
    const planTitleId = uid("sw-plan");
    const timesTitleId = uid("sw-plan-times");
    const card = el("article", { class: "card", "aria-labelledby": planTitleId }, [
      el("div", { class: "admin-head" }, [
        el("div", { style: "min-width:0;" }, [
          el("div", { class: "name", id: planTitleId }, head),
          statusLine ? el("div", { class: "sub" }, statusLine) : null,
        ]),
        el("div", { class: "actions" }, [pill, ...actions]),
      ]),
    ]);
    const body = el("div", { class: "admin-body" });
    body.appendChild(chain);
    body.appendChild(el("div", { class: "sub" }, this._t("plans.summary", { steps: steps.length, min: totalMin })));
    const times = (st.schedules || []).filter(s => s.cycle_id === c.id);
    const group = el("section", { class: "times", "aria-labelledby": timesTitleId }, [
      el("h3", { class: "times-h", id: timesTitleId }, this._t("plans.times")),
    ]);
    times.forEach(s => group.appendChild(this._schedRow(s, false, c.name)));
    if (!times.length) group.appendChild(el("div", { class: "muted small" }, this._t("plans.no_times")));
    group.appendChild(el("div", {}, el("button", {
      class: "btn ghost",
      "aria-label": this._named(this._t("zones.add_time"), planName),
      onClick: () => this._openScheduleModal(null, { kind: "cycle", id: c.id }),
    }, this._t("zones.add_time"))));
    body.appendChild(group);
    card.appendChild(body);
    return card;
  }

  _openCycleModal(existing) {
    if (!this._state.valves.length) { this._toast(this._t("cycles.add_valve_first"), "error"); return; }

    let name = existing ? existing.name : "";
    let enabled = existing ? !!existing.enabled : true;
    let steps = existing ? JSON.parse(JSON.stringify(existing.steps || [])) : [];
    if (!steps.length) {
      const v = this._state.valves[0];
      steps.push({ entity_id: v.entity_id, duration_min: v.default_duration_min });
    }

    const nameInput = el("input", { type: "text", maxlength: "80", value: name, placeholder: this._t("cycles.name_ph"), "aria-required": "true" });
    const nameErr = fieldError("sw-plan-name-err");
    nameInput.addEventListener("input", () => { name = nameInput.value; if (name.trim()) setFieldError(nameErr, nameInput, ""); });

    const enabledField = this._switchField(this._t("common.enabled"), enabled, (on) => { enabled = on; });

    const stepsCap = uid("sw-steps-cap");
    const stepsWrap = el("div", { role: "group", "aria-labelledby": stepsCap });
    const stepsErr = fieldError("sw-plan-steps-err");
    const renderSteps = () => {
      stepsWrap.innerHTML = "";
      steps.forEach((s, idx) => {
        const sel = el("select", { "aria-label": this._t("sched.valve") });
        if (s.entity_id && !this._state.valves.some(v => v.entity_id === s.entity_id)) {
          const stale = el("option", { value: s.entity_id, style: "color:var(--sw-muted);font-style:italic;" }, `${this._t("cycles.missing")} \u2066${s.entity_id}\u2069`);
          stale.selected = true;
          sel.appendChild(stale);
        }
        this._state.valves.forEach(v => {
          const opt = el("option", { value: v.entity_id }, optLabel(v.label, v.entity_id));
          if (v.entity_id === s.entity_id) opt.selected = true;
          sel.appendChild(opt);
        });
        sel.addEventListener("change", () => { s.entity_id = sel.value; });

        const durInput = el("input", {
          type: "number", min: "1", max: "1440",
          value: String(s.duration_min), style: "width:70px;",
          "aria-label": this._t("sched.duration"),
        });
        durInput.addEventListener("input", () => { s.duration_min = parseInt(durInput.value, 10) || 1; });

        const row = el("div", {
          style: "display:grid;grid-template-columns:24px minmax(0,1fr) 80px auto auto;gap:6px;align-items:center;padding:4px 0;",
        }, [
          el("span", { class: "muted small" }, String(idx + 1)),
          sel,
          durInput,
          el("button", {
            class: "btn small",
            disabled: idx === 0,
            title: this._t("cycles.move_up"),
            "aria-label": this._t("cycles.move_up"),
            onClick: () => {
              [steps[idx - 1], steps[idx]] = [steps[idx], steps[idx - 1]];
              renderSteps();
            },
          }, "▲"),
          el("button", {
            class: "btn danger small",
            title: this._t("cycles.remove_step"),
            "aria-label": this._t("cycles.remove_step"),
            onClick: () => { steps.splice(idx, 1); renderSteps(); },
          }, "✕"),
        ]);
        stepsWrap.appendChild(row);
      });
      stepsWrap.appendChild(el("button", {
        class: "btn small",
        style: "margin-top:6px;",
        onClick: () => {
          const v = this._state.valves[0];
          steps.push({ entity_id: v.entity_id, duration_min: v.default_duration_min });
          setFieldError(stepsErr, stepsWrap, "");
          renderSteps();
        },
      }, this._t("cycles.add_step")));
    };
    renderSteps();

    const fields = [
      el("label", { class: "field" }, [el("span", {}, this._t("cycles.name")), nameInput, nameErr]),
      el("div", { class: "field" }, [el("span", { id: stepsCap }, this._t("cycles.steps")), stepsWrap, stepsErr]),
      enabledField,
    ];

    this._showModal(this._t(existing ? "cycles.edit_title" : "cycles.add_title"), fields, async () => {
      // Inline errors next to the field, focus on the first one, the toast repeats it (UX-005).
      const invalid = [];
      setFieldError(nameErr, nameInput, name.trim() ? "" : this._t("cycles.name_required"));
      if (!name.trim()) invalid.push([nameInput, this._t("cycles.name_required")]);
      setFieldError(stepsErr, stepsWrap, steps.length ? "" : this._t("cycles.one_step"));
      if (!steps.length) invalid.push([stepsWrap.querySelector("button:last-of-type") || stepsWrap, this._t("cycles.one_step")]);
      if (invalid.length) {
        invalid[0][0].focus();
        this._toast(invalid[0][1], "error");
        return false;
      }
      const payload = {
        name,
        enabled,
        steps: steps.map(s => ({
          entity_id: s.entity_id,
          duration_minutes: s.duration_min,
        })),
      };
      if (existing) {
        return await this._callService("update_cycle", { cycle_id: existing.id, ...payload });
      }
      return await this._callService("add_cycle", payload);
    });
  }

  _openScheduleModal(existing, preset) {
    const hasValves = this._state.valves.length > 0;
    const hasCycles = (this._state.cycles || []).length > 0;
    if (!hasValves && !hasCycles) { this._toast(this._t("sched.add_first"), "error"); return; }

    let targetKind;
    if (existing) targetKind = existing.cycle_id ? "cycle" : "valve";
    else if (preset) targetKind = preset.kind;
    else targetKind = hasValves ? "valve" : "cycle";
    const locked = !!(existing || preset);
    let valveEntity = existing && existing.valve_entity_id ? existing.valve_entity_id
      : (preset && preset.kind === "valve" ? preset.id : (hasValves ? this._state.valves[0].entity_id : ""));
    let cycleId = existing && existing.cycle_id ? existing.cycle_id
      : (preset && preset.kind === "cycle" ? preset.id : (hasCycles ? this._state.cycles[0].id : ""));
    const presetValve = targetKind === "valve" ? this._state.valves.find(v => v.entity_id === valveEntity) : null;
    let name = existing ? existing.name : "";
    let time = existing ? existing.time_hhmm : "06:00";
    let duration = existing ? existing.duration_min
      : (presetValve ? presetValve.default_duration_min : (this._state.options.default_duration || 10));
    let mask = existing && existing.repeat !== "interval" ? existing.days_mask : 127;
    let repeat = existing && existing.repeat === "interval" ? "interval" : "weekdays";
    let enabled = existing ? !!existing.enabled : true;
    let timeMode = existing && (existing.time_mode === "sunrise" || existing.time_mode === "sunset") ? existing.time_mode : "clock";
    const offset0 = existing ? parseInt(existing.sun_offset_min, 10) || 0 : 0;

    const targetSel = el("select", { disabled: locked });
    if (hasValves) targetSel.appendChild(el("option", { value: "valve" }, this._t("sched.single_valve")));
    if (hasCycles) targetSel.appendChild(el("option", { value: "cycle" }, this._t("sched.cycle_multi")));
    targetSel.value = targetKind;
    targetSel.addEventListener("change", () => { targetKind = targetSel.value; renderTargetField(); });

    const targetFieldHost = el("div");
    const valveSel = el("select", { disabled: locked });
    this._state.valves.forEach(v => {
      const opt = el("option", { value: v.entity_id }, optLabel(v.label, v.entity_id));
      if (v.entity_id === valveEntity) opt.selected = true;
      valveSel.appendChild(opt);
    });
    valveSel.addEventListener("change", () => { valveEntity = valveSel.value; });

    const cycleSel = el("select", { disabled: locked });
    (this._state.cycles || []).forEach(c => {
      const opt = el("option", { value: c.id }, `${c.name}`);
      if (c.id === cycleId) opt.selected = true;
      cycleSel.appendChild(opt);
    });
    cycleSel.addEventListener("change", () => { cycleId = cycleSel.value; });

    const durRow = el("div", { class: "field-row" });
    const timeInput = el("input", { type: "time", value: time });
    timeInput.addEventListener("input", () => { time = timeInput.value; });
    const timeField = el("label", { class: "field" }, [el("span", {}, this._t("sched.time")), timeInput]);
    const durInput = el("input", { type: "number", min: "1", max: "1440", value: String(duration) });
    const durErr = el("div", { class: "field-error", id: "sw-sched-duration-err", role: "alert", hidden: true });
    durInput.addEventListener("input", () => {
      duration = minutesValue(durInput.value);
      if (duration !== null) setErr(durErr, durInput, "");
    });
    const renderTargetField = () => {
      targetFieldHost.innerHTML = "";
      durRow.innerHTML = "";
      if (targetKind === "cycle") {
        targetFieldHost.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.cycle")), cycleSel]));
        durRow.appendChild(timeField);
      } else {
        targetFieldHost.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.valve")), valveSel]));
        durRow.appendChild(timeField);
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.duration")), durInput, durErr]));
      }
    };
    renderTargetField();

    const nameInput = el("input", { type: "text", maxlength: "80", value: name, placeholder: this._t("common.optional") });
    nameInput.addEventListener("input", () => { name = nameInput.value; });

    const enabledField = this._switchField(this._t("common.enabled"), enabled, (on) => { enabled = on; });

    // Inline validation messages (the server validates the same rules).
    const errNode = (id) => el("div", { class: "field-error", id, role: "alert", hidden: true });
    const setErr = (node, input, msg) => {
      node.textContent = msg || "";
      node.hidden = !msg;
      if (input) {
        if (msg) { input.setAttribute("aria-invalid", "true"); input.setAttribute("aria-describedby", node.id); }
        else { input.removeAttribute("aria-invalid"); input.removeAttribute("aria-describedby"); }
      }
    };
    const daysErr = errNode("sw-sched-days-err");
    const intervalErr = errNode("sw-sched-interval-err");
    const startErr = errNode("sw-sched-start-err");
    const offsetErr = errNode("sw-sched-offset-err");

    // Start at a clock time, or at sunrise / sunset plus or minus some minutes (#59).
    const modeSel = el("select", {});
    modeSel.appendChild(el("option", { value: "clock" }, this._t("sched.mode_clock")));
    modeSel.appendChild(el("option", { value: "sunrise" }, this._t("sched.mode_sunrise")));
    modeSel.appendChild(el("option", { value: "sunset" }, this._t("sched.mode_sunset")));
    modeSel.value = timeMode;
    const offsetInput = el("input", {
      type: "number", min: "0", max: String(SUN_OFFSET_MAX), step: "1", inputmode: "numeric",
      value: String(Math.abs(offset0)),
    });
    const dirSel = el("select", {});
    dirSel.appendChild(el("option", { value: "before" }, this._t("sched.offset_before")));
    dirSel.appendChild(el("option", { value: "after" }, this._t("sched.offset_after")));
    dirSel.value = offset0 < 0 ? "before" : "after";
    const offsetValue = () => {
      const raw = String(offsetInput.value).trim();
      const n = Number(raw);
      return raw !== "" && Number.isInteger(n) && n >= 0 && n <= SUN_OFFSET_MAX ? n : null;
    };
    const signedOffset = (n) => (dirSel.value === "before" ? -n : n);
    // The next start times come from the server: they need the Home Assistant location.
    const sunPreview = el("div", { class: "muted small", "aria-live": "polite", style: "margin:-4px 0 12px;" });
    let sunSeq = 0;
    let sunTimer = null;
    const updateSunPreview = () => {
      clearTimeout(sunTimer);
      const seq = ++sunSeq;
      sunPreview.innerHTML = "";
      const off = offsetValue();
      if (timeMode === "clock" || off === null) return;
      const msg = { type: "schedule_wizard/preview_schedule", time_mode: timeMode, sun_offset_minutes: signedOffset(off), count: 3 };
      if (repeat === "interval") {
        const n = intervalValue();
        const start = startValue();
        if (n === null || !start) return;
        Object.assign(msg, { repeat: "interval", interval_days: n, start_date: start });
      } else {
        if (!mask) return;
        Object.assign(msg, { repeat: "weekdays", days_mask: mask });
      }
      sunTimer = setTimeout(() => {
        this._hass.callWS(msg).then((res) => {
          if (seq !== sunSeq) return;
          const list = (res && res.next) || [];
          if (!list.length) { sunPreview.textContent = this._t("sched.sun_none"); return; }
          const text = list.map(ts => this._fmtDT(ts, { weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit" })).join(" · ");
          sunPreview.append(...this._tn("sched.next_runs", { list: text }));
        }).catch(() => { if (seq === sunSeq) sunPreview.innerHTML = ""; });
      }, 250);
    };
    const startField = el("label", { class: "field" }, [el("span", {}, this._t("sched.start_at")), modeSel]);
    const sunRow = el("div", {}, [
      el("label", { class: "field" }, [
        el("span", {}, this._t("sched.offset_min")),
        el("div", { style: "display:flex;gap:8px;" }, [offsetInput, dirSel]),
        offsetErr,
      ]),
      el("p", { class: "muted small", style: "margin:-6px 0 8px;" }, this._t("sched.sun_hint")),
      sunPreview,
    ]);
    const syncMode = () => {
      timeField.hidden = timeMode !== "clock";
      sunRow.hidden = timeMode === "clock";
      updateFirstRun();
    };
    modeSel.addEventListener("change", () => { timeMode = modeSel.value; setErr(offsetErr, offsetInput, ""); syncMode(); });
    offsetInput.addEventListener("input", () => { if (offsetValue() !== null) setErr(offsetErr, offsetInput, ""); updateSunPreview(); });
    dirSel.addEventListener("change", updateSunPreview);
    // Service fields for the start time, or null after showing an inline error.
    const timeFields = () => {
      setErr(offsetErr, offsetInput, "");
      if (timeMode === "clock") return { time, time_mode: "clock" };
      const off = offsetValue();
      if (off === null) { setErr(offsetErr, offsetInput, this._t("sched.err_offset")); offsetInput.focus(); return null; }
      const out = { time_mode: timeMode, sun_offset_minutes: signedOffset(off) };
      if (/^\d{2}:\d{2}$/.test(String(time))) out.time = time;
      return out;
    };

    const daysCap = uid("sw-days-cap");
    const days = el("div", { class: "days", role: "group", "aria-labelledby": daysCap, "aria-describedby": daysErr.id });
    this._weekOrder().forEach((i) => {
      const tog = el("button", {
        type: "button",
        class: "day-chip",
        "aria-pressed": (mask & DAY_BITS[i]) ? "true" : "false",
        title: I18N.weekdayLong(i, this._lang, this._fo()),
      }, I18N.weekdayShort(i, this._lang, this._fo()));
      tog.addEventListener("click", () => {
        mask ^= DAY_BITS[i];
        tog.setAttribute("aria-pressed", (mask & DAY_BITS[i]) ? "true" : "false");
        if (mask) setErr(daysErr, null, "");
        updateSunPreview();
      });
      days.appendChild(tog);
    });

    const repeatSel = el("select", {});
    repeatSel.appendChild(el("option", { value: "weekdays" }, this._t("sched.repeat_weekdays")));
    repeatSel.appendChild(el("option", { value: "interval" }, this._t("sched.repeat_interval")));
    repeatSel.value = repeat;
    const intervalInput = el("input", {
      type: "number", min: String(INTERVAL_MIN), max: String(INTERVAL_MAX), step: "1", inputmode: "numeric",
      value: String(existing && existing.repeat === "interval" ? existing.interval_days : INTERVAL_MIN),
    });
    const startInput = el("input", {
      type: "date",
      value: existing && existing.repeat === "interval" && existing.start_date ? existing.start_date : todayKey(this._hass),
    });
    const intervalValue = () => {
      const raw = String(intervalInput.value).trim();
      const n = Number(raw);
      return raw !== "" && Number.isInteger(n) && n >= INTERVAL_MIN && n <= INTERVAL_MAX ? n : null;
    };
    const startValue = () => (/^\d{4}-\d{2}-\d{2}$/.test(startInput.value) ? startInput.value : null);
    // Live "First run: <weekday date time>, then every N days" under the fields (#30).
    const firstRunLine = el("div", { class: "muted small", "aria-live": "polite", style: "margin:-4px 0 12px;" });
    const updateFirstRun = () => {
      firstRunLine.innerHTML = "";
      updateSunPreview();
      if (timeMode !== "clock") return;
      const n = intervalValue();
      const start = startValue();
      const hhmm = /^\d{2}:\d{2}$/.test(String(timeInput.value)) ? timeInput.value : null;
      if (n === null || !start || !hhmm) return;
      firstRunLine.append(...this._firstRunNodes(n, start, hhmm));
    };
    intervalInput.addEventListener("input", () => { if (intervalValue() !== null) setErr(intervalErr, intervalInput, ""); updateFirstRun(); });
    startInput.addEventListener("input", () => { if (startValue()) setErr(startErr, startInput, ""); updateFirstRun(); });
    timeInput.addEventListener("input", updateFirstRun);
    const daysField = el("div", { class: "field" }, [el("span", { id: daysCap }, this._t("sched.days")), days, daysErr]);
    const intervalRow = el("div", {}, [
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, this._t("sched.interval_days")), intervalInput, intervalErr]),
        el("label", { class: "field" }, [el("span", {}, this._t("sched.start_date")), startInput, startErr]),
      ]),
      firstRunLine,
    ]);
    const intervalErrText = () => this._t("sched.err_interval", { option: this._t("sched.repeat_weekdays") });
    const syncRepeat = () => {
      daysField.hidden = repeat !== "weekdays";
      intervalRow.hidden = repeat !== "interval";
      updateFirstRun();
    };
    repeatSel.addEventListener("change", () => { repeat = repeatSel.value; syncRepeat(); });
    syncRepeat();
    syncMode();

    // Service fields for the repeat rule, or null after showing inline errors.
    const repeatFields = () => {
      [[daysErr, null], [intervalErr, intervalInput], [startErr, startInput]].forEach(([n, i]) => setErr(n, i, ""));
      if (repeat === "weekdays") {
        if (!mask) { setErr(daysErr, null, this._t("sched.pick_day")); return null; }
        return { days: daysFromMaskNames(mask) };
      }
      const n = intervalValue();
      const start = startValue();
      if (n === null) setErr(intervalErr, intervalInput, intervalErrText());
      if (!start) setErr(startErr, startInput, this._t("sched.err_start_date"));
      if (n === null) { intervalInput.focus(); return null; }
      if (!start) { startInput.focus(); return null; }
      return { every_n_days: n, start_date: start };
    };
    // Server-side validation errors land next to their field.
    const submit = async (service, payload) => {
      try {
        await this._hass.callService("schedule_wizard", service, payload);
      } catch (e) {
        const msg = String((e && (e.message || e.code)) || e);
        if (/sun_offset/.test(msg)) setErr(offsetErr, offsetInput, this._t("sched.err_offset"));
        else if (/every_n_days/.test(msg)) setErr(intervalErr, intervalInput, intervalErrText());
        else if (/start_date/.test(msg)) setErr(startErr, startInput, this._t("sched.err_start_date"));
        else if (/at least one day/.test(msg)) setErr(daysErr, null, this._t("sched.pick_day"));
        else this._toast(msg, "error");
        return false;
      }
      this._toast(this._t("common.done"), "ok");
      this._refresh();
      return true;
    };

    const OPERATORS = ["above", "below", "equals", "not_equals"].map(op => [op, this._t("op." + op)]);
    const conditions = (existing && Array.isArray(existing.conditions) ? existing.conditions : []).map(c => ({
      entity_id: c.entity_id || "",
      attribute: c.attribute || "",
      operator: c.operator || "equals",
      value: c.value === null || c.value === undefined ? "" : String(c.value),
    }));
    const condCap = uid("sw-cond-cap");
    const condWrap = el("div", { role: "group", "aria-labelledby": condCap });
    const renderConditions = () => {
      condWrap.innerHTML = "";
      conditions.forEach((c, idx) => {
        // Each field is named, with its row number, beyond its placeholder (BUG-007).
        const n = idx + 1;
        const named = (key) => this._t("sched.cond_field", { field: this._t(key), n });
        const entInput = el("input", { type: "text", dir: "ltr", placeholder: "sensor.example", value: c.entity_id, "aria-label": named("sched.cond_entity") });
        entInput.addEventListener("input", () => { c.entity_id = entInput.value; });
        const attrInput = el("input", { type: "text", maxlength: "255", placeholder: this._t("sched.attr_ph"), value: c.attribute, "aria-label": named("common.attribute_optional") });
        attrInput.addEventListener("input", () => { c.attribute = attrInput.value; });
        const opSel = el("select", { "aria-label": named("sched.cond_operator") });
        OPERATORS.forEach(([val, lbl]) => {
          const opt = el("option", { value: val }, lbl);
          if (val === c.operator) opt.selected = true;
          opSel.appendChild(opt);
        });
        opSel.addEventListener("change", () => { c.operator = opSel.value; });
        const valInput = el("input", { type: "text", maxlength: "255", placeholder: this._t("sched.value_ph"), value: c.value, "aria-label": named("sched.cond_value") });
        valInput.addEventListener("input", () => { c.value = valInput.value; });
        condWrap.appendChild(el("div", { class: "cond-row" }, [
          entInput, attrInput, opSel, valInput,
          el("button", {
            class: "btn danger small",
            type: "button",
            title: this._t("sched.remove_condition_n", { n }),
            "aria-label": this._t("sched.remove_condition_n", { n }),
            onClick: () => { conditions.splice(idx, 1); renderConditions(); },
          }, "✕"),
        ]));
      });
      condWrap.appendChild(el("button", {
        class: "btn small",
        type: "button",
        style: "margin-top:6px;",
        disabled: conditions.length >= 10,
        onClick: () => {
          if (conditions.length >= 10) return;
          conditions.push({ entity_id: "", attribute: "", operator: "above", value: "" });
          renderConditions();
        },
      }, this._t("sched.add_condition")));
    };
    renderConditions();
    const collectConditions = () => conditions
      .filter(c => c.entity_id.trim())
      .map(c => ({
        entity_id: c.entity_id.trim(),
        attribute: c.attribute.trim(),
        operator: c.operator,
        value: c.value.trim(),
      }));

    const fields = [
      el("label", { class: "field", style: locked ? "display:none;" : null }, [el("span", {}, this._t("sched.target")), targetSel]),
      targetFieldHost,
      el("label", { class: "field" }, [el("span", {}, this._t("sched.repeat")), repeatSel]),
      daysField,
      intervalRow,
      startField,
      sunRow,
      durRow,
      el("label", { class: "field" }, [el("span", {}, this._t("common.name")), nameInput]),
      el("div", { class: "field" }, [el("span", { id: condCap }, this._t("sched.conditions")), condWrap]),
      enabledField,
    ];

    this._showModal(this._t(existing ? "sched.edit_title" : "sched.add_title"), fields, async () => {
      const rep = repeatFields();
      if (!rep) return false;
      const timing = timeFields();
      if (!timing) return false;
      if (targetKind === "valve" && (minutesValue(durInput.value) === null || durInput.validity.badInput)) {
        setErr(durErr, durInput, this._t("valves.err_duration"));
        durInput.focus();
        return false;
      }
      const conds = collectConditions();
      if (existing) {
        return await submit("update_schedule", {
          schedule_id: existing.id,
          name,
          ...timing,
          duration_minutes: targetKind === "valve" ? duration : 1,
          ...rep,
          enabled,
          conditions: conds,
        });
      }
      const base = {
        ...timing,
        ...rep,
        name,
        enabled,
        conditions: conds,
      };
      if (targetKind === "cycle") {
        return await submit("add_schedule", { ...base, cycle_id: cycleId, duration_minutes: 1 });
      }
      return await submit("add_schedule", { ...base, valve_entity_id: valveEntity, duration_minutes: duration });
    });
  }

  // "First run: Wed, Oct 3 06:00, then every 2 days" for every N days from a start date at a clock time (#30).
  _firstRunNodes(n, start, hhmm) {
    const today = dayNum(todayKey(this._hass));
    const passed = hhmm <= nowHHMM(this._hass);
    let first = dayNum(start);
    let key = "sched.first_run";
    if (first < today) {
      key = "sched.next_run_line";
      first += Math.ceil((today - first) / n) * n;
      if (first === today && passed) first += n;
    } else if (first === today && passed) {
      key = "sched.first_run_passed";
      first += n;
    }
    const [fy, fm, fd] = dayFromNum(first).split("-").map(Number);
    const ts = Date.UTC(fy, fm - 1, fd, 12) / 1000;
    const clock = this._fmtClock(hhmm);
    const when = el("span", {}, [
      I18N.fmtDate(ts, this._lang, { hass: this._hass, timeZone: "UTC", weekday: "short", month: "short", day: "numeric" }),
      " ", clock,
    ]);
    return this._tn(key, { when, n, time: clock });
  }

  // ---------- Setup wizard ----------

  _openWizard() {
    const st = this._state;
    const t = this._t;
    const opts = st.options || {};
    const registered = new Map((st.valves || []).map(v => [v.entity_id, v]));
    const ents = st.controllable || [];
    const friendly = (id) => { const e = ents.find(x => x.entity_id === id); return e ? e.friendly_name : id; };
    const isNew = (id) => !registered.has(id);
    const wz = {
      idx: 0, picked: [], names: {}, mins: {}, mask: DAY_BITS[0] | DAY_BITS[2] | DAY_BITS[4],
      // Every N days, sunrise / sunset start and rain skip in the first-run flow too (UX-009).
      repeat: "weekdays", interval: String(INTERVAL_MIN), start: todayKey(this._hass),
      timeMode: "clock", offset: "0", offsetDir: "before",
      time: "06:00", mode: "sequence", plan: "", planTouched: false, search: "", saving: false,
    };
    const nameOf = (id) => (isNew(id) ? (wz.names[id] ?? friendly(id)) : registered.get(id).label);
    const minOf = (id) => wz.mins[id] ?? (registered.has(id) ? registered.get(id).default_duration_min : 10);
    const evening = () => (wz.timeMode === "clock" ? (parseInt(wz.time, 10) || 0) >= 12 : wz.timeMode === "sunset");
    const defaultPlan = () => t(evening() ? "wiz.plan_evening" : "wiz.plan_morning");
    const planName = () => (wz.planTouched ? wz.plan : defaultPlan()).trim();
    const intervalValue = () => {
      const n = Number(String(wz.interval).trim());
      return String(wz.interval).trim() !== "" && Number.isInteger(n) && n >= INTERVAL_MIN && n <= INTERVAL_MAX ? n : null;
    };
    const startValue = () => (/^\d{4}-\d{2}-\d{2}$/.test(wz.start) ? wz.start : null);
    const offsetValue = () => {
      const n = Number(String(wz.offset).trim());
      return String(wz.offset).trim() !== "" && Number.isInteger(n) && n >= 0 && n <= SUN_OFFSET_MAX ? n : null;
    };
    const signedOffset = () => (wz.offsetDir === "before" ? -1 : 1) * (offsetValue() || 0);
    // The same four steps whatever is picked (UX-018: the count used to change from 3 to 5 after step 1).
    // New zones are named on the first step; a single zone only names the plan on the third.
    const stepKeys = () => ["pick", "when", "plan", "check"];
    const titleOf = (key) => ({
      pick: "wiz.t_pick", when: "wiz.t_when", plan: wz.picked.length > 1 ? "wiz.t_order" : "wiz.t_plan_name", check: "wiz.t_check",
    })[key];
    const valid = (key) => {
      if (key === "pick") return wz.picked.length > 0 && wz.picked.filter(isNew).every(id => String(nameOf(id)).trim());
      if (key === "when") {
        const repeatOk = wz.repeat === "weekdays" ? !!(wz.mask & 127) : intervalValue() !== null && !!startValue();
        const timeOk = wz.timeMode === "clock" ? /^\d{2}:\d{2}$/.test(wz.time) : offsetValue() !== null;
        return repeatOk && timeOk;
      }
      return !!planName();
    };
    // The stored-schedule shape, for the summary sentence.
    const schedShape = () => ({
      repeat: wz.repeat === "interval" ? "interval" : "weekdays", days_mask: wz.mask,
      interval_days: intervalValue(), start_date: startValue(),
      time_hhmm: wz.time, time_mode: wz.timeMode, sun_offset_min: signedOffset(),
    });

    const modal = el("div", { class: "modal wizard", role: "dialog", "aria-modal": "true", "aria-labelledby": "sw-wiz-title" });
    const head = el("div", { class: "wiz-head" });
    const body = el("div", { class: "wiz-body" });
    const foot = el("div", { class: "wiz-foot" });
    modal.append(head, body, foot);
    const overlay = el("div", { class: "modal-overlay" }, modal);
    let close = () => {};

    let nextBtn = null;
    const refreshNext = () => { if (nextBtn) nextBtn.disabled = wz.saving || !valid(stepKeys()[wz.idx]); };
    let rainPicker = null;

    const drawHead = () => {
      const keys = stepKeys();
      head.innerHTML = "";
      head.appendChild(el("div", { class: "wiz-steps", "aria-hidden": "true" }, keys.map((_, i) => el("i", { class: i <= wz.idx ? "on" : "" }))));
      head.appendChild(el("div", { class: "muted small" }, t("wiz.step_of", { n: wz.idx + 1, total: keys.length })));
      head.appendChild(el("h3", { id: "sw-wiz-title", tabindex: "-1" }, t(titleOf(keys[wz.idx]))));
    };

    const minutesStepper = (id) => {
      const val = el("span", { class: "stepper-val", "aria-live": "polite" }, t("unit.min", { n: minOf(id) }));
      const change = (dir) => { wz.mins[id] = stepMinutes(minOf(id), dir); val.textContent = t("unit.min", { n: wz.mins[id] }); };
      return el("span", { class: "stepper" }, [
        el("button", { type: "button", "aria-label": this._named(t("zone.less"), nameOf(id)), title: t("zone.less"), onClick: () => change(-1) }, "−"),
        val,
        el("button", { type: "button", "aria-label": this._named(t("zone.more"), nameOf(id)), title: t("zone.more"), onClick: () => change(1) }, "+"),
      ]);
    };

    // Two or three exclusive choices as pressed buttons, named by their caption.
    const choiceRow = (caption, options, current, onPick) => {
      const capId = uid("sw-wiz-cap");
      const row = el("div", { class: "seg", role: "group", "aria-labelledby": capId });
      options.forEach(([value, label]) => {
        const b = el("button", { type: "button", class: "btn small", "aria-pressed": value === current ? "true" : "false" }, label);
        b.addEventListener("click", () => {
          row.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
          onPick(value);
        });
        row.appendChild(b);
      });
      return el("div", { class: "field", style: "margin:0;" }, [el("span", { id: capId }, caption), row]);
    };

    const planNameField = () => {
      const input = el("input", { type: "text", maxlength: "80", value: planName(), placeholder: t("cycles.name_ph") });
      input.addEventListener("input", () => { wz.plan = input.value; wz.planTouched = true; refreshNext(); });
      return el("label", { class: "field", style: "margin:0;" }, [el("span", {}, t("wiz.plan_name")), input]);
    };

    const bodyPick = () => {
      body.appendChild(el("p", { class: "muted" }, t("wiz.pick_hint")));
      const search = el("input", { type: "search", value: wz.search, placeholder: t("valves.search_ph"), "aria-label": t("valves.search") });
      const listHost = el("div", { class: "wiz-list" });
      const checkRow = (e) => {
        const id = e.entity_id;
        const cb = el("input", { type: "checkbox" });
        cb.checked = wz.picked.includes(id);
        const reg = registered.get(id);
        // A new zone is named right under its tick box (UX-018: no separate step that comes and goes).
        let nameField = null;
        if (!reg) {
          const errId = uid("sw-wiz-name-err");
          const err = fieldError(errId);
          const input = el("input", {
            type: "text", maxlength: "80", value: nameOf(id), placeholder: t("valves.label_ph"),
            "aria-label": this._named(t("wiz.zone_name"), friendly(id)),
          });
          input.addEventListener("input", () => {
            wz.names[id] = input.value;
            setFieldError(err, input, input.value.trim() ? "" : t("valves.label_required"));
            refreshNext();
          });
          nameField = el("label", { class: "field", style: "margin:4px 0 0;padding-inline-start:42px;", hidden: !cb.checked }, [
            el("span", {}, t("wiz.zone_name")), input, err,
          ]);
        }
        cb.addEventListener("change", () => {
          if (cb.checked) { if (!wz.picked.includes(id)) wz.picked.push(id); }
          else wz.picked = wz.picked.filter(x => x !== id);
          if (nameField) nameField.hidden = !cb.checked;
          drawHead();
          refreshNext();
        });
        return el("div", {}, [
          el("label", { class: "check" }, [
            cb,
            el("span", { style: "min-width:0;" }, [
              el("div", {}, iso(reg ? reg.label : e.friendly_name)),
              el("div", { class: "sub" }, ltr(id)),
            ]),
          ]),
          nameField,
        ]);
      };
      const renderList = () => {
        listHost.innerHTML = "";
        const q = wz.search.trim().toLowerCase();
        const match = (e) => !q || e.entity_id.toLowerCase().includes(q) || String(e.friendly_name).toLowerCase().includes(q) ||
          (registered.has(e.entity_id) && String(registered.get(e.entity_id).label).toLowerCase().includes(q));
        const fresh = ents.filter(e => isNew(e.entity_id) && match(e));
        const known = ents.filter(e => !isNew(e.entity_id) && match(e));
        if (!ents.length) { listHost.appendChild(el("div", { class: "empty" }, t("wiz.no_entities"))); return; }
        if (!fresh.length && !known.length) { listHost.appendChild(el("div", { class: "empty" }, t("valves.no_matches"))); return; }
        fresh.forEach(e => listHost.appendChild(checkRow(e)));
        if (known.length) {
          listHost.appendChild(el("div", { class: "sub", style: "margin-top:6px;font-weight:600;" }, t("wiz.already_added")));
          known.forEach(e => listHost.appendChild(checkRow(e)));
        }
      };
      search.addEventListener("input", () => { wz.search = search.value; renderList(); });
      renderList();
      body.append(search, listHost);
    };

    const bodyWhen = () => {
      const daysCap = uid("sw-wiz-days");
      const minsCap = uid("sw-wiz-mins");
      const days = el("div", { class: "days", role: "group", "aria-labelledby": daysCap });
      // In the order the user's week runs (UX-017).
      this._weekOrder().forEach((i) => {
        const chip = el("button", {
          type: "button", class: "day-chip",
          "aria-pressed": (wz.mask & DAY_BITS[i]) ? "true" : "false",
          title: I18N.weekdayLong(i, this._lang, this._fo()),
        }, I18N.weekdayShort(i, this._lang, this._fo()));
        chip.addEventListener("click", () => {
          wz.mask ^= DAY_BITS[i];
          chip.setAttribute("aria-pressed", (wz.mask & DAY_BITS[i]) ? "true" : "false");
          setFieldError(daysErr, null, wz.mask & 127 ? "" : t("sched.pick_day"));
          refreshNext();
        });
        days.appendChild(chip);
      });
      const daysErr = fieldError(uid("sw-wiz-days-err"));
      days.setAttribute("aria-describedby", daysErr.id);
      const daysField = el("div", { class: "field", style: "margin:0;" }, [el("span", { id: daysCap }, t("wiz.which_days")), days, daysErr]);

      // Every N days from a start date, with the "First run: ..." line (#30).
      const intervalErr = fieldError(uid("sw-wiz-interval-err"));
      const startErr = fieldError(uid("sw-wiz-start-err"));
      const intervalInput = el("input", {
        type: "number", min: String(INTERVAL_MIN), max: String(INTERVAL_MAX), step: "1", inputmode: "numeric", value: wz.interval,
      });
      const startInput = el("input", { type: "date", value: wz.start });
      const firstRun = el("div", { class: "muted small", "aria-live": "polite" });
      const updateFirstRun = () => {
        firstRun.innerHTML = "";
        const n = intervalValue();
        const start = startValue();
        if (wz.repeat !== "interval" || n === null || !start || wz.timeMode !== "clock" || !/^\d{2}:\d{2}$/.test(wz.time)) return;
        firstRun.append(...this._firstRunNodes(n, start, wz.time));
      };
      intervalInput.addEventListener("input", () => {
        wz.interval = intervalInput.value;
        setFieldError(intervalErr, intervalInput, intervalValue() === null ? t("sched.err_interval", { option: t("sched.repeat_weekdays") }) : "");
        updateFirstRun(); updatePreview(); refreshNext();
      });
      startInput.addEventListener("input", () => {
        wz.start = startInput.value;
        setFieldError(startErr, startInput, startValue() ? "" : t("sched.err_start_date"));
        updateFirstRun(); updatePreview(); refreshNext();
      });
      const intervalRow = el("div", {}, [
        el("div", { class: "field-row" }, [
          el("label", { class: "field", style: "margin:0;" }, [el("span", {}, t("sched.interval_days")), intervalInput, intervalErr]),
          el("label", { class: "field", style: "margin:0;" }, [el("span", {}, t("sched.start_date")), startInput, startErr]),
        ]),
        firstRun,
      ]);

      // A clock time, or sunrise / sunset with minutes before or after (#59).
      const timeInput = el("input", { type: "time", value: wz.time, required: true });
      timeInput.addEventListener("input", () => { wz.time = timeInput.value; updateFirstRun(); refreshNext(); });
      const timeField = el("label", { class: "field", style: "margin:0;" }, [el("span", {}, t("wiz.start_time")), timeInput]);
      const offsetErr = fieldError(uid("sw-wiz-offset-err"));
      const offsetInput = el("input", {
        type: "number", min: "0", max: String(SUN_OFFSET_MAX), step: "1", inputmode: "numeric", value: wz.offset,
        "aria-label": t("sched.offset_min"),
      });
      const dirSel = el("select", { "aria-label": t("sched.offset_min") });
      dirSel.appendChild(el("option", { value: "before" }, t("sched.offset_before")));
      dirSel.appendChild(el("option", { value: "after" }, t("sched.offset_after")));
      dirSel.value = wz.offsetDir;
      const preview = el("div", { class: "muted small", "aria-live": "polite" });
      let seq = 0;
      let timer = null;
      const updatePreview = () => {
        clearTimeout(timer);
        const mine = ++seq;
        preview.innerHTML = "";
        if (wz.timeMode === "clock" || offsetValue() === null) return;
        const msg = { type: "schedule_wizard/preview_schedule", time_mode: wz.timeMode, sun_offset_minutes: signedOffset(), count: 3 };
        if (wz.repeat === "interval") {
          if (intervalValue() === null || !startValue()) return;
          Object.assign(msg, { repeat: "interval", interval_days: intervalValue(), start_date: startValue() });
        } else {
          if (!(wz.mask & 127)) return;
          Object.assign(msg, { repeat: "weekdays", days_mask: wz.mask });
        }
        timer = setTimeout(() => {
          this._hass.callWS(msg).then((res) => {
            if (mine !== seq) return;
            const list = (res && res.next) || [];
            if (!list.length) { preview.textContent = t("sched.sun_none"); return; }
            const text = list.map(ts => this._fmtDT(ts, { weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit" })).join(" · ");
            preview.append(...this._tn("sched.next_runs", { list: text }));
          }).catch(() => { if (mine === seq) preview.innerHTML = ""; });
        }, 250);
      };
      offsetInput.addEventListener("input", () => {
        wz.offset = offsetInput.value;
        setFieldError(offsetErr, offsetInput, offsetValue() === null ? t("sched.err_offset") : "");
        updatePreview(); refreshNext();
      });
      dirSel.addEventListener("change", () => { wz.offsetDir = dirSel.value; updatePreview(); });
      const sunRow = el("div", {}, [
        el("div", { class: "field", style: "margin:0;" }, [
          el("span", {}, t("sched.offset_min")),
          el("div", { style: "display:flex;gap:8px;" }, [offsetInput, dirSel]),
          offsetErr,
        ]),
        el("p", { class: "muted small", style: "margin:4px 0;" }, t("sched.sun_hint")),
        preview,
      ]);

      const sync = () => {
        daysField.hidden = wz.repeat !== "weekdays";
        intervalRow.hidden = wz.repeat !== "interval";
        timeField.hidden = wz.timeMode !== "clock";
        sunRow.hidden = wz.timeMode === "clock";
        updateFirstRun();
        updatePreview();
        refreshNext();
      };
      const repeatRow = choiceRow(t("sched.repeat"), [
        ["weekdays", t("sched.repeat_weekdays")], ["interval", t("sched.repeat_interval")],
      ], wz.repeat, (v) => { wz.repeat = v; sync(); });
      const modeRow = choiceRow(t("sched.start_at"), [
        ["clock", t("sched.mode_clock")], ["sunrise", t("sched.mode_sunrise")], ["sunset", t("sched.mode_sunset")],
      ], wz.timeMode, (v) => { wz.timeMode = v; sync(); });

      const mins = el("div", { class: "list", role: "group", "aria-labelledby": minsCap });
      wz.picked.forEach(id => mins.appendChild(el("div", { class: "zmin" }, [iso(nameOf(id)), minutesStepper(id)])));
      body.append(
        repeatRow, daysField, intervalRow,
        modeRow, timeField, sunRow,
        el("div", { class: "field", style: "margin:0;" }, [el("span", { id: minsCap }, t("wiz.minutes_per_zone")), mins]),
      );
      sync();
    };

    const bodyPlan = () => {
      if (wz.picked.length < 2) {
        body.append(el("p", { class: "muted" }, t("wiz.plan_name_hint")), planNameField());
        return;
      }
      const choice = el("div", { class: "choice" });
      const opt = (mode, titleKey, hintKey) => {
        const b = el("button", { type: "button", "aria-pressed": wz.mode === mode ? "true" : "false" }, [
          el("strong", {}, t(titleKey)), el("small", {}, t(hintKey)),
        ]);
        b.addEventListener("click", () => {
          wz.mode = mode;
          choice.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
        });
        return b;
      };
      choice.append(
        opt("sequence", "wiz.one_at_a_time", "wiz.one_at_a_time_hint"),
        opt("together", "wiz.together", "wiz.together_hint"),
      );
      body.append(choice, planNameField());
    };

    const bodyCheck = () => {
      const ids = wz.picked;
      const seq = ids.length > 1 && wz.mode === "sequence";
      const total = ids.length === 1 ? minOf(ids[0])
        : seq ? ids.reduce((a, id) => a + minOf(id), 0)
          : Math.max(...ids.map(minOf));
      const zones = el("div", { class: "chain" });
      ids.forEach((id, i) => {
        if (i) zones.appendChild(seq ? this._chainSep() : el("span", { class: "sep", "aria-hidden": "true" }, "+"));
        zones.appendChild(el("span", {}, [iso(nameOf(id)), " (" + t("unit.min", { n: minOf(id) }) + ")"]));
      });
      const summary = el("div", { class: "summary" }, [
        el("strong", {}, iso(planName())),
        el("span", {}, this._whenNodes(schedShape())),
        zones,
        el("span", { class: "muted" }, t(ids.length > 1 ? (seq ? "wiz.mode_sequence" : "wiz.mode_together") : "wiz.mode_single")),
        el("span", { class: "muted" }, t("wiz.total", { n: total })),
      ]);
      if (opts.rain_entity) summary.appendChild(el("span", { class: "muted" }, t("wiz.rain_note")));
      body.appendChild(summary);
      // Rain skip in the first-run flow (UX-009): the same picker and check as Settings.
      if (!opts.rain_entity) {
        if (!rainPicker) {
          rainPicker = this._rainPicker("", () => rainRules(opts.rain_skip_states ?? DEFAULT_RAIN_STATES, opts.rain_attribute, opts.rain_threshold),
            t("wiz.rain_q"));
        }
        body.append(
          rainPicker.node,
          el("p", { class: "muted small", style: "margin:-6px 0 0;" }, t("wiz.rain_later")),
        );
      }
    };

    const save = async () => {
      wz.saving = true;
      refreshNext();
      nextBtn.textContent = t("wiz.saving");
      const ids = wz.picked.slice();
      const name = planName();
      const when = {
        ...(wz.repeat === "interval"
          ? { every_n_days: intervalValue(), start_date: startValue() }
          : { days: daysFromMaskNames(wz.mask) }),
        ...(wz.timeMode === "clock"
          ? { time: wz.time }
          : { time: /^\d{2}:\d{2}$/.test(wz.time) ? wz.time : "06:00", time_mode: wz.timeMode, sun_offset_minutes: signedOffset() }),
      };
      const rain = rainPicker ? rainPicker.value() : "";
      const step = async (label, fn) => {
        try { return await fn(); } catch (e) { throw { label, error: e }; }
      };
      const svc = (service, data) => this._hass.callService("schedule_wizard", service, data);
      try {
        // First: the rain source is checked by the server and saving it twice does no harm.
        if (rain) {
          await step(t("wiz.fail_rain"), () => this._hass.callWS({ type: "schedule_wizard/update_options", rain_entity: rain }));
        }
        for (const id of ids) {
          if (!isNew(id)) continue;
          await step(t("wiz.fail_zone", { zone: nameOf(id) }), () => svc("add_valve", {
            entity_id: id, label: String(nameOf(id)).trim(), default_duration_minutes: minOf(id), enabled: true,
          }));
        }
        if (ids.length === 1) {
          await step(t("wiz.fail_schedule"), () => svc("add_schedule", {
            valve_entity_id: ids[0], ...when, duration_minutes: minOf(ids[0]), name, enabled: true,
          }));
        } else if (wz.mode === "sequence") {
          const res = await step(t("wiz.fail_plan"), () => this._hass.callWS({
            type: "call_service",
            domain: "schedule_wizard",
            service: "add_cycle",
            service_data: { name, steps: ids.map(id => ({ entity_id: id, duration_minutes: minOf(id) })), enabled: true },
            return_response: true,
          }));
          const cycleId = res && res.response && res.response.cycle && res.response.cycle.id;
          if (!cycleId) throw { label: t("wiz.fail_plan"), error: new Error(t("common.unknown")) };
          await step(t("wiz.fail_schedule"), () => svc("add_schedule", {
            cycle_id: cycleId, ...when, duration_minutes: 1, name, enabled: true,
          }));
        } else {
          for (const id of ids) {
            await step(t("wiz.fail_zone_time", { zone: nameOf(id) }), () => svc("add_schedule", {
              valve_entity_id: id, ...when, duration_minutes: minOf(id), name, enabled: true,
            }));
          }
        }
      } catch (err) {
        wz.saving = false;
        const e = err && err.error ? err.error : err;
        if (rainPicker && /rain_entity/.test(String((e && e.message) || ""))) rainPicker.setError(t("set.rain_invalid", { entity: rain }));
        this._toast(t("wiz.failed", { step: (err && err.label) || "", error: (e && (e.message || e.code)) || String(e) }), "error");
        nextBtn.textContent = t("wiz.save");
        refreshNext();
        this._refresh();
        return;
      }
      close();
      this._tab = "home";
      this._view = null;
      await this._refresh();
      this._render();
      this._toast(t("wiz.saved", { plan: name }), "ok");
    };

    const draw = () => {
      drawHead();
      const keys = stepKeys();
      const key = keys[wz.idx];
      body.innerHTML = "";
      foot.innerHTML = "";
      ({ pick: bodyPick, when: bodyWhen, plan: bodyPlan, check: bodyCheck })[key]();
      const last = wz.idx === keys.length - 1;
      const backBtn = el("button", {
        class: "btn", type: "button",
        onClick: () => { if (wz.saving) return; if (wz.idx === 0) close(); else { wz.idx--; draw(); } },
      }, t(wz.idx === 0 ? "common.cancel" : "wiz.back"));
      nextBtn = el("button", {
        class: "btn primary", type: "button",
        onClick: () => {
          if (!valid(key) || wz.saving) return;
          if (last) save();
          else { wz.idx++; draw(); }
        },
      }, t(last ? "wiz.save" : "wiz.next"));
      const right = [nextBtn];
      if (wz.idx > 0) right.unshift(el("button", { class: "btn ghost", type: "button", onClick: () => { if (!wz.saving) close(); } }, t("common.cancel")));
      foot.append(backBtn, el("div", { class: "actions" }, right));
      refreshNext();
      // A step without a field (the check step) puts focus on its heading, not on the page behind (BUG-003).
      const first = body.querySelector("input, button") || head.querySelector("h3");
      if (first) first.focus();
    };

    close = this._openDialog(overlay, modal, { canClose: () => !wz.saving, focus: () => { draw(); return null; } });
  }

  // ---------- Reports ----------

  _renderReports(root) {
    const history = this._state.history || [];
    const valves = this._state.valves || [];
    const cycles = this._state.cycles || [];
    const cyclesById = Object.fromEntries(cycles.map(c => [c.id, c]));
    const now = this._state.now;
    const day = 86400;

    const inWindow = (ts, days) => ts >= (now - days * day);

    const valveStats = {};
    const cycleStats = {};
    const dailyMin = {};
    // Every skipped_* status lands in exactly one tile (Other catches the rest), so the tiles add up.
    const skipReasons = {
      skipped_rain: 0, skipped_moisture: 0, skipped_overlap: 0, skipped_seasonal_zero: 0, skipped_other: 0,
      failed_to_open: 0, cancelled: 0,
    };
    const water = {};
    let water30 = 0;
    let historyWater = false;

    history.forEach(h => {
      const status = h.status || "";
      const dur = parseInt(h.duration_min || 0, 10);
      const isCycleEntry = !!cyclesById[h.valve_entity_id];

      if (status === "started") return;

      if (status in skipReasons) skipReasons[status]++;
      else if (status.startsWith("skipped_")) skipReasons.skipped_other++;

      const liters = Number(h.liters) || 0;
      if (!isCycleEntry && liters > 0) {
        historyWater = true;
        const w = water[h.valve_entity_id] = water[h.valve_entity_id] || { d7: 0, d30: 0 };
        if (inWindow(h.ts, 7)) w.d7 += liters;
        if (inWindow(h.ts, 30)) { w.d30 += liters; water30 += liters; }
      }

      if (!isCycleEntry) {
        const id = h.valve_entity_id;
        const s = valveStats[id] = valveStats[id] || { runs_7d: 0, min_7d: 0, runs_30d: 0, min_30d: 0, runs_total: 0, min_total: 0, last: null };
        if (status === "completed" || status === "cancelled") {
          if (inWindow(h.ts, 7)) { s.runs_7d++; s.min_7d += dur; }
          if (inWindow(h.ts, 30)) { s.runs_30d++; s.min_30d += dur; }
          s.runs_total++; s.min_total += dur;
          if (!s.last || h.ts > s.last.ts) s.last = h;
          if (inWindow(h.ts, 30)) {
            const dayKey = I18N.dayKey(h.ts, this._hass);
            dailyMin[dayKey] = (dailyMin[dayKey] || 0) + dur;
          }
        } else if (status === "superseded" && h.planned_min != null) {
          // Replaced by a new run on the zone: not a run of its own, but its minutes were watered (BUG-028).
          // Rows written before 0.15.0 have no planned_min and hold the planned length, not what watered.
          if (inWindow(h.ts, 7)) s.min_7d += dur;
          if (inWindow(h.ts, 30)) {
            s.min_30d += dur;
            const dayKey = I18N.dayKey(h.ts, this._hass);
            dailyMin[dayKey] = (dailyMin[dayKey] || 0) + dur;
          }
          s.min_total += dur;
        }
      } else {
        const id = h.valve_entity_id;
        const cs = cycleStats[id] = cycleStats[id] || { runs_30d: 0, completed: 0, cancelled: 0, skipped: 0 };
        if (inWindow(h.ts, 30)) {
          cs.runs_30d++;
          if (status === "cycle_completed") cs.completed++;
          else if (status === "cycle_cancelled") cs.cancelled++;
          else if (status.startsWith("skipped")) cs.skipped++;
        }
      }
    });

    root.appendChild(el("div", { class: "section-h" }, [
      el("button", { class: "btn ghost", onClick: () => { this._view = null; this._render(); } }, [this._chevron(false), " ", this._t("reports.back")]),
    ]));

    root.appendChild(el("div", { class: "card" }, [
      el("div", { class: "row-between", style: "margin-bottom:8px;" }, [
        el("h2", { style: "margin:0;" }, this._t("tab.reports")),
        el("button", {
          class: "btn primary small",
          onClick: () => this._downloadHistoryCsv(),
        }, this._t("reports.export")),
      ]),
      // No storage limit in the sentence (UX-018); it is only said when the oldest records are being dropped.
      el("p", { class: "muted small", style: "margin:0;" },
        this._t(history.length >= 500 ? "reports.based_on_full" : "reports.based_on", { n: history.length })),
    ]));

    const totalWater = Number(this._state.water_total_l) || 0;
    const hasWater = historyWater || totalWater > 0 || valves.some(v => (Number(v.water_total_l) || 0) > 0);
    if (hasWater) {
      root.appendChild(el("div", { class: "card" }, [
        el("p", { style: "margin:0;font-weight:500;" }, this._t("reports.water_headline", { total: this._fmtLiters(totalWater), d30: this._fmtLiters(water30) })),
      ]));
    }

    const dayLabels = [];
    const dayValues = [];
    for (let i = 29; i >= 0; i--) {
      const key = I18N.dayKey(now - i * day, this._hass);
      dayLabels.push(this._fmtDate(now - i * day, { month: "numeric", day: "numeric" }));
      dayValues.push(dailyMin[key] || 0);
    }
    const maxVal = Math.max(1, ...dayValues);
    const totalMin = dayValues.reduce((a, b) => a + b, 0);
    const peak = dayValues.indexOf(Math.max(...dayValues));
    // BUG-009: the bars are a picture; the name carries the total and the peak day, the table every value.
    const chartSummary = totalMin
      ? this._t("reports.chart_summary", { total: totalMin, date: dayLabels[peak], n: dayValues[peak] })
      : this._t("reports.chart_none");
    const chartCard = el("div", { class: "card" }, [el("h2", {}, this._t("reports.chart_title"))]);
    const chart = el("div", {
      role: "img",
      "aria-label": chartSummary,
      style: "display:flex;align-items:flex-end;gap:2px;height:120px;border-bottom:1px solid var(--sw-border);padding-bottom:4px;",
    });
    dayValues.forEach((v, i) => {
      const h = Math.round((v / maxVal) * 110);
      chart.appendChild(el("div", {
        title: this._t("reports.bar_title", { date: dayLabels[i], n: v }),
        style: `flex:1;height:${h}px;min-width:6px;background:var(--sw-primary);border-radius:2px 2px 0 0;`,
      }));
    });
    // A minute scale for the bars (UX-018): the top value of the axis.
    chartCard.appendChild(el("div", { "aria-hidden": "true", class: "muted", style: "font-size:11px;margin-bottom:2px;" }, this._t("unit.min", { n: maxVal })));
    chartCard.appendChild(chart);
    chartCard.appendChild(el("div", { "aria-hidden": "true", style: "display:flex;justify-content:space-between;font-size:11px;color:var(--sw-muted);margin-top:4px;" }, [
      el("span", {}, dayLabels[0]),
      el("span", {}, dayLabels[Math.floor(dayValues.length / 2)]),
      el("span", {}, dayLabels[dayValues.length - 1]),
    ]));
    if (totalMin) {
      const values = reportTable("50%", [this._t("reports.col_day"), this._t("sched.duration")]);
      dayValues.forEach((v, i) => {
        if (v) values.tbody.appendChild(el("tr", {}, [el("th", { scope: "row" }, dayLabels[i]), el("td", { class: "num" }, String(v))]));
      });
      const det = el("details", { class: "chart-values" }, [el("summary", {}, this._t("reports.chart_values")), values.table]);
      if (this._chartValuesOpen) det.open = true;
      det.addEventListener("toggle", () => { this._chartValuesOpen = det.open; });
      chartCard.appendChild(det);
    }
    root.appendChild(chartCard);

    const valveTable = el("div", { class: "card" }, [el("h2", {}, this._t("reports.per_valve"))]);
    if (!valves.length) {
      valveTable.appendChild(el("div", { class: "empty" }, this._t("reports.no_valves")));
    } else {
      const t = reportTable("31%", [this._t("sched.valve"), this._t("reports.col_7d"), this._t("reports.col_30d"), this._t("reports.total")]);
      valves.forEach(v => {
        const s = valveStats[v.entity_id] || { runs_7d: 0, min_7d: 0, runs_30d: 0, min_30d: 0, runs_total: 0, min_total: 0 };
        const w = water[v.entity_id] || { d7: 0, d30: 0 };
        t.tbody.appendChild(el("tr", {}, [
          el("th", { scope: "row" }, iso(v.label)),
          ...[
            [s.runs_7d, s.min_7d, w.d7],
            [s.runs_30d, s.min_30d, w.d30],
            [s.runs_total, s.min_total, Number(v.water_total_l) || 0],
          // Runs and minutes on their own lines instead of "4x / 40 min" (UX-018).
          ].map(([runs, min, l]) => el("td", { class: "num" }, [
            el("span", { style: "display:block;" }, this._t("reports.runs", { n: runs })),
            el("span", { style: "display:block;" }, this._t("unit.min", { n: min })),
            hasWater ? el("span", { class: "water" }, this._fmtLiters(l)) : null,
          ])),
        ]));
      });
      valveTable.appendChild(t.table);
    }
    root.appendChild(valveTable);

    if (cycles.length) {
      const cycleTable = el("div", { class: "card" }, [el("h2", {}, this._t("reports.per_cycle"))]);
      const t = reportTable("35%", [
        this._t("sched.cycle"), this._t("reports.done"), this._t("reports.cancelled"), this._t("reports.skipped"), this._t("reports.total"),
      ]);
      cycles.forEach(c => {
        const s = cycleStats[c.id] || { completed: 0, cancelled: 0, skipped: 0, runs_30d: 0 };
        t.tbody.appendChild(el("tr", {}, [
          el("th", { scope: "row" }, iso(c.name)),
          el("td", { class: "num", style: "color:var(--sw-success-text);" }, String(s.completed)),
          el("td", { class: "num", style: "color:var(--sw-warn-text);" }, String(s.cancelled)),
          el("td", { class: "num", style: "color:var(--sw-muted);" }, String(s.skipped)),
          el("td", { class: "num", style: "font-weight:600;" }, String(s.runs_30d)),
        ]));
      });
      cycleTable.appendChild(t.table);
      root.appendChild(cycleTable);
    }

    const skipsCard = el("div", { class: "card" }, [el("h2", {}, this._t("reports.skip_reasons"))]);
    const skipGrid = el("div", { style: "display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;" });
    [
      ["skipped_rain", this._t("reports.rain")],
      ["skipped_moisture", this._t("reports.moisture")],
      ["skipped_overlap", this._t("reports.overlap")],
      ["skipped_seasonal_zero", this._t("reports.temperature")],
      ["skipped_other", this._t("reports.other")],
      ["failed_to_open", this._t("reports.failed")],
      ["cancelled", this._t("reports.cancelled")],
    ].forEach(([key, label]) => {
      skipGrid.appendChild(el("div", {
        style: "padding:10px;border:1px solid var(--sw-border);border-radius:8px;background:var(--sw-bg);text-align:center;",
      }, [
        el("div", { style: "font-size:24px;font-weight:600;color:var(--sw-text);" }, String(skipReasons[key] || 0)),
        el("div", { class: "muted small" }, label),
      ]));
    });
    skipsCard.appendChild(skipGrid);
    root.appendChild(skipsCard);
  }

  _downloadHistoryCsv() {
    const history = this._state.history || [];
    const valvesById = Object.fromEntries((this._state.valves || []).map(v => [v.entity_id, v.label]));
    const header = ["timestamp", "iso_time", "target_kind", "target_id", "target_label", "duration_min", "source", "status", "note", "liters"];
    const rows = history.map(h => {
      const isCycle = this._isPlanId(h.valve_entity_id);
      const id = h.valve_entity_id || "";
      const label = isCycle ? this._planName(id, h.name) : (valvesById[id] || id);
      const isoTime = new Date(h.ts * 1000).toISOString();
      return [
        h.ts, isoTime,
        isCycle ? "cycle" : "valve",
        id, label,
        h.duration_min || 0,
        h.source || "",
        h.status || "",
        h.note || "",
        (Number(h.liters) || 0) > 0 ? Number(h.liters) : "",
      ];
    });
    const escape = (v) => {
      let s = String(v == null ? "" : v);
      // #39: a text cell starting with = + - @ (or tab / CR) would run as a spreadsheet formula.
      if (typeof v === "string" && /^[=+\-@\t\r]/.test(s)) s = "'" + s;
      return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const csv = [header.map(escape).join(","), ...rows.map(r => r.map(escape).join(","))].join("\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `schedule_wizard_history_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
  }

  // ---------- Rain source (UX-011) ----------

  // The rain source as a list of what Home Assistant has (weather, rain sensors, other sensors) with a line under
  // it that says what counts as rain and what the source reports now. rules() gives the rain details in use:
  // { states, attribute, threshold }; label replaces the field caption. Returns { node, select, value(), setError(msg) }.
  _rainPicker(current, rules, label) {
    const states = (this._hass && this._hass.states) || {};
    const cur = String(current || "").trim();
    const name = (id) => String((states[id] && states[id].attributes && states[id].attributes.friendly_name) || id);
    const RAIN_WORDS = /rain|precip|regen|neerslag|pluie|pluv|lluvia|chuva|pioggia|regn|sade|deszcz|дожд|опад|осад|גשם|مطر|雨/i;
    const rainy = (id) => {
      const dc = String((states[id].attributes || {}).device_class || "");
      return dc === "precipitation" || dc === "precipitation_intensity" || dc === "moisture" || RAIN_WORDS.test(id) || RAIN_WORDS.test(name(id));
    };
    // Schedule Wizard's own sensors are never a rain source (#91, as #70 did for zones); a saved one stays visible.
    const own = new Set((this._state && this._state.own_entities) || []);
    const ids = Object.keys(states).filter(id => RAIN_DOMAINS.includes(id.split(".")[0]) && (!own.has(id) || id === cur))
      .sort((a, b) => name(a).localeCompare(name(b)));
    const weather = ids.filter(id => id.startsWith("weather."));
    const rain = ids.filter(id => !id.startsWith("weather.") && rainy(id));
    const other = ids.filter(id => !id.startsWith("weather.") && !rainy(id));
    const labelId = uid("sw-rain-label");
    const checkId = uid("sw-rain-check");
    const errId = uid("sw-rain-err");
    const sel = el("select", { "aria-labelledby": labelId, "aria-describedby": checkId });
    sel.appendChild(el("option", { value: "" }, this._t("set.rain_none")));
    if (cur && !states[cur]) sel.appendChild(el("option", { value: cur }, this._t("set.rain_missing_opt", { entity: `\u2066${cur}\u2069` })));
    [["set.rain_group_weather", weather], ["set.rain_group_rain", rain], ["set.rain_group_other", other]].forEach(([key, list]) => {
      if (!list.length) return;
      const group = el("optgroup", { label: this._t(key) });
      list.forEach(id => group.appendChild(el("option", { value: id }, optLabel(name(id), id))));
      sel.appendChild(group);
    });
    sel.value = cur;
    const check = el("p", { class: "check-line muted", id: checkId, "aria-live": "polite" });
    const err = fieldError(errId);
    const update = () => {
      setFieldError(err, sel, "");
      sel.setAttribute("aria-describedby", checkId);
      const id = sel.value;
      const st = id ? states[id] : null;
      check.className = "check-line muted";
      if (!id) { check.replaceChildren(this._t("set.rain_check_none")); return; }
      if (!st) {
        check.className = "check-line warn";
        check.replaceChildren(...this._tn("set.rain_check_missing", { entity: ltr(id) }));
        return;
      }
      const r = rules();
      const parts = rainCheckParts(st, r, (key, vars) => this._tn(key, vars), (key) => this._t(key));
      if (rainWouldSkip(st, r)) parts.push(" ", this._t("set.rain_would_skip"));
      check.replaceChildren(...parts);
    };
    sel.addEventListener("change", update);
    update();
    const node = el("div", { class: "field" }, [el("span", { id: labelId }, label || this._t("set.rain_using")), sel, err, check]);
    return {
      node, select: sel, update,
      value: () => sel.value,
      setError: (msg) => { setFieldError(err, sel, msg); if (msg) sel.setAttribute("aria-describedby", `${errId} ${checkId}`); },
    };
  }

  // What a notify service reaches, in words (UX-011): "Phone: Pixel 8", "Home Assistant notifications".
  _notifyLabel(info) {
    if (info.kind === "mobile") return this._t("notify.mobile", { name: info.name });
    if (info.kind === "persistent_notification") return this._t("notify.persistent");
    if (info.kind === "send_message") return this._t("notify.send_message");
    if (info.kind === "notify") return this._t("notify.default");
    return info.name || info.service;
  }

  // ---------- Settings ----------

  _optGroup(key, title, desc, on, children) {
    const titleId = uid("sw-group");
    const d = el("details", { class: "opt-group", "aria-labelledby": titleId });
    if (this._openGroups.has(key)) d.open = true;
    d.addEventListener("toggle", () => { if (d.open) this._openGroups.add(key); else this._openGroups.delete(key); });
    d.appendChild(el("summary", {}, [
      el("strong", { id: titleId, style: "font-weight:500;" }, title),
      on === null ? el("span", {}) : el("span", { class: "pill " + (on ? "ok" : "idle") }, this._t(on ? "common.on" : "common.off")),
      el("p", {}, desc),
    ]));
    d.appendChild(el("div", { class: "opt-body" }, children));
    return d;
  }

  _renderSettings(root) {
    const opts = this._state.options || {};
    const hint = (text) => el("p", { class: "muted" }, text);
    const field = (label, input) => el("label", { class: "field" }, [el("span", {}, label), input]);

    const calSel = el("select", {});
    calSel.appendChild(el("option", { value: "" }, this._t("common.none")));
    (this._state.calendars || []).forEach((c) => {
      const opt = el("option", { value: c.entity_id }, optLabel(c.friendly_name, c.entity_id));
      if (c.entity_id === (opts.calendar_entity || "")) opt.selected = true;
      calSel.appendChild(opt);
    });

    const lookInput = el("input", { type: "number", min: "1", max: "1440", value: String(opts.calendar_lookahead_min || 10) });
    const pollInput = el("input", { type: "number", min: "10", max: "3600", value: String(opts.poll_interval || 60) });
    const defDurInput = el("input", { type: "number", min: "1", max: "1440", value: String(opts.default_duration || 10) });
    // #78: optional title keyword for calendar events; #79: longest calendar / webhook run.
    const calKeywordInput = el("input", { type: "text", maxlength: "40", placeholder: "\u2066water:\u2069", value: String(opts.calendar_keyword || "") });
    const calKeywordErr = el("div", { class: "field-error", id: "sw-set-cal-keyword-err", role: "alert", hidden: true });
    const maxExtInput = el("input", { type: "number", min: "1", max: "1440", step: "1", inputmode: "numeric", value: String(opts.max_external_minutes || 120) });
    const maxExtErr = el("div", { class: "field-error", id: "sw-set-max-ext-err", role: "alert", hidden: true });
    const showSetErr = (node, input, msg) => {
      node.textContent = msg || "";
      node.hidden = !msg;
      if (msg) { input.setAttribute("aria-invalid", "true"); input.setAttribute("aria-describedby", node.id); }
      else { input.removeAttribute("aria-invalid"); input.removeAttribute("aria-describedby"); }
    };
    const maxExtValue = () => {
      const raw = String(maxExtInput.value).trim();
      const n = Number(raw);
      return raw !== "" && Number.isInteger(n) && n >= 1 && n <= 1440 ? n : null;
    };
    const externalCheck = () => {
      const kwBad = calKeywordInput.value.trim().length > 40;
      const extBad = maxExtValue() === null;
      showSetErr(calKeywordErr, calKeywordInput, kwBad ? this._t("set.cal_keyword_err") : "");
      showSetErr(maxExtErr, maxExtInput, extBad ? this._t("set.max_external_err") : "");
      return kwBad ? calKeywordInput : (extBad ? maxExtInput : null);
    };
    calKeywordInput.addEventListener("input", () => { if (calKeywordErr.textContent) externalCheck(); });
    maxExtInput.addEventListener("input", () => { if (maxExtErr.textContent) externalCheck(); });
    const rainStatesInput = el("input", { type: "text", dir: "ltr", placeholder: "rainy,pouring,snowy,lightning-rainy", value: String(opts.rain_skip_states || "") });
    const rainAttrInput = el("input", { type: "text", placeholder: this._t("settings.rain_attr_ph"), value: String(opts.rain_attribute || "") });
    const rainThresholdInput = el("input", { type: "number", min: "0", max: "100", step: "0.1", value: opts.rain_threshold != null ? String(opts.rain_threshold) : "" });
    const rainPicker = this._rainPicker(opts.rain_entity, () => rainRules(rainStatesInput.value, rainAttrInput.value, rainThresholdInput.value));
    [rainStatesInput, rainAttrInput, rainThresholdInput].forEach(i => i.addEventListener("input", rainPicker.update));

    // Essentials
    const ess = el("div", { class: "card" }, [el("h2", {}, this._t("set.essentials"))]);
    ess.appendChild(rainPicker.node);

    const availableTargets = this._state.notify_services || [];
    const availableEvents = this._state.notify_events || [];
    const currentTargets = new Set(Array.isArray(opts.notify_targets) ? opts.notify_targets : (opts.notify_targets ? String(opts.notify_targets).split(",").map(s => s.trim()).filter(Boolean) : []));
    const currentEvents = new Set(Array.isArray(opts.notify_events) ? opts.notify_events : (opts.notify_events ? String(opts.notify_events).split(",").map(s => s.trim()).filter(Boolean) : []));

    const targetsCap = uid("sw-notify-to");
    const eventsCap = uid("sw-notify-when");
    const targetsWrap = el("div", { class: "check-wrap", role: "group", "aria-labelledby": targetsCap });
    if (!availableTargets.length) {
      targetsWrap.appendChild(el("div", { class: "empty", style: "padding:4px;" }, this._t("settings.no_notify")));
    } else {
      const infos = Array.isArray(this._state.notify_targets_info) ? this._state.notify_targets_info
        : availableTargets.map(service => ({ service, kind: "other", name: service }));
      infos.forEach(info => {
        const name = info.service;
        const cb = el("input", { type: "checkbox" });
        cb.checked = currentTargets.has(name);
        cb.addEventListener("change", () => { if (cb.checked) currentTargets.add(name); else currentTargets.delete(name); });
        // Readable name; the service itself stays in the tooltip for people who know it (UX-011).
        targetsWrap.appendChild(el("label", { title: `notify.${name}` }, [cb, iso(this._notifyLabel(info))]));
      });
    }
    const eventsWrap = el("div", { class: "check-wrap", role: "group", "aria-labelledby": eventsCap });
    // Short label for the long 0 % skip text, next to "Skipped (rain)" (UX-018).
    const eventLabel = (ev) => (ev === "skipped_seasonal" ? this._t("set.ev_skipped_seasonal")
      : this._t.has("event." + ev) ? this._t("event." + ev) : ev);
    availableEvents.forEach(ev => {
      const cb = el("input", { type: "checkbox" });
      cb.checked = currentEvents.has(ev);
      cb.addEventListener("change", () => { if (cb.checked) currentEvents.add(ev); else currentEvents.delete(ev); });
      eventsWrap.appendChild(el("label", {}, [cb, eventLabel(ev)]));
    });
    ess.appendChild(el("div", { class: "field" }, [el("span", { id: targetsCap }, this._t("settings.notify_services")), targetsWrap]));
    ess.appendChild(el("div", { class: "field" }, [el("span", { id: eventsCap }, this._t("settings.notify_when")), eventsWrap]));
    const curReminder = Math.max(0, parseInt(opts.reminder_minutes, 10) || 0);
    const reminderVals = [0, 10, 15, 30, 60];
    if (!reminderVals.includes(curReminder)) reminderVals.push(curReminder);
    const reminderSel = el("select", {});
    reminderVals.sort((a, b) => a - b).forEach(n => {
      const opt = el("option", { value: String(n) }, n ? this._t("set.reminder_opt", { n }) : this._t("common.off"));
      if (n === curReminder) opt.selected = true;
      reminderSel.appendChild(opt);
    });
    ess.appendChild(field(this._t("set.reminder"), reminderSel));
    ess.appendChild(el("p", { class: "muted small", style: "margin:-6px 0 12px;" }, this._t("set.reminder_hint")));
    ess.appendChild(field(this._t("set.calendar_optional"), calSel));
    ess.appendChild(el("p", { class: "muted small", style: "margin:-6px 0 0;" }, this._t("settings.calendar_hint")));
    root.appendChild(ess);

    // Seasonal
    const tempUnit = this._state.temperature_unit || "°";
    const seasonalEnabledInput = el("input", { type: "checkbox" });
    seasonalEnabledInput.checked = !!opts.seasonal_enabled;
    const seasonalTempEntity = el("input", { type: "text", dir: "ltr", placeholder: this._t("settings.temp_entity_ph"), value: String(opts.seasonal_temp_entity || "") });
    const seasonalTempAttr = el("input", { type: "text", placeholder: this._t("settings.temp_attr_ph"), value: String(opts.seasonal_temp_attribute || "") });
    const seasonalLow = el("input", { type: "number", step: "0.5", value: String(opts.seasonal_temp_low ?? 10) });
    const seasonalHigh = el("input", { type: "number", step: "0.5", value: String(opts.seasonal_temp_high ?? 30) });
    const seasonalMin = el("input", { type: "number", min: "0", max: "200", value: String(opts.seasonal_min_pct ?? 50) });
    const seasonalMax = el("input", { type: "number", min: "0", max: "200", value: String(opts.seasonal_max_pct ?? 120) });
    const seasonalPreview = el("div", {
      style: "margin-top:8px;padding:8px 10px;border-radius:6px;background:var(--sw-bg);border:1px solid var(--sw-border);font-size:13px;",
    });
    let previewSeq = 0;
    let previewTimer = null;
    const computePreview = () => {
      const seq = ++previewSeq;
      const entityId = seasonalTempEntity.value.trim();
      if (!entityId) {
        seasonalPreview.innerHTML = "";
        seasonalPreview.appendChild(el("span", { class: "muted" }, this._t("settings.preview_need_entity")));
        return;
      }
      const attr = seasonalTempAttr.value.trim();
      const lookup = this._hass && this._hass.states
        ? Promise.resolve(this._hass.states[entityId] || null)
        : this._hass.callWS({ type: "get_states" }).then(states => states.find(x => x.entity_id === entityId) || null);
      lookup.then(s => {
        if (seq !== previewSeq) return;
        seasonalPreview.innerHTML = "";
        if (!s) { seasonalPreview.appendChild(el("span", { style: "color:var(--sw-danger-text)" }, this._tn("settings.preview_not_found", { entity: ltr(entityId) }))); return; }
        let temp = null;
        try { temp = parseFloat(attr ? s.attributes[attr] : s.state); } catch {}
        if (temp == null || isNaN(temp)) { seasonalPreview.appendChild(el("span", { style: "color:var(--sw-danger-text)" }, this._tn("settings.preview_not_numeric", { state: ltr(s.state) }))); return; }
        const low = parseFloat(seasonalLow.value) || 0;
        const high = parseFloat(seasonalHigh.value) || 0;
        const minP = parseFloat(seasonalMin.value) || 0;
        const maxP = parseFloat(seasonalMax.value) || 0;
        let pct;
        if (high <= low) pct = 100;
        else if (temp <= low) pct = minP;
        else if (temp >= high) pct = maxP;
        else { const f = (temp - low) / (high - low); pct = minP + f * (maxP - minP); }
        const example10 = Math.max(1, Math.round(10 * pct / 100));
        // 0 % skips scheduled watering. Math.round (half up) matches the backend's seasonal_percent().
        seasonalPreview.appendChild(el("span", {}, Math.round(pct) <= 0
          ? this._tn("settings.preview_skip", { temp: ltr(`${temp}${tempUnit}`), arrow: this._arrow() })
          : this._tn("settings.preview", {
            temp: ltr(`${temp}${tempUnit}`), arrow: this._arrow(), pct: String(Math.round(pct)), n: example10,
          })));
      }).catch(() => {
        if (seq !== previewSeq) return;
        seasonalPreview.innerHTML = "";
        seasonalPreview.appendChild(el("span", { class: "muted" }, this._t("settings.preview_error")));
      });
    };
    const schedulePreview = () => {
      if (previewTimer) clearTimeout(previewTimer);
      previewTimer = setTimeout(() => { previewTimer = null; computePreview(); }, 400);
    };
    [seasonalTempEntity, seasonalTempAttr, seasonalLow, seasonalHigh, seasonalMin, seasonalMax].forEach(i => i.addEventListener("input", schedulePreview));
    computePreview();

    // Moisture
    const moistureEntity = el("input", { type: "text", dir: "ltr", placeholder: "sensor.garden_moisture", value: String(opts.moisture_entity || "") });
    const moistureAttr = el("input", { type: "text", placeholder: this._t("common.moisture_attr_ph"), value: String(opts.moisture_attribute || "") });
    const moistureThresholdRaw = (opts.moisture_threshold_skip_above === null || opts.moisture_threshold_skip_above === undefined) ? "" : String(opts.moisture_threshold_skip_above);
    const moistureThreshold = el("input", { type: "number", min: "0", max: "100", step: "0.5", value: moistureThresholdRaw });

    // Overlap
    const allowConcurrent = el("input", { type: "checkbox" });
    allowConcurrent.checked = !!opts.allow_concurrent_cycles;

    // Master
    const masterEntity = el("input", { type: "text", dir: "ltr", placeholder: "switch.water_pump", value: String(opts.master_valve_entity || "") });
    const masterPreOpen = el("input", { type: "number", min: "0", max: "600", value: String(opts.master_valve_pre_open_sec ?? 0) });
    // Inline error; the server checks the same rule (#40).
    const masterErr = el("div", { class: "field-error", id: "sw-master-err", role: "alert", hidden: true });
    const masterCheck = () => {
      const v = masterEntity.value.trim();
      const ok = !v || v === String(opts.master_valve_entity || "") ||
        (this._state.controllable || []).some(c => c.entity_id === v);
      masterErr.replaceChildren(...(ok ? [] : this._tn("settings.master_invalid", { entity: ltr(v) })));
      masterErr.hidden = ok;
      if (ok) { masterEntity.removeAttribute("aria-invalid"); masterEntity.removeAttribute("aria-describedby"); }
      else { masterEntity.setAttribute("aria-invalid", "true"); masterEntity.setAttribute("aria-describedby", masterErr.id); }
      return ok;
    };
    masterEntity.addEventListener("change", masterCheck);

    // Fail detection
    const failEnabled = el("input", { type: "checkbox" });
    failEnabled.checked = !!opts.fail_detection_enabled;
    const failSeconds = el("input", { type: "number", min: "1", max: "120", value: String(opts.fail_detection_seconds ?? 5) });

    // Flow
    const numVal = (v) => (v === null || v === undefined) ? "" : String(v);
    const flowEntity = el("input", { type: "text", dir: "ltr", placeholder: "sensor.water_flow", value: String(opts.flow_entity || "") });
    const flowAttr = el("input", { type: "text", placeholder: this._t("settings.flow_attr_ph"), value: String(opts.flow_attribute || "") });
    const flowLeak = el("input", { type: "number", min: "0", step: "0.1", value: numVal(opts.flow_leak_threshold ?? 0) });
    const flowMax = el("input", { type: "number", min: "0", step: "0.1", value: numVal(opts.flow_max_running ?? 0) });
    const flowDelay = el("input", { type: "number", min: "5", max: "3600", value: numVal(opts.flow_delay_sec ?? 60) });
    const flowStopAll = el("input", { type: "checkbox" });
    flowStopAll.checked = !!opts.flow_stop_all;

    // Rain forecast
    const fcEntity = el("input", { type: "text", dir: "ltr", placeholder: "weather.home", value: String(opts.forecast_entity || "") });
    const fcMm = el("input", { type: "number", min: "0", step: "0.5", value: numVal(opts.forecast_skip_mm ?? 0) });
    const fcHours = el("select", {});
    [6, 12, 24, 48].forEach(h => fcHours.appendChild(el("option", { value: String(h) }, this._t("set.fc_hours_opt", { n: h }))));
    fcHours.value = String([6, 12, 24, 48].includes(Number(opts.forecast_hours)) ? opts.forecast_hours : 24);
    const fc = this._state.forecast || {};
    const fcNow = !fc.entity_id ? null
      : (fc.mm === null || fc.mm === undefined)
        ? this._t("set.fc_unavailable")
        : this._t("set.fc_now", { mm: fc.mm, n: fc.hours || 24 });

    // Webhook
    const webhookId = this._state.webhook_id || "";
    const webhookChildren = [hint(this._t("settings.webhook_hint"))];
    if (webhookId) {
      let webhookUrl = `${location.origin}/api/webhook/${webhookId}`;
      const urlInput = el("input", {
        type: "text", readonly: true, dir: "ltr", value: webhookUrl,
        "aria-label": this._t("settings.webhook"),
        style: "width:100%;padding:6px 8px;border:1px solid var(--sw-border);border-radius:6px;background:var(--sw-bg);color:var(--sw-text);font-family:monospace;font-size:12px;",
        onClick: (e) => e.target.select(),
      });
      webhookChildren.push(urlInput, el("button", {
        class: "btn small",
        style: "margin-top:6px;",
        onClick: async () => {
          try {
            await navigator.clipboard.writeText(webhookUrl);
          } catch {
            urlInput.select();
            document.execCommand("copy");
          }
          this._toast(this._t("common.copied"), "ok");
        },
      }, this._t("settings.copy_url")), el("button", {
        class: "btn small",
        style: "margin-top:6px;margin-inline-start:6px;",
        onClick: async () => {
          if (!await this._confirm(this._t("settings.webhook_rotate_confirm"), this._t("settings.webhook_rotate"))) return;
          try {
            const res = await this._hass.callWS({ type: "schedule_wizard/rotate_webhook" });
            this._state.webhook_id = res.webhook_id;
            webhookUrl = `${location.origin}/api/webhook/${res.webhook_id}`;
            urlInput.value = webhookUrl;
            this._toast(this._t("settings.webhook_rotated"), "ok");
          } catch (e) {
            this._toast(e.message || String(e), "error");
          }
        },
      }, this._t("settings.webhook_rotate")));
    } else {
      webhookChildren.push(hint(this._t("settings.webhook_admin_only")));
    }

    // Voice
    let voiceOn = opts.voice_enabled !== false;
    const voiceSwitch = el("button", {
      type: "button",
      class: "switch",
      role: "switch",
      "aria-checked": voiceOn ? "true" : "false",
      "aria-label": this._t("set.voice_toggle"),
      onClick: () => { voiceOn = !voiceOn; voiceSwitch.setAttribute("aria-checked", voiceOn ? "true" : "false"); },
    });
    const voiceChildren = [
      el("div", { class: "row-between", style: "margin-bottom:12px;" }, [el("span", {}, this._t("set.voice_toggle")), voiceSwitch]),
      el("p", { class: "muted", style: "margin:0;" }, this._t("set.voice_examples")),
      el("ul", { class: "voice-ex" }, [1, 2, 3, 4, 5].map(i => el("li", {}, this._t("set.voice_ex" + i)))),
      hint(this._tn("set.voice_entities", { entity: ltr("switch.<zone>_watering") })),
    ];

    // Smarter cycle & soak
    let interleaveOn = opts.interleave_soak !== false;
    const interleaveSwitch = el("button", {
      type: "button",
      class: "switch",
      role: "switch",
      "aria-checked": interleaveOn ? "true" : "false",
      "aria-label": this._t("set.interleave_toggle"),
      onClick: () => { interleaveOn = !interleaveOn; interleaveSwitch.setAttribute("aria-checked", interleaveOn ? "true" : "false"); },
    });

    // A <details> group is named by its caption (BUG-025).
    const moreCap = uid("sw-more");
    const more = el("details", { class: "more", "aria-labelledby": moreCap });
    if (this._moreOpen) more.open = true;
    more.addEventListener("toggle", () => { this._moreOpen = more.open; });
    more.appendChild(el("summary", { id: moreCap }, this._t("set.more")));
    more.appendChild(el("p", { class: "muted small", style: "margin:8px 0 4px;" }, this._t("set.more_hint")));
    more.append(
      this._optGroup("seasonal", this._t("set.g_seasonal"), this._t("set.g_seasonal_d"), !!opts.seasonal_enabled, [
        el("p", { class: "muted" }, [
          this._t("settings.seasonal_p1") + " " + this._t("settings.seasonal_p2"),
          el("br"),
          el("b", {}, this._t("settings.seasonal_how") + " "),
          this._t("settings.seasonal_p3", { arrow: this._arrow() }) + " " + this._t("settings.seasonal_p4") + " " + this._t("settings.seasonal_p5"),
        ]),
        field(this._t("common.enabled"), seasonalEnabledInput),
        field(this._t("settings.temp_entity"), seasonalTempEntity),
        field(this._t("settings.temp_attr"), seasonalTempAttr),
        el("div", { class: "field-row" }, [
          field(this._t("settings.temp_low", { unit: tempUnit }), seasonalLow),
          field(this._t("settings.temp_high", { unit: tempUnit }), seasonalHigh),
        ]),
        el("div", { class: "field-row" }, [
          field(this._t("settings.min_pct"), seasonalMin),
          field(this._t("settings.max_pct"), seasonalMax),
        ]),
        seasonalPreview,
      ]),
      this._optGroup("moisture", this._t("set.g_moisture"), this._t("set.g_moisture_d"), !!opts.moisture_entity, [
        hint(this._t("settings.moisture_hint")),
        field(this._t("settings.moisture_entity"), moistureEntity),
        el("div", { class: "field-row" }, [
          field(this._t("common.attribute_optional"), moistureAttr),
          field(this._t("common.skip_when_gte"), moistureThreshold),
        ]),
      ]),
      this._optGroup("forecast", this._t("set.g_forecast"), this._t("set.g_forecast_d"), !!opts.forecast_entity && Number(opts.forecast_skip_mm) > 0, [
        hint(this._t("set.fc_hint")),
        field(this._t("set.fc_entity"), fcEntity),
        el("div", { class: "field-row" }, [
          field(this._t("set.fc_mm"), fcMm),
          field(this._t("set.fc_hours"), fcHours),
        ]),
        fcNow ? el("p", { class: "muted small" }, fcNow) : null,
      ]),
      this._optGroup("interleave", this._t("set.g_interleave"), this._t("set.g_interleave_d"), opts.interleave_soak !== false, [
        el("div", { class: "row-between", style: "margin-bottom:12px;gap:12px;" }, [el("span", {}, this._t("set.interleave_toggle")), interleaveSwitch]),
        hint(this._t("set.interleave_hint")),
      ]),
      this._optGroup("master", this._t("set.g_master"), this._t("set.g_master_d"), !!opts.master_valve_entity, [
        hint(this._t("settings.master_hint")),
        field(this._t("settings.master_entity"), masterEntity),
        masterErr,
        field(this._t("settings.master_pre_open"), masterPreOpen),
      ]),
      this._optGroup("flow", this._t("set.g_flow"), this._t("set.g_flow_d"), !!opts.flow_entity, [
        hint(this._t("settings.flow_hint")),
        hint(this._t("settings.flow_water_hint")),
        field(this._t("settings.flow_entity"), flowEntity),
        field(this._t("common.attribute_optional"), flowAttr),
        el("div", { class: "field-row" }, [
          field(this._t("settings.flow_leak"), flowLeak),
          field(this._t("settings.flow_max"), flowMax),
        ]),
        el("div", { class: "field-row" }, [
          field(this._t("settings.flow_delay"), flowDelay),
          field(this._t("settings.flow_stop_all"), flowStopAll),
        ]),
      ]),
      this._optGroup("fail", this._t("set.g_fail"), this._t("set.g_fail_d"), !!opts.fail_detection_enabled, [
        hint(this._t("settings.fail_hint")),
        field(this._t("common.enabled"), failEnabled),
        field(this._t("settings.fail_window"), failSeconds),
      ]),
      this._optGroup("overlap", this._t("set.g_overlap"), this._t("set.g_overlap_d"), !!opts.allow_concurrent_cycles, [
        hint(this._t("settings.overlap_hint")),
        field(this._t("settings.allow_concurrent"), allowConcurrent),
      ]),
      this._optGroup("voice", this._t("set.g_voice"), this._t("set.g_voice_d"), opts.voice_enabled !== false, voiceChildren),
      this._optGroup("calendar", this._t("set.g_calendar"), this._t("set.g_calendar_d"), null, [
        el("div", { class: "field-row" }, [
          field(this._t("settings.lookahead"), lookInput),
          field(this._t("settings.poll"), pollInput),
        ]),
        field(this._t("settings.default_duration"), defDurInput),
        el("label", { class: "field" }, [el("span", {}, this._t("set.cal_keyword")), calKeywordInput, calKeywordErr]),
        hint(this._t("set.cal_keyword_hint")),
        el("label", { class: "field" }, [el("span", {}, this._t("set.max_external")), maxExtInput, maxExtErr]),
        hint(this._t("set.max_external_hint")),
      ]),
      this._optGroup("rain", this._t("set.g_rain"), this._t("set.g_rain_d"), null, [
        hint(this._t("settings.rain_hint")),
        field(this._t("settings.rain_states"), rainStatesInput),
        el("div", { class: "field-row" }, [
          field(this._t("settings.rain_attr"), rainAttrInput),
          field(this._t("settings.rain_threshold"), rainThresholdInput),
        ]),
      ]),
      this._optGroup("webhook", this._t("settings.webhook"), this._t("set.g_webhook_d"), null, webhookChildren),
      this._optGroup("current", this._t("settings.current"), this._t("set.g_current_d"), null, [
        el("pre", { dir: "ltr" }, JSON.stringify(opts, null, 2)),
        hint(this._t("settings.current_hint", { arrow: this._arrow() })),
      ]),
    );
    root.appendChild(el("div", { class: "card" }, more));

    const feedback = el("div", { class: "muted", style: "font-size:12px;", "aria-live": "polite" });
    const saveBtn = el("button", { class: "btn primary" }, this._t("settings.save"));
    saveBtn.addEventListener("click", async () => {
      if (!masterCheck()) {
        more.open = true;
        const group = masterErr.closest("details");
        if (group) group.open = true;
        masterEntity.focus();
        this._toast(masterErr.textContent, "error");
        return;
      }
      const rainNow = rainPicker.value();
      const ownIds = new Set(this._state.own_entities || []);
      if (rainNow && rainNow !== String(opts.rain_entity || "").trim() && (!(this._hass.states || {})[rainNow] || ownIds.has(rainNow))) {
        rainPicker.setError(this._t("set.rain_invalid", { entity: rainNow }));
        rainPicker.select.focus();
        return;
      }
      const badExternal = externalCheck();
      if (badExternal) {
        more.open = true;
        const group = badExternal.closest("details");
        if (group) group.open = true;
        badExternal.focus();
        return;
      }
      saveBtn.disabled = true;
      const oldText = saveBtn.textContent;
      saveBtn.textContent = this._t("settings.saving");
      const thresholdRaw = rainThresholdInput.value.trim();
      const threshold = thresholdRaw === "" ? null : parseFloat(thresholdRaw);
      const seasonalNums = {};
      [
        ["seasonal_temp_low", seasonalLow],
        ["seasonal_temp_high", seasonalHigh],
        ["seasonal_min_pct", seasonalMin],
        ["seasonal_max_pct", seasonalMax],
      ].forEach(([key, input]) => {
        const n = parseFloat(input.value);
        if (input.value.trim() !== "" && !isNaN(n)) seasonalNums[key] = n;
      });
      const flowNums = {};
      [["flow_leak_threshold", flowLeak], ["flow_max_running", flowMax]].forEach(([key, input]) => {
        const n = parseFloat(input.value);
        if (input.value.trim() !== "" && !isNaN(n)) flowNums[key] = Math.max(0, n);
      });
      const fcN = parseFloat(fcMm.value);
      if (fcMm.value.trim() !== "" && !isNaN(fcN)) flowNums.forecast_skip_mm = Math.max(0, fcN);
      const delayN = parseInt(flowDelay.value, 10);
      if (flowDelay.value.trim() !== "" && !isNaN(delayN)) flowNums.flow_delay_sec = Math.min(3600, Math.max(5, delayN));
      try {
        await this._hass.callWS({
          type: "schedule_wizard/update_options",
          calendar_entity: calSel.value || "",
          calendar_lookahead_min: parseInt(lookInput.value, 10) || 10,
          poll_interval: parseInt(pollInput.value, 10) || 60,
          default_duration: parseInt(defDurInput.value, 10) || 10,
          rain_entity: rainPicker.value(),
          rain_skip_states: rainStatesInput.value.trim(),
          rain_attribute: rainAttrInput.value.trim(),
          rain_threshold: (threshold !== null && !isNaN(threshold)) ? threshold : null,
          notify_targets: Array.from(currentTargets),
          notify_events: Array.from(currentEvents),
          seasonal_enabled: seasonalEnabledInput.checked,
          seasonal_temp_entity: seasonalTempEntity.value.trim(),
          seasonal_temp_attribute: seasonalTempAttr.value.trim(),
          ...seasonalNums,
          allow_concurrent_cycles: allowConcurrent.checked,
          moisture_entity: moistureEntity.value.trim(),
          moisture_attribute: moistureAttr.value.trim(),
          moisture_threshold_skip_above: moistureThreshold.value.trim() === "" ? null : parseFloat(moistureThreshold.value),
          master_valve_entity: masterEntity.value.trim(),
          master_valve_pre_open_sec: parseInt(masterPreOpen.value, 10) || 0,
          fail_detection_enabled: failEnabled.checked,
          fail_detection_seconds: parseInt(failSeconds.value, 10) || 5,
          flow_entity: flowEntity.value.trim(),
          flow_attribute: flowAttr.value.trim(),
          ...flowNums,
          flow_stop_all: flowStopAll.checked,
          forecast_entity: fcEntity.value.trim(),
          forecast_hours: parseInt(fcHours.value, 10) || 24,
          reminder_minutes: Math.min(720, Math.max(0, parseInt(reminderSel.value, 10) || 0)),
          voice_enabled: voiceOn,
          interleave_soak: interleaveOn,
          calendar_keyword: calKeywordInput.value.trim(),
          max_external_minutes: maxExtValue(),
        });
        feedback.textContent = this._t("settings.saved_at", {
          time: this._fmtTime(Math.floor(Date.now() / 1000), { hour: "numeric", minute: "2-digit", second: "2-digit" }),
        });
        this._toast(this._t("settings.saved"), "ok");
        setTimeout(() => this._refresh(), 1500);
      } catch (e) {
        if (/rain_entity/.test(String(e.message || ""))) {
          rainPicker.setError(this._t("set.rain_invalid", { entity: rainPicker.value() }));
          rainPicker.select.focus();
        }
        this._toast(e.message || String(e), "error");
        feedback.textContent = this._t("settings.save_failed", { error: e.message || e });
      } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = oldText;
      }
    });
    root.appendChild(el("div", { class: "row-between", style: "margin-bottom:14px;" }, [feedback, saveBtn]));
  }

  _showModal(title, fields, onSave) {
    const titleId = uid("sw-dialog-title");
    const modal = el("div", { class: "modal", role: "dialog", "aria-modal": "true", "aria-labelledby": titleId });
    modal.appendChild(el("h3", { id: titleId }, title));
    fields.forEach((f) => modal.appendChild(f));

    let close = () => {};
    const cancelBtn = el("button", { class: "btn", onClick: () => close() }, this._t("common.cancel"));
    const saveBtn = el("button", { class: "btn primary", onClick: async () => {
      saveBtn.disabled = true;
      try {
        const ok = await onSave();
        if (ok) close();
      } finally {
        saveBtn.disabled = false;
      }
    } }, this._t("common.save"));

    modal.appendChild(el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]));

    const overlay = el("div", { class: "modal-overlay" }, modal);
    close = this._openDialog(overlay, modal);
  }
}

if (!customElements.get("schedule-wizard-panel")) {
  customElements.define("schedule-wizard-panel", ScheduleWizardPanel);
}
