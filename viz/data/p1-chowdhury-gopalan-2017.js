/* Chowdhury & Gopalan — On Kernelized Multi-armed Bandits (ICML 2017, arXiv:1704.00445v2)
 * The confidence-set technology every kernel-bandit paper downstream builds on.
 */
KM.addPaper('p1', {
  nodes: [

  { id: 'p1.rkhs-model', type: 'definition', tier: 1, concept: 'model',
    label: 'RKHS reward', title: 'Reward lies in a known RKHS',
    where: { section: '2', page: 2 },
    statement: String.raw`y_t = f(x_t) + \varepsilon_t \text{ over a continuous arm set }
      D \subset \mathbb R^d, \text{ where } f \in \mathcal H_k(D) \text{ with }
      \|f\|_k \le B \text{ for a KNOWN kernel } k, \text{ and } \varepsilon_t \text{ is }
      \text{conditionally } R\text{-sub-Gaussian.}`,
    proof: { status: 'none' },
    note: 'Nonparametric but not assumption-free: the KERNEL is known, which is the RKHS analogue ' +
          'of knowing the link. That is precisely the assumption the single-index line removes.' },

  { id: 'p1.info-gain', type: 'definition', tier: 1, concept: 'link-learn',
    label: 'γ_T', title: 'Maximum information gain',
    where: { section: '2', page: 3 },
    statement: String.raw`\gamma_T \;=\; \max_{A \subset D,\,|A|=T}\ \tfrac12
      \ln\det\!\left(I + \lambda^{-1}K_A\right),`,
    proof: { status: 'none' },
    note: 'The complexity measure that replaces dimension d in every kernel-bandit bound. Linear ' +
          'kernel: γ_T = O(d ln T). RBF: O((ln T)^{d+1}). It is how "effective dimension" is ' +
          'expressed when the feature space is infinite.' },

  { id: 'p1.thm1', type: 'theorem', tier: 1, concept: 'concentration',
    label: 'Thm 1', title: 'Self-normalised bound for infinite-dimensional martingales',
    where: { section: '3', page: 4 },
    statement: String.raw`\text{For predictable } \{x_t\} \text{ and conditionally } R
      \text{-sub-Gaussian } \{\varepsilon_t\}, \text{ with probability } \ge 1-\delta,
      \text{ simultaneously for all } t \ge 0:
      \\[6pt] \left\|\varepsilon_{1:t}\right\|^2_{\left((K_t+\eta I)^{-1}+I\right)^{-1}}
      \;\le\; 2R^2 \ln\frac{\sqrt{\det\left((1+\eta)I + K_t\right)}}{\delta}.`,
    consumes: ['p1.rkhs-model'],
    proof: { status: 'full', body: String.raw`
      A method-of-mixtures argument, lifted from $\mathbb R^d$ to an arbitrary, possibly
      infinite-dimensional feature space.

      **Step 1 — a supermartingale.** For a fixed direction $g$ in the RKHS, the exponential process
      $M_t^{g} = \exp\big(\langle g, S_t\rangle/R - \|g\|_{V_t}^2/2\big)$, with
      $S_t = \sum_{s\le t}\varepsilon_s\phi(x_s)$, is a supermartingale: conditional
      $R$-sub-Gaussianity of $\varepsilon_t$ given $\mathcal F_{t-1}$ bounds
      $\mathbb E[e^{\lambda\varepsilon_t}\mid\mathcal F_{t-1}] \le e^{\lambda^2R^2/2}$, and predictability
      of $x_t$ makes $\phi(x_t)$ known at time $t-1$.

      **Step 2 — mix over $g$.** Rather than union-bounding over a net of directions, which is what
      costs a $\sqrt{d\log T}$ factor and is unavailable when the dimension is infinite, integrate
      $M_t^g$ against a Gaussian prior on $g$. The integral of a supermartingale is a supermartingale,
      and the Gaussian integral evaluates in closed form to
      $\bar M_t = \det(I+V_t)^{-1/2}\exp\big(\|S_t\|^2_{V_t^{-1}}/2R^2\big)$.

      **Step 3 — Ville's inequality.** $\mathbb E[\bar M_t] \le 1$, so
      $\mathbb P(\exists t:\ \bar M_t > 1/\delta) \le \delta$. Rearranging the closed form gives the
      stated bound, and because Ville's inequality is a statement about the whole trajectory the
      result holds SIMULTANEOUSLY for all $t$ — which is what makes it usable inside a bandit loop.

      **Step 4 — back to the Gram matrix.** Lemma 1 identifies $\|S_t\|_{V_t^{-1}}$ with
      $\|\varepsilon_{1:t}\|_{(K_t^{-1}+I)^{-1}}$ and $\det(I+V_t)$ with
      $\det(I+K_t)$, both computable from the $t\times t$ kernel matrix. The regulariser $\eta$
      handles the case where $K_t$ is singular; when $K_t \succ 0$ almost surely one may take $\eta=0$.
    ` },
    note: 'THE technical contribution. Extends Abbasi-Yadkori et al.’s finite-dimensional ' +
          'self-normalised bound to arbitrary, possibly infinite, dimension — which is what makes ' +
          'a frequentist RKHS confidence set possible at all.',
    tags: ['tool', 'headline'] },

  { id: 'p1.lem1', type: 'lemma', tier: 2, concept: 'concentration',
    label: 'Lem 1', title: 'Feature-space view of the self-normalised process',
    where: { section: '3', page: 4 },
    statement: String.raw`\text{With } S_t = \sum_{s\le t}\varepsilon_s\phi(x_s) \text{ and }
      V_t = I + \sum_{s\le t}\phi(x_s)\phi(x_s)^\top, \text{ whenever } K_t \succ 0:
      \\[4pt] \left\|\varepsilon_{1:t}\right\|_{(K_t^{-1}+I)^{-1}} \;=\; \|S_t\|_{V_t^{-1}} .`,
    consumes: ['p1.thm1'],
    proof: { status: 'sketch', body: String.raw`
      A direct computation in the feature space: substitute $\Phi_t$ for the stacked feature map,
      use $K_t = \Phi_t\Phi_t^\top$ and the push-through identity
      $\Phi_t^\top(\Phi_t\Phi_t^\top + I)^{-1} = (\Phi_t^\top\Phi_t + I)^{-1}\Phi_t^\top$ to move
      between the $t\times t$ Gram form and the (possibly infinite-dimensional) covariance form.` },
    note: 'The reason the bound is computable: everything is expressed through the t×t Gram ' +
          'matrix rather than an infinite-dimensional covariance.' },

  { id: 'p1.thm2', type: 'theorem', tier: 1, concept: 'concentration',
    label: 'Thm 2', title: 'Uniform RKHS confidence band',
    where: { section: '3', page: 5 },
    statement: String.raw`\text{With probability } \ge 1-\delta, \text{ for ALL } x \in D
      \text{ and all } t \ge 1:
      \\[6pt] \left|\mu_{t-1}(x) - f(x)\right| \;\le\;
      \left(B + R\sqrt{2\!\left(\gamma_{t-1}+1+\ln(1/\delta)\right)}\right)\sigma_{t-1}(x),`,
    consumes: ['p1.thm1', 'p1.info-gain', 'p1.rkhs-model'],
    proof: { status: 'full', body: String.raw`
      Write the kernel ridge predictor as $\mu_{t-1}(x) = k_{t-1}(x)^\top(K_{t-1}+\lambda I)^{-1}y_{1:t-1}$
      and split the error at the noiseless predictor:
      $$\mu_{t-1}(x) - f(x) \;=\; \underbrace{\big[\mu_{t-1}(x) - \bar\mu_{t-1}(x)\big]}_{\text{noise}} \;+\; \underbrace{\big[\bar\mu_{t-1}(x) - f(x)\big]}_{\text{bias}},$$
      where $\bar\mu$ is the same predictor applied to the noiseless observations $f(x_s)$.

      **Bias.** By the reproducing property and Cauchy-Schwarz in the RKHS, the regularisation bias is
      at most $\|f\|_k\,\sigma_{t-1}(x) \le B\,\sigma_{t-1}(x)$.

      **Noise.** The noise term is $\langle \phi(x), V_{t-1}^{-1}S_{t-1}\rangle$, so by Cauchy-Schwarz
      in the $V_{t-1}^{-1}$ norm it is at most $\|S_{t-1}\|_{V_{t-1}^{-1}}\sigma_{t-1}(x)$. Theorem 1
      bounds that first factor by $R\sqrt{2(\gamma_{t-1}+1+\ln(1/\delta))}$, using
      $\tfrac12\ln\det(I+K_{t-1}) \le \gamma_{t-1}$ by definition of the maximum information gain.

      Adding the two and noting that Theorem 1 holds simultaneously over all $t$ AND that the
      Cauchy-Schwarz step is valid for every $x$ at once gives a band uniform in both — the
      improvement over Maillard (2016), which fixes $x$ in advance. Take $\lambda = 1+\eta$ with
      $\eta = 2/T$.
    ` },
    note: 'Simultaneous over all x — an improvement on Maillard (2016), which bounds a single ' +
          'fixed x. This uniformity is exactly what Dubey & Pentland instantiate per agent.',
    tags: ['tool'] },

  { id: 'p1.alg-igpucb', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'IGP-UCB', title: 'Algorithm 1 — Improved GP-UCB',
    where: { section: '4', page: 5 },
    statement: String.raw`x_t \;=\; \arg\max_{x \in D}\ \mu_{t-1}(x) + \beta_t\,\sigma_{t-1}(x),
      \qquad \beta_t = B + R\sqrt{2(\gamma_{t-1}+1+\ln(1/\delta))} .`,
    consumes: ['p1.thm2'],
    proof: { status: 'none' },
    note: 'Used in Fed-ZoomSIB as the "no structure exploited" control: it learns a full ' +
          'd-dimensional function without using the single-index structure, so its regret should ' +
          'visibly degrade as d grows. Confirmed in Phase-1 results.',
    tags: ['baseline'] },

  { id: 'p1.alg-gpts', type: 'algorithm', tier: 2, concept: 'exploration',
    label: 'GP-TS', title: 'Algorithm 2 — GP Thompson Sampling',
    where: { section: '4', page: 6 },
    statement: String.raw`\text{Sample } f_t(x) \sim N\!\left(\mu_{t-1}(x),\,\beta_t^2\sigma^2_{t-1}(x)\right)
      \text{ on a discretisation } D_t, \text{ then play } x_t = \arg\max_{x\in D_t} f_t(x) .`,
    consumes: ['p1.thm2'],
    proof: { status: 'none' } },

  { id: 'p1.thm3', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 3', title: 'IGP-UCB regret',
    where: { section: '4.1', page: 6 },
    statement: String.raw`R_T \;=\; O\!\left(B\sqrt{T\gamma_T} \;+\;
      \sqrt{T\gamma_T\left(\gamma_T + \ln(1/\delta)\right)}\right) .`,
    consumes: ['p1.alg-igpucb', 'p1.thm2'],
    proof: { status: 'full', body: String.raw`
      The standard optimism argument, with Theorem 2 supplying the confidence width.

      **Optimism.** On the event of Theorem 2, $f(x) \le \mu_{t-1}(x)+\beta_t\sigma_{t-1}(x)$ for all
      $x$, so the IGP-UCB index of the optimal arm upper-bounds $f(x^*)$. Since the algorithm
      maximises that index, the instantaneous regret is bounded by twice the confidence width at the
      played point: $r_t = f(x^*)-f(x_t) \le 2\beta_t\sigma_{t-1}(x_t)$.

      **Summing.** Cauchy-Schwarz gives $R_T \le \sqrt{T\sum_t r_t^2} \le 2\beta_T\sqrt{T\sum_t \sigma^2_{t-1}(x_t)}$.
      The elliptical-potential argument (Lemma 4) bounds
      $\sum_{t\le T}\sigma^2_{t-1}(x_t) \le \tfrac{2}{\ln(1+\lambda^{-1})}\gamma_T$, which is where the
      information gain enters: it caps how much total posterior variance any sequence of $T$ points
      can have.

      Substituting $\beta_T = B + R\sqrt{2(\gamma_T+1+\ln(1/\delta))}$ gives
      $O\big(B\sqrt{T\gamma_T} + \sqrt{T\gamma_T(\gamma_T+\ln(1/\delta))}\big)$.

      **Why this beats GP-UCB.** Srinivas et al. union-bound over a discretisation of $D$ that refines
      with $t$, paying an extra $\sqrt{\log(|D_t|)}$; Theorem 2's band is already uniform over $D$, so
      that step disappears. With a linear kernel $\gamma_T = O(d\ln T)$ and the bound recovers the
      optimal $\tilde O(d\sqrt T)$ for linear bandits.
    ` },
    note: 'Tighter than Srinivas et al.’s GP-UCB by removing an explicit union bound over a ' +
          'discretisation. With a linear kernel γ_T = O(d ln T) and this recovers the ' +
          'optimal Õ(d√T) for linear bandits.' },

  { id: 'p1.thm4', type: 'theorem', tier: 2, concept: 'upper-bounds',
    label: 'Thm 4', title: 'GP-TS regret — first frequentist TS bound in RKHS',
    where: { section: '4.2', page: 7 },
    statement: String.raw`R_T \;=\; O\!\left(\left(\gamma_T+\ln(2/\delta)\right)
      \sqrt{d\ln(BdT)}\sqrt{T\gamma_T} \;+\; B\sqrt{T\ln(2/\delta)}\right) .`,
    consumes: ['p1.alg-gpts', 'p1.thm2'],
    proof: { status: 'sketch', body: String.raw`
      Thompson sampling has no optimism to lean on, so the argument runs through SATURATED points —
      those whose confidence width is already smaller than their gap to the optimum.

      On the event of Theorem 2, at every round the sampled function $f_t$ is, with probability
      bounded below by a constant, at least as large at some unsaturated point as $f(x^*)$ — this is
      Gaussian anti-concentration (Lemma 7). Hence TS plays an unsaturated point a constant fraction
      of the time, and at unsaturated points instantaneous regret is controlled by the confidence
      width, exactly as in the UCB case. A supermartingale argument (Lemmas 11-13) converts the
      "constant fraction of rounds" statement into a high-probability bound on the sum, and the
      elliptical potential lemma closes it as in Theorem 3.

      The extra $\sqrt{d\ln(BdT)}$ comes from the discretisation $D_t$ needed to make the
      anti-concentration step uniform over a continuous domain; each $f_t$ is a fresh random draw, so
      the Theorem 2 band cannot be reused to make that step discretisation-free. Removing it is
      stated as open.
    ` },
    note: 'A √(d ln(BdT)) factor worse than IGP-UCB, entirely a consequence of the ' +
          'discretisation step. Removing it — making the analysis discretisation-free — is stated ' +
          'as open.' },

  { id: 'p1.open-disc', type: 'open-problem', tier: 2, concept: 'open',
    label: 'Open: discret.', title: 'Discretisation-free analysis of GP-TS',
    where: { section: '4.2', page: 7 },
    statement: String.raw`\text{Whether the extra } \sqrt{d\ln(BdT)} \text{ in the GP-TS bound can}
      \text{ be removed, i.e. whether the analysis can avoid discretising } D, \text{ is open.}`,
    consumes: ['p1.thm4'],
    proof: { status: 'none' } }

  ]
});
