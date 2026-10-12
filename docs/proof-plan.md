# Proof plan: Dec-ZoomSIB (decentralised single-index bandits)

Goal: prove for Dec-ZoomSIB the kinds of bounds that the decentralised-bandit papers prove
(`papers/04-decentralized-bandits-graph/`). The base results with a server are in
[`proofs/server.tex`](proofs/server.tex). Last updated 2026-10-12.

## Status

| # | Item | State |
|---|---|---|
| 0a | Trigger threshold γ: Theorem 9 for any γ, with an explicit √(1+Nγ) factor | **Done.** Checked by E30 ([table](../results/claims_e30.md)) |
| 0b | d-dependence: (dNT)^{2/3} against DBG's d²T^{2/3} | **Deferred to future work.** The argument is in Remark `rem:d`; not needed for this paper |
| 1 | Relay theorem, made rigorous | **Next** |
| 2 | Tight delay term | open, main contribution |
| 3 | Communication theorem for the relay | open |
| 4 | Lower bound that depends on the graph | open, ambitious |
| 5 | Agreement and stopping, Phase 1 → Phase 2 | open |
| 6 | Robustness corollaries | open, cheap once 1 is done |

## The proofs

**1. Relay theorem, rigorous** (sketch at `server.tex`, `thm:relay`)
- (a) Phase 1 over a spanning tree is exact. "Phase 1 is exactly centralised" carries over after
  2·depth extra rounds, and every agent freezes the same θ̂.
- (b) Stale counts: each bin has at most (N−1)·D extra pulls still in flight. Mechanical.
- (c) **The confidence lemma is the hard step.**
  - As sketched, an agent's view is split into N per-agent prefixes, each bounded separately.
  - That makes the confidence width √N wider, which breaks the matching rate.
  - E23 (+1.5–9%) says the loss is an artefact of the proof.
  - Fix: either a sharper concentration lemma, or build the UCB on statistics every agent shares
    (DLUCB does this with delayed but consistent statistics).
  - First check how Dubey & Pentland (arXiv:2008.06220) handle it.

**2. Tight delay term**
- Replace N·D·N_bins with Σ_b min(N·D·Δ_b, log T/Δ_b): charge delay to a bin only while it is
  under-sampled (Joulani et al. 2013; DLUCB Lemma 2).
- Hard part: bins are sleeping, and DBG give no gap-dependent analysis. This needs a margin
  condition on f along the index line.
- Measured delay cost is 60–150× below the current term and almost flat in T.

**3. Communication theorem for the relay**
- Each agent republishes a bin at most log_{1+γ} times, and flooding sends each record across
  each edge once: O(|E|·N_bins·log NT) scalars.
- This backs the "~2000× fewer scalars than consensus" claim.
- Stronger version: count only bins that are actually pulled.

**4. Lower bound that depends on the graph.** Ω((NT)^{2/3}) already holds with no server. An
additive Ω(·D) term would combine "an agent sees only its D/2-ball for D/2 rounds" with DBG's
bump construction. Dubey & Pentland list this as open.

**5. Agreement and stopping.** If frozen directions differ by η, regret grows by O(NTη). Exact
pooling up the tree gives η = 0. Any adaptive stopping rule needs ≥ D rounds to detect that all
agents are ready. E28 measures both.

**6. Robustness corollaries.** Flooded records arrive late, never wrong. So graphs that are
connected over every window of B rounds give D → B·D; link failures and directed links work the
same way.

## Other theoretical directions to explore

Candidate directions beyond 1–6. Each points to the evidence or paper it would build on;
literature claims come from [`literature-map.md`](literature-map.md) and still need checking
against the PDFs.

| Direction | What it would prove | Builds on |
|---|---|---|
| Regret–communication trade-off | best regret with a budget of C sync rounds; is polylog(NT) enough? | `server.tex` Conjecture, E27 |
| Lower bound on communication | Ω(N·polylog) messages are needed to reach (NT)^{2/3} | Wang et al. ICLR 2020; Amani et al. ICML 2023 |
| Per-agent regret | each agent's own regret, not just the network sum | Chawla et al. 2020; Barnea et al. 2024 |
| Heterogeneous agents | different θ*_i or links; sign-invariant Stein pooling | E29, `papers/05-beyond-homogeneous-agents/` |
| Byzantine / malicious relays | honest agents' regret is affected only locally | Vial et al. 2022 |
| Asynchronous agents | only some agents are active each round: a "sleeping agents" problem | SIGMETRICS '25 asynchronous MAB |
| Private Phase 1 | differentially private Stein mean over the tree | He, Zhang & Chen, JASA 2025 (federated SIR) |
| Gap condition from E30 | when does a small γ avoid the √(1+Nγ) loss? needs an evenness assumption on pulls | E30 |

## Future work (parked)

- **d-dependence (0b).** Charging the projection error per pull gives Õ(d^{2/3}(NT)^{2/3})
  plus a d²/μ*² burn-in, against DBG's d². Before claiming it: check d^{2/3} empirically (best
  T₀ against d), and raise it with Prof. Ghosh, since it also improves DBG's single-agent result.
