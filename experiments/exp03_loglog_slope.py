"""E2 -- log-log regret scaling (reproduces Dey et al. Fig. 1a).

Reads the arrays cached by exp02 -- no extra simulation.  On log-log axes the
slope of the cumulative-regret curve is the scaling exponent:

    R_T ~ T^alpha   =>   log R_T = alpha log T + const

Theory says ZoomSIB-UCB has alpha <= 2/3 (and that 2/3 is minimax-optimal for
general non-monotone links), while GSTOR's guarantee is only alpha <= 3/4.
Dey et al. report an empirical slope of 0.53 for ZoomSIB-UCB -- below the
worst-case ceiling, because the bound is tight only on adversarial instances.

Produces: results/fig03_loglog_slope.{pdf,png}
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.envs import LINK_LABEL                      # noqa: E402
from src.plotting import save, use_style             # noqa: E402
from src.runner import STYLE, loglog_slope           # noqa: E402

LINKS = ["quadratic", "asymmetric", "zigzag", "logistic"]
SHOW = ["linucb", "igpucb", "estor", "gstor", "zoomsib"]


def main():
    use_style()
    import matplotlib.pyplot as plt

    missing = [l for l in LINKS if not os.path.exists(f"results/exp02_{l}.npz")]
    if missing:
        sys.exit(f"missing cached results for {missing}; run exp02 first")

    fig, axes = plt.subplots(1, 4, figsize=(15.0, 3.5))
    table = {}

    for li, link in enumerate(LINKS):
        z = np.load(f"results/exp02_{link}.npz")
        grid = z["grid"]
        ax = axes[li]
        for key in SHOW:
            m = z[key].mean(axis=0)
            ax.plot(grid, m, **STYLE[key])
            s, _ = loglog_slope(grid, m, lo_frac=0.3)
            table.setdefault(key, {})[link] = s

        # reference slopes anchored at the ZoomSIB curve's midpoint
        mid = len(grid) // 2
        anchor = z["zoomsib"].mean(axis=0)[mid]
        for alpha, col, lab in [(2 / 3, "crimson", r"$T^{2/3}$ (optimal)"),
                                (3 / 4, "darkorange", r"$T^{3/4}$ (GSTOR)"),
                                (1.0, "0.55", r"$T^{1}$ (linear)")]:
            ref = anchor * (grid / grid[mid]) ** alpha
            ax.plot(grid, ref, color=col, ls=(0, (2, 2)), lw=1.0,
                    label=lab if li == 0 else None)

        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(f"{link}\n{LINK_LABEL[link]}", fontsize=9)
        ax.set_xlabel("round $t$")
        if li == 0:
            ax.set_ylabel("cumulative regret $R_t$")
            ax.legend(fontsize=7, loc="upper left")
        if li == len(LINKS) - 1:
            ax.legend([STYLE[k]["label"] for k in SHOW], fontsize=7,
                      loc="lower right")

    fig.suptitle("E2 · Log-log regret scaling — fitted exponent over the last 70% "
                 "of the horizon", y=1.04, fontsize=10)
    save(fig, "fig03_loglog_slope")

    print("\n  Fitted scaling exponent alpha  (R_T ~ T^alpha):")
    head = "    " + f"{'algorithm':<26}" + "".join(f"{l:>13}" for l in LINKS)
    print(head)
    print("    " + "-" * (len(head) - 4))
    for key in SHOW:
        row = f"    {STYLE[key]['label']:<26}"
        for link in LINKS:
            row += f"{table[key][link]:>13.3f}"
        print(row)
    print("\n    theory: ZoomSIB-UCB <= 0.667,  GSTOR <= 0.75,  "
          "misspecified LinUCB -> 1.0")


if __name__ == "__main__":
    main()
