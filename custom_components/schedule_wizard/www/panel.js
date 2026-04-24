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
    if (k === "class") node.className = attrs[k];
    else if (k === "html") node.innerHTML = attrs[k];
    else if (k.startsWith("on") && typeof attrs[k] === "function") {
      node.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
    } else if (attrs[k] !== undefined && attrs[k] !== null) {
      node.setAttribute(k, attrs[k]);
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
      this._render();
    } catch (e) {
      this._renderError(e);
    }
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
    [["dashboard", "Dashboard"], ["valves", "Valves"], ["schedules", "Schedules"], ["settings", "Settings"]]
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
      case "schedules": this._renderSchedules(content); break;
      case "settings": this._renderSettings(content); break;
    }
  }

  _renderDashboard(root) {
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
    const minsInput = el("input", {
      type: "number", min: "1", max: "1440",
      value: String(v.default_duration_min),
      style: "width:70px;",
    });
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, v.label),
        el("div", { class: "sub" }, `${v.entity_id} • default ${v.default_duration_min}m`),
      ]),
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
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, v.label + (v.enabled ? "" : " (disabled)")),
        el("div", { class: "sub" }, `${v.entity_id} • ${v.default_duration_min}m default`),
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
    const valve = this._state.valves.find((v) => v.entity_id === s.valve_entity_id);
    const valveName = valve ? valve.label : s.valve_entity_id;
    return el("div", { class: "item" }, [
      el("div", {}, [
        el("div", { class: "name" }, (s.name || `${valveName} @ ${s.time_hhmm}`) + (s.enabled ? "" : " (disabled)")),
        el("div", { class: "sub" }, `${valveName} • ${s.time_hhmm} • ${daysFromMask(s.days_mask)} • ${s.duration_min}m`),
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
    if (!this._state.valves.length) { this._toast("Add a valve first", "error"); return; }

    let valveEntity = existing ? existing.valve_entity_id : this._state.valves[0].entity_id;
    let name = existing ? existing.name : "";
    let time = existing ? existing.time_hhmm : "06:00";
    let duration = existing ? existing.duration_min : (this._state.options.default_duration || 10);
    let mask = existing ? existing.days_mask : 127;
    let enabled = existing ? !!existing.enabled : true;

    const valveSel = el("select", existing ? { disabled: "disabled" } : {});
    this._state.valves.forEach((v) => {
      const opt = el("option", { value: v.entity_id }, `${v.label} (${v.entity_id})`);
      if (v.entity_id === valveEntity) opt.selected = true;
      valveSel.appendChild(opt);
    });
    valveSel.addEventListener("change", () => { valveEntity = valveSel.value; });

    const nameInput = el("input", { type: "text", value: name, placeholder: "Optional" });
    nameInput.addEventListener("input", () => { name = nameInput.value; });

    const timeInput = el("input", { type: "time", value: time });
    timeInput.addEventListener("input", () => { time = timeInput.value; });

    const durInput = el("input", { type: "number", min: "1", max: "1440", value: String(duration) });
    durInput.addEventListener("input", () => { duration = parseInt(durInput.value, 10) || 10; });

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
      el("label", { class: "field" }, [el("span", {}, "Valve"), valveSel]),
      el("label", { class: "field" }, [el("span", {}, "Name"), nameInput]),
      el("div", { class: "field-row" }, [
        el("label", { class: "field" }, [el("span", {}, "Time"), timeInput]),
        el("label", { class: "field" }, [el("span", {}, "Duration (min)"), durInput]),
      ]),
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
          duration_minutes: duration,
          days: daysFromMaskNames(mask),
          enabled,
        });
      }
      return await this._callService("add_schedule", {
        valve_entity_id: valveEntity,
        time,
        duration_minutes: duration,
        days: daysFromMaskNames(mask),
        name,
        enabled,
      });
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
