"""E3 -- dimension scaling (reproduces Dey et al. Fig. 1d).

ZoomSIB-UCB compresses a d-dimensional arm into a single scalar index before
it ever runs a bandit, so after Phase 1 the *bandit* problem is
one-dimensional regardless of d.  Only the direction-estimation cost should
grow with d.  IGP-UCB, which models the reward as an RKHS function of the full
context, has no such protection and should degrade much faster.

This experiment matters for the federated stage too: it isolates the
d-dependent part of the regret, which is precisely the part that one-shot
Stein averaging is expected to amortize across agents.

Produces: results/fig04_dim_scaling.{pdf,png}
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.plotting import save, use_style                        # noqa: E402
from src.runner import STYLE, mean_ci, run_sweep                # noqa: E402

DIMS = [5, 10, 20, 40, 80]
K, T = 20, 10_000
SIGMA = 0.1
N_TRIALS = 15
LINK = "quadratic"
ALGOS = ["linucb", "igpucb", "gstor", "zoomsib"]
ALGO_KW = {"igpucb": dict(max_points=250, refit_every=50)}


CACHE = "results/exp04_dim_scaling.npz"


def main(replot=False):
    os.makedirs("results", exist_ok=True)
    use_style()
    import matplotlib.pyplot as plt

    if replot:
        z = np.load(CACHE)
        final = {k: list(z[f"final_{k}"]) for k in ALGOS}
        half = {k: list(z[f"half_{k}"]) for k in ALGOS}
        t0_frac = list(z["t0"])
    else:
        final = {k: [] for k in ALGOS}
        half = {k: [] for k in ALGOS}
        t0_frac = []

        for d in DIMS:
            print(f"[exp04] d={d}", flush=True)
            curves, grid, diag = run_sweep(
                ALGOS, N_TRIALS, d, K, T, LINK, sigma=SIGMA, index_scale=1.0,
                record_every=50, algo_kw=ALGO_KW)
            for k in ALGOS:
                m, h = mean_ci(curves[k])
                final[k].append(m[-1])
                half[k].append(h[-1])
            t0 = [x["T0_used"] for x in diag["zoomsib"] if x]
            t0_frac.append(float(np.mean(t0)))

        np.savez_compressed(CACHE, dims=DIMS, t0=t0_frac,
                            **{f"final_{k}": np.array(final[k]) for k in ALGOS},
                            **{f"half_{k}": np.array(half[k]) for k in ALGOS})

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.5))

    ax = axes[0]
    for k in ALGOS:
        ax.errorbar(DIMS, final[k], yerr=half[k], marker="o", ms=4, capsize=2,
                    **STYLE[k])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks(DIMS); ax.set_xticklabels([str(d) for d in DIMS])
    ax.minorticks_off()
    ax.set_xlabel("dimension $d$")
    ax.set_ylabel(f"$R_T$ at $T={T:,}$")
    ax.set_title("Final regret vs. dimension")
    ax.legend(fontsize=7)

    ax = axes[1]
    base = {k: final[k][0] for k in ALGOS}
    for k in ALGOS:
        ax.plot(DIMS, [final[k][i] / base[k] for i in range(len(DIMS))],
                marker="o", ms=4, **STYLE[k])
    ax.set_xscale("log")
    ax.set_xticks(DIMS); ax.set_xticklabels([str(d) for d in DIMS])
    ax.minorticks_off()
    ax.set_xlabel("dimension $d$")
    ax.set_ylabel(r"$R_T(d)\,/\,R_T(d{=}5)$")
    ax.set_title("Relative inflation (lower = more robust)")
    ax.legend(fontsize=7)

    fig.suptitle(f"E3 · Dimension scaling (quadratic link, K={K}, "
                 f"{N_TRIALS} trials, 95% CI)", y=1.04, fontsize=10)
    save(fig, "fig04_dim_scaling")

    print("\n  Final regret by dimension:")
    head = "    " + f"{'algorithm':<26}" + "".join(f"{d:>12}" for d in DIMS)
    print(head)
    print("    " + "-" * (len(head) - 4))
    for k in ALGOS:
        print(f"    {STYLE[k]['label']:<26}"
              + "".join(f"{final[k][i]:>12.0f}" for i in range(len(DIMS))))
    print("\n    inflation from d=5 to d=80:")
    for k in ALGOS:
        print(f"      {STYLE[k]['label']:<26} {final[k][-1]/final[k][0]:.2f}x")
    print("\n    ZoomSIB Phase-1 length by d: "
          + ", ".join(f"d={d}:{n:.0f}" for d, n in zip(DIMS, t0_frac)))


if __name__ == "__main__":
    main(replot="--replot" in sys.argv)
