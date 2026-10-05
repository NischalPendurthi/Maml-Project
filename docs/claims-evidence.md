# Paper A (Dec-SIB): claims and evidence for decentralised single-index bandits

*Branch `Dec-SIB`. Each claim behind Paper A is listed with the experiment or proof that tests
it and an honest verdict, including where the data contradicts the claim. Proofs:
[`docs/proofs/server.pdf`](proofs/server.pdf). Tables: `results/claims_e2*.md`.*

*Paper A's story:* the first single-index bandit over a network. It is optimal with a server
(the base theorem), and we characterise what the graph costs without one: a delay term to
tighten, plus agreement at the end of exploration.

*Not on this branch:* the multi-index extension (E25, Paper B), and the compression and batching
studies (E26, E27). They live on branch `research/claims-evidence`.
Claims keep their numbering from our brainstorm, so the list jumps from 2.1 to 4.

**Common setup** (unless stated):
- d = 10, K = 20, σ = 0.1, unit index variance.
- **Fixed** Phase-1 length, with pooled size 960 at N·T = 160k, scaled ∝ (NT)^{2/3}.
- Event-triggered Phase 2 with γ = 0.5.
- Bin width Δ = (NT)^{-1/3}.
- Paired trials, so every configuration sees the same instances and contexts.
- Results are mean ± 95% CI.

| # | Claim | Evidence | Verdict |
|---|---|---|---|
| 1.1 | With a server, N agents × T rounds ≡ one agent × N·T rounds | E22 | **Confirmed** |
| 1.2 | …and this is provably the best possible | Thm 3 + Thm 9 | **Proved** (rate in N, T) |
| 1.3 | Event-triggered sync reaches the rate with O(log NT) syncs | Thm 12 + E22b | **Confirmed**, but the bound is 60–75× loose |
| 1.4 | Without a server you pay an extra N·D·(NT)^{1/3} | Thm 16 (sketch) + E23 | **Bound holds but looks loose**; the real cost is far smaller |
| 2.1 | Phase 1 is a negligible share of communication; compressing it buys nothing | Prop 15 + E24 | **Confirmed** |
| 4 | Without a server, exploration length and communication are coupled | E28 | **Partly**: the coupling is through *agreement*, not through the best length |

---

## Point 1: the server setting

### 1.1 One agent at N·T vs N agents at T (E22, [fig22](../results/fig22_single_vs_network.png), [table](../results/claims_e22.md))

We fix the total budget at N·T = 160 000 pulls, with the same pooled exploration and the same
bin width for every N.

| N | quadratic: ratio to 1 agent (event-triggered) | zigzag | independent agents (quadratic / zigzag) |
|---|---|---|---|
| 2 | 1.04 | 0.99 | 2.6× / 2.3× |
| 4 | 1.10 | 1.02 | 2.9× / 2.8× |
| 8 | 1.02 | 1.01 | 3.8× / 3.3× |
| 16 | 1.10 | 1.05 | 5.1× / 4.6× |

- The regret curves against total pulls lie on top of each other.
- N synced agents are within 0–10% of the single agent. Most of those gaps are inside the CI.
- None of them beats the single agent, which matches the lower bound.
- Independent agents are 2.3–5.1× worse. So collaboration is worth exactly the extra data, and
  no more.

### 1.2 Proof (docs/proofs/server.pdf, §2–3)

- **Theorem 3 (lower bound by simulation).** Any N-agent algorithm, even one that shares
  everything every round, can be simulated by one agent over N·T rounds that holds back
  same-round feedback. So its worst-case regret is at least Ω((NT)^{2/3}) (Dey et al. Thm 5.1
  at horizon NT). This also covers every serverless algorithm.
- **Theorem 9 (upper bound).** Fed-ZoomSIB-SS achieves Õ(d^{2/3}(NT)^{2/3}) for N ≤ √T. The
  ingredients are:
  - exact pooling (Lemma 5);
  - a confidence bound for stale, agent-specific tables (Lemma 6);
  - a per-pull regret bound valid for any sleeping pattern (Lemma 7);
  - a stale-count lemma from the trigger (Lemma 8).
