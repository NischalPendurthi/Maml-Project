/* Fed-ZoomSIB — this project.  CS6007, IIT Bombay.
 *
 * These are TARGETS, not established facts. Every node here is a conjecture, an
 * open problem, or a claim we intend to prove or measure — and the `proof.status`
 * of each says so honestly. Source: docs/01-literature-and-problem.md §4.
 */
KM.addPaper('p8', {
  nodes: [

  { id: 'p8.setting', type: 'definition', tier: 1, concept: 'model',
    label: 'Fed setting', title: 'The federated single-index bandit',
    where: { section: '4.1', page: null },
    statement: String.raw`N \text{ agents on a connected undirected } G \text{ with communication}
      \text{ matrix } P \text{ (Amani–Thrampoulidis A1). Each round } t:
      \\[4pt] \text{(i) agent } i \text{ sees } \mathcal X_{i,t}=\{x_{i,t,a}\}_{a\in[K]}
      \text{ i.i.d. from a known } p;
      \\[2pt] \text{(ii) pulls } x_{i,t}, \text{ observes } y_{i,t}=f(\langle x_{i,t},\theta^{*}\rangle)+\eta_{i,t};
      \\[2pt] \text{(iii) every } C \text{ rounds, exchanges} \le B \text{ values with neighbours.}
      \\[6pt] \textbf{Network regret: } R_T(N)=\sum_{t=1}^{T}\sum_{i=1}^{N}
      \left[f(\langle x^{*}_{i,t},\theta^{*}\rangle) - f(\langle x_{i,t},\theta^{*}\rangle)\right].`,
    proof: { status: 'none' },
    note: 'f and θ* are UNKNOWN and SHARED across agents. Assumptions A1–A3 of Dey et al. ' +
          'carry over verbatim per agent. Dropping the shared-θ* assumption is extension E3.',
    tags: ['ours', 'pitch'] },

  { id: 'p8.score-known', type: 'assumption', tier: 1, concept: 'model',
    label: 'Score known', title: 'Inherited assumption — the score function is known',
    where: { section: '4.4', page: null },
    statement: String.raw`\text{Stein’s identity requires } S(x)=-\nabla\log p(x)
      \text{ to be available to the learner. Contexts are Gaussian throughout our experiments,}
      \text{ so } S \text{ is available in closed form.}`,
    proof: { status: 'none' },
    note: 'STATE THIS IN THE PITCH rather than hiding it — the roadmap flags it as the most likely ' +
          'audience question. It is inherited from the whole SIB literature, not a weakness we ' +
          'introduced, and it is reasonable when p is estimated offline from logged data.',
    tags: ['ours', 'risk', 'pitch'] },

  /* ------------------------------------------- the two federation claims -- */
  { id: 'p8.lem-fed-stein', type: 'conjecture', tier: 1, concept: 'index-est',
    label: 'Fed Stein', title: 'Target Lemma — Phase 1 federates EXACTLY',
    where: { section: '4.2', page: null },
    statement: String.raw`\text{The Stein estimator is a sample mean, so averaging local estimators}
      \text{ is ALGEBRAICALLY IDENTICAL to the centralized estimator on pooled data:}
      \\[6pt] \frac1N\sum_{i=1}^{N}\hat\theta_i \;=\; \hat\theta^{\text{pooled}}
      \quad\text{exactly — no approximation, no consensus iteration.}
      \\[6pt] \text{Hence } \varepsilon \asymp C_\theta d\sqrt{\tfrac{\log(2d/\delta)}{N T_0}},
      \text{ and to meet } \varepsilon \le \Delta/(2L) \text{ with } \Delta=T^{-1/3}:
      \\[4pt] T_0 \;=\; \tilde O\!\left(\frac{d^2T^{2/3}}{N}\right)
      \quad\text{vs.}\quad \tilde O\!\left(d^2T^{2/3}\right) \text{ for a lone agent.}`,
    consumes: ['p8.setting'],
    proof: { status: 'sketch', body: String.raw`
      **This is a proof strategy for a target, not a proof of an established result.**

      The claim rests on one algebraic fact. The truncated Stein estimator is a plain sample mean,
      $\hat\theta = \frac1n\sum_i \varphi_\tau(y_i S(x_i))$, and a mean of means over equal-sized local
      samples is the mean over the pooled sample:
      $$\frac1N\sum_{i=1}^{N}\hat\theta_i \;=\; \frac{1}{N}\sum_{i=1}^N \frac{1}{T_0}\sum_{t\le T_0}\varphi_\tau(y_{i,t}S(x_{i,t})) \;=\; \frac{1}{NT_0}\sum_{i,t}\varphi_\tau(y_{i,t}S(x_{i,t})) \;=\; \hat\theta^{\text{pooled}}.$$
      This is an identity, not an approximation — no consensus iteration, no error term. It holds
      because truncation is applied ELEMENTWISE BEFORE averaging, so each agent's summand is already
      the same bounded random variable the centralized estimator would form.

      Given that, Lemma B.1 of Dey et al. applies verbatim to the pooled sample of size $NT_0$,
      giving $\varepsilon \asymp C_\theta d\sqrt{\log(2d/\delta)/(NT_0)}$, and Lemma 2.1's
      normalisation step is unchanged. Imposing the same calibration $\varepsilon \le \Delta/(2L)$ at
      $\Delta = T^{-1/3}$ and solving for $T_0$ gives $T_0 = \tilde O(d^2T^{2/3}/N)$.

      **What still has to be checked.** (a) Agents must draw contexts from the SAME density $p$, or
      the pooled sample is not i.i.d. and Stein's identity no longer yields a common $\mu^*\theta^*$ —
      this is what extension E3 relaxes, and where negative transfer would appear. (b) The high-
      probability event is now over $NT_0$ samples, so the union bound and the truncation threshold
      $\tau$ must be restated at the pooled sample size. (c) Sample splitting (Remark 3.1) must be
      preserved: $\hat\theta_0$ must still be frozen before any agent enters Phase 2, or bin
      assignment stops being predictable and the Phase-2 martingale argument breaks network-wide.
    ` },
    note: 'THE headline claim. Phase-1 NETWORK cost is N·T₀ = Õ(d²T^{2/3}) — ' +
          'INDEPENDENT of N — against N·Õ(d²T^{2/3}) for N independent learners. ' +
          'A factor-N saving bought with exactly ONE round of communication of d numbers per agent. ' +
          'Very few bandit primitives federate this cleanly.',
    tags: ['ours', 'headline', 'pitch'] },

  { id: 'p8.coop-sleeping', type: 'conjecture', tier: 1, concept: 'communication',
    label: 'Coop sleeping', title: 'Target Lemma — Phase 2 as a cooperative sleeping bandit',
    where: { section: '4.2', page: null },
    statement: String.raw`\text{The per-bin sufficient statistics are just } (n_j,S_j) \text{ — two}
      \text{ scalars per bin over } O(T^{1/3}) \text{ bins. Sharing them is a standard cooperative}
      \text{ MAB over a graph. Invoking the } \sqrt N \text{-speedup results inside Prop 4.7:}
      \\[6pt] \mathrm{Reg}_{\mathcal A}(N_{\text{bins}},T) \;=\;
      \tilde O\!\left(\sqrt{N_{\text{bins}}\cdot N\cdot T}\right)
      \;=\; \tilde O\!\left(\sqrt N\, T^{2/3}\right),`,
    consumes: ['p8.setting', 'p8.lem-fed-stein'],
    proof: { status: 'sketch', body: String.raw`
      **Proof strategy, resting entirely on Prop 4.7 of Dey et al.**

      That proposition says Phase 2 is a black box: any algorithm $\mathcal A$ for $N_{\text{bins}}$
      arms under stochastic availability, with a regret guarantee against the best AVAILABLE arm,
      can be substituted and the overall bound follows as
      $R_T \le R_T^{(1)} + \mathrm{Reg}_{\mathcal A}(N_{\text{bins}},T) + 2L_{f'}T\Delta$.

      So the task reduces to supplying a COOPERATIVE sleeping bandit and quoting its regret. The
      per-bin state is two scalars $(n_j, S_j)$, so sharing is cheap, and the standard distributed-MAB
      results (Landgren et al. 2016; Martinez-Rubio et al. 2019) give a $\sqrt N$ speedup over $N$
      independent learners. Substituting $N_{\text{bins}} = O(T^{1/3})$:
      $$\mathrm{Reg}_{\mathcal A} = \tilde O\big(\sqrt{N_{\text{bins}}\cdot N\cdot T}\big) = \tilde O\big(\sqrt N\,T^{2/3}\big).$$

      **What still has to be checked, and why this one is harder than Phase 1.** The pooling here is
      STATISTICAL, not exact: an agent cannot reconstruct the centralized bin statistics from one
      message, so delayed or rare communication genuinely degrades the bound rather than merely
      postponing it. Concretely: (a) the existing $\sqrt N$-speedup results assume a COMMON arm set,
      whereas here availability $\mathcal B_{i,t}$ is agent-specific and random, so the sleeping
      structure and the cooperation structure interact; (b) shared bin counts arriving with delay
      break the martingale property that Remark 3.1 secures in the single-agent case, so the
      confidence radius must absorb a staleness term in the manner of Amani & Thrampoulidis' Lemma 2;
      (c) the spectral gap $1-|\lambda_2|$ should enter additively, as it does for DLUCB, but that has
      to be shown rather than assumed.

      This is why the honest position is that Phase 1 is provable and Phase 2 may end up supported
      empirically — and why extension E1 (the communication sweep) is the safety net.
    ` },
    note: 'Against N·T^{2/3} for independent learners — a factor √N saving. Note the ' +
          'pooling here is STATISTICAL, not exact: unlike Phase 1, agents cannot reconstruct the ' +
          'centralized state from one message.',
    tags: ['ours', 'pitch'] },

  { id: 'p8.conj1', type: 'conjecture', tier: 1, concept: 'upper-bounds',
    label: 'Main conjecture', title: 'Conjectured main theorem',
    where: { section: '4.2', page: null },
    statement: String.raw`\textbf{Network: }\quad R_T(N) \;=\;
      \tilde O\!\left(d^2T^{2/3} \;+\; \sqrt N\,T^{2/3}\right)
      \\[8pt] \textbf{Per-agent: }\quad \frac{R_T(N)}{N} \;=\;
      \tilde O\!\left(\frac{d^2T^{2/3}}{N} \;+\; \frac{T^{2/3}}{\sqrt N}\right)
      \\[8pt] \text{versus } N\cdot\tilde O\!\left(d^2T^{2/3}\right)
      \text{ for } N \text{ independent ZoomSIB-UCB learners.}`,
    consumes: ['p8.lem-fed-stein', 'p8.coop-sleeping'],
    proof: { status: 'sketch', body: String.raw`
      **Conjectured. The strategy is to compose the two preceding lemmas through Prop 4.7.**

      Substituting the federated Phase-1 cost and the cooperative Phase-2 cost into
      $R_T \le R_T^{(1)} + \mathrm{Reg}_{\mathcal A}(N_{\text{bins}},T) + 2L_{f'}T\Delta$, and summing
      over the $N$ agents for network regret:

      - Phase 1: each agent explores for $T_0 = \tilde O(d^2T^{2/3}/N)$ rounds, so the NETWORK cost is
        $N \cdot T_0 = \tilde O(d^2T^{2/3})$ — independent of $N$.
      - Phase 2: $\tilde O(\sqrt N\,T^{2/3})$ by the cooperative sleeping-bandit bound.
      - Discretisation bias: $2L_{f'}\cdot NT\Delta$, which is $N$ times the single-agent term and so
        does NOT amortise at all.

      The third bullet is worth pausing on, because it is the honest caveat: bias is incurred
      per-agent-per-round and no amount of communication removes it. It is dominated by the Phase-2
      term only because both are $T^{2/3}$ and the constant $L_{f'}$ is fixed; a sharper statement
      would carry it explicitly.

      **Sanity check at $N = 1$:** the bound must reduce to Dey et al.'s $\tilde O(d^2T^{2/3})$, which
      it does, since $\sqrt 1 = 1$ and $T_0$ returns to $\tilde O(d^2T^{2/3})$.

      **Falsifiable content.** The two terms amortise at DIFFERENT rates — $N$ versus $\sqrt N$ — so
      the model predicts that collaboration helps most in high dimension. Sweeping $d$ at fixed $N$
      would refute it if the two curves scaled alike.
    ` },
    note: 'A TARGET to prove, not an established fact. Even if only the Phase-1 lemma is proven ' +
          'rigorously and Phase 2 is supported empirically, the project is complete and honest.',
    tags: ['ours', 'headline', 'pitch'] },

  { id: 'p8.asymmetry', type: 'conjecture', tier: 1, concept: 'open',
    label: 'The asymmetry', title: 'The falsifiable scientific finding',
    where: { section: '4.2', page: null },
    statement: String.raw`\text{The } d\text{-dependent ESTIMATION cost is FULLY amortized across the}
      \text{ network } (\div N), \text{ while the BANDIT-EXPLORATION cost is only }
      \sqrt N\text{-amortized.}
      \\[6pt] \Rightarrow \text{ collaboration helps MOST in HIGH DIMENSION,}
      \text{ which is directly falsifiable by sweeping } d \text{ at fixed } N.`,
    consumes: ['p8.conj1'],
    proof: { status: 'sketch', body: String.raw`
      Not a theorem — a reading of the conjectured bound, and the experiment that could refute it.

      Per-agent regret is $\tilde O\big(d^2T^{2/3}/N + T^{2/3}/\sqrt N\big)$. The first term carries
      ALL of the $d$-dependence and divides by $N$; the second carries none and divides only by
      $\sqrt N$. So the ratio of federated to independent per-agent regret improves with $d$:
      the estimation term, which dominates when $d$ is large, is exactly the term that amortises fully.

      **Why the two differ.** Phase 1 shares a SUFFICIENT STATISTIC — a sample mean, which pools
      exactly, so $N$ agents each doing $1/N$ of the work is lossless. Phase 2 shares EVIDENCE about
      which bin is best; agents still have to play sub-optimal bins to generate that evidence, and
      exploration cannot be divided without each agent still paying to act on it. That is the
      standard $\sqrt N$ ceiling for cooperative bandits, and it is structural rather than an artefact
      of the analysis.

      **The refuting experiment.** Sweep $d \in \{5,10,20,40\}$ at fixed $N$ and plot federated versus
      independent per-agent regret. The prediction is that the gap WIDENS with $d$. If the two curves
      stay parallel, the claimed asymmetry is wrong. exp04_dim_scaling.py already measures the
      single-agent side of this, and the Stein rate has been verified at exactly $n^{-1/2}$
      (fitted $-0.496$ to $-0.501$), which is the premise the whole argument stands on.
    ` },
    note: 'This asymmetry is the interesting scientific content — not the rates themselves. ' +
          'It makes a prediction that a single experiment can refute, which is what separates a ' +
          'result from an observation. exp04_dim_scaling.py is the harness.',
    tags: ['ours', 'headline', 'pitch'] },

  /* -------------------------------------------------------- extensions -- */
  { id: 'p8.e1', type: 'open-problem', tier: 1, concept: 'communication',
    label: 'E1 comm.', title: 'Extension E1 — communication efficiency (do this)',
    where: { section: '4.3', page: null },
    statement: String.raw`\text{Phase 1 needs ONE message. How rarely can Phase 2 communicate before}
      \text{ the } \sqrt N \text{ gain disappears? Sweep the interval } C \text{ and byte budget }
      B; \text{ compare periodic against event-triggered (send only when a bin’s count changes}
      \text{ by a multiplicative factor). Port RC-DLUCB’s rare-communication idea.}`,
    consumes: ['p8.coop-sleeping'],
    proof: { status: 'none' },
    note: 'The most CS6007-flavoured axis, since communication complexity is the course’s ' +
          'central concern. Also the safety net: if the federated Phase-1 proof stalls, the ' +
          'project still stands on this empirical study.',
    tags: ['ours', 'priority-1'] },

  { id: 'p8.e2', type: 'open-problem', tier: 1, concept: 'safety',
    label: 'E2 safety', title: 'Extension E2 — safety (if time allows)',
    where: { section: '4.3', page: null },
    statement: String.raw`\textbf{Tier (a) linear: } \langle\mu^{*},x\rangle \le c \text{ — exactly}
      \text{ Safe-DLUCB, and a safe project.}
      \\[6pt] \textbf{Tier (b) single-index: } h(\langle\mu^{*},x\rangle) \le c \text{ with } h
      \text{ unknown — genuinely new. Build a pessimistic safe set from a SECOND Stein estimator}
      \text{ plus a binned lower confidence bound, and restrict Phase-2 UCB to the safe bins.}`,
    consumes: ['p8.conj1'],
    proof: { status: 'none' },
    note: 'Tier (b) is the honest reading of the "Safe" in the original project title. Note it ' +
          'reuses the SAME binning machinery as the reward side — which is what makes it ' +
          'tractable rather than a second research project.',
    tags: ['ours', 'priority-2'] },

  { id: 'p8.e3', type: 'open-problem', tier: 1, concept: 'index-est',
    label: 'E3 clustered', title: 'Extension E3 — clustered indices (highest ceiling)',
    where: { section: '4.3', page: null },
    statement: String.raw`\text{Drop the shared-}\theta^{*} \text{ assumption: agent } i \text{ has}
      \text{ its own } \theta^{*}_i, \text{ and agents fall into } M \text{ unknown clusters}
      \ \theta^{*}_{(1)},\dots,\theta^{*}_{(M)}. \text{ Naive averaging now causes NEGATIVE TRANSFER.}
      \\[6pt] \text{Run an IFCA-style alternation: each agent assigns itself to the cluster whose}
      \text{ current index best explains its local Stein statistic; each cluster then averages its}
      \text{ members’ estimators.}`,
    consumes: ['p8.lem-fed-stein'],
    proof: { status: 'none' },
    note: 'Prof. Ghosh’s own IFCA (NeurIPS 2020) applied to his own ZoomSIB — a ' +
          'combination nobody has published. Keep it as the "excellent" tier, never a dependency.',
    tags: ['ours', 'priority-3'] },

  { id: 'p8.e4', type: 'open-problem', tier: 2, concept: 'open',
    label: 'E4 multi-index', title: 'Extension E4 — multi-index (stretch, do not attempt)',
    where: { section: '4.3', page: null },
    statement: String.raw`f\!\left(\langle x,\theta_1\rangle,\dots,\langle x,\theta_m\rangle\right)
      \text{ — listed as open by Dey et al. Mention in future work ONLY.}`,
    consumes: ['p8.conj1'],
    proof: { status: 'none' },
    tags: ['ours', 'out-of-scope'] },

  { id: 'p8.gap', type: 'regret-bound', tier: 1, concept: 'open',
    label: 'The gap table', title: '§3 — every column solved, the last row empty',
    where: { section: '3', page: null },
    statement: String.raw`\begin{array}{lcccc}
      \textbf{work} & \textbf{unknown link} & \textbf{multi-agent} & \textbf{safety} & \textbf{optimal rate} \\[3pt]
      \text{OFUL '11} & \times & \times & \times & - \\
      \text{Chowdhury–Gopalan '17} & \checkmark\ \text{RKHS} & \times & \times & - \\
      \text{Dubey–Pentland '20} & \checkmark\ \text{RKHS} & \checkmark & \times & - \\
      \text{Amani–Thrampoulidis '21} & \times & \checkmark & \checkmark & - \\
      \text{Kang et al. '26} & \checkmark\ \text{SIM} & \times & \times & \times\ (T^{3/4}) \\
      \text{Arya et al. '26} & \checkmark\ \text{SIM+RKHS} & \times & \times & - \\
      \text{Dey et al. '26} & \checkmark\ \text{SIM} & \times & \times & \checkmark\ \tilde\Theta(T^{2/3}) \\[3pt]
      \textbf{Fed-ZoomSIB} & \checkmark & \checkmark & \checkmark & \checkmark
      \end{array}`,
    consumes: ['p8.conj1'],
    proof: { status: 'none' },
    note: 'Every column has been solved. NO PAPER OCCUPIES THE LAST ROW. Single-index bandits are a ' +
          '2025–26 development and the multi-agent version simply has not been written yet. ' +
          'This table is the collapsed-view legend of the whole map.',
    tags: ['ours', 'pitch', 'headline'] }

  ]
});
