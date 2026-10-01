import sys,json,time,statistics
sys.path.insert(0,"D:/Code/home assistant extensions/schedule_wizard")
sys.path.insert(0,"D:/Code/home assistant extensions/schedule_wizard/qa/tools")
import win_shim  # noqa
from datetime import timedelta
from homeassistant.util import dt as dt_util
dt_util.set_default_time_zone(dt_util.get_time_zone("Asia/Jerusalem"))
from custom_components.schedule_wizard import planner
data=json.load(open("store_copy.json"))["data"]
class St:
    def __init__(s,d): s.d=d
    @property
    def schedules(s): return list(s.d["schedules"])
    @property
    def valves(s): return list(s.d["valves"])
    @property
    def cycles(s): return list(s.d["cycles"])
    def get_cycle(s,i): return next((c for c in s.d["cycles"] if c["id"]==i),None)
    def get_valve(s,i): return next((v for v in s.d["valves"] if v["entity_id"]==i),None)
    def is_skipped(s,a,b): return b in s.d["skips"].get(a,[])
st=St(data); opts={}
def t(name,fn,n=50):
    xs=[]
    for _ in range(n):
        a=time.perf_counter(); r=fn(); xs.append((time.perf_counter()-a)*1000)
    print("%-48s median %.2f ms  max %.2f ms  (n=%d) res=%s"%(name,statistics.median(xs),max(xs),n,len(r) if hasattr(r,'__len__') else r))
now=dt_util.now()
sod=dt_util.start_of_local_day()
print("schedules",len(st.schedules),"valves",len(st.valves),"cycles",len(st.cycles))
t("occurrences 7d (get_state 'week')",lambda: planner.occurrences(st,opts,sod,sod+timedelta(days=7)))
t("occurrences lookahead_end (calendar.event)",lambda: planner.occurrences(st,opts,now-timedelta(hours=24),planner.lookahead_end(st,now)))
t("occurrences 62d (calendar get_events max)",lambda: planner.occurrences(st,opts,now-timedelta(days=1),now+timedelta(days=62)))
cb={c["id"]:c for c in st.cycles}
def nextrun_all():
    out=[]
    for v in st.valves:
        best=None
        for s in st.schedules:
            if not s.get("enabled"): continue
            m= s.get("valve_entity_id")==v["entity_id"]
            if not m and s.get("cycle_id"):
                c=cb.get(s["cycle_id"]); m=bool(c) and any(x["entity_id"]==v["entity_id"] for x in c["steps"])
            if not m: continue
            f=planner.next_fire(s,now)
            if f and (best is None or f<best): best=f
        out.append(best)
    return out
t("_next_run_for x20 valves (get_state)",nextrun_all)
def nextsens():
    best=None
    for s in st.schedules:
        f=planner.next_fire(s,now)
        if f and (best is None or f<best): best=f
    return [best]
t("NextScheduleSensor._compute_next (30s poll, x2/poll)",nextsens)
cnt=0
orig=planner.next_fire
def counting(*a,**k):
    global cnt; cnt+=1; return orig(*a,**k)
planner.next_fire=counting; nextrun_all(); print("next_fire calls per get_state:",cnt)
planner.next_fire=orig
h=data["history"]
t("history stats loop (500)",lambda: [x for x in h if x.get("valve_entity_id")])
t("json.dumps full store (what each Store save does)",lambda: json.dumps(data))
