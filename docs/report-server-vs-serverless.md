# Fed-ZoomSIB with and without a server — what to prove, which algorithm, and where the contribution is

*CS6007 project report. Covers experiments E6–E21 of this repository and proposes the next step.*

---

## 0. Summary

| Question | Answer |
|---|---|
| Which algorithm, **with a server**? | **Fed-ZoomSIB-SS**: exact sufficient-statistic pooling in Phase 1, event-triggered sufficient-statistic sync in Phase 2, **fixed Phase-1 length** |
| Which algorithm, **without a server**? | **Dec-ZoomSIB-Relay**: spanning-tree pooling in Phase 1, event-triggered *flooding* of bin tables in Phase 2, fixed Phase-1 length. If the graph changes over time, use flooding in Phase 1 as well |
| How close is serverless to server? | 3 % more regret at the **same** communication (E20); regret still grows like N^0.44–0.46 on well-connected graphs (E19) |
| What can be proved? | With a server: the optimal network rate `Õ(d²(NT)^{2/3})` with a matching lower bound. Without a server: the same rate **plus** an additive delay term `Õ(N·D·N_bins)`, where D is the graph diameter (§3, §4) |
| Which is harder to prove? | Server: Phase 1 is a corollary, Phase 2 is moderate work. Serverless: everything in the server proof plus delay bookkeeping (relay version), or spectral-gap analysis (consensus version, much harder) |
| Which is more publishable? | The server result alone is thin, because Phase 1 is "just averaging". Server + serverless together is a solid paper. **Multi-index** (§6) makes Phase 1 genuinely hard and is the strongest single contribution |
| Recommendation | Prove the server theorem first (it is the core of everything), add the relay-based serverless theorem as a second result, and scope the federated multi-index bandit as the headline if time allows (§7) |

---

## 1. The two settings

**Common model.** N agents. Each round every agent i sees K arms `x_{i,t,a} ~ p` and observes
`y = f(⟨x, θ*⟩) + η` for the arm it pulls. `θ*` (with `‖θ*‖₁ = 1`) and the link `f` are unknown
and shared. Network regret is `R_T(N) = Σ_i Σ_t [f(⟨x*_{i,t}, θ*⟩) − f(⟨x_{i,t}, θ*⟩)]`.

| | With a server (federated) | Without a server (decentralised) |
|---|---|---|
| Who talks to whom | every agent ↔ one coordinator (star) | neighbours on a connected graph G: diameter D, mixing matrix P with spectral gap 1 − λ |
| One communication round | upload + broadcast | one exchange along every edge |
| Code | `src/fed/` (engine `fed`) | `src/dec/` (engine `dec`) |
| Experiments | E6–E13 | E14–E21 |
| Trust | the server sees all statistics | no single party sees everything |

---

## 2. What the experiments say

All numbers are from this repository. `d = 10`, `K = 20`, `T = 10 000` rounds per agent. Unless
stated otherwise, comparisons use a fixed Phase-1 length, so that only communication differs.

### 2.1 Head to head (N = 16, quadratic link)

| | Server | Serverless (tree + event flooding) | Source |
|---|---|---|---|
| Regret ÷ best, 3 graphs × {iid, covariate shift} | **1.000** | 1.030 | E20 |
| Communication (torus, iid) | 56 836 scalars | 60 481 scalars | E20 |
| Regret growth in N (fixed pooled Phase 1) | N^0.43 | N^0.44 (complete) · N^0.46 (hypercube) · N^0.55 (ring) | E19 |
| At N = 32 | 8 888 | 9 413 (hypercube, +6 %) · 11 544 (ring, +30 %) | E19 |
| 30 % / 60 % / 90 % random link failures | n/a | +6 % / +9 % / +27 % (torus) | E18 |
| Directed links | n/a | +8 % | E18 |
| Independent agents (no communication) | ×4.87 | ×4.87 | E20 |

### 2.2 What matters, in order

