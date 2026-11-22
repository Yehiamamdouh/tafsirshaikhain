const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const [u, sel, out] = process.argv.slice(2);
  await p.goto('http://localhost:8765/' + u, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  const el = await p.$(sel);
  if (el) { await el.scrollIntoViewIfNeeded(); await p.evaluate(s => document.querySelector(s).scrollIntoView({block:'start'}), sel); }
  await p.waitForTimeout(500);
  const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  await p.screenshot({ path: out });
  console.log(u, sel, el ? 'found' : 'MISSING', 'scrollWidth', w[0], w[0] > w[1] ? 'HSCROLL!' : 'ok');
  await b.close();
})();
