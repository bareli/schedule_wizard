# Dev environment notes (learned in the v0.16.0 cycle, 2026-10-09)

- **Port 8170 may belong to another project's QA instance.** Check the process command line
  (`Get-CimInstance Win32_Process`, look for `haconfig-<port>`) before logging in; a login that fails with the
  fixture password is the first sign you are on someone else's instance.
- **HA 2026.9 keeps the HTTP port in `.storage/http`** (`data.stable.server_port`), not only in
  `configuration.yaml`. A copied config dir must have both changed, or the copy fails to bind the original port.
  After a port change HA shows "Confirm new HTTP server configuration": press Confirm.
- Parallel agents get their own instance (copy `.storage` + `configuration.yaml`, junction
  `custom_components/schedule_wizard` to the repo). Restart helper used this cycle: `restart_ha.sh <port>` in
  the session scratchpad (kills the `haconfig-<port>` python and relaunches `qa/tools/ha_launch.py`).
- **Panel JS is cached by URL** (`?v=<manifest version>`): with an unchanged version the browser keeps the old
  panel.js. Disable cache via CDP `Network.setCacheDisabled` before testing a JS change.
- **Weather fixture**: a template weather (`weather.garden_weather`) with `forecast_daily_template` gives a
  controllable daily forecast for weather tips. Template weathers report no forecast until HA has fully
  started; tips appear within ~2 minutes of a restart (fetch on HA started + 2-minute retry).
- **REST service errors**: a `HomeAssistantError` raised in a service answers HTTP 500 over REST; read the
  message from the log or the websocket `call_service` result instead of the status code.
- **Subagent progress hook**: the QA subagent types (qa-engineer, qa-ux-expert, ...) cannot load the
  `talk-progress` tool the session hook demands, so they are blocked at their first tool call. This cycle ran
  them as general-purpose agents told to load `mcp__talk-progress__progress` via ToolSearch first and to follow
  `~/.claude/agents/qa-<role>.md`. (May deserve a kit-level note; owner decides.)
- HA runs in UTC on the dev instances while the PC is in Asia/Jerusalem: schedule "now + N minutes" in HA's
  clock, not the PC's (a BUG-042 retest was invalid until redone in UTC).
