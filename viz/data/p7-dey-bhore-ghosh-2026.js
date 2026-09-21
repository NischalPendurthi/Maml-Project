/* Dey, Bhore & Ghosh — Optimal Regret for Single Index Bandits (arXiv:2605.09454v3)
 * The project's backbone. Prop 4.7 is the hinge the whole Fed-ZoomSIB argument hangs on.
 */
KM.addPaper('p7', {
  nodes: [

  /* ------------------------------------------------------------- model -- */
  { id: 'p7.asm1', type: 'assumption', tier: 1, concept: 'model',
    label: 'A1 noise', title: 'Assumption 1 — noise',
    where: { section: '2', page: 3 },
    statement: String.raw`\eta_t \text{ is independent of } x_t \text{ and of the whole arm set }
      \mathcal X_t \text{ at round } t,\ \mathbb E[\eta_t \mid \mathcal F_{t-1}] = 0,
      \text{ and } \eta_t \text{ is conditionally } \sigma\text{-sub-Gaussian.}`,
    proof: { status: 'none' },
    note: 'Independence from the arm SET, not merely from the pulled arm. Phase 2 needs this: ' +
          'bin membership is determined by the whole arm set, so noise must not know it.' },

  { id: 'p7.asm2', type: 'assumption', tier: 1, concept: 'model',
    label: 'A2 score', title: 'Assumption 2 — score moment',
    where: { section: '4', page: 7 },
    statement: String.raw`\exists\, M>0 \text{ such that } \mathbb E\!\left[S_j(X)^2\right] \le M
      \quad \text{for all } j \in [d], \qquad X \sim \mathcal D.`,
    proof: { status: 'none' },
    note: 'Only a SECOND moment of the score. Identical to Kang et al. Assumption 2.2, and weaker ' +
          'than the fourth-moment conditions usual in the robust-estimation literature.' },

  { id: 'p7.asm3', type: 'assumption', tier: 1, concept: 'model',
    label: 'A3 regularity', title: 'Assumption 3 — context regularity and Lipschitz link',
    where: { section: '4', page: 7 },
    statement: String.raw`\text{Contexts are i.i.d. from a continuous } \mathcal D \text{ with }
      p \in C^1(\mathbb R^d),\ p(x)>0,\ \text{and each coordinate of } X \text{ is }
      \kappa\text{-sub-Gaussian: } \mathbb E[e^{\lambda X_j}] \le e^{\kappa^2\lambda^2/2}. \\[4pt]
      f \in C^1 \text{ with } |f(z)| \le L_f \text{ and } |f'(z)| \le L_{f'}
      \text{ for all } |z| \le C_W\sqrt{\log(dTK/\delta)}.`,
    proof: { status: 'none' },
    note: 'Boundedness of f is LOCAL — only on the effective range of the projected index, which ' +
          'Lemma C.2 shows is O(1) w.h.p. So f need not be globally bounded, and the unbounded ' +
          'links used in the experiments are admissible.' },

  /* --------------------------------------------------- index estimation -- */
  { id: 'p7.def-score', type: 'definition', tier: 2, concept: 'index-est',
    label: 'Score fn', title: 'Definition 2.1 — score function',
    where: { section: '2', page: 3 },
    statement: String.raw`S_p : \mathbb R^d \to \mathbb R^d, \qquad S_p(x) \;=\; -\nabla_x \log p(x).`,
    proof: { status: 'none' },
    note: 'Assumed KNOWN to the learner. This is inherited by the entire single-index bandit ' +
          'literature and is the assumption an audience is most likely to challenge.' },

  { id: 'p7.stein-identity', type: 'lemma', tier: 1, concept: 'index-est',
    label: "Stein id.", title: "Remark 2.2 — Stein's identity for the single-index model",
    where: { section: '2', page: 3 },
    statement: String.raw`\mathbb E\!\left[f(X^\top\theta^*)\,S(X)\right]
      \;=\; \mathbb E\!\left[f'(X^\top\theta^*)\right]\,\theta^{*}
      \;=\; \mu^{*}\theta^{*}, \qquad \mu^{*} := \mathbb E[f'(X^\top\theta^*)].`,
    consumes: ['p7.def-score', 'p7.asm3'],
    proof: { status: 'sketch', body: String.raw`
      Integration by parts against the density. Writing $\mathbb E[f(X^\top\theta^*)S(X)]
      = -\int f(x^\top\theta^*)\nabla_x p(x)\,dx$ and integrating by parts moves the gradient
      onto $f$, giving $\int \nabla_x\!\left[f(x^\top\theta^*)\right] p(x)\,dx
      = \mathbb E[f'(X^\top\theta^*)]\,\theta^*$ by the chain rule. The boundary term vanishes
      under the regularity conditions of Assumption 3.` },
    note: 'THE pivot of the whole literature. The identity never references the FORM of f, so the ' +
          'unknown direction is estimable by a plain sample average — no likelihood, no link, no ' +
          'optimisation. And a sample mean is the one statistic that federates EXACTLY.',
    tags: ['pivot', 'pitch'] },

  { id: 'p7.lem2-1', type: 'lemma', tier: 1, concept: 'index-est',
    label: 'Lem 2.1', title: 'Normalized Stein estimation error',
    where: { section: '2.2', page: 4 },
    statement: String.raw`\text{With the truncated estimator } \hat\theta = \tfrac1n\sum_i
      \varphi_\tau\!\left(y_i S(x_i)\right) \text{ and } \hat\theta_0 = \hat\theta/\|\hat\theta\|_1,
      \\[4pt] \left\|\hat\theta_0 - \theta^{*}\right\|_1 \;=\; \tilde O\!\left(\frac{d}{\mu^{*}\sqrt n}\right)
      \quad\text{with probability } 1-\delta .`,
    consumes: ['p7.stein-identity', 'p7.asm1', 'p7.asm2'],
    proof: { status: 'full', body: String.raw`
      Condition on the high-probability event of Lemma B.1, which gives
      $\|\hat\theta - \mu^*\theta^*\|_1 \le \epsilon$ with
      $\epsilon = C_\theta d\sqrt{\log(2d/\delta)/n}$.

      **Step 1 — the denominator is bounded away from zero.** By the reverse triangle
      inequality, $\big|\,\|\hat\theta\|_1 - \|\mu^*\theta^*\|_1\big| \le \|\hat\theta - \mu^*\theta^*\|_1 \le \epsilon$.
      Since $\mu^* > 0$ and $\|\theta^*\|_1 = 1$ we have $\|\mu^*\theta^*\|_1 = \mu^*$, so
      $\big|\,\|\hat\theta\|_1 - \mu^*\big| \le \epsilon$ and therefore
      $\|\hat\theta\|_1 \in [\mu^*-\epsilon,\ \mu^*+\epsilon]$. Under the sample-size condition
      $\epsilon \le \mu^*/2$ this gives $\|\hat\theta\|_1 \ge \mu^*/2 > 0$, so the normalisation is well defined.

      **Step 2 — add and subtract the target.** Writing
      $\|\hat\theta_0 - \theta^*\|_1 = \|\hat\theta\|_1^{-1}\,\|\hat\theta - \|\hat\theta\|_1\theta^*\|_1$
      and inserting $\pm\mu^*\theta^*$ inside the norm,
      $$\|\hat\theta_0-\theta^*\|_1 \le \frac{1}{\|\hat\theta\|_1}\Big(\|\hat\theta-\mu^*\theta^*\|_1 + \big|\mu^*-\|\hat\theta\|_1\big|\,\|\theta^*\|_1\Big).$$

      **Step 3 — combine.** Both bracketed terms are at most $\epsilon$ by Step 1, and
      $\|\theta^*\|_1 = 1$, so the bracket is at most $2\epsilon$. Dividing by
      $\|\hat\theta\|_1 \ge \mu^*/2$ gives $\|\hat\theta_0-\theta^*\|_1 \le 4\epsilon/\mu^*$.

      Substituting $\epsilon$ yields the stated $\tilde O\big(d/(\mu^*\sqrt n)\big)$ rate. Note where the
      $1/\mu^*$ comes from: it is purely the cost of dividing by a denominator that is itself only
      of size $\mu^*$. This is the precise origin of the $\mu^* \ne 0$ requirement.
    ` },
    note: 'The \u2113\u2081 normalisation is what removes the unknown scale \u03BC*: the unnormalised ' +
          'estimator only recovers \u03BC*\u03B8*. Dey et al. use \u2113\u2081 specifically because ' +
          'the Phase-2 discretisation is built on \u2113\u2081 geometry.' },

  /* ------------------------------------------------------- exploration -- */
  { id: 'p7.alg-zoomsib', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'ZoomSIB-UCB', title: 'Algorithm 1 — Zooming Single-Index Bandit with UCB',
    where: { section: '3', page: 5 },
    statement: String.raw`\textbf{Phase 1 } (t \le T_0),\ T_0 = \lceil d^2 T^{2/3}\,\mathrm{polylog}(dT/\delta)\rceil:
      \text{ pull arms uniformly; form } \hat\theta_0 = \hat\theta/\|\hat\theta\|_1 \text{ and FREEZE it.}
      \\[6pt] \textbf{Phase 2 } (t > T_0): \text{ partition } [-W,W],\ W = 4\kappa\sqrt{\log(TK/\delta)},
      \text{ into } N = \lceil 2W/\Delta\rceil = O(T^{1/3}) \text{ bins of width } \Delta = T^{-1/3}.
      \\[4pt] \text{Project } \hat z_{t,a} = x_{t,a}^\top\hat\theta_0,\ \text{form the available bin set }
      \mathcal B_t, \text{ and play}
      \\[4pt] a_t = \arg\max_{a:\,b_{t,a}\in\mathcal B_t} \mathrm{UCB}_{b_{t,a}}(t),
      \qquad \mathrm{UCB}_j(t) = \frac{S_j}{n_j} + \sigma\sqrt{\frac{2\log(2NT/\delta)}{n_j}} .`,
    consumes: ['p7.lem2-1'],
    proof: { status: 'none' },
    note: 'The "zooming" is NOT adaptive in the classical sense — it is a one-shot reduction from a ' +
          'd-dimensional arm space to a uniform grid on R, made possible by the single-index ' +
          'structure. \u0394 = T^{-1/3} is exactly the Lipschitz bias-variance balance.',
    tags: ['backbone', 'pitch'] },

  { id: 'p7.sample-split', type: 'proposition', tier: 1, concept: 'exploration',
    label: 'Sample split', title: 'Remark 3.1 — sample splitting is load-bearing',
    where: { section: '3', page: 6 },
    statement: String.raw`\hat\theta_0 \text{ is computed entirely from Phase-1 data and then frozen,}
      \text{ so the bin assignment } b_{t,a} \text{ is } \mathcal F_{t-1}\text{-measurable and the }
      \text{within-bin noise is a martingale difference sequence.}`,
    consumes: ['p7.alg-zoomsib'],
    proof: { status: 'none' },
    note: 'Without this the Phase-2 analysis simply breaks — reusing Phase-2 data to refine ' +
          '\u03B8\u0302 would make bin membership depend on the very noise being averaged. Any ' +
          'federated variant must preserve it.' },

  { id: 'p7.prop4-7', type: 'proposition', tier: 1, concept: 'exploration',
    label: 'Prop 4.7', title: 'Modular reduction to any sleeping bandit',
    where: { section: '4', page: 8 },
    statement: String.raw`\text{Let } \mathcal A \text{ be any bandit algorithm for } N \text{ arms with}
      \text{ stochastic availability, achieving regret } \mathrm{Reg}_{\mathcal A}(N,T)
      \text{ against the best AVAILABLE arm.}
      \\[4pt] \text{Run Phase 1 to obtain } \hat\theta_0, \text{ then run } \mathcal A
      \text{ on the } N \text{ bins. Then}
      \\[6pt] R_T \;\le\; R_T^{(1)} \;+\; \mathrm{Reg}_{\mathcal A}(N,T) \;+\; 2L_{f'} T \Delta .`,
    consumes: ['p7.alg-zoomsib', 'p7.sample-split', 'p7.lemC5'],
    proof: { status: 'sketch', body: String.raw`
      Phase 1 contributes $R_T^{(1)}$ trivially, since it plays uniformly for $T_0$ rounds and
      rewards are bounded by $L_f$. Conditioned on the Phase-1 event
      $\|\hat\theta_0-\theta^*\|_1 \le \Delta/(2L)$, every arm's projected index is displaced by at
      most half a bin width, so the induced $N$-armed sleeping instance is well defined and its bin
      assignment is $\mathcal F_{t-1}$-measurable (Remark 3.1). By Lipschitzness of $f$ and
      Lemma C.5, the best available BIN is within $2L_{f'}\Delta$ of the best available ARM at every
      round, which contributes $2L_{f'}T\Delta$ over the horizon. Applying $\mathcal A$'s own
      guarantee to that induced instance gives the middle term.` },
    note: 'THE HINGE. Phase 2 is a black box: swap in any sleeping-bandit subroutine and the bound ' +
          'follows automatically. A cooperative multi-agent sleeping bandit is exactly such a ' +
          'subroutine — so Fed-ZoomSIB reduces to (a) a federated Phase-1 concentration lemma and ' +
          '(b) a cooperative sleeping-UCB regret bound, instead of one monolithic proof.',
    tags: ['hinge', 'pitch', 'ours'] },

  /* ------------------------------------------------------ upper bounds -- */
  { id: 'p7.thm4-3', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 4.3', title: 'Main regret bound — \u00D5(d\u00B2T\u00B2\u141F\u00B3)',
    where: { section: '4', page: 7 },
    statement: String.raw`\text{Under Assumptions 1, 2, 3, with } \tau =
      \sqrt{3(\sigma^2+L_f^2)MT_0/\log(2d/\delta)} \text{ and } \mu^{*} \ge
      c_0/\mathrm{polylog}(dT/\delta), \text{ with probability } \ge 1-\delta:
      \\[6pt] R_T \;\le\; O\!\left(d^2T^{2/3}\,\mathrm{polylog}\tfrac{dT}{\delta}
      \;+\; 4\sigma\sqrt{NT\log\tfrac{2NT}{\delta}} \;+\; 4L_{f'}T^{2/3}\right)
      \;=\; \tilde O\!\left(d^2 T^{2/3}\right).`,
    consumes: ['p7.asm1', 'p7.asm2', 'p7.asm3', 'p7.lem2-1', 'p7.alg-zoomsib', 'p7.lemC5', 'p7.lemC6'],
    proof: { status: 'full', body: String.raw`
      Decompose the regret at the phase boundary and bound the two phases separately.

      **Phase 1 (Lemma C.4).** Since $|f| \le L_f$, instantaneous regret is at most $2L_f$ per round,
      so $R_T^{(1)} \le 2L_f T_0$. With
      $T_0 = \lceil (4C_\theta L/(\mu^*\Delta))^2 d^2\log(8d/\delta)\rceil$, $\Delta = T^{-1/3}$,
      $L^2 = 16\log(4dT/\delta)$ and $\mu^* \ge c_0/\mathrm{polylog}(Td/\delta)$, this is
      $O(d^2T^{2/3}\,\mathrm{polylog}(dT/\delta))$.

      **Phase 2.** For $t > T_0$ let $b_t^*$ be the bin of the optimal available arm and $b_t$ the bin
      played. Split the instantaneous regret three ways, with $\mu_j := f(\tilde z_j)$ the reward at the
      bin centre:
      $$f(z_t^*) - f(z_{t,a_t}) \;=\; \underbrace{f(z_t^*) - \mu_{b_t^*}}_{\text{(i)}} \;+\; \underbrace{\mu_{b_t^*} - \mu_{b_t}}_{\text{(ii)}} \;+\; \underbrace{\mu_{b_t} - f(z_{t,a_t})}_{\text{(iii)}}.$$

      Terms (i) and (iii) are the discretisation bias, bounded by Lemma C.5 at
      $2L_{f'}T\Delta = 2L_{f'}T^{2/3}$. Term (ii) is the bandit regret against the best AVAILABLE bin,
      bounded by the sleeping-UCB argument of Lemma C.6 at
      $4\sigma\sqrt{NT\log(2NT/\delta)} + 2sT$.

      **Balancing.** With $N = O(T^{1/3})$ bins, the Phase-2 estimation term is
      $\tilde O(\sqrt{T^{1/3}\cdot T}) = \tilde O(T^{2/3})$. So all three sources — Phase-1
      exploration, Phase-2 estimation and discretisation bias — are simultaneously $T^{2/3}$, which is
      exactly what makes $\Delta = T^{-1/3}$ the right resolution: any finer and $N$ grows, inflating
      the bandit term; any coarser and the bias term grows. Summing and taking a union bound over the
      Phase-1 event and the per-bin concentration events gives the claim with probability $1-\delta$.
    ` },
    note: 'Three terms, one per source of cost: Phase-1 exploration, Phase-2 sleeping-UCB ' +
          'estimation over N = O(T^{1/3}) bins, and discretisation bias. All three are ' +
          'simultaneously T^{2/3} — which is what makes \u0394 = T^{-1/3} the right choice.',
    tags: ['headline', 'pitch'] },

  { id: 'p7.cor4-6', type: 'corollary', tier: 2, concept: 'upper-bounds',
    label: 'Cor 4.6', title: 'Expected regret',
    where: { section: '4', page: 8 },
    statement: String.raw`\text{Setting } \delta = 1/T \text{ in Theorem 4.3: }\quad
      \mathbb E[R_T] \;=\; \tilde O\!\left(d^2T^{2/3}\right).`,
    consumes: ['p7.thm4-3'],
    proof: { status: 'sketch', body: String.raw`
      On the failure event, of probability $\delta = 1/T$, regret is at most $2L_f T$, contributing
      $O(L_f)$ in expectation. Adding this to the high-probability bound leaves the rate unchanged.` } },

  { id: 'p7.cor4-8', type: 'corollary', tier: 1, concept: 'upper-bounds',
    label: 'Cor 4.8', title: 'Instance-dependent bound',
    where: { section: '4', page: 8 },
    statement: String.raw`\text{Let } \Delta_j = \mu_{j^*} - \mu_j \text{ be the gap of bin } j
      \text{ and } s = L_{f'}\Delta. \text{ Instantiating Prop 4.7 with UCB,}
      \\[6pt] R_T^{(2)} \;\le\; O\!\left(\sum_{j:\,\Delta_j > 2s}
      \frac{\sigma^2\log(NT/\delta)}{\Delta_j}\right) \;+\; 2sT .`,
    consumes: ['p7.prop4-7'],
    proof: { status: 'sketch', body: String.raw`
      Standard gap-based UCB analysis applied to the induced $N$-bin sleeping instance, with the
      discretisation slack $s = L_{f'}\Delta$ absorbed into the confidence radius. Bins whose gap
      does not exceed $2s$ are indistinguishable from optimal at this resolution and are charged
      the flat $2sT$ term instead.` },
    note: 'If f has a unique well-separated maximum this improves to O(T^{1/3} log T). Phase-1 ' +
          'results measure a fitted exponent of 0.294 on the quadratic link — close to that ' +
          'T^{1/3} prediction, and 0.602 on the flattest link, approaching the 2/3 worst case.',
    tags: ['empirical-link'] },

  /* ------------------------------------------------------ lower bounds -- */
  { id: 'p7.thm5-1', type: 'theorem', tier: 1, concept: 'lower-bounds',
    label: 'Thm 5.1', title: 'Minimax lower bound — \u03A9\u0303(T\u00B2\u141F\u00B3)',
    where: { section: '5', page: 9 },
    statement: String.raw`\text{Under Assumptions 2 and 3, there exist } c>0 \text{ and } T_0
      \text{ such that for all } T \ge T_0 \text{ and every policy } \pi,
      \\[6pt] \sup_{(\theta^{*},f,\mathcal D)} \mathbb E\!\left[R_T(\pi)\right] \;\ge\; c\,T^{2/3},
      \\[4pt] \text{the supremum over valid instances with } d=1,\ \theta^{*}=+1,\
      \mathcal D = N(0,1),\ K = \lceil 4N\log T/p_{\min}\rceil .`,
    proof: { status: 'full', body: String.raw`
      A hypothesis-class construction at $d = 1$, $\theta^* = +1$, $\mathcal D = N(0,1)$ — so the
      hardness is in the unknown LINK, not the dimension.

      **The instances.** Partition $[0,1]$ into $N$ bins $B_j$ of width $w = 1/N$ with centres $c_j$,
      and let $B_j^\circ = [c_j - w/4,\ c_j + w/4]$ be their strictly disjoint inner halves. Define
      plateaued bump functions $\psi_j$ equal to $1$ on $B_j^\circ$, falling linearly to $0$ on
      $B_j \setminus B_j^\circ$, and $0$ elsewhere, so $\|\psi_j'\|_\infty \le 4/w = 4N$. Fix a smooth
      ramp $\rho$ with $\rho \equiv 0$ below $-1$, increasing on $(-1,0)$, and $\rho \equiv 1$ above $0$.
      For each sign vector $\beta \in \{-1,+1\}^N$ set
      $$f_\beta(z) \;=\; \tfrac12 + \lambda\rho(z) + \varepsilon\sum_{j=1}^{N}\beta_j\psi_j(z).$$

      **Validity (Lemma F.1).** Each $f_\beta$ satisfies $\|f_\beta\|_\infty \le \tfrac12+\lambda+\varepsilon \le 1 \le L_f$
      and $\|f_\beta'\|_\infty \le \lambda C_\rho + 4N\varepsilon \le 3 \le L_{f'}$, so every hypothesis is
      admissible under Assumption 3. The ramp is flat on $[0,1]$, so it does not interfere with the
      bumps, and it supplies $\mu^* = \mathbb E[f_\beta'(X)] = \lambda c_1 + O(T^{-1/3}) > 0$ with
      $c_1 > 0$ independent of $\beta$ — so the instances also satisfy the signal-strength condition
      the upper bound assumes. On $B_j^\circ$, $f_\beta \equiv \tfrac12 + \lambda + \varepsilon\beta_j$:
      the sign $\beta_j$ is the ONLY thing distinguishing bin $j$.

      **Reduction.** With $K = \lceil 4N\log T/p_{\min}\rceil$ arms drawn per round, every bin is
      available in most rounds with high probability (Lemma F.2). Playing a bin with $\beta_j = -1$
      when some $\beta_{j'} = +1$ is available costs at least $\varepsilon$ per round (Lemma F.3), so
      the problem reduces to an $N$-armed bandit in which the learner must identify the sign of each
      bin.

      **Information (Proposition F.1).** Contexts and noise are drawn independently of $\beta$, and
      $f_\beta$ and $f_{\beta \oplus j}$ differ only inside $B_j$. By the chain rule the divergence
      accumulates only over rounds that land in bin $j$, and for unit-variance Gaussian noise with
      mean gap $|\Delta\mu| \le 2\varepsilon$,
      $\mathrm{KL}(P_\beta^\pi \,\|\, P_{\beta\oplus j}^\pi) \le 2\varepsilon^2 N_j^\pi(\beta)$.

      **Bretagnolle-Huber.** Averaging over $\beta$ and applying the two-point inequality, any policy
      must either mis-identify a constant fraction of the signs or spend
      $\Omega(\varepsilon^{-2})$ pulls per bin. Since $\sum_j N_j^\pi = T$, some bin gets at most
      $T/N$ pulls, forcing regret $\Omega(N\varepsilon)$ whenever $\varepsilon \lesssim \sqrt{N/T}$.
      Optimising the free parameters at $\varepsilon \asymp 1/(2N)$ and $N \asymp T^{1/3}$ balances
      the two sources and yields $\sup_{(\theta^*,f,\mathcal D)} \mathbb E[R_T(\pi)] \ge cT^{2/3}$.

      A standard mollification $\tilde f_\beta = f_\beta * \rho_\eta$ with bandwidth $\eta = T^{-10}$
      makes every hypothesis infinitely differentiable without changing any of the above.
    ` },
    note: 'Construction: embed 2^N plateaued "bump" perturbations of height \u03B5 ~ 1/(2N) on a ' +
          'common ramp, reduce to an N-armed bandit, apply Bretagnolle\u2013Huber. Note it holds ' +
          'already at d = 1 — the hardness is in the UNKNOWN LINK, not the dimension.',
    tags: ['headline', 'pitch'] },

  /* ------------------------------------- tier-2 machinery behind Thm 4.3 -- */
  { id: 'p7.lemC5', type: 'lemma', tier: 2, concept: 'link-learn',
    label: 'Lem C.5', title: 'Discretisation bias',
    where: { section: 'C', page: 17 },
    statement: String.raw`\text{On } \mathcal E_1\cap\mathcal E_2\cap\mathcal E_3, \text{ for every }
      t>T_0 \text{ and every arm } a \text{ assigned to bin } b_{t,a}=j,
      \quad \left|f(x_{t,a}^\top\theta^{*}) - \mu_j\right| \;\le\; L_{f'}\Delta ,`,
    consumes: ['p7.asm3', 'p7.lem2-1'],
    proof: { status: 'full', body: String.raw`
      Let arm $a$ satisfy $\hat z_{t,a} \in B_j$. Two displacements accumulate, each at most $\Delta/2$:

      1. **Bin width.** By definition of the bin, $|\hat z_{t,a} - \tilde z_j| \le \Delta/2$.
      2. **Estimation error.** On the Phase-1 event, $|z_{t,a} - \hat z_{t,a}| \le \Delta/2$ — this is
         exactly what $T_0$ was calibrated to deliver, via $\|\hat\theta_0-\theta^*\|_1 \le \Delta/(2L)$
         together with $\|x_{t,a}\|_\infty \le L$.

      By the triangle inequality $|z_{t,a} - \tilde z_j| \le \Delta/2 + \Delta/2 = \Delta$. Since
      $|f'| \le L_{f'}$, the link is $L_{f'}$-Lipschitz, so
      $|f(z_{t,a}) - \mu_j| = |f(z_{t,a}) - f(\tilde z_j)| \le L_{f'}\Delta$.

      Applying this to both the optimal available arm ($a = a_t^*$, $j = b_t^*$) and the played arm
      ($a = a_t$, $j = b_t$) and summing over the horizon gives
      $\sum_{t>T_0} [\text{(i)}+\text{(iii)}] \le 2L_{f'}T\Delta = 2L_{f'}T^{2/3}$ at $\Delta = T^{-1/3}$.
    ` },
    note: 'Two sources of displacement, each at most \u0394/2: the width of the bin itself, and the ' +
          'Phase-1 estimation error. T\u2080 is calibrated precisely so the second is \u0394/(2L).' },

  { id: 'p7.lemC6', type: 'lemma', tier: 2, concept: 'exploration',
    label: 'Lem C.6', title: 'Sleeping-UCB regret over N bins',
    where: { section: 'C', page: 18 },
    statement: String.raw`\text{For } N \text{ bins with means } \mu_1,\dots,\mu_N, \text{ stochastic
      availability } \mathcal B_t \subseteq [N], \text{ and UCB played over the available set, the
      regret against the best available bin is } O\!\left(\sqrt{NT\log(NT/\delta)}\right).`,
    consumes: ['p7.asm1', 'p7.sample-split'],
    proof: { status: 'full', body: String.raw`
      On the good event the empirical bin means satisfy
      $|\bar y_j(n) - \mu_j| \le s + U_j(n)$ simultaneously for every bin $j \in [N]$ and every pull
      count, where $s = L_{f'}\Delta$ is the deterministic within-bin bias (bounded pathwise by
      Lemma C.5) and $U_j(n) = \sigma\sqrt{2\log(2NT/\delta)/n}$ is the stochastic radius (Lemma C.3).

      The bias $s$ is absorbed into an inflated confidence radius, which restores optimism: the index
      of the best available bin upper-bounds its true mean. The standard UCB argument then applies
      **per round to the available set** $\mathcal B_t$ rather than to all $N$ bins — the step where a
      naive analysis would be invalid, since availability is random and determined by where the $K$
      freshly drawn arms land.

      Because $\hat\theta_0$ is frozen after Phase 1 (Remark 3.1), the bin assignment is
      $\mathcal F_{t-1}$-measurable, so within-bin noise is a martingale difference sequence and the
      deviation bounds hold conditionally on the availability pattern. Summing the per-round
      confidence widths over pulls and applying Cauchy-Schwarz across the $N$ bins gives
      $4\sigma\sqrt{NT\log(2NT/\delta)}$, and the accumulated bias contributes a further $2sT$.
    ` },
    note: 'A standard UCB analysis over all N bins would be INVALID here: only a random subset is ' +
          'available each round, because availability depends on where the K freshly drawn arms ' +
          'happen to land. This is the sleeping-bandit model of Kanade et al. 2009 / Kleinberg ' +
          'et al. 2010, and it is the slot a cooperative subroutine would fill.',
    tags: ['ours'] },

  /* ----------------------------------------------------- open problems -- */
  { id: 'p7.open-mu', type: 'open-problem', tier: 1, concept: 'open',
    label: 'Open: \u03BC*', title: 'Removing the \u03BC* \u2260 0 / Stein dependence',
    where: { section: '6', page: 10 },
    statement: String.raw`\text{Every bound here degrades as } 1/\mu^{*},\ \mu^{*} =
      \mathbb E[f'(X^\top\theta^*)]. \text{ For a link that is symmetric about the context mean,}
      \ \mu^{*}=0 \text{ and the Stein estimator carries no signal at all.}`,
    proof: { status: 'none' },
    note: 'The sharpest limitation of the whole Stein-based line, and the most likely question ' +
          'from an audience.' },

  { id: 'p7.open-multi', type: 'open-problem', tier: 1, concept: 'open',
    label: 'Open: multi-idx', title: 'The multi-index setting',
    where: { section: '6', page: 10 },
    statement: String.raw`\text{Reward } f\!\left(\langle x,\theta_1\rangle,\dots,
      \langle x,\theta_m\rangle\right) \text{ for } m>1 \text{ unknown directions and an unknown }
      m\text{-variate link. Explicitly listed as open.}`,
    proof: { status: 'none' },
    note: 'Named in the roadmap as extension E4 — future-work slide only, not to be attempted.' }

  ],

  /* Intra-paper edges beyond the `consumes` shorthand: the tightness claim. */
  edges: [
    { from: 'p7.thm5-1', to: 'p7.thm4-3', type: 'matches',
      note: 'Upper and lower bound agree up to log factors, so the minimax regret for ' +
            'non-monotone single-index bandits is exactly \u0398\u0303(T^{2/3}). This pairing ' +
            'is the paper\u2019s headline result.' }
  ]
});
