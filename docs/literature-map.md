<!--
Saved 2026-10-06 on branch Dec-SIB (Paper A).
Source: output of an external literature-search assistant, run with the search prompt we drafted
for Paper A. Stored as received, for later questions. Not yet verified by us: check citations,
quoted theorems and constants against the papers before using them in the paper.
-->

# Decentralised Single-Index Contextual Bandits: Literature Map for Dec-ZoomSIB-Relay (2015–2026)

No published paper or preprint we found studies multi-agent, federated or decentralised single-index (or unknown-link semiparametric) bandits, so the core setting of Dec-ZoomSIB-Relay looks open as of October 2026. However, the single-agent single-index bandit literature is moving fast (four new arXiv preprints in 2026 alone), so scooping risk is real on a months-long horizon. On the technical side, the strongest evidence for why your additive O(N·D·N_bins) term is loose comes from three sources: the "regret of delay" decomposition in DLUCB (Amani & Thrampoulidis, AAAI 2021), the Joulani–György–Szepesvári additive-delay reduction for stochastic bandits, and two delayed Lipschitz/zooming bandit papers: Liu, Kang & Lee (ICLR 2026, arXiv:2510.00309) and Liu, Chen & Huang (arXiv:2608.15036). In all three, the delay penalty multiplies only the *number of effectively-explored arms* (governed by a zooming/near-optimality dimension or a potential-function count), not the full discretisation size.

## TL;DR

- **Scooping risk: low today, rising.** Every single-index bandit paper found (Kang et al. ICLR 2026; Dey–Bhore–Ghosh 2026; Ma & Cai 2025; Arya & Song 2025; Arya–Bhattacharjee–Sriperumbudur 2026; Liu–Kang–Lee Sep 2026; Arya & Ong Sep 2026) is single-agent or batched. The only multi-agent work with flexible links is kernel/RKHS or "non-linear" federated optimisation, and none of it uses a Stein index estimator, a non-monotone link, or a graph.
- **Your delay term is loose because it charges N·D stale samples to every bin.** DLUCB-style and Joulani-style analyses charge delay only to "bad" (agent, round) pairs, where stale information changes the confidence width by more than a constant. That gives an additive term of roughly S·(effective dimension)·log(NT). For bins it becomes Σ_b min(N·D·Δ_b, log T/Δ_b), which is nearly flat in T and grows with the number of near-optimal bins (the zooming dimension), not with N_bins.
- **Read first:** Amani & Thrampoulidis (DLUCB); Dubey & Pentland (message passing with delay, the LOCAL protocol, and a graph-dependent lower bound); Joulani et al. 2013; the delayed Lipschitz bandit papers by Liu–Kang–Lee (ICLR 2026, arXiv:2510.00309) and Liu–Chen–Huang (arXiv:2608.15036); and Dey–Bhore–Ghosh 2026 (your base).

## Scooping-Risk Section (read first)

**⚠️ SCOOPING CHECK RESULT: No direct scoop found.** I ran targeted searches for:
- federated, distributed or decentralised single-index bandits;
- federated GLM bandits with unknown link;
- multi-agent semiparametric or partially linear bandits;
- decentralised Stein-estimator bandits;
- follow-ups by Dey, Bhore or Ghosh.

All of them returned only single-agent work. This is a negative search result, not proof of absence.

**Closest single-agent single-index papers (must cite; monitor for multi-agent follow-ups):**

1. **Dey, Bhore & Ghosh (2026), "Optimal Regret for Single Index Bandits."** arXiv:2605.09454 (v1 10 May 2026, v3 Aug 2026). https://arxiv.org/abs/2605.09454
   - **Setting:** single agent, K i.i.d. contexts per round, y = f(xᵀθ*) + η. The link f is bounded and Lipschitz, possibly non-monotone. Identifiability uses ‖θ*‖₁ = 1 and μ* = E[f′(Xᵀθ*)] > 0.
   - **Result:** ZoomSIB-UCB achieves Õ(T^{2/3}). There is a matching Ω̃(T^{2/3}) minimax lower bound, built from plateaued bumps of height ~T^{−1/3} and a reduction to a T^{1/3}-armed bandit with Bretagnolle–Huber.
   - **Technique:** a normalised Stein estimator, then N ~ T^{1/3} bins on the index line, then sleeping UCB (only a random subset of bins is available each round). The authors say explicitly that the "zooming" is "a one-shot reduction from a d-dimensional arm space to a uniform grid on ℝ", i.e., not adaptive zooming.
   - **Graph:** none.
   - **Scooping risk: highest of any group.** This is your base, and the authors (IIT Bombay) are natural candidates to write the multi-agent extension. Ghosh has prior distributed/federated learning work. His homepage lists a Jan 2026 grant titled "Competitive Markets: A Multi-Agent Bandits Viewpoint", with no matching paper yet.
   - **Idea to borrow:** their lower-bound construction is one-dimensional. You can lift it to N agents × T rounds to show Ω((NT)^{2/3}) is unavoidable even with a server, which makes your centralised term tight.