- **Caveat to check with the advisor (Remark 10).** The d-exponent here differs from Dey et al.'s
  d². The N, T dependence doesn't depend on this.

**So what.** The server setting's regret rate is *closed*: matching upper and lower bounds,
with nothing left to improve in N or T. Any contribution in the server setting has to be about
communication.

### 1.3 Communication (Theorem 12; E22b, [fig22b](../results/fig22b_sync_rounds.png))

N = 8, event-triggered sync:

| N·T | measured syncs | Thm 12 bound | per-round sync | busiest bin's syncs | per-bin bound |
|---|---|---|---|---|---|
| 10k | 61 | 3 625 | 1 130 | 2.9 | 23.7 |
| 80k | 130 | 8 806 | 9 880 | 3.2 | 28.8 |
| 320k | 213 | 15 627 | 39 880 | 3.2 | 32.3 |

- Sync count grows slowly (about logarithmically), while per-round sync grows linearly. The
  rate in Theorem 12 holds.
- The bound is **60–75× loose**. It assumes every bin is pulled heavily, but sleeping UCB pulls
  only a few near-optimal bins, and the busiest bin triggers just ~3 syncs.
- **A tight, gap-dependent communication bound is open.** That's a concrete research target.

### 1.4 The cost of no server (E23, [fig23](../results/fig23_server_vs_serverless.png), [table](../results/claims_e23.md))

Setup: N = 16, with the same engine, seeds, T0 and γ for both versions.

| graph | D | excess regret, quadratic | excess % | bound term N·D·N_bins |
|---|---|---|---|---|
| complete | 1 | 106 ± 12 | +1.5% | 6 246 |
| expander | 3 | 238 ± 16 | +3.4% | 18 739 |
| hypercube / torus | 4 | 262 / 274 | +3.8% / +4.0% | 24 986 |
| ring | 8 | 527 ± 26 | +7.6% | 49 971 |
| path | 15 | 630 ± 31 | +9.1% | 93 696 |

- **The cost grows with D, but sublinearly** (roughly D^0.65 here), from +1.5% to +9%.
- **The bound term overstates it 60–150×.**
- **The excess is nearly flat in T.** The log-log slope is 0.13–0.14 against the predicted
  0.33, so the relative cost *falls*, from +11% to +4.5% on the ring as N·T goes 40k → 640k.
- **Reading.** The additive N·D·N_bins in Theorem 16 is a valid upper bound but very likely not
  the truth. The diameter seems to cost only in Phase-1 delay and first visits to bins.
- **Open question.** Prove a tighter delay term, or a lower bound showing what is necessary.
  This is the most concrete theory question in the serverless direction.
- Communication: relay uses 15–20% *fewer* scalars than the server here, because the server's
  broadcast goes to all N agents.

---

## Point 2: Phase-1 communication

### 2.1 Phase 1 is negligible (Prop 15; E24, [fig24](../results/fig24_phase1_share.png), [table](../results/claims_e24.md))

**Phase-1 share of all scalars** (N = 16, N·T = 160k):

| d | 5 | 10 | 20 | 50 | 100 | 200 |
|---|---|---|---|---|---|---|
| server | 0.10% | 0.17% | 0.28% | 0.63% | 0.81% | 1.37% |
| serverless (ring) | 0.26% | 0.33% | 0.43% | 0.75% | 0.97% | 1.59% |

- The share also **shrinks with the horizon**: at d = 10 it falls from 0.79% at N·T = 10k to
  0.08% at 640k. This matches Proposition 15's O(d / (NT)^{1/3}).

**Quantising the Phase-1 upload:**
- **Direct saving:** at most **0.06% (d = 10) to 0.38% (d = 100)** of total bits, even at
  2 bits.
- **Regret:** +1–3% at 4 bits, +37–50% at 2 bits. Indirect changes in Phase-2 traffic are of
  the same order as the direct saving, and noise.

**Verdict.** Phase-1 compression cannot matter for the single-index model, and a rate argument
backs this. Communication work belongs in Phase 2.

---

## Point 4: serverless exploration–communication coupling (E28, [fig28](../results/fig28_dec_coupling.png), [fig28b](../results/fig28b_stop_rules.png), [table](../results/claims_e28.md))

