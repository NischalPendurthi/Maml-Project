"""E16 -- how much does the topology cost?  Twelve graphs, five decentralised designs.

One decentralised design per family, each on every undirected topology of
src/dec/graph/topologies.py (N = 16), against the federated reference (a
server) and N independent agents.  Regret is then read against the two graph
quantities theory says should matter: the spectral gap 1 − λ (consensus-type
methods) and the diameter (relay-type methods, whose information is stale by
graph distance).

Produces results/fig16_dec_topology.{pdf,png} and results/dec_topology_benchmark.md.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import FED_REFERENCE, INDEPENDENT, dec_config  # noqa: E402
from dec_common import N, run_cells, md_table                              # noqa: E402
from src.dec.graph import Graph                                            # noqa: E402
from src.plotting import save, use_style                                   # noqa: E402

GRAPHS = ["complete", "hypercube", "torus", "expander", "erdos", "smallworld", "star",
          "grid", "geometric", "barbell", "ring", "path"]
LINK = "quadratic"
CACHE = "results/exp16_dec_topology.cells"
DESIGNS = {
    "relay_event": ("flood", {}, "flood", {"gamma": 0.5}, "Flooding + event-triggered flooding",
                    "#2a78d6", "o"),
    "relay":       ("flood", {}, "flood", {}, "Flooding + flooding every round", "#9cc0ea", "o"),
    "consensus":   ("consensus", {"steps": 5}, "consensus", {}, "Running consensus (both)",
                    "#eb6834", "s"),
    "pushsum":     ("pushsum", {}, "pushsum", {}, "Push-sum (both)", "#e87ba4", "s"),
    "chebyshev":   ("chebyshev", {"k": 20}, "gossip", {"k": 5, "every": 10, "ess": True,
                                                       "accelerate": True},
                    "Chebyshev gossip + ESS gossip", "#1baf7a", "^"),
}


T0_FAIR = 60


def configs_for(cell):
    g = cell[0]
    cfgs = {k: dec_config(g, p1, k1, p2, k2, freeze="adaptive", label=lab)
            for k, (p1, k1, p2, k2, lab, _, _) in DESIGNS.items()}
    # Fair comparison: everyone freezes at the same round (see main()).
    for k, (p1, k1, p2, k2, lab, _, _) in DESIGNS.items():
        cfgs[k + "|fixed"] = dec_config(g, p1, k1, p2, k2, freeze="fixed", T0=T0_FAIR,
                                        label=f"{lab}, T0={T0_FAIR}")
    if g == "complete":
        cfgs["fed_reference"] = FED_REFERENCE
        cfgs["independent"] = INDEPENDENT
        for t0 in (35, T0_FAIR):
            cfgs[f"server|fixed{t0}"] = dec_config(g, "server", {}, "server_event", {"gamma": 0.5},
                                                   freeze="fixed", T0=t0,
                                                   label=f"Server + event sync, T0={t0}")
    return cfgs


def fair_plot(B, info):
    """Same-T0 comparison: regret ÷ server at the same T0, against gap and diameter."""
    import matplotlib.pyplot as plt

    c0 = ("complete", LINK, "iid")
    if "server|fixed60" not in B[c0]:
        return
    ref = B[c0][f"server|fixed{T0_FAIR}"]["R"].mean()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.0))
    for ax, xkey, xlab, xlog in ((axes[0], "gap", "spectral gap 1 − λ", True),
                                 (axes[1], "diameter", "diameter", False)):
        for k, (_, _, _, _, lab, col, mk) in DESIGNS.items():
            if k + "|fixed" not in B[c0]:
                continue
            x = [getattr(info[g], xkey) for g in GRAPHS]
            y = [B[(g, LINK, "iid")][k + "|fixed"]["R"].mean() / ref for g in GRAPHS]
            ax.scatter(x, y, color=col, marker=mk, s=30, edgecolors="white", linewidths=0.7,
                       label=lab, zorder=3)
        ax.axhline(1, color="#4a3aa7", lw=0.9, ls="--", label=f"server, same T0={T0_FAIR}")
        if xlog:
            ax.set_xscale("log")
        ax.set_xlabel(xlab)
        ax.set_ylabel(f"regret ÷ server at T0={T0_FAIR}")
    axes[0].legend(fontsize=6.5)
    fig.suptitle(f"E16 (fair) · cost of the topology at a fixed Phase-1 length T0={T0_FAIR}",
                 fontsize=10, y=1.03)
    save(fig, "fig16_dec_topology_fair")
    hdr = ["graph", "diameter", "gap"] + [DESIGNS[k][4] for k in DESIGNS]
    rows = [[g, info[g].diameter, f"{info[g].gap:.3f}"] +
            [f"{B[(g, LINK, 'iid')][k + '|fixed']['R'].mean() / ref:.3f}" for k in DESIGNS]
            for g in GRAPHS]
    rows.append(["server T0=35 / T0=60", "–", "–",
                 f"{B[c0]['server|fixed35']['R'].mean():.0f} / {ref:.0f}"] + [""] * (len(DESIGNS) - 1))
    md_table("results/dec_topology_fair.md", "E16 (fair) · topology at fixed T0",
             f"Regret ÷ server (event-triggered) at the same fixed T0 = {T0_FAIR}; N = {N}, {LINK}.",
             hdr, rows)


def main():
    os.makedirs("results", exist_ok=True)
    cells = [(g, LINK, "iid") for g in GRAPHS]
    B = run_cells(CACHE, cells, configs_for)
    info = {g: Graph(g, N, seed=0) for g in GRAPHS}
    ref = B[("complete", LINK, "iid")]["fed_reference"]["R"].mean()
    ind = B[("complete", LINK, "iid")]["independent"]["R"].mean()
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.3), gridspec_kw=dict(width_ratios=[1, 1, 1.25]))
    for ax, xkey, xlab, xlog in ((axes[0], "gap", "spectral gap 1 − λ (Metropolis)", True),
                                 (axes[1], "diameter", "diameter", False)):
        for k, (_, _, _, _, lab, col, mk) in DESIGNS.items():
            x = [getattr(info[g], xkey) for g in GRAPHS]
            y = [B[(g, LINK, "iid")][k]["R"].mean() / ref for g in GRAPHS]
            ax.scatter(x, y, color=col, marker=mk, s=30, edgecolors="white", linewidths=0.7,
                       label=lab, zorder=3)
        ax.axhline(1, color="#4a3aa7", lw=0.9, ls="--", label="federated reference (server)")
        ax.axhline(ind / ref, color="#8a8984", lw=0.9, ls=":", label="independent agents")
        if xlog:
            ax.set_xscale("log")
        ax.set_xlabel(xlab)
        ax.set_ylabel("network regret ÷ federated reference")
    for g in GRAPHS:
        axes[1].annotate(g, (info[g].diameter, B[(g, LINK, "iid")]["relay_event"]["R"].mean() / ref),
                         fontsize=6, color="#52514e", textcoords="offset points", xytext=(3, 3))
    axes[0].legend(fontsize=6.5)
    axes[0].set_title("consensus-type methods track the spectral gap", fontsize=9, loc="left")
    axes[1].set_title("relay-type methods track the diameter", fontsize=9, loc="left")
    ax = axes[2]
    for k, (_, _, _, _, lab, col, mk) in DESIGNS.items():
        x = [max(B[(g, LINK, "iid")][k]["comm"].mean(), 1) for g in GRAPHS]
        y = [B[(g, LINK, "iid")][k]["R"].mean() / ref for g in GRAPHS]
        ax.scatter(x, y, color=col, marker=mk, s=30, edgecolors="white", linewidths=0.7, zorder=3)
    ax.axhline(1, color="#4a3aa7", lw=0.9, ls="--")
    ax.set_xscale("log")
    ax.set_xlabel("total scalars communicated")
    ax.set_ylabel("regret ÷ federated reference")
    ax.set_title("cost of each design across the 12 graphs", fontsize=9, loc="left")
    fig.suptitle(f"E16 · Topology: 12 graphs × 5 decentralised designs (N={N}, {LINK})",
                 fontsize=11, y=1.02)
    save(fig, "fig16_dec_topology")

    hdr = ["graph", "edges", "diameter", "gap"] + [DESIGNS[k][4] for k in DESIGNS]
    rows = [[g, info[g].n_edges, info[g].diameter, f"{info[g].gap:.3f}"] +
            [f"{B[(g, LINK, 'iid')][k]['R'].mean():.0f} ({B[(g, LINK, 'iid')][k]['comm'].mean():.1e})"
             for k in DESIGNS] for g in GRAPHS]
    fair_plot(B, info)
    md_table("results/dec_topology_benchmark.md", "E16 · Topology sweep",
             f"Network regret (total scalars) per design and graph, N = {N}, {LINK}, 6 trials.  "
             f"Federated reference {ref:.0f}; independent agents {ind:.0f}.", hdr, rows)


if __name__ == "__main__":
    main()
