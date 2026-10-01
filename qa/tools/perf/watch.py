import asyncio,sys,time,os,psutil
sys.path.insert(0,".")
from lib import WS
F=sys.argv[1]; MODE=sys.argv[2]; secs=int(sys.argv[3])
P="C:/Users/barel/AppData/Local/Temp/claude/D--Code-home-assistant-extensions-good-days/f3802ecc-2b66-432d-963d-f0b1f5d18979/scratchpad/haconfig-8174/.storage/schedule_wizard.data"
async def watcher(ev,out):
    last=os.stat(P).st_mtime_ns
    while not ev.is_set():
        try: m=os.stat(P).st_mtime_ns
        except FileNotFoundError: m=last
        if m!=last: out.append((time.time(),os.stat(P).st_size)); last=m
        await asyncio.sleep(0.005)
async def main():
    ev=asyncio.Event(); out=[]
    w=asyncio.create_task(watcher(ev,out))
    p=psutil.Process(41996); c0=sum(p.cpu_times()[:2]); t0=time.time()
    async with WS() as ws:
        if MODE=="valve": await ws.svc("run_valve",{"entity_id":"input_boolean.pz01","duration_minutes":1})
        elif MODE=="cycle":
            r,_=await ws.cmd({"type":"schedule_wizard/get_state"})
            cid=sorted(r["result"]["cycles"],key=lambda c:c["name"])[0]["id"]
            await ws.svc("run_cycle",{"cycle_id":cid})
        await asyncio.sleep(secs)
    ev.set(); await w
    c1=sum(p.cpu_times()[:2])
    print(MODE,"window s %.0f"%(time.time()-t0),"store writes",len(out),"size",out[-1][1] if out else None,"cpu s total %.2f"%(c1-c0))
    print([round(t-t0,2) for t,_ in out])
asyncio.run(main())
