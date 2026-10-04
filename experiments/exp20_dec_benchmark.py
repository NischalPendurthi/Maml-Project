"""E20 -- combined decentralised leaderboard: Phase-1 strategy × Phase-2 strategy.

Five Phase-1 strategies × five Phase-2 strategies on a ring, a torus and an
expander, with iid and covariate-shifted agents, plus the federated reference
and independent agents.  Phase-1 hyperparameters come from E14's tuning
(results/dec_tuned_phase1.json) when available.

Every decentralised design (and a server reference run in the same engine)
freezes at the SAME fixed round T0_FAIR, so differences are due to
communication alone -- with adaptive stopping, agents that disagree explore
longer, which confounds topology with Phase-1 length (found in E16).

Leaderboard columns as in E12: geometric-mean regret ratio to the best config
in each cell, mean rank, worst cell, and communication on the torus.

Produces results/fig20_dec_benchmark.{pdf,png} and results/dec_benchmark.md.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import (FED_REFERENCE, INDEPENDENT, P1_LABEL,   # noqa: E402
                                   P2_LABEL, dec_config, dec_from_keys)
from dec_common import N, run_cells, md_table                              # noqa: E402
from src.plotting import heatmap, save, use_style                          # noqa: E402

GRAPHS = ["ring", "torus", "expander"]
SCENARIOS = ["iid", "covariate"]
LINK = "quadratic"
P1 = ["flood", "tree", "chebyshev", "consensus", "pushsum"]
P2 = ["flood", "flood_event", "cheb_ess", "consensus", "pushsum"]
CACHE = "results/exp20_dec_benchmark.cells"


def tuned():
    try:
        with open("results/dec_tuned_phase1.json") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None


T0_FAIR = 60     # every design freezes at the same round, so only communication differs


def configs_for(cell):
    g = cell[0]
    t = tuned()
    cfgs = {f"{a} + {b}": dec_from_keys(g, a, b, t, freeze="fixed", T0=T0_FAIR)
            for a in P1 for b in P2}
    cfgs["server_fixed"] = dec_config(g, "server", {}, "server_event", {"gamma": 0.5},
                                      freeze="fixed", T0=T0_FAIR,
                                      label=f"Server + event-triggered server sync, T0={T0_FAIR}")
    cfgs["fed_reference"] = FED_REFERENCE
    cfgs["independent"] = INDEPENDENT
    return cfgs


def main():
    os.makedirs("results", exist_ok=True)
    cells = [(g, LINK, s) for g in GRAPHS for s in SCENARIOS]
    B = run_cells(CACHE, cells, configs_for)
    names = list(B[cells[0]])
    M = np.array([[B[c][n]["R"].mean() for c in cells] for n in names])
    ratio = M / M.min(axis=0, keepdims=True)
    ranks = M.argsort(axis=0).argsort(axis=0) + 1
    tor = ("torus", LINK, "iid")
    board = sorted(({"name": n, "gm": float(np.exp(np.log(ratio[i]).mean())),
                     "rank": float(ranks[i].mean()), "worst": float(ratio[i].max()),
                     "comm": float(B[tor][n]["comm"].mean())} for i, n in enumerate(names)),
                   key=lambda r: r["gm"])

    def label(n):
        if n in ("fed_reference", "independent", "server_fixed"):
            return B[cells[0]][n]["label"]
        a, b = n.split(" + ")
        return f"{P1_LABEL[a]} + {P2_LABEL[b]}"

    use_style()
    import matplotlib.pyplot as plt

    order = [names.index(b["name"]) for b in board]
    fig, ax = plt.subplots(figsize=(13, 9))
    heatmap(ax, ratio[order], [f"{label(names[i])}   ×{board[j]['gm']:.2f} · "
                               f"{board[j]['comm']:.1e} sc."
                               for j, i in enumerate(order)],
            [f"{c[0]}·{c[2]}" for c in cells], diverging_at=1.0, fmt="{:.2f}", fontsize=6.5)
    ax.set_title(f"E20 · regret ÷ best in cell, sorted by geometric mean "
                 f"(N={N}, {LINK}); text = geo-mean ratio · scalars on torus", fontsize=9,
                 loc="left")
    fig.subplots_adjust(left=0.42, right=0.99, top=0.95, bottom=0.08)
    save(fig, "fig20_dec_benchmark")
    hdr = ["#", "configuration", "regret ÷ best", "mean rank", "worst cell", "scalars (torus·iid)"] + \
          [f"R {c[0]}·{c[2]}" for c in cells]
    rows = [[i + 1, label(b["name"]), f"{b['gm']:.3f}", f"{b['rank']:.1f}", f"{b['worst']:.2f}",
             f"{b['comm']:,.0f}"] + [f"{B[c][b['name']]['R'].mean():.0f}" for c in cells]
            for i, b in enumerate(board)]
    md_table("results/dec_benchmark.md", "E20 · Decentralised leaderboard",
             f"N = {N}, {LINK}, 6 trials per cell.", hdr, rows)
    for r in rows[:12]:
        print("   ", r[:6])


if __name__ == "__main__":
    main()
