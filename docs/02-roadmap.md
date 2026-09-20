# CS6007 Project Roadmap — Fed-ZoomSIB

**Pitch:** 28 Sept 2026 · **Final presentation:** early Nov 2026

Read [01-literature-and-problem.md](01-literature-and-problem.md) first for the papers and
the formal problem. This document answers two questions: **what is the baseline**, and
**what exactly are we improving on top of it**.

---

## Status

| Phase | Content | State |
|---|---|---|
| 0 | Project pitch | deck built, needs names/roll numbers |
| **1** | **Single-agent baseline + reproduction** | **complete — see Part A** |
| 2 | Federated Phase 1 (one-shot Stein averaging) | not started |
| 3 | Cooperative Phase 2 (sleeping UCB over a graph) | not started |
| 4 | Communication efficiency | not started |
| 5 | One extension: safety *or* clustered indices | not started |
| 6 | Final deck + report | not started |

---

# Part A — The baseline

## A.1 What "the baseline" means here

The baseline is the **complete single-agent problem**: one learner, no communication, no
safety constraint, one shared unknown index `θ*` and one shared unknown link `f`. Every
algorithm in it already exists in the literature. Nothing in Part A is a contribution —
its entire job is to be a *trustworthy measuring stick*, because every claim we will make
later has the form "collaboration buys you X", and X is measured against these curves.

## A.2 What is implemented

| Module | Contents | Source |
|---|---|---|
| [src/envs.py](../src/envs.py) | `SIBEnv`, four link functions, score function `S(x)` | Dey et al. §2, §6 |
| [src/stein.py](../src/stein.py) | truncated + ℓ1-normalised Stein estimator | Dey et al. §2.2, Eq. 1 |
| [src/zoomsib.py](../src/zoomsib.py) | `ZoomSIBUCB` (Algorithm 1) + oracle-θ ablation | Dey et al. §3 |
| [src/baselines.py](../src/baselines.py) | `RandomPolicy`, `LinUCB`, `ESTOR`, `GSTOR`, `IGPUCB` | see below |
| [src/runner.py](../src/runner.py) | parallel trial harness, CI helper, log-log slope fit | — |

Baseline provenance: **LinUCB** = Abbasi-Yadkori et al. 2011; **ESTOR/GSTOR** = Kang et al.
ICLR 2026 (our reimplementation — no reference code is public, so exploration schedules use
the rates their analysis prescribes, `O(√T)` and `O(T^{3/4})`, with constants exposed as
arguments); **IGP-UCB** = Chowdhury & Gopalan ICML 2017.

## A.3 What the baseline establishes

See [03-phase1-results.md](03-phase1-results.md) for the figures, tables and the two
setup decisions that materially affect what the benchmark measures.

The four results that matter downstream:

1. **The Stein estimator converges at exactly `n^{-1/2}`** (fitted exponents −0.496 to
   −0.501 across `d ∈ {5,10,20,40}`). This is the single most important number in Part A:
   the federated claim is that `N` agents reach the same accuracy from `n/N` samples each,
   and that claim is only measurable against a verified single-agent rate.
2. **Exploiting the single-index structure is worth a lot.** ZoomSIB-UCB beats GSTOR,
   LinUCB and IGP-UCB on every non-monotone link.
3. **Phase 1 dominates the regret at simulable horizons.** Handing ZoomSIB-UCB the true
   `θ*` cuts regret by 2.3×–5.3×. So *direction estimation, not binned exploration, is the
   thing worth attacking* — which is exactly what federation attacks.
4. **The `d`-dependence lives entirely in Phase 1**, and it is large. At `d = 80` the
   adaptive rule spends **36% of the entire horizon** estimating `θ*` (`T₀ = 3612` of
   10 000 rounds), against 1.1% at `d = 5`. That single number is the strongest motivation
   available for one-shot Stein averaging: it is the cost a factor-`N` speedup would remove,
   for one message of `d` numbers.

## A.4 What the baseline deliberately does *not* do

