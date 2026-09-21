/* Build the publishable copy:  node viz/tools/make-artifact.mjs
 *
 * Two differences from the local page, both forced by how Artifacts are served:
 *
 * 1. The Artifact runtime supplies its own <!doctype>/<html>/<head>/<body>, so
 *    the published file must contain only the page content. The local index.html
 *    keeps its full skeleton, because without a doctype a file:// page renders in
 *    quirks mode.
 * 2. Published pages are served from their own origin with a strict CSP: scripts
 *    may come from a short CDN allowlist, but STYLESHEETS, FONTS and fetch() may
 *    not. Everything here is same-origin (vendored + published as sibling files),
 *    which sidesteps that entirely — the same choice that makes the page work
 *    offline at a talk.
 *
 * Writes dist/artifact.html and dist/files.json (the publish manifest).
 */
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const viz = join(here, '..');
const dist = join(viz, 'dist');
mkdirSync(dist, { recursive: true });

/* ------------------------------------------------------------------ page -- */
let html = readFileSync(join(viz, 'index.html'), 'utf8');

const body = html.slice(html.indexOf('<body>') + '<body>'.length,
                        html.lastIndexOf('</body>'));
const headLinks = [...html.matchAll(/<link rel="stylesheet" href="([^"]+)">/g)]
  .map(m => `<link rel="stylesheet" href="${m[1]}">`).join('\n');

const title = /<title>([^<]*)<\/title>/.exec(html)[1];

writeFileSync(join(dist, 'artifact.html'),
`<title>${title}</title>
${headLinks}
${body.trim()}
`);

/* ------------------------------------------------- data with rebased PDFs -- */
const metaSrc = readFileSync(join(viz, 'data/meta.js'), 'utf8')
  .replace("KM.pdfBase = '../papers/';", "KM.pdfBase = 'papers/';");
mkdirSync(join(dist, 'data'), { recursive: true });
writeFileSync(join(dist, 'data/meta.js'), metaSrc);

/* -------------------------------------------------------------- manifest -- */
const files = {};
const add = (published, source) => { files[published] = source; };

for (const f of ['km.css', 'km.js', 'validate.js']) add(f, `viz/${f}`);
add('data/meta.js', 'viz/dist/data/meta.js');          // the rebased copy
for (const f of readdirSync(join(viz, 'data')))
  if (f.endsWith('.js') && f !== 'meta.js') add(`data/${f}`, `viz/data/${f}`);
for (const f of readdirSync(join(viz, 'vendor')))
  if (f.endsWith('.js') || f.endsWith('.css')) add(`vendor/${f}`, `viz/vendor/${f}`);
for (const f of readdirSync(join(viz, 'vendor/fonts')))
  add(`vendor/fonts/${f}`, `viz/vendor/fonts/${f}`);

/* Carry the source PDFs so the panel's "§4, p.8" deep links actually resolve in
   the published copy. Largest is ~3.8MB, well inside the 15MB per-binary cap. */
const papers = join(viz, '../papers');
if (existsSync(papers))
  for (const f of readdirSync(papers))
    if (f.endsWith('.pdf')) add(`papers/${f}`, `papers/${f}`);

writeFileSync(join(dist, 'files.json'), JSON.stringify(files, null, 2));

console.log(`artifact.html written (${(readFileSync(join(dist,'artifact.html')).length/1024).toFixed(1)} KB)`);
console.log(`${Object.keys(files).length} supporting files in dist/files.json`);
