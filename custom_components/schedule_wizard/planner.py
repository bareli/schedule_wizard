"""Upcoming schedule occurrences, shared by the calendar entity, the week view and reminders."""
from __future__ import annotations

from datetime import date, datetime, time as dtime, timedelta
from typing import Any, Optional

from homeassistant.util import dt as dt_util

from .const import INTERVAL_MAX_DAYS, SUN_OFFSET_MAX, TIME_MODE_CLOCK, TIME_MODES
from .storage import WizardStore

# Far enough to find the next run of an every-N-days schedule (N up to 30).
NEXT_RUN_DAYS = INTERVAL_MAX_DAYS + 1


def parse_day(value: Any) -> Optional[date]:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except (TypeError, ValueError):
        return None


def runs_on(sched: dict, day: date) -> bool:
    """Whether a schedule has a run on this local date (weekdays, or every N days from start_date)."""
    if sched.get("repeat") == "interval":
        start = parse_day(sched.get("start_date"))
        try:
            n = int(sched.get("interval_days") or 0)
        except (TypeError, ValueError):
            return False
        if start is None or n < 1:
            return False
        delta = (day - start).days
        return delta >= 0 and delta % n == 0
    try:
        mask = int(sched.get("days_mask") or 0)
    except (TypeError, ValueError):
        return False
    return bool(mask & (1 << day.weekday()))


def _tz():
    return dt_util.get_default_time_zone() if hasattr(dt_util, "get_default_time_zone") else dt_util.DEFAULT_TIME_ZONE


def _hhmm(sched: dict) -> Optional[tuple[int, int]]:
    try:
        hh, mm = (int(x) for x in str(sched.get("time_hhmm", "")).split(":"))
    except (TypeError, ValueError):
        return None
    return hh, mm


# (event, local date, location) -> local datetime of the event (None = no such event that day).
_SUN_CACHE: dict[tuple, Optional[datetime]] = {}
_SUN_CACHE_MAX = 2000


def time_mode(sched: dict) -> str:
    mode = sched.get("time_mode") or TIME_MODE_CLOCK
    return mode if mode in TIME_MODES else TIME_MODE_CLOCK


def sun_offset(sched: dict) -> int:
    try:
        n = int(sched.get("sun_offset_min") or 0)
    except (TypeError, ValueError):
        return 0
    return max(-SUN_OFFSET_MAX, min(SUN_OFFSET_MAX, n))


def _sun_event(hass, event: str, day: date) -> Optional[datetime]:
    """Local time of sunrise/sunset on this local date at the HA location (None at polar day/night)."""
    from homeassistant.helpers.sun import get_astral_event_date

    cfg = hass.config
    key = (event, day, cfg.latitude, cfg.longitude, cfg.elevation, str(_tz()))
    if key in _SUN_CACHE:
        return _SUN_CACHE[key]
    found = None
    # Astral works on UTC dates: the event of a local date can sit on the UTC day before or after.
    for shift in (0, -1, 1):
        try:
            when = get_astral_event_date(hass, event, day + timedelta(days=shift))
        except Exception:  # bad location data
            when = None
        if when is not None and dt_util.as_local(when).date() == day:
            found = dt_util.as_local(when)
            break
    if len(_SUN_CACHE) >= _SUN_CACHE_MAX:
        _SUN_CACHE.clear()
    _SUN_CACHE[key] = found
    return found


