import { open, FIND } from "./lib.mjs";
const { browser, page } = await open();
try {
  const r = await page.evaluate(`(() => { const p = ${FIND}; const xs=[]; const orig=HTMLAnchorElement.prototype.click; HTMLAnchorElement.prototype.click=function(){}; for(let i=0;i<20;i++){const a=performance.now(); p._downloadHistoryCsv(); xs.push(performance.now()-a);} HTMLAnchorElement.prototype.click=orig; xs.sort((a,b)=>a-b); return {n:p._state.history.length, median:xs[10], max:xs[19]}; })()`);
  console.log("CSV export of", r.n, "rows: median", r.median.toFixed(2), "ms, max", r.max.toFixed(2), "ms");
} finally { await browser.close(); }
