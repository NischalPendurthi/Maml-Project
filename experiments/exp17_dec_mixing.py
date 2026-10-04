"""E17 -- which communication MATRIX?  Five mixing rules on five graphs.

Only consensus-type methods use the weights P (flooding and trees only need
the adjacency).  Each rule in src/dec/graph/mixing.py -- Metropolis, max-degree,
best-constant Laplacian, lazy, row-stochastic -- drives running consensus and
Chebyshev gossip on graphs chosen to separate them: irregular (star, barbell)
where row-stochastic weights are NOT doubly stochastic and so bias the
average, and regular ones (ring, torus, expander) where the rules differ only
in speed.  Also reports λ = max(|λ₂|, |λ_N|) of every (graph, rule).

Produces results/fig17_dec_mixing.{pdf,png} and results/dec_mixing_benchmark.md.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import FED_REFERENCE, T0_FAIR, dec_config       # noqa: E402
from dec_common import N, run_cells, md_table                              # noqa: E402
from src.dec.graph import MIXING, Graph                                    # noqa: E402
from src.plotting import heatmap, save, use_style                          # noqa: E402

GRAPHS = ["star", "barbell", "ring", "torus", "expander"]
MIXES = list(MIXING)
LINK = "quadratic"
CACHE = "results/exp17_dec_mixing.cells"
DESIGNS = {
    "consensus": ("consensus", {"steps": 5}, "consensus", {}, "Running consensus (both phases)"),
    "chebyshev": ("chebyshev", {"k": 20}, "gossip", {"k": 5, "every": 10, "ess": True,
                                                     "accelerate": True},
                  "Chebyshev gossip + ESS gossip"),
}


def configs_for(cell):
    g = cell[0]
    cfgs = {}
    for m in MIXES:
        for k, (p1, k1, p2, k2, lab) in DESIGNS.items():
            cfgs[f"{k}|{m}"] = dec_config(g, p1, k1, p2, k2, graph_kw=dict(mixing=m),
                                          freeze="adaptive", label=f"{lab}, {m}")
            cfgs[f"{k}|{m}|fixed"] = dec_config(g, p1, k1, p2, k2, graph_kw=dict(mixing=m),
                                                label=f"{lab}, {m}, T0={T0_FAIR}")
    if g == "star":
        cfgs["fed_reference"] = FED_REFERENCE
        cfgs["server|fixed"] = dec_config(g, "server", {}, "server_event", {"gamma": 0.5},
                                          label=f"Server + event sync, T0={T0_FAIR}")
    return cfgs


def main():
    os.makedirs("results", exist_ok=True)
    cells = [(g, LINK, "iid") for g in GRAPHS]
    B = run_cells(CACHE, cells, configs_for)
    ref = B[("star", LINK, "iid")]["fed_reference"]["R"].mean()
    lam = np.array([[Graph(g, N, mixing=m).lam for g in GRAPHS] for m in MIXES])
    ds = np.array([[Graph(g, N, mixing=m).doubly_stochastic for g in GRAPHS] for m in MIXES])
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 3.9))
    heatmap(axes[0], lam, MIXES, GRAPHS, cmap="Blues", vmin=0, vmax=1, fmt="{:.3f}",
            text=[[f"{lam[i, j]:.3f}" + ("" if ds[i, j] else " ✗DS") for j in range(len(GRAPHS))]
                  for i in range(len(MIXES))], fontsize=7)
    axes[0].set_title("λ = max(|λ₂|, |λ_N|)  (✗DS = not doubly stochastic)", fontsize=9, loc="left")
    for ax, k in zip(axes[1:], DESIGNS):
        R = np.array([[B[(g, LINK, "iid")][f"{k}|{m}"]["R"].mean() / ref for g in GRAPHS]
                      for m in MIXES])
        heatmap(ax, R, MIXES, GRAPHS, diverging_at=1.0, fmt="{:.2f}", fontsize=7)
        ax.set_title(f"{DESIGNS[k][4]}: regret ÷ federated reference", fontsize=9, loc="left")
    fig.suptitle(f"E17 · Mixing matrices (N={N}, {LINK}), adaptive stopping", fontsize=11, y=1.03)
    save(fig, "fig17_dec_mixing")
    c0 = ("star", LINK, "iid")
    if "server|fixed" in B[c0]:
        ref_f = B[c0]["server|fixed"]["R"].mean()
        fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))
        for ax, k in zip(axes, DESIGNS):
            Rf = np.array([[B[(g, LINK, "iid")][f"{k}|{m}|fixed"]["R"].mean() / ref_f for g in GRAPHS]
                           for m in MIXES])
            heatmap(ax, Rf, MIXES, GRAPHS, diverging_at=1.0, fmt="{:.2f}", fontsize=7)
            ax.set_title(f"{DESIGNS[k][4]}: regret ÷ server, both at T0={T0_FAIR}",
                         fontsize=9, loc="left")
        fig.suptitle(f"E17 (fair) · Mixing matrices at a fixed Phase-1 length", fontsize=11, y=1.03)
        save(fig, "fig17_dec_mixing_fair")
        md_table("results/dec_mixing_fair.md", "E17 (fair) · mixing at fixed T0",
                 f"Regret ÷ server (event sync) at the same T0 = {T0_FAIR} ({ref_f:.0f}); "
                 f"N = {N}, {LINK}.", ["mixing"] + [f"{k} {g}" for k in DESIGNS for g in GRAPHS],
                 [[m] + [f"{B[(g, LINK, 'iid')][f'{k}|{m}|fixed']['R'].mean() / ref_f:.3f}"
                         for k in DESIGNS for g in GRAPHS] for m in MIXES])
    hdr = ["mixing"] + [f"λ {g}" for g in GRAPHS] + \
          [f"R {k} {g}" for k in DESIGNS for g in GRAPHS]
    rows = [[m] + [f"{lam[i, j]:.3f}{'' if ds[i, j] else ' (not DS)'}" for j in range(len(GRAPHS))] +
            [f"{B[(g, LINK, 'iid')][f'{k}|{m}']['R'].mean():.0f}" for k in DESIGNS for g in GRAPHS]
            for i, m in enumerate(MIXES)]
    md_table("results/dec_mixing_benchmark.md", "E17 · Mixing matrices",
             f"N = {N}, {LINK}, 6 trials; federated reference {ref:.0f}.", hdr, rows)


if __name__ == "__main__":
    main()