2. **Kang, Liu, Yi, Lyu, Zhang, Zhou & Li (2025/ICLR 2026), "Single Index Bandits: Generalized Linear Contextual Bandits with Unknown Reward Functions."** arXiv:2506.12751. https://arxiv.org/abs/2506.12751
   - **Setting:** single agent. STOR/ESTOR achieve Õ(√T) for monotone f. GSTOR handles general f (Gaussian design, kernel regression for f) and gets Õ(T^{3/4}). There is also a sparse high-dimensional extension.
   - **Technique:** a truncated Stein-identity estimator of θ* (a sample mean of y·S(x)), building on Yang, Balasubramanian & Liu-style thresholded score estimators.
   - **Scooping risk:** moderate. The group (Kang, Li, Lee) has already produced a follow-up (below), which suggests an active pipeline.
   - **Idea to borrow:** because the Stein estimator is a *sample mean*, it is exactly a sum-statistic. You can pool it without bias using any exact-sum protocol (your spanning tree) or push-sum. State this as a lemma.

3. **Liu, Kang & Lee (Sep 2026), "Low-Rank Single-Index Bandits with Unknown Links: From Matrices to Tensors."** arXiv:2609.33025. Single-agent, monotone link, T-ESTOR; square-root regret with a matching monotone lower bound. Low risk, but it shows the Kang group is extending SIBs structurally.

4. **Ma & Cai (2025), "Nonparametric Bandits with Single-Index Rewards: Optimality and Adaptivity."** arXiv:2512.24669.
   - Single-agent, per-arm single-index regression (maximum rank correlation + local polynomial).
   - Minimax-optimal regret independent of d, an impossibility result for adapting to unknown smoothness, and a phase transition in d.
   - **Idea to borrow:** the smoothness-adaptivity impossibility result tells you not to promise adaptive bin width in the decentralised version without extra assumptions.

5. **Arya & Song (2025), "Batched Single-Index Global Multi-Armed Bandits with Covariates."** arXiv:2503.00565.
   - Batched (not multi-agent) BIDS algorithm: batched successive elimination with dynamic binning along the index. Minimax-optimal (d = 1 rates) given a good pilot direction.
   - **Relevance:** batching is the closest proxy to rare communication.
   - **Idea to borrow:** their dynamic binning under batches is a ready-made template for "communication rounds = batches" in a lower-bound argument.

6. **Arya, Bhattacharjee & Sriperumbudur (2026), "Kernel Single-Index Bandits: Estimation, Inference, and Learning."** arXiv:2603.18938. Kernel ε-greedy with Stein index estimates and IPW kernel ridge regression. The abstract claims O(√T) under common-link Lipschitz conditions. Single-agent.

7. **Arya & Ong (Sep 2026), "Elicitation and Decision Geometry in Single-Index Bandits."** arXiv:2609.35622. Two arms, arm-specific indices, shared unknown monotone link. Natural Boundary Learning via a sequential Stein contrast gives O(log n) regret under decision stability. Single-agent.

**Nearby multi-agent work with flexible links (not a scoop, but reviewers will ask):**
- Dubey & Pentland's cooperative Kernel-UCB (ICML 2020, arXiv:2008.06220);
- Li et al.'s asynchronous distributed kernel bandits (ICLR 2023, OpenReview -G1kjTFsSs);
- FedGLB (Li & Wang, NeurIPS 2022, arXiv:2202.01087), with a *known* link;
- "Communication-Efficient Federated Non-Linear Bandit Optimization" (arXiv:2311.01695);
- Fed-PNE federated X-armed bandits (arXiv:2205.15268).

None uses an index direction, a Stein estimator, or a non-monotone link on a peer-to-peer graph.

## Key Findings by Question

### Q1. Tight (additive / logarithmic / mixing-time) delay terms

**Q1.1 Joulani, György & Szepesvári (ICML 2013), "Online Learning under Delayed Feedback."** arXiv:1306.0686. https://arxiv.org/abs/1306.0686
- **Setting:** single learner, stochastic and adversarial, delayed feedback. Provides a server-free black-box reduction (BOLD).
- **Result:** delay inflates regret **multiplicatively in adversarial** problems but only **additively in stochastic** ones. Delayed-UCB1 pays an additive term of order (expected delay) × roughly K, on top of the delay-free bound.
- **Graph:** none; the delay τ plays the role your D plays.
- **Technique:** a queue-based reduction in which the base algorithm only ever sees non-delayed data. Plus a direct UCB analysis showing that the confidence width using only observed rewards is off by at most the number of in-flight samples.
- **Idea to borrow:** their UCB proof charges delay only through "in-flight samples per arm", and only while an arm is still being pulled. Apply this per bin with in-flight count ≤ N·D. This immediately gives Σ_b (N·D)·Δ_b rather than N·D·N_bins·(max gap). Combined with the log T/Δ_b² pull cap, it yields Σ_b min(N D Δ_b, log T/Δ_b).

**Q1.2 Amani & Thrampoulidis (AAAI 2021), "Decentralized Multi-Agent Linear Bandits with Safety Constraints" (DLUCB, RC-DLUCB, Safe-DLUCB).** arXiv:2012.00314. https://arxiv.org/abs/2012.00314
- **Setting:** fully decentralised, arbitrary connected graph, linear bandit, symmetric doubly-stochastic gossip matrix P.
- **Result (Theorem 2, verbatim):** with probability ≥ 1 − δ, "R_T ≤ 2Sd log(1 + NT/(dλ)) + 2eβ_T √(2dNT log(λ + NT/d))".
  - The first term is named the "**regret of delay**"; the second matches centralised regret.
  - S = log(2N/ε)/√(2 log(1/|λ₂|)) is the accelerated (Chebyshev) gossip length.