This list is the specification for Part B.

| Baseline behaviour | Why it is a limitation |
|---|---|
| One learner; no notion of a second agent | the course is Multi-Agent ML; no collaboration is measured |
| `θ̂₀` estimated from one agent's `T₀` samples | the estimator is a sample mean — pooling it is free and unused |
| Per-bin statistics `(n_j, S_j)` kept privately | two scalars per bin; trivially shareable, currently not shared |
| No communication model at all | no graph, no interval `C`, no byte budget, no spectral gap |
| No safety constraint | every arm is playable |
| One global `θ*` shared by assumption | no heterogeneity, so no negative-transfer question |

---

# Part B — The improvements

Each improvement below is stated as an explicit delta: what the baseline does now, what we
change, what we must code, and how we will know whether it worked.

## B.1 Improvement 1 — Federate Phase 1 by one-shot Stein averaging ★ protect this one

> **Baseline:** agent estimates `θ̂₀` from its own `T₀` samples; error `≍ C·d/√T₀`.
> **Improvement:** `N` agents each collect `T₀/N` samples, average their local Stein
> estimators **once**, and all adopt the result.

**Why it should work, exactly.** The Stein estimator is `(1/n)Σ φ_τ(yᵢS(xᵢ))` — an
average. Averaging `N` local averages of equal size is *algebraically identical* to the
centralized estimator on the pooled data. Not an approximation, not a consensus iteration:
one broadcast of `d` numbers per agent. Almost no other bandit primitive has this property.

**To code** — `src/fed_stein.py`:
```
theta_i  = truncated_stein(S_i, y_i, tau)      # local, from T0/N rounds
theta_bar= (1/N) * sum_i theta_i               # one broadcast (or gossip with P)
theta_0  = normalize_l1(theta_bar)             # normalise AFTER averaging
```
Note the ordering: average the **unnormalised** estimators, then normalise. Normalising
first would average `N` unit-ℓ1 vectors and throw away the relative signal strengths.

**How we measure it.**
- *E-A (headline).* Fix a target accuracy `ε`; measure per-agent rounds `T₀(N)` needed to
  reach it for `N ∈ {1,2,4,8,16,32}`. Expect `T₀ ∝ 1/N`; **plot `N·T₀(N)` vs `N` and look
  for a flat line.** Baseline reference: the `n^{-1/2}` curve from Part A.
- *E-B.* Sweep `d ∈ {5,10,20,40}` at fixed `N`. The gain should *grow* with `d`, because
  Part A showed the `d`-dependence is concentrated in Phase 1.

**Theory task T-A.** Prove `‖θ̄ − μ*θ*‖₁ ≤ C_θ d √(log(2d/δ)/(Nn))` w.h.p., then push it
through the normalisation step of Dey et al. Lemma 2.1. Independent sub-Gaussian averages
plus a union bound — tractable, and it is the theorem slide of the final deck.

## B.2 Improvement 2 — Cooperative Phase 2 over a communication graph

> **Baseline:** each agent runs its own sleeping-UCB over `O(T^{1/3})` bins.
> **Improvement:** agents share the per-bin sufficient statistics `(n_j, S_j)` over a
> graph `G` with communication matrix `P`.

**Why it is tractable.** Dey et al. **Proposition 4.7** is a modular reduction: *any*
bandit algorithm for `N` bins with stochastic availability can be substituted into Phase 2,
and the regret bound follows. A cooperative sleeping bandit is exactly such an algorithm,
so we cite a distributed-MAB bound rather than proving one from scratch.

Unlike B.1 this pooling is **statistical, not exact** — which is the point. We expect the
two phases to benefit by different amounts, and quantifying that asymmetry is the project's
main scientific question.

**To code** — `src/coop_bins.py`: centralized pooling (upper-bound reference), gossip /
consensus with `P` over complete / ring / star / Erdős–Rényi graphs, and independent
learners (lower-bound reference).

