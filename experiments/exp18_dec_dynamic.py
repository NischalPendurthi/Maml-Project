"""E18 -- unreliable and directed links.

  failure q    every edge is down independently w.p. q each round (q = 0 … 0.9)
  matching     randomised pairwise gossip: one random matching per round
  directed     a strongly connected digraph with unequal out-degrees

Consensus with locally computed weights is exact on a static undirected graph,
loses speed when links fail, and is BIASED on a digraph; push-sum is designed
for both; flooding only needs eventual delivery; Chebyshev acceleration assumes
it knows λ of a fixed P, which a failing graph violates.

All designs and the server reference freeze at the same fixed T0, so the
comparison is about communication only.

Produces results/fig18_dec_dynamic.{pdf,png} and results/dec_dynamic_benchmark.md.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import FED_REFERENCE, dec_config                # noqa: E402
from dec_common import N, run_cells, md_table                              # noqa: E402
from src.plotting import heatmap, save, use_style                          # noqa: E402

LINK = "quadratic"
CACHE = "results/exp18_dec_dynamic.cells"
QS = [0.0, 0.3, 0.6, 0.9]
SETTINGS = ([(f"torus q={q}", "torus", dict(failure=q)) for q in QS] +
            [(f"expander q={q}", "expander", dict(failure=q)) for q in QS] +
            [("torus matching", "torus", dict(matching=True)),
             ("expander matching", "expander", dict(matching=True)),
             ("directed", "directed", {})])
DESIGNS = {
    "relay":     ("flood", {}, "flood", {"gamma": 0.5}, "Flooding + event flooding"),
    "consensus": ("consensus", {"steps": 5}, "consensus", {}, "Running consensus"),
    "pushsum":   ("pushsum", {}, "pushsum", {}, "Push-sum"),
    "chebyshev": ("chebyshev", {"k": 20}, "gossip", {"k": 5, "every": 10, "ess": True,
                                                     "accelerate": True}, "Chebyshev + ESS gossip"),
}


def configs_for(cell):
    name = cell[0]
    _, graph, gkw = next(s for s in SETTINGS if s[0] == name)
    cfgs = {k: dec_config(graph, p1, k1, p2, k2, graph_kw=gkw, label=lab)
            for k, (p1, k1, p2, k2, lab) in DESIGNS.items()}
    if name == "directed":
        cfgs["fed_reference"] = FED_REFERENCE
        cfgs["server_fixed"] = dec_config("ring", "server", {}, "server_event", {"gamma": 0.5},
                                          label="Server + event sync, same T0")
    return cfgs


def main():
    os.makedirs("results", exist_ok=True)
    cells = [(s[0], LINK, "iid") for s in SETTINGS]
    B = run_cells(CACHE, cells, configs_for)
    ref = B[("directed", LINK, "iid")]["server_fixed"]["R"].mean()     # same fixed T0
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.4), gridspec_kw=dict(width_ratios=[1, 1.5]))
    fig.subplots_adjust(wspace=0.42, bottom=0.2)
    cols = {"relay": "#2a78d6", "consensus": "#eb6834", "pushsum": "#e87ba4", "chebyshev": "#1baf7a"}
    for k in DESIGNS:
        for g, ls in (("torus", "-"), ("expander", "--")):
            y = [B[(f"{g} q={q}", LINK, "iid")][k]["R"].mean() / ref for q in QS]
            axes[0].plot(QS, y, marker="o", ms=4, color=cols[k], ls=ls,
                         label=f"{DESIGNS[k][4]} ({g})")
    axes[0].axhline(1, color="#4a3aa7", lw=0.8, ls=":")
    axes[0].set_xlabel("link failure probability q")
    axes[0].set_ylabel("network regret ÷ server (same T0)")
    axes[0].set_title("random link failures", fontsize=9, loc="left")
    axes[0].legend(fontsize=6)
    R = np.array([[B[(s[0], LINK, "iid")][k]["R"].mean() / ref for s in SETTINGS] for k in DESIGNS])
    heatmap(axes[1], R, [DESIGNS[k][4] for k in DESIGNS], [s[0] for s in SETTINGS],
            diverging_at=1.0, fmt="{:.2f}", fontsize=6.5)
    axes[1].set_title("all settings: regret ÷ server (same T0)", fontsize=9, loc="left")
    fig.suptitle(f"E18 · Link failures, randomised gossip and directed graphs (N={N}, {LINK})",
                 fontsize=11, y=1.03)
    save(fig, "fig18_dec_dynamic")
    hdr = ["setting"] + [DESIGNS[k][4] for k in DESIGNS]
    rows = [[s[0]] + [f"{B[(s[0], LINK, 'iid')][k]['R'].mean():.0f} "
                      f"({B[(s[0], LINK, 'iid')][k]['comm'].mean():.1e})" for k in DESIGNS]
            for s in SETTINGS]
    md_table("results/dec_dynamic_benchmark.md", "E18 · Dynamic and directed links",
             f"Network regret (scalars), N = {N}, {LINK}, 6 trials; server (same T0) {ref:.0f}.",
             hdr, rows)


if __name__ == "__main__":
    main()
