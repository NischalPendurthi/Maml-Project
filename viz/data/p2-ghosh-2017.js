/* Ghosh, Chowdhury & Gopalan — Misspecified Linear Bandits (AAAI 2017, arXiv:1704.06880v1)
 * The negative result that makes "unknown link" a necessity rather than a generalisation.
 */
KM.addPaper('p2', {
  nodes: [

  { id: 'p2.model', type: 'definition', tier: 1, concept: 'model',
    label: 'Misspecified', title: 'The misspecified linear bandit',
    where: { section: '3', page: 2 },
    statement: String.raw`\mu \;=\; X^\top\theta + \epsilon,`,
    proof: { status: 'none' },
    note: 'Features are designed with domain expertise, not with linearity in mind; and even small ' +
          'feature NOISE shifts the reward vector off the linear subspace. So ε ≠ 0 is ' +
          'the normal case, not a pathology.' },

  { id: 'p2.thm1', type: 'theorem', tier: 1, concept: 'lower-bounds',
    label: 'Thm 1', title: 'Impossibility under sparse perturbation',
    where: { section: '4', page: 3 },
    statement: String.raw`\text{Let } \mathcal A \text{ be any algorithm with expected regret }
      \tilde O(d\sqrt T) \text{ on every linear instance of dimension } d \text{ with rewards}
      \text{ bounded by } 1. \text{ Then there exists a sparsely perturbed instance — with}
      \text{ the expected reward of a SINGLE arm perturbed — on which } \mathcal A
      \text{ suffers } \Omega(T) \text{ expected regret.}`,
    consumes: ['p2.model'],
    proof: { status: 'sketch', body: String.raw`
      Start from a perfectly linear instance with $\Theta(\sqrt T)$ arms in dimension $d$. The
      regret hypothesis forces $\mathcal A$ to pull all but $\tilde O(d\sqrt T)$ of its rounds on
      near-optimal arms, so there must exist an arm it samples $o(T/\sqrt T)$ times. Perturb the
      expected reward of exactly that arm upward by a constant. A change-of-measure argument
      (Lemma 1) shows $\mathcal A$'s behaviour is statistically indistinguishable between the two
      instances, so it continues to under-sample the now-optimal arm and incurs constant per-round
      regret, i.e. $\Omega(T)$.` },
    note: 'The sharpest statement in this literature: optimality on linear instances is not merely ' +
          'insufficient under misspecification, it is the very property that FORCES failure. ' +
          'Being optimal is what makes you fragile.',
    tags: ['headline', 'pitch'] },

  { id: 'p2.def1', type: 'definition', tier: 1, concept: 'model',
    label: 'Non-sparse dev.', title: 'Definition 1 — (l, β) non-sparse deviation',
    where: { section: '5', page: 4 },
    statement: String.raw`\mathbb P\!\left(\left|x_{i_{d+1}}^\top\left[X^f_{i_1..i_d}\right]^{-1}
      \left[\mu_{i_1..i_d}\right] - \mu_{i_{d+1}}\right| \ge l\right) \;\ge\; 1-\beta`,
    proof: { status: 'none' },
    note: 'In words: regress any (d+1)-th reward on any d linearly independent features, and the ' +
          'error is bounded away from zero with high probability. This is what makes ' +
          'misspecification DETECTABLE — a single perturbed arm fails the condition, which is ' +
          'exactly why Theorem 1 is unbeatable and this case is not.' },

  { id: 'p2.thm2', type: 'theorem', tier: 1, concept: 'lower-bounds',
    label: 'Thm 2', title: 'OFUL fails under large non-sparse deviation',
    where: { section: '5', page: 4 },
    statement: String.raw`\text{For the linear bandit with } \mathcal A=\{1,2\},\ X=[1\ \ 2],\
      \mu=[\mu_1\ \mu_2]^\top,\ \mu_2>\mu_1,\ \mu_2 \ne 2\mu_1, \text{ and deviation }
      \epsilon=[\epsilon_1\ \epsilon_2]^\top \text{ with } |\epsilon_i|>c>0
      \text{ (so } l=c,\ \beta=0), \text{ there is an instance with }
      \mathbb E(R^{\mathrm{OFUL}}_T) = \Omega(T).`,
    consumes: ['p2.def1'],
    proof: { status: 'full', body: String.raw`
      An explicit two-arm counterexample; the point is that OFUL's confidence ellipsoid is built
      around a LINEAR fit, so a deviation that is consistent across arms is invisible to it.

      Take $\mathcal A=\{1,2\}$ with context matrix $X = [1\ \ 2]$, so arm 2's feature is exactly twice
      arm 1's. Under a perfectly linear model this forces $\mu_2 = 2\mu_1$. Choose the true means with
      $\mu_2 > \mu_1$ but $\mu_2 \ne 2\mu_1$, which is exactly the assertion that the deviation vector
      $\epsilon = [\epsilon_1\ \epsilon_2]^\top$ is non-zero, with $|\epsilon_i| > c > 0$ for both arms
      (so $l = c$, $\beta = 0$ in Definition 1).

      Least squares on observations from both arms returns the $\hat\theta$ minimising
      $\|X^\top\theta - \mu\|_2$, and because BOTH arms are perturbed there is no residual pattern
      that identifies the misspecification: the fit is self-consistent. One can choose $\epsilon$ so
      that the fitted $\hat\theta$ ranks the arms in the WRONG order, i.e.
      $\hat\theta \cdot 1 > \hat\theta \cdot 2$ while $\mu_2 > \mu_1$. OFUL's ellipsoid then shrinks
      around this wrong $\hat\theta$ at the usual rate, and the algorithm commits to arm 1 forever,
      incurring constant per-round regret and hence $\mathbb E(R_T^{\mathrm{OFUL}}) = \Omega(T)$.

      **What this shows.** Non-sparsity does not by itself rescue OFUL. What it does provide is
      DETECTABILITY — with non-sparse deviation a regression on any $d$ arms mispredicts the
      $(d{+}1)$-th by at least $l$, which is the signal RLB's hypothesis test consumes.
    ` },
    note: 'So non-sparsity alone does not rescue OFUL. What it rescues is the possibility of a ' +
          'TEST — which is what RLB exploits.' },

  { id: 'p2.oful-small', type: 'theorem', tier: 2, concept: 'upper-bounds',
    label: 'OFUL small dev.', title: 'OFUL is robust to small deviation',
    where: { section: '4.1', page: 3 },
    statement: String.raw`R^{\mathrm{OFUL}}(T) \;\le\; 8\rho'\sqrt{T d\log\!\left(1+\tfrac{TL^2}{\lambda d}\right)}
      \left[\lambda^{1/2}S + R\sqrt{2\log\tfrac1{\tilde\delta}
      + d\log\!\left(1+\tfrac{TL^2}{\lambda d}\right)}\right],`,
    consumes: ['p2.model'],
    proof: { status: 'none' },
    note: 'ρ′ is a geometric "distortion" constant measuring how far the arms’ true ' +
          'rewards sit from their linear approximation. The bound degrades gracefully — the ' +
          'failure in Theorems 1 and 2 is a cliff, not a slope, and only at LARGE deviation.' },

  { id: 'p2.alg-rlb', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'RLB', title: 'Algorithm 1 — Robust Linear Bandit',
    where: { section: '5.1', page: 5 },
    statement: String.raw`\textbf{1. } \text{Sample } d+1 \text{ arms } k \text{ times each.}\quad
      \textbf{2. } \text{Build a confidence ellipsoid for } \theta^{*} \text{ from } d \text{ of them}
      \text{ and a direct estimate } \hat\mu_{d+1} \text{ for the held-out arm.}
      \\[4pt] \textbf{3. } \text{Test } H_0 \text{ (linear: } \min_\theta\|X^\top\theta-\mu\|_2=0)
      \text{ against } H_1 \text{ ((} l_1,\beta) \text{ non-sparse deviation).}
      \\[4pt] \textbf{4. } \text{Play OFUL if } H_0, \text{ else fall back to UCB.}`,
    consumes: ['p2.def1', 'p2.thm2'],
    proof: { status: 'none' },
    note: 'A hypothesis test bolted in front of a bandit. Elegant, but it treats the link as ' +
          'binary — linear or not — rather than learning it. That limitation is the gap the ' +
          'single-index line fills.' },

  { id: 'p2.rlb-regret', type: 'regret-bound', tier: 1, concept: 'upper-bounds',
    label: 'RLB best-of-both', title: 'RLB regret — best of both worlds',
    where: { section: '5.2', page: 6 },
    statement: String.raw`\begin{array}{lll}
      \textbf{deviation} & \textbf{OFUL} & \textbf{RLB} \\[2pt]
      \text{small} & O(d\sqrt T) & O(d\sqrt T) \\[2pt]
      \text{large \& non-sparse} & \Omega(T) & O(\sqrt{NT})
      \end{array}`,
    consumes: ['p2.alg-rlb', 'p2.oful-small'],
    proof: { status: 'sketch', body: String.raw`
      Two cases, matching the two branches of the algorithm, each controlled by one lemma.

      **Under $H_0$ (the model is linear).** Lemma 3 shows the test statistic concentrates below its
      threshold with probability $1-\delta_1(k,\lambda)$, so RLB selects OFUL. It then inherits OFUL's
      $O(d\sqrt T)$ guarantee, paying only the $\tau = (d{+}1)k$ rounds spent in the sampling phase
      and a $49\delta_1(k,\lambda)N(T-\log T)$ term for the event that the test wrongly fires.

      **Under $H_1$ ($(l_1,\beta)$ non-sparse deviation).** Lemma 4 shows that when the deviation
      satisfies Definition 1, the regression residual on the held-out $(d{+}1)$-th arm exceeds the
      threshold with probability $1-\delta_2(k,\lambda)$, so RLB falls back to UCB and inherits
      $O(\sqrt{NT})$ — sublinear, where OFUL would have been $\Omega(T)$ by Theorem 2.

      **Why non-sparsity is indispensable.** If the deviation were sparse — say
      $\epsilon = (0,\dots,0,c,0,\dots,0)$ with $|c| \gg 0$ — then with $N \gg d$ the sampling phase
      misses the perturbed arm with high probability, the test sees a perfectly linear system,
      and RLB selects OFUL, which by Theorem 1 incurs $\Omega(T)$. Definition 1 is precisely the
      condition that makes the perturbation impossible to miss.

      Choosing $k$ to balance the sampling cost $(d{+}1)k$ against the error probabilities
      $\delta_1,\delta_2$ gives the table.
    ` },
    note: 'Validated on the Yahoo! Learning-to-Rank dataset. The fallback to √(NT) means ' +
          'giving up on the features entirely — rational once they carry no usable signal.' }

  ]
});
