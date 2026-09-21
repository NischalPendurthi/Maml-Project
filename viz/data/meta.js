/* Fed-ZoomSIB knowledge map — registry, vocabulary and loader.
 *
 * Loaded FIRST, before any p*.js. Everything here is plain ES5-ish JS on purpose:
 * it must work from file:// with no build step, no modules, no fetch().
 *
 * RULE: nothing in this project may read node content out of Cytoscape. Collapsed
 * children are genuinely removed from the graph, so cy.$id(...) returns empty for
 * them. The panel, search, deep links and story mode all read KM.nodes[id].
 */

window.KM = window.KM || {};

/* Where the source PDFs live, relative to the page. Local checkout serves the
   repo's papers/ one level up; the published artifact carries its own copy at
   papers/. tools/make-artifact.mjs rewrites this one line. */
KM.pdfBase = '../papers/';

/* ---------------------------------------------------------------- papers --
 * `lane` is the chronological column index; it drives the x axis in every view
 * mode, which is what keeps mode switches purely vertical.
 */
KM.papers = [
  { id: 'p1', key: 'chowdhury-gopalan-2017',
    short: 'Chowdhury & Gopalan', title: 'On Kernelized Multi-armed Bandits',
    venue: 'ICML 2017', year: 2017, arxiv: '1704.00445',
    pdf: 'arxiv-1704.00445.pdf', pages: 26,
    headline: 'IGP-UCB · GP-TS · γ_T', lane: 0 },

  { id: 'p2', key: 'ghosh-2017',
    short: 'Ghosh et al.', title: 'Misspecified Linear Bandits',
    venue: 'AAAI 2017', year: 2017, arxiv: '1704.06880',
    pdf: 'arxiv-1704.06880.pdf', pages: 12,
    headline: 'misspecification ⇒ Ω(T)', lane: 1 },

  { id: 'p3', key: 'dubey-pentland-2020',
    short: 'Dubey & Pentland', title: 'Kernel Methods for Cooperative Multi-Agent Contextual Bandits',
    venue: 'ICML 2020', year: 2020, arxiv: '2008.06220',
    pdf: 'arxiv-2008.06220.pdf', pages: 19,
    headline: 'Coop-KernelUCB · χ̄(G_γ)', lane: 2 },

  { id: 'p4', key: 'amani-thrampoulidis-2021',
    short: 'Amani & Thrampoulidis', title: 'Decentralized Multi-Agent Linear Bandits with Safety Constraints',
    venue: 'AAAI 2021', year: 2021, arxiv: '2012.00314',
    pdf: 'arxiv-2012.00314.pdf', pages: 29,
    headline: 'DLUCB · Safe-DLUCB · 1−|λ₂|', lane: 3 },

  { id: 'p5', key: 'kang-2026',
    short: 'Kang et al.', title: 'Single Index Bandits: Generalized Linear Contextual Bandits with Unknown Reward Functions',
    venue: 'ICLR 2026', year: 2026, arxiv: '2506.12751',
    pdf: 'arxiv-2506.12751.pdf', pages: 39,
    headline: 'SIB introduced · Õ(T³ᐟ⁴)', lane: 4 },

  { id: 'p6', key: 'arya-2026',
    short: 'Arya et al.', title: 'Kernel Single-Index Bandits: Estimation, Inference, and Learning',
    venue: 'arXiv 2026', year: 2026, arxiv: '2603.18938',
    pdf: 'arxiv-2603.18938.pdf', pages: 82,
    headline: 'K-SIEGE · inference · Õ(√T)', lane: 5 },

  { id: 'p7', key: 'dey-bhore-ghosh-2026',
    short: 'Dey, Bhore & Ghosh', title: 'Optimal Regret for Single Index Bandits',
    venue: 'arXiv 2026', year: 2026, arxiv: '2605.09454',
    pdf: '2605.09454-Dey-Bhore-Ghosh-Optimal-Regret-Single-Index-Bandits.pdf', pages: 31,
    headline: 'ZoomSIB-UCB · Θ̃(T²ᐟ³) TIGHT', lane: 6 },

  { id: 'p8', key: 'fedzoomsib',
    short: 'Fed-ZoomSIB (ours)', title: 'Federated Single-Index Bandits',
    venue: 'CS6007, IIT Bombay', year: 2027, arxiv: null,
    pdf: null, pages: null,
    headline: 'conjectured — open', lane: 7 }
];

/* ---------------------------------------------------------- concept lanes --
 * Reading ACROSS a lane is one idea evolving; reading DOWN a paper column is
 * that paper's whole contribution. `row` fixes the vertical order.
 */