def fire_at(sched: dict, day: date, hass=None) -> Optional[datetime]:
    """Local start time of a schedule on a local date, to the minute (ignores repeat rules and skips).

    Sunrise / sunset schedules follow the sun at the HA location plus the offset; a start pushed
    past midnight by the offset is kept on its own day (00:00 or 23:59). No hass or no sun event: None.
    """
    mode = time_mode(sched)
    if mode == TIME_MODE_CLOCK:
        hm = _hhmm(sched)
        if not hm:
            return None
        try:
            return datetime.combine(day, dtime(*hm), tzinfo=_tz())
        except ValueError:
            return None
    if hass is None:
        return None
    event = _sun_event(hass, mode, day)
    if event is None:
        return None
    # Offset in real minutes (UTC), then back to local wall time, to the minute.
    when = dt_util.as_local(dt_util.as_utc(event) + timedelta(minutes=sun_offset(sched)))
    when = when.replace(second=0, microsecond=0)
    if when.date() < day:
        return datetime.combine(day, dtime(0, 0), tzinfo=_tz())
    if when.date() > day:
        return datetime.combine(day, dtime(23, 59), tzinfo=_tz())
    return when


def fire_hhmm(sched: dict, day: date, hass=None) -> Optional[str]:
    """"HH:MM" the cron loop matches for this schedule on this local date."""
    when = fire_at(sched, day, hass)
    return when.strftime("%H:%M") if when else None


def override_of(store: Optional[WizardStore], sched: dict, day: date) -> Optional[dict]:
    """The one-off change of this schedule's run on this local date (v0.16.0), or None."""
    if store is None or not sched.get("id"):
        return None
    return store.get_override(sched["id"], day.isoformat())


def override_pct(override: Optional[dict]) -> int:
    try:
        return int((override or {}).get("pct") or 100)
    except (TypeError, ValueError):
        return 100


def run_at(store: Optional[WizardStore], sched: dict, day: date, hass=None) -> Optional[datetime]:
    """Start of the schedule's run on this local date, with a one-off new time applied (same day)."""
    o = override_of(store, sched, day)
    hm = _hhmm({"time_hhmm": o.get("time")}) if o and o.get("time") else None
    if hm:
        try:
            return datetime.combine(day, dtime(*hm), tzinfo=_tz())
        except ValueError:
            pass
    return fire_at(sched, day, hass)


def run_hhmm(store: Optional[WizardStore], sched: dict, day: date, hass=None) -> Optional[str]:
    """"HH:MM" the cron loop matches on this local date, one-off changes included."""
    when = run_at(store, sched, day, hass)
    return when.strftime("%H:%M") if when else None


def next_run_at(store: Optional[WizardStore], sched: dict, after: datetime, hass=None,
                days: int = NEXT_RUN_DAYS) -> Optional[datetime]:
    """Next run strictly after `after`, with one-off new times (a run moved later today still counts)."""
    if time_mode(sched) == TIME_MODE_CLOCK and not _hhmm(sched):
        return None
    after_l = dt_util.as_local(after)
    day = _first_day(sched, after_l.date())
    for _ in range(days + 1):
        if runs_on(sched, day):
            fire = run_at(store, sched, day, hass)
            if fire is not None and fire > after_l:
                return fire
        day += timedelta(days=1)
    return None


def _first_day(sched: dict, day: date) -> date:
    """Where a next-run search starts: an every-N-days schedule has no run before its start date."""
    if sched.get("repeat") == "interval":
        start = parse_day(sched.get("start_date"))
        if start is not None and start > day:
            return start
    return day


def next_fire(sched: dict, now: Optional[datetime] = None, days: int = NEXT_RUN_DAYS, hass=None) -> Optional[datetime]:
    """Next local start time of a schedule strictly after `now` (ignores enabled flags and skips)."""
    if time_mode(sched) == TIME_MODE_CLOCK and not _hhmm(sched):
        return None
    now_l = dt_util.as_local(now or dt_util.now())
    day = _first_day(sched, now_l.date())
    for _ in range(days + 1):
        if runs_on(sched, day):
            fire = fire_at(sched, day, hass)
            if fire is not None and fire > now_l:
                return fire
        day += timedelta(days=1)
    return None


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


def zone_pause_until(options: dict, valve: dict, fire_ts: int) -> int:
    """End of the rain pause that stops this zone at fire_ts (its own or the global one), else 0."""
    own = _valve_delay_until(valve)
    until = own if own > fire_ts else 0
    if not valve.get("rain_exempt"):
        glob = _rain_delay_until(options)
        if glob > fire_ts:
            until = max(until, glob)
    return until


