const I18N = await import(new URL("./i18n.js" + new URL(import.meta.url).search, import.meta.url).href);

const CARD_STYLES = `
:host { display: block; }
.card {
  background: var(--ha-card-background, var(--card-background-color, #fff));
  border-radius: var(--ha-card-border-radius, 12px);
  border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, #e5e7eb));
  padding: 12px 14px;
  color: var(--primary-text-color);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
  box-shadow: var(--ha-card-box-shadow, 0 1px 2px rgba(0,0,0,0.04));
}
.title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
  display: flex; align-items: center; justify-content: space-between;
}
.title h2 { font: inherit; margin: 0; min-width: 0; overflow-wrap: anywhere; }
.title .pill {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--divider-color, #e5e7eb);
  color: var(--secondary-text-color);
}
.pill.ok { background: rgba(22,163,74,0.15); color: #15803d; }
.row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 8px;
  align-items: center;
  padding: 6px 0;
  border-top: 1px solid var(--divider-color, #e5e7eb);
}
.row:first-of-type { border-top: none; }
.name { font-weight: 500; font-size: 14px; overflow-wrap: anywhere; }
.mins { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--secondary-text-color); white-space: nowrap; }
.sub { color: var(--secondary-text-color); font-size: 11px; }
.progress-wrap {
  grid-column: 1 / -1;
  height: 4px;
  background: var(--divider-color, #e5e7eb);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}
.progress-bar {
  height: 100%;
  background: var(--primary-color, #03a9f4);
  transition: width 0.5s linear;
}
input[type="number"] {
  width: 56px; padding: 4px 6px;
  border: 1px solid var(--divider-color); border-radius: 6px;
  background: var(--card-background-color); color: var(--primary-text-color);
  font: inherit;
}
button {
  padding: 4px 10px;
  border: 1px solid var(--divider-color);
  background: var(--card-background-color);
  color: var(--primary-text-color);
  border-radius: 6px; cursor: pointer; font-size: 12px; font-family: inherit;
  transition: all 0.15s;
}
button.run { background: var(--primary-color); color: #fff; border-color: var(--primary-color); }
button.stop { color: var(--error-color, #dc2626); border-color: var(--error-color, #dc2626); }
button:hover:not(:disabled) { filter: brightness(1.1); }
button:disabled { opacity: 0.4; cursor: not-allowed; }
.empty { color: var(--secondary-text-color); font-style: italic; font-size: 13px; padding: 6px 0; }
.active-runs { margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--divider-color); }
.active-runs .name { color: var(--primary-color); }
bdi { unicode-bidi: isolate; }
.error-msg {
  margin-top: 8px; padding: 6px 10px; border-radius: 6px; font-size: 12px;
  background: rgba(220,38,38,0.12); color: var(--error-color, #dc2626);
}
`;

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const k of Object.keys(attrs)) {
    const v = attrs[k];
    if (k === "class") n.className = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2).toLowerCase(), v);
    else if (v === false || v === undefined || v === null) { /* skip */ }
    else if (v === true) n.setAttribute(k, "");
    else n.setAttribute(k, v);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => {
    if (c === null || c === undefined) return;
    n.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  });
  return n;
}

function deepActiveElement() {
  let node = document.activeElement;
  while (node && node.shadowRoot && node.shadowRoot.activeElement) {
    node = node.shadowRoot.activeElement;
  }
  return node;
}

// Focus across re-renders (#41): a control is identified by what it is (tag, label, text) and the zone
// row it sits in, plus its index among equals; its replacement gets focus back after the rebuild.
const FOCUSABLE = "button, input, select, textarea, a[href], [tabindex]";

function rowKey(n) {
  const row = n.closest("[data-entity], [data-soak]");
  return row ? (row.getAttribute("data-entity") || row.getAttribute("data-soak")) : "";
}

