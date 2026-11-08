// QA: node code/qa.js  (serves the folder on :8765 and takes desktop and phone screenshots into qa/)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const types = {'.html':'text/html','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.js':'text/javascript'};
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0]).replace(/\/$/, '/index.html'));
  fs.readFile(p, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, {'Content-Type': types[path.extname(p)] || 'application/octet-stream'}); r.end(d); } }); }).listen(8765);
(async () => {
  fs.mkdirSync(path.join(root, 'qa'), { recursive: true });
  const b = await chromium.launch();
  for (const [name, w, h] of [['desktop', 1280, 820], ['phone', 390, 844]]) {
    const pg = await b.newPage({ viewport: { width: w, height: h } });
    const ML = process.env.ML_DIST;   // local copy of maplibre-gl 4.7.1 dist, as the CDN is not reachable from the container
    if (ML) await pg.route(/cdn\.jsdelivr\.net\/npm\/maplibre-gl@4\.7\.1\/dist\/(.*)$/, (rt, rq) => rt.fulfill({ path: path.join(ML, rq.url().split('/').pop()) }));
    const errs = []; pg.on('console', m => { if (m.type() === 'error' && !/ERR_TUNNEL|fonts\.g/.test(m.text())) errs.push(m.text()); }); pg.on('pageerror', e => errs.push(String(e)));
    await pg.goto('http://localhost:8765/index.html?s=p065', { waitUntil: 'networkidle' });
    await pg.waitForTimeout(2500);
    await pg.screenshot({ path: `${root}/qa/${name}_sheet.png` });
    if (name === 'phone') await pg.click('#fold');
    await pg.click('#vM'); await pg.waitForTimeout(5000);
    await pg.screenshot({ path: `${root}/qa/${name}_modern.png` });
    const sw = await pg.evaluate(() => document.documentElement.scrollWidth);
    console.log(name, 'errors:', errs.length ? errs : 'none', 'scrollWidth', sw);
  }
  await b.close(); srv.close();
})();
