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
}
* { box-sizing: border-box; }
.app {
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px;
  color: var(--sw-text);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.topbar h1 { margin: 0; font-size: 22px; font-weight: 500; }
.title-wrap { display: flex; align-items: center; gap: 4px; }
.menu-btn {
  background: transparent; border: none; padding: 8px; margin-inline-start: -8px;
  cursor: pointer; color: var(--sw-text); border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
}
.menu-btn:hover { background: var(--sw-border); }
.menu-btn svg { width: 24px; height: 24px; fill: currentColor; }
.pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: var(--sw-border);
  color: var(--sw-muted);
}
.pill.ok { background: rgba(22,163,74,0.15); color: var(--sw-success); }
.pill.err { background: rgba(220,38,38,0.15); color: var(--sw-danger); }
.tabs {
  display: flex; gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--sw-border);
  flex-wrap: wrap;
}
.tab {
  background: transparent; border: none;
  padding: 10px 14px; cursor: pointer;
  color: var(--sw-muted); font: inherit;
  border-bottom: 2px solid transparent;
}
.tab.active { color: var(--sw-primary); border-bottom-color: var(--sw-primary); font-weight: 600; }
.card {
  background: var(--sw-card);
  border: 1px solid var(--sw-border);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.card h2 { margin: 0 0 12px; font-size: 16px; font-weight: 600; }
.row-between { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.list { display: flex; flex-direction: column; gap: 8px; }
.empty { color: var(--sw-muted); font-style: italic; padding: 8px 0; }
.item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--sw-border);
  border-radius: 8px;
  background: var(--sw-bg);
}
.name { font-weight: 600; font-size: 14px; }
.sub { color: var(--sw-muted); font-size: 12px; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.btn {
  padding: 6px 12px; border: 1px solid var(--sw-border);
  background: var(--sw-card); color: var(--sw-text);
  border-radius: 6px; cursor: pointer; font: inherit; font-size: 13px;
  transition: all 0.15s;
}
.btn:hover:not(:disabled) { border-color: var(--sw-primary); color: var(--sw-primary); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn.primary { background: var(--sw-primary); color: #fff; border-color: var(--sw-primary); }
.btn.primary:hover:not(:disabled) { filter: brightness(1.1); color: #fff; }
.btn.danger { color: var(--sw-danger); border-color: var(--sw-danger); }
.btn.danger:hover:not(:disabled) { background: var(--sw-danger); color: #fff; }
.btn.small { padding: 4px 8px; font-size: 12px; }
.field { display: block; margin-bottom: 12px; }
.field > span {
  display: block; font-size: 12px; font-weight: 600;
  margin-bottom: 4px; color: var(--sw-muted);
}
.field input, .field select, .field textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--sw-border);
  border-radius: 6px;
  background: var(--sw-card);
  color: var(--sw-text);
  font: inherit;
}
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
@media (max-width: 540px) {
  .field-row { grid-template-columns: 1fr; }
  .item { grid-template-columns: 1fr; }
  .actions { justify-content: flex-start; }
}
.progress-wrap { margin-top: 6px; height: 6px; background: var(--sw-border); border-radius: 3px; overflow: hidden; }
.progress-bar { height: 100%; background: var(--sw-primary); transition: width 0.5s linear; }
.days { display: flex; gap: 4px; flex-wrap: wrap; }
.day-toggle {
  padding: 4px 10px; border: 1px solid var(--sw-border);
  border-radius: 4px; cursor: pointer; user-select: none;
  font-size: 12px; background: var(--sw-card);
}
.day-toggle.on { background: var(--sw-primary); border-color: var(--sw-primary); color: #fff; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: var(--sw-card); border-radius: 12px; padding: 20px;
  max-width: 460px; width: calc(100% - 32px);
  max-height: 85vh; overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.modal h3 { margin: 0 0 14px; font-size: 18px; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  margin-top: 14px; padding-top: 12px;
  border-top: 1px solid var(--sw-border);
}
.entity-picker {
  max-height: 280px; overflow-y: auto;
  border: 1px solid var(--sw-border); border-radius: 6px;
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
.muted { color: var(--sw-muted); }
bdi { unicode-bidi: isolate; }
.sub-tree { margin-inline-start: 18px; margin-top: 6px; border-inline-start: 2px solid var(--sw-border); padding-inline-start: 10px; display: flex; flex-direction: column; gap: 4px; }
.num { text-align: end; }
.badge {
  display: inline-block; margin-inline-start: 6px; padding: 1px 6px;
  border-radius: 4px; font-size: 11px; font-weight: 500;
  background: var(--sw-border); color: var(--sw-muted); vertical-align: middle;
}
.alert-banner {
  padding: 12px 14px; margin-bottom: 14px; border-radius: 10px;
  background: var(--sw-danger); color: #fff; font-weight: 600;
}
.cond-row { display: grid; grid-template-columns: 1.4fr 1fr 0.9fr 0.8fr auto; gap: 6px; align-items: center; padding: 4px 0; }
.cond-row input, .cond-row select {
  width: 100%; padding: 6px 8px; border: 1px solid var(--sw-border); border-radius: 6px;
  background: var(--sw-card); color: var(--sw-text); font: inherit; font-size: 13px;
}
@media (max-width: 540px) { .cond-row { grid-template-columns: 1fr 1fr; } }
.toast {
  position: fixed; bottom: 20px; inset-inline: 0; margin-inline: auto;
  width: max-content; max-width: calc(100% - 32px);
  padding: 10px 16px; background: var(--sw-text); color: var(--sw-bg);
  border-radius: 6px; font-size: 13px;
  z-index: 200; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.toast.error { background: var(--sw-danger); color: #fff; }
.toast.ok { background: var(--sw-success); color: #fff; }
pre { background: var(--sw-bg); padding: 10px; border-radius: 6px; font-size: 12px; overflow-x: auto; }
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
    if (c === null || c === undefined) return;
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

function fmtIn(t, secs) {
  const m = Math.max(0, Math.round(secs / 60));
  return m < 60 ? t("time.in_m", { n: m })
    : m < 1440 ? t("time.in_h", { n: Math.round(m / 60) })
      : t("time.in_d", { n: Math.round(m / 1440) });
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

function maskFromDays(days) {
  let mask = 0;
  for (const d of days) {
    const i = DAYS.indexOf(d);
    if (i >= 0) mask |= DAY_BITS[i];
  }
  return mask;
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

class ScheduleWizardPanel extends HTMLElement {
  constructor() {
    super();
    this._initialized = false;
    this._state = null;
    this._tab = "dashboard";
    this._refreshTimer = null;
    this._modalRoot = null;
    this._quickDur = {};
    this._editing = false;
    this._narrow = false;
    this._rainTarget = "";
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

  _arrow() { return this._rtl ? "←" : "→"; }

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
    const names = DAYS.map((_, i) => i)
      .filter(i => mask & DAY_BITS[i])
      .map(i => I18N.weekdayShort(i, this._lang, this._fo()));
    return names.join(", ") || this._t("sched.no_days");
  }

  _nextRunLine(nr, withDuration) {
    let when = nr.time_label || "";
    const ts = parseInt(nr.fires_at, 10);
    if (ts) when = `${this._fmtDate(ts, { weekday: "short" })} ${this._fmtTime(ts)}`;
    let line = this._t("run.next", { when, in: fmtIn(this._t, nr.in_seconds || 0) });
    if (withDuration && nr.duration_min) line += ` • ${this._t("unit.min", { n: nr.duration_min })}`;
    return line;
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

  _summaryText() {
    return this._t("app.summary", { valves: this._state.valves.length, active: this._state.active.length });
  }

  _updateInPlace() {
    const pill = this.querySelector(".topbar .pill");
    if (pill) {
      pill.textContent = this._summaryText();
      pill.className = "pill " + (this._state.active.length ? "ok" : "");
    }
    const bars = this.querySelectorAll(".progress-bar");
    bars.forEach(b => {
      const row = b.closest(".item[data-entity]");
      if (!row) return;
      const entity = row.getAttribute("data-entity");
      const active = this._state.active.find(r => r.entity_id === entity);
      if (!active) return;
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - this._state.now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      b.style.width = `${pct}%`;
    });
    this.querySelectorAll(".item[data-soak] .soak-left").forEach(span => {
      const entity = span.closest(".item").getAttribute("data-soak");
      const s = (this._state.soaking || []).find(x => x.entity_id === entity && x.phase === "soaking");
      if (!s) return;
      const left = Math.max(0, (parseInt(s.resume_at, 10) || 0) - this._state.now);
      span.textContent = fmtRemaining(left);
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
    const t = el("div", { class: "toast " + kind }, msg);
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

  _render() {
    const app = this.querySelector("#app");
    if (!app || !this._state) return;
    this._applyDir(this);
    this._applyDir(app);
    app.innerHTML = "";

    const top = el("div", { class: "topbar" }, [
      el("div", { class: "title-wrap" }, [this._menuButton(), el("h1", {}, "Schedule Wizard")]),
      el("span", { class: "pill " + (this._state.active.length ? "ok" : "") }, this._summaryText()),
    ]);
    app.appendChild(top);

    const tabs = el("div", { class: "tabs" });
    ["dashboard", "valves", "cycles", "schedules", "reports", "settings"]
      .forEach((key) => {
        const btn = el("button", {
          class: "tab" + (this._tab === key ? " active" : ""),
          onClick: () => { this._tab = key; this._render(); },
        }, this._t("tab." + key));
        tabs.appendChild(btn);
      });
    app.appendChild(tabs);

    const content = el("div");
    app.appendChild(content);

    switch (this._tab) {
      case "dashboard": this._renderDashboard(content); break;
      case "valves": this._renderValves(content); break;
      case "cycles": this._renderCycles(content); break;
      case "schedules": this._renderSchedules(content); break;
      case "reports": this._renderReports(content); break;
      case "settings": this._renderSettings(content); break;
    }
  }

  _renderDashboard(root) {
    const rainUntil = parseInt(this._state.rain_delay_until || 0, 10);
    const now = this._state.now;
    const soaking = this._state.soaking || [];
    const flow = this._state.flow || {};

    if (flow.alert) {
      root.appendChild(el("div", { class: "alert-banner" },
        flow.alert === "leak"
          ? this._t("dash.flow_leak")
          : flow.alert === "high_flow"
            ? this._t("dash.flow_high")
            : this._t("dash.flow_other", { alert: flow.alert })
      ));
    }

    const anythingRunning = this._state.active.length > 0 ||
      (this._state.active_cycles || []).length > 0 || soaking.length > 0;
    if (flow.entity_id || anythingRunning) {
      const headerChildren = [];
      if (flow.entity_id) {
        const flowVal = (flow.value === null || flow.value === undefined) ? this._t("common.unavailable") : String(flow.value);
        headerChildren.push(el("span", { class: "pill", title: flow.entity_id }, this._t("dash.flow_value", { value: flowVal })));
      } else {
        headerChildren.push(el("span"));
      }
      if (anythingRunning) {
        headerChildren.push(el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm(this._t("dash.stop_all_confirm"))) return;
            this._callService("stop_all", {});
          },
        }, this._t("dash.stop_all")));
      }
      root.appendChild(el("div", { class: "row-between" }, headerChildren));
    }

    const rainCard = el("div", { class: "card" });
    if (rainUntil > now) {
      const lbl = fmtDelayLeft(this._t, rainUntil - now);
      rainCard.appendChild(el("div", { class: "row-between" }, [
        el("h2", { style: "margin:0;color:var(--sw-warn);" }, this._t("dash.rain_delay_active", { left: lbl })),
        el("button", {
          class: "btn small",
          onClick: () => this._callService("clear_rain_delay", {}),
        }, this._t("common.clear")),
      ]));
    } else {
      rainCard.appendChild(el("div", { class: "row-between" }, [
        el("h2", { style: "margin:0;" }, this._t("dash.rain_delay")),
      ]));
    }
    const valves = this._state.valves || [];
    if (this._rainTarget && !valves.some(v => v.entity_id === this._rainTarget)) this._rainTarget = "";
    const targetSel = el("select", { "aria-label": this._t("dash.apply_to"), style: "max-width:220px;" });
    targetSel.appendChild(el("option", { value: "" }, this._t("dash.all_valves")));
    valves.forEach((v) => {
      const opt = el("option", { value: v.entity_id }, v.label || v.entity_id);
      if (v.entity_id === this._rainTarget) opt.selected = true;
      targetSel.appendChild(opt);
    });
    targetSel.value = this._rainTarget;
    targetSel.addEventListener("change", () => { this._rainTarget = targetSel.value; });
    const setDelay = (hours) => {
      const target = this._rainTarget;
      if (target && !(this._state.valves || []).some(v => v.entity_id === target)) {
        this._rainTarget = "";
        this._toast(this._t("dash.valve_gone"), "error");
        this._render();
        return;
      }
      this._callService("set_rain_delay", target ? { hours, entity_id: [target] } : { hours });
    };
    rainCard.appendChild(el("div", { class: "row-between", style: "margin:10px 0 0;" }, [
      el("label", { style: "display:flex;align-items:center;gap:6px;font-size:13px;" }, [
        el("span", { class: "muted" }, this._t("dash.apply_to")),
        targetSel,
      ]),
      el("div", { class: "actions" }, [
        el("button", { class: "btn small", onClick: () => setDelay(24) }, this._t("time.short_h", { n: 24 })),
        el("button", { class: "btn small", onClick: () => setDelay(48) }, this._t("time.short_h", { n: 48 })),
        el("button", { class: "btn small", onClick: () => setDelay(168) }, this._t("time.short_d", { n: 7 })),
      ]),
    ]));
    rainCard.appendChild(el("p", { class: "muted small", style: "margin:4px 0 0;" }, this._t("dash.rain_hint")));
    const delayedValves = valves.filter(v => valveDelayUntil(v, now));
    if (delayedValves.length) {
      const dList = el("div", { class: "list", style: "margin-top:10px;" });
      delayedValves.forEach((v) => {
        const lbl = fmtDelayLeft(this._t, valveDelayUntil(v, now) - now);
        dList.appendChild(el("div", { class: "item" }, [
          el("div", { class: "sub" }, this._tn("dash.valve_delayed", { valve: v.label ? iso(v.label) : ltr(v.entity_id), left: lbl })),
          el("div", { class: "actions" }, [
            el("button", {
              class: "btn small",
              onClick: () => this._callService("clear_rain_delay", { entity_id: [v.entity_id] }),
            }, this._t("common.clear")),
          ]),
        ]));
      });
      rainCard.appendChild(dList);
    }
    root.appendChild(rainCard);

    const activeCycles = this._state.active_cycles || [];
    if (activeCycles.length) {
      const cyclesCard = el("div", { class: "card" }, [el("h2", {}, this._t("dash.active_cycles"))]);
      const cyclesList = el("div", { class: "list" });
      activeCycles.forEach((c) => cyclesList.appendChild(this._activeCycleRow(c)));
      cyclesCard.appendChild(cyclesList);
      root.appendChild(cyclesCard);
    }

    const active = el("div", { class: "card" }, [el("h2", {}, this._t("dash.active_runs"))]);
    const list = el("div", { class: "list" });
    const soakingIdle = soaking.filter(s => s.phase === "soaking" &&
      !this._state.active.some(r => r.entity_id === s.entity_id));
    if (!this._state.active.length && !soakingIdle.length) {
      list.appendChild(el("div", { class: "empty" }, this._t("dash.no_active")));
    } else {
      this._state.active.forEach((r) => list.appendChild(this._activeRunRow(r)));
      soakingIdle.forEach((s) => list.appendChild(this._soakingRow(s)));
    }
    active.appendChild(list);
    root.appendChild(active);

    const quick = el("div", { class: "card" }, [el("h2", {}, this._t("dash.quick_run"))]);
    const qList = el("div", { class: "list" });
    if (!this._state.valves.length) {
      qList.appendChild(el("div", { class: "empty" }, this._t("dash.add_valves_first")));
    } else {
      this._state.valves.forEach((v) => qList.appendChild(this._quickRunRow(v)));
    }
    quick.appendChild(qList);
    root.appendChild(quick);

    const hist = el("div", { class: "card" }, [el("h2", {}, this._t("dash.recent"))]);
    const hList = el("div", { class: "list" });
    if (!this._state.history.length) {
      hList.appendChild(el("div", { class: "empty" }, this._t("dash.no_history")));
    } else {
      const grouped = this._groupHistory(this._state.history.slice(0, 30));
      grouped.slice(0, 14).forEach((g) => {
        if (g.kind === "cycle") {
          hList.appendChild(this._cycleHistoryRow(g.entry, g.children));
        } else {
          hList.appendChild(this._historyRow(g.entry));
        }
      });
    }
    hist.appendChild(hList);
    root.appendChild(hist);
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
        used.add(i);
      } else if (!h.source || !h.source.startsWith("cycle:")) {
        out.push({ kind: "valve", entry: h });
        used.add(i);
      } else {
        out.push({ kind: "valve", entry: h });
        used.add(i);
      }
    }
    return out;
  }

  _cycleHistoryRow(r, children) {
    const cycle = (this._state.cycles || []).find(c => c.id === r.valve_entity_id);
    const cycleName = cycle ? cycle.name : r.valve_entity_id;
    const valvesMap = Object.fromEntries((this._state.valves || []).map(v => [v.entity_id, v.label]));
    const wrap = el("div", { class: "item", style: "display:block;" });
    wrap.appendChild(el("div", { style: "display:flex;justify-content:space-between;gap:10px;" }, [
      el("div", {}, [
        el("div", { class: "name" }, ["🔁 ", iso(cycleName)]),
        el("div", { class: "sub" }, joinParts([this._fmtDT(r.ts), this._sourceLabel(r.source), this._statusLabel(r.status)])),
      ]),
    ]));
    const meaningfulChildren = (children || []).filter(c => c.status !== "started");
    if (meaningfulChildren.length) {
      const sub = el("div", { class: "sub-tree" });
      const hook = this._rtl ? "↲ " : "↳ ";
      meaningfulChildren.forEach(c => {
        const lbl = valvesMap[c.valve_entity_id] ? iso(valvesMap[c.valve_entity_id]) : ltr(c.valve_entity_id);
        sub.appendChild(el("div", { class: "sub" }, [hook, ...joinParts([
          lbl, this._t("unit.min", { n: c.duration_min }), this._statusLabel(c.status), this._fmtDT(c.ts),
        ])]));
      });
      wrap.appendChild(sub);
    }
    return wrap;
  }

  _activeRunRow(r) {
    const now = this._state.now;
    const remaining = Math.max(0, r.ends_at - now);
    const total = Math.max(1, r.ends_at - r.started_at);
    const pct = Math.min(100, ((total - remaining) / total) * 100);
    const valve = this._state.valves.find((v) => v.entity_id === r.entity_id);
    const label = valve ? valve.label : r.entity_id;
    const soak = (this._state.soaking || []).find(s => s.entity_id === r.entity_id && s.phase === "running");
    const chunkLbl = soak && soak.chunks > 1 ? " " + this._t("run.chunk", { chunk: soak.chunk, chunks: soak.chunks }) : "";

    return el("div", { class: "item", "data-entity": r.entity_id }, [
      el("div", {}, [
        el("div", { class: "name" }, iso(label)),
        el("div", { class: "sub" }, joinParts([
          ltr(r.entity_id), this._sourceLabel(r.source), this._t("run.left", { time: fmtRemaining(remaining) }) + chunkLbl,
        ])),
        el("div", { class: "progress-wrap" }, el("div", { class: "progress-bar", style: `width:${pct}%` })),
      ]),
      el("div", { class: "actions" }, [
        el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_valve", { entity_id: r.entity_id }),
        }, this._t("common.stop")),
      ]),
    ]);
  }

  _soakingRow(s) {
    const valve = this._state.valves.find((v) => v.entity_id === s.entity_id);
    const label = valve ? valve.label : s.entity_id;
    const left = Math.max(0, (parseInt(s.resume_at, 10) || 0) - this._state.now);
    const ownerCycle = s.owner === "cycle"
      ? (this._state.active_cycles || []).find(c => c.current_entity === s.entity_id)
      : null;
    const ownerLbl = s.owner === "cycle" ? this._t("run.part_of_cycle") : null;
    const stopBtn = ownerCycle
      ? el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_cycle", { cycle_id: ownerCycle.cycle_id }),
        }, this._t("run.stop_cycle"))
      : el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_valve", { entity_id: s.entity_id }),
        }, this._t("common.stop"));
    return el("div", { class: "item", "data-soak": s.entity_id }, [
      el("div", {}, [
        el("div", { class: "name" }, ["💧 ", iso(label)]),
        el("div", { class: "sub soak-line" }, joinParts([
          this._tn("run.soaking", { chunk: s.chunk, chunks: s.chunks, time: el("span", { class: "soak-left" }, fmtRemaining(left)) }),
          this._sourceLabel(s.source),
          ownerLbl,
        ])),
      ]),
      el("div", { class: "actions" }, [stopBtn]),
    ]);
  }

  _quickRunRow(v) {
    const active = this._state.active.find(r => r.entity_id === v.entity_id);
    const now = this._state.now;
    const minsInput = el("input", {
      type: "number", min: "1", max: "1440",
      value: String(this._quickDur[v.entity_id] ?? v.default_duration_min),
      style: "width:70px;",
    });
    minsInput.addEventListener("input", () => { this._quickDur[v.entity_id] = minsInput.value; });
    const delayUntil = valveDelayUntil(v, now);
    const delayLbl = delayUntil ? this._t("run.delayed", { left: fmtDelayLeft(this._t, delayUntil - now) }) : null;
    const meta = el("div", {}, [
      el("div", { class: "name" }, [iso(v.label), active ? "  ●" : ""]),
      el("div", { class: "sub" }, joinParts(active
        ? [ltr(v.entity_id), `${this._t("run.remaining", { time: fmtRemaining(Math.max(0, active.ends_at - now)) })} (${this._sourceLabel(active.source)})`, delayLbl]
        : [ltr(v.entity_id), this._t("run.default_dur", { n: v.default_duration_min }), delayLbl]
      )),
    ]);
    if (!active && v.next_run) {
      meta.appendChild(el("div", { class: "sub", style: "margin-top:2px;color:var(--sw-primary);" },
        this._nextRunLine(v.next_run, true)
      ));
    }
    if (active) {
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      meta.appendChild(el("div", { class: "progress-wrap" },
        el("div", { class: "progress-bar", style: `width:${pct}%` })
      ));
    }
    return el("div", { class: "item", "data-entity": v.entity_id }, [
      meta,
      el("div", { class: "actions" }, [
        minsInput,
        el("button", {
          class: "btn primary small",
          onClick: () => this._callService("run_valve", {
            entity_id: v.entity_id,
            duration_minutes: parseInt(minsInput.value, 10) || v.default_duration_min,
          }),
        }, this._t("common.run")),
        el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_valve", { entity_id: v.entity_id }),
        }, this._t("common.stop")),
      ]),
    ]);
  }

  _historyRow(r) {
    const valve = this._state.valves.find((v) => v.entity_id === r.valve_entity_id);
    const label = valve ? iso(valve.label) : ltr(r.valve_entity_id);
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, label),
        el("div", { class: "sub" }, joinParts([
          this._fmtDT(r.ts), this._t("unit.min", { n: r.duration_min }), this._sourceLabel(r.source), this._statusLabel(r.status),
        ])),
      ]),
      el("div"),
    ]);
  }

  _renderValves(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "row-between" }, [
      el("h2", {}, this._t("tab.valves")),
      el("button", {
        class: "btn primary",
        onClick: () => this._openValveModal(null),
      }, this._t("valves.add")),
    ]));
    const list = el("div", { class: "list" });
    if (!this._state.valves.length) {
      list.appendChild(el("div", { class: "empty" }, this._t("valves.empty")));
    } else {
      this._state.valves.forEach((v) => list.appendChild(this._valveRow(v)));
    }
    card.appendChild(list);
    root.appendChild(card);
  }

  _valveRow(v) {
    const stats = v.stats || {};
    let lastLine = this._t("valves.never_run");
    if (stats.last_run) {
      const ago = Math.max(0, this._state.now - stats.last_run.ts);
      lastLine = joinParts([
        this._t("valves.last", { ago: this._fmtAgo(ago) }),
        this._t("unit.min", { n: stats.last_run.duration_min }),
        this._statusLabel(stats.last_run.status),
      ]).join("");
    }
    const week = stats.runs_7d
      ? this._t("valves.week", { runs: stats.runs_7d, min: stats.total_min_7d })
      : this._t("valves.week_none");
    const badges = [];
    if ((v.soak_run_min || 0) > 0 && (v.soak_pause_min || 0) > 0) {
      badges.push(el("span", { class: "badge", title: this._t("valves.badge_soak_title") }, this._t("valves.badge_soak", { run: v.soak_run_min, pause: v.soak_pause_min })));
    }
    if (v.moisture_entity) {
      badges.push(el("span", { class: "badge", title: v.moisture_entity }, this._t("valves.badge_moisture")));
    }
    if (v.rain_exempt) {
      badges.push(el("span", { class: "badge", title: this._t("valves.badge_indoor_title") }, this._t("valves.badge_indoor")));
    }
    const vDelay = valveDelayUntil(v, this._state.now);
    if (vDelay) {
      const until = this._fmtDT(vDelay, { month: "numeric", day: "numeric", hour: "numeric", minute: "2-digit" });
      badges.push(el("span", { class: "badge", title: this._t("valves.badge_delay_title") }, this._t("valves.badge_delay", { until })));
    }
    const metaChildren = [
      el("div", { class: "name" }, [iso(v.label), v.enabled ? "" : " " + this._t("common.disabled_tag"), ...badges]),
      el("div", { class: "sub" }, joinParts([ltr(v.entity_id), this._t("valves.default_dur", { n: v.default_duration_min })])),
      el("div", { class: "sub", style: "margin-top:2px;" }, lastLine + " • " + week),
    ];
    if (v.next_run) {
      metaChildren.push(el("div", { class: "sub", style: "margin-top:2px;color:var(--sw-primary);" },
        this._nextRunLine(v.next_run, true)
      ));
    }
    return el("div", { class: "item" }, [
      el("div", {}, metaChildren),
      el("div", { class: "actions" }, [
        el("button", { class: "btn small", onClick: () => this._openValveModal(v) }, this._t("common.edit")),
        el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm(this._t("valves.delete_confirm", { name: v.label }))) return;
            this._callService("remove_valve", { entity_id: v.entity_id });
          },
        }, this._t("common.delete")),
      ]),
    ]);
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

    const hasAdvanced = !!(existing && ((existing.soak_run_min || 0) > 0 || (existing.soak_pause_min || 0) > 0 || existing.moisture_entity));
    const advBody = el("div", { style: hasAdvanced ? "" : "display:none;" }, [
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
    const advToggle = el("button", { class: "btn small", type: "button" }, this._t(hasAdvanced ? "common.hide_advanced" : "common.show_advanced"));
    advToggle.addEventListener("click", () => {
      const hidden = advBody.style.display === "none";
      advBody.style.display = hidden ? "" : "none";
      advToggle.textContent = this._t(hidden ? "common.hide_advanced" : "common.show_advanced");
    });

    const fields = [
      el("label", { class: "field" }, [el("span", {}, this._t("valves.search")), search, picker]),
      el("label", { class: "field" }, [el("span", {}, this._t("valves.label")), labelInput]),
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
      });
      if (ok && existing && existing.entity_id !== chosen) {
        const oldSchedules = (this._state.schedules || []).filter(s => s.valve_entity_id === existing.entity_id);
        for (const s of oldSchedules) {
          const payload = {
            valve_entity_id: chosen,
            time: s.time_hhmm,
            days: daysFromMaskNames(s.days_mask),
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

  _activeCycleRow(c) {
    const valve = this._state.valves.find(v => v.entity_id === c.current_entity);
    const currentLabel = valve ? iso(valve.label) : (c.current_entity ? ltr(c.current_entity) : "-");
    const paused = !!c.paused;
    const stepLine = paused
      ? joinParts([this._t("cycle.paused_at", { step: c.paused_at_step || c.step, total: c.total_steps }), this._sourceLabel(c.source)])
      : joinParts([this._t("cycle.step", { step: c.step, total: c.total_steps }), currentLabel, this._sourceLabel(c.source)]);
    const actions = [];
    if (paused) {
      actions.push(el("button", {
        class: "btn primary small",
        onClick: () => this._callService("resume_cycle", { cycle_id: c.cycle_id }),
      }, this._t("cycle.resume")));
    } else {
      actions.push(el("button", {
        class: "btn small",
        onClick: () => this._callService("pause_cycle", { cycle_id: c.cycle_id }),
      }, this._t("cycle.pause")));
    }
    actions.push(el("button", {
      class: "btn danger small",
      onClick: () => this._callService("stop_cycle", { cycle_id: c.cycle_id }),
    }, this._t("common.stop")));
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, [paused ? "⏸ " : "● ", iso(c.cycle_name || c.cycle_id)]),
        el("div", { class: "sub" }, stepLine),
      ]),
      el("div", { class: "actions" }, actions),
    ]);
  }

  _renderCycles(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "row-between" }, [
      el("h2", {}, this._t("tab.cycles")),
      el("button", {
        class: "btn primary",
        onClick: () => this._openCycleModal(null),
      }, this._t("cycles.add")),
    ]));
    const list = el("div", { class: "list" });
    const cycles = this._state.cycles || [];
    if (!cycles.length) {
      list.appendChild(el("div", { class: "empty" },
        this._t("cycles.empty", { arrow: this._arrow() })
      ));
    } else {
      cycles.forEach(c => list.appendChild(this._cycleRow(c)));
    }
    card.appendChild(list);
    root.appendChild(card);
  }

  _cycleRow(c) {
    const active = (this._state.active_cycles || []).some(a => a.cycle_id === c.id);
    const steps = c.steps || [];
    const totalMin = steps.reduce((a, s) => a + (s.duration_min || 0), 0);
    const valvesMap = Object.fromEntries(this._state.valves.map(v => [v.entity_id, v.label]));
    const stepLabels = joinParts(steps.map(s => [
      valvesMap[s.entity_id] ? iso(valvesMap[s.entity_id]) : ltr(s.entity_id),
      " " + this._t("unit.min", { n: s.duration_min }),
    ]), ` ${this._arrow()} `);
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, [
          iso(c.name || c.id),
          c.enabled ? "" : " " + this._t("common.disabled_tag"),
          active ? " ● " + this._t("common.running") : "",
        ]),
        el("div", { class: "sub" }, this._t("cycles.summary", { steps: steps.length, min: totalMin })),
        el("div", { class: "sub", style: "margin-top:2px;" }, stepLabels),
      ]),
      el("div", { class: "actions" }, [
        active
          ? el("button", {
              class: "btn danger small",
              onClick: () => this._callService("stop_cycle", { cycle_id: c.id }),
            }, this._t("common.stop"))
          : el("button", {
              class: "btn primary small",
              onClick: () => this._callService("run_cycle", { cycle_id: c.id }),
            }, this._t("common.run")),
        el("button", {
          class: "btn small",
          onClick: () => this._openCycleModal(c),
        }, this._t("common.edit")),
        el("button", {
          class: "btn small",
          onClick: () => this._callService("update_cycle", { cycle_id: c.id, enabled: !c.enabled }),
        }, this._t(c.enabled ? "common.disable" : "common.enable")),
        el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm(this._t("cycles.delete_confirm", { name: c.name }))) return;
            this._callService("remove_cycle", { cycle_id: c.id });
          },
        }, this._t("common.delete")),
      ]),
    ]);
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
        const sel = el("select", {});
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
        });
        durInput.addEventListener("input", () => { s.duration_min = parseInt(durInput.value, 10) || 1; });

        const row = el("div", {
          style: "display:grid;grid-template-columns:24px 1fr 80px auto auto;gap:6px;align-items:center;padding:4px 0;",
        }, [
          el("span", { class: "muted small" }, String(idx + 1)),
          sel,
          durInput,
          el("button", {
            class: "btn small",
            disabled: idx === 0 ? "disabled" : null,
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
      el("label", { class: "field" }, [el("span", {}, this._t("common.name")), nameInput]),
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

  _renderSchedules(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "row-between" }, [
      el("h2", {}, this._t("tab.schedules")),
      el("button", {
        class: "btn primary",
        onClick: () => this._openScheduleModal(null),
      }, this._t("sched.add")),
    ]));
    const list = el("div", { class: "list" });
    if (!this._state.schedules.length) {
      list.appendChild(el("div", { class: "empty" }, this._t("sched.empty")));
    } else {
      this._state.schedules.forEach((s) => list.appendChild(this._scheduleRow(s)));
    }
    card.appendChild(list);
    root.appendChild(card);
  }

  _scheduleRow(s) {
    let targetName;
    let targetDuration;
    if (s.cycle_id) {
      const cycle = (this._state.cycles || []).find(c => c.id === s.cycle_id);
      targetName = this._t("sched.target_cycle", { name: cycle ? cycle.name : s.cycle_id });
      targetDuration = cycle ? this._t("sched.total", { n: (cycle.steps || []).reduce((a, x) => a + (x.duration_min || 0), 0) }) : "";
    } else {
      const valve = this._state.valves.find(v => v.entity_id === s.valve_entity_id);
      targetName = valve ? valve.label : s.valve_entity_id;
      targetDuration = this._t("unit.min", { n: s.duration_min });
    }
    const condCount = Array.isArray(s.conditions) ? s.conditions.length : 0;
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, [
          iso(s.name || this._t("sched.name_at", { target: targetName, time: s.time_hhmm })),
          s.enabled ? "" : " " + this._t("common.disabled_tag"),
          condCount ? el("span", { class: "badge" }, condCount === 1 ? this._t("sched.conditions_one") : this._t("sched.conditions_other", { n: condCount })) : null,
        ]),
        el("div", { class: "sub" }, joinParts([iso(targetName), ltr(s.time_hhmm), this._daysFromMask(s.days_mask), targetDuration])),
      ]),
      el("div", { class: "actions" }, [
        el("button", {
          class: "btn small",
          onClick: () => this._openScheduleModal(s),
        }, this._t("common.edit")),
        el("button", {
          class: "btn small",
          onClick: () => this._callService("update_schedule", { schedule_id: s.id, enabled: !s.enabled }),
        }, this._t(s.enabled ? "common.disable" : "common.enable")),
        el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm(this._t("sched.delete_confirm"))) return;
            this._callService("remove_schedule", { schedule_id: s.id });
          },
        }, this._t("common.delete")),
      ]),
    ]);
  }

  _openScheduleModal(existing) {
    const hasValves = this._state.valves.length > 0;
    const hasCycles = (this._state.cycles || []).length > 0;
    if (!hasValves && !hasCycles) { this._toast(this._t("sched.add_first"), "error"); return; }

    let targetKind;
    if (existing) {
      targetKind = existing.cycle_id ? "cycle" : "valve";
    } else {
      targetKind = hasValves ? "valve" : "cycle";
    }
    let valveEntity = existing && existing.valve_entity_id ? existing.valve_entity_id : (hasValves ? this._state.valves[0].entity_id : "");
    let cycleId = existing && existing.cycle_id ? existing.cycle_id : (hasCycles ? this._state.cycles[0].id : "");
    let name = existing ? existing.name : "";
    let time = existing ? existing.time_hhmm : "06:00";
    let duration = existing ? existing.duration_min : (this._state.options.default_duration || 10);
    let mask = existing ? existing.days_mask : 127;
    let enabled = existing ? !!existing.enabled : true;

    const targetSel = el("select", existing ? { disabled: "disabled" } : {});
    if (hasValves) targetSel.appendChild(el("option", { value: "valve" }, this._t("sched.single_valve")));
    if (hasCycles) targetSel.appendChild(el("option", { value: "cycle" }, this._t("sched.cycle_multi")));
    targetSel.value = targetKind;
    targetSel.addEventListener("change", () => { targetKind = targetSel.value; renderTargetField(); });

    const targetFieldHost = el("div");
    const valveSel = el("select", existing ? { disabled: "disabled" } : {});
    this._state.valves.forEach(v => {
      const opt = el("option", { value: v.entity_id }, optLabel(v.label, v.entity_id));
      if (v.entity_id === valveEntity) opt.selected = true;
      valveSel.appendChild(opt);
    });
    valveSel.addEventListener("change", () => { valveEntity = valveSel.value; });

    const cycleSel = el("select", existing ? { disabled: "disabled" } : {});
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

    const days = el("div", { class: "days" });
    DAYS.forEach((_, i) => {
      const tog = el("div", {
        class: "day-toggle" + ((mask & DAY_BITS[i]) ? " on" : ""),
        title: I18N.weekdayLong(i, this._lang, this._fo()),
      }, I18N.weekdayShort(i, this._lang, this._fo()));
      tog.addEventListener("click", () => {
        mask ^= DAY_BITS[i];
        tog.classList.toggle("on", !!(mask & DAY_BITS[i]));
      });
      days.appendChild(tog);
    });

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
      el("label", { class: "field" }, [el("span", {}, this._t("sched.target")), targetSel]),
      targetFieldHost,
      durRow,
      el("label", { class: "field" }, [el("span", {}, this._t("common.name")), nameInput]),
      el("div", { class: "field" }, [el("span", {}, this._t("sched.days")), days]),
      el("div", { class: "field" }, [el("span", {}, this._t("sched.conditions")), condWrap]),
      el("label", { class: "field" }, [el("span", {}, this._t("common.enabled")), enabledInput]),
    ];

    this._showModal(this._t(existing ? "sched.edit_title" : "sched.add_title"), fields, async () => {
      if (!mask) { this._toast(this._t("sched.pick_day"), "error"); return false; }
      const conds = collectConditions();
      if (existing) {
        return await this._callService("update_schedule", {
          schedule_id: existing.id,
          name,
          time,
          duration_minutes: targetKind === "valve" ? duration : 1,
          days: daysFromMaskNames(mask),
          enabled,
          conditions: conds,
        });
      }
      const base = {
        time,
        days: daysFromMaskNames(mask),
        name,
        enabled,
        conditions: conds,
      };
      if (targetKind === "cycle") {
        return await this._callService("add_schedule", { ...base, cycle_id: cycleId, duration_minutes: 1 });
      }
      return await this._callService("add_schedule", { ...base, valve_entity_id: valveEntity, duration_minutes: duration });
    });
  }

  _renderReports(root) {
    const history = this._state.history || [];
    const valves = this._state.valves || [];
    const cycles = this._state.cycles || [];
    const cyclesById = Object.fromEntries(cycles.map(c => [c.id, c]));
    const valvesById = Object.fromEntries(valves.map(v => [v.entity_id, v]));
    const now = this._state.now;
    const day = 86400;

    const inWindow = (ts, days) => ts >= (now - days * day);

    const valveStats = {};
    const cycleStats = {};
    const dailyMin = {};
    const skipReasons = { skipped_rain: 0, skipped_moisture: 0, skipped_overlap: 0, failed_to_open: 0, cancelled: 0 };

    history.forEach(h => {
      const status = h.status || "";
      const dur = parseInt(h.duration_min || 0, 10);
      const isCycleEntry = !!cyclesById[h.valve_entity_id];
      const target = isCycleEntry ? "cycle" : "valve";

      if (status === "started") return;

      if (status in skipReasons) skipReasons[status]++;

      if (target === "valve") {
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
        const cs = cycleStats[id] = cycleStats[id] || { name: cyclesById[id]?.name || id, runs_30d: 0, completed: 0, cancelled: 0, skipped: 0 };
        if (inWindow(h.ts, 30)) {
          cs.runs_30d++;
          if (status === "cycle_completed") cs.completed++;
          else if (status === "cycle_cancelled") cs.cancelled++;
          else if (status.startsWith("skipped")) cs.skipped++;
        }
      }
    });

    const exportCard = el("div", { class: "card" }, [
      el("div", { class: "row-between" }, [
        el("h2", {}, this._t("tab.reports")),
        el("button", {
          class: "btn primary small",
          onClick: () => this._downloadHistoryCsv(),
        }, this._t("reports.export")),
      ]),
      el("p", { class: "muted small", style: "margin:0;" }, this._t("reports.based_on", { n: history.length })),
    ]);
    root.appendChild(exportCard);

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
      const bar = el("div", {
        title: this._t("reports.bar_title", { date: dayLabels[i], n: v }),
        style: `flex:1;height:${h}px;min-width:6px;background:var(--sw-primary);border-radius:2px 2px 0 0;`,
      });
      chart.appendChild(bar);
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
      const head = el("div", {
        style: "display:grid;grid-template-columns:1.4fr repeat(3, 1fr);gap:6px;font-size:12px;font-weight:600;color:var(--sw-muted);padding:6px 4px;border-bottom:1px solid var(--sw-border);",
      }, [
        el("span", {}, this._t("sched.valve")),
        el("span", { class: "num" }, this._t("reports.col_7d")),
        el("span", { class: "num" }, this._t("reports.col_30d")),
        el("span", { class: "num" }, this._t("reports.total")),
      ]);
      valveTable.appendChild(head);
      valves.forEach(v => {
        const s = valveStats[v.entity_id] || { runs_7d: 0, min_7d: 0, runs_30d: 0, min_30d: 0, runs_total: 0, min_total: 0 };
        const row = el("div", {
          style: "display:grid;grid-template-columns:1.4fr repeat(3, 1fr);gap:6px;font-size:13px;padding:6px 4px;border-bottom:1px solid var(--sw-border);",
        }, [
          el("span", {}, iso(v.label)),
          el("span", { class: "num" }, this._t("reports.runs_min", { runs: s.runs_7d, min: s.min_7d })),
          el("span", { class: "num" }, this._t("reports.runs_min", { runs: s.runs_30d, min: s.min_30d })),
          el("span", { class: "num" }, this._t("reports.runs_min", { runs: s.runs_total, min: s.min_total })),
        ]);
        valveTable.appendChild(row);
      });
    }
    root.appendChild(valveTable);

    if (cycles.length) {
      const cycleTable = el("div", { class: "card" }, [el("h2", {}, this._t("reports.per_cycle"))]);
      const head = el("div", {
        style: "display:grid;grid-template-columns:1.5fr repeat(3, 0.7fr) 0.7fr;gap:6px;font-size:12px;font-weight:600;color:var(--sw-muted);padding:6px 4px;border-bottom:1px solid var(--sw-border);",
      }, [
        el("span", {}, this._t("sched.cycle")),
        el("span", { class: "num" }, this._t("reports.done")),
        el("span", { class: "num" }, this._t("reports.cancelled")),
        el("span", { class: "num" }, this._t("reports.skipped")),
        el("span", { class: "num" }, this._t("reports.total")),
      ]);
      cycleTable.appendChild(head);
      cycles.forEach(c => {
        const s = cycleStats[c.id] || { completed: 0, cancelled: 0, skipped: 0, runs_30d: 0 };
        const row = el("div", {
          style: "display:grid;grid-template-columns:1.5fr repeat(3, 0.7fr) 0.7fr;gap:6px;font-size:13px;padding:6px 4px;border-bottom:1px solid var(--sw-border);",
        }, [
          el("span", {}, iso(c.name)),
          el("span", { class: "num", style: "color:var(--sw-success);" }, String(s.completed)),
          el("span", { class: "num", style: "color:var(--sw-warn);" }, String(s.cancelled)),
          el("span", { class: "num", style: "color:var(--sw-muted);" }, String(s.skipped)),
          el("span", { class: "num", style: "font-weight:600;" }, String(s.runs_30d)),
        ]);
        cycleTable.appendChild(row);
      });
      root.appendChild(cycleTable);
    }

    const skipsCard = el("div", { class: "card" }, [el("h2", {}, this._t("reports.skip_reasons"))]);
    const skipGrid = el("div", { style: "display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;" });
    [
      ["skipped_rain", this._t("reports.rain")],
      ["skipped_moisture", this._t("reports.moisture")],
      ["skipped_overlap", this._t("reports.overlap")],
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
    const header = ["timestamp", "iso_time", "target_kind", "target_id", "target_label", "duration_min", "source", "status", "note"];
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
      ];
    });
    const escape = (v) => {
      const s = String(v == null ? "" : v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const csv = [header.map(escape).join(","), ...rows.map(r => r.map(escape).join(","))].join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `schedule_wizard_history_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
  }

  _renderSettings(root) {
    const opts = this._state.options || {};

    const advancedKey = "_sw_show_advanced";
    const showAdvanced = !!this._showAdvanced;

    const card = el("div", { class: "card" }, [el("h2", {}, this._t("settings.calendar"))]);
    card.appendChild(el("p", { class: "muted" }, this._t("settings.calendar_hint")));

    const calSel = el("select", {});
    calSel.appendChild(el("option", { value: "" }, this._t("common.none")));
    this._state.calendars.forEach((c) => {
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

    card.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.calendar_entity")), calSel]));
    card.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("settings.lookahead")), lookInput]),
      el("label", { class: "field" }, [el("span", {}, this._t("settings.poll")), pollInput]),
    ]));
    card.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.default_duration")), defDurInput]));

    const advancedToggle = el("div", {
      style: "margin-top:14px;padding-top:12px;border-top:1px solid var(--sw-border);display:flex;justify-content:space-between;align-items:center;",
    });
    advancedToggle.appendChild(el("strong", {}, this._t(showAdvanced ? "settings.advanced_shown" : "settings.advanced_hidden")));
    const advBtn = el("button", { class: "btn small" }, this._t(showAdvanced ? "common.hide" : "common.show"));
    advBtn.addEventListener("click", () => {
      this._showAdvanced = !this._showAdvanced;
      this._render();
    });
    advancedToggle.appendChild(advBtn);
    card.appendChild(advancedToggle);

    if (!showAdvanced) {
      card.appendChild(el("p", { class: "muted small", style: "margin-top:8px;" }, this._t("settings.advanced_hint")));
    }

    const rainSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    rainSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.rain_skip")));
    rainSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.rain_hint")));
    rainSection.appendChild(el("label", { class: "field" }, [
      el("span", {}, this._t("settings.rain_entity")),
      rainEntityInput,
    ]));
    rainSection.appendChild(el("label", { class: "field" }, [
      el("span", {}, this._t("settings.rain_states")),
      rainStatesInput,
    ]));
    rainSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [
        el("span", {}, this._t("settings.rain_attr")),
        rainAttrInput,
      ]),
      el("label", { class: "field" }, [
        el("span", {}, this._t("settings.rain_threshold")),
        rainThresholdInput,
      ]),
    ]));
    card.appendChild(rainSection);

    const notifySection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    notifySection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.notify")));
    notifySection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.notify_hint")));

    const availableTargets = this._state.notify_services || [];
    const availableEvents = this._state.notify_events || [];
    const currentTargets = new Set(Array.isArray(opts.notify_targets) ? opts.notify_targets : (opts.notify_targets ? String(opts.notify_targets).split(",").map(s => s.trim()).filter(Boolean) : []));
    const currentEvents = new Set(Array.isArray(opts.notify_events) ? opts.notify_events : (opts.notify_events ? String(opts.notify_events).split(",").map(s => s.trim()).filter(Boolean) : []));

    const targetsWrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:6px;max-height:160px;overflow:auto;padding:8px;border:1px solid var(--sw-border);border-radius:6px;background:var(--sw-bg);" });
    if (!availableTargets.length) {
      targetsWrap.appendChild(el("div", { class: "empty", style: "padding:4px;" }, this._t("settings.no_notify")));
    } else {
      availableTargets.forEach(name => {
        const lbl = el("label", { style: "display:flex;gap:6px;align-items:center;font-size:13px;padding:2px 6px;border:1px solid var(--sw-border);border-radius:4px;cursor:pointer;" });
        const cb = el("input", { type: "checkbox" });
        cb.checked = currentTargets.has(name);
        cb.addEventListener("change", () => {
          if (cb.checked) currentTargets.add(name);
          else currentTargets.delete(name);
        });
        lbl.appendChild(cb);
        lbl.appendChild(ltr(name));
        targetsWrap.appendChild(lbl);
      });
    }
    notifySection.appendChild(el("label", { class: "field" }, [
      el("span", {}, this._t("settings.notify_services")),
      targetsWrap,
    ]));

    const eventsWrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:6px;" });
    const eventLabel = (ev) => (this._t.has("event." + ev) ? this._t("event." + ev) : ev);
    availableEvents.forEach(ev => {
      const lbl = el("label", { style: "display:flex;gap:6px;align-items:center;font-size:13px;padding:2px 6px;border:1px solid var(--sw-border);border-radius:4px;cursor:pointer;" });
      const cb = el("input", { type: "checkbox" });
      cb.checked = currentEvents.has(ev);
      cb.addEventListener("change", () => {
        if (cb.checked) currentEvents.add(ev);
        else currentEvents.delete(ev);
      });
      lbl.appendChild(cb);
      lbl.appendChild(document.createTextNode(eventLabel(ev)));
      eventsWrap.appendChild(lbl);
    });
    notifySection.appendChild(el("label", { class: "field" }, [
      el("span", {}, this._t("settings.notify_when")),
      eventsWrap,
    ]));

    card.appendChild(notifySection);

    const seasonalSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    seasonalSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.seasonal")));
    const tempUnit = this._state.temperature_unit || "°";
    seasonalSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;line-height:1.45;" }, [
      el("span", {}, this._t("settings.seasonal_p1") + " "),
      el("span", {}, this._t("settings.seasonal_p2") + " "),
      el("br"),
      el("b", {}, this._t("settings.seasonal_how") + " "),
      el("span", {}, this._t("settings.seasonal_p3", { arrow: this._arrow() }) + " "),
      el("span", {}, this._t("settings.seasonal_p4") + " "),
      el("span", {}, this._t("settings.seasonal_p5")),
    ]));
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
        else { const t = (temp - low) / (high - low); pct = minP + t * (maxP - minP); }
        const example10 = Math.max(1, Math.round(10 * pct / 100));
        seasonalPreview.appendChild(el("span", {}, this._tn("settings.preview", {
          temp: ltr(`${temp}${tempUnit}`), arrow: this._arrow(), pct: pct.toFixed(0), n: example10,
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

    seasonalSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("common.enabled")), seasonalEnabledInput]));
    seasonalSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.temp_entity")), seasonalTempEntity]));
    seasonalSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.temp_attr")), seasonalTempAttr]));
    seasonalSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("settings.temp_low", { unit: tempUnit })), seasonalLow]),
      el("label", { class: "field" }, [el("span", {}, this._t("settings.temp_high", { unit: tempUnit })), seasonalHigh]),
    ]));
    seasonalSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("settings.min_pct")), seasonalMin]),
      el("label", { class: "field" }, [el("span", {}, this._t("settings.max_pct")), seasonalMax]),
    ]));
    seasonalSection.appendChild(seasonalPreview);
    card.appendChild(seasonalSection);

    const moistureSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    moistureSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.moisture")));
    moistureSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.moisture_hint")));
    const moistureEntity = el("input", { type: "text", dir: "ltr", placeholder: "sensor.garden_moisture", value: String(opts.moisture_entity || "") });
    const moistureAttr = el("input", { type: "text", placeholder: this._t("common.moisture_attr_ph"), value: String(opts.moisture_attribute || "") });
    const moistureThresholdRaw = (opts.moisture_threshold_skip_above === null || opts.moisture_threshold_skip_above === undefined) ? "" : String(opts.moisture_threshold_skip_above);
    const moistureThreshold = el("input", { type: "number", min: "0", max: "100", step: "0.5", value: moistureThresholdRaw });
    moistureSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.moisture_entity")), moistureEntity]));
    moistureSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("common.attribute_optional")), moistureAttr]),
      el("label", { class: "field" }, [el("span", {}, this._t("common.skip_when_gte")), moistureThreshold]),
    ]));
    card.appendChild(moistureSection);

    const overlapSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    overlapSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.overlap")));
    overlapSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.overlap_hint")));
    const allowConcurrent = el("input", { type: "checkbox" });
    allowConcurrent.checked = !!opts.allow_concurrent_cycles;
    overlapSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.allow_concurrent")), allowConcurrent]));
    card.appendChild(overlapSection);

    const masterSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    masterSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.master")));
    masterSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.master_hint")));
    const masterEntity = el("input", { type: "text", dir: "ltr", placeholder: "switch.water_pump", value: String(opts.master_valve_entity || "") });
    const masterPreOpen = el("input", { type: "number", min: "0", max: "600", value: String(opts.master_valve_pre_open_sec ?? 0) });
    masterSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.master_entity")), masterEntity]));
    masterSection.appendChild(el("label", { class: "field" }, [
      el("span", {}, this._t("settings.master_pre_open")),
      masterPreOpen,
    ]));
    card.appendChild(masterSection);

    const failSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    failSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.fail")));
    failSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.fail_hint")));
    const failEnabled = el("input", { type: "checkbox" });
    failEnabled.checked = !!opts.fail_detection_enabled;
    const failSeconds = el("input", { type: "number", min: "1", max: "120", value: String(opts.fail_detection_seconds ?? 5) });
    failSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("common.enabled")), failEnabled]));
    failSection.appendChild(el("label", { class: "field" }, [
      el("span", {}, this._t("settings.fail_window")),
      failSeconds,
    ]));
    card.appendChild(failSection);

    const flowSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);" + (showAdvanced ? "" : "display:none;"),
    });
    flowSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, this._t("settings.flow")));
    flowSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" }, this._t("settings.flow_hint")));
    const numVal = (v) => (v === null || v === undefined) ? "" : String(v);
    const flowEntity = el("input", { type: "text", dir: "ltr", placeholder: "sensor.water_flow", value: String(opts.flow_entity || "") });
    const flowAttr = el("input", { type: "text", placeholder: this._t("settings.flow_attr_ph"), value: String(opts.flow_attribute || "") });
    const flowLeak = el("input", { type: "number", min: "0", step: "0.1", value: numVal(opts.flow_leak_threshold ?? 0) });
    const flowMax = el("input", { type: "number", min: "0", step: "0.1", value: numVal(opts.flow_max_running ?? 0) });
    const flowDelay = el("input", { type: "number", min: "5", max: "3600", value: numVal(opts.flow_delay_sec ?? 60) });
    const flowStopAll = el("input", { type: "checkbox" });
    flowStopAll.checked = !!opts.flow_stop_all;
    flowSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("settings.flow_entity")), flowEntity]));
    flowSection.appendChild(el("label", { class: "field" }, [el("span", {}, this._t("common.attribute_optional")), flowAttr]));
    flowSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("settings.flow_leak")), flowLeak]),
      el("label", { class: "field" }, [el("span", {}, this._t("settings.flow_max")), flowMax]),
    ]));
    flowSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, this._t("settings.flow_delay")), flowDelay]),
      el("label", { class: "field" }, [el("span", {}, this._t("settings.flow_stop_all")), flowStopAll]),
    ]));
    card.appendChild(flowSection);

    const feedback = el("div", { class: "muted", style: "margin-top:8px;font-size:12px;" });
    const saveBtn = el("button", { class: "btn primary" }, this._t("settings.save"));
    saveBtn.addEventListener("click", async () => {
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
      const delayN = parseInt(flowDelay.value, 10);
      if (flowDelay.value.trim() !== "" && !isNaN(delayN)) flowNums.flow_delay_sec = Math.min(3600, Math.max(5, delayN));
      try {
        const result = await this._hass.callWS({
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

    card.appendChild(saveBtn);
    card.appendChild(feedback);
    root.appendChild(card);

    const webhookId = this._state.webhook_id || "";
    if (webhookId) {
      const webhookUrl = `${location.origin}/api/webhook/${webhookId}`;
      const webhookCard = el("div", { class: "card" });
      webhookCard.appendChild(el("h2", {}, this._t("settings.webhook")));
      webhookCard.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 8px;" }, this._t("settings.webhook_hint")));
      const urlInput = el("input", {
        type: "text",
        readonly: "readonly",
        dir: "ltr",
        value: webhookUrl,
        style: "width:100%;padding:6px 8px;border:1px solid var(--sw-border);border-radius:6px;background:var(--sw-bg);color:var(--sw-text);font-family:monospace;font-size:12px;",
        onClick: (e) => e.target.select(),
      });
      const copyBtn = el("button", {
        class: "btn",
        style: "margin-top:6px;font-size:12px;",
        onClick: async () => {
          try {
            await navigator.clipboard.writeText(webhookUrl);
            this._toast(this._t("common.copied"), "ok");
          } catch {
            urlInput.select();
            document.execCommand("copy");
            this._toast(this._t("common.copied"), "ok");
          }
        },
      }, this._t("settings.copy_url"));
      webhookCard.appendChild(urlInput);
      webhookCard.appendChild(copyBtn);
      root.appendChild(webhookCard);
    }

    const card2 = el("div", { class: "card" }, [
      el("h2", {}, this._t("settings.current")),
      el("pre", { dir: "ltr" }, JSON.stringify(opts, null, 2)),
      el("p", { class: "muted", style: "font-size:12px;margin-top:8px;" },
        this._t("settings.current_hint", { arrow: this._arrow() })),
    ]);
    root.appendChild(card2);
  }

  _showModal(title, fields, onSave) {
    this._modalRoot.innerHTML = "";
    const modal = el("div", { class: "modal" });
    modal.appendChild(el("h3", {}, title));
    fields.forEach((f) => modal.appendChild(f));

    const cancelBtn = el("button", { class: "btn", onClick: () => { this._modalRoot.innerHTML = ""; } }, this._t("common.cancel"));
    const saveBtn = el("button", { class: "btn primary", onClick: async () => {
      saveBtn.disabled = true;
      try {
        const ok = await onSave();
        if (ok) this._modalRoot.innerHTML = "";
      } finally {
        saveBtn.disabled = false;
      }
    } }, this._t("common.save"));

    modal.appendChild(el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]));

    const overlay = el("div", { class: "modal-overlay" }, modal);
    overlay.addEventListener("click", (e) => { if (e.target === overlay) this._modalRoot.innerHTML = ""; });
    this._modalRoot.appendChild(overlay);
  }
}

if (!customElements.get("schedule-wizard-panel")) {
  customElements.define("schedule-wizard-panel", ScheduleWizardPanel);
}
