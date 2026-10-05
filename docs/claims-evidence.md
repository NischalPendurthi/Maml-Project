# Claims and evidence: where the research value of Fed-ZoomSIB lies

*Branch `research/claims-evidence`. Each claim from our brainstorm is listed with the
experiment or proof that tests it and an honest verdict, including where the data contradicts
the claim. Proofs: [`docs/proofs/server.pdf`](proofs/server.pdf). Tables: `results/claims_e2*.md`.*

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
| 2.2 | In multi-index bandits Phase 1 becomes expensive | E25 | **Confirmed at large d** (11% at d = 100), with a real communication–accuracy trade-off |
| 3.1 | Quantisation / top-k / rand-k, measured cleanly | E26 | **Phase-1 compression never helps; top-k Phase-2 bins with error feedback saves 26–29% for free** |
| 3.2 | The regret–communication trade-off is a research path | E27 + §6 of the proofs | **Yes, but not via batching**: *when* to sync matters more than *how often* |
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

### 2.2 Multi-index bandits (E25, [fig25](../results/fig25_multiindex.png), [table](../results/claims_e25.md))

New code in `src/multiindex/`:
- **Model:** y = g(Bᵀx) + noise, with B ∈ R^{d×m}.
- **Phase 1:** second-order Stein (a d×d matrix); B̂ = its top-m eigenvectors.
- **Phase 2:** sleeping UCB on m-dimensional cubes of side 4·(NT)^{-1/(m+2)}.
- The constant 4 was calibrated once. With constant 1, an m = 2 grid has 10⁴ cubes, more than a
  run can visit.

**Estimator.** The subspace error decays like n^{-0.49} (bowl) and n^{-0.48} (mixed), the
expected n^{-1/2}.

**Collaboration still works** (network regret exponent in N, m = 2):

| setting | Fed-ZoomMIB | Phase-1 sharing only | single-index Fed-ZoomSIB on the same problem |
|---|---|---|---|
| bowl, m = 2 | **0.45** | 1.04 | 0.90 (4.1× more regret at N = 8) |
| mixed, m = 2 | **0.52** | 0.94 | 0.94 (5.2× more regret at N = 8) |

