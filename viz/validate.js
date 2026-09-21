/* Data validation. Runs on every page load and from tools/check.mjs.
 *
 * This replaces a schema. With ~230 hand-edited nodes across nine files, the
 * failure modes are mundane and repetitive — a renamed id, an edge in the wrong
 * file, a typo'd type — so the checks are chosen to name the actual mistake and
 * the file it is in, which JSON Schema would not.
 */
(function () {
  'use strict';

  KM.validate = function () {
    var errors = [], warnings = [], i;

    var nodeTypes = {}; KM.nodeTypes.forEach(function (t) { nodeTypes[t] = 1; });
    var edgeTypes = {}; KM.edgeTypes.forEach(function (t) { edgeTypes[t] = 1; });
    var concepts  = {}; KM.concepts.forEach(function (c) { concepts[c.id] = 1; });
    var papers    = {}; KM.papers.forEach(function (p) { papers[p.id] = 1; });

    /* Problems already collected during loading (duplicate ids, unknown paper). */
    KM._problems.forEach(function (p) { errors.push(p); });

    /* ---------------------------------------------------------- nodes -- */
    Object.keys(KM.nodes).forEach(function (id) {
      var n = KM.nodes[id];

      if (!nodeTypes[n.type])       errors.push(id + ': unknown type "' + n.type + '"');
      if (!concepts[n.concept])     errors.push(id + ': unknown concept "' + n.concept + '"');
      if (!(n.tier >= 1 && n.tier <= 3)) errors.push(id + ': tier must be 1, 2 or 3 (got ' + n.tier + ')');
      if (!n.label)                 errors.push(id + ': missing label');
      if (n.label && n.label.length > 16)
        warnings.push(id + ': label "' + n.label + '" is ' + n.label.length +
                      ' chars; >16 will overflow the node on canvas');
      if (!n.statement)             errors.push(id + ': missing statement');

      /* id prefix must match the file it was registered from — catches
         paste-into-wrong-file, which is otherwise silent and very confusing. */
      var prefix = id.split('.')[0];
      if (prefix !== n.paper)
        errors.push(id + ': id prefix "' + prefix + '" does not match its paper "' + n.paper + '"');

      var st = n.proof && n.proof.status;
      if (['full', 'sketch', 'none', 'pending'].indexOf(st) < 0)
        errors.push(id + ': proof.status must be full|sketch|none|pending (got "' + st + '")');
      if ((st === 'full' || st === 'sketch') && !(n.proof.body || '').trim())
        errors.push(id + ': proof.status is "' + st + '" but proof.body is empty');
      if (st === 'none' && n.proof.body)
        warnings.push(id + ': proof.status "none" but a body is present — did you mean "sketch"?');

      /* Page provenance: required for real papers, meaningless for ours. */
      var paper = KM.papers.filter(function (p) { return p.id === n.paper; })[0];
      if (paper && paper.pdf && !(n.where && n.where.page))
        warnings.push(id + ': no where.page, so the panel cannot deep-link into the PDF');
      if (paper && paper.pages && n.where && n.where.page > paper.pages)
        errors.push(id + ': where.page ' + n.where.page + ' exceeds ' + paper.short +
                    "'s " + paper.pages + ' pages');
    });

    /* ---------------------------------------------------------- edges -- */
    KM.edges.forEach(function (e, idx) {
      var tag = 'edge[' + idx + '] ' + e.from + ' -> ' + e.to;

      if (!KM.nodes[e.from]) errors.push(tag + ': source does not resolve');
      if (!KM.nodes[e.to])   errors.push(tag + ': target does not resolve');
      if (!edgeTypes[e.type]) errors.push(tag + ': unknown edge type "' + e.type + '"');
      if (e.from === e.to)    errors.push(tag + ': self-loop');

      if (!KM.nodes[e.from] || !KM.nodes[e.to]) return;

      /* THE structural invariant the collapse algorithm relies on: the file
         boundary is the collapse boundary. A cross-paper edge hiding inside a
         per-paper file would never be re-routed into a meta-edge. */
      var isCross = KM.nodes[e.from].paper !== KM.nodes[e.to].paper;
      if (isCross && !e.cross)
        errors.push(tag + ': crosses papers but is declared in a per-paper file — ' +
                    'move it to cross-edges.js');
      if (!isCross && e.cross)
        errors.push(tag + ': stays within ' + KM.nodes[e.from].paper +
                    ' but sits in cross-edges.js — move it into that paper file');
      if (isCross && !e.note)
        warnings.push(tag + ' (' + e.type + '): cross-paper edge with no note. ' +
                      'These are the claims the project rests on — say why it holds.');
    });

    /* ------------------------------------------ cycles in the true DAG -- */
    var dagTypes = { 'depends-on': 1, 'proves': 1, 'assumes': 1 };
    var adj = {};
    KM.edges.forEach(function (e) {
      if (!dagTypes[e.type] || !KM.nodes[e.from] || !KM.nodes[e.to]) return;
      (adj[e.from] = adj[e.from] || []).push(e.to);
    });
    var state = {};   // 0 unvisited, 1 on stack, 2 done
    var stack = [];
    function visit(id) {
      if (state[id] === 2) return;
      if (state[id] === 1) {
        errors.push('cycle in depends-on: ' + stack.slice(stack.indexOf(id)).concat(id).join(' -> '));
        return;
      }
      state[id] = 1; stack.push(id);
      (adj[id] || []).forEach(visit);
      stack.pop(); state[id] = 2;
    }
    Object.keys(KM.nodes).forEach(visit);

    /* ------------------------------------------------------ positions -- */
    var missingPos = Object.keys(KM.nodes).filter(function (id) { return !KM.positions[id]; });
    if (missingPos.length && Object.keys(KM.positions).length)
      errors.push(missingPos.length + ' node(s) have no baked position — the layout is stale, ' +
                  're-run tools/bake-layout.mjs. First: ' + missingPos.slice(0, 5).join(', '));

    /* ------------------------------------------------------- censuses -- */
    var byTier = {1: 0, 2: 0, 3: 0}, byProof = {full: 0, sketch: 0, none: 0, pending: 0};
    var pendingByPaper = {};
    Object.keys(KM.nodes).forEach(function (id) {
      var n = KM.nodes[id];
      byTier[n.tier]++;
      byProof[n.proof.status]++;
      if (n.proof.status === 'pending')
        pendingByPaper[n.paper] = (pendingByPaper[n.paper] || 0) + 1;
    });

    return {
      ok: errors.length === 0,
      errors: errors,
      warnings: warnings,
      stats: {
        nodes: Object.keys(KM.nodes).length,
        edges: KM.edges.length,
        cross: KM.edges.filter(function (e) { return e.cross; }).length,
        byTier: byTier,
        byProof: byProof,
        pendingByPaper: pendingByPaper
      }
    };
  };

  /* Pretty console report; returns the result so callers can branch on it. */
  KM.report = function (log) {
    log = log || console;
    var r = KM.validate(), s = r.stats;

    log.log('Fed-ZoomSIB knowledge map — ' + s.nodes + ' nodes, ' + s.edges + ' edges (' +
            s.cross + ' cross-paper)');
    log.log('  tiers:  1:' + s.byTier[1] + '  2:' + s.byTier[2] + '  3:' + s.byTier[3]);
    log.log('  proofs: full:' + s.byProof.full + '  sketch:' + s.byProof.sketch +
            '  none:' + s.byProof.none + '  pending:' + s.byProof.pending);

    var pend = Object.keys(s.pendingByPaper);
    if (pend.length) {
      log.log('  proofs still owed, by paper:');
      pend.sort().forEach(function (p) {
        var paper = KM.papers.filter(function (x) { return x.id === p; })[0];
        log.log('    ' + p + ' ' + (paper ? paper.short : '') + ': ' + s.pendingByPaper[p]);
      });
    }

    r.warnings.forEach(function (w) { log.warn('  WARN  ' + w); });
    r.errors.forEach(function (e) { log.error('  ERROR ' + e); });
    if (r.ok) log.log('  ✓ no errors');
    return r;
  };
})();
