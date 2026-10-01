import asyncio,sys,time
sys.path.insert(0,".")
from lib import WS
async def m():
    async with WS() as ws:
        t0=time.time();rounds=0
        while True:
            r,_=await ws.cmd({"type":"schedule_wizard/get_state"})
            n=len(r["result"]["history"])
            if n>=500: break
            ids=[f"input_boolean.pz{i:02d}" for i in range(1,21)]
            await asyncio.gather(*[ws.svc("run_valve",{"entity_id":e,"duration_minutes":1}) for e in ids]) if False else None
            for e in ids:
                await ws.svc("run_valve",{"entity_id":e,"duration_minutes":1})
            for e in ids:
                await ws.svc("stop_valve",{"entity_id":e})
            rounds+=1
        print("history",n,"rounds",rounds,"secs %.1f"%(time.time()-t0))
asyncio.run(m())
