"""E34 -- prior papers' ALGORITHMS on our problem, over a graph.

E15–E20 ran the prior papers' communication protocols (consensus, gossip, push-sum,
message passing) inside ZoomSIB.  Here we run their bandit algorithms instead, each with
IDEAL relaying of every raw observation along the graph (src/dec/netbaselines.py), which is
at least as informative as the gossip the papers use:

    DLUCB-style        LinUCB on all relayed data (linear reward model)
    Dec-ESTOR          monotone single-index, pooled forced exploration
    Dec-GSTOR          explore-then-commit single-index, pooled exploration
    Coop-Kernel-style  IGP-UCB (RBF kernel on R^d) on all relayed data

against Dec-ZoomSIB-Relay (tree Phase 1 + event-triggered flooding), the server version,
and N independent ZoomSIB agents, on a ring with N = 8, for a non-monotone (quadratic),
a multimodal (zigzag) and a monotone (logistic) link.

Writes results/fig34_net_baselines.{png,pdf}, results/claims_e34.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, np, pick, plt, run_cells, save, summarize,
                           sweep, trials, use_style)
from configs.decentralized import dec_config

N = 8
GRAPH = "ring"
TS = pick([1000, 4000], [500])
LINKS = pick(["quadratic", "zigzag", "logistic"], ["quadratic", "logistic"])
NTR = trials(10, 2)
GAMMA = 0.5
N0 = 960                                       # pooled Phase-1 size at N·T = 160k (as E22–E31)

LABEL = {"relay": "Dec-ZoomSIB-Relay (ours)", "server": "ZoomSIB with a server",
         "indep": "independent ZoomSIB", "linucb": "DLUCB-style (LinUCB)",
         "estor": "Dec-ESTOR", "gstor": "Dec-GSTOR", "igpucb": "Coop-Kernel-style (IGP-UCB)"}
COLOR = {"relay": "#2a78d6", "server": "#1a1a1a", "indep": "#8a8984", "linucb": "#eb6834",
         "estor": "#eda100", "gstor": "#1baf7a", "igpucb": "#4a3aa7"}


def t0_for(T):
    return max(1, int(np.ceil(N0 * (N * T / 160_000) ** (2 / 3) / N)))


def configs(T):
    t0 = t0_for(T)
    c = {"relay": dec_config(GRAPH, "tree", {}, "flood", {"gamma": GAMMA}, T0=t0, bin_width="network"),
         "server": dec_config("complete", "server", {}, "server_event", {"gamma": GAMMA}, T0=t0,
                              bin_width="network"),
         "indep": dict(engine="indep", inner=dict(engine="fed", freeze="fixed", T0=t0 * N,
                                                  bin_width="network"))}
    for a in ("linucb", "estor", "gstor", "igpucb"):
        c[a] = dict(engine="netbase", graph=GRAPH, algo=a)
    # refit the GP every 25·N pooled points: as often per agent as single-agent IGP-UCB
    c["igpucb"]["algo_kw"] = dict(refit_every=25 * N)
    return c


def cell_fn(cell, names=None):
    link, T = cell
    c = {k: v for k, v in configs(T).items() if names is None or k in names}
    out, _ = sweep(c, NTR, N, T, link)
    return summarize(out)


def main():
    res = run_cells("e34", [(l, T) for l in LINKS for T in TS], cell_fn)
    use_style()
    fig, axes = plt.subplots(1, len(LINKS), figsize=(4.6 * len(LINKS), 3.8))
    axes = np.atleast_1d(axes)
    rows = []
    T = TS[-1]
    for ax, link in zip(axes, LINKS):
        r = res[(link, T)]
        keys = list(LABEL)
        vals = [r[k]["R"].mean() for k in keys]
        errs = [1.96 * r[k]["R"].std(ddof=1) / np.sqrt(len(r[k]["R"])) if len(r[k]["R"]) > 1 else 0
                for k in keys]
        ax.barh(range(len(keys)), vals, xerr=errs, color=[COLOR[k] for k in keys])
        ax.set_yticks(range(len(keys)), [LABEL[k] for k in keys], fontsize=7)
        ax.invert_yaxis()
        ax.set(xlabel="network regret", title=f"{link} link, N = {N}, T = {T:,}, {GRAPH}")
    fig.tight_layout()
    save(fig, "fig34_net_baselines")
    for link in LINKS:
        for T in TS:
            r = res[(link, T)]
            ref = r["relay"]["R"].mean()
            for k in LABEL:
                rows.append([link, f"{T:,}", LABEL[k], fmt(r[k]["R"]), f"{r[k]['R'].mean() / ref:.2f}",
                             f"{r[k]['comm'].mean():,.0f}"])
    intro = (f"N = {N} agents on a {GRAPH} (D = {N // 2}), d = 10, K = 20, σ = 0.1, {NTR} paired trials, "
             "mean ± 95% CI. Prior algorithms get IDEAL relaying: every raw observation reaches every "
             "agent after graph-distance rounds (d + 2 scalars per pull per receiving agent), an upper bound "
             "on the information their own gossip provides. IGP-UCB refits every 25·N pooled points (as often per agent as the single-agent version) on at most 400 points. ZoomSIB variants use pooled Phase-1 size "
             f"{N0}·(NT/160k)^(2/3). '÷ ours' is regret relative to Dec-ZoomSIB-Relay.")
    md_table(f"{OUT}/claims_e34.md", "E34: prior papers' algorithms on our problem, over a graph", intro,
             ["link", "T", "algorithm", "network regret", "÷ ours", "scalars"], rows)


if __name__ == "__main__":
    main()
