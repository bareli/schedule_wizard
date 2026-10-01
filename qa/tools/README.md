# Dev Home Assistant tooling (Windows)

Copied out of the session scratchpad so a new session can rebuild the QA environment.

1. Venv (Python 3.14 via uv): `uv venv --python 3.14 venv314` then
   `uv pip install --python venv314/Scripts/python.exe homeassistant==<ver> home-assistant-frontend==<from that version's components/frontend/manifest.json> -r extras.txt`,
   then pin component requirements from that version's own manifests (see `qa/knowledge/environment.md`).
2. Copy `stubs/*.py` into the venv's `Lib/site-packages` (Windows lacks fcntl/resource; two voice libs have no wheels).
3. Config dir with `configuration.yaml` (`http: server_port: <port>`), `custom_components/easy_sidebar_pro` as a directory junction to this repo.
4. Start (own background task, longest timeout): `PYTHONPATH=<this dir> <venv>/Scripts/python.exe ha_launch.py -c <config> --ignore-os-check --skip-pip`.
5. Seed: `python esp_seed.py <port> qa/fixtures/dev-accounts-<port>.json` (accounts file is git-ignored); on HA 2026.8+ promote the HTTP config right away: `python ha_ws.py <accounts> '{"type":"http/config/promote"}'`.
6. Tokens expire after 30 min: `python ha_login.py <accounts>`.
7. Browser checks: copy `lib.mjs` / `compat.mjs` into `~/.claude/qa-playwright/espjs/` (they import `playwright` from there). `PORT=<port> node espjs/compat.mjs`.

`win_shim.py` on PYTHONPATH makes pytest-socket a no-op for the pytest suite on Windows.
