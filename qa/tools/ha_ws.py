"""Send websocket commands to the QA dev HA as qa_admin: ha_ws.py <accounts.json> '<json msg>' ..."""
import asyncio
import json
import sys

import aiohttp


async def main() -> None:
    accounts = json.load(open(sys.argv[1]))
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(accounts["base"].replace("http", "ws") + "/api/websocket") as ws:
            await ws.receive_json()
            await ws.send_json({"type": "auth", "access_token": accounts["admin"]["token"]})
            assert (await ws.receive_json())["type"] == "auth_ok"
            for i, raw in enumerate(sys.argv[2:], start=1):
                msg = json.loads(raw)
                msg["id"] = i
                await ws.send_json(msg)
                while True:
                    reply = await ws.receive_json()
                    if reply.get("id") == i and reply.get("type") == "result":
                        print(json.dumps(reply, ensure_ascii=False)[:2000])
                        break


asyncio.run(main())
