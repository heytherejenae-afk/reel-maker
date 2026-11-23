// Render HTML snippets to transparent PNGs with the pre-installed Playwright Chromium.
// Usage: node html2png.js jobs.json   (jobs = [{html, out, width, height}])
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const job of jobs) {
    await page.setViewportSize({ width: job.width, height: job.height });
    // Load from a file so file:// fonts and images are allowed.
    const htmlPath = require('path').resolve(job.out.replace(/\.png$/, '.html'));
    fs.writeFileSync(htmlPath, job.html);
    await page.goto('file://' + htmlPath, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.out, omitBackground: true });
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
