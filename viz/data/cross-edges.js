/* CROSS-PAPER EDGES — the file that carries the project's thesis.
 *
 * These are the edges that become meta-edges when paper clusters collapse, and
 * they are the assertions Fed-ZoomSIB actually rests on. Every one carries a
 * `note` saying WHY it holds; an edge here without a note is an edge nobody has
 * thought about yet.
 *
 * Loaded LAST, after every p*.js, so that both endpoints already exist.
 */
KM.addCrossEdges([

  /* ===================================================================
   * 1. Why the problem exists at all: misspecification is fatal
   * =================================================================== */
  { from: 'p2.thm1', to: 'p5.problem', type: 'motivates',
    note: 'The founding argument of the whole single-index line. Any algorithm optimal on linear ' +
          'instances suffers Ω(T) under a perturbation of a SINGLE arm — so assuming a known ' +
          'link is not a harmless convenience, and misspecification does not degrade gracefully, ' +
          'it fails outright. That is what makes "unknown f" the honest formulation rather than a ' +
          'generalisation for its own sake.' },

  { from: 'p2.thm2', to: 'p5.problem', type: 'motivates',
    note: 'And non-sparsity does not rescue you either: OFUL still incurs Ω(T) under large ' +
          'non-sparse deviation. So the fix cannot be a better linear algorithm — the model itself ' +
          'has to change.' },

  { from: 'p2.alg-rlb', to: 'p5.alg-gstor', type: 'motivates',
    note: 'RLB’s answer is a hypothesis TEST: decide whether the model is linear, then commit ' +
          'to OFUL or fall back to UCB. That treats the link as binary. GSTOR is the next move — ' +
          'stop testing the link and start ESTIMATING it.' },

  /* ===================================================================
   * 2. The Stein estimator: introduced, then sharpened
   * =================================================================== */
  { from: 'p5.thm3-1', to: 'p7.lem2-1', type: 'improves-on',
    note: 'Same truncated Stein estimator, one change: Dey et al. normalise to ' +
          'θ̂0 = θ̂/‖θ̂‖₁. Kang et al. only ever ' +
          'recover μ*θ* and never need the scale, because monotonicity means ranking by ' +
          'projection is enough. Once the link is non-monotone you must locate the index on the ' +
          'real line, so the scale matters — and ℓ₁ is chosen because the Phase-2 ' +
          'discretisation is built on ℓ₁ geometry.' },

  { from: 'p5.identifiability', to: 'p7.lem2-1', type: 'depends-on',
    note: 'The ‖θ*‖₁ = 1 convention is what makes the normalised estimator ' +
          'well defined; without fixing the scale there is nothing for θ̂0 to converge to.' },

  { from: 'p6.prop1', to: 'p7.stein-identity', type: 'generalizes',
    note: 'Arya et al. state the first-order non-Gaussian Stein identity in general form (after ' +
          'Yang et al. 2017); the single-index version used by Kang and Dey is the special case ' +
          'g(x) = f(xᵀθ*). Same tool, three papers.' },

  { from: 'p5.thm3-1', to: 'p6.alg-ksiege', type: 'reuses-tool',
    note: 'K-SIEGE estimates each arm’s βᵢ by the same score-based method, agnostic ' +
          'to the unknown link — but per arm, on inverse-propensity-weighted data, which is what ' +
          'makes the accompanying inference hard.' },

  /* ===================================================================
   * 3. The rate: T^{3/4} -> T^{2/3}, and the conjecture it settles
   * =================================================================== */
  { from: 'p7.thm4-3', to: 'p5.thm3-9', type: 'supersedes',
    note: 'Õ(d²T^{2/3}) replaces O(d^{3/8}T^{3/4}) for general non-monotone links — and ' +
          'Theorem 5.1 shows it cannot be improved. Read the trade honestly though: Dey et al. are ' +
          'WORSE in d (d² vs d^{3/8}) and better in T. Remark 4.5 argues the T exponent ' +
          'amortises the d cost even at moderate T, which the Phase-1 experiments corroborate.' },

  { from: 'p7.thm5-1', to: 'p5.conj-sqrtT', type: 'resolves',
    note: 'Kang et al. conjectured √T is unattainable for general links, reasoning by analogy ' +
          'with Lipschitz bandits. Right about the obstruction, wrong about where it bites: the ' +
          'true minimax rate is Θ̃(T^{2/3}), strictly between their T^{3/4} and √T.' },

  { from: 'p5.monotone', to: 'p7.alg-zoomsib', type: 'motivates',
    note: 'ZoomSIB-UCB exists to remove exactly this assumption. Under monotonicity the best arm ' +
          'is the largest projection and f never needs estimating; without it you must resolve f ' +
          'on the index line, which is what the binning does.' },

  { from: 'p5.alg-gstor', to: 'p7.alg-zoomsib', type: 'improves-on',
    note: 'Both split their samples: estimate θ* first, then the link. GSTOR then COMMITS ' +
          '(explore-then-commit); ZoomSIB keeps running UCB over the bins for the remaining ' +
          'horizon. That single structural difference is the T^{3/4} → T^{2/3} gain.' },

  /* ===================================================================
   * 4. The apparent contradiction — pre-answered for the pitch
   * =================================================================== */
  { from: 'p6.thm6', to: 'p7.thm5-1', type: 'apparent-tension',
    note: 'APPARENT ONLY, and worth being able to say crisply. Arya et al. obtain Õ(√T), ' +
          'which looks like it beats a Θ̃(T^{2/3}) MINIMAX lower bound. It does not: ' +
          'their rate holds under a COMMON Lipschitz link shared by all arms, so the only thing ' +
          'differing between arms is the finite-dimensional βₐ and the problem is ' +
          'effectively parametric. Dey et al. quantify over the general non-monotone bounded-' +
          'Lipschitz class. Different function classes — no contradiction.' },

  { from: 'p6.thm5', to: 'p7.thm4-3', type: 'apparent-tension',
    note: 'Same resolution at T^{2/3}: Arya et al. reach T^{2/3} only for a FINITE-DIMENSIONAL ' +
          'RKHS (T^{4/5} in general), and against a per-arm model with finitely many arms. Dey et ' +
          'al.’s T^{2/3} is over a continuum of arms with one shared unknown link.' },

  /* ===================================================================
   * 5. The confidence-set lineage
   * =================================================================== */
  { from: 'p1.thm2', to: 'p3.lem1', type: 'depends-on',
    note: 'Dubey & Pentland do not reprove the RKHS confidence band — they cite Chowdhury & ' +
          'Gopalan Theorem 2 directly and instantiate it per agent. The uniformity over all x, ' +
          'which is exactly what Theorem 2 adds over Maillard (2016), is what lets a single band ' +
          'cover every agent’s continuum-armed decision set.' },

  { from: 'p1.info-gain', to: 'p3.cor1', type: 'depends-on',
    note: 'γ_T is the complexity measure the cooperative bound is written in; the product ' +
          'kernel turns it into Υ_z·γ̂_{VT}, splitting agent similarity from ' +
          'action complexity.' },

  { from: 'p1.rkhs-model', to: 'p6.m3', type: 'generalizes',
    note: 'Arya et al. adopt the same bounded-RKHS model class, but over the ONE-DIMENSIONAL ' +
          'index Xᵀβᵢ rather than over R^d. That is the whole point: kernel ' +
          'regression on a scalar dodges the curse of dimensionality that makes IGP-UCB degrade ' +
          'as d grows.' },

  { from: 'p1.alg-igpucb', to: 'p8.setting', type: 'baseline-for',
    note: 'The "no structure exploited" control in our experiments: it learns a full ' +
          'd-dimensional function without using the single-index structure, so its regret should ' +
          'degrade visibly as d grows. Phase-1 results confirm it (final regret 8510 on the ' +
          'quadratic link vs 2657 for ZoomSIB-UCB).' },

  { from: 'p5.alg-estor', to: 'p8.setting', type: 'baseline-for',
    note: 'The monotonicity assumption made visible: ESTOR is WORSE than LinUCB on the quadratic ' +
          'link (21267 vs 17865) and best of all on the logistic one (708). Exactly what an ' +
          'assumption-violation should look like.' },

  { from: 'p5.alg-gstor', to: 'p8.setting', type: 'baseline-for',
    note: 'The shape-agnostic explore-then-commit control — the direct predecessor of our ' +
          'backbone, so the gap between them measures what the T^{3/4} → T^{2/3} improvement ' +
          'is actually worth (10593 vs 2657 at T = 20000).' },

  /* ===================================================================
   * 6. The multi-agent machinery Fed-ZoomSIB plugs in
   * =================================================================== */
  { from: 'p7.prop4-7', to: 'p8.coop-sleeping', type: 'reduces-to',
    note: 'THE HINGE, and the reason this project is tractable as a course project. Prop 4.7 says ' +
          'Phase 2 is a black box: any sleeping-bandit algorithm with a regret guarantee against ' +
          'the best AVAILABLE arm slots straight in. A cooperative multi-agent sleeping bandit is ' +
          'exactly such an algorithm. So the theory reduces to two separable lemmas instead of one ' +
          'monolithic proof — which de-risks the whole theoretical component.' },

  { from: 'p7.lemC6', to: 'p8.coop-sleeping', type: 'depends-on',
    note: 'The single-agent sleeping-UCB bound is the slot the cooperative version replaces. ' +
          'Getting √(N_bins·N·T) instead of N·√(N_bins·T) here IS ' +
          'the √N speedup claim.' },

  { from: 'p3.cor1', to: 'p8.coop-sleeping', type: 'depends-on',
    note: 'Supplies the per-agent regret notion and the "collaboration buys a √N-type ' +
          'speedup" framing that the Phase-2 claim invokes.' },

  { from: 'p4.thm2', to: 'p8.coop-sleeping', type: 'depends-on',
    note: 'DLUCB shows a fully decentralised algorithm can match the CENTRALIZED regret order, ' +
          'with topology entering only as an additive spectral-gap term. That is the precedent ' +
          'making the Phase-2 conjecture plausible rather than optimistic.' },

  { from: 'p4.asm1', to: 'p8.setting', type: 'depends-on',
    note: 'The doubly-stochastic consensus matrix and its spectral gap are carried over verbatim ' +
          'as the communication model.' },

  { from: 'p3.def2', to: 'p8.e3', type: 'depends-on',
    note: 'Fed-ZoomSIB’s core setting is Υ_z = 1 (one shared θ*), the most ' +
          'favourable case. E3 is precisely the move to 1 < Υ_z < V, where naive averaging ' +
          'starts causing negative transfer.' },

  { from: 'p3.mmd', to: 'p8.e3', type: 'reuses-tool',
    note: 'Kernel mean embeddings estimate agent similarity from observed contexts when it is not ' +
          'known a priori — the same problem E3’s IFCA alternation solves by assignment ' +
          'rather than by embedding. Two routes to the same unknown.' },

  { from: 'p4.alg-rcdlucb', to: 'p8.e1', type: 'instantiates',
    note: 'E1 ports exactly this: event-triggered rather than periodic communication, with the ' +
          'trigger being a multiplicative change in a bin’s count rather than in a ' +
          'determinant.' },

  { from: 'p4.tradeoff', to: 'p8.e1', type: 'depends-on',
    note: 'The regret-versus-communication table is the axis E1 sweeps, and the shape to beat.' },

  { from: 'p4.alg-safe', to: 'p8.e2', type: 'depends-on',
    note: 'E2 tier (a) IS Safe-DLUCB, essentially off the shelf. The conservative safe set seeded ' +
          'by a known-safe action transfers unchanged.' },

  { from: 'p4.limit-linear', to: 'p8.e2', type: 'motivates',
    note: 'E2 tier (b) is the genuinely new part: an unknown SINGLE-INDEX safety constraint ' +
          'h(⟨μ*,x⟩) ≤ c, built from a second Stein estimator plus a binned ' +
          'lower confidence bound, restricting Phase-2 UCB to safe bins. It reuses the reward ' +
          'side’s binning machinery, which is what keeps it from being a second project.' },

  { from: 'p3.limit-linear', to: 'p8.gap', type: 'motivates',
    note: 'Dubey & Pentland have the cooperative machinery but assume the link away; Dey et al. ' +
          'remove the link assumption but are single-agent. Neither cell is empty — their ' +
          'INTERSECTION is.' },

  { from: 'p7.thm4-3', to: 'p8.conj1', type: 'depends-on',
    note: 'The single-agent bound the conjecture must reduce to at N = 1.' },

  /* ===================================================================
   * 7. Shared open problems
   * =================================================================== */
  { from: 'p6.open-score', to: 'p8.score-known', type: 'depends-on',
    note: 'The known-score assumption is shared by every paper in this line, and every one of them ' +
          'flags plug-in estimation as open. Worth stating in the pitch as inherited rather than ' +
          'introduced.' },

  { from: 'p7.open-mu', to: 'p8.score-known', type: 'depends-on',
    note: 'The companion limitation: even with a known score, every bound degrades as 1/μ*, ' +
          'and μ* = 0 for a link symmetric about the context mean. Our experiments scale ' +
          'contexts so the projected index has unit variance partly to keep μ* away from 0.' },

  { from: 'p7.open-multi', to: 'p8.e4', type: 'motivates',
    note: 'Named as open by Dey et al. and carried into our roadmap as E4 — future-work slide ' +
          'only, explicitly not to be attempted.' }

]);
