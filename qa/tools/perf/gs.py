import asyncio,sys,time,statistics,json,psutil
sys.path.insert(0,".")
from lib import WS
PID=41996
async def m(n=40):
    p=psutil.Process(PID)
    async with WS() as ws:
        ts=[];sz=0
        c0=sum(p.cpu_times()[:2]); w0=time.perf_counter()
        for _ in range(n):
            raw,dt=await ws.cmd({"type":"schedule_wizard/get_state"},raw=True)
            ts.append(dt*1000); sz=len(raw.encode())
        c1=sum(p.cpu_times()[:2]); w1=time.perf_counter()
        d=json.loads(raw)["result"]
        print("n",n,"bytes",sz,"hist",len(d["history"]),"week",len(d["week"]),"valves",len(d["valves"]),"controllable",len(d["controllable"]))
        print("rtt ms median %.1f p95 %.1f max %.1f min %.1f"%(statistics.median(ts),sorted(ts)[int(n*.95)-1],max(ts),min(ts)))
        print("HA cpu s per request (user+sys): %.4f"%((c1-c0)/n))
        keys={k:len(json.dumps(v)) for k,v in d.items()}
        print(sorted(keys.items(),key=lambda x:-x[1])[:8])
asyncio.run(m(int(sys.argv[1]) if len(sys.argv)>1 else 40))