# Runs a zone may have skipped in a row before its next real one (a 7-day rain pause on a daily schedule).
SKIP_SCAN_LIMIT = 60


def next_zone_run(store: WizardStore, options: dict, sched: dict, valve: dict,
                  now: datetime, hass=None) -> tuple[Optional[datetime], Optional[dict[str, Any]]]:
    """Next start of a schedule that will water this zone, and the first run before it that will not (UX-010).

    A run does not water the zone when the user skipped that day or a rain pause covers the zone then.
    Returns (fire, skip) where skip is {"fires_at", "reason": "skipped_manual" | "rain_delay", "until"} or None.
    """
    after = now
    skip: Optional[dict[str, Any]] = None
    for _ in range(SKIP_SCAN_LIMIT):
        fire = next_run_at(store, sched, after, hass=hass)
        if fire is None:
            return None, skip
        ts = int(fire.timestamp())
        until = 0
        if store.is_skipped(sched["id"], fire.date().isoformat()):
            reason = "skipped_manual"
        else:
            until = zone_pause_until(options, valve, ts)
            reason = "rain_delay" if until else None
        if reason is None:
            return fire, skip
        if skip is None:
            skip = {"fires_at": ts, "reason": reason, "until": until}
        after = fire
    return None, skip


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
    store: WizardStore, options: dict, start: datetime, end: datetime, limit: Optional[int] = 500,
) -> list[dict[str, Any]]:
    """All schedule runs whose start falls in [start, end), sorted by time; the first `limit` (None: all)."""
    hass = store.hass
    start_l = dt_util.as_local(start)
    end_l = dt_util.as_local(end)
    out: list[dict[str, Any]] = []
    for sched in store.schedules:
        target = schedule_target(store, sched)
        if not target:
            continue
        if time_mode(sched) == TIME_MODE_CLOCK and not _hhmm(sched):
            continue
        # A run before the schedule existed never happened: not a past run in the week or the calendar (#93).
        created = int(sched.get("created_at") or 0)
        day = start_l.date()
        while day <= end_l.date():
            if runs_on(sched, day):
                fire = run_at(store, sched, day, hass)
                if fire is not None and start_l <= fire < end_l and int(fire.timestamp()) >= created:
                    fire_ts = int(fire.timestamp())
                    day_s = day.isoformat()
                    o = override_of(store, sched, day)
                    pct = override_pct(o)
                    zones = [
                        {**{k: z[k] for k in ("entity_id", "label", "indoor")}, "minutes": scale_pct(z["minutes"], pct)}
                        for z in target["zones"]
                    ]
                    minutes = sum(z["minutes"] for z in zones)
                    out.append({
                        "start": fire_ts,
                        "end": fire_ts + max(1, minutes) * 60,
                        "day": day_s,
                        "schedule_id": sched["id"],
                        "kind": target["kind"],
                        "target": target["id"],
                        "name": target["name"],
                        "zones": zones,
                        "minutes": minutes,
                        "base_minutes": target["minutes"],
                        "override": {"time": o.get("time") or "", "pct": pct} if o else None,
                        "skip": predicted_skip(store, options, sched, target, fire_ts, day_s),
                    })
            day += timedelta(days=1)
    out.sort(key=lambda o: (o["start"], o["name"]))
    return out if limit is None else out[:limit]


def scale_pct(minutes: int, pct: int) -> int:
    """Minutes at a percent of the plan, at least 1 (0 stays 0)."""
    if pct == 100 or minutes <= 0:
        return int(minutes)
    return max(1, int(round(minutes * pct / 100)))


# Runs that do not water: they cannot clash with anything.
_NO_WATER = ("skipped_manual", "rain_delay")


