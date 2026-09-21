/* Bake node positions:  node viz/tools/bake-layout.mjs
 *
 * Writes data/positions.js. Run after ANY change to the node data; validate.js
 * flags a stale bake on the next page load.
 *
 * WHY NO ELK. The original plan reached for elk.bundled.js (1.6 MB) with
 * two-level partitioning. But this graph's layout is almost fully determined
 * before any layout engine runs: x is the paper's chronological lane and y is
 * the concept row, both pinned by the data. All a layered engine could still
 * choose is the ORDER of nodes inside a single (paper, concept) cell — typically
 * 1-4 nodes. A few barycentre sweeps do that in 40 lines, deterministically,
 * with no dependency and no npm install.
 *
 * THE INVARIANT EVERYTHING ELSE RELIES ON: x depends only on the paper (and the
 * node's depth within that paper). It NEVER depends on the view mode. So
 * switching Concept -> Timeline -> Matrix moves nodes vertically only, the
 * chronology never reshuffles, and expansion reads as growth rather than a
 * re-layout.
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const viz = join(here, '..');

/* ------------------------------------------------------------- geometry -- */
const COL_W      = 310;   // horizontal pitch between paper lanes
const DEPTH_DX   = 66;   // rightward nudge per step of intra-paper depth
const NODE_H     = 40;    // vertical pitch between stacked nodes in a cell
const ROW_PAD    = 62;   // blank space between concept bands
const ROW_MIN_H  = 78;    // a band is at least this tall even when nearly empty

/* -------------------------------------------------------------- loading -- */
const sandbox = { console };
sandbox.window = sandbox;
vm.createContext(sandbox);

for (const rel of [
  'data/meta.js',
  'data/p1-chowdhury-gopalan-2017.js', 'data/p2-ghosh-2017.js',
  'data/p3-dubey-pentland-2020.js',    'data/p4-amani-thrampoulidis-2021.js',
  'data/p5-kang-2026.js',              'data/p6-arya-2026.js',
  'data/p7-dey-bhore-ghosh-2026.js',   'data/p8-fedzoomsib-conjecture.js',
  'data/cross-edges.js'
]) {
  const path = join(viz, rel);
  if (!existsSync(path)) { console.error('missing ' + rel); process.exit(2); }
  vm.runInContext(readFileSync(path, 'utf8'), sandbox, { filename: rel });
}
const KM = sandbox.KM;
const ids = Object.keys(KM.nodes);

/* --------------------------------------- intra-paper longest-path depth -- */
/* Depth within the node's OWN paper, over structural edges only. Assumptions and
 * definitions land at 0, lemmas at 1, theorems at 2, corollaries at 3 — which is
 * what makes dependencies inside a paper read left-to-right as well as between
 * papers. */
const DAG = new Set(['depends-on', 'proves', 'assumes']);
const preds = {};
ids.forEach(id => (preds[id] = []));
for (const e of KM.edges) {
  if (!DAG.has(e.type)) continue;
  const a = KM.nodes[e.from], b = KM.nodes[e.to];
  if (!a || !b || a.paper !== b.paper) continue;    // intra-paper only
  preds[e.to].push(e.from);
}

const depth = {};
const MARK = Symbol('visiting');
function depthOf(id) {
  if (depth[id] === MARK) return 0;                 // cycle guard (validate.js reports it)
  if (depth[id] !== undefined) return depth[id];
  depth[id] = MARK;
  let d = 0;
  for (const p of preds[id]) d = Math.max(d, depthOf(p) + 1);
  return (depth[id] = d);
}
ids.forEach(depthOf);

/* ------------------------------------------------------------ x, pinned -- */
const x = {};
for (const id of ids) {
  const n = KM.nodes[id];
  x[id] = n.lane * COL_W + Math.min(depth[id], 3) * DEPTH_DX;
}

/* ------------------------------------- group into (concept, paper) cells -- */
const cells = new Map();                            // "concept|paper" -> [ids]
for (const id of ids) {
  const n = KM.nodes[id];
  const key = n.concept + '|' + n.paper;
  if (!cells.has(key)) cells.set(key, []);
  cells.get(key).push(id);
}
/* Deterministic seed order: shallower dependencies first, then by id. */
for (const list of cells.values()) {
  list.sort((a, b) => depth[a] - depth[b] || (a < b ? -1 : a > b ? 1 : 0));
}

/* --------------------------------------------- row heights, then slot y -- */
const rowOf = {};
KM.concepts.forEach(c => (rowOf[c.id] = c.row));