- **Graph:** enters only through the spectral gap 1 − |λ₂| (via S); diameter does not appear.
  - DLUCB (Table 1): regret O(d·log(Nd)/log^{0.5}(1/|λ₂|)·log(NT) + d log(NT)√(NT)); communication O(dN²T·log(Nd)/log^{0.5}(1/|λ₂|)).
  - RC-DLUCB reduces total communication to O(d³N^{2.5} log(Nd)/log^{0.5}(1/|λ₂|)).
- **Technique:** Lemma 2 shows that stale Gram matrices inflate ‖x‖² in the inverse norm by at most a factor e, for all but ψ = S·d·log(1 + NT/(dλ)) (agent, round) pairs. This is an elliptical-potential count.
- **Idea to borrow (most important for your bound):** build the per-bin analogue of Lemma 2.
  - For bin b, delayed counts satisfy n̂_b ≥ n_b − N·D. Once n_b ≥ N·D, the stale UCB radius is within √2 of the fresh one.
  - So "bad" rounds per bin number at most N·D, and *they only occur in the first N·D pulls of that bin network-wide*.
  - Summing gives an additive term like D·N·(number of bins that are ever pulled).
  - In sleeping UCB with bins of width ε ~ (NT)^{−1/3}, the number of bins pulled more than O(1) times depends on how many bins are near-optimal, not on N_bins.

**Q1.3 Liu, Kang & Lee (ICLR 2026), "Lipschitz Bandits with Stochastic Delayed Feedback."** arXiv:2510.00309. (Yue Kang is also a co-author of the Kang et al. single-index bandit paper.)
- **Setting:** single agent, Lipschitz/zooming.
- **Result:** Delayed Zooming achieves Õ(T^{(d_z+1)/(d_z+2)} + τ_max·T^{d_z/(d_z+2)}).
  - At τ_max = 0 this recovers the delay-free optimal rate.
  - When d_z = 0 it reduces to the bounded-delay MAB result O(√(cT log T) + c·τ_max).
  - A phased algorithm (DLPP) handles unbounded delays.
- **Technique:** a "lazy update" that caches delayed feedback so the confidence radius "does not fall below half of its value from the last time the arm was pulled". This gives Δ(x) ≤ 6r_t(x) (Lemma 8), compared with 3r_t(x) without delay.
- **Idea to borrow:** the delay term scales with T^{d_z/(d_z+2)}, the number of active zooming balls, and **is T-independent when the zooming dimension d_z = 0**. For a Lipschitz link on the index line with finitely many non-degenerate maxima, d_z is typically 0. This is a plausible explanation for why your empirical delay cost is nearly flat in T.

**Q1.4 Liu, Chen & Huang (2026), "Lipschitz Bandits with Arbitrary Feedback Delays."** arXiv:2608.15036. https://arxiv.org/abs/2608.15036
- **Result:** Õ(T^{(d_z+1)/(d_z+2)} + √D) for total delay D. The stochastic case uses elimination; the adversarial case is EXP3-based. The delay penalty is an additive √(total delay), matching finite-armed results.
- **Idea to borrow:** measure your communication delay as *total* delay D_tot = Σ_t Σ_i (hop-distance staleness) ≤ N·T·D, and use their elimination-style analysis. Under event-triggered flooding, the realised total delay is much smaller than the worst case, because only bins with new data are flooded.

**Q1.5 Howson, Pike-Burke & Filippi (AISTATS 2023), "Delayed Feedback in Generalised Linear Bandits Revisited."** arXiv:2207.10786.
- An optimistic GLB algorithm whose worst-case regret increases only by an additive term in the expected delay, improving earlier multiplicative bounds.
- The key is separating delay from learning difficulty when constructing confidence sets.
- **Idea to borrow:** the same separation applies to your Phase-1 estimator; show that the θ̂ error does not interact with flooding delay.

**Q1.6 Pike-Burke, Agrawal, Szepesvári & Grünewälder (ICML 2018), "Bandits with Delayed, Aggregated Anonymous Feedback."** arXiv:1709.06853.
- The additive delay penalty survives even with aggregated anonymous feedback, when the expected delay is known.
- **Idea to borrow:** if you ever compress flooded records into per-bin aggregates (sums/counts without timestamps), this shows the additive penalty survives aggregation.

**Q1.7 Martínez-Rubio, Kanade & Rebeschini (NeurIPS 2019), "Decentralized Cooperative Stochastic Bandits" (DDUCB).** arXiv:1810.04468.
- **Setting:** N agents, K arms, arbitrary graph, gossip.
- **Result:** regret is bounded by the optimal centralised regret plus a "natural and simple term depending on the spectral gap of the communication matrix", with a graph-independent factor multiplying log T.
- **Technique:** accelerated (Chebyshev) consensus computes delayed running averages; the UCB accounts for both delay and consensus error.
- **Idea to borrow:** their bound puts the graph only in a lower-order additive term, roughly of order N·K·(mixing time). Mirror that structure: centralised (NT)^{2/3} + N_eff·(mixing or D)·polylog.

**Q1.8 Dubey & Pentland (ICML 2020), "Cooperative Multi-Agent Bandits with Heavy Tails" (MP-UCB).** arXiv:2008.06244.
- Message passing runs at a density γ ≤ diameter. At γ = diameter(G), the decentralised group regret is O(K ln T), matching the lower bound, with only a **constant** overhead from communication delay.
- **Idea to borrow:** your relayed-records protocol is exactly their γ = D regime. Cite this to argue the delay term should be constant in T.

