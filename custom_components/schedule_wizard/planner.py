"""Upcoming schedule occurrences, shared by the calendar entity, the week view and reminders."""
from __future__ import annotations

from datetime import datetime, time as dtime, timedelta
from typing import Any, Optional

from homeassistant.util import dt as dt_util

from .storage import WizardStore


def _rain_delay_until(options: dict) -> int:
    try:
        return int(options.get("rain_delay_until") or 0)
    except (TypeError, ValueError):
        return 0


def _valve_delay_until(valve: dict) -> int:
    try:
        return int(valve.get("rain_delay_until") or 0)
    except (TypeError, ValueError):
        return 0


def schedule_target(store: WizardStore, sched: dict) -> Optional[dict[str, Any]]:
    """Resolve a schedule to {kind, id, name, zones: [{entity_id, label, minutes, indoor}], minutes}."""
    if not sched.get("enabled"):
        return None
    cycle_id = sched.get("cycle_id") or ""
    if cycle_id:
        cycle = store.get_cycle(cycle_id)
        if not cycle or not cycle.get("enabled"):
            return None
        zones = []
        for step in cycle.get("steps") or []:
            valve = store.get_valve(step.get("entity_id") or "") or {}
            zones.append({
                "entity_id": step.get("entity_id"),
                "label": valve.get("label") or step.get("entity_id"),
                "minutes": int(step.get("duration_min") or 0),
                "indoor": bool(valve.get("rain_exempt")),
                "delay_until": _valve_delay_until(valve),
            })
        return {
            "kind": "cycle", "id": cycle_id, "name": cycle.get("name") or cycle_id,
            "zones": zones, "minutes": sum(z["minutes"] for z in zones),
        }
    entity_id = sched.get("valve_entity_id") or ""
    valve = store.get_valve(entity_id)
    if not valve or not valve.get("enabled"):
        return None
    minutes = int(sched.get("duration_min") or 0)
    return {
        "kind": "valve", "id": entity_id, "name": valve.get("label") or entity_id,
        "zones": [{
            "entity_id": entity_id, "label": valve.get("label") or entity_id, "minutes": minutes,
            "indoor": bool(valve.get("rain_exempt")), "delay_until": _valve_delay_until(valve),
        }],
        "minutes": minutes,
    }


def predicted_skip(store: WizardStore, options: dict, sched: dict, target: dict, fire_ts: int, day: str) -> Optional[str]:
    """What we already know will stop this run: a manual skip or a rain delay. Weather is not predicted."""
    if store.is_skipped(sched["id"], day):
        return "skipped_manual"
    global_until = _rain_delay_until(options)
    blocked = [
        z["delay_until"] > fire_ts or (not z["indoor"] and global_until > fire_ts)
        for z in target["zones"]
    ]
    if blocked and all(blocked):
        return "rain_delay"
    if any(blocked):
        return "partial_rain_delay"
    return None


def occurrences(
    store: WizardStore, options: dict, start: datetime, end: datetime, limit: int = 500,
) -> list[dict[str, Any]]:
    """All schedule runs whose start falls in [start, end), sorted by time."""
    tz = dt_util.get_default_time_zone() if hasattr(dt_util, "get_default_time_zone") else dt_util.DEFAULT_TIME_ZONE
    start_l = dt_util.as_local(start)
    end_l = dt_util.as_local(end)
    out: list[dict[str, Any]] = []
    for sched in store.schedules:
        target = schedule_target(store, sched)
        if not target:
            continue
        try:
            hh, mm = (int(x) for x in str(sched.get("time_hhmm", "")).split(":"))
        except (TypeError, ValueError):
            continue
        mask = int(sched.get("days_mask") or 0)
        day = start_l.date()
        while day <= end_l.date():
            if mask & (1 << day.weekday()):
                fire = datetime.combine(day, dtime(hh, mm), tzinfo=tz)
                if start_l <= fire < end_l:
                    fire_ts = int(fire.timestamp())
                    day_s = day.isoformat()
                    out.append({
                        "start": fire_ts,
                        "end": fire_ts + max(1, target["minutes"]) * 60,
                        "day": day_s,
                        "schedule_id": sched["id"],
                        "kind": target["kind"],
                        "target": target["id"],
                        "name": target["name"],
                        "zones": [{k: z[k] for k in ("entity_id", "label", "minutes", "indoor")} for z in target["zones"]],
                        "minutes": target["minutes"],
                        "skip": predicted_skip(store, options, sched, target, fire_ts, day_s),
                    })
            day += timedelta(days=1)
    out.sort(key=lambda o: (o["start"], o["name"]))
    return out[:limit]


def next_occurrence(store: WizardStore, options: dict, schedule_id: Optional[str] = None,
                    now: Optional[datetime] = None, days: int = 8) -> Optional[dict[str, Any]]:
    now = now or dt_util.now()
    for occ in occurrences(store, options, now, now + timedelta(days=days)):
        if schedule_id is None or occ["schedule_id"] == schedule_id:
            return occ
    return None
