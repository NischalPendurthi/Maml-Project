/* Kang, Liu, Yi, Lyu, Zhang, Zhou & Li — Single Index Bandits (ICLR 2026, arXiv:2506.12751v3)
 * The paper that introduces the problem. Everything in p7 is a response to this.
 */
KM.addPaper('p5', {
  nodes: [

  /* ------------------------------------------------------------- model -- */
  { id: 'p5.problem', type: 'definition', tier: 1, concept: 'model',
    label: 'SIB problem', title: 'The single-index bandit problem',
    where: { section: '2', page: 3 },
    statement: String.raw`\text{At round } t \text{ the learner sees arms } \mathcal X_t,
      \text{ pulls } x_t \text{ and observes}
      \\[4pt] y_t \;=\; f\!\left(x_t^\top\theta^{*}\right) + \eta_t,
      \qquad \textbf{both } f \textbf{ and } \theta^{*} \textbf{ unknown.}
      \\[6pt] \text{Regret is against } \arg\max_a f(x_{t,a}^\top\theta^{*}) \text{ — which for
      non-monotone } f \text{ is NOT the arm of largest projection.}`,
    proof: { status: 'none' },
    note: 'Semiparametric, strictly between the linear bandit (f = identity) and the generalized ' +
          'linear bandit (f known and monotone). The regret target is what makes it hard: with an ' +
          'unknown non-monotone f you cannot rank arms by projection.',
    tags: ['pitch'] },

  { id: 'p5.identifiability', type: 'definition', tier: 2, concept: 'model',
    label: 'Identifiability', title: 'Scale and sign conventions',
    where: { section: '2', page: 3 },
    statement: String.raw`f(\langle x,\theta^{*}\rangle) \text{ is unchanged under }
      \theta^{*}\!\to\! c\theta^{*},\ f(z)\!\to\! f(z/c). \text{ Two conventions fix this:}
      \\[4pt] \textbf{(i) scale: } \|\theta^{*}\|_1 = 1; \qquad
      \textbf{(ii) sign: } \mu^{*} := \mathbb E[f'(X^\top\theta^{*})] > 0 .`,
    proof: { status: 'none' },
    note: 'μ* is not just a normalisation device — it is a SIGNAL-STRENGTH parameter, and how ' +
          'hard an algorithm leans on it is a real point of difference between these papers.' },

  { id: 'p5.asm2-2', type: 'assumption', tier: 1, concept: 'model',
    label: 'A2.2 score', title: 'Assumption 2.2 — score second moment',
    where: { section: '2', page: 4 },
    statement: String.raw`\exists\, M>0:\quad \mathbb E\!\left(S_j(X)^2\right) \le M
      \quad \text{for all } j \in [d].`,
    proof: { status: 'none' },
    note: 'Mild, and notably weaker than the finite FOURTH moment typically required in the ' +
          'Stein-method and robust-estimation literature. Admits many non-sub-Gaussian and even ' +
          'non-zero-mean context distributions.' },

  { id: 'p5.asm2-3', type: 'assumption', tier: 1, concept: 'model',
    label: 'A2.3 bounded', title: 'Assumption 2.3 — bounded contexts and link',
    where: { section: '2', page: 4 },
    statement: String.raw`\|x_{t,i}\|_\infty \le L \text{ for all } i,t, \text{ together with }
      |f(z)| \le L_f \text{ and } |f'(z)| \le L_{f'} .`,
    proof: { status: 'none' },
    note: 'Equivalent in force to the usual ‖x‖₂ ≤ S, ‖θ*‖₂ ' +
          '≤ S pairing: both ensure the inner product is bounded. Stated in ℓ∞ form ' +
          'to match the sparse-linear-bandit literature.' },

  { id: 'p5.monotone', type: 'assumption', tier: 1, concept: 'model',
    label: 'f monotone', title: 'Monotonicity of the link (STOR / ESTOR only)',
    where: { section: '3', page: 5 },
    statement: String.raw`f \text{ is monotonically increasing.}
      \\[4pt] \text{Consequence: } \arg\max_a f(x_{t,a}^\top\theta^{*})
      = \arg\max_a x_{t,a}^\top\theta^{*}, \text{ so } f \text{ need never be estimated.}`,
    proof: { status: 'none' },
    note: 'This single assumption is why STOR and ESTOR can skip link estimation entirely — and ' +
          'exactly why they collapse on non-monotone links. Phase-1 results show ESTOR is worse ' +
          'than LinUCB on the quadratic link and best on the logistic one: the assumption made ' +
          'visible.',
    tags: ['empirical-link', 'pitch'] },

  { id: 'p5.asm3-3', type: 'assumption', tier: 2, concept: 'model',
    label: 'A3.3 density', title: 'Assumption 3.3 — projected-density moment',
    where: { section: '3', page: 7 },
    statement: String.raw`\exists\, C>0:\quad \mathbb E\!\left(p_v(X^\top v)^2\right) \le C
      \quad \text{for all } v \in \mathbb R^d .`,
    consumes: ['p5.asm2-2'],
    proof: { status: 'none' },
    note: 'Needed only by ESTOR, whose epoched greedy selection makes the sampling density change ' +
          'from epoch to epoch; this controls the score moment under the INDUCED distribution.' },

  /* --------------------------------------------------- index estimation -- */
  { id: 'p5.thm3-1', type: 'theorem', tier: 1, concept: 'index-est',
    label: 'Thm 3.1', title: 'Truncated Stein estimator — d/√n rate',
    where: { section: '3', page: 5 },
    statement: String.raw`\text{With } \tau = \sqrt{3(\sigma^2+L_f^2)M\,n/\log(2d/\delta)}
      \text{ and } \lambda=0, \text{ with probability } 1-\delta:
      \\[6pt] \left\|\hat\theta - \mu^{*}\theta^{*}\right\|_2 \;=\; \tilde O\!\left(\sqrt{\tfrac{d}{n}}\right),
      \qquad \left\|\hat\theta - \mu^{*}\theta^{*}\right\|_1 \;=\; \tilde O\!\left(\tfrac{d}{\sqrt n}\right).`,
    consumes: ['p5.asm2-2', 'p5.asm2-3'],
    proof: { status: 'sketch', body: String.raw`
      Stein's identity gives $\mathbb E[y_i S(x_i)] = \mu^*\theta^*$, which motivates the estimator.
      Bound the optimisation gap $\mathcal L(\hat\theta)-\mathcal L(\mu^*\theta^*)$ by controlling
      $\|\nabla\mathcal L(\mu^*\theta^*)\|_\infty$. The heavy tails of $y_iS(x_i)$ — which has only
      a second moment under Assumption 2.2 — are handled by elementwise truncation at $\tau$, after
      which Bernstein's inequality applies coordinatewise and a union bound over $d$ coordinates
      yields the $\log(2d/\delta)$ factor.` },
    note: 'The estimator recovers μ*θ*, NOT θ*. Kang et al. never need the scale ' +
          'because monotonicity means only the direction matters for ranking; Dey et al. do need ' +
          'it, and that is why they normalise.',
    tags: ['pivot'] },

  { id: 'p5.thm3-7', type: 'theorem', tier: 2, concept: 'index-est',
    label: 'Thm 3.7', title: 'Sparse single-index estimation',
    where: { section: '3', page: 7 },
    statement: String.raw`\text{If } \theta^{*} \text{ has } s \text{ nonzero entries, with }
      \lambda = 11\sqrt{M(\sigma^2+L_f^2)\log(2d/\delta)/n} :
      \\[6pt] \left\|\hat\theta-\mu^{*}\theta^{*}\right\|_2 \le \tfrac34\lambda\sqrt s
      = \tilde O\!\left(\sqrt{\tfrac sn}\right), \qquad
      \left\|\hat\theta-\mu^{*}\theta^{*}\right\|_1 \le 3\lambda s = \tilde O\!\left(\tfrac{s}{\sqrt n}\right).`,
    consumes: ['p5.thm3-1'],
    proof: { status: 'sketch', body: String.raw`
      The same truncated estimator, with the unregularised loss of Eqn. (1) replaced by its
      $\ell_1$-regularised counterpart at
      $\lambda = 11\sqrt{M(\sigma^2+L_f^2)\log(2d/\delta)/n}$.

      Stein's identity still gives $\mathbb E[y_iS(x_i)] = \mu^*\theta^*$, so the population minimiser
      is unchanged and $\mu^*\theta^*$ inherits the $s$-sparsity of $\theta^*$. Truncation at $\tau$
      controls the heavy tails, after which a coordinatewise Bernstein bound gives
      $\|\nabla\mathcal L(\mu^*\theta^*)\|_\infty \le \lambda/2$ with probability $1-\delta$ — which is
      precisely the standard Lasso condition that $\lambda$ dominate the noise level.

      On that event the usual basic inequality plus a cone/restricted-eigenvalue argument gives
      $\|\hat\theta-\mu^*\theta^*\|_2 \le \tfrac34\lambda\sqrt s$ and
      $\|\hat\theta-\mu^*\theta^*\|_1 \le 3\lambda s$. Ambient $d$ survives only inside
      $\log(2d/\delta)$, so the rate is $\tilde O(\sqrt{s/n})$ and $\tilde O(s/\sqrt n)$.

      Note $\lambda$ does not depend on $s$, which is why the algorithm never needs to know the
      sparsity index.
    ` },
    note: 'Same truncated estimator with an ℓ₁-regularised loss. Ambient d is replaced by ' +
          'the sparsity index s throughout — and crucially WITHOUT the algorithm needing to know s.' },

  /* -------------------------------------------- algorithms & exploration -- */
  { id: 'p5.alg-stor', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'STOR', title: "Algorithm 1 — Stein's Oracle Single Index Bandit",
    where: { section: '3', page: 5 },
    statement: String.raw`\text{Explore-then-commit. For } t \le T_1 \text{ pull uniformly at random;}
      \text{ form } \hat\theta \text{ by Eqn. (1); then for } t>T_1 \text{ play greedily}
      \\[4pt] x_t \;=\; \arg\max_{x \in \mathcal X_t} x^\top\hat\theta .`,
    consumes: ['p5.thm3-1', 'p5.monotone'],
    proof: { status: 'none' },
    note: 'Monotonicity is what licenses the greedy rule: maximising the projection maximises the ' +
          'reward. Drop it and this algorithm is simply wrong, not merely suboptimal.' },

  { id: 'p5.alg-estor', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'ESTOR', title: "Algorithm 2 — Epoched Stein's Oracle SIB",
    where: { section: '3', page: 6 },
    statement: String.raw`\text{Epochs } e_i = (2^i-1)T_0. \text{ In epoch } i, \text{ re-estimate }
      \hat\theta_i \text{ from epoch } i{-}1 \text{ data using the score of the INDUCED density}
      \\[4pt] p_i(x) \;=\; K\cdot p(x)\cdot F_i\!\left(x^\top\hat\theta_i\right)^{K-1},`,
    consumes: ['p5.thm3-1', 'p5.monotone', 'p5.asm3-3'],
    proof: { status: 'none' },
    note: 'The technical move: greedy selection distorts the sampling distribution away from p, so ' +
          'the score function used for the next Stein estimate must be the score of the induced ' +
          'density p_i, not of p. Tracking that distortion is what buys √T over T^{2/3}.' },

  { id: 'p5.alg-gstor', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'GSTOR', title: "Algorithm 3 — General Stein's Oracle SIB",
    where: { section: '3', page: 9 },
    statement: String.raw`\text{Two independent exploration phases: } T_1 \text{ samples to estimate }
      \theta^{*} \text{ via Eqn. (1), then } T_1 \text{ FRESH samples to estimate } f \text{ by}
      \text{ kernel smoothing with bandwidth } h = T_1^{1/3}. \text{ Then act greedily on }
      \hat f(x^\top\hat\theta).`,
    consumes: ['p5.thm3-1', 'p5.asm2-3'],
    proof: { status: 'none' },
    note: 'Drops monotonicity — the first algorithm to do so. The double-exploration split is the ' +
          'ancestor of ZoomSIB-UCB’s sample splitting, but GSTOR commits after exploring ' +
          'whereas ZoomSIB keeps running UCB, which is where the T^{3/4} → T^{2/3} gain comes from.' },

  /* ------------------------------------------------------ upper bounds -- */
  { id: 'p5.thm3-2', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 3.2', title: 'STOR regret — Õ(d²ᐟ³T²ᐟ³)',
    where: { section: '3', page: 5 },
    statement: String.raw`\text{With } T_1 = (dT)^{2/3}\ln^{1/3}(2d/\delta),\ \tau=\sqrt{3T_1/\ln(2d/\delta)},
      \lambda=0, \text{ with probability } 1-\delta:
      \\[6pt] R_T \;=\; O\!\left(d^{2/3}T^{2/3}\left(\ln(d/\delta)\right)^{1/3}\right)
      \;=\; \tilde O\!\left(d^{2/3}T^{2/3}\right).`,
    consumes: ['p5.alg-stor', 'p5.thm3-1'],
    proof: { status: 'sketch', body: String.raw`
      The exploration phase costs $O(L_f T_1)$ outright. After it, per-round regret is controlled by
      $\|\hat\theta-\mu^*\theta^*\|$ through the monotonicity of $f$: an error of $\varepsilon$ in
      the estimated direction can misrank two arms only when their projections differ by less than
      $O(\varepsilon)$. Balancing $T_1$ against $T\cdot\tilde O(d/\sqrt{T_1})$ gives
      $T_1 \asymp (dT)^{2/3}$ and the stated rate.` } },

  { id: 'p5.thm3-5', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 3.5', title: 'ESTOR regret — Õ(dK³ᐟ²√T), near-optimal',
    where: { section: '3', page: 6 },
    statement: String.raw`\text{With } \lambda=0,\ \tau_i = \sqrt{3(e_{i-1}-e_{i-2})/\log(2d\log_2 T/\delta)}
      \text{ and } T_0 \le d\sqrt{K^3T\log(2d\log_2 T/\delta)} :
      \\[6pt] R_T \;=\; O\!\left(dK^{3/2}\sqrt{C\,T\log(d\log_2 T/\delta)}\right)
      \;=\; \tilde O_T\!\left(\sqrt T\right).`,
    consumes: ['p5.alg-estor', 'p5.thm3-1', 'p5.asm3-3'],
    proof: { status: 'sketch', body: String.raw`
      Characterise the arm-sampling distribution induced by greedy selection within an epoch; it is
      $p_i(x) = K p(x)F_i(x^\top\hat\theta_i)^{K-1}$, the density of the argmax of $K$ draws. Apply
      Stein's identity under THAT density to bound the estimation error of $\hat\theta_i$ from the
      previous epoch's samples, using a moment analysis of the score under the induced law
      (Assumption 3.3). Per-round regret within an epoch is bounded by the estimation error of
      $\hat\theta_i$; because epoch lengths grow geometrically, those errors decay geometrically
      across epochs. Summing the geometric series gives $\tilde O(dK^{3/2}\sqrt T)$.` },
    note: 'The K^{3/2} is a worst-case artefact of a conservative bound; the paper notes it ' +
          'improves under common designs, e.g. Gaussian arms.' },

  { id: 'p5.cor3-8', type: 'corollary', tier: 2, concept: 'upper-bounds',
    label: 'Cor 3.8', title: 'Sparse regret — d replaced by s',
    where: { section: '3', page: 8 },
    statement: String.raw`\text{For a sparse SIB with an increasing link, STOR attains }
      R_T = \tilde O(s^{2/3}T^{2/3}) \text{ and ESTOR attains the } \tilde O_T(\sqrt T)
      \text{ rate, both with ambient } d \text{ replaced by the sparsity index } s,
      \text{ and WITHOUT the algorithm knowing } s .`,
    consumes: ['p5.thm3-7', 'p5.thm3-2', 'p5.thm3-5'],
    proof: { status: 'sketch', body: String.raw`
      Immediate from Theorem 3.7 by substitution. Both STOR and stage-wise ESTOR only ever consume
      the estimator through its error bound, so replacing Theorem 3.1's $\tilde O(d/\sqrt n)$ with
      Theorem 3.7's $\tilde O(s/\sqrt n)$ propagates $d \to s$ through the identical balancing
      computation.

      For STOR: re-balance $T_1$ against $T\cdot\tilde O(s/\sqrt{T_1})$ to get
      $T_1 = (sT)^{2/3}\log^{1/3}(2d/\delta)$ and $R_T = \tilde O(s^{2/3}T^{2/3})$. For ESTOR the
      per-epoch errors again decay geometrically, giving the $\tilde O_T(\sqrt T)$ rate with $s$ in
      place of $d$.

      Neither algorithm changes structurally — only line 4 of Algorithm 1 and line 5 of Algorithm 2,
      where the unregularised solve becomes an $\ell_1$-regularised one. Computational and memory
      efficiency are preserved, and $s$ need not be known.
    ` },
    note: 'Both algorithms inherit this by swapping in the ℓ₁-regularised estimator at one ' +
          'line — no change to the exploration schedule, no loss of computational efficiency.' },

  { id: 'p5.thm3-9', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 3.9', title: 'GSTOR regret — O(d³ᐟ⁸T³ᐟ⁴), general links',
    where: { section: '3', page: 9 },
    statement: String.raw`\text{Under a Gaussian design with } T_1 = d^{3/8}T^{3/4},\
      \tau = \sqrt{3T_1/\log(2d/\delta)},\ W = 2\sqrt{\log T_1},\ h = T_1^{1/3},\ \lambda = 0,
      \text{ and } d^{15} = O(T^{3/2}):
      \\[6pt] \mathbb E(R_T) \;=\; O\!\left(d^{3/8}T^{3/4}\right).`,
    consumes: ['p5.alg-gstor', 'p5.thm3-1'],
    proof: { status: 'sketch', body: String.raw`
      GSTOR is explore-then-commit with TWO independent exploration phases, and the two-phase split
      is what makes the analysis go through.

      **Phase A ($T_1$ samples).** Estimate $\theta^*$ by the truncated Stein estimator, giving
      $\|\hat\theta-\mu^*\theta^*\| = \tilde O(\sqrt{d/T_1})$ by Theorem 3.1.

      **Phase B ($T_1$ FRESH samples).** Estimate $f$ by kernel smoothing of $y$ against the projected
      index $x^\top\hat\theta$, with bandwidth $h = T_1^{1/3}$ and window $W = 2\sqrt{\log T_1}$.
      Independence from Phase A matters: the projection direction must not depend on the data used to
      smooth along it, or the smoothing errors are no longer conditionally mean-zero.

      **Prediction error.** Combining a standard kernel-smoothing bias-variance decomposition with a
      perturbation argument that transfers the error in $\hat\theta$ into a horizontal displacement of
      the regression design yields $\tilde O(\sqrt d\,T_1^{-1/3})$ under the Gaussian design.

      **Balancing.** Committing greedily on $\hat f(x^\top\hat\theta)$ for the remaining
      $T - 2T_1$ rounds costs $T \cdot \tilde O(\sqrt d\,T_1^{-1/3})$, and exploration costs
      $O(L_f T_1)$. Setting $T_1 = d^{3/8}T^{3/4}$ balances them at
      $\mathbb E(R_T) = O(d^{3/8}T^{3/4})$, under the technical condition $d^{15} = O(T^{3/2})$.

      **Where the looseness is.** The $T^{1/3}$ kernel rate is not the bottleneck; COMMITTING is. By
      keeping a UCB running over the discretised index instead of committing, Dey et al. reach
      $T^{2/3}$, which Theorem 5.1 shows is optimal.
    ` },
    note: 'The first sublinear bound for general non-monotone links — and the number Dey, Bhore & ' +
          'Ghosh improve to T^{2/3}. Note the d-dependence here (d^{3/8}) is far BETTER than ' +
          'ZoomSIB-UCB’s d²; the trade is dimension against horizon.',
    tags: ['superseded', 'pitch'] },

  /* ----------------------------------------------------- open problems -- */
  { id: 'p5.conj-sqrtT', type: 'open-problem', tier: 1, concept: 'open',
    label: 'Is √T possible?', title: 'Conjecture — √T is unattainable for general links',
    where: { section: '3', page: 9 },
    statement: String.raw`\text{Kang et al. conjecture that } \tilde O(\sqrt T) \text{ is}
      \textit{ fundamentally unattainable} \text{ for general reward functions without further}
      \text{ structure, reasoning that even Lipschitz bandits without contexts exceed } \sqrt T .`,
    consumes: ['p5.thm3-9'],
    proof: { status: 'none' },
    note: 'RESOLVED by Dey, Bhore & Ghosh: the conjecture is correct in direction — √T is ' +
          'indeed unattainable — but the true rate is Θ̃(T^{2/3}), not the T^{3/4} they ' +
          'achieved. A good example of a conjecture being right about the obstruction and wrong ' +
          'about the constant.',
    tags: ['resolved', 'pitch'] }

  ]
});
