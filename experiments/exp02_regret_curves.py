"""E1 -- main reproduction: cumulative regret for every algorithm, four links.

This is the Phase-1 deliverable.  It reproduces the qualitative content of
Figure 1 of Dey, Bhore & Ghosh (2026) and establishes the single-agent
reference that every federated claim will later be measured against.

Three things to look for:
  * on the three NON-monotone links, ZoomSIB-UCB should sit below GSTOR;
  * ESTOR (which assumes monotonicity) should be strong on `logistic` and
    poor on `quadratic`/`asymmetric`;
  * LinUCB is misspecified throughout and should grow close to linearly.

Produces: results/fig02_regret_curves.{pdf,png} and a summary table.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.envs import LINK_LABEL                                 # noqa: E402
from src.plotting import band, save, use_style                  # noqa: E402
from src.runner import STYLE, loglog_slope, mean_ci, run_sweep  # noqa: E402

D, K, T = 10, 20, 20_000
SIGMA = 0.1
N_TRIALS = 20
RECORD_EVERY = 20
LINKS = ["quadratic", "asymmetric", "zigzag", "logistic"]
ALGOS = ["random", "linucb", "igpucb", "estor", "gstor", "zoomsib", "zoomsib_oracle"]

# Keep IGP-UCB affordable: cap the conditioning set and refresh the posterior
# every 50 rounds rather than every round.
ALGO_KW = {"igpucb": dict(max_points=250, refit_every=50)}


def main():
    os.makedirs("results", exist_ok=True)
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(15.0, 3.5))
    summary = {}
    explore_frac = {}

    for li, link in enumerate(LINKS):
        print(f"[exp02] link={link}", flush=True)
        curves, grid, diag = run_sweep(
            ALGOS, N_TRIALS, D, K, T, link, sigma=SIGMA, index_scale=1.0,
            record_every=RECORD_EVERY, algo_kw=ALGO_KW)
        np.savez_compressed(f"results/exp02_{link}.npz", grid=grid,
                            **{k: v for k, v in curves.items()})

        t0 = [x["T0_used"] for x in diag["zoomsib"] if x]
        explore_frac[link] = (float(np.mean(t0)), float(np.mean(t0)) / T)

        ax = axes[li]
        for key in ALGOS:
            m, h = mean_ci(curves[key])
            band(ax, grid, m, h, **STYLE[key])
            summary.setdefault(key, {})[link] = (m[-1], h[-1])
        ax.set_title(f"{link}\n{LINK_LABEL[link]}", fontsize=9)
        ax.set_xlabel("round $t$")
        if li == 0:
            ax.set_ylabel("cumulative regret $R_t$")
        if li == len(LINKS) - 1:
            ax.legend(loc="upper left", fontsize=7)

    fig.suptitle(f"E1 · Single-agent reproduction  "
                 f"(d={D}, K={K}, T={T:,}, σ={SIGMA}, {N_TRIALS} trials, 95% CI)",
                 y=1.04, fontsize=10)
    save(fig, "fig02_regret_curves")

    # ---- table -------------------------------------------------------
    print("\n  Final cumulative regret R_T (mean ± 95% CI half-width):")
    head = "    " + f"{'algorithm':<26}" + "".join(f"{l:>20}" for l in LINKS)
    print(head)
    print("    " + "-" * (len(head) - 4))
    for key in ALGOS:
        row = f"    {STYLE[key]['label']:<26}"
        for link in LINKS:
            m, h = summary[key][link]
            row += f"{m:>13.0f} ±{h:>5.0f}"
        print(row)

    print("\n  ZoomSIB-UCB adaptive stopping (Phase-1 length):")
    for link in LINKS:
        n, frac = explore_frac[link]
        print(f"    {link:<12} T0 = {n:7.1f}  ({100*frac:.2f}% of horizon)")

    print("\n  log-log regret slope over the last 70% of the horizon:")
    for link in LINKS:
        z = np.load(f"results/exp02_{link}.npz")
        g = z["grid"]
        line = f"    {link:<12}"
        for key in ["zoomsib", "gstor", "linucb"]:
            s, _ = loglog_slope(g, z[key].mean(axis=0), lo_frac=0.3)
            line += f"  {STYLE[key]['label']}={s:+.3f}"
        print(line)


if __name__ == "__main__":
    main()