const rowSize = {};                                 // concept -> tallest cell
for (const [key, list] of cells) {
  const concept = key.split('|')[0];
  rowSize[concept] = Math.max(rowSize[concept] || 0, list.length);
}

const rowTop = {};
let cursor = 0;
for (const c of KM.concepts.slice().sort((a, b) => a.row - b.row)) {
  rowTop[c.id] = cursor;
  cursor += Math.max(ROW_MIN_H, (rowSize[c.id] || 0) * NODE_H) + ROW_PAD;
}

/* Slot index within the cell -> y. Cells are centred in their band so a sparse
 * row does not look top-aligned against a dense one. */
function slotY(concept, slot, n) {
  const bandH = Math.max(ROW_MIN_H, (rowSize[concept] || 0) * NODE_H);
  const stackH = n * NODE_H;
  return rowTop[concept] + (bandH - stackH) / 2 + slot * NODE_H + NODE_H / 2;
}

const order = new Map();                            // key -> ids in slot order
for (const [key, list] of cells) order.set(key, list.slice());

/* ------------------------------------------------- barycentre sweeps ----- */
/* The only real freedom left: the order of nodes inside one cell. Order each
 * cell by the mean y of its neighbours so edges run as flat as possible. Four
 * sweeps is well past convergence at this size, and the tie-break on id keeps
 * the result byte-identical between runs. */
const nbrs = {};
ids.forEach(id => (nbrs[id] = []));
for (const e of KM.edges) {
  if (!KM.nodes[e.from] || !KM.nodes[e.to]) continue;
  nbrs[e.from].push(e.to);
  nbrs[e.to].push(e.from);
}

let y = {};
function assignY() {
  for (const [key, list] of order) {
    const concept = key.split('|')[0];
    list.forEach((id, i) => (y[id] = slotY(concept, i, list.length)));
  }
}
assignY();

for (let sweep = 0; sweep < 4; sweep++) {
  for (const [key, list] of order) {
    if (list.length < 2) continue;
    const bary = {};
    for (const id of list) {
      const ns = nbrs[id].filter(n => y[n] !== undefined);
      bary[id] = ns.length ? ns.reduce((s, n) => s + y[n], 0) / ns.length : y[id];
    }
    list.sort((a, b) => bary[a] - bary[b] || depth[a] - depth[b] || (a < b ? -1 : 1));
  }
  assignY();
}

/* ------------------------------------------------------------ cell boxes -- */
/* Bounding box of each (concept, paper) cell, so the Matrix view can draw real
 * cells and a collapsed cluster can sit at its true centroid. */
const cellBox = {};
for (const [key, list] of order) {
  const xs = list.map(id => x[id]), ys = list.map(id => y[id]);
  cellBox[key] = {
    x: (Math.min(...xs) + Math.max(...xs)) / 2,
    y: (Math.min(...ys) + Math.max(...ys)) / 2,
    w: Math.max(...xs) - Math.min(...xs),
    h: Math.max(...ys) - Math.min(...ys),
    n: list.length
  };
}

/* ------------------------------------------------------------- emitting -- */
const positions = {};
for (const id of ids) positions[id] = { x: Math.round(x[id]), y: Math.round(y[id]) };

const bands = KM.concepts.slice().sort((a, b) => a.row - b.row).map(c => ({
  id: c.id,
  top: Math.round(rowTop[c.id]),
  height: Math.round(Math.max(ROW_MIN_H, (rowSize[c.id] || 0) * NODE_H))
}));

const lanes = KM.papers.map(p => ({ id: p.id, x: p.lane * COL_W, w: COL_W }));

const out =
`/* GENERATED by tools/bake-layout.mjs — do not hand-edit.
 * ${ids.length} nodes. Re-run after any change to the node data.
 */
KM.positions = ${JSON.stringify(positions, null, 0)};
KM.bands = ${JSON.stringify(bands)};
KM.lanes = ${JSON.stringify(lanes)};
KM.cellBox = ${JSON.stringify(cellBox)};
KM.extent = ${JSON.stringify({
  x0: Math.min(...ids.map(i => x[i])), x1: Math.max(...ids.map(i => x[i])),
  y0: 0, y1: Math.round(cursor)
})};
`;

writeFileSync(join(viz, 'data/positions.js'), out);
console.log(`baked ${ids.length} positions -> data/positions.js`);
console.log(`  extent ${Math.round(Math.min(...ids.map(i => x[i])))}..${Math.round(Math.max(...ids.map(i => x[i])))} x 0..${Math.round(cursor)}`);
console.log(`  ${cells.size} non-empty (concept x paper) cells of ${KM.concepts.length * KM.papers.length} possible`);
