# QA overlay: Schedule Wizard

Read `~/.claude/qa-kit/RULEBOOK.md` first, then `qa/PROJECT.md`. Same § numbers.

## §1 Environments

| Env | Base URL | Writes |
|---|---|---|
| `dev` | `http://127.0.0.1:8170` (HA 2026.9.4 on Windows, scratchpad venv `venv314`) | Allowed |
| `prod` | none. Never touch anyone's real Home Assistant. | - |

Accounts: `qa/fixtures/dev-accounts-8170.json` (git-ignored): `qa_admin` (owner), `qa_user` (non-admin).
Tokens expire after 30 min: `qa/tools/ha_login.py`.

## §2 Boundaries

`custom_components/schedule_wizard` is junctioned into the instance: finders never edit it.

## §3 Builds

No build. Python changes need an HA restart (orchestrator only); JS changes need a browser reload.

## §4 Instances

8170: test zones are `input_boolean.zone_front`, `zone_back`, `zone_herbs`, `input_number.qa_temp`
(temperature for the seasonal adjustment). See `qa/tools/README.md` and `qa/knowledge/`.