function focusDesc(n) {
  const field = n.tagName === "INPUT" || n.tagName === "SELECT" || n.tagName === "TEXTAREA";
  return [
    n.tagName, n.getAttribute("aria-label") || "", n.className || "",
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
  if (!root || !n || !root.contains(n) || !n.matches(FOCUSABLE)) return null;
  const all = focusables(root);
  const pos = all.indexOf(n);
  const row = rowKey(n);
  const inRow = row ? all.filter(x => rowKey(x) === row) : [];
  const rowPos = inRow.indexOf(n);
  const near = (list, i) => [list[i + 1], list[i - 1]].filter(Boolean).map(x => focusId(all, x));
  return { pos, row, rowPos, self: focusId(all, n), rowNear: row ? near(inRow, rowPos) : [], near: near(all, pos) };
}

function restoreFocus(root, key) {
  if (!root || !key) return;
  const all = focusables(root);
  const find = (id) => {
    const same = all.filter(x => focusDesc(x) === id.desc);
    return same[id.nth] || same[0];
  };
  const inRow = key.row ? all.filter(x => rowKey(x) === key.row) : [];
  const target = find(key.self) || key.rowNear.map(find).find(Boolean) ||
    (inRow.length ? inRow[Math.min(key.rowPos, inRow.length - 1)] : null) ||
    key.near.map(find).find(Boolean) || (all.length ? all[Math.min(key.pos, all.length - 1)] : null);
  if (target) target.focus({ preventScroll: true });
}

// State without the fields that change on every poll, to tell a real change from a clock tick.
function stateSig(st) {
  return JSON.stringify(st, (k, v) => (k === "now" || k === "in_seconds" ? undefined : v));
}

// A full rebuild still happens this often while focus is inside, so "in N min" stays current.
const FOCUSED_RERENDER_MS = 60000;

function ltr(text) {
  return el("bdi", { dir: "ltr" }, String(text == null ? "" : text));
}

function iso(text) {
  return el("bdi", {}, String(text == null ? "" : text));
}

function fmtIn(t, secs) {
  const m = Math.max(0, Math.round(secs / 60));
  return m < 60 ? t("time.in_m", { n: m })
    : m < 1440 ? t("time.in_h", { n: Math.round(m / 60) })
      : t("time.in_d", { n: Math.round(m / 1440) });
}

function fmtRemaining(s) {
  if (s <= 0) return "0:00";
  const m = Math.floor(s / 60);
  const r = String(s % 60).padStart(2, "0");
  return `${m}:${r}`;
}

// The running block and the zone list (UX-016): a zone in the running block is not listed again below it.
// An empty `valves` list means every zone, the same as no list.
export function cardSections(state, config) {
  const cfg = config || {};
  const allowed = Array.isArray(cfg.valves) && cfg.valves.length ? new Set(cfg.valves) : null;
  const shown = (id) => !allowed || allowed.has(id);
  const runs = (state.active || []).filter(r => shown(r.entity_id));
  const soaks = (state.soaking || []).filter(s => s.phase === "soaking" &&
    !(state.active || []).some(r => r.entity_id === s.entity_id) && shown(s.entity_id));
  const showActive = cfg.show_active !== false && (runs.length > 0 || soaks.length > 0);
  const inBlock = new Set(showActive ? [...runs, ...soaks].map(x => x.entity_id) : []);
  const valves = (state.valves || []).filter(v => shown(v.entity_id) && !inBlock.has(v.entity_id));
  return { runs, soaks, showActive, valves, anyValves: (state.valves || []).some(v => shown(v.entity_id)) };
}

// ha-form is lazy-loaded by the HA frontend; opening a built-in card's editor loads it.
async function ensureHaForm() {
  if (customElements.get("ha-form")) return;
  try {
    const helpers = window.loadCardHelpers && await window.loadCardHelpers();
    const probe = helpers && await helpers.createCardElement({ type: "entities", entities: [] });
    if (probe && probe.constructor && probe.constructor.getConfigElement) await probe.constructor.getConfigElement();
  } catch (e) {
    // The editor renders as soon as ha-form is defined.
  }
}

const EDITOR_LABELS = {
  title: "card.editor_title",
  valves: "card.editor_zones",
  show_active: "card.editor_show_active",
  show_quick_run: "card.editor_show_quick_run",
};

class ScheduleWizardCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = Object.assign({}, config || {});
    this._draw();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    this._t = I18N.makeT(I18N.resolveLang(hass));
    if (first) this._loadZones();
    this._draw();
  }

  async _loadZones() {
    try {
      const st = await this._hass.callWS({ type: "schedule_wizard/get_state" });
      this._zones = (st.valves || []).map(v => v.entity_id);
    } catch (e) {
      this._zones = null;
    }
    this._draw();
  }

  _schema() {
    const entity = { multiple: true };
    if (this._zones && this._zones.length) entity.include_entities = this._zones;
    return [
      { name: "title", selector: { text: {} } },
      { name: "valves", selector: { entity } },
      { name: "show_active", selector: { boolean: {} } },
      { name: "show_quick_run", selector: { boolean: {} } },
    ];
  }

  _draw() {
    if (!this._config || !this._hass) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (ev) => this._changed(ev));
      this.appendChild(this._form);
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = Object.assign({ show_active: true, show_quick_run: true }, this._config);
    this._form.computeLabel = (field) => (EDITOR_LABELS[field.name] ? this._t(EDITOR_LABELS[field.name]) : field.name);
  }

  _changed(ev) {
    ev.stopPropagation();
    const config = Object.assign({}, this._config, ev.detail.value);
    if (Array.isArray(config.valves) && !config.valves.length) delete config.valves;
    this._config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }));
  }
}

