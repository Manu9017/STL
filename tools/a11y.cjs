#!/usr/bin/env node
/* Accessibility check (axe-core, the engine inside Lighthouse) for SHIVAS pages, light and dark mode, phone width.

     node tools/a11y.cjs                         # every page except the 3D viewers
     node tools/a11y.cjs index.html items/kettle.html
     node tools/a11y.cjs --json preview/a11y.json

   Prints one line per rule and selector, with how many pages show it. Needs axe-core: tools/lighthouse.sh installs it
   (with Lighthouse) in ~/.cache/shivas-lighthouse; or: npm i axe-core in that folder. */
const fs = require('fs'), path = require('path'), os = require('os'), { spawn } = require('child_process');
const { chromium, devices } = require('playwright');
const ROOT = path.join(__dirname, '..', 'site');
const AXE = path.join(os.homedir(), '.cache', 'shivas-lighthouse', 'node_modules', 'axe-core', 'axe.min.js');
const args = process.argv.slice(2);
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : null;
let pages = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--json');
if (!pages.length) {
  pages = [];
  (function walk(d) { for (const n of fs.readdirSync(path.join(ROOT, d))) { const rel = d ? d + '/' + n : n;
    if (fs.statSync(path.join(ROOT, rel)).isDirectory()) { if (!['v', 'setup', 'photos', 'assets'].includes(rel)) walk(rel); }
    else if (n.endsWith('.html')) pages.push(rel); } })('');
  pages.sort();
}
if (!fs.existsSync(AXE)) { console.error('axe-core missing: run tools/lighthouse.sh once (it installs it)'); process.exit(2); }
const PORT = 8813;
const srv = spawn('node', [path.join(__dirname, 'screenshot.cjs'), '--serve', '--port', String(PORT)], { stdio: 'ignore' });
setTimeout(async () => {
  const b = await chromium.launch();
  const found = {}; let total = 0;
  for (const theme of ['light', 'dark']) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], colorScheme: theme });
    await ctx.addInitScript((t) => { try { localStorage.setItem('shivas.mode', t); } catch (e) {} }, theme);
    for (const p of pages) {
      const pg = await ctx.newPage();
      try {
        await pg.goto(`http://127.0.0.1:${PORT}/${p}`, { waitUntil: 'load', timeout: 30000 });
        await pg.waitForTimeout(300);
        await pg.addScriptTag({ path: AXE });
        const res = await pg.evaluate(async () => (await axe.run(document, { resultTypes: ['violations'],
          runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice'] } })).violations);
        for (const v of res) for (const n of v.nodes) {
          const key = `${v.id} | ${n.target.join(' ')}`;
          const f = found[key] || (found[key] = { rule: v.id, impact: v.impact, target: n.target.join(' '), why: (n.failureSummary || '').split('\n').slice(1, 2).join('').trim().slice(0, 140), pages: new Set(), themes: new Set() });
          f.pages.add(p); f.themes.add(theme); total++;
        }
      } catch (e) { console.log(`${theme} ${p}: ${e.message.split('\n')[0]}`); }
      await pg.close();
    }
    await ctx.close();
  }
  await b.close(); srv.kill();
  const rows = Object.values(found).sort((a, b) => a.rule.localeCompare(b.rule) || b.pages.size - a.pages.size);
  for (const r of rows) console.log(`${r.rule.padEnd(26)} ${String(r.pages.size).padStart(3)}p ${[...r.themes].join('+').padEnd(10)} ${r.target.slice(0, 70).padEnd(70)} ${r.why}  e.g. ${[...r.pages][0]}`);
  console.log(`\n${rows.length} distinct problems (${total} instances) on ${pages.length} pages x 2 themes`);
  if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(rows.map((r) => ({ ...r, pages: [...r.pages], themes: [...r.themes] })), null, 1));
  process.exit(rows.length ? 1 : 0);
}, 800);
