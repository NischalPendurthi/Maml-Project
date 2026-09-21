/* Dubey & Pentland — Kernel Methods for Cooperative Multi-Agent Contextual Bandits
 * (ICML 2020, arXiv:2008.06220v1).  The closest existing work to Fed-ZoomSIB.
 */
KM.addPaper('p3', {
  nodes: [

  { id: 'p3.model', type: 'definition', tier: 1, concept: 'model',
    label: 'Coop. model', title: 'Cooperative multi-agent kernel bandit with delays',
    where: { section: '1', page: 1 },
    statement: String.raw`V \text{ agents on an undirected graph } G=(V,E). \text{ Each round, agent }
      v \text{ sees } \mathcal D_{v,t}, \text{ plays } x_{v,t} \text{ and observes }
      y_{v,t}=f(x_{v,t})+\varepsilon_{v,t}.
      \\[4pt] \text{Messages from } v \text{ reach } v' \text{ after } d(v,v')-1 \text{ rounds.}
      \\[6pt] R_G(T) = \sum_{v\in V}\sum_{t=1}^{T}\left[f(x^{*}_{v,t}) - f(x_{v,t})\right].`,
    proof: { status: 'none' },
    note: 'The delay is the whole technical difficulty: it creates heterogeneity in what each ' +
          'agent knows, even when the underlying problem is shared.' },

  { id: 'p3.def2', type: 'definition', tier: 1, concept: 'communication',
    label: 'Υ_z heterog.', title: 'Definition 2 — agent heterogeneity',
    where: { section: '3.2', page: 5 },
    statement: String.raw`\text{With } K_z = \left(K_z(z_v,z_{v'})\right)_{v,v'\in V}
      \text{ the matrix of pairwise agent interactions,} \qquad \Upsilon_z \;=\;
      \mathrm{rank}(K_z).`,
    proof: { status: 'none' },
    note: 'Υ_z = 1 means fully cooperative (all agents share one problem); Υ_z = V means ' +
          'no two agents help each other. In Fed-ZoomSIB’s core setting θ* and f are ' +
          'SHARED, i.e. Υ_z = 1 — the most favourable case. Extension E3 (clustered indices) ' +
          'is exactly the move to 1 < Υ_z < V.',
    tags: ['ours'] },

  { id: 'p3.clique', type: 'definition', tier: 1, concept: 'communication',
    label: 'χ̄(G_γ)', title: 'Clique cover of the γ-power graph',
    where: { section: '3.1', page: 4 },
    statement: String.raw`\bar\chi(G_\gamma) \;=\; \text{the minimum clique covering number of }
      G_\gamma, \text{ the } \gamma\text{-th power of the communication graph.}`,
    proof: { status: 'none' },
    note: 'Best case γ-complete: χ̄ = 1 (e.g. a γ/2-star). Worst case a line ' +
          'graph: χ̄ = ⌈V/γ⌉, at which point the bound equals V agents ' +
          'learning in isolation — cooperation buys nothing.' },

  { id: 'p3.lem1', type: 'lemma', tier: 1, concept: 'concentration',
    label: 'Lem 1', title: 'Per-agent RKHS confidence set (instantiated)',
    where: { section: '3', page: 4 },
    statement: String.raw`\text{For } \tilde{\mathcal X}\subset\mathbb R^d \text{ and } F
      \text{ in the RKHS with kernel } K, \text{ the Chowdhury–Gopalan band holds for each}
      \text{ agent’s local posterior, giving } \left|\mu_{v,t-1}(\tilde x) - F(\tilde x)\right|
      \le \beta_{v,t}\,\sigma_{v,t-1}(\tilde x).`,
    consumes: ['p3.model'],
    proof: { status: 'none' },
    note: 'Cited directly as Chowdhury & Gopalan (2017) Theorem 2 — this paper does not reprove it.' },

  { id: 'p3.lem2', type: 'lemma', tier: 2, concept: 'concentration',
    label: 'Lem 3', title: 'Per-clique variance bound',
    where: { section: 'A', page: 13 },
    statement: String.raw`\text{For a clique } C \text{ in } G_\gamma \text{ with Gram matrix }
      K_{C,T} \text{ formed from all actions of all agents in } C \text{ up to } T,
      \text{ the summed predictive variances within } C \text{ are controlled by }
      \hat\gamma_T \text{ of the pooled action set.}`,
    consumes: ['p3.lem1', 'p3.clique'],
    proof: { status: 'sketch', body: String.raw`
      The step that turns "agents within a clique hear each other within $\gamma$ rounds" into a
      single pooled information-gain term.

      Fix a clique $C$ of $G_\gamma$. Every pair of agents in $C$ is within distance $\gamma$, so each
      agent's observation reaches every other member with delay at most $\gamma-1$. Up to that
      bounded staleness, all members of $C$ therefore hold the SAME Gram matrix, namely $K_{C,T}$
      formed from $(\tilde x_{v,t})_{v\in C,\,t\in[T]}$.

      A Schur-complement argument (Theorem 4) bounds each member's individual posterior variance by
      the variance of the pooled clique predictor, inflated by a factor accounting for the at most
      $\gamma$ missing observations. Applying the elliptical-potential lemma to $K_{C,T}$ then bounds
      $\sum_{v\in C}\sum_t \sigma^2_{v,t-1}$ by $\hat\gamma_T$ of the pooled action set rather than by
      $|C|$ separate single-agent terms.

      Summing over a minimal clique cover $\mathcal C$ and applying Cauchy-Schwarz across the
      $\bar\chi(G_\gamma)$ cliques produces the $\sqrt{\bar\chi(G_\gamma)}$ factor: cooperation is
      perfect inside a clique and absent between cliques, so the number of cliques needed to cover
      the graph is exactly the price of delay.
    ` },
    note: 'The step that converts "agents in a clique see each other within γ rounds" into a ' +
          'single pooled information-gain term. This is where the √(χ̄) factor ' +
          'actually enters.' },

  { id: 'p3.alg-coop', type: 'algorithm', tier: 1, concept: 'exploration',
    label: 'Coop-KernelUCB', title: 'Algorithm 1 — Coop-KernelUCB',
    where: { section: '3', page: 4 },
    statement: String.raw`\text{Each agent runs KernelUCB on the AUGMENTED context }
      \tilde x_{v,t}=(z_v, x_{v,t}) \text{ with the product kernel } K = K_z \otimes K_x,
      \text{ incorporating delayed neighbour observations with a per-clique reweighting.}`,
    consumes: ['p3.lem1', 'p3.def2'],
    proof: { status: 'none' },
    note: 'The product kernel is the trick: agent similarity and action similarity multiply, so a ' +
          'neighbour’s observation is automatically discounted by how different that ' +
          'neighbour’s problem is.' },

  { id: 'p3.thm1', type: 'theorem', tier: 1, concept: 'upper-bounds',
    label: 'Thm 1', title: 'Group regret under delayed communication',
    where: { section: '3.1', page: 4 },
    statement: String.raw`\text{With } \mathcal C \text{ a minimal clique covering of } G_\gamma
      \text{ and continuum-armed } \mathcal D_{v,t}, \text{ Coop-KernelUCB incurs per-agent}
      \text{ average regret carrying an extra factor } O\!\left(\sqrt{\bar\chi(G_\gamma)}\right)
      \text{ relative to the single-agent bound.}`,
    consumes: ['p3.alg-coop', 'p3.lem2', 'p3.clique'],
    proof: { status: 'sketch', body: String.raw`
      Optimism plus the clique decomposition.

      Each agent runs KernelUCB on the augmented context $\tilde x_{v,t}=(z_v,x_{v,t})$, so Lemma 1
      (Chowdhury-Gopalan Theorem 2, instantiated per agent) gives
      $|\mu_{v,t-1}(\tilde x)-F(\tilde x)| \le \beta_{v,t}\sigma_{v,t-1}(\tilde x)$ uniformly. Optimism
      then bounds each agent's instantaneous regret by $2\beta_{v,t}\sigma_{v,t-1}(\tilde x_{v,t})$,
      exactly as in the single-agent case.

      Summing over agents and rounds and applying Cauchy-Schwarz gives
      $R_G(T) \le 2\beta_T\sqrt{VT\sum_{v,t}\sigma^2_{v,t-1}}$. The sum of posterior variances is
      where the multi-agent structure enters, and Lemma 3 bounds it per clique. Summing over a
      minimal clique cover of $G_\gamma$ contributes the extra $\sqrt{\bar\chi(G_\gamma)}$ relative to
      the single-agent bound.

      **Reading the two extremes.** If $G$ is $\gamma$-complete then $G_\gamma$ is complete,
      $\bar\chi = 1$, and the bound is as if all $V$ agents shared one learner — a $\gamma/2$-star
      achieves this. If $G$ is a line graph then $\bar\chi = \lceil V/\gamma\rceil$ and the bound
      degenerates to $V$ agents learning in isolation. The clique cover number is therefore the exact
      measure of how much the topology lets cooperation pay.
    ` },
    tags: ['headline'] },

  { id: 'p3.cor1', type: 'corollary', tier: 1, concept: 'upper-bounds',
    label: 'Cor 1', title: 'Per-agent regret under the product kernel',
    where: { section: '3.2', page: 5 },
    statement: String.raw`\text{When } K = K_z\otimes K_x, \text{ with probability } \ge 1-\delta,
      \\[6pt] \bar R(T) \;=\; O\!\left(\sqrt{\Upsilon_z\cdot\hat\Upsilon_{VT}\cdot
      \bar\chi(G_\gamma)\cdot\frac TV\cdot\log\!\left(\frac{V\lambda}{\delta}\right)}\right).`,
    consumes: ['p3.thm1', 'p3.def2'],
    proof: { status: 'sketch', body: String.raw`
      Specialise Theorem 1 to the product kernel $K = K_z \otimes K_x$.

      For a product kernel the information gain factorises: Lemma 4 shows
      $\hat\gamma_T \le 2\Upsilon_z(\Upsilon_x + \log T)$ where $\Upsilon_z = \mathrm{rank}(K_z)$.
      That is the formal content of "agent similarity multiplies action complexity" — a neighbour's
      observation is automatically discounted by how different that neighbour's problem is, with no
      explicit reweighting.

      Substituting into Theorem 1 and dividing by $V$ for the per-agent average gives
      $$\bar R(T) = O\Big(\sqrt{\Upsilon_z\cdot\hat\Upsilon_{VT}\cdot\bar\chi(G_\gamma)\cdot\tfrac TV\cdot\log(V\lambda/\delta)}\Big).$$

      **Reading the three factors.** $T/V$ is the cooperative speedup; $\bar\chi(G_\gamma)$ is the
      price of communication delay; $\Upsilon_z$ is the price of heterogeneity. Communication acts as
      a MASK on an underlying gain that is set by how similar the agents' problems actually are:
      if the network contexts are identical then $\Upsilon_z = 1$ and topology alone determines the
      regret; if $K_z$ is full rank then $\Upsilon_z = V$ and cooperation buys nothing regardless of
      topology. For an RBF network kernel $\Upsilon_z = O(d\ln V)$.
    ` },
    note: 'Read the structure: T/V is the cooperative speedup, χ̄(G_γ) is the price ' +
          'of delay, Υ_z is the price of heterogeneity. Communication acts as a MASK on an ' +
          'underlying gain set by agent similarity.',
    tags: ['pitch'] },

  { id: 'p3.mmd', type: 'proposition', tier: 2, concept: 'communication',
    label: 'MMD embedding', title: 'Estimating network contexts by kernel mean embedding',
    where: { section: '3.3', page: 5 },
    statement: String.raw`\hat K_{z,t}(P_v,P_{v'}) \;=\; \exp\!\left(-\mathrm{MMD}_{\mathcal H}
      \!\left(\hat\Psi_t(P_v),\hat\Psi_t(P_{v'})\right)\big/2\sigma_z^2\right),
      \qquad \hat\Psi_t(P_v) = \tfrac1t\sum_{i\le t}K_x(\cdot,x_{v,i}).`,
    consumes: ['p3.def2'],
    proof: { status: 'none' },
    note: 'Removes the need to know agent similarity a priori — it is estimated from the contexts ' +
          'each agent actually sees. Relevant to extension E3, where cluster membership is unknown.' },

  { id: 'p3.thm2', type: 'theorem', tier: 2, concept: 'upper-bounds',
    label: 'Thm 2', title: 'Dist-KernelUCB — independent-set partition',
    where: { section: '4', page: 6 },
    statement: String.raw`\text{Partitioning } V \text{ into "central" agents (a maximal weighted
      independent set of } G_\gamma) \text{ and peripheral agents assigned to them,}
      \text{ Dist-KernelUCB attains a per-agent average regret of the same form with a}
      \text{ reduced communication requirement.}`,
    consumes: ['p3.thm1'],
    proof: { status: 'sketch', body: String.raw`
      Same optimism skeleton as Theorem 1, with the clique cover replaced by an independent-set
      partition chosen to cut communication.

      Set the "central" agents $\mathcal V_C$ to be a maximum weighted independent set of $G_\gamma$,
      weighting each $v$ by $|\mathcal N_\gamma(v)|$, and assign every peripheral agent to a central
      neighbour (breaking ties by degree). Each central agent aggregates only its own assigned group
      rather than a full clique, so messages flow along a star rather than all-to-all.

      Lemma 6 bounds a centre's posterior variance over its $\gamma$-neighbourhood, and because the
      centres form an independent set their neighbourhoods overlap in a controlled way, so summing
      over groups does not double-count. The independence number $\alpha(G_\gamma)$ takes the role
      $\bar\chi(G_\gamma)$ played in Theorem 1, giving a per-agent average regret of the same form at
      substantially lower communication.
    ` } },

  { id: 'p3.limit-linear', type: 'open-problem', tier: 1, concept: 'open',
    label: 'Gap: link fixed', title: 'Limitation — reward is linear in the RKHS image',
    where: { section: '2', page: 2 },
    statement: String.raw`\text{Coop-KernelUCB assumes the reward is a linear function of the}
      \text{ contexts’ images in a KNOWN RKHS — i.e. the link is effectively fixed. It}
      \text{ neither estimates nor exploits single-index structure.}`,
    consumes: ['p3.model'],
    proof: { status: 'none' },
    note: 'This is how Fed-ZoomSIB positions its novelty: Dubey & Pentland supply the cooperative ' +
          'machinery but assume away the unknown link; Dey et al. remove the link assumption but ' +
          'are single-agent. Nobody occupies both cells.',
    tags: ['gap', 'pitch', 'ours'] }

  ]
});
