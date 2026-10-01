import asyncio, json, sys, time, aiohttp
ACC = "D:/Code/home assistant extensions/schedule_wizard/qa/fixtures/dev-accounts-8174.json"
class WS:
    def __init__(self): self.i = 0
    async def __aenter__(self):
        acc = json.load(open(ACC))
        self.s = aiohttp.ClientSession()
        self.w = await self.s.ws_connect(acc["base"].replace("http","ws")+"/api/websocket", max_msg_size=0)
        await self.w.receive_json()
        await self.w.send_json({"type":"auth","access_token":acc["admin"]["token"]})
        assert (await self.w.receive_json())["type"]=="auth_ok"
        return self
    async def __aexit__(self,*a):
        await self.w.close(); await self.s.close()
    async def cmd(self, msg, raw=False):
        self.i += 1; msg["id"]=self.i
        t=time.perf_counter()
        await self.w.send_json(msg)
        while True:
            m = await self.w.receive()
            if m.type != aiohttp.WSMsgType.TEXT: raise RuntimeError(m)
            if m.data.startswith('{"id": %d,'%self.i) or json.loads(m.data).get("id")==self.i:
                dt=time.perf_counter()-t
                if raw: return m.data, dt
                return json.loads(m.data), dt
    async def svc(self, service, data, domain="schedule_wizard", resp=False):
        r,_ = await self.cmd({"type":"call_service","domain":domain,"service":service,"service_data":data,"return_response":resp})
        if not r.get("success"): raise RuntimeError(r)
        return r["result"]