KM.concepts = [
  { id: 'model',         row: 0, label: 'Model & assumptions',
    blurb: 'What each paper had to assume in order to get its rate.' },
  { id: 'index-est',     row: 1, label: 'Index estimation (Stein)',
    blurb: 'Score function → truncation → ℓ₁ normalisation → per-arm → federated.' },
  { id: 'link-learn',    row: 2, label: 'Link-function learning',
    blurb: 'RKHS / γ_T → kernel smoothing → IPW-KRR → binning at Δ = T⁻¹ᐟ³.' },
  { id: 'concentration', row: 3, label: 'Concentration & confidence sets',
    blurb: 'Self-normalised martingale bounds → Gram concentration → martingale CLT.' },
  { id: 'exploration',   row: 4, label: 'Exploration strategy',
    blurb: 'ETC → epoched → UCB / TS → ε-greedy → zooming over sleeping bins.' },
  { id: 'communication', row: 5, label: 'Communication & network',
    blurb: 'Clique cover and heterogeneity → consensus and spectral gap → rare communication.' },
  { id: 'safety',        row: 6, label: 'Safety',
    blurb: 'Conservative safe set from an LCB → κ_r → an unknown single-index constraint.' },
  { id: 'upper-bounds',  row: 7, label: 'Regret upper bounds',
    blurb: 'The headline chronological story: T³ᐟ⁴ → T²ᐟ³ → matched.' },
  { id: 'lower-bounds',  row: 8, label: 'Lower bounds & impossibility',
    blurb: 'Ω(T) under misspecification → Θ̃(T²ᐟ³) minimax.' },
  { id: 'open',          row: 9, label: 'Open problems & our conjectures',
    blurb: 'μ* dependence, multi-index, and the Fed-ZoomSIB targets E1–E3.' }
];

/* ------------------------------------------------------------ vocabulary --
 * `tier`: 1 load-bearing · 2 supporting · 3 appendix machinery.
 * `proof.status`: full | sketch | none | pending.  `none` is the honest value
 * for assumptions, definitions and algorithm statements; `pending` means we
 * still owe it, and validate.js counts those out loud on every load.
 */
KM.nodeTypes = [
  'assumption', 'definition', 'lemma', 'theorem', 'corollary',
  'proposition', 'algorithm', 'regret-bound', 'open-problem', 'conjecture'
];

KM.edgeTypes = [
  'depends-on',       // X's proof uses Y
  'assumes',          // result -> assumption it consumes
  'proves',           // lemma -> the theorem it establishes
  'improves-on',      // same setting, better constant or rate
  'supersedes',       // strictly replaces a previous result
  'matches',          // upper bound <-> lower bound: tightness
  'motivates',        // a negative result -> the formulation it forces
  'resolves',         // settles a previously stated open question or conjecture
  'reduces-to',       // modular reduction
  'instantiates',     // concrete algorithm -> general template
  'reuses-tool',      // borrows machinery without improving it
  'baseline-for',     // prior algorithm used as an experimental control
  'generalizes',
  'apparent-tension'  // looks contradictory, is not; `note` carries the resolution
];

/* Edge types that point backwards in time by design. The layout reverses them
 * and they are drawn distinctly, so "this one points back" reads as
 * information rather than as a rendering glitch. */
KM.retroEdgeTypes = ['supersedes', 'improves-on', 'matches', 'apparent-tension'];

/* -------------------------------------------------------------- registry --*/
KM.nodes = {};      // id -> node (the single source of truth for all UI)
KM.edges = [];      // {from, to, type, note?, cross:bool, paper?}
KM.positions = {};  // id -> {x, y}; filled by data/positions.js (generated)
KM._problems = [];  // validate.js appends here

/**
 * Register one paper's nodes and its INTRA-paper edges.
 * Intra-paper only: a cross-paper edge here is a validation error, because the
 * file boundary is the collapse boundary the meta-edge logic relies on.
 */
KM.addPaper = function (paperId, spec) {
  var paper = KM.papers.filter(function (p) { return p.id === paperId; })[0];
  if (!paper) { KM._problems.push('addPaper: unknown paper id "' + paperId + '"'); return; }

  (spec.nodes || []).forEach(function (n) {
    if (KM.nodes[n.id]) { KM._problems.push('duplicate node id "' + n.id + '"'); return; }
    n.paper = paperId;
    n.lane = paper.lane;
    n.year = paper.year;
    if (!n.proof) n.proof = { status: 'none' };
    if (!n.tier) n.tier = 1;
    KM.nodes[n.id] = n;

    // `consumes` is terse shorthand for intra-paper depends-on edges.
    (n.consumes || []).forEach(function (src) {
      KM.edges.push({ from: src, to: n.id, type: 'depends-on', cross: false, paper: paperId });
    });
  });

  (spec.edges || []).forEach(function (e) {
    e.cross = false;
    e.paper = paperId;
    KM.edges.push(e);
  });
};

/** Register cross-paper edges. These become the meta-edges when clusters
 *  collapse, and they are the assertions the project actually rests on — so
 *  every one of them should carry a `note` explaining why it holds. */
KM.addCrossEdges = function (list) {
  (list || []).forEach(function (e) { e.cross = true; KM.edges.push(e); });
};

/* ----------------------------------------------------------- conveniences --*/
KM.paperOf   = function (id) { var n = KM.nodes[id]; return n && KM.papers.filter(function (p) { return p.id === n.paper; })[0]; };
KM.conceptOf = function (id) { var n = KM.nodes[id]; return n && KM.concepts.filter(function (c) { return c.id === n.concept; })[0]; };
KM.incoming  = function (id) { return KM.edges.filter(function (e) { return e.to === id; }); };
KM.outgoing  = function (id) { return KM.edges.filter(function (e) { return e.from === id; }); };

/** Deep link into the source PDF at the right page. Chrome's viewer honours #page=N. */
KM.pdfLink = function (id) {
  var n = KM.nodes[id], p = n && KM.paperOf(id);
  if (!p || !p.pdf || !n.where || !n.where.page) return null;
  return KM.pdfBase + p.pdf + '#page=' + n.where.page;
};