1. **How Phase 1 ends matters more than how agents communicate.**
   - The single-agent adaptive stopping tolerance stops too early with N agents. At N = 16 it costs ×1.40 regret (E20). At N = 32 it doubles regret: 20 257 vs 8 888 (E19).
   - Even at the *same average* Phase-1 length, adaptive stopping is worse than a fixed length (≈ 9 700 vs ≈ 7 100 at T₀ ≈ 35, E14). A few trials stop very early, and those dominate the mean.
   - Without a server, the stop rule "freeze when *any* agent is stable" fires at the earliest of N stopping times and roughly doubles regret (E14).
   - **Every theorem below therefore uses a fixed, N-calibrated Phase-1 length**, which is also what works best in practice.
2. **Exactness beats sophistication.** Both phases are federated least squares (E10–E11). Sufficient statistics give the centralised answer in one round. Of the 14 FL methods tested:
   - none improves on that;
   - model averaging (one-shot FedAvg, distillation) is *biased* on the bin table;
   - drift-correcting methods (SCAFFOLD, FedDyn) need many rounds, and FedDyn's state goes stale when data arrive unevenly.
3. **Without a server, relaying beats mixing.**
   - Flooding (relaying exact records) depends only on the diameter. It is exact up to a delay, robust to link failures, and cheap when event-triggered.
   - Consensus and push-sum depend on the spectral gap, and cost about 2 000× more communication for the same regret (E15).
   - Chebyshev acceleration is excellent on a fixed graph (E14), but collapses under link failures, at 2–7× regret (E18), because it assumes a known, fixed P.
4. **Each family depends on a different graph quantity** (E16, at a fixed T₀).
   - Flooding's extra regret grows with the *diameter*: +1 % at D = 1, +5 % at D = 3–4, +12 % at D = 8, +15 % at D = 15.
   - Consensus depends on the *spectral gap*: best on expanders (+1 %), worst on a star (+15 %) even though the star's diameter is 2.
5. **The communication matrix matters only for mixing-based methods** (E17).
   - The best-constant Laplacian is best: on the star it halves consensus's extra regret (+15 % → +7 %).
   - Row-stochastic weights, which are not doubly stochastic, are biased on irregular graphs and are the worst on the star (+33 %).
   - Relay methods do not use P at all.

---

## 3. With a server: what can be proved

### 3.1 Algorithm (Fed-ZoomSIB-SS)

```
Phase 1 (rounds 1 … T₀, all agents):
    pull uniformly; keep (S_i(x), y) locally
    at round T₀: each agent sends  b_i = Σ_t φτ(y_t S_i(x_t))  and  n_i      (d + 1 numbers)
                 with τ set for the pooled size n = Σ n_i
    server:      θ̂₀ = normalise(Σ b_i / Σ n_i)   — exactly the centralised Stein estimator
    each agent sends max |⟨x, θ̂₀⟩| over its Phase-1 data; server sets W, broadcasts (θ̂₀, W)

Phase 2 (rounds T₀+1 … T):
    bins of width Δ on [−W, W]; agent i acts on (global table) + (own unsynced pulls)
    sleeping UCB over the bins its K arms fall into
    sync when some agent's unsynced count in a bin j exceeds γ · n_j^global:
        everyone uploads (bin, n, S) for touched bins; server merges and broadcasts
```

Config: `dict(engine="fed", phase1="exact", phase2="fl", phase2_kw=dict(method="suffstat", gamma=γ))`,
with a fixed Phase-1 length (in `src/dec` this is `phase1="server", phase2="server_event", freeze="fixed"`).

### 3.2 Assumptions

- **A1–A3 of Dey et al.** for every agent: sub-Gaussian contexts with known density, bounded link and noise, `f` Lipschitz with constant `L_{f'}`.
- **Shared θ\* and f.**
- **Identifiability.** Single agent: `μ* = E[f'(⟨X, θ*⟩)] > 0`. With covariate shift it is enough that the *network-weighted* `μ̄ = Σ n_i μ_i / Σ n_i > 0` (E10 found this; some agents may have μ_i < 0).

### 3.3 Results and their difficulty

**Lemma S1 (Phase 1 is exactly centralised).** `Σ b_i / Σ n_i` *is* the truncated Stein estimator on the pooled `N T₀` samples (an algebraic identity; tested to 2·10⁻¹⁶). Dey et al.'s Lemma B.1, restated at the pooled sample size, then gives

    ‖θ̂₀ − θ*‖₁ ≤ C_θ d √(log(2d/δ) / (N T₀))    with probability 1 − δ.

