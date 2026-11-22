const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const pages = process.argv.slice(2);
  for (const u of pages) {
    await p.goto('http://localhost:8765/' + u, { waitUntil: 'networkidle' });
    await p.waitForTimeout(800);
    const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    const name = u.replace(/[^a-z0-9]+/gi, '_');
    await p.screenshot({ path: '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/full/shot_' + name + '.png', fullPage: false });
    console.log(u, 'scrollWidth', w[0], 'inner', w[1], w[0] > w[1] ? 'HSCROLL!' : 'ok');
  }
  await b.close();
})();
