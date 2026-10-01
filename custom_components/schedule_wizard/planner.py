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
        day = start_l.date()
        while day <= end_l.date():
            if runs_on(sched, day):
                fire = fire_at(sched, day, hass)
                if fire is not None and start_l <= fire < end_l:
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