- *Difficulty: easy.* A corollary of the single-agent result.
- *Novelty: low,* except for the μ̄ > 0 relaxation, which is new and short.

**Lemma S2 (the freeze keeps the analysis valid).** θ̂₀ is frozen for every agent at once. Bin assignments are therefore predictable for every agent, and Remark 3.1's martingale argument applies to the pooled pull sequence.
- *Difficulty: easy.*

**Lemma S3 (event-triggered sync: staleness and communication).**
- *Staleness.* Between syncs, every agent's unsynced count in bin j is at most `γ n_j`, so the true pooled count is at most `(1 + Nγ) n_j`. Each agent's estimate averages at least `n_true / (1 + Nγ)` real samples, so the confidence width grows by at most `√(1 + Nγ)`. With `γ = γ₀/N` that is a constant factor.
- *Communication.* Each sync caused by bin j multiplies `n_j` by at least `1 + γ`, so bin j causes at most `log_{1+γ}(NT)` syncs. In total there are `O(N_bins · log(NT) / γ)` sync rounds.
- *Difficulty: moderate.* The argument mirrors DisLinUCB (Wang et al. 2020). The new parts are sleeping arms, where each agent's available set `B_{i,t}` is random and different per agent, and the N parallel pulls per round, which are bounded the same way as the stale counts.

**Lemma S4 (Phase-2 regret).** Feed the pooled pulls into Prop. 4.7 of Dey et al. (Phase 2 as a black-box sleeping bandit), using the inflated widths from S3:

    Reg₂ = Õ( √((1 + Nγ) · N_bins · N T) ).

- *Difficulty: moderate.* You must check that Prop. 4.7's "best available arm" comparator works per agent.

**Theorem S (network regret, optimal).** Take `Δ = (NT)^{-1/3}`, `N T₀ = Õ(d² (NT)^{2/3})` and `γ = γ₀/N`. Then

    R_T(N) = Õ( d² (NT)^{2/3} ),

using `O(N d)` scalars in Phase 1 and `O(N_bins log(NT))` sync rounds in Phase 2.

**Lower bound.** N agents with free communication are no stronger than a single learner making NT pulls in batches of N, and batching only makes learning harder. Dey et al.'s lower bound at horizon NT therefore gives `Ω((NT)^{2/3})`, and **Theorem S is optimal up to logs**.
- *Difficulty: easy* (a reduction).

**What the server theorem does *not* cover, and should say so:**
- adaptive stopping (the theorem uses a fixed T₀);
- the gap-dependent rates we measure, with exponents 0.43–0.6 below 2/3 (a gap-dependent bound would explain them);
- concept shift, where agents have different θ\*_i. There, sharing is harmful and every federated variant loses to independent agents (E12).

**Overall effort: moderate.**
- **Light parts:** S1, S2 and the lower bound, at about a page each.
- **Real work:** S3 and S4, the per-agent sleeping-arm availability combined with stale counts. Budget a few weeks of careful work with the advisor.

---

## 4. Without a server: what can be proved

### 4.1 Algorithm (Dec-ZoomSIB-Relay)

```
Phase 1:  agents pull uniformly for T₀ rounds (fixed, so no stop flag is needed)
          spanning-tree aggregation: sums go up a BFS tree to a root and the total comes back down
          (2·depth ≤ 2D rounds, 2(N−1)(d+1) scalars) → every agent holds the exact pooled θ̂₀
          W by max-consensus over D rounds → shared grid
Phase 2:  every agent stores the freshest copy it has heard of each agent's OWN bin table
          (n_kj, S_kj) and acts on their sum + its own new pulls
          an agent re-publishes its own table when its unpublished count in some bin
          exceeds γ × the count it currently sees; records are relayed one hop per round
```

Config: `dec_config(graph, "tree", {}, "flood", {"gamma": γ}, freeze="fixed", T0=T₀)`.
On time-varying graphs, replace `"tree"` with `"flood"`: Phase-1 records are relayed the same way.

### 4.2 Assumptions (in addition to §3.2)

- G is connected with diameter D. For time-varying graphs, B-connectivity: the union of any B consecutive graphs is connected, so information crosses in at most B·D rounds.
- Agents know N, T₀ and an upper bound on D.

