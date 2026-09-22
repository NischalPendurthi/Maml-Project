/* Fed-ZoomSIB knowledge map — application.
 *
 * TWO RULES THAT THIS FILE DEPENDS ON THROUGHOUT:
 *
 * 1. NEVER CACHE A CYTOSCAPE ELEMENT ACROSS A COLLAPSE. `edge.move()` is
 *    implemented as remove + re-add, so any held reference goes stale. Always
 *    re-query with cy.$id(id).
 *
 * 2. NEVER READ NODE CONTENT OUT OF CYTOSCAPE. Collapsed children are genuinely
 *    removed from the graph, so cy.$id('p7.thm4-3') is empty while paper 7 is
 *    collapsed. The panel, search, deep links and the story stepper all read
 *    KM.nodes[id], which is always complete.
 */
(function () {
  'use strict';

  var cy = null;
  var ec = null;                       // expand-collapse api handle
  var mode = 'concept';                // concept | timeline | matrix
  var maxTier = 1;
  var collapsed = new Set();           // container ids currently collapsed
  var selectedId = null;
  var mathCache = new Map();           // node id -> rendered panel HTML

  var $ = function (sel) { return document.querySelector(sel); };

  /* =================================================================== data */

  function yearKey(paper) {
    return paper.id === 'p8' ? 'ours' : String(paper.year);
  }

  function visibleNodeIds() {
    return Object.keys(KM.nodes).filter(function (id) { return KM.nodes[id].tier <= maxTier; });
  }

  /* Container id for a node under the current mode. */
  function containerOf(id) {
    var n = KM.nodes[id];
    if (mode === 'concept')  return 'C:' + n.concept;
    if (mode === 'timeline') return 'P:' + n.paper;
    return 'M:' + n.concept + '|' + n.paper;
  }

  function containerMeta(cid) {
    var kind = cid.charAt(0), rest = cid.slice(2);
    if (kind === 'C') {
      var c = KM.concepts.filter(function (x) { return x.id === rest; })[0];
      return { label: c.label, blurb: c.blurb, year: null, kind: 'concept', concept: c };
    }
    if (kind === 'P') {
      var p = KM.papers.filter(function (x) { return x.id === rest; })[0];
      return { label: p.short, blurb: p.headline, year: yearKey(p), kind: 'paper', paper: p };
    }
    var parts = rest.split('|');
    var cc = KM.concepts.filter(function (x) { return x.id === parts[0]; })[0];
    var pp = KM.papers.filter(function (x) { return x.id === parts[1]; })[0];
    return { label: pp.short, blurb: cc.label, year: yearKey(pp), kind: 'cell', paper: pp };
  }

  /* Centroid of a container's members, from the baked positions. A collapsed
     container sits here, so expanding grows outward from the right place. */
  function centroid(ids) {
    var sx = 0, sy = 0, n = 0;
    ids.forEach(function (id) {
      var p = KM.positions[id];
      if (p) { sx += p.x; sy += p.y; n++; }
    });
    return n ? { x: sx / n, y: sy / n } : { x: 0, y: 0 };
  }

  function buildElements() {
    var ids = visibleNodeIds();
    var byContainer = {};
    ids.forEach(function (id) {
      var c = containerOf(id);
      (byContainer[c] = byContainer[c] || []).push(id);
    });

    var els = [];

    Object.keys(byContainer).forEach(function (cid) {
      var m = containerMeta(cid), members = byContainer[cid];
      var c = centroid(members);
      var d = {
        id: cid, kind: 'container', ckind: m.kind,
        label: m.label, blurb: m.blurb,
        year: m.year || 'mixed', count: members.length,
        caption: m.label + '\n' + members.length + (members.length === 1 ? ' node' : ' nodes'),
        capline: m.label + '   \u00b7   ' + members.length +
                 (members.length === 1 ? ' node' : ' nodes')
      };

      /* A concept cluster spans every year, so it has no single position on the
         time axis. Rather than park it at a meaningless centroid, draw it as a
         full-width LANE BAR whose gradient segments sit under exactly the papers
         that contributed to it — the matrix row, collapsed. Reading across it is
         still reading across time. */
      if (m.kind === 'concept') {
        var present = {};
        members.forEach(function (id) { present[KM.nodes[id].paper] = 1; });
        d.laneBar = 1;
        /* TWO stops per lane at the segment's start and end, so each paper's
           contribution reads as a hard block rather than a smear into its
           neighbours. Absent papers get the surface colour — NOT 'transparent',
           which Cytoscape cannot parse in a gradient and silently renders black. */
        var empty = cssVar('--bg');
        var cols = [], pos = [], n = KM.papers.length;
        KM.papers.forEach(function (p, i) {
          var col = present[p.id] ? tintFor(yearKey(p)) : empty;
          cols.push(col, col);
          pos.push((i / n) * 100, ((i + 1) / n) * 100);
        });
        d.stops = cols.join(' ');
        d.stopPos = pos.map(function (v) { return v.toFixed(2); }).join(' ');
        c = { x: (KM.extent.x0 + KM.extent.x1) / 2, y: c.y };
      }

      els.push({
        group: 'nodes', data: d,
        position: { x: c.x, y: c.y },
        selectable: false, grabbable: false
      });
    });

    ids.forEach(function (id) {
      var n = KM.nodes[id];
      var p = KM.papers.filter(function (x) { return x.id === n.paper; })[0];
      els.push({
        group: 'nodes',
        data: {
          id: id, parent: containerOf(id), kind: 'node',
          label: n.label, type: n.type, tier: n.tier,
          year: yearKey(p),
          pending: n.proof.status === 'pending' ? 1 : 0
        },
        position: { x: KM.positions[id].x, y: KM.positions[id].y },
        grabbable: false
      });
    });

    var present = {};
    ids.forEach(function (id) { present[id] = 1; });
    KM.edges.forEach(function (e, i) {
      if (!present[e.from] || !present[e.to]) return;
      els.push({
        group: 'edges',
        data: {
          id: 'e' + i, source: e.from, target: e.to,
          osrc: e.from, otgt: e.to,
          type: e.type, note: e.note || '', cross: e.cross ? 1 : 0
        }
      });
    });

    return els;
  }

  /* ================================================================== style */

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function tintFor(y) { return cssVar('--tint-' + y); }
  function ringFor(y) { return cssVar('--yr-' + y); }

  var SHAPE = {
    assumption: 'ellipse', definition: 'ellipse',
    lemma: 'rectangle', theorem: 'round-rectangle', corollary: 'round-rectangle',
    proposition: 'round-rectangle', algorithm: 'diamond',
    'regret-bound': 'tag', 'open-problem': 'octagon', conjecture: 'hexagon'
  };

  /* Edge semantics are dash pattern + arrowhead + width, NEVER colour — the
     colour budget is spent on the year ramp and the one "ours" accent. */
  var EDGE = {
    'depends-on':       { dash: [],      w: 1.3, arrow: 'triangle' },
    'assumes':          { dash: [3, 3],  w: 1.1, arrow: 'triangle' },
    'proves':           { dash: [],      w: 1.9, arrow: 'triangle' },
    'improves-on':      { dash: [],      w: 2.2, arrow: 'triangle-backcurve' },
    'supersedes':       { dash: [],      w: 3.0, arrow: 'triangle-backcurve' },
    'matches':          { dash: [6, 3],  w: 2.4, arrow: 'triangle' },
    'motivates':        { dash: [7, 4],  w: 1.7, arrow: 'vee' },
    'resolves':         { dash: [7, 4],  w: 2.4, arrow: 'vee' },
    'reduces-to':       { dash: [],      w: 2.6, arrow: 'diamond' },
    'instantiates':     { dash: [2, 3],  w: 1.5, arrow: 'vee' },
    'reuses-tool':      { dash: [2, 4],  w: 1.3, arrow: 'vee' },
    'baseline-for':     { dash: [1, 4],  w: 1.2, arrow: 'circle' },
    'generalizes':      { dash: [5, 3],  w: 1.6, arrow: 'triangle-tee' },
    'apparent-tension': { dash: [4, 4],  w: 2.0, arrow: 'tee' }
  };

  function buildStyle() {
    var tint = {
      '2017': cssVar('--tint-2017'), '2020': cssVar('--tint-2020'),
      '2021': cssVar('--tint-2021'), '2026': cssVar('--tint-2026'),
      'ours': cssVar('--tint-ours')
    };
    var ring = {
      '2017': cssVar('--yr-2017'), '2020': cssVar('--yr-2020'),
      '2021': cssVar('--yr-2021'), '2026': cssVar('--yr-2026'),
      'ours': cssVar('--yr-ours')
    };
    var ink = cssVar('--ink'), ink2 = cssVar('--ink-2'), ink3 = cssVar('--ink-3');
    var edge = cssVar('--edge'), edgeStr = cssVar('--edge-str'), surface = cssVar('--surface');

    var s = [
      { selector: 'node[kind="node"]', style: {
          'label': 'data(label)', 'font-family': 'IBM Plex Sans, system-ui, sans-serif',
          'font-size': 11, 'font-weight': 500, 'color': ink,
          'text-valign': 'center', 'text-halign': 'center',
          'text-max-width': 118, 'text-wrap': 'ellipsis',
          'width': 'label', 'height': 26, 'padding': '7px',
          'background-color': surface, 'border-width': 1.6,
          'shape': 'round-rectangle',
          'transition-property': 'opacity, background-color, border-color',
          'transition-duration': '160ms'
      }},
      { selector: 'node[kind="container"]', style: {
          'label': function (e) { return e.data('label'); },
          'font-family': 'Source Serif 4, Georgia, serif',
          'font-size': 15, 'font-weight': 600, 'color': ink,
          'text-valign': 'top', 'text-halign': 'center', 'text-margin-y': -8,
          'background-color': surface, 'background-opacity': .5,
          'border-width': 1.2, 'border-style': 'dashed', 'border-color': cssVar('--line-2'),
          'shape': 'round-rectangle', 'padding': '22px',
          'z-compound-depth': 'bottom'
      }},
      /* A collapsed container is a real object, not a bounding box: solid fill,
         solid border, its member count on a second line. */
      { selector: 'node.cy-expand-collapse-collapsed-node', style: {
          'label': 'data(caption)',
          'background-color': cssVar('--surface-2'), 'background-opacity': 1,
          'border-style': 'solid', 'border-width': 2, 'border-color': cssVar('--line-2'),
          'shape': 'round-rectangle', 'width': 190, 'height': 62,
          'text-valign': 'center', 'text-halign': 'center', 'text-margin-y': 0,
          'font-size': 17, 'text-wrap': 'wrap', 'text-max-width': 168,
          'line-height': 1.35, 'color': ink
      }},
      /* Collapsed concept lane: a full-width bar, its gradient segments sitting
         under the papers that contributed. */
      { selector: 'node.cy-expand-collapse-collapsed-node[laneBar=1]', style: {
          'width': Math.max(640, (KM.extent.x1 - KM.extent.x0) + 260), 'height': 52,
          'background-fill': 'linear-gradient',
          'background-gradient-direction': 'to-right',
          'background-gradient-stop-colors': 'data(stops)',
          'background-gradient-stop-positions': 'data(stopPos)',
          'label': 'data(capline)',
          'font-size': 23, 'text-max-width': 900, 'text-wrap': 'none',
          'text-halign': 'center', 'text-valign': 'center',
          'text-background-color': cssVar('--surface'), 'text-background-opacity': .82,
          'text-background-padding': 5, 'text-background-shape': 'roundrectangle',
          'border-color': cssVar('--line-2'), 'border-width': 1.2
      }},
      { selector: 'edge', style: {
          'curve-style': 'straight', 'line-color': edge, 'target-arrow-color': edge,
          'width': 1.3, 'target-arrow-shape': 'triangle', 'arrow-scale': .9,
          'opacity': .75,
          'transition-property': 'opacity, line-color, width', 'transition-duration': '160ms'
      }},
      { selector: 'edge[cross=1]', style: {
          'line-color': edgeStr, 'target-arrow-color': edgeStr, 'opacity': .95
      }},
      { selector: 'edge.bundle-rep', style: {
          'label': function (e) { return e.data('type') + ' ×' + e.data('bundleCount'); },
          'font-family': 'IBM Plex Mono, monospace', 'font-size': 9.5, 'color': ink3,
          'text-background-color': surface, 'text-background-opacity': .9,
          'text-background-padding': 2, 'text-rotation': 'autorotate'
      }},
      { selector: '.faded', style: { 'opacity': .07, 'text-opacity': .07 } },
      { selector: 'node.hit', style: {
          'border-width': 3, 'border-color': cssVar('--accent')
      }},
      { selector: 'node:selected', style: {
          'border-width': 3.4, 'border-color': cssVar('--accent')
      }},
      { selector: 'edge.lit', style: { 'opacity': 1, 'width': 3.2, 'line-color': cssVar('--accent'),
          'target-arrow-color': cssVar('--accent') } },
      { selector: 'node[pending=1]', style: { 'border-style': 'dotted' } }
    ];

    Object.keys(tint).forEach(function (y) {
      s.push({ selector: 'node[kind="node"][year="' + y + '"]', style: {
        'background-color': tint[y], 'border-color': ring[y] } });
      s.push({ selector: 'node[kind="container"][year="' + y + '"]', style: {
        'background-color': tint[y], 'border-color': ring[y] } });
    });

    Object.keys(SHAPE).forEach(function (t) {
      s.push({ selector: 'node[type="' + t + '"]', style: { 'shape': SHAPE[t] } });
    });

    Object.keys(EDGE).forEach(function (t) {
      var d = EDGE[t];
      s.push({ selector: 'edge[type="' + t + '"]', style: {
        'width': d.w, 'target-arrow-shape': d.arrow,
        'line-style': d.dash.length ? 'dashed' : 'solid',
        'line-dash-pattern': d.dash.length ? d.dash : undefined
      }});
    });

    return s;
  }

  /* ============================================== meta-edge de-duplication */
  /* The extension re-routes boundary-crossing edges onto the collapsed cluster
     correctly, but nine edges between two collapsed papers become nine parallel
     arrows fanned by bezier bundling. Group by (source, target, type), keep one
     representative labelled "×9", and hide the rest with display:none.
     Presentational only — the edges stay IN the graph, so the extension's own
     repairEdges still finds them on expand. Nothing to reconstruct. */
  function bundleMetaEdges() {
    if (!cy) return;
    cy.batch(function () {
      cy.edges().removeClass('bundle-rep').removeData('bundleCount').style('display', 'element');
      var groups = {};
      cy.edges().forEach(function (e) {
        var src = cy.$id(e.data('source')), tgt = cy.$id(e.data('target'));
        var bothCollapsed = src.hasClass('cy-expand-collapse-collapsed-node') &&
                            tgt.hasClass('cy-expand-collapse-collapsed-node');
        var k = e.data('source') + '|' + e.data('target') +
                (bothCollapsed ? '' : '|' + e.data('type'));
        (groups[k] = groups[k] || []).push(e.id());
      });
      Object.keys(groups).forEach(function (k) {
        var list = groups[k];
        if (list.length < 2) return;
        cy.$id(list[0]).addClass('bundle-rep').data('bundleCount', list.length);
        for (var i = 1; i < list.length; i++) cy.$id(list[i]).style('display', 'none');
      });
    });
  }

  /* Every lane bar shares one centre x, so meta-edges between them would all
     degenerate onto a single vertical line. Anchor each one at the horizontal
     position of the node it actually comes from, which both fans them out and
     makes the attachment point meaningful: an edge leaves a lane under the paper
     that produced it. */
  function anchorMetaEdges() {
    var mid = (KM.extent.x0 + KM.extent.x1) / 2;
    cy.edges().forEach(function (e) {
      ['source', 'target'].forEach(function (end) {
        var holder = cy.$id(e.data(end));
        var orig = KM.positions[e.data(end === 'source' ? 'osrc' : 'otgt')];
        if (holder.nonempty() && holder.data('laneBar') && orig) {
          e.style(end + '-endpoint', Math.round(orig.x - mid) + 'px 0px');
        } else {
          e.style(end + '-endpoint', 'outside-to-node');
        }
      });
    });
  }

  /* Collapsed clusters can overlap vertically. Deterministic separation pass
     over the <=10 visible cluster nodes, x held fixed so the chronology is
     untouched. */
  function separateY() {
    var nodes = cy.nodes('.cy-expand-collapse-collapsed-node').sort(function (a, b) {
      return a.position('y') - b.position('y');
    });
    var MIN = 74;
    for (var i = 1; i < nodes.length; i++) {
      var prev = nodes[i - 1], cur = nodes[i];
      if (Math.abs(cur.position('x') - prev.position('x')) > 300) continue;
      var need = prev.position('y') + MIN - cur.position('y');
      if (need > 0) cur.position('y', cur.position('y') + need);
    }
  }

  /* ================================================================== build */

  function render(opts) {
    opts = opts || {};
    var els = buildElements();
    var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (cy) { cy.destroy(); cy = null; ec = null; }

    cy = cytoscape({
      container: $('#cy'),
      elements: els,
      style: buildStyle(),
      layout: { name: 'preset', fit: false },
      /* Culls labels below this rendered size. At 100 nodes the perf argument for
         a high threshold does not apply, and a high value is what silently hides
         the cluster captions when the view is fitted. */
      minZoomedFontSize: 5,
      textureOnViewport: true,
      motionBlur: false,
      wheelSensitivity: 0.18,
      boxSelectionEnabled: false,
      autoungrabify: true,
      maxZoom: 2.5, minZoom: 0.08
    });

    if (typeof cytoscapeExpandCollapse !== 'undefined' && KM.useExpandCollapse !== false) {
      ec = cy.expandCollapse({
        layoutBy: null,       // we own layout
        fisheye: false,       // DEFAULT true — would reposition bystanders, killing the axis
        animate: false,       // DEFAULT true — a 1000ms tween that fights our own animate()
        undoable: false,
        cueEnabled: true,
        expandCollapseCuePosition: 'top-left',
        expandCollapseCueSize: 13,
        zIndex: 2,
        animationDuration: 0
      });

      cy.on('expandcollapse.aftercollapse', function (evt) {
        collapsed.add(evt.target.id());
        requestAnimationFrame(function () { separateY(); bundleMetaEdges(); anchorMetaEdges(); });
      });

      cy.on('expandcollapse.afterexpand', 'node', function () {
        var parent = this;
        collapsed.delete(parent.id());
        var c = { x: parent.position('x'), y: parent.position('y') };
        var kids = parent.descendants();
        if (!reduced) {
          kids.forEach(function (n) {
            var target = KM.positions[n.id()];
            if (!target) return;
            n.position(c);
            n.style('opacity', 0);
            n.animate({ position: { x: target.x, y: target.y }, style: { opacity: 1 } },
                      { duration: 420, easing: 'ease-out-cubic' });
          });
        } else {
          kids.forEach(function (n) {
            var t = KM.positions[n.id()];
            if (t) n.position(t);
            n.style('opacity', 1);
          });
        }
        requestAnimationFrame(function () { bundleMetaEdges(); anchorMetaEdges(); });
      });
    }

    /* Restore collapse state across a rebuild. On first render everything is
       collapsed, which is the landing view the brief asked for. */
    var containers = cy.nodes('[kind="container"]');
    if (opts.firstRender) {
      collapsed = new Set(containers.map(function (n) { return n.id(); }));
    }
    if (ec) {
      containers.forEach(function (n) {
        if (collapsed.has(n.id()) && ec.isCollapsible(n)) ec.collapse(n);
      });
      /* Re-seat collapsed clusters on their true centroid; the extension does
         not move them, and a cleared bounding box would otherwise drift. */
      cy.nodes('.cy-expand-collapse-collapsed-node').forEach(function (n) {
        var members = Object.keys(KM.nodes).filter(function (id) {
          return KM.nodes[id].tier <= maxTier && containerOf(id) === n.id();
        });
        var c = centroid(members);
        /* A lane bar spans the whole time axis, so only its ROW is meaningful.
           Re-seating it on its centroid would slide each lane sideways by its own
           mean, breaking alignment with the axis above. */
        if (n.data('laneBar')) c.x = (KM.extent.x0 + KM.extent.x1) / 2;
        n.position(c);
      });
      separateY();
    }

    bundleMetaEdges();
    anchorMetaEdges();
    wireGraphEvents();

    if (opts.fit !== false) initialView();
    syncAxis();
  }

  /* Fit to WIDTH, not to everything. Fitting the full 2368x1898 field into a
     laptop viewport lands around zoom 0.43, which shrinks the cluster captions
     to ~7px — technically drawn, practically unreadable. Height is the binding
     constraint, and vertical panning is cheap, so show the full time axis and
     the first few lanes at a legible zoom instead. */
  function initialView() {
    var bb = cy.elements().boundingBox();
    var w = cy.width(), h = cy.height();
    if (!bb.w || !w) { cy.fit(undefined, 60); return; }
    var z = Math.min(Math.max((w - 120) / bb.w, 0.34), 1.0);
    if (bb.h * z < h - 120) z = Math.min(z, (h - 120) / bb.h);   // it all fits: use it
    cy.zoom(z);
    cy.pan({ x: (w - bb.w * z) / 2 - bb.x1 * z, y: 60 - bb.y1 * z });
  }

  function wireGraphEvents() {
    cy.on('tap', 'node[kind="node"]', function () { openPanel(this.id()); });

    cy.on('tap', 'node[kind="container"]', function () {
      if (!ec) return;
      var n = this;
      if (ec.isCollapsible(n)) collapseWithGrowth(n);
      else if (ec.isExpandable(n)) ec.expand(n);
    });

    cy.on('tap', 'edge', function () {
      var e = this;
      if (e.data('note')) showEdgeNote(e.data());
    });

    cy.on('tap', function (evt) { if (evt.target === cy) closePanel(); });
    cy.on('viewport', syncAxis);
  }

  /* Mirror of the expand animation: shrink children into the centroid FIRST,
     then collapse. Calling collapse first would remove them before they move. */
  function collapseWithGrowth(parent) {
    var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var kids = parent.descendants();
    if (reduced || !kids.length) { ec.collapse(parent); return; }
    var c = centroid(kids.map(function (n) { return n.id(); }));
    var pending = kids.length;
    kids.forEach(function (n) {
      n.animate({ position: c, style: { opacity: 0 } },
        { duration: 260, easing: 'ease-in-cubic', complete: function () {
            if (--pending === 0) { ec.collapse(parent); }
        }});
    });
  }

  /* ============================================================== year axis */

  function syncAxis() {
    if (!cy) return;
    var z = cy.zoom(), p = cy.pan();
    var host = $('#axis');
    if (!host._ticks) {
      host._ticks = KM.papers.map(function (paper) {
        var lane = KM.lanes.filter(function (l) { return l.id === paper.id; })[0];
        var el = document.createElement('div');
        el.className = 'tick';
        el.innerHTML = '<b>' + (paper.id === 'p8' ? 'ours' : paper.year) + '</b>' +
                       escapeHtml(paper.short);
        host.appendChild(el);
        return { el: el, x: lane.x - 40 };
      });
    }
    /* Clamp each tick to its lane's CURRENT on-screen width, or adjacent paper
       names overlap as soon as the view zooms out. */
    var laneW = (KM.lanes[1] ? KM.lanes[1].x - KM.lanes[0].x : 310) * z;
    host._ticks.forEach(function (t) {
      t.el.style.transform = 'translateX(' + (t.x * z + p.x) + 'px)';
      t.el.style.maxWidth = Math.max(46, laneW - 6) + 'px';
      t.el.style.opacity = z < 0.22 ? 0.45 : 1;
    });
  }

  /* ================================================================== panel */

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function tex(src, display) {
    if (typeof katex === 'undefined') return '<code>' + escapeHtml(src) + '</code>';
    try {
      return katex.renderToString(src, {
        displayMode: display !== false, throwOnError: false, trust: false,
        strict: false, maxSize: 30
      });
    } catch (err) {
      return '<code>' + escapeHtml(src) + '</code>';
    }
  }

  /* Prose with display ($$...$$) and inline ($...$) math, plus **bold**.
     Tokenised in ONE left-to-right pass rather than split on a single-$ regex:
     a naive split mis-pairs the delimiters of a $$...$$ block and inverts the
     text/math parity for everything after it, which silently turns the rest of
     a proof into garbled italics. */
  function prose(src) {
    var s = String(src), out = '', i = 0;

    function flushText(txt) {
      // paragraph breaks are handled by the caller; here: escape + bold
      var esc = escapeHtml(txt);
      return esc.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    }

    while (i < s.length) {
      var dd = s.indexOf('$$', i);
      var sd = s.indexOf('$', i);
      // a lone '$' that is really the start of '$$' must not be treated as inline
      if (dd >= 0 && dd === sd) {
        var end = s.indexOf('$$', dd + 2);
        if (end < 0) { out += flushText(s.slice(i)); break; }
        out += flushText(s.slice(i, dd));
        out += tex(s.slice(dd + 2, end), true);
        i = end + 2;
      } else if (sd >= 0) {
        var e2 = s.indexOf('$', sd + 1);
        if (e2 < 0) { out += flushText(s.slice(i)); break; }
        out += flushText(s.slice(i, sd));
        out += tex(s.slice(sd + 1, e2), false);
        i = e2 + 1;
      } else {
        out += flushText(s.slice(i));
        break;
      }
    }

    /* Split into paragraphs on blank lines, but never inside a rendered block. */
    return out.split(/\n\s*\n/).map(function (p) {
      return p.trim() ? '<p>' + p + '</p>' : '';
    }).join('');
  }

  var PROOF_LABEL = {
    full: 'full proof', sketch: 'proof sketch',
    none: 'no proof (definition or assumption)', pending: 'proof not yet transcribed'
  };

  function panelHtml(id) {
    if (mathCache.has(id)) return mathCache.get(id);
    var n = KM.nodes[id];
    var paper = KM.paperOf(id);
    var concept = KM.conceptOf(id);
    var pdf = KM.pdfLink(id);
    var h = '';

    h += '<div class="sec"><h3>Statement</h3><div class="math">' + tex(n.statement) + '</div></div>';

    var assumes = KM.incoming(id).filter(function (e) {
      return KM.nodes[e.from] && KM.nodes[e.from].type === 'assumption';
    });
    if (assumes.length) {
      h += '<div class="sec"><h3>Assumes</h3><div class="chips">' +
        assumes.map(function (e) {
          return '<span class="chip">' + escapeHtml(KM.nodes[e.from].label) + '</span>';
        }).join('') + '</div></div>';
    }

    var st = n.proof.status;
    h += '<div class="sec"><details class="proof"' + (st === 'full' || st === 'sketch' ? ' open' : '') +
         '><summary>' + PROOF_LABEL[st] + '</summary>';
    if (n.proof.body) h += '<div class="prose">' + prose(n.proof.body) + '</div>';
    else if (st === 'pending')
      h += '<div class="prose"><p>Not yet transcribed from the source. ' +
           (pdf ? 'It is in the paper at <a href="' + pdf + '" target="_blank" rel="noopener">page ' +
                  n.where.page + '</a>.' : '') + '</p></div>';
    else h += '<div class="prose"><p>This node states a definition or an assumption; ' +
              'there is nothing to prove.</p></div>';
    h += '</details></div>';

    if (n.note) {
      h += '<div class="sec"><h3>Why it matters</h3><div class="note' +
           (n.paper === 'p8' ? ' ours' : '') + '">' + prose(n.note) + '</div></div>';
    }

    h += relSection('Depends on', KM.incoming(id));
    h += relSection('Used by', KM.outgoing(id));

    var meta = [];
    meta.push('<span class="chip">' + escapeHtml(n.type) + '</span>');
    meta.push('<span class="chip">tier ' + n.tier + '</span>');
    meta.push('<span class="chip">' + escapeHtml(concept ? concept.label : n.concept) + '</span>');
    meta.push('<span class="chip badge-' + st + '">' + st + '</span>');
    h += '<div class="sec"><h3>Metadata</h3><div class="chips">' + meta.join('') + '</div></div>';

    mathCache.set(id, h);
    return h;
  }

  function relSection(title, edges) {
    if (!edges.length) return '';
    var h = '<div class="sec"><h3>' + title + ' <span style="color:var(--ink-3)">' +
            edges.length + '</span></h3><ul class="links">';
    edges.forEach(function (e) {
      var otherId = (title === 'Depends on') ? e.from : e.to;
      var other = KM.nodes[otherId];
      if (!other) return;
      var p = KM.paperOf(otherId);
      h += '<li><button data-goto="' + escapeHtml(otherId) + '">' +
           '<span class="rel">' + escapeHtml(e.type) + '</span>' +
           '<span><b>' + escapeHtml(other.label) + '</b> &middot; ' +
           escapeHtml(p ? p.short : '') + '</span></button>';
      if (e.note) h += '<span class="why">' + escapeHtml(e.note) + '</span>';
      h += '</li>';
    });
    return h + '</ul></div>';
  }

  function openPanel(id) {
    var n = KM.nodes[id];
    if (!n) return;
    selectedId = id;
    var paper = KM.paperOf(id);
    var pdf = KM.pdfLink(id);

    $('#panelKicker').innerHTML =
      '<span>' + escapeHtml(n.type) + '</span>' +
      (n.tags && n.tags.indexOf('headline') >= 0 ? '<span style="color:var(--accent)">headline</span>' : '') +
      (n.paper === 'p8' ? '<span style="color:var(--ours)">ours &middot; conjectured</span>' : '');
    $('#panelTitle').textContent = n.title || n.label;
    $('#panelSrc').innerHTML = paper
      ? escapeHtml(paper.short) + ', <i>' + escapeHtml(paper.venue) + '</i>' +
        (pdf ? ' &middot; <a href="' + pdf + '" target="_blank" rel="noopener">§' +
               escapeHtml(n.where.section) + ', p.' + n.where.page + ' ↗</a>' : '')
      : '';
    $('#panelBody').innerHTML = panelHtml(id);
    $('#panelBody').scrollTop = 0;
    $('#panel').classList.add('open');

    if (cy) {
      cy.nodes().unselect();
      var el = cy.$id(id);
      if (el.nonempty()) el.select();
    }
    history.replaceState(null, '', '#node=' + encodeURIComponent(id));
  }

  function showEdgeNote(d) {
    selectedId = null;
    $('#panelKicker').innerHTML = '<span>relation</span>' +
      (d.cross ? '<span style="color:var(--accent)">cross-paper</span>' : '');
    $('#panelTitle').textContent = d.type;
    var a = KM.nodes[d.source], b = KM.nodes[d.target];
    $('#panelSrc').innerHTML = a && b
      ? escapeHtml(a.label) + ' → ' + escapeHtml(b.label) : '';
    $('#panelBody').innerHTML =
      '<div class="sec"><h3>Why this edge holds</h3><div class="note">' +
      prose(d.note) + '</div></div>' +
      (a && b ? '<div class="sec"><h3>Endpoints</h3><ul class="links">' +
        '<li><button data-goto="' + escapeHtml(d.source) + '"><span class="rel">from</span><span><b>' +
        escapeHtml(a.label) + '</b></span></button></li>' +
        '<li><button data-goto="' + escapeHtml(d.target) + '"><span class="rel">to</span><span><b>' +
        escapeHtml(b.label) + '</b></span></button></li></ul></div>' : '');
    $('#panel').classList.add('open');
  }

  function closePanel() {
    $('#panel').classList.remove('open');
    selectedId = null;
    if (cy) cy.nodes().unselect();
    history.replaceState(null, '', location.pathname + location.search);
  }

  /* Reveal a node that may be inside a collapsed container. */
  function goTo(id) {
    if (!KM.nodes[id]) return;
    if (KM.nodes[id].tier > maxTier) {
      maxTier = KM.nodes[id].tier;
      $('#tier').value = maxTier;
      updateTierLabel();
      render({ fit: false });
    }
    var cid = containerOf(id);
    if (ec && collapsed.has(cid)) {
      var container = cy.$id(cid);
      if (container.nonempty() && ec.isExpandable(container)) ec.expand(container);
    }
    setTimeout(function () {
      var el = cy.$id(id);
      if (el.nonempty()) {
        cy.animate({ center: { eles: el }, zoom: Math.max(cy.zoom(), 0.75) }, { duration: 380 });
      }
      openPanel(id);
    }, 60);
  }

  /* ================================================================ focus */

  function focusOn(id) {
    var el = cy.$id(id);
    if (el.empty()) return;
    var sub = el.union(el.predecessors()).union(el.successors());
    cy.batch(function () {
      cy.elements().addClass('faded');
      sub.removeClass('faded');
      sub.edges().addClass('lit');
    });
  }
  function clearFocus() {
    if (!cy) return;
    cy.batch(function () { cy.elements().removeClass('faded lit'); });
  }

  /* ================================================================ search */

  function runSearch(q) {
    if (!cy) return;
    cy.nodes().removeClass('hit');
    q = q.trim().toLowerCase();
    if (!q) return;
    var hits = Object.keys(KM.nodes).filter(function (id) {
      var n = KM.nodes[id];
      return (n.label + ' ' + (n.title || '') + ' ' + id + ' ' + (n.note || ''))
        .toLowerCase().indexOf(q) >= 0;
    });
    /* Expand any container holding a hit, so search can find things that are
       currently collapsed away. */
    if (ec) {
      var want = new Set(hits.map(containerOf));
      want.forEach(function (cid) {
        var c = cy.$id(cid);
        if (c.nonempty() && ec.isExpandable(c)) ec.expand(c);
      });
    }
    setTimeout(function () {
      var eles = cy.collection();
      hits.forEach(function (id) {
        var el = cy.$id(id);
        if (el.nonempty()) { el.addClass('hit'); eles = eles.union(el); }
      });
      if (eles.nonempty()) cy.animate({ fit: { eles: eles, padding: 90 } }, { duration: 380 });
    }, 80);
  }

  /* ============================================================== controls */

  function updateTierLabel() {
    var counts = { 1: 0, 2: 0, 3: 0 };
    Object.keys(KM.nodes).forEach(function (id) { counts[KM.nodes[id].tier]++; });
    var shown = 0;
    for (var t = 1; t <= maxTier; t++) shown += counts[t];
    $('#tierVal').textContent = shown + ' / ' + Object.keys(KM.nodes).length + ' nodes';
  }

  function setMode(m) {
    if (m === mode) return;
    mode = m;
    collapsed = new Set();            // container ids differ per mode
    document.querySelectorAll('#modes button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.mode === m));
    });
    var stage = $('#cy');
    stage.style.transition = 'opacity .18s';
    stage.style.opacity = '0';
    setTimeout(function () {
      render({ firstRender: true });
      stage.style.opacity = '1';
    }, 180);
  }

  function setTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem('km-theme', t); } catch (e) { /* private window */ }
    $('#themeBtn').textContent = t === 'dark' ? 'Light' : 'Dark';
    if (cy) cy.style(buildStyle());
  }

  function wireControls() {
    document.querySelectorAll('#modes button').forEach(function (b) {
      b.addEventListener('click', function () { setMode(b.dataset.mode); });
    });

    $('#tier').addEventListener('input', function () {
      maxTier = +this.value;
      updateTierLabel();
      render({ fit: false });
    });

    $('#expandAll').addEventListener('click', function () {
      if (!ec) return;
      ec.expandAll();
      collapsed.clear();
      requestAnimationFrame(function () { bundleMetaEdges(); anchorMetaEdges(); cy.fit(undefined, 60); });
    });
    $('#collapseAll').addEventListener('click', function () {
      if (!ec) return;
      ec.collapseAll();
      collapsed = new Set(cy.nodes('[kind="container"]').map(function (n) { return n.id(); }));
      requestAnimationFrame(function () { separateY(); bundleMetaEdges(); anchorMetaEdges(); cy.fit(undefined, 60); });
    });

    $('#themeBtn').addEventListener('click', function () {
      var cur = document.documentElement.getAttribute('data-theme');
      setTheme(cur === 'dark' ? 'light' : 'dark');
    });

    var t = null;
    $('#search').addEventListener('input', function () {
      var v = this.value;
      clearTimeout(t);
      t = setTimeout(function () { runSearch(v); }, 220);
    });

    $('#panelClose').addEventListener('click', closePanel);

    $('#panelBody').addEventListener('click', function (e) {
      var b = e.target.closest('[data-goto]');
      if (b) goTo(b.dataset.goto);
    });

    $('#focusBtn').addEventListener('click', function () {
      if (selectedId) focusOn(selectedId); else clearFocus();
    });
    $('#clearFocusBtn').addEventListener('click', clearFocus);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closePanel(); clearFocus(); }
      if (e.key === '/' && document.activeElement !== $('#search')) {
        e.preventDefault(); $('#search').focus();
      }
    });

    window.addEventListener('resize', syncAxis);
  }

  /* ================================================================== boot */

  function showProblems(result) {
    if (result.ok && !result.warnings.length) return;
    var el = document.createElement('div');
    el.id = 'problems';
    el.innerHTML = '<b>' + (result.errors.length ? 'DATA ERRORS' : 'data warnings') + '</b><br>' +
      result.errors.concat(result.warnings).slice(0, 24)
        .map(function (s) { return escapeHtml(s); }).join('<br>');
    $('#stage').appendChild(el);
    if (!result.errors.length) setTimeout(function () { el.remove(); }, 9000);
  }

  function boot() {
    var saved = null;
    try { saved = localStorage.getItem('km-theme'); } catch (e) { /* ignore */ }
    if (saved) setTheme(saved);
    else $('#themeBtn').textContent =
      matchMedia('(prefers-color-scheme: dark)').matches ? 'Light' : 'Dark';

    var result = KM.report(console);
    showProblems(result);

    wireControls();
    updateTierLabel();
    render({ firstRender: true });

    var m = /#node=([^&]+)/.exec(location.hash);
    if (m) setTimeout(function () { goTo(decodeURIComponent(m[1])); }, 220);

    setTimeout(function () {
      var h = $('#hint');
      if (h) { h.style.opacity = '0'; setTimeout(function () { h.remove(); }, 400); }
    }, 7000);
  }

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
