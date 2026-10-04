"""E19 -- does collaboration still pay without a server?  Network regret vs N.

Phase 1 has a fixed POOLED size (each agent explores 960 / N rounds), the
same for the server reference, so N changes only who has to talk to whom.

The two strongest decentralised designs on a ring (diameter N/2, gap ~ 1/N²),
a hypercube (diameter log N) and the complete graph, for N = 4 … 32, against
the federated reference and independent agents.  The question is whether the
√N-type scaling of E6 survives when information must travel hop by hop.

Produces results/fig19_dec_scaling.{pdf,png} and results/dec_scaling_benchmark.md.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import FED_REFERENCE, INDEPENDENT, dec_config   # noqa: E402
from dec_common import run_cells, md_table                                 # noqa: E402
from src.plotting import save, use_style                                   # noqa: E402

NS = [4, 8, 16, 32]
GRAPHS = ["complete", "hypercube", "ring"]
LINK = "quadratic"
CACHE = "results/exp19_dec_scaling.cells"
DESIGNS = {
    "relay_event": ("flood", {}, "flood", {"gamma": 0.5}, "Flooding + event flooding"),
    "chebyshev":   ("chebyshev", {"k": 20}, "gossip", {"k": 5, "every": 10, "ess": True,
                                                       "accelerate": True},
                    "Chebyshev + ESS gossip"),
}
STYLE = {"complete": "-", "hypercube": "--", "ring": ":"}
COLOR = {"relay_event": "#2a78d6", "chebyshev": "#1baf7a"}


POOLED_T0 = 960     # fixed POOLED Phase-1 size: each agent explores 960 / N rounds


def slope(ns, ys):
    """Exponent of y in N by least squares on log-log (all points)."""
    return float(np.polyfit(np.log(ns), np.log(ys), 1)[0])


def configs_for(cell):
    g, n = cell[0], cell[3]
    t0 = int(np.ceil(POOLED_T0 / n))
    cfgs = {k: dec_config(g, p1, k1, p2, k2, T0=t0, label=f"{lab} ({g})")
            for k, (p1, k1, p2, k2, lab) in DESIGNS.items()}
    if g == "complete":
        cfgs["fed_reference"] = FED_REFERENCE
        cfgs["independent"] = INDEPENDENT
        cfgs["server_fixed"] = dec_config(g, "server", {}, "server_event", {"gamma": 0.5}, T0=t0,
                                          label="Server + event sync, same T0")
    return cfgs


def main():
    os.makedirs("results", exist_ok=True)
    cells = [(g, LINK, "iid", n) for g in GRAPHS for n in NS]
    B = run_cells(CACHE, cells, configs_for)
    use_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    slopes = {}
    for g in GRAPHS:
        for k in DESIGNS:
            y = [B[(g, LINK, "iid", n)][k]["R"].mean() for n in NS]
            slopes[g, k] = slope(NS, y)
            ax.plot(NS, y, marker="o", ms=4, color=COLOR[k], ls=STYLE[g],
                    label=f"{DESIGNS[k][4]}, {g}  (slope {slopes[g, k]:.2f})")
    for ref, col, lab in (("server_fixed", "#4a3aa7", "server, same pooled T0"),
                          ("fed_reference", "#c3b8f0", "federated, adaptive stop"),
                          ("independent", "#8a8984", "independent agents")):
        y = [B[("complete", LINK, "iid", n)][ref]["R"].mean() for n in NS]
        slopes[ref] = slope(NS, y)
        ax.plot(NS, y, marker="s", ms=4, color=col, lw=2,
                label=f"{lab}  (slope {slopes[ref]:.2f})")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(NS, [str(n) for n in NS])
    ax.set_xlabel("number of agents N")
    ax.set_ylabel("network regret")
    ax.legend(fontsize=6.5)
    ax.set_title(f"E19 · Network regret vs N without a server ({LINK})", fontsize=10)
    save(fig, "fig19_dec_scaling")
    hdr = ["design"] + [f"N={n}" for n in NS] + ["exponent in N"]
    rows = [[f"{DESIGNS[k][4]}, {g}"] + [f"{B[(g, LINK, 'iid', n)][k]['R'].mean():.0f}" for n in NS]
            + [f"{slopes[g, k]:.2f}"] for g in GRAPHS for k in DESIGNS]
    rows += [[lab] + [f"{B[('complete', LINK, 'iid', n)][r]['R'].mean():.0f}" for n in NS]
             + [f"{slopes[r]:.2f}"] for r, lab in (("server_fixed", "Server, same pooled T0"),
                                                  ("fed_reference", "Federated, adaptive stop"),
                                                  ("independent", "Independent agents"))]
    md_table("results/dec_scaling_benchmark.md", "E19 · Scaling with N",
             f"Network regret, {LINK}, 6 trials, T = 10 000 per agent.", hdr, rows)


if __name__ == "__main__":
    main()