**Bonus: the μ\* = 0 case.** `mixed` with m = 1 is g(z) = cos 2z.
- It is even, so μ\* = E[g'] = 0, and first-order Stein (ZoomSIB) cannot find the direction:
  8 384 regret for one agent.
- Second-order Stein finds it: **1 653 regret, 5× less**.
- Dey et al. list "requires μ\* ≠ 0; can an alternative technique be developed?" as open.
- This is one link and no theory, but it is a lead worth showing Prof. Ghosh.

**Does Phase 1 stop being negligible?** Phase-1 share of all scalars (N = 8, m = 2):

| d | 10 | 20 | 50 | 100 |
|---|---|---|---|---|
| exact matrix pooling, d(d+1)/2 per agent | 0.20% | 0.61% | 3.2% | **11.4%** |
| projection averaging, d·m per agent | 0.11% | 0.21% | 0.48% | 0.97% |
| single-index (vector), for reference | 0.19% | 0.34% | 0.82% | 1.31% |

**There is a real communication–accuracy trade-off between Phase-1 methods**, which never
happens in the single-index model:
- **Projection averaging** sends 7× less than exact pooling at d = 50.
  - It costs nothing on `bowl` (large eigengap).
  - It costs **+22% regret on `mixed`** (small eigengap).
- **Federated power iteration** with 2 rounds fails at d = 50: subspace error 0.42–0.52 and
  +40–94% regret. 5 rounds match exact pooling. The number of rounds needed is set by the
  eigengap, as the theory predicts.

**Verdict.** In multi-index bandits Phase 1 is a genuine federated estimation problem: a
nonlinear target, cost growing like d², and an eigengap-dependent trade-off. This is where
Phase-1 communication research belongs.

---

## Point 3: compression and the regret–communication trade-off

### 3.1 Compression, measured cleanly (E26, [fig26](../results/fig26_compression.png), [table](../results/claims_e26.md))

N = 8, T = 10 000, one change at a time, 20 paired trials. Bits are counted on the wire.

| what is compressed | regret vs exact | total bits saved |
|---|---|---|
| Phase 1, 8-bit | same | +0.6% / −0.7% |
| Phase 1, 2-bit | +50% | **−10%** (more bits) |
| Phase 1, top-k / rand-k (25–50%) | +80% to +620% | **−17% to −148%** |
| Phase 2, 16-bit sums | same | +14–15% |
| Phase 2, 8-bit sums | +1–3% | +5–15% |
| **Phase 2, top-25% bins + error feedback** | **+0.2–0.4%** | **+26–29%** |
| Phase 2, top-25% bins, no error feedback | +1.6–3% | +44–46% |
| Phase 2, rand-50% bins | +0.3–10% | −9% to −19% |

1. **Compressing Phase 1 backfires.** A noisier frozen direction makes Phase 2 sync more and
   regret more, so total bits *rise*.
2. **Quantising Phase-2 values tops out around 15%.** Each bin message is (index, count, sum),
   and only the sum can be rounded; counts must stay exact.
3. **The lever is sending fewer bin messages.**
   - Top-k by "news ratio" with error feedback is free: unsent bins wait for a later sync.
   - Rand-k loses because the bins it skips keep firing the trigger.

### 3.2 The regret–communication frontier (E27, [fig27](../results/fig27_comm_tradeoff.png), [table](../results/claims_e27.md))

Same N and T, regret ÷ sync every round:

| schedule | sync rounds | quadratic | zigzag |
|---|---|---|---|
| every round | 9 880 | 1.00 | 1.00 |
| periodic every 100 | 99 | 1.45 | 1.37 |
| **event-triggered γ = 0.5** | **130–162** | **1.004** | **1.003** |
| event-triggered γ = 1 | 7–10 | 1.52 | 1.54 |
| geometric grid, 8 batches | 8 | 1.48 | 1.28 |
| minimax (Perchet) grid, 8 batches | 8 | 2.09 | 1.64 |

1. **When to sync matters far more than how often.**
   - Periodic sync with 99 rounds loses 37–45%.
   - The event trigger with 130 rounds loses 0.4%.
   - Data-driven timing is worth an order of magnitude in communication.
2. **Fixed batch schedules do not reach the optimum.** Even at 8 batches the minimax grid is at
   2.1× and the geometric grid at 1.3–1.5×. M\* is above 8 at every horizon (N·T = 20k–320k),
   against log log(NT) ≈ 2.3–2.5. The O(log log T) result for batched Lipschitz bandits does
   **not** transfer to our UCB agents:
   - between syncs, every agent re-explores the same new bins;
   - the context-driven (sleeping) arms prevent the elimination schedules those results rely on.
3. **The cliff between γ = 0.5 and γ = 1 is a mechanism effect.** A first pull into an empty bin
   fires the trigger only if 1 > γ, so for γ ≥ 1 newly found bins are not shared promptly.
   - Sharing *new bins* promptly is what matters.
   - A trigger that does this, but is lazier on known bins, could cut the ~130 syncs further.
     That is an open design question.

**Verdict on 3.2.** The trade-off is a real research path, in this form:
- *What is the minimum number of syncs for the optimal rate when arms are context-driven?*
- Both sides are open:
  - the current upper bound is 60–75× loose (claim 1.3);
  - naive batching fails (above).
- The proofs document (§6) states a heuristic lower bound and a conjecture. Neither is proved.

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

## What this means for the project

1. **The server single-index result is closed in rate** (Theorems 3 and 9).
   - Keep it as the base theorem.
   - Its open part is communication: the sync bound is 60–75× loose, and the optimal number of
     syncs with context-driven arms is unknown.
2. **The serverless result is the stronger paper.**
   - Prove Theorem 16 properly.
   - Attack the delay term: the measured cost is 60–150× below it and nearly flat in T.
   - Add the agreement/stopping question from Point 4.
3. **Phase-1 compression is a dead end for single-index** (E24, E26).
   - It becomes a real problem only for **multi-index**, where projection averaging and power
     iteration show an eigengap-dependent trade-off (E25).
4. **Leads to discuss with Prof. Ghosh:**
   - second-order Stein solves a μ\* = 0 instance that ZoomSIB cannot (E25);
   - the d-dependence remark in the proofs (Remark 10).

## Reproduce

```
python3 experiments/exp22_single_vs_network.py      # ~30 min
python3 experiments/exp23_server_vs_serverless_D.py # ~50 min
python3 experiments/exp24_phase1_share.py           # ~15 min
python3 experiments/exp25_multiindex.py           # ~20 min
python3 experiments/exp26_compression.py          # ~15 min
python3 experiments/exp27_comm_tradeoff.py        # ~35 min
python3 experiments/exp28_dec_explore_coupling.py # ~1 h (10 trials)
```

Every script also accepts `--quick`, which writes to `results/quick/` in a few minutes.
Results are cached per cell, so an interrupted run resumes where it stopped.
