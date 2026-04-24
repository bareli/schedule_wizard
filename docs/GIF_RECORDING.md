# Recording a demo GIF

Can't automate screen recording. Here's the manual path — 5 minutes.

## Recommended tool — ScreenToGif

- Free, open source, Windows only.
- https://www.screentogif.com/

## Recipe

1. Install ScreenToGif. Launch.
2. Click **Recorder**.
3. Resize the recorder frame to cover just the Schedule Wizard panel content (not the whole HA sidebar, ~1100×750 looks right).
4. In Chrome, open `http://homeassistant.local:8123/schedule-wizard` at the **Dashboard** tab.
5. Click **Record** (F7). Do this sequence:
   - Land on Dashboard (1 sec)
   - Click **Run** on one valve (with `duration_minutes=1`)
   - Watch the progress bar animate for ~5 seconds
   - Click **Stop** on that valve
   - Switch to **Valves** tab (1 sec)
   - Switch to **Schedules** tab (1 sec)
6. **Stop recording** (F8). Editor opens.
7. **Delay** → set every frame to 80–100 ms (fps control).
8. **File → Save as → GIF** → filename `panel-demo.gif`.
9. Save to `docs/screenshots/panel-demo.gif`.

Target output:
- 5–15 seconds total length
- 1–2 MB file size (use the editor's "Optimize" to cut frames)
- Under 1000 px wide (GitHub shrinks bigger ones anyway)

## After saving

Ping me "gif done" and I'll:

1. Embed it at the top of the README
2. Update the social post drafts to mention "demo GIF available"
3. Commit + push

## Alternative tools

- **LICEcap** (simpler, Mac + Windows): https://www.cockos.com/licecap/
- **Peek** (Linux): https://github.com/phw/peek
- **OBS + ffmpeg** (overkill but highest quality): record MP4 in OBS, convert via `ffmpeg -i in.mp4 -vf "fps=12,scale=900:-1:flags=lanczos" panel-demo.gif`

## Size too big?

If GIF ends up > 5 MB, strip frames or reduce size:

```powershell
# Needs ffmpeg in PATH
ffmpeg -i panel-demo.gif -vf "fps=10,scale=800:-1:flags=lanczos" panel-demo-small.gif
```

Or upload the GIF to GitHub as an **asset on a release** (unlimited size) and link to it in README rather than committing into the repo.