class ScheduleWizardCard extends HTMLElement {
  static async getConfigElement() {
    await ensureHaForm();
    return document.createElement("schedule-wizard-card-editor");
  }

  static getStubConfig() {
    return { title: "Schedule Wizard", show_active: true, show_quick_run: true };
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._state = null;
    this._timer = null;
    this._initialized = false;
    this._quickDur = {};
    this._error = null;
    this._errorTimer = null;
  }

  setConfig(config) {
    this._config = Object.assign({
      title: "Schedule Wizard",
      show_active: true,
      show_quick_run: true,
      valves: null,
    }, config || {});
    if (this._initialized) this._render();
  }

  getCardSize() {
    if (!this._state) return 2;
    const count = (this._state.active?.length || 0) + (this._state.valves?.length || 0);
    return Math.min(8, 1 + Math.ceil(count / 2));
  }

  set hass(hass) {
    this._hass = hass;
    const langChanged = this._applyLang();
    if (!this._initialized) this._init();
    else if (langChanged && this._state) this._render();
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

  _applyDir(node) {
    if (!node) return;
    node.setAttribute("dir", this._rtl ? "rtl" : "ltr");
    node.setAttribute("lang", this._lang);
  }

  _sourceLabel(code) {
    const c = String(code || "");
    if (c.startsWith("cycle:")) {
      const id = c.slice(6).split("|")[0];
      const cycle = ((this._state && this._state.cycles) || []).find(x => x.id === id);
      return this._t("source.cycle", { name: cycle ? cycle.name : this._t("home.deleted_plan") });
    }
    return c && this._t.has("source." + c) ? this._t("source." + c) : c;
  }

  _nextRunLine(nr) {
    let when = nr.time_label || "";
    const ts = parseInt(nr.fires_at, 10);
    if (ts) {
      const fo = { hass: this._hass };
      when = `${I18N.fmtDate(ts, this._lang, Object.assign({ weekday: "short" }, fo))} ${I18N.fmtTime(ts, this._lang, fo)}`;
    }
    return this._t("run.next", { when, in: fmtIn(this._t, nr.in_seconds || 0) });
  }

  connectedCallback() {
    if (this._hass && !this._initialized) {
      this._init();
    } else if (this._initialized && !this._timer) {
      this._refresh();
      this._timer = setInterval(() => this._refresh(), 5000);
    }
  }

  disconnectedCallback() {
    if (this._timer) { clearInterval(this._timer); this._timer = null; }
  }

  _init() {
    this._initialized = true;
    const style = document.createElement("style");
    style.textContent = CARD_STYLES;
    this.shadowRoot.appendChild(style);
    this._root = document.createElement("div");
    this.shadowRoot.appendChild(this._root);
    this._refresh();
    this._timer = setInterval(() => this._refresh(), 5000);
  }

  async _refresh() {
    try {
      this._state = await this._hass.callWS({ type: "schedule_wizard/get_state" });
      this._stateSig = stateSig(this._state);
      const focused = deepActiveElement();
      const focusedHere = focused && this.shadowRoot.contains(focused) &&
        (focused.tagName === "INPUT" || focused.tagName === "TEXTAREA" || focused.tagName === "SELECT");
      if (focusedHere) {
        this._updateInPlace();
        return;
      }
      // Nothing but the clock moved and the user is on a control here: update numbers, keep the DOM (#41).
      if (focused && this.shadowRoot.contains(focused) && this._stateSig === this._renderedSig &&
        Date.now() - this._renderedAt < FOCUSED_RERENDER_MS) {
        this._updateInPlace();
        return;
      }
      this._render();
    } catch (e) {
      this._renderError(e);
    }
  }

  _updateInPlace() {
    if (!this._root) return;
    const bars = this._root.querySelectorAll(".progress-bar");
    bars.forEach(b => {
      const row = b.closest(".row[data-entity]");
      if (!row) return;
      const entity = row.getAttribute("data-entity");
      const active = this._state.active.find(r => r.entity_id === entity);
      if (!active) return;
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - this._state.now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      b.style.width = `${pct}%`;
    });
    this._root.querySelectorAll(".row[data-soak] .soak-left").forEach(span => {
      const entity = span.closest(".row").getAttribute("data-soak");
      const s = (this._state.soaking || []).find(x => x.entity_id === entity && x.phase === "soaking");
      if (!s) return;
      const left = Math.max(0, (parseInt(s.resume_at, 10) || 0) - this._state.now);
      span.textContent = fmtRemaining(left);
    });
  }

  _renderError(e) {
    this._applyDir(this._root);
    this._root.innerHTML = "";
    this._root.appendChild(el("div", { class: "card" }, [
      el("div", { class: "title" }, el("h2", {}, this._config.title || "Schedule Wizard")),
      el("div", { class: "empty" }, this._t("app.load_failed", { error: e.message || this._t("common.unknown") })),
    ]));
  }

  _render() {
    if (!this._state || !this._root) return;
    this._applyDir(this._root);
    const focusKey = captureFocus(this._root);
    this._renderedSig = this._stateSig;
    this._renderedAt = Date.now();
    this._root.innerHTML = "";

    const sec = cardSections(this._state, this._config);

    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "title" }, [
      el("h2", {}, this._config.title || "Schedule Wizard"),
      el("span", { class: "pill " + (this._state.active.length ? "ok" : "") },
        this._state.active.length ? this._t("card.running", { n: this._state.active.length }) : this._t("zone.off")),
    ]));

    if (sec.showActive) {
      const activeDiv = el("div", { class: "active-runs" });
      sec.runs.forEach(r => activeDiv.appendChild(this._activeRow(r)));
      sec.soaks.forEach(s => activeDiv.appendChild(this._soakRow(s)));
      card.appendChild(activeDiv);
    }

    if (this._config.show_quick_run !== false) {
      if (!sec.anyValves) {
        card.appendChild(el("div", { class: "empty" }, this._t("card.no_valves")));
      } else {
        sec.valves.forEach(v => card.appendChild(this._valveRow(v)));
      }
    }

    if (this._error) card.appendChild(el("div", { class: "error-msg" }, this._error));

    this._root.appendChild(card);
    restoreFocus(this._root, focusKey);
  }

  _activeRow(r) {
    const now = this._state.now;
    const remaining = Math.max(0, r.ends_at - now);
    const total = Math.max(1, r.ends_at - r.started_at);
    const pct = Math.min(100, ((total - remaining) / total) * 100);
    const valve = this._state.valves.find(v => v.entity_id === r.entity_id);
    const label = valve ? valve.label : r.entity_id;
    return el("div", { class: "row", "data-entity": r.entity_id }, [
      el("div", {}, [
        el("div", { class: "name" }, ["● ", iso(label)]),
        el("div", { class: "sub" }, `${this._t("run.remaining", { time: fmtRemaining(remaining) })} · ${this._sourceLabel(r.source)}`),
      ]),
      el("div"),
      this._stopButton(r.entity_id, label),
      el("div", { class: "progress-wrap" }, el("div", { class: "progress-bar", style: `width:${pct}%` })),
    ]);
  }

  _soakRow(s) {
    const valve = this._state.valves.find(v => v.entity_id === s.entity_id);
    const label = valve ? valve.label : s.entity_id;
    const left = Math.max(0, (parseInt(s.resume_at, 10) || 0) - this._state.now);
    return el("div", { class: "row", "data-soak": s.entity_id }, [
      el("div", {}, [
        el("div", { class: "name" }, ["💧 ", iso(label)]),
        el("div", { class: "sub soak-line" }, this._tn("card.soaking", {
          time: el("span", { class: "soak-left" }, fmtRemaining(left)), chunk: s.chunk, chunks: s.chunks,
        })),
      ]),
      el("div"),
      s.owner === "cycle" ? el("div") : this._stopButton(s.entity_id, label),
    ]);
  }

  // Visible text first in the name (WCAG 2.5.3), then the zone, so each row's button is distinct (BUG-008).
  _stopButton(entityId, label) {
    const text = this._t("home.stop_watering");
    return el("button", {
      class: "stop",
      "aria-label": this._t("card.action_for", { action: text, zone: label }),
      onClick: () => this._callService("stop_valve", { entity_id: entityId }),
    }, text);
  }

  _valveRow(v) {
    const active = this._state.active.find(r => r.entity_id === v.entity_id);
    const now = this._state.now;
    const soaking = (this._state.soaking || []).find(s => s.entity_id === v.entity_id &&
      s.phase === "soaking" && s.owner !== "cycle");
    const minsInput = el("input", {
      type: "number", min: "1", max: "1440",
      value: String(this._quickDur[v.entity_id] ?? v.default_duration_min),
      "aria-label": this._t("card.minutes_for", { zone: v.label }),
    });
    minsInput.addEventListener("input", () => { this._quickDur[v.entity_id] = minsInput.value; });
    const subLines = [
      active
        ? this._t("run.remaining", { time: fmtRemaining(Math.max(0, active.ends_at - now)) })
        : this._t("run.default_dur", { n: v.default_duration_min }),
    ];
    const delayUntil = parseInt((v && v.rain_delay_until) || 0, 10) || 0;
    if (delayUntil > now) subLines[0] += " · " + this._t("card.rain_delay");
    if (!active && v.next_run) {
      subLines.push(this._nextRunLine(v.next_run));
    }
    const metaInner = [el("div", { class: "name" }, [iso(v.label), active ? " ●" : ""])];
    subLines.forEach(s => metaInner.push(el("div", { class: "sub" }, s)));
    const waterNow = this._t("zone.water_now");
    const children = [
      el("div", {}, metaInner),
      el("label", { class: "mins" }, this._tn("unit.min", { n: minsInput })),
      active || soaking
        ? this._stopButton(v.entity_id, v.label)
        : el("button", {
            class: "run",
            "aria-label": this._t("card.action_for", { action: waterNow, zone: v.label }),
            onClick: () => this._callService("run_valve", {
              entity_id: v.entity_id,
              duration_minutes: parseInt(minsInput.value, 10) || v.default_duration_min,
            }),
          }, waterNow),
    ];
    if (active) {
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      children.push(el("div", { class: "progress-wrap" },
        el("div", { class: "progress-bar", style: `width:${pct}%` })
      ));
    }
    return el("div", { class: "row", "data-entity": v.entity_id }, children);
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("schedule_wizard", service, data);
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      this._showError(this._t("card.failed", { service, error: (e && (e.message || e.code)) || this._t("common.unknown") }));
    }
  }

  _showError(msg) {
    this._error = msg;
    if (this._errorTimer) clearTimeout(this._errorTimer);
    this._errorTimer = setTimeout(() => {
      this._error = null;
      this._errorTimer = null;
      this._render();
    }, 5000);
    this._render();
  }
}

if (!customElements.get("schedule-wizard-card-editor")) {
  customElements.define("schedule-wizard-card-editor", ScheduleWizardCardEditor);
}

if (!customElements.get("schedule-wizard-card")) {
  customElements.define("schedule-wizard-card", ScheduleWizardCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "schedule-wizard-card",
    name: "Schedule Wizard",
    description: "Dashboard card for Schedule Wizard: active runs + quick run.",
    preview: true,
  });
}