### 4.3 Results and their difficulty

**Lemma D1 (Phase 1 is still exact).** Tree aggregation computes the same pooled sum as the server, so Lemma S1 holds verbatim. It needs 2·depth extra rounds, during which agents keep exploring; that costs an additive `O(N D)` regret, which is negligible. With flooding instead of a tree, the estimate is exact on data at most D rounds old, which is equivalent to running Phase 1 for T₀ − D rounds.
- *Difficulty: easy.*

**Lemma D2 (relay staleness).** At round t, agent i's table contains every pull that agent k had published by round `t − dist(i, k)`. Two kinds of pulls are missing: unpublished ones (at most γ·n_j per agent, by the trigger) and pulls still in transit (at most `N · D` per bin). The confidence argument of S3 therefore goes through with:
- a multiplicative factor `√(1 + Nγ)`, as before;
- an **additive delay term**, by the standard reduction for bandits with delayed feedback (Joulani et al. 2013): total regret grows by at most O(delay × number of arms), which here is `O(N · D · N_bins)`.

- *Difficulty: moderate.* It is the server proof plus delay bookkeeping. The new subtlety is that different agents hold different views at the same round.

**Theorem D (serverless network regret).** With the parameters of Theorem S,

    R_T(N) = Õ( d² (NT)^{2/3}  +  N · D · (NT)^{1/3} ),

using `O(N d)` scalars in Phase 1 and `O(|E| · N · N_bins · log(NT))` scalars in Phase 2 in the worst case. This **matches the server rate whenever `N · D ≲ (NT)^{1/3}`**, that is, on graphs whose diameter is small compared with `(NT)^{1/3} / N`. It explains E19: the hypercube (D = log N) stays within 6 % of the server at N = 32, while the ring (D = N/2) loses 30 %.

**Theorem D′ (consensus or push-sum version; optional, harder).** This is the variant with one gossip step per round and constant memory per agent. Estimates then carry a consensus error that decays like `λ^t`. The known analyses (Landgren et al. 2016; Martínez-Rubio et al. 2019, "DDUCB") give regret equal to the centralised rate plus a term in `1/√(1 − λ)` or `log(1/(1 − λ))`. Here those analyses must be combined with sleeping arms and with Phase 1, where agents end with *different* θ̂_i: their bins disagree by up to `L·‖θ̂_i − θ̂_j‖`, which adds a bias term.
- *Difficulty: hard.* Spectral arguments, per-agent bin mismatch, and consensus error, all at once.
- Experimentally it is no better than relaying (E15, E20) and costs about 2 000× more communication. **Not recommended as the main proof.** Its one advantage is memory: one table per agent, against N for flooding.

**Directed or time-varying graphs.**
- *Relay version:* needs only B-connectivity, giving D → B·D in Theorem D. That is a small change.
- *Push-sum version:* needs the Nedić–Olshevsky (2015) analysis. That is a significant change, and push-sum was *worse* in our experiments (E18).

### 4.4 Effort

| Piece | Server | Serverless (relay) | Serverless (consensus) |
|---|---|---|---|
| Phase-1 estimation | corollary | corollary + O(N D) | consensus error + per-agent mismatch (hard) |
| Freeze / grid | trivial | max-consensus, trivial | needs agreement or a mismatch bound |
| Phase-2 confidence | stale counts (moderate) | + delay term (moderate) | + spectral term (hard) |
| Communication bound | event counting (easy) | × \|E\| relays (easy) | per-round state (easy, but large) |
| Lower bound | reduction (easy) | same | same |
| **Overall** | **moderate** | **moderate+** (≈ server + 30 %) | **hard** |

---

## 5. Comparison: effort, applications, use, acceptance

