"""E15 -- decentralised Phase 2: sharing the bin table over a communication graph.

Every strategy in src/dec/phase2/ on four graphs.  Phase 1 is held at exact
spanning-tree pooling with an agreement step, so all agents bin with the same
θ̂ and only the table sharing differs.  References: the federated version
(server, event-triggered) and N independent agents.

What to look for: flooding is exact but stale by up to the diameter; running
consensus / push-sum send their whole state every round; burst gossip with
naive counts is over-confident before mixing, which effective-sample-size
counts fix; one-hop sharing never pools beyond neighbours.

Produces results/fig15_dec_phase2.{pdf,png} and results/dec_phase2_benchmark.md.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import (DEC_P2, FAMILY_COLOR, FED_REFERENCE,  # noqa: E402
                                   INDEPENDENT, P2_FAMILY, P2_LABEL, dec_config)
from dec_common import N, run_cells, ratio_table, md_table              # noqa: E402
from src.plotting import heatmap, save, use_style                       # noqa: E402

GRAPHS = ["expander", "torus", "star", "ring"]
LINKS = ["quadratic", "zigzag"]
CACHE = "results/exp15_dec_phase2.cells"
KEYS = list(DEC_P2)


def configs_for(cell):
    graph = cell[0]
    cfgs = {"fed_reference": FED_REFERENCE, "independent": INDEPENDENT}
    for key in KEYS:
        name, kw = DEC_P2[key]
        # tree pooling gives every agent the same estimate, so adaptive stopping
        # behaves exactly like the server's and needs no fixed T0 here
        cfgs[key] = dec_config(graph, "tree", {}, name, kw, agree="exact", freeze="adaptive",
                               stop_rule="any", label=P2_LABEL[key])
    return cfgs


def main():
    os.makedirs("results", exist_ok=True)
    cells = [(g, l, "iid") for g in GRAPHS for l in LINKS]
    B = run_cells(CACHE, cells, configs_for)
    use_style()
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(16.5, 7.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.35,
                          left=0.17, right=0.99, top=0.86, bottom=0.17)
    names = KEYS + ["independent"]
    ax = fig.add_subplot(gs[0])
    R = ratio_table(B, cells, names, "fed_reference")
    heatmap(ax, R, [P2_LABEL.get(k, "Independent agents") for k in names],
            [f"{c[0]}·{c[1][:4]}" for c in cells], diverging_at=1.0, fmt="{:.2f}", fontsize=6.5)
    ax.set_title("network regret ÷ federated reference (server, event-triggered)\n"
                 "Phase 1 fixed at exact tree pooling · blue = better", fontsize=9, loc="left")

    ax = fig.add_subplot(gs[1])
    c0 = ("ring", "quadratic", "iid")
    c1 = ("expander", "quadratic", "iid")
    seen = set()
    for k in KEYS:
        fam = P2_FAMILY[k]
        for c, mk in ((c0, "o"), (c1, "s")):
            b = B[c][k]
            ax.scatter([max(b["comm"].mean(), 1)], [b["R"].mean()], s=34, marker=mk,
                       color=FAMILY_COLOR[fam], edgecolors="white", linewidths=0.8, zorder=3,
                       label=fam if (fam, mk) not in seen and mk == "o" else None)
            seen.add((fam, mk))
    for c, mk, lab in ((c0, "o", "ring"), (c1, "s", "expander")):
        ax.scatter([], [], marker=mk, color="#52514e", label=f"{lab} (marker)")
        ax.axhline(B[c]["fed_reference"]["R"].mean(), color="#4a3aa7", lw=0.8,
                   ls="--" if mk == "o" else ":")
    ax.set_xscale("log")
    ax.set_xlabel("total scalars communicated")
    ax.set_ylabel("network regret (quadratic)")
    ax.set_title("regret vs communication · dashed/dotted = federated reference on ring/expander",
                 fontsize=9, loc="left")
    ax.legend(fontsize=6.5, loc="upper right")
    fig.suptitle(f"E15 · Decentralised Phase 2: sharing the bin table over a graph (N={N})",
                 fontsize=11)
    save(fig, "fig15_dec_phase2")

    hdr = ["strategy", "family"] + [f"R {c[0]}·{c[1]}" for c in cells] + \
          ["scalars ring·quad", "scalars expander·quad"]
    rows = []
    for k in KEYS + ["fed_reference", "independent"]:
        lab = P2_LABEL.get(k, B[cells[0]][k]["label"])
        rows.append([lab, P2_FAMILY.get(k, "reference")] +
                    [f"{B[c][k]['R'].mean():.0f}" for c in cells] +
                    [f"{B[c0][k]['comm'].mean():,.0f}", f"{B[c1][k]['comm'].mean():,.0f}"])
    md_table("results/dec_phase2_benchmark.md", "E15 · Decentralised Phase 2",
             f"N = {N}, T = 10 000 per agent, 6 trials; Phase 1 = exact tree pooling + agreement.",
             hdr, rows)


if __name__ == "__main__":
    main()
