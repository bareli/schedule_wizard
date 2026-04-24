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
.row-between { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
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
.toast {
  position: fixed; bottom: 20px; left: 50%;
  transform: translateX(-50%);
  padding: 10px 16px; background: var(--sw-text); color: var(--sw-bg);
  border-radius: 6px; font-size: 13px;
  z-index: 200; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.toast.error { background: var(--sw-danger); color: #fff; }
.toast.ok { background: var(--sw-success); color: #fff; }
pre { background: var(--sw-bg); padding: 10px; border-radius: 6px; font-size: 12px; overflow-x: auto; }
`;

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
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

function fmtTime(ts) {
  if (!ts) return "";
  return new Date(ts * 1000).toLocaleString();
}

function fmtRemaining(secs) {
  if (secs <= 0) return "0:00";
  const m = Math.floor(secs / 60);
  const s = String(secs % 60).padStart(2, "0");
  return `${m}:${s}`;
}

function daysFromMask(mask) {
  return DAY_LABELS.filter((_, i) => mask & DAY_BITS[i]).join(",") || "—";
}

function maskFromDays(days) {
  let mask = 0;
  for (const d of days) {
    const i = DAYS.indexOf(d);
    if (i >= 0) mask |= DAY_BITS[i];
  }
  return mask;
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
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) this._init();
  }
  set narrow(v) { this._narrow = v; }
  set route(v) { this._route = v; }
  set panel(v) { this._panel = v; }

  connectedCallback() {
    if (this._hass && !this._initialized) this._init();
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
    this._refresh();
    this._refreshTimer = setInterval(() => this._refresh(), 5000);
  }

  async _refresh() {
    try {
      this._state = await this._hass.callWS({ type: "schedule_wizard/get_state" });
      if (this._tab === "settings") return;
      const focused = document.activeElement;
      if (focused && (focused.tagName === "INPUT" || focused.tagName === "TEXTAREA" || focused.tagName === "SELECT") && this.contains(focused)) {
        this._updateInPlace();
        return;
      }
      this._render();
    } catch (e) {
      this._renderError(e);
    }
  }

  _updateInPlace() {
    const pills = this.querySelectorAll(".pill");
    if (pills && pills[0]) {
      pills[0].textContent = `${this._state.valves.length} valves, ${this._state.active.length} active`;
      pills[0].className = "pill " + (this._state.active.length ? "ok" : "");
    }
    const bars = this.querySelectorAll(".progress-bar");
    bars.forEach(b => {
      const row = b.closest(".item");
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
    const app = this.querySelector("#app");
    if (!app) return;
    app.innerHTML = "";
    app.appendChild(el("div", { class: "card" }, [
      el("h2", {}, "Schedule Wizard"),
      el("div", { class: "muted" }, "Failed to load: " + (e.message || e.code || "unknown")),
    ]));
  }

  _toast(msg, kind = "") {
    const t = el("div", { class: "toast " + kind }, msg);
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2800);
  }

  _fmtAgo(secs) {
    if (secs < 60) return `${secs}s ago`;
    const m = Math.floor(secs / 60);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    const d = Math.floor(h / 24);
    return `${d}d ago`;
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("schedule_wizard", service, data);
      this._toast("Done", "ok");
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
    app.innerHTML = "";

    const top = el("div", { class: "topbar" }, [
      el("h1", {}, "Schedule Wizard"),
      el("span", { class: "pill " + (this._state.active.length ? "ok" : "") },
        `${this._state.valves.length} valves, ${this._state.active.length} active`),
    ]);
    app.appendChild(top);

    const tabs = el("div", { class: "tabs" });
    [["dashboard", "Dashboard"], ["valves", "Valves"], ["cycles", "Cycles"], ["schedules", "Schedules"], ["settings", "Settings"]]
      .forEach(([key, label]) => {
        const btn = el("button", {
          class: "tab" + (this._tab === key ? " active" : ""),
          onClick: () => { this._tab = key; this._render(); },
        }, label);
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
      case "settings": this._renderSettings(content); break;
    }
  }

  _renderDashboard(root) {
    const activeCycles = this._state.active_cycles || [];
    if (activeCycles.length) {
      const cyclesCard = el("div", { class: "card" }, [el("h2", {}, "Active cycles")]);
      const cyclesList = el("div", { class: "list" });
      activeCycles.forEach((c) => cyclesList.appendChild(this._activeCycleRow(c)));
      cyclesCard.appendChild(cyclesList);
      root.appendChild(cyclesCard);
    }

    const active = el("div", { class: "card" }, [el("h2", {}, "Active runs")]);
    const list = el("div", { class: "list" });
    if (!this._state.active.length) {
      list.appendChild(el("div", { class: "empty" }, "No active runs."));
    } else {
      this._state.active.forEach((r) => list.appendChild(this._activeRunRow(r)));
    }
    active.appendChild(list);
    root.appendChild(active);

    const quick = el("div", { class: "card" }, [el("h2", {}, "Quick run")]);
    const qList = el("div", { class: "list" });
    if (!this._state.valves.length) {
      qList.appendChild(el("div", { class: "empty" }, "Add valves first."));
    } else {
      this._state.valves.forEach((v) => qList.appendChild(this._quickRunRow(v)));
    }
    quick.appendChild(qList);
    root.appendChild(quick);

    const hist = el("div", { class: "card" }, [el("h2", {}, "Recent activity")]);
    const hList = el("div", { class: "list" });
    if (!this._state.history.length) {
      hList.appendChild(el("div", { class: "empty" }, "No history yet."));
    } else {
      this._state.history.slice(0, 12).forEach((r) => hList.appendChild(this._historyRow(r)));
    }
    hist.appendChild(hList);
    root.appendChild(hist);
  }

  _activeRunRow(r) {
    const now = this._state.now;
    const remaining = Math.max(0, r.ends_at - now);
    const total = Math.max(1, r.ends_at - r.started_at);
    const pct = Math.min(100, ((total - remaining) / total) * 100);
    const valve = this._state.valves.find((v) => v.entity_id === r.entity_id);
    const label = valve ? valve.label : r.entity_id;

    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, label),
        el("div", { class: "sub" }, `${r.entity_id} • ${r.source} • ${fmtRemaining(remaining)} left`),
        el("div", { class: "progress-wrap" }, el("div", { class: "progress-bar", style: `width:${pct}%` })),
      ]),
      el("div", { class: "actions" }, [
        el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_valve", { entity_id: r.entity_id }),
        }, "Stop"),
      ]),
    ]);
  }

  _quickRunRow(v) {
    const active = this._state.active.find(r => r.entity_id === v.entity_id);
    const now = this._state.now;
    const minsInput = el("input", {
      type: "number", min: "1", max: "1440",
      value: String(v.default_duration_min),
      style: "width:70px;",
    });
    const meta = el("div", {}, [
      el("div", { class: "name" }, v.label + (active ? "  ●" : "")),
      el("div", { class: "sub" },
        active
          ? `${v.entity_id} • ${fmtRemaining(Math.max(0, active.ends_at - now))} remaining (${active.source})`
          : `${v.entity_id} • default ${v.default_duration_min}m`
      ),
    ]);
    if (active) {
      const total = Math.max(1, active.ends_at - active.started_at);
      const remaining = Math.max(0, active.ends_at - now);
      const pct = Math.min(100, ((total - remaining) / total) * 100);
      meta.appendChild(el("div", { class: "progress-wrap" },
        el("div", { class: "progress-bar", style: `width:${pct}%` })
      ));
    }
    return el("div", { class: "item" }, [
      meta,
      el("div", { class: "actions" }, [
        minsInput,
        el("button", {
          class: "btn primary small",
          onClick: () => this._callService("run_valve", {
            entity_id: v.entity_id,
            duration_minutes: parseInt(minsInput.value, 10) || v.default_duration_min,
          }),
        }, "Run"),
        el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_valve", { entity_id: v.entity_id }),
        }, "Stop"),
      ]),
    ]);
  }

  _historyRow(r) {
    const valve = this._state.valves.find((v) => v.entity_id === r.valve_entity_id);
    const label = valve ? valve.label : r.valve_entity_id;
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, label),
        el("div", { class: "sub" },
          `${fmtTime(r.ts)} • ${r.duration_min}m • ${r.source} • ${r.status}`),
      ]),
      el("div"),
    ]);
  }

  _renderValves(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "row-between" }, [
      el("h2", {}, "Valves"),
      el("button", {
        class: "btn primary",
        onClick: () => this._openValveModal(null),
      }, "+ Add valve"),
    ]));
    const list = el("div", { class: "list" });
    if (!this._state.valves.length) {
      list.appendChild(el("div", { class: "empty" }, "No valves yet. Add one to begin."));
    } else {
      this._state.valves.forEach((v) => list.appendChild(this._valveRow(v)));
    }
    card.appendChild(list);
    root.appendChild(card);
  }

  _valveRow(v) {
    const stats = v.stats || {};
    let lastLine = "Never run";
    if (stats.last_run) {
      const ago = Math.max(0, this._state.now - stats.last_run.ts);
      lastLine = `Last: ${this._fmtAgo(ago)} • ${stats.last_run.duration_min}m • ${stats.last_run.status}`;
    }
    const week = stats.runs_7d
      ? `${stats.runs_7d} runs / ${stats.total_min_7d}m last 7 days`
      : "no runs last 7 days";
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, v.label + (v.enabled ? "" : " (disabled)")),
        el("div", { class: "sub" }, `${v.entity_id} • ${v.default_duration_min}m default`),
        el("div", { class: "sub", style: "margin-top:2px;" }, lastLine + " • " + week),
      ]),
      el("div", { class: "actions" }, [
        el("button", { class: "btn small", onClick: () => this._openValveModal(v) }, "Edit"),
        el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm(`Delete valve "${v.label}"? Schedules attached will be removed too.`)) return;
            this._callService("remove_valve", { entity_id: v.entity_id });
          },
        }, "Delete"),
      ]),
    ]);
  }

  _openValveModal(existing) {
    let chosen = existing ? existing.entity_id : "";
    let label = existing ? existing.label : "";
    let duration = existing ? existing.default_duration_min : (this._state.options.default_duration || 10);
    let enabled = existing ? !!existing.enabled : true;

    const labelInput = el("input", { type: "text", value: label, placeholder: "e.g. Front lawn" });
    labelInput.addEventListener("input", () => { label = labelInput.value; });

    const durInput = el("input", { type: "number", min: "1", max: "1440", value: String(duration) });
    durInput.addEventListener("input", () => { duration = parseInt(durInput.value, 10) || 10; });

    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const search = el("input", { type: "text", placeholder: "Search entity..." });
    const picker = el("div", { class: "entity-picker" });
    const renderPicker = () => {
      const q = search.value.trim().toLowerCase();
      picker.innerHTML = "";
      const filtered = this._state.controllable.filter((e) =>
        !q || e.entity_id.toLowerCase().includes(q) || e.friendly_name.toLowerCase().includes(q)
      );
      if (!filtered.length) {
        picker.appendChild(el("div", { class: "empty", style: "padding:10px;" }, "No matches."));
      }
      filtered.forEach((e) => {
        const row = el("div", { class: "entity-row" + (chosen === e.entity_id ? " selected" : "") }, [
          el("div", {}, [
            el("div", { style: "font-weight:600" }, e.friendly_name),
            el("div", { class: "muted", style: "font-size:12px" }, e.entity_id),
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

    const fields = [
      el("label", { class: "field" }, [el("span", {}, "Search entity"), search, picker]),
      el("label", { class: "field" }, [el("span", {}, "Label (used for calendar matching)"), labelInput]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Default duration (min)"), durInput]),
        el("label", { class: "field" }, [el("span", {}, "Enabled"), enabledInput]),
      ]),
    ];

    this._showModal(existing ? "Edit valve" : "Add valve", fields, async () => {
      if (!chosen) { this._toast("Pick an entity", "error"); return false; }
      if (!label.trim()) { this._toast("Label required", "error"); return false; }
      const ok = await this._callService("add_valve", {
        entity_id: chosen,
        label: label.trim(),
        default_duration_minutes: duration,
        enabled,
      });
      if (existing && existing.entity_id !== chosen) {
        await this._callService("remove_valve", { entity_id: existing.entity_id });
      }
      return ok;
    });
  }

  _activeCycleRow(c) {
    const valve = this._state.valves.find(v => v.entity_id === c.current_entity);
    const currentLabel = valve ? valve.label : (c.current_entity || "—");
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, `● ${c.cycle_name || c.cycle_id}`),
        el("div", { class: "sub" },
          `step ${c.step}/${c.total_steps} • ${currentLabel} • ${c.source}`
        ),
      ]),
      el("div", { class: "actions" }, [
        el("button", {
          class: "btn danger small",
          onClick: () => this._callService("stop_cycle", { cycle_id: c.cycle_id }),
        }, "Stop"),
      ]),
    ]);
  }

  _renderCycles(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "row-between" }, [
      el("h2", {}, "Cycles"),
      el("button", {
        class: "btn primary",
        onClick: () => this._openCycleModal(null),
      }, "+ Add cycle"),
    ]));
    const list = el("div", { class: "list" });
    const cycles = this._state.cycles || [];
    if (!cycles.length) {
      list.appendChild(el("div", { class: "empty" },
        "No cycles yet. A cycle runs multiple valves one after another (e.g. zone 1 → zone 2 → zone 3)."
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
    const stepLabels = steps.map(s => `${valvesMap[s.entity_id] || s.entity_id} ${s.duration_min}m`).join(" → ");
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, (c.name || c.id) + (c.enabled ? "" : " (disabled)") + (active ? " ● running" : "")),
        el("div", { class: "sub" }, `${steps.length} steps • total ${totalMin}m`),
        el("div", { class: "sub", style: "margin-top:2px;" }, stepLabels),
      ]),
      el("div", { class: "actions" }, [
        active
          ? el("button", {
              class: "btn danger small",
              onClick: () => this._callService("stop_cycle", { cycle_id: c.id }),
            }, "Stop")
          : el("button", {
              class: "btn primary small",
              onClick: () => this._callService("run_cycle", { cycle_id: c.id }),
            }, "Run"),
        el("button", {
          class: "btn small",
          onClick: () => this._openCycleModal(c),
        }, "Edit"),
        el("button", {
          class: "btn small",
          onClick: () => this._callService("update_cycle", { cycle_id: c.id, enabled: !c.enabled }),
        }, c.enabled ? "Disable" : "Enable"),
        el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm(`Delete cycle "${c.name}"?`)) return;
            this._callService("remove_cycle", { cycle_id: c.id });
          },
        }, "Delete"),
      ]),
    ]);
  }

  _openCycleModal(existing) {
    if (!this._state.valves.length) { this._toast("Add a valve first", "error"); return; }

    let name = existing ? existing.name : "";
    let enabled = existing ? !!existing.enabled : true;
    let steps = existing ? JSON.parse(JSON.stringify(existing.steps || [])) : [];
    if (!steps.length) {
      const v = this._state.valves[0];
      steps.push({ entity_id: v.entity_id, duration_min: v.default_duration_min });
    }

    const nameInput = el("input", { type: "text", value: name, placeholder: "e.g. Morning irrigation" });
    nameInput.addEventListener("input", () => { name = nameInput.value; });

    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const stepsWrap = el("div");
    const renderSteps = () => {
      stepsWrap.innerHTML = "";
      steps.forEach((s, idx) => {
        const sel = el("select", {});
        this._state.valves.forEach(v => {
          const opt = el("option", { value: v.entity_id }, `${v.label} (${v.entity_id})`);
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
            onClick: () => {
              [steps[idx - 1], steps[idx]] = [steps[idx], steps[idx - 1]];
              renderSteps();
            },
          }, "▲"),
          el("button", {
            class: "btn danger small",
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
      }, "+ Add step"));
    };
    renderSteps();

    const fields = [
      el("label", { class: "field" }, [el("span", {}, "Name"), nameInput]),
      el("div", { class: "field" }, [el("span", {}, "Steps (sequential)"), stepsWrap]),
      el("label", { class: "field" }, [el("span", {}, "Enabled"), enabledInput]),
    ];

    this._showModal(existing ? "Edit cycle" : "Add cycle", fields, async () => {
      if (!name.trim()) { this._toast("Name required", "error"); return false; }
      if (!steps.length) { this._toast("At least one step", "error"); return false; }
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
      el("h2", {}, "Schedules"),
      el("button", {
        class: "btn primary",
        onClick: () => this._openScheduleModal(null),
      }, "+ Add schedule"),
    ]));
    const list = el("div", { class: "list" });
    if (!this._state.schedules.length) {
      list.appendChild(el("div", { class: "empty" }, "No schedules yet."));
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
      targetName = cycle ? `cycle: ${cycle.name}` : `cycle: ${s.cycle_id}`;
      targetDuration = cycle ? `${(cycle.steps || []).reduce((a, x) => a + (x.duration_min || 0), 0)}m total` : "";
    } else {
      const valve = this._state.valves.find(v => v.entity_id === s.valve_entity_id);
      targetName = valve ? valve.label : s.valve_entity_id;
      targetDuration = `${s.duration_min}m`;
    }
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, (s.name || `${targetName} @ ${s.time_hhmm}`) + (s.enabled ? "" : " (disabled)")),
        el("div", { class: "sub" }, `${targetName} • ${s.time_hhmm} • ${daysFromMask(s.days_mask)} • ${targetDuration}`),
      ]),
      el("div", { class: "actions" }, [
        el("button", {
          class: "btn small",
          onClick: () => this._openScheduleModal(s),
        }, "Edit"),
        el("button", {
          class: "btn small",
          onClick: () => this._callService("update_schedule", { schedule_id: s.id, enabled: !s.enabled }),
        }, s.enabled ? "Disable" : "Enable"),
        el("button", {
          class: "btn danger small",
          onClick: () => {
            if (!confirm("Delete schedule?")) return;
            this._callService("remove_schedule", { schedule_id: s.id });
          },
        }, "Delete"),
      ]),
    ]);
  }

  _openScheduleModal(existing) {
    const hasValves = this._state.valves.length > 0;
    const hasCycles = (this._state.cycles || []).length > 0;
    if (!hasValves && !hasCycles) { this._toast("Add a valve or cycle first", "error"); return; }

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
    if (hasValves) targetSel.appendChild(el("option", { value: "valve" }, "Single valve"));
    if (hasCycles) targetSel.appendChild(el("option", { value: "cycle" }, "Cycle (multi-valve)"));
    targetSel.value = targetKind;
    targetSel.addEventListener("change", () => { targetKind = targetSel.value; renderTargetField(); });

    const targetFieldHost = el("div");
    const valveSel = el("select", existing ? { disabled: "disabled" } : {});
    this._state.valves.forEach(v => {
      const opt = el("option", { value: v.entity_id }, `${v.label} (${v.entity_id})`);
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
        targetFieldHost.appendChild(el("label", { class: "field" }, [el("span", {}, "Cycle"), cycleSel]));
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, "Time"), timeInput]));
      } else {
        targetFieldHost.appendChild(el("label", { class: "field" }, [el("span", {}, "Valve"), valveSel]));
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, "Time"), timeInput]));
        durRow.appendChild(el("label", { class: "field" }, [el("span", {}, "Duration (min)"), durInput]));
      }
    };
    renderTargetField();

    const nameInput = el("input", { type: "text", value: name, placeholder: "Optional" });
    nameInput.addEventListener("input", () => { name = nameInput.value; });

    const enabledInput = el("input", { type: "checkbox" });
    enabledInput.checked = enabled;
    enabledInput.addEventListener("change", () => { enabled = enabledInput.checked; });

    const days = el("div", { class: "days" });
    DAY_LABELS.forEach((d, i) => {
      const tog = el("div", { class: "day-toggle" + ((mask & DAY_BITS[i]) ? " on" : "") }, d);
      tog.addEventListener("click", () => {
        mask ^= DAY_BITS[i];
        tog.classList.toggle("on", !!(mask & DAY_BITS[i]));
      });
      days.appendChild(tog);
    });

    const fields = [
      el("label", { class: "field" }, [el("span", {}, "Target"), targetSel]),
      targetFieldHost,
      durRow,
      el("label", { class: "field" }, [el("span", {}, "Name"), nameInput]),
      el("div", { class: "field" }, [el("span", {}, "Days"), days]),
      el("label", { class: "field" }, [el("span", {}, "Enabled"), enabledInput]),
    ];

    this._showModal(existing ? "Edit schedule" : "Add schedule", fields, async () => {
      if (!mask) { this._toast("Pick at least one day", "error"); return false; }
      if (existing) {
        return await this._callService("update_schedule", {
          schedule_id: existing.id,
          name,
          time,
          duration_minutes: targetKind === "valve" ? duration : 1,
          days: daysFromMaskNames(mask),
          enabled,
        });
      }
      const base = {
        time,
        days: daysFromMaskNames(mask),
        name,
        enabled,
      };
      if (targetKind === "cycle") {
        return await this._callService("add_schedule", { ...base, cycle_id: cycleId, duration_minutes: 1 });
      }
      return await this._callService("add_schedule", { ...base, valve_entity_id: valveEntity, duration_minutes: duration });
    });
  }

  _renderSettings(root) {
    const opts = this._state.options || {};

    const card = el("div", { class: "card" }, [el("h2", {}, "Calendar integration")]);
    card.appendChild(el("p", { class: "muted" },
      "Pick an HA calendar. Events whose summary contains a valve label will trigger that valve. " +
      "Put the duration in minutes in the event description."
    ));

    const calSel = el("select", {});
    calSel.appendChild(el("option", { value: "" }, "(none)"));
    this._state.calendars.forEach((c) => {
      const opt = el("option", { value: c.entity_id }, `${c.friendly_name} (${c.entity_id})`);
      if (c.entity_id === (opts.calendar_entity || "")) opt.selected = true;
      calSel.appendChild(opt);
    });

    const lookInput = el("input", { type: "number", min: "1", max: "1440", value: String(opts.calendar_lookahead_min || 10) });
    const pollInput = el("input", { type: "number", min: "10", max: "3600", value: String(opts.poll_interval || 60) });
    const defDurInput = el("input", { type: "number", min: "1", max: "1440", value: String(opts.default_duration || 10) });
    const rainEntityInput = el("input", { type: "text", placeholder: "weather.home or sensor.rain_forecast", value: String(opts.rain_entity || "") });
    const rainStatesInput = el("input", { type: "text", placeholder: "rainy,pouring,snowy,lightning-rainy", value: String(opts.rain_skip_states || "") });
    const rainAttrInput = el("input", { type: "text", placeholder: "precipitation (optional)", value: String(opts.rain_attribute || "") });
    const rainThresholdInput = el("input", { type: "number", min: "0", max: "100", step: "0.1", value: opts.rain_threshold != null ? String(opts.rain_threshold) : "" });

    card.appendChild(el("label", { class: "field" }, [el("span", {}, "Calendar entity"), calSel]));
    card.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, "Lookahead (minutes)"), lookInput]),
      el("label", { class: "field" }, [el("span", {}, "Poll interval (seconds)"), pollInput]),
    ]));
    card.appendChild(el("label", { class: "field" }, [el("span", {}, "Default duration (minutes)"), defDurInput]));

    const rainSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);",
    });
    rainSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, "Rain skip"));
    rainSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" },
      "Optional. Skips cron schedules when the selected entity matches any skip state, or its numeric value exceeds the threshold. Calendar and manual runs are not affected."
    ));
    rainSection.appendChild(el("label", { class: "field" }, [
      el("span", {}, "Rain / weather entity"),
      rainEntityInput,
    ]));
    rainSection.appendChild(el("label", { class: "field" }, [
      el("span", {}, "Skip when state is (comma-separated)"),
      rainStatesInput,
    ]));
    rainSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [
        el("span", {}, "Attribute to check (optional)"),
        rainAttrInput,
      ]),
      el("label", { class: "field" }, [
        el("span", {}, "Numeric threshold (blank = disabled)"),
        rainThresholdInput,
      ]),
    ]));
    card.appendChild(rainSection);

    const notifySection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);",
    });
    notifySection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, "Notifications"));
    notifySection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" },
      "Pick one or more notify services (e.g. your mobile app) and tick which events should send a notification."
    ));

    const availableTargets = this._state.notify_services || [];
    const availableEvents = this._state.notify_events || [];
    const currentTargets = new Set(Array.isArray(opts.notify_targets) ? opts.notify_targets : (opts.notify_targets ? String(opts.notify_targets).split(",").map(s => s.trim()).filter(Boolean) : []));
    const currentEvents = new Set(Array.isArray(opts.notify_events) ? opts.notify_events : (opts.notify_events ? String(opts.notify_events).split(",").map(s => s.trim()).filter(Boolean) : []));

    const targetsWrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:6px;max-height:160px;overflow:auto;padding:8px;border:1px solid var(--sw-border);border-radius:6px;background:var(--sw-bg);" });
    if (!availableTargets.length) {
      targetsWrap.appendChild(el("div", { class: "empty", style: "padding:4px;" }, "No notify.* services detected."));
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
        lbl.appendChild(document.createTextNode(name));
        targetsWrap.appendChild(lbl);
      });
    }
    notifySection.appendChild(el("label", { class: "field" }, [
      el("span", {}, "Notify services (e.g. notify.mobile_app_your_phone)"),
      targetsWrap,
    ]));

    const eventsWrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:6px;" });
    const EVENT_LABELS = {
      valve_start: "Valve opened",
      valve_end: "Valve closed",
      cycle_start: "Cycle started",
      cycle_end: "Cycle ended",
      skipped_rain: "Skipped (rain)",
    };
    availableEvents.forEach(ev => {
      const lbl = el("label", { style: "display:flex;gap:6px;align-items:center;font-size:13px;padding:2px 6px;border:1px solid var(--sw-border);border-radius:4px;cursor:pointer;" });
      const cb = el("input", { type: "checkbox" });
      cb.checked = currentEvents.has(ev);
      cb.addEventListener("change", () => {
        if (cb.checked) currentEvents.add(ev);
        else currentEvents.delete(ev);
      });
      lbl.appendChild(cb);
      lbl.appendChild(document.createTextNode(EVENT_LABELS[ev] || ev));
      eventsWrap.appendChild(lbl);
    });
    notifySection.appendChild(el("label", { class: "field" }, [
      el("span", {}, "Send notification when"),
      eventsWrap,
    ]));

    card.appendChild(notifySection);

    const seasonalSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);",
    });
    seasonalSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, "Seasonal adjustment (temperature-based)"));
    const tempUnit = this._state.temperature_unit || "°";
    seasonalSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;line-height:1.45;" }, [
      el("span", {}, "Scales schedule & calendar durations by the outside temperature. "),
      el("span", {}, `Runs shrink in cool weather, grow in heat. Manual runs are NOT scaled. `),
      el("br"),
      el("b", {}, "How it works: "),
      el("span", {}, `when temp ≤ Low → runs use Min %. When temp ≥ High → runs use Max %. `),
      el("span", {}, `Between Low and High the percentage scales linearly. `),
      el("span", {}, `Example: a 10 min schedule with factor 78% runs for 8 min.`),
    ]));
    const seasonalEnabledInput = el("input", { type: "checkbox" });
    seasonalEnabledInput.checked = !!opts.seasonal_enabled;
    const seasonalTempEntity = el("input", { type: "text", placeholder: "weather.forecast_home or sensor.outdoor_temp", value: String(opts.seasonal_temp_entity || "") });
    const seasonalTempAttr = el("input", { type: "text", placeholder: "temperature (if entity is weather.*)", value: String(opts.seasonal_temp_attribute || "") });
    const seasonalLow = el("input", { type: "number", step: "0.5", value: String(opts.seasonal_temp_low ?? 10) });
    const seasonalHigh = el("input", { type: "number", step: "0.5", value: String(opts.seasonal_temp_high ?? 30) });
    const seasonalMin = el("input", { type: "number", min: "0", max: "200", value: String(opts.seasonal_min_pct ?? 50) });
    const seasonalMax = el("input", { type: "number", min: "0", max: "200", value: String(opts.seasonal_max_pct ?? 120) });

    const seasonalPreview = el("div", {
      style: "margin-top:8px;padding:8px 10px;border-radius:6px;background:var(--sw-bg);border:1px solid var(--sw-border);font-size:13px;",
    });
    const computePreview = () => {
      seasonalPreview.innerHTML = "";
      const entityId = seasonalTempEntity.value.trim();
      if (!entityId) { seasonalPreview.appendChild(el("span", { class: "muted" }, "Set a temperature entity to see a live preview.")); return; }
      const attr = seasonalTempAttr.value.trim();
      this._hass.callWS({ type: "get_states" }).then(states => {
        const s = states.find(x => x.entity_id === entityId);
        if (!s) { seasonalPreview.appendChild(el("span", { style: "color:var(--sw-danger)" }, `Entity ${entityId} not found.`)); return; }
        let temp = null;
        try { temp = parseFloat(attr ? s.attributes[attr] : s.state); } catch {}
        if (temp == null || isNaN(temp)) { seasonalPreview.appendChild(el("span", { style: "color:var(--sw-danger)" }, `Value not numeric (state=${s.state}).`)); return; }
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
        seasonalPreview.appendChild(el("span", {}, `Current: ${temp}${tempUnit} → factor ${pct.toFixed(0)}% → 10 min schedule would run ${example10} min`));
      }).catch(() => {
        seasonalPreview.appendChild(el("span", { class: "muted" }, "Could not read state."));
      });
    };
    [seasonalTempEntity, seasonalTempAttr, seasonalLow, seasonalHigh, seasonalMin, seasonalMax].forEach(i => i.addEventListener("input", computePreview));
    computePreview();

    seasonalSection.appendChild(el("label", { class: "field" }, [el("span", {}, "Enabled"), seasonalEnabledInput]));
    seasonalSection.appendChild(el("label", { class: "field" }, [el("span", {}, "Temperature entity"), seasonalTempEntity]));
    seasonalSection.appendChild(el("label", { class: "field" }, [el("span", {}, "Attribute (optional; e.g. 'temperature' for weather.*)"), seasonalTempAttr]));
    seasonalSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, `Low temp (${tempUnit})`), seasonalLow]),
      el("label", { class: "field" }, [el("span", {}, `High temp (${tempUnit})`), seasonalHigh]),
    ]));
    seasonalSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, "Min % (at or below low temp)"), seasonalMin]),
      el("label", { class: "field" }, [el("span", {}, "Max % (at or above high temp)"), seasonalMax]),
    ]));
    seasonalSection.appendChild(seasonalPreview);
    card.appendChild(seasonalSection);

    const moistureSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);",
    });
    moistureSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, "Soil moisture skip"));
    moistureSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" },
      "Skip cron/calendar triggers when soil moisture is above a threshold (soil already wet)."
    ));
    const moistureEntity = el("input", { type: "text", placeholder: "sensor.garden_moisture", value: String(opts.moisture_entity || "") });
    const moistureAttr = el("input", { type: "text", placeholder: "moisture (optional attribute)", value: String(opts.moisture_attribute || "") });
    const moistureThresholdRaw = (opts.moisture_threshold_skip_above === null || opts.moisture_threshold_skip_above === undefined) ? "" : String(opts.moisture_threshold_skip_above);
    const moistureThreshold = el("input", { type: "number", min: "0", max: "100", step: "0.5", value: moistureThresholdRaw });
    moistureSection.appendChild(el("label", { class: "field" }, [el("span", {}, "Moisture sensor entity"), moistureEntity]));
    moistureSection.appendChild(el("div", { class: "field-row" }, [
      el("label", { class: "field" }, [el("span", {}, "Attribute (optional)"), moistureAttr]),
      el("label", { class: "field" }, [el("span", {}, "Skip when ≥ (blank = off)"), moistureThreshold]),
    ]));
    card.appendChild(moistureSection);

    const overlapSection = el("div", {
      style: "margin-top:16px;padding-top:12px;border-top:1px solid var(--sw-border);",
    });
    overlapSection.appendChild(el("h3", { style: "margin:0 0 6px;font-size:14px;" }, "Cycle overlap"));
    overlapSection.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 10px;" },
      "When off (default), a schedule or calendar event that would start a cycle while another cycle is already running is skipped. Manual runs always allowed."
    ));
    const allowConcurrent = el("input", { type: "checkbox" });
    allowConcurrent.checked = !!opts.allow_concurrent_cycles;
    overlapSection.appendChild(el("label", { class: "field" }, [el("span", {}, "Allow concurrent cycles"), allowConcurrent]));
    card.appendChild(overlapSection);

    const feedback = el("div", { class: "muted", style: "margin-top:8px;font-size:12px;" });
    const saveBtn = el("button", { class: "btn primary" }, "Save settings");
    saveBtn.addEventListener("click", async () => {
      saveBtn.disabled = true;
      const oldText = saveBtn.textContent;
      saveBtn.textContent = "Saving...";
      const thresholdRaw = rainThresholdInput.value.trim();
      const threshold = thresholdRaw === "" ? null : parseFloat(thresholdRaw);
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
          seasonal_temp_low: parseFloat(seasonalLow.value),
          seasonal_temp_high: parseFloat(seasonalHigh.value),
          seasonal_min_pct: parseFloat(seasonalMin.value),
          seasonal_max_pct: parseFloat(seasonalMax.value),
          allow_concurrent_cycles: allowConcurrent.checked,
          moisture_entity: moistureEntity.value.trim(),
          moisture_attribute: moistureAttr.value.trim(),
          moisture_threshold_skip_above: moistureThreshold.value.trim() === "" ? null : parseFloat(moistureThreshold.value),
        });
        feedback.textContent = "Saved at " + new Date().toLocaleTimeString() + ". Integration reloaded.";
        this._toast("Settings saved", "ok");
        setTimeout(() => this._refresh(), 1500);
      } catch (e) {
        this._toast(e.message || String(e), "error");
        feedback.textContent = "Save failed: " + (e.message || e);
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
      webhookCard.appendChild(el("h2", {}, "Webhook"));
      webhookCard.appendChild(el("p", { class: "muted", style: "font-size:12px;margin:0 0 8px;" },
        "POST entity_id (+ optional duration_minutes, action) to this URL. Secret via the URL itself; rotate by removing and re-adding the integration."
      ));
      const urlInput = el("input", {
        type: "text",
        readonly: "readonly",
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
            this._toast("Copied", "ok");
          } catch {
            urlInput.select();
            document.execCommand("copy");
            this._toast("Copied", "ok");
          }
        },
      }, "Copy URL");
      webhookCard.appendChild(urlInput);
      webhookCard.appendChild(copyBtn);
      root.appendChild(webhookCard);
    }

    const card2 = el("div", { class: "card" }, [
      el("h2", {}, "Current options"),
      el("pre", {}, JSON.stringify(opts, null, 2)),
      el("p", { class: "muted", style: "font-size:12px;margin-top:8px;" },
        "These same values are also editable from Settings → Devices & Services → Schedule Wizard → Configure."),
    ]);
    root.appendChild(card2);
  }

  _showModal(title, fields, onSave) {
    this._modalRoot.innerHTML = "";
    const modal = el("div", { class: "modal" });
    modal.appendChild(el("h3", {}, title));
    fields.forEach((f) => modal.appendChild(f));

    const cancelBtn = el("button", { class: "btn", onClick: () => { this._modalRoot.innerHTML = ""; } }, "Cancel");
    const saveBtn = el("button", { class: "btn primary", onClick: async () => {
      saveBtn.disabled = true;
      try {
        const ok = await onSave();
        if (ok) this._modalRoot.innerHTML = "";
      } finally {
        saveBtn.disabled = false;
      }
    } }, "Save");

    modal.appendChild(el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]));

    const overlay = el("div", { class: "modal-overlay" }, modal);
    overlay.addEventListener("click", (e) => { if (e.target === overlay) this._modalRoot.innerHTML = ""; });
    this._modalRoot.appendChild(overlay);
  }
}

if (!customElements.get("schedule-wizard-panel")) {
  customElements.define("schedule-wizard-panel", ScheduleWizardPanel);
}