**Q1.9 Sleeping-bandit foundations.**
- Kanade, McMahan & Bryan (AISTATS 2009), "Sleeping Experts and Bandits with Stochastic Action Availability and Adversarial Rewards".
- Kleinberg, Niculescu-Mizil & Sharma (Machine Learning 2010), "Regret Bounds for Sleeping Experts and Bandits".

These provide the best-available-arm regret notion that ZoomSIB-UCB uses. This search found no delayed or multi-agent sleeping-bandit analysis; see open gaps.

### Q2. Lower bounds that depend on graph quantities

**Q2.1 Dubey & Pentland (ICML 2020), Heavy-Tails paper (above).**
- **Theorem 1:** the first problem-dependent asymptotic lower bound for cooperative group regret, Ω(K Δ^{−1/ε} ln T) for (1+ε)-heavy tails. It assumes that messages from m reach m′ no earlier than d(m, m′) − 1 rounds later (graph distance), on graphs with diameter γ* ≪ M.
- **Graph:** diameter, and the clique covering number χ̄(G_γ) of the γ-th graph power; at γ = diameter, χ̄ = 1.
- **Idea to borrow:** their upper bounds scale with χ̄(G_γ), the number of "information cliques" after γ hops. Restate your delay term in χ̄ terms rather than N·D: each clique of G_D shares data with a one-round lag.

**Q2.2 Cesa-Bianchi, Gentile, Mansour & Minora (COLT 2016), "Delay and Cooperation in Nonstochastic Bandits" (Exp3-Coop).** arXiv:1602.04741.
- **Result (abstract):** average per-agent regret is at most of order √((d + 1 + (K/N)·α_{≤d})(T ln K)), where α_{≤d} is the independence number of the d-th power of G.
  - With d = √K this is ≤ K^{1/4}√(T ln K) + √K ln T on any connected graph.
  - The single-agent minimax regret with delay d is of order √((d+K)T).
- **Graph:** the independence number of G^d, plus the delay d; no spectral term.
- **Idea to borrow:** the d-hop horizon is a tuning knob. You can relay records only up to h ≤ D hops, trading α(G^h)-type sample sharing against h-round staleness (a bias–variance trade-off). Optimising h may beat D.

**Q2.3 Kolla, Jagannathan & Gopalan (IEEE/ACM ToN 2018), "Collaborative Learning of Stochastic Bandits over a Social Network."** arXiv:1602.08886.
- **Setting:** agents observe neighbours' rewards instantly (one-hop sharing, no relaying).
- **Result:**
  - Lower bounds show that non-altruistic, individually consistent policies suffer large regret.
  - UCB-Network regret is bounded via the independence numbers α(G) and α(G²).
  - A dominating-set leader–follower policy improves regret.
- **Idea to borrow:** dominating-set leaders are a cheap alternative to flooding for Phase 2: only leaders run sleeping UCB on full statistics.

**Q2.4 Xu & Klabjan (2023), "Regret Lower Bounds in Multi-agent Multi-armed Bandit."** arXiv:2308.08046.
- Per the abstract, the Ω(T^{2/3}) lower bound for connected graphs holds under adversarial rewards ("Assuming adversarial rewards, we establish a lower bound O(T^{2/3}) for connected graphs").
- For stochastic rewards on well-connected graphs, it gives O(log T) instance-dependent and √T gap-independent bounds, and a linear lower bound for disconnected graphs.
- **Caveat:** we read only the abstract. The Ω(T^{2/3}) bound concerns adversarial rewards, not homogeneous stochastic cooperative bandits; verify before citing.
- **Idea to borrow:** their temporal-graph instance technique could produce a graph-dependent lower bound for your additive term.

**Q2.5 Communication lower bounds.**
- Wang, Hu, Chen & Wang (ICLR 2020) show that near-optimal regret in distributed MAB needs at least Ω(M) communication.
- Amani, Lattimore, György & Yang (ICML 2023, "Distributed Contextual Linear Bandits with Minimax Optimal Communication Cost") give a communication lower bound for distributed contextual linear bandits, and the matching DisBE-LUCB algorithm.
- Fed-PNE (Li et al.) shows logarithmic-in-T communication is unavoidable for its regret rate, and proves a federated X-armed regret lower bound even with unlimited communication.
- **Idea to borrow:** combine Dey et al.'s bump construction with the Amani et al. communication argument to show that Ω(N·polylog) messages are needed to reach (NT)^{2/3}.

**Q2.6 Barnea et al. (2024), "Individual Regret in Cooperative Stochastic Multi-Armed Bandits" (COOP-SE).** arXiv:2411.06501.
- Individual regret O(R/m + A² + A√log T), with a nearly matching lower bound. This is **independent of graph diameter** on arbitrary connected graphs and holds with logarithmic message size.
- With log T communication rounds, the bound is O(R/m + A log T).
- **Idea to borrow:** this is direct evidence that a diameter-free additive term is achievable. Elimination-style sharing (successive elimination over bins) may let you drop D entirely from the leading delay term.

### Q3. Flooding / message passing / LOCAL vs consensus / gossip / push-sum

**Q3.1 Dubey & Pentland (ICML 2020), "Kernel Methods for Cooperative Multi-Agent Contextual Bandits" (Coop-KernelUCB).** arXiv:2008.06220.
- **Setting:** agents on a graph with delays. Each agent sends ⟨t, v, x, y⟩ messages, forwarded with a time-to-live γ, so data from v reach v′ after d(v, v′) − 1 rounds. This is the LOCAL model.
- **Result:** near-optimal per-agent regret; the graph enters through γ-hop powers.
- **Cost:** communication is linear in T (raw data every round), as Li et al. (ICLR 2023) later noted.
- **Idea to borrow:** this is the closest existing analogue to your record relay. Cite it as the protocol you improve on via event-triggering.

