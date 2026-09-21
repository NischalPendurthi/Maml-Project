/* CLI validation harness:  node viz/tools/check.mjs
 *
 * Loads the browser data files in a minimal fake-window sandbox and runs the
 * same KM.validate() the page runs, so the data can be checked without opening
 * a browser. Exits non-zero on error, which makes it usable from a hook or CI.
 */
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const viz = join(here, '..');

const FILES = [
  'data/meta.js',
  'data/p1-chowdhury-gopalan-2017.js',
  'data/p2-ghosh-2017.js',
  'data/p3-dubey-pentland-2020.js',
  'data/p4-amani-thrampoulidis-2021.js',
  'data/p5-kang-2026.js',
  'data/p6-arya-2026.js',
  'data/p7-dey-bhore-ghosh-2026.js',
  'data/p8-fedzoomsib-conjecture.js',
  'data/cross-edges.js',   // must load last: both endpoints have to exist
  'data/positions.js',     // generated; optional until the layout is baked
  'validate.js'
];

const sandbox = { console };
sandbox.window = sandbox;
vm.createContext(sandbox);

for (const rel of FILES) {
  const path = join(viz, rel);
  if (!existsSync(path)) {
    if (rel === 'data/positions.js') continue;          // not baked yet — fine
    console.error(`missing file: ${rel}`);
    process.exit(2);
  }
  try {
    vm.runInContext(readFileSync(path, 'utf8'), sandbox, { filename: rel });
  } catch (err) {
    console.error(`\n${rel} failed to parse or run:\n  ${err.message}\n`);
    process.exit(2);
  }
}

const result = sandbox.KM.report(console);
process.exit(result.ok ? 0 : 1);
