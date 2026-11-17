// Opens every page of the served book in headless Chromium at 320, 375 and 1280 px and reports what a reader
// would hit: HTTP status, console errors, sideways scroll of the page itself (long code lines must scroll inside
// their own box), a missing level-1 heading, and the Tab order's first stops. Uses the playwright-core that
// Exact's setup installs.
// Run (with `bun exact.mjs serve dist --port 8770` running): bun tools/browser-qa.ts http://127.0.0.1:8770
import { chromium } from '../../.cache-ext/exact/node_modules/playwright-core/index.mjs';
import { SECTIONS } from '../book.gen.ts';

const base = process.argv[2] ?? 'http://127.0.0.1:8770';
const paths = ['/', ...SECTIONS.map(s => `/read/${s.id}`)];
const widths = [320, 375, 1280];
const browser = await chromium.launch();
const problems: string[] = [];
let checked = 0;

for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 800 } });
  const errors: string[] = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  for (const path of paths) {
    errors.length = 0;
    const response = await page.goto(base + path, { waitUntil: 'networkidle' });
    const status = response?.status();
    const report = await page.evaluate(() => {
      const doc = document.documentElement;
      // Long code lines must scroll inside their own box, never the page.
      const pageOverflow = doc.scrollWidth - doc.clientWidth;
      return { pageOverflow, h1: document.querySelector('[role=heading][aria-level="1"], h1')?.textContent ?? '' };
    });
    checked++;
    if (status !== 200) problems.push(`${width}px ${path}: HTTP ${status}`);
    if (report.pageOverflow > 1) problems.push(`${width}px ${path}: page scrolls sideways by ${report.pageOverflow}px`);
    if (errors.length) problems.push(`${width}px ${path}: console ${errors.slice(0, 2).join(' | ')}`);
    if (!report.h1) problems.push(`${width}px ${path}: no level-1 heading`);
  }
  await page.close();
}

// Keyboard: the first Tab stops on a section page at 375 px, then Enter on the 목차 button.
const page = await browser.newPage({ viewport: { width: 375, height: 800 } });
await page.goto(`${base}/read/fde-role`, { waitUntil: 'networkidle' });
const stops: string[] = [];
for (let i = 0; i < 5; i++) {
  await page.keyboard.press('Tab');
  stops.push(await page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    const visible = el ? getComputedStyle(el).outlineStyle !== 'none' || getComputedStyle(el).boxShadow !== 'none' : false;
    return `${el?.tagName.toLowerCase()}:${(el?.textContent ?? '').trim().slice(0, 18)}${visible ? '' : '(no focus ring)'}`;
  }));
}
await page.keyboard.press('Shift+Tab');
await page.keyboard.press('Shift+Tab'); // from the 5th stop back to the 3rd, the 목차 button

await page.keyboard.press('Enter');
await page.waitForTimeout(300);
const panelOpen = await page.evaluate(() => !!document.getElementById('toc-panel'));
await browser.close();

console.log(`pages checked: ${checked} (${paths.length} paths x ${widths.length} widths)`);
console.log(`Tab stops at 375px on /read/fde-role: ${stops.join(' -> ')}`);
console.log(`Enter on the 목차 button opens the panel: ${panelOpen}`);
console.log(problems.length ? problems.join('\n') : 'no problems');
process.exit(problems.length ? 1 : 0);
