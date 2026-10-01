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
.tab.active { color: var(--sw-primary); border-bottom-color: var(--sw-primary); }
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
  padding: 7px 14px; border: 1px solid var(--sw-border);
  background: var(--sw-card); color: var(--sw-text);
  border-radius: 999px; cursor: pointer; font: inherit; font-size: 14px; font-weight: 500;
  transition: all 0.15s;
}
.btn:hover:not(:disabled) { border-color: var(--sw-primary); color: var(--sw-primary); }
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.btn.primary { background: var(--sw-primary); color: #fff; border-color: var(--sw-primary); }
.btn.primary:hover:not(:disabled) { filter: brightness(1.1); color: #fff; }
.btn.danger { color: var(--sw-danger); border-color: var(--sw-danger); background: transparent; }
.btn.danger:hover:not(:disabled) { background: var(--sw-danger); color: #fff; }
.btn.ghost { border-color: transparent; background: transparent; color: var(--sw-primary); padding-inline: 8px; }
.btn.small { padding: 4px 10px; font-size: 12px; }
.link-btn { background: none; border: none; color: var(--sw-primary); cursor: pointer; font: inherit; font-size: 13px; padding: 4px 0; text-decoration: underline; }
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
.field-error { color: var(--sw-danger); font-size: 12px; margin-top: 4px; }
.field input[aria-invalid="true"] { border-color: var(--sw-danger); }
.modal [hidden] { display: none !important; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.progress-wrap { height: 8px; background: var(--sw-border); border-radius: 999px; overflow: hidden; }
.progress-bar { height: 100%; background: var(--sw-primary); border-radius: inherit; transition: width 0.5s linear; }
.pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 500;
  background: var(--sw-border); color: var(--sw-muted); white-space: nowrap;
}
.pill.run { background: rgba(3,169,244,0.15); color: var(--sw-primary); }
.pill.pause { background: rgba(180,83,9,0.15); color: var(--sw-warn); }
.pill.ok { background: rgba(22,163,74,0.15); color: var(--sw-success); }
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
.stepper button:hover { color: var(--sw-primary); }
.stepper-val { min-width: 58px; text-align: center; font-variant-numeric: tabular-nums; font-size: 14px; }
details > summary { cursor: pointer; font-weight: 500; }
.activity-card { display: flex; gap: 12px; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; }
.activity-card details { flex: 1 1 260px; min-width: 0; }
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
.switch { width: 40px; height: 22px; border-radius: 999px; background: var(--sw-border); border: 0; position: relative; cursor: pointer; flex: 0 0 auto; }
.switch::after { content: ""; position: absolute; inset-block-start: 3px; inset-inline-start: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: inset-inline-start .15s; }
.switch[aria-checked="true"] { background: var(--sw-primary); }
.switch[aria-checked="true"]::after { inset-inline-start: 21px; }
.chain { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 14px; }
.chain .sep { color: var(--sw-muted); }
.muted { color: var(--sw-muted); }
bdi { unicode-bidi: isolate; }
.num { text-align: end; }
.num .water { display: block; color: var(--sw-primary); font-size: 12px; }
.badge {
  display: inline-block; margin-inline-start: 6px; padding: 1px 6px;
  border-radius: 4px; font-size: 11px; font-weight: 500;
  background: var(--sw-border); color: var(--sw-muted); vertical-align: middle;
}
.badge.warn { background: rgba(180,83,9,0.15); color: var(--sw-warn); }
.wk-wrap { container-type: inline-size; }
.week { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; }
.wk-day { display: grid; gap: 6px; align-content: start; min-width: 0; padding: 8px; border: 1px solid var(--sw-border); border-radius: 10px; background: var(--sw-bg); }
.wk-day.today { border-color: var(--sw-primary); }
.wk-head { display: flex; justify-content: space-between; align-items: center; gap: 4px; flex-wrap: wrap; }
.wk-head strong { font-weight: 500; font-size: 14px; margin-inline-end: 4px; }
.wk-head .btn { padding: 2px 6px; font-size: 12px; }
.wk-runs { display: flex; flex-direction: column; gap: 6px; }
.wk-run {
  display: grid; gap: 1px; width: 100%; text-align: start; cursor: pointer;
  padding: 6px 8px; border: 1px solid var(--sw-border); border-radius: 8px;
  background: var(--sw-card); color: var(--sw-text); font: inherit; font-size: 13px;
}
.wk-run:hover { border-color: var(--sw-primary); }
.wk-run .t { font-weight: 600; font-variant-numeric: tabular-nums; }
.wk-run .n { overflow-wrap: anywhere; }
.wk-run.past { opacity: 0.55; }
.wk-run.skipped .t, .wk-run.skipped .n { text-decoration: line-through; color: var(--sw-muted); }
.wk-run.rain { border-color: var(--sw-warn); background: rgba(180,83,9,0.07); }
.wk-tag { font-size: 11px; font-weight: 500; color: var(--sw-muted); }
.wk-run.rain .wk-tag, .wk-tag.warn { color: var(--sw-warn); }
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
  background: var(--sw-danger); color: #fff; font-weight: 600;
}
.days { display: flex; gap: 6px; flex-wrap: wrap; }
.day-chip {
  min-width: 44px; height: 36px; padding: 0 8px; border: 1px solid var(--sw-border);
  border-radius: 999px; cursor: pointer; font: inherit; font-size: 13px; font-weight: 500;
  background: var(--sw-card); color: var(--sw-text);
}
.day-chip[aria-pressed="true"] { background: var(--sw-primary); border-color: var(--sw-primary); color: #fff; }
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
  padding: 8px 10px; cursor: pointer;
  border-bottom: 1px solid var(--sw-border);
  display: flex; justify-content: space-between; gap: 10px;
}
.entity-row:last-child { border-bottom: none; }
.entity-row:hover { background: var(--sw-bg); }
.entity-row.selected { background: rgba(3,169,244,0.12); }
.domain {
  font-size: 11px; padding: 2px 6px;
  border-radius: 4px; background: var(--sw-primary);
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
.toast {
  position: fixed; bottom: calc(20px + env(safe-area-inset-bottom, 0px)); inset-inline: 0; margin-inline: auto;
  width: max-content; max-width: calc(100% - 32px);
  padding: 10px 16px; background: var(--sw-text); color: var(--sw-bg);
  border-radius: 999px; font-size: 13px;
  z-index: 200; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.toast.error { background: var(--sw-danger); color: #fff; }
.toast.ok { background: var(--sw-success); color: #fff; }
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
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
`;

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];

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

function daysFromMaskNames(mask) {
  return DAYS.filter((_, i) => mask & DAY_BITS[i]);
}

// Service fields that recreate a stored schedule's repeat rule.
function repeatPayload(s) {
  return s.repeat === "interval"
    ? { every_n_days: s.interval_days, start_date: s.start_date }
    : { days: daysFromMaskNames(s.days_mask) };
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
    this._activityOpen = false;
    this._moreOpen = false;
    this._openGroups = new Set();
  }

  set hass(hass) {
    this._hass = hass;
    const langChanged = this._applyLang();
    if (!this._initialized) this._init();
    else {
      this._syncMenuButton();
      if (langChanged) {
        this._modalRoot.innerHTML = "";
        if (this._state) this._render();
      }
    }
  }

  _applyLang() {
    const h = this._hass;
    const lang = I18N.resolveLang(h);
    const rtl = I18N.isRtl(h, lang);
    const loc = h && h.locale ? [h.locale.language, h.locale.time_format, h.locale.time_zone].join("|") : (h && h.language) || "";
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

  _fo(extra) {
    return Object.assign({ hass: this._hass }, extra || {});
  }

  _fmtDT(ts, opts) { return I18N.fmtDateTime(ts, this._lang, this._fo(opts)); }
  _fmtTime(ts, opts) { return I18N.fmtTime(ts, this._lang, this._fo(opts)); }
  _fmtDate(ts, opts) { return I18N.fmtDate(ts, this._lang, this._fo(opts)); }
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

  _sourceLabel(code) {
    const c = String(code || "");
    if (c.startsWith("cycle:")) {
      const id = c.slice(6).split("|")[0];
      const cycle = ((this._state && this._state.cycles) || []).find(x => x.id === id);
      return this._t("source.cycle", { name: cycle ? cycle.name : id });
    }
    return c && this._t.has("source." + c) ? this._t("source." + c) : c;
  }

  _daysFromMask(mask) {
    if ((mask & 127) === 127) return this._t("sched.every_day");
    const names = DAYS.map((_, i) => i)
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

  _whenNodes(s) {
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
  }

  disconnectedCallback() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer);
      this._refreshTimer = null;
    }
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
    this.addEventListener("focusin", (ev) => {
      const t = ev.target;
      this._editing = !!(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT"));
    });
    this.addEventListener("focusout", () => { this._editing = false; });
    this._refresh();
    this._refreshTimer = setInterval(() => this._refresh(), 5000);
  }

  async _refresh() {
    try {
      this._state = await this._hass.callWS({ type: "schedule_wizard/get_state" });
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
      b.style.width = `${Math.min(100, ((total - remaining) / total) * 100)}%`;
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

  _toast(msg, kind = "") {
    const t = el("div", { class: "toast " + kind, role: "status" }, msg);
    this._applyDir(t);
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2800);
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

  _confirmDelete(message, service, data) {
    if (!confirm(message)) return;
    this._callService(service, data);
  }

  _render() {
    const app = this.querySelector("#app");
    if (!app || !this._state) return;
    this._applyDir(this);
    this._applyDir(app);
    app.innerHTML = "";

    app.appendChild(el("div", { class: "topbar" }, [
      el("div", { class: "title-wrap" }, [this._menuButton(), el("h1", {}, "Schedule Wizard")]),
    ]));

    const tabs = el("div", { class: "tabs", role: "tablist" });
    ["home", "zones", "programs", "settings"].forEach((key) => {
      const selected = this._tab === key;
      tabs.appendChild(el("button", {
        class: "tab" + (selected ? " active" : ""),
        role: "tab",
        "aria-selected": selected ? "true" : "false",
        onClick: () => { this._tab = key; this._view = null; this._render(); },
      }, this._t("tab." + key)));
    });
    app.appendChild(tabs);

    const content = el("div", { role: "tabpanel" });
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
          onClick: () => {
            if (!confirm(this._t("week.skip_day_confirm", { day: info.full }))) return;
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
    const close = () => { this._modalRoot.innerHTML = ""; this._editing = false; };
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

    const actions = [el("button", { class: "btn", onClick: close }, this._t("common.close"))];
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
    overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });
    overlay.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
    this._modalRoot.innerHTML = "";
    this._applyDir(overlay);
    this._modalRoot.appendChild(overlay);
    actions[actions.length - 1].focus();
  }

  _statusCard() {
    const st = this._state;
    const now = st.now;
    const active = st.active || [];
    const cycles = st.active_cycles || [];
    const soaking = st.soaking || [];
    const valves = st.valves || [];
    const rainUntil = parseInt(st.rain_delay_until || 0, 10) || 0;
    const card = el("section", { class: "card status", "aria-live": "polite" });

    let pill;
    let title;
    const subs = [];
    const actions = [];
    let progress = null;
    let extra = null;

    const stopAllBtn = () => el("button", {
      class: "btn danger",
      onClick: () => {
        if (!confirm(this._t("dash.stop_all_confirm"))) return;
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
      const wk = this._weekRuns().find(r => r.start > now && r.skip !== "skipped_manual");
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

    let nextLine;
    if (v.next_run && parseInt(v.next_run.fires_at, 10)) {
      nextLine = this._t("home.next_zone", { when: this._fmtWhen(parseInt(v.next_run.fires_at, 10)), n: v.next_run.duration_min });
    } else {
      nextLine = this._t("home.no_schedule");
    }
    if (v.rain_exempt) nextLine += " · " + this._t("zone.indoor_suffix");

    const card = el("article", { class: "card zone" + (active ? " running" : ""), "data-entity": id }, [
      el("div", { class: "zone-head" }, [
        el("strong", {}, [iso(v.label), v.enabled ? "" : " " + this._t("common.disabled_tag")]),
        pill,
      ]),
      el("div", { class: "sub small" }, nextLine),
    ]);

    if (active) {
      const remaining = Math.max(0, active.ends_at - now);
      const total = Math.max(1, active.ends_at - active.started_at);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      card.appendChild(el("div", { class: "progress-wrap" }, el("div", { class: "progress-bar", style: `width:${pct}%` })));
      card.appendChild(el("div", { class: "actions" }, [
        el("button", { class: "btn danger", onClick: () => this._callService("stop_valve", { entity_id: id }) }, this._t("common.stop")),
        el("span", { class: "muted small" }, this._tn("run.left", { time: el("span", { "data-left": id }, fmtRemaining(remaining)) })),
      ]));
    } else if (soak) {
      const ownerCycle = soak.owner === "cycle"
        ? (st.active_cycles || []).find(c => c.current_entity === id)
        : null;
      card.appendChild(el("div", { class: "actions" }, [
        ownerCycle
          ? el("button", { class: "btn danger", onClick: () => this._callService("stop_cycle", { cycle_id: ownerCycle.cycle_id }) }, this._t("run.stop_cycle"))
          : el("button", { class: "btn danger", onClick: () => this._callService("stop_valve", { entity_id: id }) }, this._t("common.stop")),
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
          el("button", { type: "button", "aria-label": this._t("zone.less"), title: this._t("zone.less"), onClick: () => change(-1) }, "−"),
          val,
          el("button", { type: "button", "aria-label": this._t("zone.more"), title: this._t("zone.more"), onClick: () => change(1) }, "+"),
        ]),
        el("button", {
          class: "btn primary",
          onClick: () => this._callService("run_valve", { entity_id: id, duration_minutes: cur() }),
        }, this._t("zone.water_now")),
      ]));
    }
    return card;
  }

  _activityCard() {
    const st = this._state;
    const det = el("details", { class: "activity" });
    if (this._activityOpen) det.open = true;
    det.addEventListener("toggle", () => { this._activityOpen = det.open; });
    det.appendChild(el("summary", {}, this._t("dash.recent")));
    const history = st.history || [];
    if (!history.length) {
      det.appendChild(el("div", { class: "empty" }, this._t("dash.no_history")));
    } else {
      const ul = el("ul", { class: "log" });
      this._groupHistory(history.slice(0, 30)).slice(0, 14).forEach(g => ul.appendChild(this._activityItem(g)));
      det.appendChild(ul);
    }
    return el("div", { class: "card activity-card" }, [
      det,
      el("button", { class: "btn", onClick: () => { this._view = "reports"; this._render(); } }, this._t("home.reports")),
    ]);
  }

  _activitySentence(h) {
    const cycle = (this._state.cycles || []).find(c => c.id === h.valve_entity_id);
    const name = cycle ? iso(cycle.name) : this._valveName(h.valve_entity_id);
    if (!cycle && h.status === "completed") return this._tn("home.act_watered", { zone: name, n: h.duration_min });
    return this._tn("home.act_status", { name, status: this._statusLabel(h.status) });
  }

  _activityItem(g) {
    const h = g.entry;
    const left = el("div", { style: "min-width:0;" }, [
      el("div", {}, [...this._activitySentence(h), h.liters > 0 ? " · " + this._fmtLiters(h.liters) : null]),
      el("div", { class: "sub" }, this._sourceLabel(h.source)),
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
    return el("li", {}, [
      left,
      el("span", { class: "when" }, this._fmtDT(h.ts, { weekday: "short", hour: "numeric", minute: "2-digit" })),
    ]);
  }

  _groupHistory(history) {
    const cyclesById = Object.fromEntries((this._state.cycles || []).map(c => [c.id, c]));
    const used = new Set();
    const out = [];
    for (let i = 0; i < history.length; i++) {
      if (used.has(i)) continue;
      const h = history[i];
      if (cyclesById[h.valve_entity_id]) {
        const cycleId = h.valve_entity_id;
        const children = [];
        for (let j = i + 1; j < history.length; j++) {
          if (used.has(j)) continue;
          const c = history[j];
          if (cyclesById[c.valve_entity_id] && c.valve_entity_id === cycleId) break;
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
    const week = stats.runs_7d
      ? this._t("valves.week", { runs: stats.runs_7d, min: stats.total_min_7d })
      : this._t("valves.week_none");
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

    const card = el("article", { class: "card" }, [
      el("div", { class: "admin-head" }, [
        el("div", { style: "min-width:0;" }, [
          el("div", { class: "name" }, [iso(v.label), v.enabled ? "" : " " + this._t("common.disabled_tag"), ...badges]),
          el("div", { class: "sub" }, joinParts([ltr(v.entity_id), this._t("zones.min_per_run", { n: v.default_duration_min })])),
          el("div", { class: "sub" }, lastLine + " • " + week),
          (v.water_total_l || 0) > 0 ? el("div", { class: "sub" }, this._t("valves.water_used", { amount: this._fmtLiters(v.water_total_l) })
            + (v.avg_lpm > 0 ? " · " + this._t("valves.usually_lpm", { lpm: this._fmtLpm(v.avg_lpm) }) : "")) : null,
        ]),
        el("div", { class: "actions" }, [
          el("button", { class: "btn small", onClick: () => this._openValveModal(v) }, this._t("zones.edit")),
          el("button", {
            class: "btn danger small",
            onClick: () => this._confirmDelete(this._t("valves.delete_confirm", { name: v.label }), "remove_valve", { entity_id: v.entity_id }),
          }, this._t("common.delete")),
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
    const toggle = el("button", {
      class: "switch",
      role: "switch",
      "aria-checked": s.enabled ? "true" : "false",
      "aria-label": this._t("common.enabled"),
      title: this._t(s.enabled ? "common.disable" : "common.enable"),
      onClick: () => this._callService("update_schedule", { schedule_id: s.id, enabled: !s.enabled }),
    });
    const skipped = this._nextSkippedDay(s);
    let skipBtn = null;
    if (skipped) {
      skipBtn = el("button", {
        class: "btn small",
        onClick: () => this._callService("unskip", { schedule_id: s.id, date: skipped }),
      }, this._t("common.undo"));
    } else if (this._schedActive(s)) {
      skipBtn = el("button", {
        class: "btn small",
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
        el("button", { class: "btn small", onClick: () => this._openScheduleModal(s) }, this._t("common.edit")),
        el("button", {
          class: "btn danger small",
          onClick: () => this._confirmDelete(this._t("sched.delete_confirm"), "remove_schedule", { schedule_id: s.id }),
        }, this._t("common.delete")),
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

    const labelInput = el("input", { type: "text", value: label, placeholder: this._t("valves.label_ph") });
    labelInput.addEventListener("input", () => { label = labelInput.value; });

    const durInput = el("input", { type: "number", min: "1", max: "1440", value: String(duration) });
    durInput.addEventListener("input", () => { duration = parseInt(durInput.value, 10) || 10; });

    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const rainExemptInput = el("input", { type: "checkbox" });
    rainExemptInput.checked = !!(existing && existing.rain_exempt);

    const search = el("input", { type: "text", placeholder: this._t("valves.search_ph") });
    const picker = el("div", { class: "entity-picker" });
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
        const row = el("div", { class: "entity-row" + (chosen === e.entity_id ? " selected" : "") }, [
          el("div", {}, [
            el("div", { style: "font-weight:600" }, iso(e.friendly_name)),
            el("div", { class: "muted", style: "font-size:12px" }, ltr(e.entity_id)),
          ]),
          el("span", { class: "domain" }, e.domain),
        ]);
        row.addEventListener("click", () => {
          chosen = e.entity_id;
          if (!label.trim()) { label = e.friendly_name; labelInput.value = label; }
          renderPicker();
        });
        picker.appendChild(row);
      });
    };
    search.addEventListener("input", renderPicker);
    renderPicker();

    const soakRunInput = el("input", { type: "number", min: "0", max: "1440", value: String(existing ? (existing.soak_run_min || 0) : 0) });
    const soakPauseInput = el("input", { type: "number", min: "0", max: "1440", value: String(existing ? (existing.soak_pause_min || 0) : 0) });
    const vMoistEntity = el("input", { type: "text", dir: "ltr", placeholder: "sensor.zone_moisture", value: String((existing && existing.moisture_entity) || "") });
    const vMoistAttr = el("input", { type: "text", placeholder: this._t("common.moisture_attr_ph"), value: String((existing && existing.moisture_attribute) || "") });
    const vMoistThrRaw = (existing && existing.moisture_threshold !== null && existing.moisture_threshold !== undefined) ? String(existing.moisture_threshold) : "";
    const vMoistThreshold = el("input", { type: "number", min: "0", max: "100", step: "0.5", value: vMoistThrRaw });

    const flowRateRaw = (existing && existing.flow_rate_lpm !== null && existing.flow_rate_lpm !== undefined) ? String(existing.flow_rate_lpm) : "";
    const flowRateInput = el("input", { type: "number", min: "0", max: "10000", step: "any", inputmode: "decimal", value: flowRateRaw });

    const hasAdvanced = !!(existing && ((existing.soak_run_min || 0) > 0 || (existing.soak_pause_min || 0) > 0 || existing.moisture_entity || flowRateRaw));
    const advBody = el("div", { style: hasAdvanced ? "" : "display:none;" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("valves.flow_rate")), flowRateInput]),
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
      el("label", { class: "field" }, [el("span", {}, this._t("valves.label")), labelInput]),
      el("label", { class: "field" }, [el("span", {}, this._t("valves.search")), search, picker]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, this._t("valves.default_duration")), durInput]),
        el("label", { class: "field" }, [el("span", {}, this._t("common.enabled")), enabledInput]),
      ]),
      el("label", { class: "field" }, [el("span", {}, this._t("valves.indoor")), rainExemptInput]),
      el("div", { class: "field", style: "padding-top:10px;border-top:1px solid var(--sw-border);" }, [advToggle]),
      advBody,
    ];

    this._showModal(this._t(existing ? "valves.edit_title" : "valves.add_title"), fields, async () => {
      if (!chosen) { this._toast(this._t("valves.pick_entity"), "error"); return false; }
      if (!label.trim()) { this._toast(this._t("valves.label_required"), "error"); return false; }
      const clampMin = (input) => Math.min(1440, Math.max(0, parseInt(input.value, 10) || 0));
      const thrRaw = vMoistThreshold.value.trim();
      const thr = thrRaw === "" ? null : parseFloat(thrRaw);
      const flowRaw = flowRateInput.value.trim();
      const flowRate = flowRaw === "" ? null : parseFloat(flowRaw);
      if (flowRateInput.validity.badInput || (flowRaw !== "" && (isNaN(flowRate) || flowRate <= 0 || flowRate > 10000))) {
        this._toast(this._t("valves.flow_rate_invalid"), "error");
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
            time: s.time_hhmm,
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

    const actions = [];
    if (!ac) {
      actions.push(el("button", { class: "btn primary small", onClick: () => this._callService("run_cycle", { cycle_id: c.id }) }, this._t("plans.run_now")));
    } else {
      actions.push(ac.paused
        ? el("button", { class: "btn primary small", onClick: () => this._callService("resume_cycle", { cycle_id: c.id }) }, this._t("cycle.resume"))
        : el("button", { class: "btn small", onClick: () => this._callService("pause_cycle", { cycle_id: c.id }) }, this._t("cycle.pause")));
      actions.push(el("button", { class: "btn danger small", onClick: () => this._callService("stop_cycle", { cycle_id: c.id }) }, this._t("common.stop")));
    }
    actions.push(
      el("button", { class: "btn small", onClick: () => this._openCycleModal(c) }, this._t("common.edit")),
      el("button", { class: "btn small", onClick: () => this._callService("update_cycle", { cycle_id: c.id, enabled: !c.enabled }) }, this._t(c.enabled ? "common.disable" : "common.enable")),
      el("button", {
        class: "btn danger small",
        onClick: () => this._confirmDelete(this._t("cycles.delete_confirm", { name: c.name }), "remove_cycle", { cycle_id: c.id }),
      }, this._t("common.delete")),
    );

    const chain = el("div", { class: "chain" });
    steps.forEach((s, i) => {
      if (i) chain.appendChild(this._chainSep());
      chain.appendChild(el("span", {}, [this._valveName(s.entity_id), " (" + this._t("unit.min", { n: s.duration_min }) + ")"]));
    });

    const card = el("article", { class: "card" }, [
      el("div", { class: "admin-head" }, [
        el("div", { style: "min-width:0;" }, [
          el("div", { class: "name" }, head),
          statusLine ? el("div", { class: "sub" }, statusLine) : null,
        ]),
        pill,
      ]),
    ]);
    const body = el("div", { class: "admin-body" });
    const times = (st.schedules || []).filter(s => s.cycle_id === c.id);
    times.forEach(s => body.appendChild(this._schedRow(s, false, c.name)));
    if (!times.length) body.appendChild(el("div", { class: "muted small" }, this._t("plans.no_times")));
    body.appendChild(el("div", {}, el("button", {
      class: "btn ghost",
      onClick: () => this._openScheduleModal(null, { kind: "cycle", id: c.id }),
    }, this._t("zones.add_time"))));
    body.appendChild(chain);
    body.appendChild(el("div", { class: "sub" }, this._t("plans.summary", { steps: steps.length, min: totalMin })));
    body.appendChild(el("div", { class: "actions" }, actions));
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

    const nameInput = el("input", { type: "text", value: name, placeholder: this._t("cycles.name_ph") });
    nameInput.addEventListener("input", () => { name = nameInput.value; });

    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const stepsWrap = el("div");
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
          renderSteps();
        },
      }, this._t("cycles.add_step")));
    };
    renderSteps();

    const fields = [
      el("label", { class: "field" }, [el("span", {}, this._t("cycles.name")), nameInput]),
      el("div", { class: "field" }, [el("span", {}, this._t("cycles.steps")), stepsWrap]),
      el("label", { class: "field" }, [el("span", {}, this._t("common.enabled")), enabledInput]),
    ];

    this._showModal(this._t(existing ? "cycles.edit_title" : "cycles.add_title"), fields, async () => {
      if (!name.trim()) { this._toast(this._t("cycles.name_required"), "error"); return false; }
      if (!steps.length) { this._toast(this._t("cycles.one_step"), "error"); return false; }
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
    const durInput = el("input", { type: "number", min: "1", max: "1440", value: String(duration) });
    durInput.addEventListener("input", () => { duration = parseInt(durInput.value, 10) || 10; });
    const renderTargetField = () => {
      targetFieldHost.innerHTML = "";
      durRow.innerHTML = "";
      if (targetKind === "cycle") {
        targetFieldHost.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.cycle")), cycleSel]));
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.time")), timeInput]));
      } else {
        targetFieldHost.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.valve")), valveSel]));
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.time")), timeInput]));
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("sched.duration")), durInput]));
      }
    };
    renderTargetField();

    const nameInput = el("input", { type: "text", value: name, placeholder: this._t("common.optional") });
    nameInput.addEventListener("input", () => { name = nameInput.value; });

    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

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

    const days = el("div", { class: "days", role: "group", "aria-describedby": daysErr.id });
    DAYS.forEach((_, i) => {
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
      const n = intervalValue();
      const start = startValue();
      const hhmm = /^\d{2}:\d{2}$/.test(String(timeInput.value)) ? timeInput.value : null;
      if (n === null || !start || !hhmm) return;
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
      const when = el("span", {}, [
        I18N.fmtDate(ts, this._lang, { hass: this._hass, timeZone: "UTC", weekday: "short", month: "short", day: "numeric" }),
        " ", ltr(hhmm),
      ]);
      firstRunLine.append(...this._tn(key, { when, n, time: ltr(hhmm) }));
    };
    intervalInput.addEventListener("input", () => { if (intervalValue() !== null) setErr(intervalErr, intervalInput, ""); updateFirstRun(); });
    startInput.addEventListener("input", () => { if (startValue()) setErr(startErr, startInput, ""); updateFirstRun(); });
    timeInput.addEventListener("input", updateFirstRun);
    const daysField = el("div", { class: "field" }, [el("span", {}, this._t("sched.days")), days, daysErr]);
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
        if (/every_n_days/.test(msg)) setErr(intervalErr, intervalInput, intervalErrText());
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
    const condWrap = el("div");
    const renderConditions = () => {
      condWrap.innerHTML = "";
      conditions.forEach((c, idx) => {
        const entInput = el("input", { type: "text", dir: "ltr", placeholder: "sensor.example", value: c.entity_id });
        entInput.addEventListener("input", () => { c.entity_id = entInput.value; });
        const attrInput = el("input", { type: "text", placeholder: this._t("sched.attr_ph"), value: c.attribute });
        attrInput.addEventListener("input", () => { c.attribute = attrInput.value; });
        const opSel = el("select", {});
        OPERATORS.forEach(([val, lbl]) => {
          const opt = el("option", { value: val }, lbl);
          if (val === c.operator) opt.selected = true;
          opSel.appendChild(opt);
        });
        opSel.addEventListener("change", () => { c.operator = opSel.value; });
        const valInput = el("input", { type: "text", placeholder: this._t("sched.value_ph"), value: c.value });
        valInput.addEventListener("input", () => { c.value = valInput.value; });
        condWrap.appendChild(el("div", { class: "cond-row" }, [
          entInput, attrInput, opSel, valInput,
          el("button", {
            class: "btn danger small",
            type: "button",
            title: this._t("sched.remove_condition"),
            "aria-label": this._t("sched.remove_condition"),
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
      durRow,
      el("label", { class: "field" }, [el("span", {}, this._t("common.name")), nameInput]),
      el("div", { class: "field" }, [el("span", {}, this._t("sched.conditions")), condWrap]),
      el("label", { class: "field" }, [el("span", {}, this._t("common.enabled")), enabledInput]),
    ];

    this._showModal(this._t(existing ? "sched.edit_title" : "sched.add_title"), fields, async () => {
      const rep = repeatFields();
      if (!rep) return false;
      const conds = collectConditions();
      if (existing) {
        return await submit("update_schedule", {
          schedule_id: existing.id,
          name,
          time,
          duration_minutes: targetKind === "valve" ? duration : 1,
          ...rep,
          enabled,
          conditions: conds,
        });
      }
      const base = {
        time,
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

  // ---------- Setup wizard ----------

  _openWizard() {
    const st = this._state;
    const t = this._t;
    const registered = new Map((st.valves || []).map(v => [v.entity_id, v]));
    const ents = st.controllable || [];
    const friendly = (id) => { const e = ents.find(x => x.entity_id === id); return e ? e.friendly_name : id; };
    const isNew = (id) => !registered.has(id);
    const wz = {
      idx: 0, picked: [], names: {}, mins: {}, mask: DAY_BITS[0] | DAY_BITS[2] | DAY_BITS[4],
      time: "06:00", mode: "sequence", plan: "", planTouched: false, search: "", saving: false,
    };
    const nameOf = (id) => (isNew(id) ? (wz.names[id] ?? friendly(id)) : registered.get(id).label);
    const minOf = (id) => wz.mins[id] ?? (registered.has(id) ? registered.get(id).default_duration_min : 10);
    const defaultPlan = () => t((parseInt(wz.time, 10) || 0) < 12 ? "wiz.plan_morning" : "wiz.plan_evening");
    const planName = () => (wz.planTouched ? wz.plan : defaultPlan()).trim();
    const stepKeys = () => [
      "pick",
      ...(wz.picked.some(isNew) ? ["name"] : []),
      "when",
      ...(wz.picked.length > 1 ? ["order"] : []),
      "check",
    ];
    const TITLES = { pick: "wiz.t_pick", name: "wiz.t_name", when: "wiz.t_when", order: "wiz.t_order", check: "wiz.t_check" };
    const valid = (key) => {
      if (key === "pick") return wz.picked.length > 0;
      if (key === "name") return wz.picked.filter(isNew).every(id => String(nameOf(id)).trim());
      if (key === "when") return !!(wz.mask & 127) && /^\d{2}:\d{2}$/.test(wz.time);
      return !!planName();
    };

    const modal = el("div", { class: "modal wizard", role: "dialog", "aria-modal": "true", "aria-labelledby": "sw-wiz-title" });
    const head = el("div", { class: "wiz-head" });
    const body = el("div", { class: "wiz-body" });
    const foot = el("div", { class: "wiz-foot" });
    modal.append(head, body, foot);
    const overlay = el("div", { class: "modal-overlay" }, modal);
    const close = () => { this._modalRoot.innerHTML = ""; this._editing = false; };
    overlay.addEventListener("click", (e) => { if (e.target === overlay && !wz.saving) close(); });
    overlay.addEventListener("keydown", (e) => { if (e.key === "Escape" && !wz.saving) close(); });

    let nextBtn = null;
    const refreshNext = () => { if (nextBtn) nextBtn.disabled = wz.saving || !valid(stepKeys()[wz.idx]); };

    const drawHead = () => {
      const keys = stepKeys();
      if (wz.idx >= keys.length) wz.idx = keys.length - 1;
      head.innerHTML = "";
      head.appendChild(el("div", { class: "wiz-steps", "aria-hidden": "true" }, keys.map((_, i) => el("i", { class: i <= wz.idx ? "on" : "" }))));
      head.appendChild(el("div", { class: "muted small" }, t("wiz.step_of", { n: wz.idx + 1, total: keys.length })));
      head.appendChild(el("h3", { id: "sw-wiz-title" }, t(TITLES[keys[wz.idx]])));
    };

    const minutesStepper = (id) => {
      const val = el("span", { class: "stepper-val", "aria-live": "polite" }, t("unit.min", { n: minOf(id) }));
      const change = (dir) => { wz.mins[id] = stepMinutes(minOf(id), dir); val.textContent = t("unit.min", { n: wz.mins[id] }); };
      return el("span", { class: "stepper" }, [
        el("button", { type: "button", "aria-label": t("zone.less"), title: t("zone.less"), onClick: () => change(-1) }, "−"),
        val,
        el("button", { type: "button", "aria-label": t("zone.more"), title: t("zone.more"), onClick: () => change(1) }, "+"),
      ]);
    };

    const planNameField = () => {
      const input = el("input", { type: "text", value: planName(), placeholder: t("cycles.name_ph") });
      input.addEventListener("input", () => { wz.plan = input.value; wz.planTouched = true; refreshNext(); });
      return el("label", { class: "field", style: "margin:0;" }, [el("span", {}, t("wiz.plan_name")), input]);
    };

    const bodyPick = () => {
      body.appendChild(el("p", { class: "muted" }, t("wiz.pick_hint")));
      const search = el("input", { type: "search", value: wz.search, placeholder: t("valves.search_ph"), "aria-label": t("valves.search") });
      const listHost = el("div", { class: "wiz-list" });
      const checkRow = (e) => {
        const cb = el("input", { type: "checkbox" });
        cb.checked = wz.picked.includes(e.entity_id);
        cb.addEventListener("change", () => {
          if (cb.checked) { if (!wz.picked.includes(e.entity_id)) wz.picked.push(e.entity_id); }
          else wz.picked = wz.picked.filter(x => x !== e.entity_id);
          drawHead();
          refreshNext();
        });
        const reg = registered.get(e.entity_id);
        return el("label", { class: "check" }, [
          cb,
          el("span", { style: "min-width:0;" }, [
            el("div", {}, iso(reg ? reg.label : e.friendly_name)),
            el("div", { class: "sub" }, ltr(e.entity_id)),
          ]),
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

    const bodyName = () => {
      body.appendChild(el("p", { class: "muted" }, t("wiz.name_hint")));
      wz.picked.filter(isNew).forEach(id => {
        const input = el("input", { type: "text", value: nameOf(id), placeholder: t("valves.label_ph") });
        input.addEventListener("input", () => { wz.names[id] = input.value; refreshNext(); });
        body.appendChild(el("label", { class: "field", style: "margin:0;" }, [
          el("span", {}, [iso(friendly(id)), " (", ltr(id), ")"]),
          input,
        ]));
      });
    };

    const bodyWhen = () => {
      const days = el("div", { class: "days" });
      DAYS.forEach((_, i) => {
        const chip = el("button", {
          type: "button", class: "day-chip",
          "aria-pressed": (wz.mask & DAY_BITS[i]) ? "true" : "false",
          title: I18N.weekdayLong(i, this._lang, this._fo()),
        }, I18N.weekdayShort(i, this._lang, this._fo()));
        chip.addEventListener("click", () => {
          wz.mask ^= DAY_BITS[i];
          chip.setAttribute("aria-pressed", (wz.mask & DAY_BITS[i]) ? "true" : "false");
          refreshNext();
        });
        days.appendChild(chip);
      });
      const timeInput = el("input", { type: "time", value: wz.time, required: true });
      timeInput.addEventListener("input", () => { wz.time = timeInput.value; refreshNext(); });
      const mins = el("div", { class: "list" });
      wz.picked.forEach(id => mins.appendChild(el("div", { class: "zmin" }, [iso(nameOf(id)), minutesStepper(id)])));
      body.append(
        el("div", { class: "field", style: "margin:0;" }, [el("span", {}, t("wiz.which_days")), days]),
        el("label", { class: "field", style: "margin:0;" }, [el("span", {}, t("wiz.start_time")), timeInput]),
        el("div", { class: "field", style: "margin:0;" }, [el("span", {}, t("wiz.minutes_per_zone")), mins]),
      );
    };

    const bodyOrder = () => {
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
        el("span", {}, this._whenNodes({ days_mask: wz.mask, time_hhmm: wz.time })),
        zones,
        el("span", { class: "muted" }, t(ids.length > 1 ? (seq ? "wiz.mode_sequence" : "wiz.mode_together") : "wiz.mode_single")),
        el("span", { class: "muted" }, t("wiz.total", { n: total })),
      ]);
      if ((st.options || {}).rain_entity) summary.appendChild(el("span", { class: "muted" }, t("wiz.rain_note")));
      body.appendChild(summary);
      if (ids.length === 1) body.appendChild(planNameField());
    };

    const save = async () => {
      wz.saving = true;
      refreshNext();
      nextBtn.textContent = t("wiz.saving");
      const ids = wz.picked.slice();
      const days = daysFromMaskNames(wz.mask);
      const name = planName();
      const time = wz.time;
      const step = async (label, fn) => {
        try { return await fn(); } catch (e) { throw { label, error: e }; }
      };
      const svc = (service, data) => this._hass.callService("schedule_wizard", service, data);
      try {
        for (const id of ids) {
          if (!isNew(id)) continue;
          await step(t("wiz.fail_zone", { zone: nameOf(id) }), () => svc("add_valve", {
            entity_id: id, label: String(nameOf(id)).trim(), default_duration_minutes: minOf(id), enabled: true,
          }));
        }
        if (ids.length === 1) {
          await step(t("wiz.fail_schedule"), () => svc("add_schedule", {
            valve_entity_id: ids[0], time, days, duration_minutes: minOf(ids[0]), name, enabled: true,
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
            cycle_id: cycleId, time, days, duration_minutes: 1, name, enabled: true,
          }));
        } else {
          for (const id of ids) {
            await step(t("wiz.fail_zone_time", { zone: nameOf(id) }), () => svc("add_schedule", {
              valve_entity_id: id, time, days, duration_minutes: minOf(id), name, enabled: true,
            }));
          }
        }
      } catch (err) {
        wz.saving = false;
        const e = err && err.error ? err.error : err;
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
      ({ pick: bodyPick, name: bodyName, when: bodyWhen, order: bodyOrder, check: bodyCheck })[key]();
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
      const first = body.querySelector("input, button");
      if (first) first.focus();
    };

    this._modalRoot.innerHTML = "";
    this._applyDir(overlay);
    this._modalRoot.appendChild(overlay);
    draw();
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
      el("p", { class: "muted small", style: "margin:0;" }, this._t("reports.based_on", { n: history.length })),
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
    const chartCard = el("div", { class: "card" }, [el("h2", {}, this._t("reports.chart_title"))]);
    const chart = el("div", {
      style: "display:flex;align-items:flex-end;gap:2px;height:120px;border-bottom:1px solid var(--sw-border);padding-bottom:4px;",
    });
    dayValues.forEach((v, i) => {
      const h = Math.round((v / maxVal) * 110);
      chart.appendChild(el("div", {
        title: this._t("reports.bar_title", { date: dayLabels[i], n: v }),
        style: `flex:1;height:${h}px;min-width:6px;background:var(--sw-primary);border-radius:2px 2px 0 0;`,
      }));
    });
    chartCard.appendChild(chart);
    chartCard.appendChild(el("div", { style: "display:flex;justify-content:space-between;font-size:11px;color:var(--sw-muted);margin-top:4px;" }, [
      el("span", {}, dayLabels[0]),
      el("span", {}, dayLabels[Math.floor(dayValues.length / 2)]),
      el("span", {}, dayLabels[dayValues.length - 1]),
    ]));
    root.appendChild(chartCard);

    const valveTable = el("div", { class: "card" }, [el("h2", {}, this._t("reports.per_valve"))]);
    if (!valves.length) {
      valveTable.appendChild(el("div", { class: "empty" }, this._t("reports.no_valves")));
    } else {
      valveTable.appendChild(el("div", {
        style: "display:grid;grid-template-columns:1.4fr repeat(3, 1fr);gap:6px;font-size:12px;font-weight:600;color:var(--sw-muted);padding:6px 4px;border-bottom:1px solid var(--sw-border);",
      }, [
        el("span", {}, this._t("sched.valve")),
        el("span", { class: "num" }, this._t("reports.col_7d")),
        el("span", { class: "num" }, this._t("reports.col_30d")),
        el("span", { class: "num" }, this._t("reports.total")),
      ]));
      valves.forEach(v => {
        const s = valveStats[v.entity_id] || { runs_7d: 0, min_7d: 0, runs_30d: 0, min_30d: 0, runs_total: 0, min_total: 0 };
        const w = water[v.entity_id] || { d7: 0, d30: 0 };
        valveTable.appendChild(el("div", {
          style: "display:grid;grid-template-columns:1.4fr repeat(3, 1fr);gap:6px;font-size:13px;padding:6px 4px;border-bottom:1px solid var(--sw-border);",
        }, [
          el("span", {}, iso(v.label)),
          ...[
            [s.runs_7d, s.min_7d, w.d7],
            [s.runs_30d, s.min_30d, w.d30],
            [s.runs_total, s.min_total, Number(v.water_total_l) || 0],
          ].map(([runs, min, l]) => el("span", { class: "num" }, [
            this._t("reports.runs_min", { runs, min }),
            hasWater ? el("span", { class: "water" }, this._fmtLiters(l)) : null,
          ])),
        ]));
      });
    }
    root.appendChild(valveTable);

    if (cycles.length) {
      const cycleTable = el("div", { class: "card" }, [el("h2", {}, this._t("reports.per_cycle"))]);
      cycleTable.appendChild(el("div", {
        style: "display:grid;grid-template-columns:1.5fr repeat(3, 0.7fr) 0.7fr;gap:6px;font-size:12px;font-weight:600;color:var(--sw-muted);padding:6px 4px;border-bottom:1px solid var(--sw-border);",
      }, [
        el("span", {}, this._t("sched.cycle")),
        el("span", { class: "num" }, this._t("reports.done")),
        el("span", { class: "num" }, this._t("reports.cancelled")),
        el("span", { class: "num" }, this._t("reports.skipped")),
        el("span", { class: "num" }, this._t("reports.total")),
      ]));
      cycles.forEach(c => {
        const s = cycleStats[c.id] || { completed: 0, cancelled: 0, skipped: 0, runs_30d: 0 };
        cycleTable.appendChild(el("div", {
          style: "display:grid;grid-template-columns:1.5fr repeat(3, 0.7fr) 0.7fr;gap:6px;font-size:13px;padding:6px 4px;border-bottom:1px solid var(--sw-border);",
        }, [
          el("span", {}, iso(c.name)),
          el("span", { class: "num", style: "color:var(--sw-success);" }, String(s.completed)),
          el("span", { class: "num", style: "color:var(--sw-warn);" }, String(s.cancelled)),
          el("span", { class: "num", style: "color:var(--sw-muted);" }, String(s.skipped)),
          el("span", { class: "num", style: "font-weight:600;" }, String(s.runs_30d)),
        ]));
      });
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
    const cyclesById = Object.fromEntries((this._state.cycles || []).map(c => [c.id, c.name]));
    const header = ["timestamp", "iso_time", "target_kind", "target_id", "target_label", "duration_min", "source", "status", "note", "liters"];
    const rows = history.map(h => {
      const isCycle = !!cyclesById[h.valve_entity_id];
      const id = h.valve_entity_id || "";
      const label = isCycle ? cyclesById[id] : (valvesById[id] || id);
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
      const s = String(v == null ? "" : v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
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

  // ---------- Settings ----------

  _optGroup(key, title, desc, on, children) {
    const d = el("details", { class: "opt-group" });
    if (this._openGroups.has(key)) d.open = true;
    d.addEventListener("toggle", () => { if (d.open) this._openGroups.add(key); else this._openGroups.delete(key); });
    d.appendChild(el("summary", {}, [
      el("strong", { style: "font-weight:500;" }, title),
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
    const rainEntityInput = el("input", { type: "text", dir: "ltr", placeholder: this._t("settings.rain_entity_ph"), value: String(opts.rain_entity || "") });
    const rainStatesInput = el("input", { type: "text", dir: "ltr", placeholder: "rainy,pouring,snowy,lightning-rainy", value: String(opts.rain_skip_states || "") });
    const rainAttrInput = el("input", { type: "text", placeholder: this._t("settings.rain_attr_ph"), value: String(opts.rain_attribute || "") });
    const rainThresholdInput = el("input", { type: "number", min: "0", max: "100", step: "0.1", value: opts.rain_threshold != null ? String(opts.rain_threshold) : "" });

    // Essentials
    const ess = el("div", { class: "card" }, [el("h2", {}, this._t("set.essentials"))]);
    ess.appendChild(field(this._t("set.rain_using"), rainEntityInput));
    ess.appendChild(el("p", { class: "muted small", style: "margin:-6px 0 12px;" }, this._t("set.rain_using_hint")));

    const availableTargets = this._state.notify_services || [];
    const availableEvents = this._state.notify_events || [];
    const currentTargets = new Set(Array.isArray(opts.notify_targets) ? opts.notify_targets : (opts.notify_targets ? String(opts.notify_targets).split(",").map(s => s.trim()).filter(Boolean) : []));
    const currentEvents = new Set(Array.isArray(opts.notify_events) ? opts.notify_events : (opts.notify_events ? String(opts.notify_events).split(",").map(s => s.trim()).filter(Boolean) : []));

    const targetsWrap = el("div", { class: "check-wrap" });
    if (!availableTargets.length) {
      targetsWrap.appendChild(el("div", { class: "empty", style: "padding:4px;" }, this._t("settings.no_notify")));
    } else {
      availableTargets.forEach(name => {
        const cb = el("input", { type: "checkbox" });
        cb.checked = currentTargets.has(name);
        cb.addEventListener("change", () => { if (cb.checked) currentTargets.add(name); else currentTargets.delete(name); });
        targetsWrap.appendChild(el("label", {}, [cb, ltr(name)]));
      });
    }
    const eventsWrap = el("div", { class: "check-wrap" });
    const eventLabel = (ev) => (this._t.has("event." + ev) ? this._t("event." + ev) : ev);
    availableEvents.forEach(ev => {
      const cb = el("input", { type: "checkbox" });
      cb.checked = currentEvents.has(ev);
      cb.addEventListener("change", () => { if (cb.checked) currentEvents.add(ev); else currentEvents.delete(ev); });
      eventsWrap.appendChild(el("label", {}, [cb, eventLabel(ev)]));
    });
    ess.appendChild(el("div", { class: "field" }, [el("span", {}, this._t("settings.notify_services")), targetsWrap]));
    ess.appendChild(el("div", { class: "field" }, [el("span", {}, this._t("settings.notify_when")), eventsWrap]));
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
        if (!s) { seasonalPreview.appendChild(el("span", { style: "color:var(--sw-danger)" }, this._tn("settings.preview_not_found", { entity: ltr(entityId) }))); return; }
        let temp = null;
        try { temp = parseFloat(attr ? s.attributes[attr] : s.state); } catch {}
        if (temp == null || isNaN(temp)) { seasonalPreview.appendChild(el("span", { style: "color:var(--sw-danger)" }, this._tn("settings.preview_not_numeric", { state: ltr(s.state) }))); return; }
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
          if (!confirm(this._t("settings.webhook_rotate_confirm"))) return;
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

    const more = el("details", { class: "more" });
    if (this._moreOpen) more.open = true;
    more.addEventListener("toggle", () => { this._moreOpen = more.open; });
    more.appendChild(el("summary", {}, this._t("set.more")));
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
          rain_entity: rainEntityInput.value.trim(),
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
        });
        feedback.textContent = this._t("settings.saved_at", {
          time: this._fmtTime(Math.floor(Date.now() / 1000), { hour: "numeric", minute: "2-digit", second: "2-digit" }),
        });
        this._toast(this._t("settings.saved"), "ok");
        setTimeout(() => this._refresh(), 1500);
      } catch (e) {
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
    this._modalRoot.innerHTML = "";
    const modal = el("div", { class: "modal", role: "dialog", "aria-modal": "true" });
    modal.appendChild(el("h3", {}, title));
    fields.forEach((f) => modal.appendChild(f));

    const close = () => { this._modalRoot.innerHTML = ""; this._editing = false; };
    const cancelBtn = el("button", { class: "btn", onClick: close }, this._t("common.cancel"));
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
    overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });
    overlay.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
    this._modalRoot.appendChild(overlay);
  }
}

if (!customElements.get("schedule-wizard-panel")) {
  customElements.define("schedule-wizard-panel", ScheduleWizardPanel);
}