| | **With a server** | **Without a server** |
|---|---|---|
| **Proof effort** | Moderate. Phase 1 is a corollary; the work is the Phase-2 sync analysis | Moderate+ with relaying (adds a delay term); hard with consensus |
| **Novelty of the theory** | Thin on its own: reviewers will say "Phase 1 is averaging, Phase 2 is known distributed UCB". The defensible new pieces are the sleeping/stale-statistics analysis, μ̄ > 0, and the negative result that standard FL is biased on the bin table | Higher: no decentralised single-index bandit exists, the diameter/gap dependence is a clean new statement, and the "relaying beats mixing" finding is useful |
| **Applications** | Cross-silo settings with a coordinator: hospitals sharing a recommendation policy, multi-region A/B testing, a cloud service learning from many client apps | No trusted coordinator or no backbone: sensor networks, robot or drone swarms, vehicular networks, peer-to-peer recommendation, privacy-sensitive consortia |
| **Practical cost** | Smallest: 57k scalars at N = 16 (E20) | Same with relay + event triggers (60k); per-agent memory O(N · N_bins) for flooding |
| **Robustness** | Single point of failure | Survives 60 % link failures within 9 %; works on directed graphs (E18) |
| **Experimental support** | Complete (E6–E13, E20) | Complete (E14–E21) |
| **Acceptance (rough, see note)** | Workshop high · TMLR ~50–60 % · AISTATS/UAI ~20–30 % · NeurIPS/ICML ~10–15 % | Together with the server result: TMLR ~60–70 % · AISTATS/UAI ~35–45 % · NeurIPS/ICML ~20–30 % · control/signal-processing venues (CDC, IEEE TSP), where decentralised bandit papers commonly appear: favourable |

*Note on acceptance.* These are rough judgments from base rates and from how reviewers treat
"composition" papers; they are not computed. Peer review is noisy. Two things move the odds
most: the rigour of the Phase-2 proof, and Prof. Ghosh's involvement (he wrote ZoomSIB and IFCA).

**Recommendation.** Write one paper with **two theorems**: the server result as Theorem 1 (the core) and the relay-based serverless result as Theorem 2, which is a moderate extension of the same proof. Our experiments already back both. The multi-index extension (§6) is the one that adds a genuinely new *estimation* problem, which is exactly the part the single-index server version lacks.

---

## 6. The multi-index extension (because Phase 1 is too easy)

### 6.1 Why Phase 1 is trivial now, and why multi-index changes that

In the single-index model the Phase-1 statistic is a **vector mean** `E[y S(x)] = μ* θ*`. A vector mean federates exactly in one message of d + 1 numbers, so there is nothing left to design or prove. E10 confirmed this: all 14 FL methods give the same θ̂ or a worse one.

In a **multi-index** model

    y = f(Bᵀx) + η,      B ∈ R^{d×m} with orthonormal columns,  f : R^m → R unknown,  m ≪ d,

two things change:

1. **The first-order Stein statistic is not enough.** `E[y S(x)] = B · E[∇f(Bᵀx)]` is a *single* vector in span(B), so it cannot identify an m-dimensional subspace.
2. **The second-order statistic is a matrix, and the target is its eigenspace.** Second-order Stein's identity (Yang, Balasubramanian, Wang & Liu, NeurIPS 2017) gives

       M := E[ y · T(x) ] = B · E[∇²f(Bᵀx)] · Bᵀ,      T(x) = S(x)S(x)ᵀ − ∇S(x),

   which for Gaussian contexts `N(0, s²I)` is `T(x) = (xxᵀ − s²I) / s⁴`. The subspace span(B) is the top-m eigenspace of M, provided `E[∇²f]` has rank m and a nonzero eigengap `g`.

The matrix mean M̂ still federates exactly, but now an exact upload costs `d(d+1)/2` numbers per agent instead of d + 1. The object the algorithm actually needs, the eigenspace, is a **nonlinear** function of M̂. So a real communication–accuracy trade-off appears, and the choice of federation method matters:

| Phase-1 federation for multi-index | Agent sends | Exact? | Communication | Analysis |
|---|---|---|---|---|
| Exact matrix pooling | upper triangle of `Σ φτ(y T(x))` | yes | d(d+1)/2 | matrix Bernstein + Davis–Kahan |
| One-shot projection averaging (Fan, Wang, Wang & Zhu, *Ann. Stat.* 2019) | local top-m eigenvectors (d·m) | no: bias when local n is small | d·m | known: matches the centralised rate once each agent's sample is large enough relative to the eigengap; below that a bias term appears (check their exact condition) |
| Federated power / orthogonal iteration | `M̂_i V` per round (d·m) | yes in the limit | d·m × O(log(1/ε)/g) rounds | standard; rounds depend on the eigengap |
| First-order + second-order mix | vector + sketch | yes | d + d·m | recovers directions second order misses (below) |