**Q3.2 Dubey & Pentland Heavy-Tails (above).**
- Key qualitative point: robust estimators (median-of-means etc.) make averaging-based protocols such as running consensus infeasible, which is why they switch to message passing.
- **Idea to borrow:** your truncated Stein estimator is nonlinear only through truncation, and the per-bin sleeping-UCB counts are integers. Relaying exact counts avoids the consensus bias that would otherwise enter the UCB radius.

**Q3.3 Landgren, Srivastava & Leonard (CDC 2016 / ECC 2016), coop-UCB and coop-UCB2.**
- Running-consensus estimates of arm means and counts. The regret terms depend on graph explore-exploit indices derived from eigenvalues/eigenvectors of the consensus matrix (not verified in detail in this session).
- **Idea to borrow:** a clean experimental baseline. Run your Phase 2 with consensus-averaged counts to show flooding's advantage.

**Q3.4 Szörényi et al. (ICML 2013), "Gossip-based Distributed Stochastic Bandit Algorithms."** Early gossip-based ε-greedy on P2P networks. Baseline only.

**Q3.5 Chawla, Sankararaman, Ganesh & Shakkottai (AISTATS 2020), "The Gossiping Insert-Eliminate Algorithm for Multi-Agent Bandits."** arXiv:2001.05452.
- Agents gossip only *arm recommendations* (O(log K) bits), which restricts each agent to a small active set.
- Per-agent regret is roughly (K/N + small)·log T/Δ; the graph enters via the gossip spreading time (conductance-type).
- **Idea to borrow:** in Phase 2 an agent only needs statistics for bins that are both available and near-optimal. Recommend-then-pull reduces flooding volume.

**Q3.6 Zhu, Mulle, Smith, Koppel & Liu (2021–2023), "Decentralized UCB Algorithms for Homogeneous Multi-Agent MAB."** arXiv:2111.10933.
- Consensus-based decentralised UCB/KL-UCB on fixed undirected graphs, plus a directed variant.
- Each agent beats single-agent UCB, and more neighbours give better regret.

**When relaying beats averaging (synthesis):**
- **Relaying** exact records (or exact sums along a tree) gives unbiased statistics with deterministic staleness ≤ D. The UCB analysis then only needs an "in-flight samples" correction (Joulani-style).
- **Gossip** gives biased estimates whose error decays like λ^t. That requires inflated confidence radii and a mixing-time term (Martínez-Rubio et al.; Amani & Thrampoulidis).
- **Per-round bandwidth:** flooding can cost O(N·deg) records per round per new sample in the worst case. Gossip costs O(deg·K) numbers per round regardless of activity.
- **Event-triggered flooding** is the regime where relaying wins on both axes, because messages are sent only when counts change materially.

### Q4. Agreement and stopping in distributed explore-then-commit / two-phase algorithms

Direct literature here is thin; this is a genuine gap.

**Q4.1 Wang, Proutiere, Ariu, Jedra & Russo (AISTATS 2020), "Optimal Algorithms for Multiplayer Multi-Armed Bandits" (DPE1/DPE2).** http://proceedings.mlr.press/v108/wang20m.html
- **Setting:** multiplayer bandits with collisions and a leader–follower structure. Communication happens via collisions, and each communication phase takes at most D rounds.
- **Result:** regret asymptotically matches the optimal centralised algorithm, and the expected number of communication bits does not grow with T.
- **Idea to borrow:** a leader election plus a leader-announced commit time solves your Phase 1 → Phase 2 agreement. Elect a root of the spanning tree; the root broadcasts θ̂ and the bin grid once, so all agents commit to the *same* estimate after ≤ 2D rounds.

**Q4.2 Agarwal, Aggarwal & Azizzadenesheli (JMLR 2022), "Multi-Agent Multi-Armed Bandits with Limited Communication" (LCC-UCB).** https://www.jmlr.org/papers/v23/21-138.html
- Doubling epochs. Agents communicate only at epoch ends, sharing the best-arm index (O(log K) bits).
- Per-agent regret Õ(√((K/N + N)T)).
- The sparse-graph variant, with max degree K_G and diameter D, has Õ(D√((K/N + K_G)DT)). That is **a multiplicative diameter dependence**, the thing you want to avoid.

**Q4.3 Arya & Song (2025), BIDS (above).** Batch boundaries act as synchronous stopping points. The analyses with a pilot direction versus an estimated direction quantify the cost of committing to an imperfect θ̂.

**Regret cost of disagreement (synthesis):**
- If agent i commits to θ̂_i with ‖θ̂_i − θ̂‖ ≤ η, its index-line projections differ by at most η‖x‖.
- So bin assignments disagree only for contexts within η of a bin boundary.
- With Lipschitz f this costs O(L·η) per round, i.e., O(N·T·η) in total.
- Exact tree pooling makes η = 0, which is a clean argument for your design over gossip in Phase 1.

### Q5. Event-triggered / rare communication with instance-dependent bounds

