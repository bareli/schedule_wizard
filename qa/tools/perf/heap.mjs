import { open, FIND } from "./lib.mjs";
import { execSync } from "node:child_process";
const PY = "C:/Users/barel/AppData/Local/Temp/claude/D--Code-home-assistant-extensions-good-days/f3802ecc-2b66-432d-963d-f0b1f5d18979/scratchpad/venv314/Scripts/python.exe";
const cpu = () => Number(execSync(`"${PY}" -c "import psutil;p=psutil.Process(41996);t=p.cpu_times();print(t.user+t.system)"`).toString());
const MIN = Number(process.env.MIN || 10);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
// phase A: server idle, no panel open
const a0 = cpu(); await sleep(120000); const a1 = cpu();
console.log(`SERVER no panel: ${(a1 - a0).toFixed(2)} cpu-s over 120 s = ${((a1 - a0) / 120 * 100).toFixed(2)} % of one core`);
const { browser, page } = await open();
try {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Performance.enable"); await cdp.send("HeapProfiler.enable"); await cdp.send("Runtime.enable");
  await page.evaluate(`(() => { const p = ${FIND}; p._tab="home"; p._view=null; p._render(); })()`);
  const sample = async (label) => {
    await cdp.send("HeapProfiler.collectGarbage");
    const h = await cdp.send("Runtime.getHeapUsage");
    const c = await cdp.send("Memory.getDOMCounters").catch(() => ({}));
    const proto = await cdp.send("Runtime.evaluate", { expression: "HTMLElement.prototype" });
    const q = await cdp.send("Runtime.queryObjects", { prototypeObjectId: proto.result.objectId, objectGroup: "q" });
    const n = await cdp.send("Runtime.callFunctionOn", { objectId: q.objects.objectId, functionDeclaration: "function(){return this.length}", returnByValue: true });
    await cdp.send("Runtime.releaseObjectGroup", { objectGroup: "q" });
    console.log(`${label}: heapUsed ${(h.usedSize / 1048576).toFixed(2)} MB | DOM nodes ${c.nodes} listeners ${c.jsEventListeners} documents ${c.documents} | live HTMLElement objects ${n.result.value}`);
  };
  await sleep(5000); await sample("t=0m");
  const b0 = cpu(); const t0 = Date.now();
  for (let m = 1; m <= MIN; m++) { await sleep(60000); await sample(`t=${m}m`); }
  const b1 = cpu(); const s = (Date.now() - t0) / 1000;
  console.log(`SERVER with panel (5 s poll, home tab): ${(b1 - b0).toFixed(2)} cpu-s over ${s.toFixed(0)} s = ${((b1 - b0) / s * 100).toFixed(2)} % of one core`);
} finally { await browser.close(); }