### 6.2 Algorithm sketch (Fed-ZoomMIB)

```
Phase 1:  uniform pulls for T₀ rounds
          federated estimation of M = E[y T(x)] (exact, projection-averaged, or power iteration)
          B̂ = top-m eigenvectors of M̂   (m known, or chosen by an eigenvalue threshold)
Phase 2:  project arms to z = B̂ᵀx ∈ R^m; grid [−W, W]^m into cubes of side Δ
          sleeping UCB over the cubes the arms fall into, with event-triggered sufficient-statistic
          sync of (n_cube, S_cube), as in Fed-ZoomSIB
```

### 6.3 What can be proved (targets)

1. **Matrix concentration.** Truncated second-order Stein, with heavier tails because T(x) is quadratic in x, should give `‖M̂ − M‖_op ≲ d · √(log(d/δ) / n)` up to constants and log factors. This rate is a target to verify, not a known result for this setting. *Moderate:* adapt Yang et al.'s truncation argument to the bandit's Phase-1 data.
2. **Subspace error.** By Davis–Kahan, `‖B̂B̂ᵀ − BBᵀ‖ ≤ 2‖M̂ − M‖ / g`. *Easy.* For one-shot projection averaging, add Fan et al.'s bias term. *Moderate,* and this is the new federated content.
3. **Cell assignment.** Projections move by at most `‖(B̂B̂ᵀ − BBᵀ)x‖ ≤ W' · subspace error`. Choose n so that this is at most Δ/2 and each arm lands in its own or an adjacent cube. *Easy.*
4. **Phase-2 regret.** There are `N_cubes ≈ (2W/Δ)^m` cubes. Regret is `Õ(√(N_cubes · N T)) + L · N T · Δ`. With `Δ = (NT)^{-1/(m+2)}` this gives `Õ((NT)^{(m+1)/(m+2)})`. That matches the `T^{(m+1)/(m+2)}` lower bound for Lipschitz bandits in dimension m (Kleinberg, Slivkins & Upfal 2008), with T replaced by NT. *Moderate:* reuse the server Phase-2 argument with m-dimensional cells.
5. **Phase-1 cost.** Accuracy Δ/2 needs pooled `n ≳ d² Δ^{-2} / g² = d² (NT)^{2/(m+2)} / g²`. That is below the Phase-2 term for every m ≥ 1, so

       R_T(N) = Õ( d² g^{-2} (NT)^{2/(m+2)} + (NT)^{(m+1)/(m+2)} ),

   which reduces to the single-index `Õ((NT)^{2/3})` at m = 1.
6. **Communication.** With exact pooling, Phase 1 costs `O(N d²)`. With projection averaging it costs `O(N d m)` and the bias of item 2. Phase 2 is as in Lemma S3, with N_cubes in place of N_bins.

**Why this is a better paper.** Phase 1 now has a real federated estimation problem: a nonlinear target, a communication/accuracy trade-off, and an eigengap-dependent number of rounds. The problem is listed as **open by Dey et al. (§6)**, and the federated version is unstudied. The decentralised version (§4) carries over: relaying exact matrix sums still works, and Theorem D's delay term is unchanged.

### 6.4 Risks, honestly

- **Identifiability.** If `E[∇²f]` has rank below m, second order misses directions. For example, with `f(z₁, z₂) = z₁ + z₂²` it misses z₁. The fix is to combine first- and second-order statistics, `M + v vᵀ`, which complicates the theory.
- **Small eigengap g.** The `g^{-2}` factor can dominate; it should be stated explicitly.
- **Curse of m.** Phase-2 regret `(NT)^{(m+1)/(m+2)}` approaches linear quickly, so the method is practical for m ≤ 3. Zooming (adaptive cells) instead of a fixed grid would replace m by a zooming dimension, but that is a harder proof.
- **Unknown m.** Choosing m by eigenvalue thresholding adds a model-selection step.
- **Scope.** The project's own roadmap marks multi-index as a stretch goal (knowledge-map node E4). It is a larger commitment than the single-index proofs.