**Q5.1 Wang, Hu, Chen & Wang (ICLR 2020), "Distributed Bandit Learning: Near-Optimal Regret with Efficient Communication" (DisLinUCB, DELB, DEMAB).** https://openreview.net/pdf?id=SJxZnR4YvB
- **Setting:** star network (server).
- **Result:**
  - Distributed K-armed bandits with M agents: near-optimal regret O(√(MKT log T)) with O(M log T) or O(MK log M) communication.
  - DisLinUCB synchronises when a log-determinant ratio trigger fires, giving near-optimal linear-bandit regret with O(M^{1.5}d³) communication.
  - Ω(M) communication is necessary.
- **Idea to borrow:** the per-bin analogue of the determinant trigger is "flood bin b when its local unshared count exceeds a constant fraction of its last synchronised count". This gives O(log T) floods per bin. Crucially, it makes floods instance-dependent: bins that stop being pulled stop generating traffic.

**Q5.2 Li & Wang (AISTATS 2022), "Asynchronous Upper Confidence Bound Algorithms for Federated Linear Bandits" (Async-LinUCB).** arXiv:2110.01463.
- Asynchronous event-triggered communication with a server; clients upload independently.
- The regret/communication trade-off is tunable, e.g., communication C_T ≤ N d log T.
- **Idea to borrow:** their asynchronous trigger avoids forcing all agents to sync on any one agent's event, which is exactly what event-triggered flooding needs.

**Q5.3 Li & Wang (NeurIPS 2022), "Communication Efficient Federated Learning for Generalized Linear Bandits" (FedGLB-UCB).** arXiv:2202.01087.
- Server-based, **known**-link GLB.
- Communication is sub-linear in T while matching centralised regret, using online regression plus occasional global updates.
- **Not a scoop** (the link is known), but reviewers will compare.

**Q5.4 Li et al. (ICLR 2023), asynchronous distributed kernelised contextual bandits.** OpenReview -G1kjTFsSs.
- The first asynchronous distributed kernel bandit. It uses Nyström-type embeddings so that only sufficient statistics are shared.
- The authors note that a communication lower bound for distributed contextual bandits remains open.

**Q5.5 Amani, Lattimore, György & Yang (ICML 2023), DisBE-LUCB.** Minimax-optimal regret Õ(d√(NT)) with minimax-optimal communication for distributed contextual linear bandits (server).

**Q5.6 Madhushani & Leonard (2021), "When to Call Your Neighbor? Strategic Communication in Cooperative Stochastic Bandits."** arXiv:2110.04396.
- Agents communicate only when doing so is informative (e.g., after exploratory pulls).
- Their ComEx protocol "achieves the same order of performance as full communication while communicating only O(log T) number of messages", versus Θ(T) messages under full communication.
- **Idea to borrow:** flood only the records generated by *exploratory* pulls of under-sampled bins. Exploitative pulls of the incumbent bin rarely change any agent's decision.

**Q5.7 Fed-PNE (Li, Song, Honorio & Lin, AAAI 2024), "Federated X-Armed Bandit."** arXiv:2205.15268.
- **Setting:** server; heterogeneous local objectives over a common domain; a hierarchical partition with phased node elimination.
- **Result:**
  - Sublinear regret in both M and T.
  - Õ(M log T) communication rounds, shown to be unavoidable for that regret rate.
  - A regret lower bound that holds even with unlimited communication, and a DP variant.
- **Idea to borrow:** phased elimination over a hierarchical partition makes communication *depend on the near-optimality dimension*. A phased-elimination version of your Phase 2 would have per-bin traffic O(log T), and only for surviving bins.

**Q5.8 Personalised federated X-armed bandits.**
- PF-PNE (Li et al., arXiv:2310.16323): communication is bounded by a constant C₁M log(1/Δ) when the heterogeneity Δ is large, and by C₂M log(MT) otherwise.
- PF-XAB (Arabzadeh et al., arXiv:2409.07251): logarithmic communication.

### Q6. Multi-agent bandits with unknown or misspecified links

**Q6.1 Kernel/RKHS.**
- Dubey & Pentland's Coop-KernelUCB (ICML 2020): graph, LOCAL message passing; the graph enters via γ-hop powers and delays.
- Li et al.'s asynchronous kernel bandits (ICLR 2023): server-based.

**Q6.2 GLM with known link:** FedGLB (above).

**Q6.3 X-armed / Lipschitz.**
- Fed-PNE, PF-PNE and PF-XAB are all server-based.
- A 2026 decentralised multi-player Lipschitz bandit with collisions (arXiv:2602.16965) first runs a coordination phase that seats players on distinct high-value regions via maxima-directed search. It then decouples into independent single-player Lipschitz bandits. This is a collision model, not cooperative estimation.

**Q6.4 Nonlinear federated:** "Communication-Efficient Federated Non-Linear Bandit Optimization" (arXiv:2311.01695). Server-based, with a general function class that is not index-structured.

**Q6.5 Low-dimensional linear:** Chawla, Sankararaman & Shakkottai (2020), "Multi-Agent Low-Dimensional Linear Bandits" (arXiv:2007.01442). Agents gossip subspace/arm recommendations; closest in spirit to "share a low-dimensional direction".

**Q6.6 Semiparametric (single-agent).**
- Krishnamurthy, Wu & Syrgkanis (ICML 2018), "Semiparametric Contextual Bandits" (BOSE: orthogonalised estimation with an additive confounding term).
- Kim & Paik (ICML 2019, arXiv:1901.11221): a nonstationary semiparametric reward.
- Neither is multi-agent nor single-index. **Cite them to separate "semiparametric" from "single-index".**

