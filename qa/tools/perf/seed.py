import asyncio, datetime, json, sys
sys.path.insert(0, __file__.rsplit("/",1)[0])
from lib import WS
async def main():
    async with WS() as ws:
        for i in range(1,21):
            await ws.svc("add_valve", {"entity_id":f"input_boolean.pz{i:02d}","label":f"Perf zone {i:02d}","default_duration_minutes":1})
        cyc=[]
        for c in range(10):
            steps=[{"entity_id":f"input_boolean.pz{((c*2+k)%20)+1:02d}","duration_minutes":1} for k in range(5)]
            r=await ws.svc("add_cycle",{"name":f"Perf plan {c+1:02d}","steps":steps},resp=True)
            cyc.append(r["response"]["cycle"]["id"] if "response" in r else r["cycle"]["id"])
        today=datetime.date.today().isoformat()
        n=0
        for k in range(30):
            t=f"03:{k:02d}"
            d={"time":t,"duration_minutes":1,"name":f"perf sched {k:02d}"}
            if k<10: d["valve_entity_id"]=f"input_boolean.pz{k+1:02d}"
            elif k<20: d["cycle_id"]=cyc[k-10]
            else:
                d["valve_entity_id"]=f"input_boolean.pz{k-9:02d}" if k%2 else None
                if not d["valve_entity_id"]: d.pop("valve_entity_id"); d["cycle_id"]=cyc[k-20]
            if k<20: d["days"]=["mon","tue","wed","thu","fri","sat","sun"]
            else:
                d["every_n_days"]=30 if k<26 else 2+k; d["start_date"]=today
            await ws.svc("add_schedule",d); n+=1
        print("seeded", n, cyc[:2])
asyncio.run(main())
