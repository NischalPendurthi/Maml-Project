/* Arya, Bhattacharjee & Sriperumbudur — Kernel Single-Index Bandits (arXiv:2603.18938v1)
 * The inference-first branch of the single-index line. 82 pages; tier 3 is its appendix.
 */
KM.addPaper('p6', {
  nodes: [

  { id: 'p6.model', type: 'definition', tier: 1, concept: 'model',
    label: 'Per-arm SIM', title: 'Per-arm single-index reward model',
    where: { section: '2', page: 4 },
    statement: String.raw`\mathbb E\!\left[r \mid X, a=i\right] \;=\; f_i\!\left(X^\top\beta_i\right),
      \qquad i \in \{1,\dots,L\},
      \\[4pt] \text{each arm carrying its OWN index } \beta_i \text{ and its own unknown}
      \text{ nonparametric link } f_i. \text{ Regret against }
      a^{*}_t = \arg\max_i f_i(X_t^\top\beta_i).`,
    proof: { status: 'none' },
    note: 'This is the formulation the project\u2019s original proposal wrote down. Arms are ' +
          'STABLE decision options (treatment levels, dosages, motion primitives), so arm-specific ' +
          'heterogeneity arises through distinct low-dimensional mechanisms.',
    tags: ['pitch'] },

  { id: 'p6.m1', type: 'assumption', tier: 1, concept: 'model',
    label: 'M1 covariates', title: 'Assumption (M1) — covariate distribution and known score',
    where: { section: '2', page: 4 },
    statement: String.raw`X_t \in \mathbb R^d \text{ i.i.d. from } p \in C^1(\mathbb R^d),\ p>0
      \text{ on } \mathrm{supp}(P_X), \text{ with score } S(x) = -\nabla_x\log p(x)
      \textbf{ assumed known.}`,
    proof: { status: 'none' },
    note: 'Same known-score assumption as the rest of the line. The paper explicitly flags plug-in ' +
          'score estimators as future work — so this limitation is shared, not particular.' },

  { id: 'p6.m3', type: 'assumption', tier: 1, concept: 'model',
    label: 'M3 RKHS', title: 'Assumption (M3) — RKHS model class',
    where: { section: '2', page: 4 },
    statement: String.raw`\text{Each } f_i \in \mathcal H_K \text{ for a bounded continuous positive}
      \text{ definite } K:\mathcal U\times\mathcal U\to\mathbb R \text{ with }
      \sup_{x}K(x,x)\le\kappa, \text{ where } \mathcal U\subset\mathbb R \text{ is compact and}
      \text{ contains the range of } U_t = X_t^\top\beta_i .`,
    proof: { status: 'none' },
    note: 'Note the RKHS is over the ONE-DIMENSIONAL index, not over R^d. That is what dodges the ' +
          'curse of dimensionality that afflicts IGP-UCB.' },

  { id: 'p6.prop1', type: 'proposition', tier: 1, concept: 'index-est',
    label: 'Prop 1', title: 'First-order non-Gaussian Stein identity',
    where: { section: '4', page: 8 },
    statement: String.raw`\text{For } X \text{ with differentiable density } p \text{ and score }
      S(x)=-\nabla_x\log p(x), \text{ and suitably regular } g:
      \\[4pt] \mathbb E\!\left[g(X)S(X)^\top\right] \;=\; \mathbb E\!\left[\nabla g(X)\right]^\top .`,
    consumes: ['p6.m1'],
    proof: { status: 'sketch', body: String.raw`
      Integration by parts, exactly as in the Gaussian case, but carried out against a general
      differentiable density rather than the Gaussian one; the Gaussian score $S(x)=x$ is the
      special case. Regularity conditions ensure the boundary term vanishes.` },
    note: 'The general form (Yang et al. 2017) of the identity that Kang et al. and Dey et al. use ' +
          'in the single-index special case.' },

  { id: 'p6.a1-predict', type: 'assumption', tier: 2, concept: 'model',
    label: 'A1 predictab.', title: 'Assumption (A1) — stationary second moment',
    where: { section: '4', page: 9 },
    statement: String.raw`\text{The inverse-propensity-weighted Gram structure } \hat\Gamma_{i,t}
      \text{ is predictable and has a stable limit } \Gamma, \text{ with the uniform exploration}
      \text{ coefficient } r_t = t^{-2}\sum_{s\le t} 1/p^{\star}_s,\
      p^{\star}_s = \inf_{w,i} p_{s,i}(w).`,
    proof: { status: 'none' },
    note: 'r_t is the quantity that governs everything: it measures how badly inverse-propensity ' +
          'weighting inflates variance when the policy stops exploring. It sets the optimal ' +
          '\u03B5-greedy schedule.' },

  { id: 'p6.alg-ksiege', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'K-SIEGE', title: 'Algorithm 1 — Kernelized Single-Index \u03B5-Greedy Exploration',
    where: { section: '3', page: 6 },
    statement: String.raw`\textbf{Warm start: } \text{pull each arm at least once.}
      \\[4pt] \text{At each } t: \text{ compute } A_t = \arg\max_i \hat f_{i,t-1}
      \!\left(X_t^\top\hat\beta^{(t-1)}_i\right); \text{ play } A_t \text{ w.p. } 1-\epsilon_t,
      \text{ else a uniform other arm.}
      \\[4pt] \text{Update ONLY the pulled arm: } \hat\beta_i \text{ by Stein estimation,}
      \ \hat f_i \text{ by IPW kernel ridge regression on } X_t^\top\hat\beta_{i,t}.`,
    consumes: ['p6.model', 'p6.prop1', 'p6.m3'],
    proof: { status: 'none' },
    note: '\u03B5-greedy rather than UCB, precisely BECAUSE the propensities must stay known and ' +
          'bounded below for the IPW weights and the inference to be valid. Optimism would make ' +
          'the propensity intractable.' },

  { id: 'p6.thm1', type: 'theorem', tier: 1, concept: 'concentration',
    label: 'Thm 1', title: 'Asymptotic normality of the index estimator',
    where: { section: '4', page: 12 },
    statement: String.raw`\text{Under Assumptions 1\u20133, } \ t^{\alpha}\left(\hat\beta_{i,t}
      - \beta_i\right) \;\longrightarrow\; N\!\left(0, V_{\beta,i}^{-1}\right),
      \text{ yielding valid confidence regions for } \beta_i \text{ under ADAPTIVE sampling.}`,
    consumes: ['p6.alg-ksiege', 'p6.a1-predict', 'p6.prop1'],
    proof: { status: 'sketch', body: String.raw`
      The difficulty is entirely that the data is ADAPTIVELY collected: the design depends on the
      policy, which depends on past data, so the classical M-estimation argument does not apply.

      **Decomposition.** Write the Stein estimating equation in inverse-propensity-weighted form,
      $\hat\Gamma_{i,t}\hat\beta_{i,t} = \hat m_{i,t}$, with weights $1/p_{s,i}$ restoring an
      unbiased population target. Expand around the truth to isolate a principal stochastic term plus
      a remainder: $t^\alpha(\hat\beta_{i,t}-\beta_i) = \Gamma^{-1}\,t^\alpha S_{t,i} + r_t$.

      **The principal term.** $S_{t,i}$ is a martingale array with respect to the bandit filtration:
      the IPW weights are $\mathcal F_{s-1}$-measurable because $\varepsilon$-greedy propensities are
      known before acting — which is exactly why the algorithm uses $\varepsilon$-greedy rather than
      UCB. Proposition 5 controls its second moment and Proposition 6 verifies the Lindeberg
      condition, so a martingale CLT gives $V_{\beta,t}S_{t,i} \to N(0,I_d)$.

      **The remainder.** High-probability concentration for the inverse-weighted Gram matrix
      (Theorem 8, Corollary 5) gives $t^\alpha\|\hat\Gamma_{i,t}-\Gamma\| \to 0$ provided the
      exploration schedule keeps $r_t = t^{-2}\sum_{s\le t}1/p^\star_s$ small enough — this is
      Assumption (A1), and it is the quantitative statement of "do not stop exploring too fast."
      Sub-Gaussian tails on the weighted scores (A3) supply the moment bounds.

      Slutsky then gives $t^\alpha(\hat\beta_{i,t}-\beta_i) \to N(0, V_{\beta,i}^{-1})$.
    ` },
    note: 'Genuinely hard: the sampling distribution depends endogenously on the policy, ' +
          'observations are dependent across time, and IPW inflates variance. Proved via ' +
          'high-probability concentration for inverse-weighted Gram matrices plus a martingale CLT.',
    tags: ['headline'] },

  { id: 'p6.cor1', type: 'corollary', tier: 2, concept: 'concentration',
    label: 'Cor 1', title: 'Feasible studentization',
    where: { section: '4', page: 13 },
    statement: String.raw`\hat V_{\beta,t,i}\, t^{\alpha}\left(\hat\beta_{i,t}-\beta_i\right)
      \longrightarrow N(0,I_d), \text{ with } \hat V \text{ computable from the data —}
      \text{ so the confidence region is usable in practice, not only in principle.}`,
    consumes: ['p6.thm1'],
    proof: { status: 'sketch', body: String.raw`
      Theorem 1's limit involves the unknown $V_{\beta,i}$, so it certifies nothing computable on its
      own. Theorem 2 shows the plug-in $\hat V_{\beta,t,i}$, built from the same IPW empirical
      moments, is consistent provided $t^{2\alpha}r_t \to 0$ and $\Gamma$ is invertible.

      Slutsky's theorem then converts the limit into
      $\hat V_{\beta,t,i}\,t^\alpha(\hat\beta_{i,t}-\beta_i) \to N(0,I_d)$, which is pivotal and
      therefore yields confidence regions computable from the data alone — the difference between an
      asymptotic curiosity and something usable in an experiment.
    ` } },

  { id: 'p6.thm3', type: 'theorem', tier: 1, concept: 'concentration',
    label: 'Thm 3', title: 'Studentized vector martingale CLT in the RKHS',
    where: { section: '5.1', page: 16 },
    statement: String.raw`\text{Under (C1)\u2013(C3) and } \gamma\in(0,\tfrac12), \text{ the}
      \text{ studentized RKHS estimator satisfies a DIRECTIONAL functional central limit theorem}
      \text{ in } \mathcal H_K, \text{ giving asymptotically valid POINTWISE confidence intervals}
      \text{ for the link } f_i .`,
    consumes: ['p6.alg-ksiege', 'p6.m3', 'p6.a1-predict'],
    proof: { status: 'sketch', body: String.raw`
      The link estimator lives in an infinite-dimensional RKHS, where a full functional CLT would
      require tightness that does not hold under adaptive sampling. The resolution is to go
      DIRECTIONAL: fix $g \in \mathcal H_K$ and prove a CLT for the scalar $\langle g, \hat f_{i,t}-f_i\rangle$.

      Decompose $t^\gamma L_{t,i} = \sum_{s\le t}\xi_{t,s,i}$ into a martingale difference array
      (Lemma 15), isolating the principal stochastic part from the ridge bias. Assumptions (C1)-(C3)
      supply the conditional-variance convergence and the Lindeberg condition for that array, giving a
      studentized scalar limit; Corollary 2 states it for fixed $g$.

      The bias is handled separately by Proposition 2 under the Hölder source condition (D1) — the
      classical inverse-problem smoothness assumption — which makes the directional bias vanish
      faster than the stochastic term for $\gamma \in (0,1/2)$, provided $\lambda_t$ is chosen in the
      admissible window of Remark 6. Taking $g = K(\cdot,x)$ and applying the reproducing property
      turns the directional statement into a POINTWISE one, giving confidence intervals for
      $f_i(x)$ (Corollary 3).
    ` },
    note: 'Directional because a full functional CLT in an infinite-dimensional RKHS would need ' +
          'tightness that does not hold here; projecting onto a fixed direction g recovers a ' +
          'usable scalar limit.',
    tags: ['headline'] },

  { id: 'p6.prop4', type: 'proposition', tier: 2, concept: 'upper-bounds',
    label: 'Prop 4', title: 'Regret decomposition',
    where: { section: '6', page: 18 },
    statement: String.raw`R_T(\pi) \text{ splits into (i) forced-exploration cost } \sum_t\epsilon_t,
      \text{ (ii) index-estimation error, and (iii) nonparametric link-estimation error.}`,
    consumes: ['p6.alg-ksiege'],
    proof: { status: 'sketch', body: String.raw`
      Add and subtract the estimated reward of the played arm and of the optimal arm. Conditioning on
      whether round $t$ was an exploration or an exploitation step splits the regret three ways:

      1. **Forced exploration.** With probability $\epsilon_t$ the algorithm plays a uniformly random
         non-greedy arm, costing at most a constant, so this contributes $\sum_t \epsilon_t$.
      2. **Index-estimation error.** On exploitation rounds, choosing the wrong arm requires
         $\hat f_{i}(X^\top\hat\beta_i)$ to misrank, which the Lipschitz constant $L_K$ converts into
         an error of order $\|\hat\beta_{i,t}-\beta_i\|$ times $\|X_t\|$.
      3. **Link-estimation error.** The remaining term is $\|\hat f_{i,t}-f_i\|_\infty$, controlled by
         the IPW-KRR rate.

      Term 3 dominates: since $\gamma_i\alpha/(2\gamma_i\alpha+\alpha+1) \le 1/2$ for
      $0 < \gamma_i \le 1/2$ and $\alpha > 1$, the nonparametric rate is always slower than the
      parametric $\sqrt{}$-rate of term 2. So the overall rate is set by RKHS smoothness, NOT by $d$.
    ` },
    note: 'The decomposition shows term (iii) DOMINATES: the nonparametric regression error is ' +
          'larger than the index estimation error, so the rate is set by RKHS smoothness, not by d.' },

  { id: 'p6.thm5', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 5', title: 'High-probability regret — T\u2074\u141F\u2075 worst case',
    where: { section: '6', page: 19 },
    statement: String.raw`\text{With } \epsilon_t = t^{-\beta} \text{ and } w =
      \frac{(\min_i\gamma_i)\alpha}{2(\min_i\gamma_i)\alpha+\alpha+1}:
      \\[6pt] R_T \;\lesssim\; T^{(\beta-1)w+1} + T^{1-\beta/p},
      \qquad \beta^{*} = \frac{w}{w+1},
      \\[4pt] \text{giving } R_T = O(T^{4/5}) \text{ in the worst case and }
      R_T \lesssim T^{2/3} \text{ for a finite-dimensional RKHS.}`,
    consumes: ['p6.prop4', 'p6.thm1', 'p6.m3'],
    proof: { status: 'sketch', body: String.raw`
      Substitute the three rates of Proposition 4 and optimise the exploration schedule.

      With $\epsilon_t = t^{-\beta}$: forced exploration costs $\sum_t \epsilon_t \asymp T^{1-\beta}$.
      The IPW-KRR error is governed by $r_t = t^{-2}\sum_{s\le t}\epsilon_s^{-1} \lesssim t^{\beta-1}$,
      and the standard kernel-ridge rate under source condition $\gamma_i$ and capacity $\alpha$
      converts that into a per-round error of order $r_t^{w}$ with
      $w = (\min_i\gamma_i)\alpha/(2(\min_i\gamma_i)\alpha+\alpha+1)$, contributing
      $T^{(\beta-1)w+1}$.

      Balancing $T^{(\beta-1)w+1}$ against $T^{1-\beta/p}$ at $p=1$ gives the optimal
      $\beta^* = w/(w+1)$. Since $w \le 1/2$, the worst case is $w \to 0$ giving $T^{4/5}$, while a
      finite-dimensional RKHS ($\alpha \to 1$, $\gamma_i \to 1/2$) gives $w \to 1/2$ and $T^{2/3}$.

      Crucially the regression runs on the ONE-DIMENSIONAL projection $X_t^\top\beta_i$, so the
      nonparametric rate carries no $d$ in its exponent — this is what separates K-SIEGE from running
      a kernel method on the full $d$-dimensional context, as IGP-UCB does.
    ` },
    note: 'Governed by the smoothness parameters \u03B3_i and the RKHS complexity \u03B1. Crucially ' +
          'the regression runs on the ONE-DIMENSIONAL projection, avoiding the curse of ' +
          'dimensionality — which is why d does not appear in the exponent.' },

  { id: 'p6.thm6', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 6', title: 'Common Lipschitz link — O_P(\u221AT)',
    where: { section: '6', page: 19 },
    statement: String.raw`\text{Suppose all arms share one link } f_a \equiv f, \text{ Lipschitz with }
      |f'| \le C_f, \text{ contexts sub-Gaussian and } \|\beta_a-\beta_{a'}\| \le C_\beta.
      \\[6pt] \text{If } \epsilon_t = O(t^{-1/2}) \text{ then } R_T(\pi) = O_P\!\left(\sqrt T\right),
      \text{ matching the minimax-optimal PARAMETRIC rate.}`,
    consumes: ['p6.thm5', 'p6.model'],
    proof: { status: 'sketch', body: String.raw`
      When all arms share one Lipschitz link $f$, the nonparametric term disappears from the
      COMPARISON between arms, and the problem becomes effectively parametric.

      The regret at round $t$ is $f(X_t^\top\beta_{a^*}) - f(X_t^\top\beta_{a_t})$. Lipschitzness with
      $|f'| \le C_f$ bounds this by $C_f|X_t^\top\beta_{a^*} - X_t^\top\beta_{a_t}|$ — note that $f$
      itself has cancelled. Misranking therefore requires the estimated indices to be misordered,
      which by Cauchy-Schwarz requires
      $\|X_t\|\,(\|\hat\beta_{a^*}-\beta_{a^*}\| + \|\hat\beta_{a_t}-\beta_{a_t}\|)$ to exceed the
      index gap. With sub-Gaussian covariates, $\|X_t\|_2 \lesssim \sigma\sqrt{d}+\sqrt{\log(1/\delta)}$
      with high probability.

      Theorem 1 gives $\|\hat\beta_{i,t}-\beta_i\| = O_P(\sqrt{r_t \vee t^{-1/2}})$. Summing over
      rounds and adding the forced-exploration cost $E_T = \sum_t \epsilon_t/(L-1)$ gives the stated
      bound. Choosing $\epsilon_t = O(t^{-1/2})$ balances $\sum_t\sqrt{r_t} \asymp \sqrt T$ against
      $E_T \asymp \sqrt T$, yielding $R_T(\pi) = O_P(\sqrt T)$.

      **Read the hypothesis carefully.** This does NOT contradict the $\tilde\Theta(T^{2/3})$ minimax
      bound for single-index bandits: there the link is unknown, non-monotone and must be resolved
      along the index line, whereas here the shared $f$ cancels and only the finite-dimensional
      $\beta_a$ must be learned. Different function classes.
    ` },
    note: 'The \u221AT headline — but read the hypothesis: a COMMON link across arms, so the only ' +
          'thing that differs between arms is the finite-dimensional \u03B2_a. That collapses the ' +
          'problem to a parametric one, which is why \u221AT is attainable.',
    tags: ['headline', 'pitch'] },

  { id: 'p6.open-score', type: 'open-problem', tier: 2, concept: 'open',
    label: 'Open: score', title: 'Plug-in score estimators',
    where: { section: '2', page: 4 },
    statement: String.raw`\text{When } p \text{ is unknown the score must be estimated. The effect}
      \text{ of a plug-in } \hat S \text{ on both the regret and the inference guarantees is}
      \text{ left to future work.}`,
    consumes: ['p6.m1'],
    proof: { status: 'none' },
    note: 'Shared with every paper in this line — the single most consequential open question for ' +
          'practical deployment of Stein-based bandits.' }

  ]
});