**Q6.7 Misspecification motivation:** Ghosh, Chowdhury & Gopalan (AAAI 2017), "Misspecified Linear Bandits". It shows misspecification can cause linear regret, and Dey et al. use it as motivation.

**Gap confirmed:** no cooperative or decentralised algorithm combines all three of:
- an index direction learned by a Stein estimator;
- a non-monotone unknown link;
- a peer-to-peer graph.

### Q7. Distributed estimation of index directions / SDR over networks

**Q7.1 He, Zhang & Chen (JASA 2025; arXiv:2306.06324), "Differentially Private Sliced Inverse Regression in the Federated Paradigm" (FSIR).**
- Federated SIR that shares only local estimates, with a vectorised Gaussian DP mechanism and collaborative variable screening. Theory covers low and high dimensions.
- Server-based and one-shot.
- **Idea to borrow:** their DP mechanism can be applied to your Phase-1 Stein mean for a "private Dec-ZoomSIB" extension.

**Q7.2 Cui, Zhao, Xu & Cheng (2023), "Federated Sufficient Dimension Reduction Through High-Dimensional Sparse Sliced Inverse Regression."** arXiv:2301.09500. Federated sparse SIR via a convex program, with the covariance constructed "safely and losslessly".

**Q7.3 Li et al. (2025), "Unified Distributed Estimation Framework for Sufficient Dimension Reduction Based on Conditional Moments."** arXiv:2509.11455.
- An exact distributed SIR (E-DSIR) that is identical to the full-sample estimator, plus approximate distributed SAVE/DR.
- **Idea to borrow:** the "exact distributed = full-sample" property is the SDR analogue of your spanning-tree pooling; cite it as precedent.

**Q7.4 Stein-type single-index estimators (single-machine foundations).**
- Yang, Balasubramanian & Liu (ICML 2017), "High-dimensional Non-Gaussian Single Index Models via Thresholded Score Function Estimation".
- Plan & Vershynin (2016) and Goldstein et al. (2018) on generalised Lasso / Gaussian-width analysis.
- Li (1991) on SIR, and Li (1992) on principal Hessian directions via Stein's lemma.

**Gap:** we found no paper on **decentralised (graph, gossip/flooding) Stein estimators for single-index models with sample-and-communication complexity**. Existing distributed SDR is server-based and one-shot. Your Phase 1 analysis (a sample mean pooled exactly in O(D) rounds using O(N·d) numbers) would be a small but genuine contribution.

### Q8. Robustness: time-varying graphs, link failures, directed links, asynchrony

**Q8.1 Xu & Klabjan (NeurIPS 2023 spotlight), "Decentralized Randomly Distributed Multi-agent Multi-armed Bandit with Heterogeneous Rewards."** arXiv:2306.05579.
- Time-dependent random graphs (generated via rapidly mixing Markov chains or random-graph models) and heterogeneous sub-exponential/sub-Gaussian rewards.
- Consensus + weighting + UCB, with high-probability bounds that capture graph randomness.

**Q8.2 Zhu et al. (2111.10933 and the directed-graph variant).** Strongly connected directed graphs suffice to beat single-agent UCB; undirected graphs give better constants.

**Q8.3 Madhushani, Dubey, Leonard & Pentland (2021), "One More Step Towards Reality: Cooperative Bandits with Imperfect Communication."** Covers probabilistic link failures, message corruption and delays.

**Q8.4 Vial, Shakkottai & Srikant (2022), "Robust Multi-Agent Bandits Over Undirected Graphs."** arXiv:2203.00076. With malicious agents, each honest agent i achieves O((d_mal(i) + K/n) log T/Δ) on any connected undirected graph, so the effect of malicious agents is entirely local.

