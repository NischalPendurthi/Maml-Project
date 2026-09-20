# CS6007 Project Roadmap — Fed-ZoomSIB

**Today:** 20 Sept 2026 · **Pitch:** 28 Sept 2026 · **Final presentation:** early Nov 2026 (last year's was 2 Nov)

Read [01-literature-and-problem.md](01-literature-and-problem.md) first. This document is
the execution plan: what to build, in what order, and where the novelty lives.

---

## Guiding principle

**Reproduce before you innovate.** Every hour spent building a single-agent ZoomSIB-UCB
that exactly reproduces Figure 1 of Dey–Bhore–Ghosh is an hour that makes the federated
result credible. A federated curve is meaningless without a trustworthy single-agent curve
underneath it, because the whole claim is *"collaboration buys you X"* — and X is measured
against that baseline.

Second principle: **the theory and the code must be attackable separately.** If the
federated Phase-1 proof stalls, the empirical communication study still carries the
project. If experiments run late, the Phase-1 lemma still carries it. Never let both
depend on the same milestone.

---

## Phase 0 — Pitch (20 → 28 Sept)

| # | Task | Owner | Done when |
|---|---|---|---|
| 0.1 | Read §2.2 of the lit review + skim arXiv:2605.09454 §3–4 | both | you can explain Phase 1/Phase 2 at a whiteboard |
| 0.2 | Compile `slides/pitch/main.tex`, fill in names/roll numbers | — | PDF builds, ≤ 5 min at speaking pace |
| 0.3 | Rehearse once with a timer | both | under 5:00 |
| 0.4 | Sanity-check the `√N` / factor-`N` arithmetic in §4.2 | — | you can rederive `T₀ = Õ(d²T^{2/3}/N)` live |

**Nothing needs to be coded before the pitch.** The pitch is a plan, not a result.
Do 0.4 seriously though — "why does Phase 1 give `N` and Phase 2 only `√N`?" is the
obvious question from a bandits instructor, and the answer (a sample mean pools exactly;
exploration only concentrates as `√·`) is the best thing you can say in the whole talk.

---

## Phase 1 — Single-agent ground truth (29 Sept → 10 Oct)

**This is "what should be coded from existing knowledge."** All of it already exists in
the papers; none of it is novel. Do not improvise here — match the papers' settings so the
numbers are checkable.

### 1.1 Environment (`src/envs.py`)

```
SIBEnv(d, K, link, context_dist, sigma, seed)
  .reset() -> arm set X_t ∈ R^{K×d}, drawn i.i.d. from p
  .step(a) -> y = f(<x_a, θ*>) + η
  .oracle(X_t) -> max_a f(<x_a, θ*>)        # for regret
  .score(x) -> S(x) = -∇ log p(x)           # = x for standard Gaussian
```

Use **standard Gaussian contexts** first: then `S(x) = x`, which removes an entire class of
bugs. Links, copied exactly from Dey et al. §6 so results are comparable:

- quadratic `f(z) = −(z−1)² + 1`
- asymmetric `f(z) = z e^{−z²}`
- zigzag `f(z) = sin(z) + 0.3 z`
- monotone control `f(z) = 1/(1+e^{−z})` (where ESTOR *should* win — a good honesty check)

Defaults: `d = 10`, `K = 20`, `σ` small, 30 seeds.

### 1.2 Stein estimator (`src/stein.py`)

```
truncated_stein(X, y, tau) -> θ̂          # (1/n) Σ φ_τ(yᵢ S(xᵢ))
normalize_l1(θ̂)          -> θ̂₀
```

**Test it in isolation before anything else.** Plot `‖θ̂₀ − θ*‖₁` against `n` on log-log
axes; you must see slope `≈ −1/2`. If you do not, nothing downstream will work. This single
plot is also a slide in the final deck.

### 1.3 Single-agent ZoomSIB-UCB (`src/zoomsib.py`)

Algorithm 1 of the paper, verbatim. Two things people get wrong:

- **Freeze `θ̂₀` after Phase 1.** Do not keep updating it during Phase 2 — sample splitting
  is what makes the bin noise a martingale difference sequence.
- **Handle the empty available-bin set.** If `B_t = ∅`, pull uniformly at random (line 13).
  Also handle `|ẑ| > W` → `b = ⊥`.

Implement the **adaptive stopping rule** too (monitor stability of `θ̂₀` across a sliding
window, exit Phase 1 on convergence). The theoretical `T₀ = d²T^{2/3}·polylog` is far too
large to run; Dey et al. use adaptive stopping in all their experiments and so must we.

### 1.4 Baselines (`src/baselines.py`)

| Baseline | Source | Why it's in the plot |
|---|---|---|
| Random | — | sanity floor |
| LinUCB / OFUL | Abbasi-Yadkori '11 | shows linear models fail on non-monotone `f` |
| ESTOR | Kang et al. '26 | strong when `f` monotone, should collapse when not |
| GSTOR | Kang et al. '26 | the `T^{3/4}` non-monotone competitor |
| IGP-UCB | Chowdhury & Gopalan '17 | ignores index structure; should degrade with `d` |

### 1.5 Deliverable of Phase 1

A figure reproducing Dey et al. Fig. 1: cumulative regret vs `T` on log-log axes, slope
`≈ 0.53–0.67`, ZoomSIB-UCB below GSTOR. **If you have this by 10 Oct, the project is safe.**

---

## Phase 2 — The novel core: Fed-ZoomSIB (11 → 22 Oct)

**This is where the effort goes.** Everything above is reproduction; everything here is new.

### 2.1 Federated Phase 1 — one-shot Stein averaging (`src/fed_stein.py`)

The contribution in three lines of code and one lemma:

```
each agent i:  θ̂_i = truncated_stein(X_i, y_i, tau)      # local, from T₀ rounds
one broadcast: θ̄   = (1/N) Σ_i θ̂_i                        # or gossip with P
all agents:    θ̂₀  = normalize_l1(θ̄)
```

**Experiment E-A (the headline plot).** Fix target accuracy `‖θ̂₀ − θ*‖₁ ≤ ε`. Measure the
per-agent rounds `T₀` needed to reach it, for `N ∈ {1, 2, 4, 8, 16, 32}`. **Expect
`T₀ ∝ 1/N`.** Plot `T₀·N` vs `N` — it should be flat. That flat line *is* the factor-`N`
result, and it is the most persuasive single figure in the project.

**Experiment E-B (the asymmetry).** Sweep `d ∈ {5, 10, 20, 40}` at fixed `N`. The
collaborative gain should *grow* with `d`, because the `d`-dependent estimation cost is the
part that amortizes fully. This tests the prediction in §4.2 of the lit review and is the
kind of "theory made falsifiable" result that reads well.

**Theory task T-A.** Prove the federated Phase-1 concentration lemma: with `N` agents and
`n` local samples each, `‖θ̄ − μ*θ*‖₁ ≤ C_θ d √(log(2d/δ)/(Nn))` w.h.p., then push through
Lemma 2.1's normalization step. This is a genuine but *tractable* proof — independent
sub-Gaussian averages plus a union bound — and it is the theorem slide of the final deck.

### 2.2 Cooperative Phase 2 (`src/coop_bins.py`)

Per-bin statistics `(n_j, S_j)` shared over graph `G`. Implement:

- **Centralized pooling** — upper-bound reference, not deployable.
- **Gossip / consensus** with matrix `P` (Amani–Thrampoulidis Assumption 1), on complete,
  ring, star, and Erdős–Rényi graphs.
- **Independent** — no sharing, the lower-bound reference.

**Experiment E-C.** Network regret vs `T` for `N ∈ {1,4,8,16}`; plot per-agent regret and
check for the `√N` improvement. Plot regret against spectral gap `1 − |λ₂|` across
topologies — Amani & Thrampoulidis predict an additive penalty, and confirming that in a
*nonlinear* setting is a real result.

**Theory task T-B.** Instantiate **Proposition 4.7** with a cooperative sleeping-UCB as the
subroutine `A`. Because Prop 4.7 is modular, this is mostly a matter of citing the right
distributed-MAB regret bound and checking that stochastic availability is preserved under
pooling. Considerably easier than proving it from scratch.

### 2.3 Deliverable of Phase 2

The three plots E-A, E-B, E-C plus lemma T-A. **This alone is a complete, strong project.**

---

## Phase 3 — Communication efficiency (23 → 29 Oct)

The most CS6007-aligned axis. Phase 1 costs exactly **one** message of `d` numbers.
The question is Phase 2.

- **Sweep the interval `C`** — communicate every `C` rounds, `C ∈ {1, 10, 100, 1000, ∞}`.
- **Event-triggered** — agent broadcasts bin `j` only when `n_j` has grown by a
  multiplicative factor `(1+γ)` since its last broadcast. Expect `O(N_bins log T)` messages
  total instead of `O(T)`.
- **Quantization** — send `(n_j, S_j)` at reduced precision; plot regret vs bits/round.
- **Headline metric: regret per transmitted byte.** Not regret vs `T`. This reframing is
  what makes it a multi-agent-learning result rather than a bandits result.

**Expected finding, and the project's thesis:** *most of the collaborative gain in a
single-index bandit is purchasable with `O(1)` communication, because the expensive part —
learning the direction — is a single average.* If that holds, it is a genuinely quotable
conclusion.

---

## Phase 4 — Pick ONE extension (30 Oct → 5 Nov)

Do not attempt both. Decide on ~29 Oct based on how Phase 2 went.

### Option A — Safety (`src/safe.py`) — lower risk
Add safety feedback `z_{i,t} = h(⟨x, μ*⟩) + ζ`. Second Stein estimator for `μ*`; build
pessimistic per-bin LCB; restrict Phase-2 UCB to safe bins; keep a known-safe fallback arm.
Metrics: constraint-violation rate and regret vs the safe optimum. Start with linear `h`
(= Safe-DLUCB, known to work), then unknown `h` (new).

### Option B — Clustered indices (`src/ifca_sib.py`) — higher ceiling
Agents have heterogeneous `θ*_i` from `M` unknown clusters. IFCA alternation: each agent
picks the cluster centre closest to its local Stein estimate; each cluster averages its
members. Show naive averaging suffers **negative transfer** while clustered averaging
recovers the gain. Sweep cluster separation. This is Prof. Ghosh's IFCA applied to his own
ZoomSIB — the highest-value result available to us.

**Recommendation: Option B**, if Phase 2 finishes on schedule. It is more novel, it is
squarely "multi-agent machine learning", and the negative-transfer plot is compelling. Take
Option A if Phase 2 slips — the linear tier is guaranteed to work.

---

## Phase 5 — Final deliverables (5 → 12 Nov)

- Final deck (same template, ~25–35 slides: problem → assumptions → algorithm → theorem → experiments → ablations → conclusion).
- Short report / arXiv-style writeup.
- Clean repo with a `README`, seeds fixed, one script per figure.
- 20+ seeds with confidence intervals on every plot. Last year's decks show error bars; match that.

---

## Where the novelty is, in one paragraph

Everything in **Phase 1 is reproduction** — ZoomSIB-UCB, the Stein estimator, LinUCB,
IGP-UCB, ESTOR/GSTOR all exist and should be implemented from the papers without
improvisation. The novelty begins at **§2.1**: no published work federates a single-index
bandit. The specific new objects are (i) the **one-shot federated Stein estimator** and its
concentration lemma, (ii) the **cooperative sleeping-bandit instantiation of Proposition
4.7**, (iii) the **communication–regret trade-off curve** for an unknown-link bandit, and
(iv) optionally the **clustered-index (IFCA-style) variant**. Of these, (i) is the one to
protect: it is small, provable, high-contrast against the `N`-independent-learners baseline,
and it is the reason the whole approach works.

---

## Proposed repo layout

```
src/
  envs.py        SIBEnv, link functions, score functions
  stein.py       truncated + normalized Stein estimator
  zoomsib.py     single-agent ZoomSIB-UCB (Algorithm 1)
  baselines.py   Random, LinUCB, ESTOR, GSTOR, IGP-UCB
  fed_stein.py   one-shot / gossip averaging of Stein estimators   ← novel
  coop_bins.py   cooperative sleeping-UCB over bins, graph topologies ← novel
  comms.py       interval / event-triggered / quantized protocols   ← novel
  safe.py        (Option A) safety filter
  ifca_sib.py    (Option B) clustered indices
experiments/     one script per figure, seeds fixed
results/         cached .npz + generated .pdf figures
docs/            this folder
slides/          pitch + final decks
papers/          the seven PDFs
```

---

## Risk register

| Risk | Mitigation |
|---|---|
| Federated Phase-1 proof stalls | Empirical E-A/E-B still stands; report as a conjecture with evidence |
| `T₀` from theory too large to simulate | Use the adaptive stopping rule (Dey et al. do this too) |
| Non-Gaussian contexts make `S(x)` messy | Stay Gaussian for the main results; one non-Gaussian robustness plot at most |
| Scope creep into robotics | Robot fleet is *one* motivating slide; no simulator on the critical path |
| Both extensions attempted, neither finished | Hard decision point on 29 Oct — pick one |
