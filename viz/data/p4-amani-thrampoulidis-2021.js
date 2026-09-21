/* Amani & Thrampoulidis — Decentralized Multi-Agent Linear Bandits with Safety Constraints
 * (AAAI 2021, arXiv:2012.00314v1).  The decentralisation and safety template, off the shelf.
 */
KM.addPaper('p4', {
  nodes: [

  { id: 'p4.asm1', type: 'assumption', tier: 1, concept: 'model',
    label: 'A1 consensus', title: 'Assumption 1 — communication matrix',
    where: { section: '2', page: 3 },
    statement: String.raw`\text{For a connected undirected } G \text{ on } N \text{ nodes, }
      P \in \mathbb R^{N\times N} \text{ is symmetric and doubly stochastic with}
      \\[4pt] 1 = |\lambda_1| > |\lambda_2| \ge \dots \ge |\lambda_N| .`,
    proof: { status: 'none' },
    note: 'The spectral gap 1 − |λ₂| is the ONLY way the graph topology enters the ' +
          'final bound, and it enters additively. That is the paper’s cleanest structural ' +
          'result: topology costs you a lower-order term, not a factor.',
    tags: ['ours'] },

  { id: 'p4.asm2', type: 'assumption', tier: 2, concept: 'model',
    label: 'A2 noise', title: 'Assumption 2 — sub-Gaussian noise',
    where: { section: '2', page: 3 },
    statement: String.raw`\text{For } i\in[N],\ t>0,\ \ \eta_{i,t},\ \zeta_{i,t} \text{ are}
      \text{ zero-mean } \sigma\text{-sub-Gaussian, where } \zeta \text{ is the noise on the}
      \text{ SAFETY observation.}`,
    proof: { status: 'none' } },

  { id: 'p4.asm3', type: 'assumption', tier: 2, concept: 'model',
    label: 'A3 bounded', title: 'Assumption 3 — boundedness',
    where: { section: '2', page: 3 },
    statement: String.raw`\|x\|_2 \le 1 \ \ \forall x\in\mathcal D, \qquad
      \|\theta^{*}\|_2 \le 1, \qquad \|\mu^{*}\|_2 \le 1 .`,
    proof: { status: 'none' } },

  { id: 'p4.thm1', type: 'theorem', tier: 1, concept: 'concentration',
    label: 'Thm 1', title: 'Confidence sets under imperfect consensus',
    where: { section: '2.2', page: 5 },
    statement: String.raw`\text{Fix } \epsilon\in(0,1). \text{ Under Assumptions 1–3, the}
      \text{ consensus-averaged estimate } \hat\theta_{i,t} \text{ admits a confidence ellipsoid}
      \text{ of the OFUL form, inflated by a factor controlled by } \epsilon
      \text{ and the spectral gap.}`,
    consumes: ['p4.asm1', 'p4.asm2', 'p4.asm3'],
    proof: { status: 'sketch', body: String.raw`
      The single-agent OFUL ellipsoid, widened to absorb the fact that no agent ever holds the exact
      pooled statistics.

      In a centralized problem each agent would use $A_t = \lambda I + \sum_{i,s}x_{i,s}x_{i,s}^\top$
      and $b_t = \sum_{i,s}y_{i,s}x_{i,s}$. Here agent $i$ holds only $\varepsilon$-accurate consensus
      approximations $\tilde A_{i,t}$, $\tilde b_{i,t}$, obtained by repeatedly averaging with
      neighbours through the doubly-stochastic $P$. Standard consensus analysis gives geometric
      convergence at rate $|\lambda_2|$, so running the averaging for
      $O(\log(1/\varepsilon)/\log(1/|\lambda_2|))$ rounds per cycle drives the disagreement below
      $\varepsilon$ — which is where the spectral gap enters and why Assumption 1 requires
      $|\lambda_1| > |\lambda_2|$ strictly.

      Self-normalised concentration (Abbasi-Yadkori et al.) applied to the exact pooled statistics
      gives the usual ellipsoid. Lemma 3 then converts an $\varepsilon$ perturbation of the Gram
      matrix into a multiplicative distortion of the norm $\|\cdot\|_{A^{-1}}$, provided
      $\varepsilon < 1/(4d+1)$ so the perturbed matrix stays well conditioned. Inflating the radius
      $\beta_t$ by that distortion factor restores validity for every agent simultaneously.
    ` },
    note: 'The technical core: agents never hold the exact pooled Gram matrix, only an ' +
          'ε-approximate consensus of it, and the ellipsoid must absorb that error.' },

  { id: 'p4.lem1', type: 'lemma', tier: 2, concept: 'concentration',
    label: 'Lem 1', title: 'Influence of imperfect information',
    where: { section: '2.2', page: 6 },
    statement: String.raw`\text{For } \epsilon \in \left(0, \tfrac1{4d+1}\right),
      \text{ the gap between the consensus-based and the exactly pooled statistics is bounded}
      \text{ uniformly over agents and rounds.}`,
    consumes: ['p4.thm1'],
    proof: { status: 'sketch', body: String.raw`
      A matrix-perturbation estimate. Write $\tilde A_{i,t} = A_t + E_{i,t}$ with
      $\|E_{i,t}\|_2 \le \varepsilon\,\mathrm{tr}(A_t)$, the consensus error after the cycle.

      For $\varepsilon < 1/(4d+1)$, a Neumann-series expansion of $(A_t+E)^{-1}$ converges and gives
      $\|x\|_{\tilde A^{-1}} \le (1+O(d\varepsilon))\|x\|_{A^{-1}}$ uniformly over $\|x\|_2 \le 1$;
      the $d$ appears because the trace bound aggregates $d$ eigenvalues, which is exactly why the
      admissible $\varepsilon$ shrinks with dimension. The same expansion controls
      $\|\hat\theta_{i,t}-\hat\theta^{\text{pooled}}_t\|$.

      Uniformity over agents and rounds follows by taking the worst case over $i \in [N]$ and a union
      bound over $t \in [T]$, both of which cost only logarithmic factors.
    ` } },

  { id: 'p4.lem2', type: 'lemma', tier: 2, concept: 'communication',
    label: 'Lem 2', title: 'Influence of delays — the regret of delay',
    where: { section: '2.2', page: 6 },
    statement: String.raw`\left\|x_{i,t}\right\|_{A^{-1}_{i,t}} \;\le\; e\left\|x_{i,t}\right\|_{B^{-1}},`,
    consumes: ['p4.asm1'],
    proof: { status: 'sketch', body: String.raw`
      Information travels at one hop per round, so at round $t$ agent $i$ acts on statistics that
      omit the most recent observations of distant agents. Let $B$ be the Gram matrix of everything
      that HAS arrived and $A_{i,t}$ the one agent $i$ actually holds.

      Because the missing observations are a bounded number of rank-one updates, the determinant
      ratio $\det(A_{i,t})/\det(B)$ is bounded by a constant, and the elliptical-potential argument
      converts that into $\|x_{i,t}\|_{A^{-1}_{i,t}} \le e\|x_{i,t}\|_{B^{-1}}$ — the constant $e$
      arising from $\log$ of the determinant ratio over one communication cycle.

      **Why this matters structurally.** The delay penalty enters the final bound as a separate
      ADDITIVE term $\psi(\lambda,|\lambda_2|,\varepsilon,d,N,T)$, the "regret of delay", rather than
      multiplying the main term. That is what makes arbitrary connected topologies tolerable: a badly
      connected graph costs a lower-order additive penalty, not a factor.
    ` },
    note: 'Yields the additive "regret of delay" term ψ(λ,|λ₂|,ε,d,N,T). ' +
          'The fact that it is ADDITIVE, not multiplicative, is why arbitrary topologies are ' +
          'tolerable here.' },

  { id: 'p4.alg-dlucb', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'DLUCB', title: 'Algorithm 1 — Decentralized Linear UCB',
    where: { section: '2.1', page: 4 },
    statement: String.raw`\text{Each agent plays a UCB action from its local estimate, then agents}
      \text{ run a consensus procedure with immediate neighbours, repeated over CYCLES whose}
      \text{ duration is tuned so the consensus error stays below } \epsilon.
      \text{ No master node is required.}`,
    consumes: ['p4.thm1', 'p4.asm1'],
    proof: { status: 'none' },
    note: 'Fully decentralised — this is the structural template Fed-ZoomSIB’s Phase 2 would ' +
          'follow. Phase 1 needs none of it: a Stein estimator is a sample mean, so one round of ' +
          'averaging is exact.',
    tags: ['ours'] },

  { id: 'p4.thm2', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 2', title: 'DLUCB regret',
    where: { section: '2.2', page: 7 },
    statement: String.raw`\text{With probability } \ge 1-\delta,
      \\[6pt] R_T \;\le\; 2Sd\log\!\left(1+\tfrac{NT}{d\lambda}\right)
      \;+\; 2e\beta_T\sqrt{2dNT\log\!\left(\lambda+\tfrac{NT}{d}\right)} .`,
    consumes: ['p4.alg-dlucb', 'p4.lem1', 'p4.lem2'],
    proof: { status: 'sketch', body: String.raw`
      Optimism with the widened ellipsoid, then the elliptical-potential lemma on the POOLED design.

      On the event of Theorem 1 the UCB index of the optimal action upper-bounds its true reward for
      every agent, so instantaneous regret at agent $i$ is at most
      $2\beta_t\|x_{i,t}\|_{A^{-1}_{i,t}}$. Lemma 2 replaces the local norm by the arrived-information
      norm at cost of the factor $e$, and Lemma 1 covers the consensus inexactness.

      Summing over $N$ agents and $T$ rounds and applying Cauchy-Schwarz gives
      $R_T \le \beta_T\sqrt{NT\sum\|x\|^2_{B^{-1}}}$, and the elliptical-potential lemma bounds the
      sum by $2d\log(\lambda + NT/d)$ — note $NT$, not $T$: the pooled design accumulates $N$
      observations per round, which is precisely the cooperative gain.

      The result, $2Sd\log(1+NT/(d\lambda)) + 2e\beta_T\sqrt{2dNT\log(\lambda+NT/d)}$, has a leading
      term of the SAME ORDER as a fully centralized algorithm, with the topology confined to the
      small additive first term.
    ` },
    note: 'Two additive terms: a small "regret of delay" depending on the spectral gap, and a main ' +
          'term of the SAME ORDER as a fully centralized problem. That is the headline: ' +
          'decentralisation is nearly free.',
    tags: ['headline', 'pitch'] },

  { id: 'p4.tradeoff', type: 'regret-bound', tier: 1, concept: 'communication',
    label: 'Comm. tradeoff', title: 'Table 1 — regret vs communication',
    where: { section: '2.4', page: 8 },
    statement: String.raw`\begin{array}{lll}
      \textbf{algorithm} & \textbf{regret} & \textbf{communication} \\[3pt]
      \text{DLUCB} & O\!\left(d\log(NT)\sqrt{NT}\right) & O(dN^2)\ \text{per round} \\[3pt]
      \text{RC-DLUCB} & O\!\left(\log^{1.5}(NT)\sqrt{NT}\right) & O(d^3N^{2.5})\ \text{TOTAL} \\[3pt]
      \text{no communication} & O\!\left(dN\log T\sqrt T\right) & 0 \\[3pt]
      \text{centralized} & O\!\left(d\log(NT)\sqrt{NT}\right) & O(dN^2T)
      \end{array}`,
    consumes: ['p4.thm2', 'p4.alg-rcdlucb'],
    proof: { status: 'none' },
    note: 'The exact axis extension E1 sweeps. Note RC-DLUCB’s communication is a TOTAL over ' +
          'all T rounds, not per round — a qualitative change, not a constant-factor saving.',
    tags: ['ours', 'pitch'] },

  { id: 'p4.alg-rcdlucb', type: 'algorithm', tier: 1, concept: 'communication',
    label: 'RC-DLUCB', title: 'Algorithm 4 — rare-communication DLUCB',
    where: { section: '2.3', page: 7 },
    statement: String.raw`\text{Communicate only when a local determinant test signals that the}
      \text{ pooled information has grown by a multiplicative factor, giving total communication}
      \ O(d^3N^{2.5}) \text{ over ALL } T \text{ rounds.}`,
    consumes: ['p4.alg-dlucb'],
    proof: { status: 'none' },
    note: 'Event-triggered rather than periodic. Portable to Fed-ZoomSIB Phase 2: trigger on a ' +
          'bin’s count changing by a multiplicative factor.',
    tags: ['ours'] },

  { id: 'p4.thm4', type: 'theorem', tier: 2, concept: 'upper-bounds',
    label: 'Thm 4', title: 'RC-DLUCB regret',
    where: { section: 'A', page: 22 },
    statement: String.raw`\text{For } \epsilon\in\left(0,\tfrac1{2d+1}\right), \text{ with}
      \text{ probability } \ge 1-\delta, \text{ RC-DLUCB trades a }
      N^{1.5}d\log(Nd)\log^2(NT) \text{ delay term for the reduced total communication.}`,
    consumes: ['p4.alg-rcdlucb', 'p4.thm2'],
    proof: { status: 'sketch', body: String.raw`
      RC-DLUCB replaces periodic consensus with an event trigger: communicate only when the local
      determinant $\det(A_{i,t})$ has grown by a constant multiplicative factor since the last
      exchange.

      **Bounding the number of triggers.** Since $\det(A_{i,t})$ is monotone increasing and bounded
      above by $(\lambda + NT/d)^d$, the number of multiplicative doublings — and hence the number of
      communication rounds — is $O(d\log(NT))$ over the whole horizon, independent of $T$'s
      granularity. Multiplying by the per-round cost $O(dN^2)$ and the consensus cycle length gives
      the total $O(d^3N^{2.5})$.

      **Bounding the cost of staleness.** Between triggers an agent's design matrix is stale by at
      most a constant determinant factor, which by the same elliptical-potential argument as Lemma 2
      inflates $\|x\|_{A^{-1}}$ by a constant. Accumulating this across the $O(d\log(NT))$ epochs
      yields the extra $N^{1.5}d\log(Nd)\log^2(NT)$ delay term, while the leading
      $\sqrt{NT}$ behaviour is unchanged.

      The trade is qualitative rather than constant-factor: communication becomes a TOTAL over all
      $T$ rounds instead of a per-round cost.
    ` } },

  /* ------------------------------------------------------------ safety -- */
  { id: 'p4.asm4', type: 'assumption', tier: 1, concept: 'safety',
    label: 'A4 safe seed', title: 'Assumption 4 — a known safe action exists',
    where: { section: '3', page: 8 },
    statement: String.raw`\text{A safe action } x_0 \in \mathcal D \text{ and its value }
      c_0 := \langle\mu^{*},x_0\rangle < c \text{ are known to all agents.}`,
    proof: { status: 'none' },
    note: 'Bootstrapping assumption: you cannot explore safely from nothing. In the robot framing ' +
          'this is the certified braking / yield primitive.' },

  { id: 'p4.alg-safe', type: 'algorithm', tier: 1, concept: 'safety',
    label: 'Safe-DLUCB', title: 'Algorithm 5 — Safe-DLUCB',
    where: { section: '3', page: 8 },
    statement: String.raw`\text{Unknown LINEAR safety constraint } \langle\mu^{*},x\rangle \le c
      \text{ with } c \text{ known. After playing, agent } i \text{ observes}
      \\[4pt] z_{i,t} = \langle\mu^{*},x_{i,t}\rangle + \zeta_{i,t}.
      \\[4pt] \text{Maintain a conservative safe set } \mathcal D_{i,t} \text{ from a confidence}
      \text{ region for } \mu^{*}, \text{ seeded by } x_0, \text{ and run DLUCB restricted to it.}`,
    consumes: ['p4.asm4', 'p4.alg-dlucb', 'p4.thm1'],
    proof: { status: 'none' },
    tags: ['ours'] },

  { id: 'p4.thm3', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 3', title: 'Safe-DLUCB regret — safety is order-free',
    where: { section: '3', page: 9 },
    statement: String.raw`\text{With } \kappa_r = \tfrac{c}{c-c_0}+1 \text{ and probability }
      \ge 1-2\delta,
      \\[6pt] R_T \;\le\; 2Sd\log\!\left(1+\tfrac{NT}{d\lambda}\right)
      \;+\; 2e\,\kappa_r\,\beta_T\sqrt{2dNT\log\!\left(\lambda+\tfrac{NT}{d}\right)} .`,
    consumes: ['p4.alg-safe', 'p4.thm2', 'p4.asm4'],
    proof: { status: 'sketch', body: String.raw`
      The same argument as Theorem 2, restricted to the conservative safe set, with one extra factor.

      **Safety holds throughout (Proposition 1).** The safe set $\mathcal D_{i,t}$ contains only
      actions whose UPPER confidence bound on $\langle\mu^*,x\rangle$ is below $c$, so every played
      action satisfies the constraint with probability $1-\delta$. Assumption 4 guarantees
      $\mathcal D_{i,t}$ is non-empty, since the known-safe $x_0$ always qualifies.

      **Optimism survives the restriction (Lemma 5).** The difficulty is that the true optimum may
      be excluded from the conservative safe set early on. The remedy is to compare against a
      shrunken version of the optimal action, $x^* $ pulled back toward $x_0$ by a factor; convexity
      of $\mathcal D$ plus $c_0 < c$ guarantees that shrunken point IS in the safe set, and
      Lipschitzness bounds the reward lost by shrinking. This is where
      $\kappa_r = c/(c-c_0) + 1$ appears: it measures how far one must retreat toward the seed action,
      and it blows up as $c_0 \to c$, i.e. as the known-safe action approaches the boundary.

      **Summing.** The regret decomposition then runs exactly as in Theorem 2, with each instantaneous
      term multiplied by $\kappa_r$, giving the same order and only that constant as the price of
      safety. Everything hinges on the constraint being LINEAR, so that the safe set is convex and
      a single confidence region for $\mu^*$ certifies it.
    ` },
    note: 'Same ORDER as unconstrained DLUCB — safety costs only the constant κ_r, which blows ' +
          'up as the seed action approaches the boundary (c₀ → c). Strong result, and ' +
          'entirely dependent on the constraint being LINEAR.',
    tags: ['headline'] },

  { id: 'p4.limit-linear', type: 'open-problem', tier: 1, concept: 'open',
    label: 'Gap: all linear', title: 'Limitation — everything here is linear',
    where: { section: '1', page: 1 },
    statement: String.raw`\text{Both the reward } \langle\theta^{*},x\rangle \text{ and the safety}
      \text{ constraint } \langle\mu^{*},x\rangle \le c \text{ are linear. Carrying either to an}
      \text{ unknown nonlinear link is open.}`,
    consumes: ['p4.thm2', 'p4.thm3'],
    proof: { status: 'none' },
    note: 'Fed-ZoomSIB extension E2 tier (b): a single-index safety constraint h(⟨μ*,x⟩) ' +
          '≤ c, built from a SECOND Stein estimator plus a binned lower confidence bound, ' +
          'restricting Phase-2 UCB to safe bins. Genuinely new.',
    tags: ['gap', 'ours'] }

  ]
});