def mark_overlaps(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add "overlaps" to each run: the other runs that water at the same time (v0.16.0).

    Two runs overlap when their [start, end) intervals meet and both will water; a plan counts as one block
    from its start to its end. Each entry: {"schedule_id", "name", "start", "kind"}.
    """
    for r in runs:
        r["overlaps"] = []
    live = sorted((r for r in runs if r.get("skip") not in _NO_WATER), key=lambda r: r["start"])
    for i, a in enumerate(live):
        for b in live[i + 1:]:
            if b["start"] >= a["end"]:
                break
            if a["schedule_id"] == b["schedule_id"]:
                continue
            a["overlaps"].append({"schedule_id": b["schedule_id"], "name": b["name"], "start": b["start"], "kind": b["kind"]})
            b["overlaps"].append({"schedule_id": a["schedule_id"], "name": a["name"], "start": a["start"], "kind": a["kind"]})
    return runs


def draft_conflicts(store: WizardStore, options: dict, draft: dict, start: datetime, days: int = 14,
                    exclude_id: str = "") -> dict[str, Any]:
    """Runs of other schedules that a schedule being edited would water at the same time as, and the
    first later clock time (5-minute steps, same day) at which it clashes with none of them.

    draft: a schedule dict (repeat, days_mask, interval_days, start_date, time_hhmm, time_mode, sun_offset_min)
    plus "minutes" (how long one run waters).
    """
    hass = store.hass
    end = start + timedelta(days=days)
    others = [
        o for o in occurrences(store, options, start, end, limit=None)
        if o["schedule_id"] != exclude_id and o.get("skip") not in _NO_WATER
    ]
    minutes = max(1, int(draft.get("minutes") or 1))
    draft_days = []
    day = dt_util.as_local(start).date()
    last = dt_util.as_local(end).date()
    while day < last:
        if runs_on(draft, day):
            fire = fire_at(draft, day, hass)
            if fire is not None:
                draft_days.append(fire)
        day += timedelta(days=1)

    def clashes(shift_min: int) -> list[dict]:
        found: dict[str, dict] = {}
        for fire in draft_days:
            a0 = int(fire.timestamp()) + shift_min * 60
            a1 = a0 + minutes * 60
            for o in others:
                if o["start"] < a1 and a0 < o["end"] and o["schedule_id"] not in found:
                    found[o["schedule_id"]] = {
                        "schedule_id": o["schedule_id"], "name": o["name"], "kind": o["kind"],
                        "start": o["start"], "end": o["end"],
                    }
        return sorted(found.values(), key=lambda c: c["start"])

    conflicts = clashes(0)
    suggestion = None
    base = _hhmm(draft)
    if conflicts and draft_days and time_mode(draft) == TIME_MODE_CLOCK and base:
        start_min = base[0] * 60 + base[1]
        for shift in range(5, 24 * 60, 5):
            total = start_min + shift
            if total + minutes > 24 * 60:
                break
            if not clashes(shift):
                suggestion = f"{total // 60:02d}:{total % 60:02d}"
                break
    return {"conflicts": conflicts, "suggestion": suggestion}


def next_occurrence(store: WizardStore, options: dict, schedule_id: Optional[str] = None,
                    now: Optional[datetime] = None, days: int = NEXT_RUN_DAYS) -> Optional[dict[str, Any]]:
    now = now or dt_util.now()
    sched = store.get_schedule(schedule_id) if schedule_id else None
    if sched:
        today = dt_util.as_local(now).date()
        first = _first_day(sched, today)
        if first > today:
            now = dt_util.start_of_local_day(first)
    for occ in occurrences(store, options, now, now + timedelta(days=days)):
        if schedule_id is None or occ["schedule_id"] == schedule_id:
            return occ
    return None


def lookahead_end(store: WizardStore, now: datetime) -> datetime:
    """End of a window long enough to hold every schedule's next run, including distant start dates."""
    today = dt_util.as_local(now).date()
    first = max((_first_day(s, today) for s in store.schedules), default=today)
    return dt_util.start_of_local_day(first) + timedelta(days=NEXT_RUN_DAYS + 1)
