# Federated Single-Index Bandits — Literature Review and Problem Definition

**Course:** CS6007, Multi-Agent Machine Learning, IIT Bombay
**Instructor:** Prof. Avishek Ghosh
**Status:** working document for the team (not a submission)

---

## 0. The single most important strategic fact

One of the papers on the instructor's own project-ideas list —
[arXiv:2605.09454, *Optimal Regret for Single Index Bandits*](https://arxiv.org/abs/2605.09454) —
is authored by **Devdan Dey, Sujoy Bhore, and Avishek Ghosh**. It is the instructor's own
2026 paper, and all three authors are at IIT Bombay CSE.

Prof. Ghosh's three relevant research lines are:

| Line | Representative work | Why it matters here |
|---|---|---|
| Single-index bandits | Dey, Bhore, Ghosh 2026 (ZoomSIB-UCB) | the algorithmic backbone we extend |
| Clustered federated learning | Ghosh, Chung, Yin, Ramchandran, NeurIPS 2020 (IFCA) | the template for our heterogeneity extension |
| Bandit misspecification | Ghosh, Chowdhury, Gopalan, AAAI 2017 | the motivation for "unknown link function" |

The intersection of the first two is empty in the literature and is a natural,
well-posed, genuinely open problem. **That intersection is our project.**

A second consequence: CS6007 is a *theory* course. Last year's decks (`../Project/Project
Presentations CS6007 2025/`) are structured as problem → assumptions → algorithm →
theorem → experiments. The robot-navigation framing in
[01-safe-cooperative-kernel-bandits.md](../01-safe-cooperative-kernel-bandits.md) should
therefore be demoted to a one-slide motivating application; a custom 2-D robot simulator
with collision geometry and ROS is off the critical path and off the grading rubric.

---

## 1. Background: the single-index model

### 1.1 Definition

In a **single-index model (SIM)**, the response depends on the covariate only through a
one-dimensional projection:

```
y = f(⟨x, θ*⟩) + η,     x ∈ R^d,  θ* ∈ R^d,  f : R → R
```

where **both** the direction `θ*` and the link function `f` are unknown. This is a
*semiparametric* model, sitting strictly between two familiar extremes:

- `f = identity` → the linear bandit (Abbasi-Yadkori et al. 2011, OFUL),
- `f` known and monotone → the generalized linear bandit (Filippi et al. 2010, Li et al. 2017),
- `f` unknown → **single-index bandit (SIB)**.

### 1.2 Why unknown `f` is the right question

Assuming a known link is not a harmless convenience. Ghosh, Chowdhury and Gopalan
(AAAI 2017) and Bogunovic & Krause (2021) show that **misspecifying the link causes
linear regret** — the algorithm does not merely degrade, it fails. In recommendation,
click-through, dose-response and congestion models, nobody knows the true link. So SIB is
the honest formulation.

### 1.3 Identifiability

`f(⟨x,θ*⟩)` is unchanged if we rescale `θ* → cθ*` and `f(z) → f(z/c)`. Two conventions fix this:

1. **Scale:** normalize `‖θ*‖₁ = 1` (Dey et al. use ℓ₁ because their discretization is
   tailored to the ℓ₁ geometry; Kang et al. do the same).
2. **Direction/sign:** assume `μ* := E[f'(⟨X,θ*⟩)] > 0`.

`μ*` is a *signal-strength* parameter, and how strongly an algorithm depends on it is a
real point of differentiation between papers (§2.2).

### 1.4 Stein's identity — the tool that makes everything work

For a density `p`, define the **score function** `S(x) = −∇ₓ log p(x)`. The generalized
Stein lemma gives, for continuously differentiable `f`,

```
E[y · S(x)] = E[f(⟨x,θ*⟩) S(x)] = E[f'(⟨x,θ*⟩)] · θ* = μ* θ*
```

Read that carefully: **the expected score-weighted reward is proportional to `θ*`, and
the identity never references the form of `f`.** So the unknown direction can be estimated
by a *plain sample average* — no likelihood, no link, no optimization:

```
θ̂ = (1/n) Σᵢ φ_τ( yᵢ S(xᵢ) ),      φ_τ = elementwise truncation at τ
θ̂₀ = θ̂ / ‖θ̂‖₁
```

Truncation at `τ = sqrt(3(σ² + L_f²)Mn / log(2d/δ))` controls heavy tails and yields the
`O(d/√n)` estimation rate. The requirement is that `p` (hence `S`) is **known to the
learner** — standard in this line of work, and reasonable when the context distribution is
estimated offline from logged data.

> **This is the technical fact our entire project pivots on.** A sample mean is the one
> statistic that federates *exactly*: averaging local Stein estimators across agents is
> algebraically identical to the centralized estimator on pooled data. Phase 1 of the
> state-of-the-art algorithm therefore parallelizes with **one round of communication and
> zero approximation error**. Very few bandit primitives have this property.

---

## 2. The papers, one by one

### 2.1 Kang, Liu, Yi, Lyu, Zhang, Zhou, Li — *Single Index Bandits: Generalized Linear Contextual Bandits with Unknown Reward Functions* (ICLR 2026) — [arXiv:2506.12751](https://arxiv.org/abs/2506.12751)

**What it does.** Introduces the SIB problem. Three algorithms:

- **STOR / ESTOR** — assume `f` is *monotonically increasing*. Use the truncated Stein
  estimator for `θ*`, then exploit monotonicity: the best arm is simply the one maximizing
  `⟨x, θ̂⟩`, so no estimate of `f` is needed at all. **ESTOR achieves Õ(√T)**, near-optimal.
- **Sparse extension** — same `√T` rate with `d` replaced by the sparsity index `s`.
- **GSTOR** — drops monotonicity. Uses a kernel-based estimate of `f` under a Gaussian
  design assumption, in an *explore-then-commit* structure. Achieves **Õ(T^{3/4})**.

**What to take from it.** The problem formulation, the truncated Stein estimator, and the
`√T` monotone benchmark. It is also the paper our backbone directly improves upon.

**Its limitations (= our opportunities).** Single agent. Non-monotone rate `T^{3/4}` is
loose. Explore-then-commit wastes a fixed, horizon-length prefix. Implicitly needs
knowledge of `μ*` to set the exploration length.

---

### 2.2 Dey, Bhore, Ghosh — *Optimal Regret for Single Index Bandits* (2026) — [arXiv:2605.09454](https://arxiv.org/abs/2605.09454) ★ backbone

**Setting.** Horizon `T`. Each round `t` the learner sees an arm set
`X_t = {x_{t,a} : a ∈ [K]}` of `K` feature vectors drawn i.i.d. from a continuous density
`p`. Pulls `x_t`, observes `y_t = f(⟨x_t, θ*⟩) + η_t`, `η_t` conditionally σ-sub-Gaussian.
Regret is measured against `argmax_a f(⟨x_{t,a}, θ*⟩)` — note that for non-monotone `f`
**this is not the arm with the largest projection**, which is precisely what makes the
problem hard.

**Assumptions.**
- *A1 (noise)*: `η_t` independent of the arm set, conditionally σ-sub-Gaussian.
- *A2 (score moment)*: `E[S_j(X)²] ≤ M` for all `j ∈ [d]`.
- *A3 (regularity)*: contexts i.i.d. from continuously differentiable `p > 0`, each
  coordinate κ-sub-Gaussian; `f` continuously differentiable with `|f| ≤ L_f`,
  `|f'| ≤ L_f'` on the effective range.

**Algorithm — ZoomSIB-UCB (two phases).**

*Phase 1 — direction estimation (`t = 1 … T₀`).* Pull arms uniformly at random. Form the
truncated Stein estimator, normalize to `θ̂₀ = θ̂/‖θ̂‖₁`. `T₀ = ⌈d²T^{2/3} · polylog(dT/δ)⌉`
is calibrated so that

```
‖θ̂₀ − θ*‖₁ ≤ Δ / (2L),     Δ = T^{−1/3},  L = 4κ√(log(dTK/δ))
```

i.e. the estimation error displaces any arm's projected index by at most **half a bin width**.

*Phase 2 — sleeping UCB over bins (`t = T₀+1 … T`).* Partition the index line `[−W, W]`
(`W = 4κ√(log(TK/δ))`) into `N = ⌈2W/Δ⌉ = O(T^{1/3})` bins of width `Δ`. Each round:
1. project each arm: `ẑ_{t,a} = ⟨x_{t,a}, θ̂₀⟩`;
2. map to its bin `b_{t,a}`, forming the **available bin set** `B_t ⊆ [N]`;
3. play `argmax_{a : b_{t,a} ∈ B_t} UCB_{b_{t,a}}(t)` with
   `UCB_j(t) = S_j/n_j + σ√(2 log(2NT/δ)/n_j)`;
4. update the per-bin sufficient statistics `(n_j, S_j)` only.

**Two subtleties that matter for us.**

- *Sleeping bandits.* Only a random subset `B_t` of bins is available each round, because
  availability depends on where the `K` freshly drawn arms happen to land. A standard UCB
  analysis over all `N` bins is invalid; the regret must be measured against the best
  *available* bin. The analysis uses a sleeping-UCB argument (Kanade et al. 2009,
  Kleinberg et al. 2010).
- *Sample splitting.* `θ̂₀` is computed entirely from Phase-1 data and then **frozen**. This
  makes the bin assignment `F_{t−1}`-measurable, so the within-bin noise is a martingale
  difference sequence. Without this, the analysis breaks.

**Results.**
- *Theorem 4.3:* `R_T ≤ Õ(d² T^{2/3})`, with probability `1−δ`, provided `μ* ≳ 1/polylog(dT/δ)`.
- *Theorem 5.1 (minimax lower bound):* `sup E[R_T] ≥ c T^{2/3}`. Construction: embed `2^N`
  plateaued "bump" perturbations of height `ε ∼ 1/(2N)` on a common ramp, reduce to an
  `N`-armed bandit, apply Bretagnolle–Huber. **So `Θ̃(T^{2/3})` is the correct rate** for
  non-monotone SIB — this closes the open question left by Kang et al.
- *Corollary 4.8 (instance-dependent):* if `f` has a unique well-separated maximum, regret
  improves to `O(T^{1/3} log T)`.
- **★ Proposition 4.7 (modular reduction).** *Let `A` be any bandit algorithm for `N` arms
  with stochastic availability, achieving regret `Reg_A(N,T)` against the best available
  arm. Run Phase 1 to obtain `θ̂₀`, then run `A` on the `N` bins. Then*
  ```
  R_T ≤ R_T^{(1)} + Reg_A(N, T) + 2 L_f' T Δ
  ```

  **This proposition is the single most important sentence in the paper for us.** It says
  Phase 2 is a *black box*: swap in any sleeping-bandit subroutine and the bound follows
  automatically. A **cooperative multi-agent sleeping bandit is exactly such a
  subroutine.** Our theory therefore reduces to (a) a federated Phase-1 concentration
  lemma and (b) a cooperative sleeping-UCB regret bound — instead of a monolithic proof
  from scratch. This de-risks the theoretical component enormously.

**Experiments.** Links `f(z) = −(z−1)²+1` (quadratic), `z e^{−z²}` (asymmetric),
`sin z + 0.3z` (zigzag); `d = 10`, `K = 20`, 30 trials. Baselines GSTOR, ESTOR, Random.
Real data: KDD Cup 99 (`d = 39`), Forest Cover Type (`d = 55`), cast as contextual bandits,
`T = 10,000`, `K = 32`. Notably they replace the theoretical `T₀` with an **adaptive
stopping rule** that monitors parameter-estimate stability — exploration ends at ~1.8% of
the horizon for easy links. We should copy this trick; the theoretical `T₀` is unusable in
practice.

**Stated open problems.** Removing the `μ* ≠ 0` / Stein dependence; going beyond bounded
Lipschitz `f`; the **multi-index** setting.

---

### 2.3 Arya, Bhattacharjee, Sriperumbudur — *Kernel Single-Index Bandits: Estimation, Inference, and Learning* (2026) — [arXiv:2603.18938](https://arxiv.org/abs/2603.18938)

**What it does.** Finitely many arms, each with an **arm-specific** index `θ_a` and an
unknown nonparametric link — i.e. `E[r | x, a] = g_a(⟨θ_a, x⟩)`. Proposes a **kernelized
ε-greedy** algorithm: Stein-based estimation of each `θ_a`, plus
**inverse-propensity-weighted kernel ridge regression** for each `g_a`.

**Why it is technically interesting.** It confronts the statistical problem that the
sampling distribution depends on the policy: observations are dependent over time and IPW
inflates variance. It delivers *inference*, not just regret: asymptotic normality of the
index estimator under adaptive sampling (→ valid confidence regions), and a directional
functional CLT for the RKHS estimator (→ pointwise confidence intervals), via concentration
for inverse-weighted Gram matrices and martingale CLTs. Regret **Õ(√T)** under
common-link Lipschitz conditions.

**What to take from it.** (i) The arm-specific `g_a(⟨θ_a, x⟩)` formulation — this is the
model our original proposal wrote down. (ii) Kernel-ridge machinery as the smooth
alternative to ZoomSIB's binning. (iii) The ε-greedy/IPW route as a *secondary baseline*.

**Trade-off to state clearly in the pitch.** Arya et al. get `Õ(√T)`, better than
`T^{2/3}` — but under a *common-link Lipschitz* condition and an ε-greedy scheme with
propensity control. Dey et al.'s `Θ̃(T^{2/3})` is the minimax rate for the *general
non-monotone bounded-Lipschitz* class. These are different function classes; they do not
contradict each other, and being able to say this crisply is a good sign of understanding.

---

### 2.4 Chowdhury & Gopalan — *On Kernelized Multi-armed Bandits* (ICML 2017) — [arXiv:1704.00445](https://arxiv.org/abs/1704.00445)

**What it does.** Reward function lies in the RKHS of a known kernel. Proposes **IGP-UCB**
and **GP-TS**. The core technical contribution is a **new self-normalized concentration
inequality for vector-valued martingales of arbitrary (possibly infinite) dimension**,
which yields a tighter confidence width than Srinivas et al.'s GP-UCB. Regret is expressed
via the **maximum information gain** `γ_T`.

**What to take from it.** This is the confidence-ellipsoid technology for RKHS rewards, and
the ancestor of everything cooperative-kernel. **IGP-UCB / GP-UCB is one of our baselines.**
It is also the "no structure exploited" control: it learns a `d`-dimensional function
without using the single-index structure, so its regret should degrade visibly as `d` grows
— a clean experiment to run.

---

### 2.5 Dubey & Pentland — *Kernel Methods for Cooperative Multi-Agent Contextual Bandits* (ICML 2020) — [arXiv:2008.06220](https://arxiv.org/abs/2008.06220)

**What it does.** `N` agents on a network with **communication delays**; each agent's
reward is a linear function of the context's image in an RKHS. Proposes **Coop-KernelUCB**,
achieving near-optimal **per-agent** regret while remaining computationally and
communicationally efficient (Nyström-type approximations to avoid shipping full kernel
matrices). Generalizes several earlier multi-agent bandit results.

**What to take from it.** (i) The **per-agent regret** notion and the "collaboration should
buy you a `√N`-type speedup" framing. (ii) How network delay enters the bound. (iii) It is
the closest existing work to ours — and **it assumes the reward is linear in the RKHS
image, i.e. the link is effectively known/fixed.** It does not exploit or estimate
single-index structure. Stating this cleanly is how we position our novelty.

---

### 2.6 Amani & Thrampoulidis — *Decentralized Multi-Agent Linear Bandits with Safety Constraints* (AAAI 2021) — [arXiv:2012.00314](https://arxiv.org/abs/2012.00314)

**What it does.** `N` agents on a connected undirected graph `G`, communicating only with
immediate neighbours via a symmetric doubly-stochastic matrix `P` (Assumption 1;
`1 = |λ₁| > |λ₂| ≥ …`). Three algorithms:

- **DLUCB** — gossip consensus repeated over cycles; network regret
  `O(d log(NT) √(NT))` at `O(dN²)` communicated values per round. The graph enters via a
  small **additive** term depending on the **spectral gap `1 − |λ₂|`**. Works for arbitrary
  connected topologies, no master node required.
- **RC-DLUCB** — rare communication; total communication cost `O(d³N^{2.5})` over *all* `T`
  rounds, trading a little regret for a large bandwidth saving.
- **Safe-DLUCB** — unknown **linear** safety constraint `⟨μ*, x⟩ ≤ c` with `c` known and
  `μ*` unknown; after playing, agent `i` observes safety feedback
  `z_{i,t} = ⟨μ*, x_{i,t}⟩ + ζ_{i,t}`. Maintains a conservative safe set from a confidence
  region for `μ*`, seeded by a known-safe action. Achieves the **same regret order as the
  unconstrained problem**.

**What to take from it.** This is our multi-agent and safety template, essentially
off-the-shelf: the consensus protocol, the spectral-gap-dependent delay analysis, the
rare-communication variant, and the safe-set construction. **Its limitation is that
everything is linear.** Our contribution is to carry it to an unknown nonlinear link.

---

### 2.7 Supporting context (cite, don't implement)

- **Ghosh, Chowdhury, Gopalan — Misspecified Linear Bandits (AAAI 2017),
  [arXiv:1704.06880](https://arxiv.org/abs/1704.06880).** Why an unknown link is not a
  technicality: misspecification can cause linear regret.
- **Ghosh, Chung, Yin, Ramchandran — An Efficient Framework for Clustered Federated
  Learning (NeurIPS 2020).** IFCA: alternately assign clients to clusters by lowest loss
  and update cluster models. The template for our heterogeneity extension (§4.3).
- **Kleinberg, Niculescu-Mizil, Sharma (2010); Kanade, McMahan, Bryan (2009).** Sleeping
  bandits — the stochastic-availability model Phase 2 lives in.
- **Abbasi-Yadkori, Pál, Szepesvári (2011).** OFUL and the self-normalized bound;
  `LinUCB`-style baseline.
- **Landgren, Srivastava, Leonard (2016); Martínez-Rubio, Kanade, Rebeschini (2019).**
  Cooperative/distributed multi-armed bandits over graphs — the `√N`-speedup results we
  will invoke for Phase 2.

---

## 3. The gap, stated as a table

| Work | unknown nonlinear link | multi-agent / graph | safety constraint | optimal non-monotone rate |
|---|:--:|:--:|:--:|:--:|
| Abbasi-Yadkori '11 (OFUL) | ✗ linear | ✗ | ✗ | — |
| Chowdhury & Gopalan '17 (IGP-UCB) | ✓ RKHS | ✗ | ✗ | — |
| Dubey & Pentland '20 (Coop-KernelUCB) | ✓ RKHS | **✓** | ✗ | — |
| Amani & Thrampoulidis '21 (Safe-DLUCB) | ✗ linear | **✓** | **✓** | — |
| Kang et al. '26 (ESTOR/GSTOR) | ✓ SIM | ✗ | ✗ | ✗ (`T^{3/4}`) |
| Arya et al. '26 (kernel SIB) | ✓ SIM+RKHS | ✗ | ✗ | — |
| **Dey, Bhore, Ghosh '26 (ZoomSIB-UCB)** | ✓ SIM | ✗ | ✗ | **✓ (`Θ̃(T^{2/3})`)** |
| **This project (Fed-ZoomSIB)** | **✓** | **✓** | **✓** | **✓** |

Every column has been solved. **No paper occupies the last row.** Single-index bandits are
a 2025–26 development and the multi-agent version simply has not been written yet.

---

## 4. Our problem

### 4.1 Core setting (this is what we commit to)

A network of `N` agents sits on a connected undirected graph `G` with communication matrix
`P` (Amani–Thrampoulidis Assumption 1). At each round `t ∈ [T]`:

1. every agent `i` observes its own arm set `X_{i,t} = {x_{i,t,a}}_{a∈[K]}`, drawn i.i.d.
   from a known density `p`;
2. agent `i` pulls `x_{i,t}` and observes `y_{i,t} = f(⟨x_{i,t}, θ*⟩) + η_{i,t}`;
3. every `C` rounds, agents exchange a message of at most `B` values with their neighbours.

The link `f` and direction `θ*` are **unknown and shared across agents**. Assumptions A1–A3
of Dey et al. carry over verbatim per agent.

**Objective — network regret:**

```
R_T(N) = Σ_{t=1}^{T} Σ_{i=1}^{N} [ f(⟨x*_{i,t}, θ*⟩) − f(⟨x_{i,t}, θ*⟩) ]
```

**Question.** *What does collaboration buy in a single-index bandit, and at what
communication cost?*

### 4.2 Why this is the right question (and why it should work)

The two phases of ZoomSIB-UCB federate for *completely different reasons*, and the gains
compose. This is the intellectual core of the project.

**Phase 1 federates exactly, in one shot.** The Stein estimator is a sample mean, so
averaging local estimators equals the centralized estimator on pooled data — no
approximation, no iteration, no consensus rounds. With `N` agents each spending `T₀` rounds
exploring, the pooled sample size is `N·T₀`, and the error becomes
`ε ≍ C_θ d √(log(2d/δ)/(N T₀))`. To meet the same calibration `ε ≤ Δ/(2L)` with
`Δ = T^{−1/3}` we need only

```
T₀ = Õ( d² T^{2/3} / N )        [vs. Õ(d² T^{2/3}) for a lone agent]
```

so the **Phase-1 network cost is `N · T₀ = Õ(d² T^{2/3})` — independent of `N`**, against
`N · Õ(d² T^{2/3})` for `N` independent learners. That is a **factor-`N`** saving purchased
with **exactly one round of communication of `d` numbers per agent.** This is an unusually
clean collaborative-gain story and it is the headline claim of the pitch.

**Phase 2 federates as a cooperative sleeping bandit.** The per-bin sufficient statistics
are just `(n_j, S_j)` — two scalars per bin, `O(T^{1/3})` bins. Sharing them is a standard
cooperative MAB over a graph. Invoking the `√N`-speedup results for distributed MAB inside
**Proposition 4.7**:

```
Reg_A(N_bins, T) = Õ( √(N_bins · N · T) ) = Õ( √N · T^{2/3} )
```

against `N · T^{2/3}` for independent learners — a **factor `√N`** saving.

**Conjectured main theorem (the target).**

```
Network:   R_T(N) = Õ( d² T^{2/3} + √N · T^{2/3} )
Per-agent: R_T(N)/N = Õ( d² T^{2/3}/N + T^{2/3}/√N )
```

versus `N · Õ(d² T^{2/3})` for `N` independent ZoomSIB-UCB learners. Note the structure:
the `d`-dependent estimation cost is *fully amortized* across the network, while the
bandit-exploration cost is only `√N`-amortized. **That asymmetry is the interesting
scientific finding** — it predicts that collaboration helps most in **high dimension**,
which is directly falsifiable by sweeping `d` at fixed `N`.

These are targets to prove, not established facts. Even if only the Phase-1 lemma is proven
rigorously and Phase 2 is supported empirically, the project is complete and honest.

### 4.3 Extensions, in priority order

- **E1 — Communication efficiency (do this).** Phase 1 needs *one* message. How rarely can
  Phase 2 communicate before the `√N` gain disappears? Sweep the interval `C` and the byte
  budget `B`; compare periodic vs. event-triggered (send only when a bin's count changes by
  a multiplicative factor). Port RC-DLUCB's rare-communication idea. This is the most
  CS6007-flavoured axis, since communication complexity is the course's central concern.

- **E2 — Safety (do this if time allows).** Add an unknown safety function with its own
  bandit feedback `z_{i,t}`. Two tiers: *(a) linear* `⟨μ*, x⟩ ≤ c`, which is exactly
  Safe-DLUCB and gives a safe project; *(b) single-index* `h(⟨μ*, x⟩) ≤ c`, which is
  genuinely new — build a pessimistic safe set from a **second** Stein estimator plus the
  binned lower confidence bound, and restrict Phase-2 UCB to the safe bins. Tier (b) is the
  honest reading of the "Safe" in our project title.

- **E3 — Heterogeneous / clustered indices (highest ceiling).** Drop the shared-`θ*`
  assumption: agent `i` has its own `θ*_i`, and the agents fall into `M` unknown clusters
  `θ*_{(1)}, …, θ*_{(M)}`. Naive averaging now causes **negative transfer**. Run an
  **IFCA-style alternation**: each agent assigns itself to the cluster whose current index
  best explains its local Stein statistic, then each cluster averages its members'
  estimators. This is Prof. Ghosh's own IFCA applied to his own ZoomSIB — a combination
  nobody has published, and a very strong final-project result. Keep it as the "excellent"
  tier, not a dependency.

- **E4 — Multi-index (stretch).** Dey et al. explicitly list the multi-index setting
  (`f(⟨x,θ₁⟩, …, ⟨x,θ_m⟩)`) as an open problem. Mention in "future work" only; do not attempt.

### 4.4 Scope controls

- No deep RL, no ROS, no hardware. The robot fleet is a motivating slide, nothing more.
- Actions stay a finite arm set of `K` feature vectors. Continuous arm sets are a separate
  research problem.
- If the federated Phase-1 proof stalls, the project still stands on the empirical
  communication study (E1) — the theory is not a single point of failure.
- The known-score-function assumption (`p` known) is inherited from the whole SIB
  literature. State it explicitly in the pitch rather than hiding it; a question about it is
  the most likely one from the audience.

---

## 5. The five references for the pitch

The brief requires at least five. These are the right five, in this order:

1. Dey, Bhore & Ghosh, *Optimal Regret for Single Index Bandits*, 2026 — the backbone.
2. Kang et al., *Single Index Bandits*, ICLR 2026 — the problem's origin.
3. Dubey & Pentland, *Kernel Methods for Cooperative Multi-Agent Contextual Bandits*, ICML 2020 — cooperative template.
4. Amani & Thrampoulidis, *Decentralized Multi-Agent Linear Bandits with Safety Constraints*, AAAI 2021 — decentralization and safety.
5. Arya, Bhattacharjee & Sriperumbudur, *Kernel Single-Index Bandits*, 2026 — kernel/inference view.
6. Chowdhury & Gopalan, *On Kernelized Multi-armed Bandits*, ICML 2017 — RKHS confidence sets.
7. Ghosh, Chung, Yin & Ramchandran, *An Efficient Framework for Clustered Federated Learning*, NeurIPS 2020 — for extension E3.
