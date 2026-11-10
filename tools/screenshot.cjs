#!/usr/bin/env node
/* Screenshot SHIVAS pages on desktop and phone.

     node tools/screenshot.cjs                         # home, galvanizing, wire drawing, one item, one article
     node tools/screenshot.cjs index.html items/kettle.html --full --out /tmp/shots
     node tools/screenshot.cjs --serve                 # only serve site/ on http://localhost:8080 until stopped

   Serves site/ itself on a free port (no other server needed), then writes
   <out>/<page>--desktop.png and <out>/<page>--phone.png. Also prints console errors and failed requests,
   so a broken script or missing file shows up even when the picture looks fine. */
const http = require('http');
const zlib = require('zlib');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const flag = (n) => args.includes(n);
const opt = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.resolve(opt('--root', path.join(__dirname, '..', 'site')));
const OUT = path.resolve(opt('--out', path.join(__dirname, '..', 'preview', 'shots')));
const FULL = flag('--full');
const SCALE = Number(opt('--scale', '1'));
const skip = new Set(['--root', '--out', '--scale', '--port']);
const pages = args.filter((a, i) => !a.startsWith('--') && !skip.has(args[i - 1]));
const PAGES = pages.length ? pages : ['index.html', 'galvanizing.html', 'wire-drawing.html', 'items/kettle.html', 'blog/pickling-right.html'];

const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
  '.xml': 'application/xml', '.txt': 'text/plain', '.avif': 'image/avif', '.woff2': 'font/woff2' };

function serve(port) {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      if (p.endsWith('/')) p += 'index.html';
      const f = path.join(ROOT, p);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end('not found'); }
      const type = TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream';
      // gzip text like GitHub Pages / Cloudflare do, so speed tests see realistic transfer sizes
      if (/text|javascript|json|xml|svg/.test(type) && /gzip/.test(req.headers['accept-encoding'] || '')) {
        res.writeHead(200, { 'Content-Type': type, 'Content-Encoding': 'gzip', 'Cache-Control': 'max-age=600' });
        return fs.createReadStream(f).pipe(zlib.createGzip()).pipe(res);
      }
      res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'max-age=600' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(port, '127.0.0.1', () => resolve(srv));
  });
}

(async () => {
  if (flag('--serve')) {
    const port = Number(opt('--port', '8080'));
    await serve(port);
    console.log(`Serving ${ROOT} on http://localhost:${port}/  (Ctrl+C to stop)`);
    return;
  }
  const { chromium, devices } = require('playwright');
  const srv = await serve(0);
  const base = `http://127.0.0.1:${srv.address().port}/`;
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const setups = [
    ['desktop', { viewport: { width: 1440, height: 900 }, deviceScaleFactor: SCALE }],
    ['phone', { ...devices['iPhone 13'] }],
  ];
  let problems = 0;
  for (const [name, ctxOpts] of setups) {
    const ctx = await browser.newContext(ctxOpts);
    for (const pg of PAGES) {
      const page = await ctx.newPage();
      const issues = [];
      page.on('console', (m) => { if (m.type() === 'error') issues.push('console: ' + m.text()); });
      page.on('pageerror', (e) => issues.push('script error: ' + e.message));
      page.on('requestfailed', (r) => { if (r.url().startsWith(base)) issues.push('failed: ' + r.url().slice(base.length)); });
      page.on('response', (r) => { if (r.url().startsWith(base) && r.status() >= 400) issues.push(`${r.status()}: ${r.url().slice(base.length)}`); });
      try {
        await page.goto(base + pg, { waitUntil: 'load', timeout: 30000 });
      } catch (e) {
        issues.push('load: ' + e.message.split('\n')[0]);
      }
      if (FULL) {   // full-length shots: load lazy images first, or they show as empty boxes
        await page.evaluate(async () => {
          const imgs = [...document.images]; imgs.forEach((i) => { i.loading = 'eager'; });
          await Promise.race([Promise.all(imgs.map((i) => i.complete ? 0 : new Promise((ok) => { i.onload = i.onerror = ok; }))),
            new Promise((ok) => setTimeout(ok, 8000))]);
          // walk down the page so decode-on-view images and scroll reveals render, then go back up
          for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.8) { scrollTo(0, y); await new Promise((ok) => setTimeout(ok, 120)); }
          scrollTo(0, 0); await new Promise((ok) => setTimeout(ok, 300));
        }).catch(() => {});
      }
      await page.waitForTimeout(600);
      const file = path.join(OUT, `${pg.replace(/[\/#?]/g, '_').replace(/\.html$/, '')}--${name}.png`);
      await page.screenshot({ path: file, fullPage: FULL });
      console.log(`${name.padEnd(7)} ${pg}  ->  ${file}`);
      for (const i of issues) { console.log('        ! ' + i); problems++; }
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  srv.close();
  console.log(problems ? `\n${problems} problem(s) seen while loading.` : '\nNo console errors or failed local requests.');
})();
