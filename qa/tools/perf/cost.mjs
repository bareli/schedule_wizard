import { open, FIND } from "./lib.mjs";
const SECS = Number(process.env.SECS || 60);
const { browser, page } = await open();
try {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Performance.enable");
  let wsBytes = 0, wsFrames = 0;
  await cdp.send("Network.enable");
  cdp.on("Network.webSocketFrameReceived", (e) => { wsBytes += e.response.payloadData.length; wsFrames++; });
  const metrics = async () => Object.fromEntries((await cdp.send("Performance.getMetrics")).metrics.map(m => [m.name, m.value]));
  // instrument _refresh / _render durations in page
  await page.evaluate(`(() => { const p = ${FIND}; window.__t = { refresh: [], render: [], long: [] };
    const r = p._render.bind(p); p._render = function () { const a = performance.now(); r(); window.__t.render.push(performance.now() - a); };
    const f = p._refresh.bind(p); p._refresh = async function () { const a = performance.now(); await f(); window.__t.refresh.push(performance.now() - a); };
    new PerformanceObserver(l => { for (const e of l.getEntries()) window.__t.long.push(e.duration); }).observe({ entryTypes: ["longtask"] }); })()`);
  for (const tab of ["home", "zones", "programs", "reports"]) {
    await page.evaluate(`(() => { const p = ${FIND}; if ("${tab}" === "reports") { p._tab = "home"; p._view = "reports"; } else { p._tab = "${tab}"; p._view = null; } p._render(); })()`);
    await page.waitForTimeout(500);
    await page.evaluate(`window.__t = { refresh: [], render: window.__t.render.slice(0,0), long: [] }; window.__t.refresh = [];`);
    wsBytes = 0; wsFrames = 0;
    const m0 = await metrics(); const t0 = Date.now();
    await page.waitForTimeout(SECS * 1000);
    const m1 = await metrics(); const secs = (Date.now() - t0) / 1000;
    const t = await page.evaluate(`window.__t`);
    const d = (k) => ((m1[k] - m0[k]) * 1000).toFixed(1);
    const nodes = await page.evaluate(`${FIND}.querySelectorAll("*").length`);
    const stat = (a) => a.length ? `n=${a.length} median ${[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)].toFixed(1)} max ${Math.max(...a).toFixed(1)}` : "n=0";
    console.log(`TAB ${tab}: window ${secs.toFixed(0)}s | refresh ms ${stat(t.refresh)} | render ms ${stat(t.render)} | long tasks ${t.long.length} ${t.long.map(x=>x.toFixed(0)).join(",")}`);
    console.log(`   CDP deltas ms: Script ${d("ScriptDuration")} Layout ${d("LayoutDuration")} RecalcStyle ${d("RecalcStyleDuration")} Task ${d("TaskDuration")} | LayoutCount ${m1.LayoutCount - m0.LayoutCount} RecalcStyleCount ${m1.RecalcStyleCount - m0.RecalcStyleCount} | panel DOM nodes ${nodes} | WS frames ${wsFrames} bytes ${wsBytes} (${(wsBytes / Math.max(1, wsFrames)).toFixed(0)}/frame, includes HA state_changed)`);
  }
} finally { await browser.close(); }
