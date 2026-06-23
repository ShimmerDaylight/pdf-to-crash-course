// Render HTML to A4 PDF using Playwright
// Usage: node playwright_to_pdf.js <input.html> <output.pdf>

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node playwright_to_pdf.js <input.html> <output.pdf>');
    process.exit(1);
  }

  const htmlPath = path.resolve(args[0]);
  const pdfPath = path.resolve(args[1]);

  if (!fs.existsSync(htmlPath)) {
    console.error(`Input file not found: ${htmlPath}`);
    process.exit(1);
  }

  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1024, height: 768 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  console.log('Loading HTML...');
  await page.goto('file:///' + htmlPath.replace(/\\/g, '/'), {
    waitUntil: 'networkidle',
    timeout: 30000,
  });

  // Wait for any remaining layout
  await page.waitForTimeout(800);

  console.log('Generating PDF...');
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: {
      top: '20mm',
      bottom: '20mm',
      left: '18mm',
      right: '18mm',
    },
    printBackground: true,
    displayHeaderFooter: false,
  });

  const stats = fs.statSync(pdfPath);
  console.log(`PDF saved to: ${pdfPath}`);
  console.log(`File size: ${(stats.size / 1024 / 1024).toFixed(1)} MB`);

  await browser.close();
  console.log('Done.');
})();
