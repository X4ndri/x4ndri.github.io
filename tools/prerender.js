/* Put the page's words into the HTML that is served.
 *
 * The page builds itself from a content object at run time, so the file that
 * goes over the wire had an empty <div id="mount"></div> and not one visible
 * character in it. Search engines mostly run JavaScript now, but "mostly" is
 * the wrong bet for the page someone reads before deciding whether to
 * interview you — and link-preview bots, text extractors and readers with
 * JavaScript off do not run it at all.
 *
 * This renders the page once in a real browser and writes the result back
 * into #mount. The script still replaces that markup on load, so behaviour is
 * unchanged; what changes is that the words are there before it does.
 *
 *   node tools/prerender.js index.html
 */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const target = process.argv[2];
if (!target) { console.error('usage: node prerender.js <file.html>'); process.exit(1); }

const root = path.dirname(path.resolve(target));
const mime = { '.html': 'text/html', '.png': 'image/png', '.woff2': 'font/woff2' };

const srv = http.createServer((q, r) => {
  let f = path.join(root, decodeURI(q.url.split('?')[0]));
  if (f.endsWith('/')) f += 'index.html';
  fs.readFile(f, (e, d) => {
    if (e) { r.writeHead(404); r.end(); return; }
    r.writeHead(200, { 'Content-Type': mime[path.extname(f)] || 'text/plain' });
    r.end(d);
  });
});

srv.listen(0, async () => {
  const port = srv.address().port;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.route('**/googletagmanager.com/**', r => r.abort());   // no analytics hit from a build
  await p.goto(`http://localhost:${port}/${path.basename(target)}`);
  await p.waitForSelector('#mount .s-sec', { timeout: 15000 });
  await p.waitForTimeout(400);

  const html = await p.evaluate(() => {
    const m = document.getElementById('mount');
    // The open tile and the cycling readout are run-time state, not content.
    m.querySelectorAll('[aria-current]').forEach(e => e.removeAttribute('aria-current'));
    return m.innerHTML;
  });
  await b.close(); srv.close();

  const src = fs.readFileSync(target, 'utf8');
  const empty = '<div id="mount"></div>';
  if (!src.includes(empty)) {
    console.error('prerender: #mount is not empty — already rendered?');
    process.exit(1);
  }
  const out = src.replace(empty,
    '<div id="mount" data-prerendered>' + html + '</div>');
  fs.writeFileSync(target, out);

  const text = out.split('<body>')[1]
    .replace(/<script[\s\S]*?<\/script>/g, '')
    .replace(/<style[\s\S]*?<\/style>/g, '')
    .replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  console.log(`prerendered ${target}: ${text.length} characters of readable text in the source`);
});
