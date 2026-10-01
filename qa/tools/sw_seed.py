"""Seed an Easy Sidebar Pro QA dev HA: esp_seed.py <port> <accounts.json>
Owner via onboarding (language he), non-admin qa_user, Easy Sidebar Pro entry, extra dashboards."""
import asyncio
import json
import secrets
import sys
import urllib.parse
import urllib.request

import aiohttp

PORT, OUT = sys.argv[1], sys.argv[2]
BASE = f"http://127.0.0.1:{PORT}"
CLIENT = BASE + "/"


def call(method, path, body=None, token=None, form=False):
    headers, data = {}, None
    if body is not None:
        if form:
            data = urllib.parse.urlencode(body).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode()
        return json.loads(text) if text else None


admin_pw, user_pw = secrets.token_urlsafe(12), secrets.token_urlsafe(12)
code = call("POST", "/api/onboarding/users", {"client_id": CLIENT, "name": "QA Admin", "username": "qa_admin", "password": admin_pw, "language": "he"})["auth_code"]
token = call("POST", "/auth/token", {"grant_type": "authorization_code", "code": code, "client_id": CLIENT}, form=True)["access_token"]
for step, body in (("core_config", {}), ("analytics", {}), ("integration", {"client_id": CLIENT, "redirect_uri": CLIENT + "?auth_callback=1"})):
    try:
        call("POST", f"/api/onboarding/{step}", body, token)
    except Exception as err:  # noqa: BLE001
        print("onboarding", step, err)
flow = call("POST", "/api/config/config_entries/flow", {"handler": "schedule_wizard"}, token)
print("flow:", call("POST", f"/api/config/config_entries/flow/{flow['flow_id']}", {}, token).get("type"))

DASHBOARDS = [] and [
    ("dash-cameras", "מצלמות", "mdi:cctv"),
    ("dash-energy-home", "Energy and solar overview for the whole house", "mdi:solar-power"),
    ("dash-kids", "חדר ילדים", "mdi:teddy-bear"),
    ("dash-garden", "Garden", "mdi:flower"),
]


async def ws():
    async with aiohttp.ClientSession() as s, s.ws_connect(BASE.replace("http", "ws") + "/api/websocket") as w:
        await w.receive_json()
        await w.send_json({"type": "auth", "access_token": token})
        assert (await w.receive_json())["type"] == "auth_ok"
        n = 0

        async def cmd(msg):
            nonlocal n
            n += 1
            msg["id"] = n
            await w.send_json(msg)
            while True:
                r = await w.receive_json()
                if r.get("id") == n and r.get("type") == "result":
                    return r

        for url, title, icon in DASHBOARDS:
            r = await cmd({"type": "lovelace/dashboards/create", "url_path": url, "title": title, "icon": icon, "show_in_sidebar": True, "require_admin": False, "mode": "storage"})
            print("dashboard", url, r["success"])
        r = await cmd({"type": "config/auth/create", "name": "QA User", "group_ids": ["system-users"], "local_only": False})
        uid = r["result"]["user"]["id"]
        r = await cmd({"type": "config/auth_provider/homeassistant/create", "user_id": uid, "username": "qa_user", "password": user_pw})
        print("qa_user", r["success"])


asyncio.run(ws())
json.dump({"base": BASE, "admin": {"username": "qa_admin", "password": admin_pw, "token": token},
           "user": {"username": "qa_user", "password": user_pw}}, open(OUT, "w"), indent=2)
print("seeded", OUT)