Setup: N = 16, Phase 2 fixed (event flooding). We sweep T0 ∈ {15, 30, 60, 120, 240} for 5
Phase-1 methods on 5 graphs, with 10 paired trials.

**(a) Does the best exploration length depend on the graph?** Barely.
- T0\* = 60 (the server's) for every method on every graph.
- The one exception is 1-step consensus on the path, where T0\* = 120.
- On this ×2 grid, the claim that "the optimal length is a function of D" is **not supported**.
  A finer grid might find small shifts.

**(b) What does the graph cost, then?** *Agreement.* Regret ÷ best server at T0\*:

| graph (D) | tree (exact) | flooding | consensus 1 step | consensus 5 steps | consensus 1 + one agreement pass |
|---|---|---|---|---|---|
| hypercube (4) | 1.04 | 1.06 | 1.07 | 1.04 | 1.04 |
| ring (8) | 1.08 | 1.11 | **1.25** | 1.11 | 1.08 |
| path (15) | 1.09 | 1.15 | **1.34** | 1.16 | 1.09 |

- Regret grows steeply once the frozen estimates disagree by more than about 10⁻² (fig28,
  panel D).
- **One flooding pass at the freeze, so that all agents adopt the same θ̂, removes the whole
  penalty.** The pass itself adds only about 2.8k scalars on the ring (24.2k against 21.4k for
  consensus alone), and the total is about 14% of flooding's Phase-1 traffic.
- Tree pooling is still cheapest: about 600 scalars, exact.

**(c) Adaptive stopping on graphs is the weak point.** Network regret, with fixed T0\* for
comparison:

| graph | stop when *any* agent is stable | stop when *all* are | fixed T0\* |
|---|---|---|---|
| ring, flooding | 10 882 ± 3 371 | 7 743 | 7 617 |
| ring, consensus 1 | 18 523 ± 7 366 | 8 740 | 8 572 |
| path, consensus 1 | 16 761 ± 7 189 | 9 518 | 9 150 |

- "Any" is 1.4–2.2× worse and highly variable.
- The *server's* adaptive rule (9 487, against 6 848 fixed) is also bad.
- **Caveat:** the engine freezes instantly under "all". A real network needs at least D more
  rounds to learn that everyone is stable, so "all" is optimistic here.

**Verdict on 4.** The coupling is real, but it is about agents freezing the *same* estimate,
not about how long they explore. The research question this supports is:

> design a decentralised stopping rule that ends with agreement, with a regret guarantee.

- Both naive rules fail ("any" in regret, "all" in its unmodelled delay).
- A fixed length plus one agreement pass works but needs T0 known in advance.

---

## What this means for Paper A

1. **Theorem 1 of the paper: the server result** (Theorems 3 and 9, E22).
   - It is closed in rate: one agent with N·T pulls, and no better.
   - Present it as the base case, not the contribution.
2. **Main contribution: the serverless (relay) theorem with a tight delay term** (Theorem 16, E23).
   - The proved additive N·D·N_bins is 60–150× above the measured cost, and the cost is nearly
     flat in T.
   - Target: show that only Phase-1 delay and first visits to bins pay the diameter. Ideally
     add a lower bound in D.
3. **Agreement at the freeze** (E28).
   - Frozen estimates that disagree cost 25–34% on the ring and path.
   - One agreement pass removes it. Formalise this as a lemma.
   - Stopping rules that end in agreement, with a guarantee, are the open follow-up.
4. **Communication is all in Phase 2** (Proposition 15, E24).
   - Phase 1 is under 2% of traffic, so the analysis should spend its effort on Phase-2 syncs.
5. **To check with Prof. Ghosh:** the d-dependence in Remark 10 of the proofs.

## Reproduce

```
python3 experiments/exp22_single_vs_network.py      # ~30 min
python3 experiments/exp23_server_vs_serverless_D.py # ~50 min
python3 experiments/exp24_phase1_share.py           # ~15 min
python3 experiments/exp28_dec_explore_coupling.py # ~1 h (10 trials)
```

Every script also accepts `--quick`, which writes to `results/quick/` in a few minutes.
Results are cached per cell, so an interrupted run resumes where it stopped.
