// Pre-render all math to SVG using mathjax-full
// Usage: node mathjax_to_svg.js <input.html> <output.html>

const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node mathjax_to_svg.js <input.html> <output.html>');
  process.exit(1);
}

const inputPath = path.resolve(args[0]);
const outputPath = path.resolve(args[1]);

if (!fs.existsSync(inputPath)) {
  console.error("Input file not found: " + inputPath);
  process.exit(1);
}

const adaptor = new liteAdaptor();
RegisterHTMLHandler(adaptor);
const tex = new TeX({ packages: AllPackages });
const svg = new SVG({ fontCache: 'local' });
const html = mathjax.document('', { InputJax: tex, OutputJax: svg });

let source = fs.readFileSync(inputPath, 'utf-8');

// Display math $$...$$
let displayCount = 0;
source = source.replace(/\$\$([\s\S]*?)\$\$/g, (full, latex) => {
  try {
    const node = html.convert(latex.trim(), { display: true });
    displayCount++;
    return adaptor.outerHTML(node);
  } catch (err) {
    console.error("  ERROR display: " + err.message);
    return full;
  }
});
console.log("Display math rendered: " + displayCount);

// Inline math $...$
let inlineCount = 0;
source = source.replace(/(?<!\$)\$(?!\$)([^$]+)\$(?!\$)/g, (full, latex) => {
  try {
    const node = html.convert(latex.trim(), { display: false });
    inlineCount++;
    return adaptor.outerHTML(node);
  } catch (err) {
    console.error("  ERROR inline: " + err.message);
    return full;
  }
});
console.log("Inline math rendered: " + inlineCount);

// Remove MathJax client-side scripts
source = source.replace(/<script[^>]*>\s*MathJax\s*=\s*\{[\s\S]*?<\/script>/g,
  '<!-- MathJax pre-rendered server-side -->');
source = source.replace(/<script[^>]*mathjax[^>]*><\/script>/gi, '');

fs.writeFileSync(outputPath, source, 'utf-8');
console.log("Output: " + outputPath + " (" + Math.round(source.length/1024) + " KB)");
