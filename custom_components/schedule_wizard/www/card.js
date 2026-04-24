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
  grid-template-columns: 1fr auto auto auto;
  gap: 8px;
  align-items: center;
  padding: 6px 0;
  border-top: 1px solid var(--divider-color, #e5e7eb);
}
.row:first-of-type { border-top: none; }
.name { font-weight: 500; font-size: 14px; }
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

function fmtRemaining(s) {
  if (s <= 0) return "0:00";
  const m = Math.floor(s / 60);
  const r = String(s % 60).padStart(2, "0");
  return `${m}:${r}`;
}

class ScheduleWizardCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._state = null;
    this._timer = null;
    this._initialized = false;
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
    if (!this._initialized) this._init();
  }

  connectedCallback() {
    if (this._hass && !this._initialized) this._init();
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
      const focused = this.shadowRoot && this.shadowRoot.activeElement;
      if (focused && (focused.tagName === "INPUT" || focused.tagName === "TEXTAREA")) {
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
      const row = b.closest(".row");
      if (!row) return;
      const name = row.querySelector(".name");
      if (!name) return;
      const label = name.textContent.replace(/\s*●\s*$/, "").trim();
      const active = this._state.active.find(r => {
        const valve = this._state.valves.find(v => v.entity_id === r.entity_id);
        return (valve ? valve.label : r.entity_id) === label;
      });
      if (!active) return;
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - this._state.now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      b.style.width = `${pct}%`;
    });
  }

  _renderError(e) {
    this._root.innerHTML = "";
    this._root.appendChild(el("div", { class: "card" }, [
      el("div", { class: "title" }, this._config.title || "Schedule Wizard"),
      el("div", { class: "empty" }, "Failed to load: " + (e.message || "unknown")),
    ]));
  }

  _render() {
    if (!this._state || !this._root) return;
    this._root.innerHTML = "";

    const allowedEntities = Array.isArray(this._config.valves) ? new Set(this._config.valves) : null;
    const filteredValves = allowedEntities
      ? this._state.valves.filter(v => allowedEntities.has(v.entity_id))
      : this._state.valves;

    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "title" }, [
      el("span", {}, this._config.title || "Schedule Wizard"),
      el("span", { class: "pill " + (this._state.active.length ? "ok" : "") },
        this._state.active.length ? `${this._state.active.length} running` : "idle"),
    ]));

    if (this._config.show_active !== false && this._state.active.length) {
      const activeDiv = el("div", { class: "active-runs" });
      this._state.active
        .filter(r => !allowedEntities || allowedEntities.has(r.entity_id))
        .forEach(r => activeDiv.appendChild(this._activeRow(r)));
      card.appendChild(activeDiv);
    }

    if (this._config.show_quick_run !== false) {
      if (!filteredValves.length) {
        card.appendChild(el("div", { class: "empty" }, "No valves configured."));
      } else {
        filteredValves.forEach(v => card.appendChild(this._valveRow(v)));
      }
    }

    this._root.appendChild(card);
  }

  _activeRow(r) {
    const now = this._state.now;
    const remaining = Math.max(0, r.ends_at - now);
    const total = Math.max(1, r.ends_at - r.started_at);
    const pct = Math.min(100, ((total - remaining) / total) * 100);
    const valve = this._state.valves.find(v => v.entity_id === r.entity_id);
    const label = valve ? valve.label : r.entity_id;
    return el("div", { class: "row" }, [
      el("div", {}, [
        el("div", { class: "name" }, `● ${label}`),
        el("div", { class: "sub" }, `${fmtRemaining(remaining)} remaining · ${r.source}`),
      ]),
      el("div"),
      el("div"),
      el("button", {
        class: "stop",
        onClick: () => this._callService("stop_valve", { entity_id: r.entity_id }),
      }, "Stop"),
      el("div", { class: "progress-wrap" }, el("div", { class: "progress-bar", style: `width:${pct}%` })),
    ]);
  }

  _valveRow(v) {
    const active = this._state.active.find(r => r.entity_id === v.entity_id);
    const now = this._state.now;
    const minsInput = el("input", { type: "number", min: "1", max: "1440", value: String(v.default_duration_min) });
    const subLines = [
      active
        ? `${fmtRemaining(Math.max(0, active.ends_at - now))} remaining`
        : `default ${v.default_duration_min}m`,
    ];
    if (!active && v.next_run) {
      const inMin = Math.max(0, Math.round(v.next_run.in_seconds / 60));
      const inLabel = inMin < 60 ? `in ${inMin}m` : inMin < 1440 ? `in ${Math.round(inMin / 60)}h` : `in ${Math.round(inMin / 1440)}d`;
      subLines.push(`Next: ${v.next_run.time_label} (${inLabel})`);
    }
    const metaInner = [el("div", { class: "name" }, v.label + (active ? " ●" : ""))];
    subLines.forEach(s => metaInner.push(el("div", { class: "sub" }, s)));
    const children = [
      el("div", {}, metaInner),
      minsInput,
      el("button", {
        class: "run",
        disabled: active ? true : false,
        onClick: () => this._callService("run_valve", {
          entity_id: v.entity_id,
          duration_minutes: parseInt(minsInput.value, 10) || v.default_duration_min,
        }),
      }, "Run"),
      el("button", {
        class: "stop",
        onClick: () => this._callService("stop_valve", { entity_id: v.entity_id }),
      }, "Stop"),
    ];
    if (active) {
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      children.push(el("div", { class: "progress-wrap" },
        el("div", { class: "progress-bar", style: `width:${pct}%` })
      ));
    }
    return el("div", { class: "row" }, children);
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("schedule_wizard", service, data);
      setTimeout(() => this._refresh(), 300);
    } catch (e) {
      console.error("schedule_wizard card:", e);
    }
  }
}

if (!customElements.get("schedule-wizard-card")) {
  customElements.define("schedule-wizard-card", ScheduleWizardCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "schedule-wizard-card",
    name: "Schedule Wizard",
    description: "Dashboard card for Schedule Wizard — active runs + quick run.",
    preview: false,
  });
}