**Measure.** Network and per-agent regret vs `T` for `N ∈ {1,4,8,16}`; regret against
spectral gap `1 − |λ₂|` across topologies (Amani & Thrampoulidis predict an additive
penalty — confirming that in a *nonlinear* setting is a real result).

## B.3 Improvement 3 — Communication efficiency

> **Baseline:** no communication exists. **Improvement:** make it as rare as possible.

Phase 1 already costs exactly **one** message. The question is Phase 2.

**To code** — `src/comms.py`: periodic (`C ∈ {1,10,100,1000,∞}`), **event-triggered**
(broadcast bin `j` only when `n_j` grows by a factor `(1+γ)` — expect `O(N_bins log T)`
messages instead of `O(T)`), and quantized `(n_j, S_j)`.

**Headline metric: regret per transmitted byte**, not regret vs `T`. That reframing is
what makes this a multi-agent-learning result rather than a bandits result.

**Thesis to test:** *most of the collaborative gain in a single-index bandit is purchasable
with `O(1)` communication, because the expensive part — learning the direction — is a
single average.*

## B.4 Improvement 4 — pick exactly ONE (decide ~29 Oct)

**Option A — Safety** (`src/safe.py`, lower risk). Safety feedback
`z_{i,t} = h(⟨x, μ*⟩) + ζ`. Second Stein estimator for `μ*`, pessimistic per-bin LCB,
restrict Phase-2 UCB to safe bins, keep a known-safe fallback arm. Start with linear `h`
(= Safe-DLUCB, known to work), then unknown `h` (new). Metrics: violation rate, regret vs
the *safe* optimum.

**Option B — Clustered indices** (`src/ifca_sib.py`, higher ceiling). Agents have
heterogeneous `θ*_i` drawn from `M` unknown clusters. Naive averaging now causes **negative
transfer**. IFCA alternation: each agent joins the cluster whose centre best explains its
local Stein statistic; each cluster averages its members. Sweep cluster separation.

**Recommendation: Option B** if B.2 finishes on time — it is Prof. Ghosh's own IFCA applied
to his own ZoomSIB, and the negative-transfer plot is the most compelling single figure
available to us. Fall back to A if B.2 slips.

---

## Summary: baseline → improvement

| Component | Baseline (Part A, done) | Improvement (Part B) | Expected effect |
|---|---|---|---|
| Direction estimate | one agent, `T₀` samples | **one-shot average of `N` local Stein estimators** | same accuracy from `T₀/N` rounds each; **exact** pooling, 1 message |
| Bin statistics | private `(n_j, S_j)` | shared over graph `G` | statistical pooling; gain limited by spectral gap |
| Communication | none | interval / event-triggered / quantized | measure regret **per byte** |
| Safety | none | pessimistic LCB over bins from a 2nd Stein estimator | low violation rate at modest regret cost |
| Heterogeneity | one global `θ*` | `M` unknown clusters, IFCA-style | avoid negative transfer |

---

## Timeline

| Window | Work |
|---|---|
| ~~to 28 Sep~~ | ~~pitch~~ · **Part A complete ahead of schedule** |
| 29 Sep – 12 Oct | **B.1** federated Stein averaging + E-A/E-B + theory task T-A |
| 13 – 22 Oct | **B.2** cooperative Phase 2, graph topologies |
| 23 – 29 Oct | **B.3** communication ablations |
| 30 Oct – 5 Nov | **B.4** one extension |
| 5 – 12 Nov | final deck + report, ≥20 seeds with CIs on every plot |

---

## Risk register

| Risk | Mitigation |
|---|---|
| Federated Phase-1 proof stalls | E-A/E-B still stand; report as a conjecture with evidence |
| Theoretical `T₀` too large to simulate | already handled — adaptive stopping, validated in Part A |
| Phase-2 cooperative gain turns out small | that is itself the finding, and B.3 makes it a *positive* result about cheap communication |
| Scope creep into robotics | the robot fleet is one motivating slide; no simulator on the critical path |
| Both extensions attempted, neither finished | hard decision point 29 Oct — pick one |
