"""E35 -- private Phase 1 (Theorem 'thm:private' of docs/proofs/serverless.tex).

Each agent adds Gaussian noise once to its truncated Stein sum before flooding it, which
makes everything the network does (ε, δ)-DP with respect to each Phase-1 sample.  The
theorem says the direction error grows by a factor 1 + κ, κ = √(6 d N log(1.25/δ)) / ε,
and that a longer Phase 1 buys it back (leading term ((1+κ) d NT)^{2/3}).

Ring, N = 16, T = 10 000, quadratic link: ε ∈ {∞, 128, 32, 8, 2} × Phase-1 length T0 ∈ {60, 240, 960}
rounds per agent, exact tree pooling of the noisy sums, event-triggered flooding in Phase 2.

Writes results/fig35_private_phase1.{png,pdf}, results/claims_e35.md.
"""

from __future__ import annotations

from claims_common import (D as DIM, OUT, fmt, md_table, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from configs.decentralized import dec_config

N = 16
T = pick(10_000, 2500)
GRAPH = "ring"
LINK = "quadratic"
EPS = [np.inf, 128.0, 32.0, 8.0, 2.0]        # ε = ∞: same code path, zero noise
T0S = pick([60, 240, 960], [60, 240])
DELTA_P = 1e-5
NTR = trials(10, 2)


def kappa(eps):
    return np.sqrt(6 * DIM * N * np.log(1.25 / DELTA_P)) / eps


def cell_fn(cell, names=None):
    eps = cell[0]
    c = {f"T0={t0}": dec_config(GRAPH, "tree", {}, "flood", {"gamma": 0.5}, T0=t0,
                                bin_width="network", dp_eps=eps, dp_delta=DELTA_P) for t0 in T0S}
    c = {k: v for k, v in c.items() if names is None or k in names}
    out, _ = sweep(c, NTR, N, T, LINK)
    return summarize(out)


def main():
    res = run_cells("e35", [(e,) for e in EPS], cell_fn)
    use_style()
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    rows = []
    for eps in EPS:
        r = res[(eps,)]
        lab = "no privacy (ε = ∞)" if np.isinf(eps) else f"ε = {eps:g}"
        ax.plot(T0S, [r[f"T0={t}"]["R"].mean() for t in T0S], "o-", label=lab)
        for t0 in T0S:
            v = r[f"T0={t0}"]
            rows.append([lab, f"{kappa(eps):.0f}", t0, fmt(v["R"]),
                         f"{v['R'].mean() / res[(np.inf,)]['T0=60']['R'].mean():.2f}"])
    ax.set(xscale="log", xlabel="Phase-1 rounds per agent T0", ylabel="network regret",
           title=f"Private Phase 1 ({GRAPH}, N = {N}, T = {T:,})")
    ax.set_xticks(T0S, [str(t) for t in T0S])
    ax.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig35_private_phase1")
    intro = (f"N = {N}, {GRAPH}, T = {T:,}, {LINK} link, d = {DIM}, δ_p = {DELTA_P:g}, {NTR} paired trials, "
             "mean ± 95% CI. Each agent adds N(0, σ_p² I) to its truncated Stein sum once, "
             "σ_p = 2τ√d·√(2 log(1.25/δ_p))/ε; Phase 2 is unchanged. All rows, including ε = ∞, use the "
             "data-free window W = X_max of the proofs, so Phase-1 contexts are not used elsewhere. "
             "κ is the theorem's factor. "
             "'÷ base' is relative to no privacy at T0 = 60.")
    md_table(f"{OUT}/claims_e35.md", "E35: private Phase 1", intro,
             ["privacy", "κ (theory)", "T0", "network regret", "÷ base"], rows)


if __name__ == "__main__":
    main()
