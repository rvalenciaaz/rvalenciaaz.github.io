const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const katex = require('../assets/vendor/katex/katex.min.js');

function hasUnsafeOutput(html) {
  return /<(?:a|img|script|iframe|object|embed)\b|\bid="unsafe-probe"|\bdata-unsafe-probe=|\bstyle="[^"]*\bbackground\s*:[^"]*url\(/i.test(html)
    || [...html.matchAll(/\bclass="([^"]*)"/g)].some(match => match[1].split(/\s+/).includes('unsafe-probe'));
}

const unsafeExpressions = [
  '\\href{javascript:alert(1)}{click}',
  '\\url{javascript:alert(1)}',
  '\\href{data:text/html,payload}{click}',
  '\\includegraphics{https://example.invalid/image.png}',
  '\\htmlClass{unsafe-probe}{x}',
  '\\htmlId{unsafe-probe}{x}',
  '\\htmlData{unsafe-probe=value}{x}',
  '\\htmlStyle{background:url(https://example.invalid/pixel)}{x}',
  '\\text{<img src=x onerror=alert(1)>}'
];
for (const expression of unsafeExpressions) {
  const html = katex.renderToString(expression, { throwOnError: false, strict: 'ignore' });
  assert(!hasUnsafeOutput(html),
    'Untrusted TeX must not create active HTML, external images or custom attributes');
}
const trustedControls = ['\\href{https://example.invalid/}{click}', ...unsafeExpressions.slice(3, 8)];
for (const expression of trustedControls) {
  assert(hasUnsafeOutput(katex.renderToString(expression, { trust: true, strict: 'ignore' })),
    'The security control must detect enabled HTML output');
}
assert.throws(() => katex.renderToString('\\def\\loop{\\loop}\\loop'), /Too many expansions/,
  'Recursive macros must stop at the expansion limit');
console.log('Passed: ' + unsafeExpressions.length + ' untrusted TeX cases, ' + trustedControls.length + ' HTML controls and the recursive-macro limit.');

let count = 0;
for (const name of ['2025-08-26-blog-post-4.md']) {
  const source = fs.readFileSync(path.join(__dirname, '..', '_posts', name), 'utf8');
  assert.match(source, /^math: true$/m, `${name} must enable math rendering`);
  assert(!source.includes('<var>'), `${name} still contains hand-formatted formulas`);
  const expressions = [...source.matchAll(/\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g)];
  assert(expressions.length > 0, `${name} has no LaTeX expressions`);
  for (const match of expressions) {
    const html = katex.renderToString(match[1] ?? match[2], {
      displayMode: match[2] !== undefined,
      throwOnError: true,
      strict: 'error'
    });
    assert(html.includes('<math') && html.includes('katex-html'), 'Math needs accessible and visual output');
    count++;
  }
}
console.log(`Passed: ${count} LaTeX expressions parse and produce HTML with accessible MathML.`);