### 6.5 Experiments needed before committing (about a week of coding in this repository)

1. **Environment.** `MultiIndexEnv`, with links such as `f(z) = −‖z − c‖² + 1` and `sin z₁ + z₂²`.
2. **Estimator.** A second-order Stein estimator, plus a check that the subspace error decays like `n^{-1/2}`.
3. **Phase 1.** As a `fl/`-style strategy with exact matrix, projection-averaging and power-iteration variants. Measure subspace error against communication.
4. **Phase 2.** m-dimensional cells, reusing the bin-table machinery with the cell index flattened.
5. **Benchmark.** A repeat of E6/E12/E20: regret against N, regret against communication, and server against serverless.

The question to answer first is whether the projection-averaging bias is visible at realistic n. If it is, the federated Phase 1 is a real contribution; if not, exact pooling is again optimal and the story collapses back to §3.

---

## 7. Recommended plan

| Option | Contents | Proof effort | Expected outcome |
|---|---|---|---|
| **A** (safe) | Theorem S (server) + experiments E6–E13 | moderate | workshop / TMLR; AISTATS possible |
| **B** (recommended) | A + Theorem D (relay serverless) + E14–E21 | moderate+ | solid AISTATS/UAI submission; TMLR strong |
| **C** (ambitious) | B for single-index, plus federated multi-index with §6 theorems and experiments | hard | strongest; realistic NeurIPS/ICML target if the multi-index Phase 1 shows a real trade-off |

Do **B first**: it is mostly done experimentally, and Theorem D reuses Theorem S. Run the §6.5
experiments in parallel, and decide on C only after seeing whether the multi-index Phase 1
gives a non-trivial federation trade-off.

**Algorithm choices, for reference**

| Setting | Phase 1 | Phase 2 | Phase-1 length | Avoid |
|---|---|---|---|---|
| Server | exact sufficient statistics | sufficient statistics, event-triggered (γ ≈ 0.5, or γ₀/N in theory) | fixed, N-calibrated | adaptive single-agent stop rule; model-averaging FL (biased); FedDyn under uneven participation |
| Serverless, static graph | spanning tree | event-triggered flooding | fixed | `any` stop rule; Chebyshev on unreliable links; one-hop sharing |
| Serverless, failing / time-varying links | flooding | event-triggered flooding | fixed | Chebyshev (2–7× worse); push-sum (worse in practice despite theory) |
| Serverless, memory-limited agents | running consensus, best-constant Laplacian weights | running consensus | fixed | row-stochastic or lazy weights on irregular graphs |

---

## References (beyond the README's list)

- Z. Yang, K. Balasubramanian, Z. Wang, H. Liu. *Learning Non-Gaussian Multi-Index Model via Second-Order Stein's Method.* NeurIPS 2017.
- J. Fan, D. Wang, K. Wang, Z. Zhu. *Distributed Estimation of Principal Eigenspaces.* Annals of Statistics, 2019.
- R. Kleinberg, A. Slivkins, E. Upfal. *Multi-Armed Bandits in Metric Spaces.* STOC 2008.
- P. Joulani, A. György, Cs. Szepesvári. *Online Learning under Delayed Feedback.* ICML 2013.
- P. Landgren, V. Srivastava, N. E. Leonard. *On Distributed Cooperative Decision-Making in Multiarmed Bandits.* ECC 2016.
- D. Martínez-Rubio, V. Kanade, P. Rebeschini. *Decentralized Cooperative Stochastic Bandits.* NeurIPS 2019.
- Y. Wang, J. Hu, X. Chen, L. Wang. *Distributed Bandit Learning: Near-Optimal Regret with Efficient Communication.* ICLR 2020.
- D. Kempe, A. Dobra, J. Gehrke. *Gossip-Based Computation of Aggregate Information.* FOCS 2003.
- A. Nedić, A. Olshevsky. *Distributed Optimization over Time-Varying Directed Graphs.* IEEE TAC, 2015.
- L. Xiao, S. Boyd. *Fast Linear Iterations for Distributed Averaging.* Systems & Control Letters, 2004.
- K. Scaman et al. *Optimal Algorithms for Smooth and Strongly Convex Distributed Optimization in Networks.* ICML 2017.
