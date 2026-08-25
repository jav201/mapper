// Verify prototypes/ui_components/out/index.html renders clean:
// reports console errors + pageerrors, screenshots each figure.
const { createRequire } = require('module');
const req = createRequire('C:/Users/jjgh8/.vscode/extensions/danielsanmedium.dscodegpt-3.24.48/standalone/node_modules/patchright/index.js');
const { chromium } = req('patchright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1300, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  const url = 'file:///C:/Users/jjgh8/Github/mapper/prototypes/ui_components/out/index.html';
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(400);

  const figs = await page.$$('.term-fig');
  console.log('figures:', figs.length);
  for (let i = 0; i < figs.length; i++) {
    await figs[i].screenshot({ path: `${__dirname}/out/verify-${i}.png` });
  }
  console.log(errors.length ? errors.join('\n') : 'no page errors');
  await browser.close();
})();
