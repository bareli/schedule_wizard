import asyncio,sys
sys.path.insert(0,".")
from lib import WS
async def m():
    async with WS() as ws:
        await ws.svc("stop_all",{})
        r,_=await ws.cmd({"type":"schedule_wizard/get_state"}); st=r["result"]
        for c in st["cycles"]:
            if c["name"].startswith("Perf plan"): await ws.svc("remove_cycle",{"cycle_id":c["id"]})
        for v in st["valves"]:
            if v["entity_id"].startswith("input_boolean.pz"): await ws.svc("remove_valve",{"entity_id":v["entity_id"]})
        r,_=await ws.cmd({"type":"schedule_wizard/get_state"}); st=r["result"]
        for s in st["schedules"]:
            if s["name"].startswith("perf sched"): await ws.svc("remove_schedule",{"schedule_id":s["id"]})
        await asyncio.sleep(2)
        r,_=await ws.cmd({"type":"input_boolean/list"})
        n=0
        for b in r["result"]:
            if b["name"].startswith("PZ"):
                x,_=await ws.cmd({"type":"input_boolean/delete","input_boolean_id":b["id"]}); n+=bool(x["success"])
        await asyncio.sleep(3)
        r,_=await ws.cmd({"type":"schedule_wizard/get_state"}); st=r["result"]
        g,_=await ws.cmd({"type":"get_states"})
        print("deleted booleans",n,"| left valves",len(st["valves"]),"cycles",len(st["cycles"]),"schedules",len(st["schedules"]),"history",len(st["history"]),"active",len(st["active"]),"| pz states",sum(1 for s in g["result"] if s["entity_id"].startswith("input_boolean.pz")), "total states",len(g["result"]))
asyncio.run(m())
