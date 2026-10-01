"""Refresh the admin access token in a dev accounts fixture: ha_login.py <accounts.json>"""
import json
import sys

import requests

path = sys.argv[1]
acc = json.load(open(path, encoding="utf-8"))
base = acc["base"]
client = base + "/"
flow = requests.post(f"{base}/auth/login_flow", json={"client_id": client, "handler": ["homeassistant", None], "redirect_uri": client}).json()
res = requests.post(
    f"{base}/auth/login_flow/{flow['flow_id']}",
    json={"client_id": client, "username": acc["admin"]["username"], "password": acc["admin"]["password"]},
).json()
tok = requests.post(f"{base}/auth/token", data={"grant_type": "authorization_code", "code": res["result"], "client_id": client}).json()
acc["admin"]["token"] = tok["access_token"]
json.dump(acc, open(path, "w", encoding="utf-8"), indent=2)
print("token refreshed")
