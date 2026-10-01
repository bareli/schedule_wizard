import { chromium } from "playwright";
import fs from "node:fs";
export const BASE = "http://127.0.0.1:8174";
const ACC = JSON.parse(fs.readFileSync("D:/Code/home assistant extensions/schedule_wizard/qa/fixtures/dev-accounts-8174.json", "utf8"));
const SCR = "C:/Users/barel/AppData/Local/Temp/claude/D--Code-home-assistant-extensions-good-days/f3802ecc-2b66-432d-963d-f0b1f5d18979/scratchpad";
export async function open(viewport = { width: 1280, height: 900 }) {
  const browser = await chromium.launch();
  const state = `${SCR}/sw-perf-state.json`;
  const ctx = await browser.newContext({ viewport, storageState: fs.existsSync(state) ? state : undefined });
  const page = await ctx.newPage();
  await page.goto(BASE + "/schedule-wizard");
  await page.waitForTimeout(1500);
  if (page.url().includes("/auth/")) {
    await page.locator("input[name=username]").fill(ACC.admin.username);
    await page.locator("input[name=password]").fill(ACC.admin.password);
    await page.keyboard.press("Enter");
    await page.waitForURL((u) => !u.toString().includes("/auth/"), { timeout: 20000 });
    await ctx.storageState({ path: state });
  }
  if (page.url().includes("/auth/")) throw new Error("still on login");
  await page.waitForFunction(() => {
    const find = (root) => { const q = root.querySelector && root.querySelector("schedule-wizard-panel"); if (q) return q; for (const e of root.querySelectorAll ? root.querySelectorAll("*") : []) if (e.shadowRoot) { const r = find(e.shadowRoot); if (r) return r; } return null; };
    const p = find(document); return p && p._state;
  }, null, { timeout: 40000 });
  return { browser, ctx, page };
}
export const FIND = `(() => { const find = (root) => { const q = root.querySelector && root.querySelector("schedule-wizard-panel"); if (q) return q; for (const e of root.querySelectorAll ? root.querySelectorAll("*") : []) if (e.shadowRoot) { const r = find(e.shadowRoot); if (r) return r; } return null; }; return find(document); })()`;