**Q8.5 Asynchronous agents.**
- "Asynchronous Multi-Agent Bandits: Fully Distributed vs. Leader-Coordinated Algorithms" (Wang, Chen, Yang, Liu, Hajiesmaili, Towsley & Lui, Proc. ACM Meas. Anal. Comput. Syst. 9(1), Article 3, SIGMETRICS '25, doi:10.1145/3711696).
  - Only an unknown, time-varying subset of agents is active each round.
  - Uses accuracy-adaptive and on-demand communication, plus dynamic leader selection via a low-switching Tsallis-INF variant.
  - Near-optimal regret and communication.
- Li & Wang (AISTATS 2022) Async-LinUCB (server).
- **Idea to borrow:** asynchronous activity is formally a sleeping-*agent* problem, so your sleeping-bin machinery may extend to it naturally.

**Q8.6 Stochastic block-model graphs:** "Heterogeneous Multi-agent Multi-armed Bandits on Stochastic Block Models" (arXiv:2502.08003). Time-varying SBM graphs; synchronisation happens stochastically, with a probability tied to the edge probabilities.

**For your protocol:**
- Flooding with per-record IDs is naturally robust to link failures and directed links: records arrive later, not wrongly.
- On a time-varying graph, D should be replaced by a "dynamic diameter"/B-connectivity window (the union of graphs over any B rounds is connected).
- This changes D to B·D in the delay term but keeps it additive.

## Diagnosis: Why O(N·D·N_bins) Is Too Loose and How to Fix It

1. **Charge delay per bin only while the bin is under-sampled.**
   - Following Joulani et al. and DLUCB Lemma 2: a stale count n̂_b ≥ n_b − N·D changes the UCB radius by at most a constant once n_b ≥ N·D.
   - So delay costs arise in at most N·D pulls of bin b *network-wide*, each costing Δ_b, and never more than the bin's total pulls, O(log T/Δ_b²).
   - The delay term becomes Σ_b min(N·D·Δ_b, C log T/Δ_b). That is at most N_bins·√(N·D·log T) in the worst case, and much smaller when few bins are near-optimal.
2. **Use the zooming / near-optimality dimension of f on the index line.**
   - Delayed zooming bounds scale as τ_max·T^{d_z/(d_z+2)}; with d_z = 0 the delay term is T-independent.
   - Define N_eff(ε) = #{bins with Δ_b ≤ ε}. For f with finitely many non-degenerate maxima, N_eff grows polylogarithmically, which matches your nearly-flat empirical cost.
3. **Sleeping availability helps further.** A bin that is unavailable in round t cannot be mis-pulled because of staleness. So the delay term should be weighted by each bin's availability probability p_b; with K contexts per round, Σ_b p_b ≤ K.
4. **Replace D by a graph quantity that reflects information cliques.** Following Dubey & Pentland and Cesa-Bianchi et al., agents within h hops form groups that share data with lag ≤ h. The effective multiplier is then χ̄(G^h) or α(G^h) rather than N, with h tuned (possibly h < D).
5. **Event-triggered flooding makes D a worst case only.** A bin whose statistics are not changing has zero effective staleness; only bins in active exploration carry delay.

**Target theorem shape:**
- R_T ≤ Õ((NT)^{2/3}) + Õ(D·Σ_{b: Δ_b > 0} min(N Δ_b, log T/(D Δ_b))) + O(N·D).
- The last term is the Phase-1 aggregation cost.
- Under a d_z = 0 margin condition, the middle term is O(D·N_eff·polylog T).

## (a) Five Papers to Read First

1. **Amani & Thrampoulidis, DLUCB (AAAI 2021, arXiv:2012.00314).** The "regret of delay" decomposition and the stale-Gram Lemma 2 are the precise template for tightening your additive term. The graph enters only through the spectral gap.
2. **Joulani, György & Szepesvári (ICML 2013, arXiv:1306.0686).** The cleanest proof that stochastic bandits pay for delay additively, via in-flight samples per arm. Port it per bin.
3. **Dubey & Pentland, Heavy-Tails (arXiv:2008.06244) and Kernel (arXiv:2008.06220), ICML 2020.** The LOCAL/message-passing protocol you are essentially using, plus a diameter-based lower bound, clique-cover graph quantities, and constant-in-T delay overhead.
4. **Liu, Kang & Lee, "Lipschitz Bandits with Stochastic Delayed Feedback" (ICLR 2026, arXiv:2510.00309) and Liu–Chen–Huang (arXiv:2608.15036).** Delay terms scale with the zooming dimension (T-independent at d_z = 0); this is the likely mechanism behind your flat empirical curve.
5. **Dey, Bhore & Ghosh (arXiv:2605.09454)** plus **Kang et al. (arXiv:2506.12751).** Your base. Check v3 of Dey et al. for any added discussion of extensions, and monitor both groups for multi-agent follow-ups.

## (b) Open Gaps This Setting Could Fill

1. **First decentralised single-index bandit with a non-monotone link:** an (NT)^{2/3} upper bound plus an additive graph term, and an Ω((NT)^{2/3}) lower bound lifted from Dey et al.
2. **Delay-robust sleeping bandits:** we found no analysis of sleeping bandits under delayed or relayed feedback. A per-bin, availability-weighted delay term would be new even for N = 1 with feedback delay τ.
3. **Zooming-dimension-dependent communication and delay costs on a graph.** Fed-PNE does this with a server; nothing does it peer-to-peer.
4. **A graph-dependent lower bound for the additive term**, e.g., Ω(D·N_eff), combining Dubey–Pentland's distance-delayed message assumption with a bump construction on the index line.
5. **Distributed Stein/SDR estimation over graphs** with explicit sample, communication and round complexity; existing distributed SIR is server-based and one-shot.
6. **Consensus on the switch from Phase 1 to Phase 2:** quantify the regret of agents committing to different θ̂_i (an O(N T η)-type cost), show that exact tree pooling removes it, and compare against a gossip-based Phase 1.
7. **Event-triggered flooding with instance-dependent traffic:** prove that per-bin floods are O(log T), and zero for eliminated bins, giving O(N·deg·N_eff·log T) total messages.
8. **Robustness extensions:** B-connected time-varying graphs, asynchronous (sleeping) agents, and malicious relays (Vial et al.-style locality) for record-relay protocols.

## Caveats

- The scooping check is a negative search result over arXiv, OpenReview and indexed venues up to early October 2026. Workshop papers, theses and unindexed submissions could exist. Re-check monthly, especially the Dey/Bhore/Ghosh and Kang/Li/Lee groups.
- Some details were verified only from abstracts or secondary summaries: Xu & Klabjan's Ω(T^{2/3}) lower bound (adversarial rewards), and the Landgren et al. spectral terms. Verify these before citing exact constants.
- Two citation corrections:
  - DLUCB is by Amani and Thrampoulidis only; Alizadeh is not an author of the AAAI 2021 paper.
  - "Delay and Cooperation in Nonstochastic Bandits" has Alberto Minora as a fourth author (COLT 2016, arXiv:1602.04741).
- The diagnosis and target theorem shape are my synthesis from the cited techniques, not results stated in any paper. They need proof in your setting, notably the d_z = 0 margin condition for f on the index line.
