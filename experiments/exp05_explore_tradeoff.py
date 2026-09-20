"""E4 -- the Phase-1 exploration trade-off, and validation of adaptive stopping.

ZoomSIB-UCB's theoretical exploration length T_0 = d^2 T^{2/3} polylog(dT/delta)
exceeds every horizon we can simulate, so Dey et al. replace it with an
adaptive stopping rule.  This experiment measures what the rule is trying to
find: sweep a FIXED T_0 and plot final regret, so the optimum is visible.

Two things come out of it:
  * the optimum sits at roughly 2% of the horizon, matching the ~1.8% that
    Dey et al. report for the quadratic link in Section 6;
  * the adaptive rule (marked on the plot) lands close to that optimum without
    being told T_0 or mu_*.

This is also the quantity the federated extension targets: with N agents the
same estimation accuracy should be reachable from ~T_0/N rounds each, so this
curve is the single-agent reference for that claim.

Produces: results/fig05_explore_tradeoff.{pdf,png}
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base import run_episode                     # noqa: E402
from src.envs import SIBEnv                          # noqa: E402
from src.plotting import save, use_style             # noqa: E402
from src.runner import build                         # noqa: E402

D, K = 10, 20
SIGMA = 0.1
N_TRIALS = 15
HORIZONS = [5_000, 20_000]
LINKS = ["quadratic", "zigzag"]
T0_GRID = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400]


def sweep(link, T):
    fixed = {}
    for T0 in T0_GRID:
        if T0 > 0.5 * T:
            continue
        vals = []
        for s in range(N_TRIALS):
            env = SIBEnv(d=D, K=K, link=link, sigma=SIGMA, seed=1000 + s,
                         run_seed=50_000 + s, index_scale=1.0)
            algo = build("zoomsib", env, T, np.random.default_rng(9000 + s),
                         T0=T0, adaptive_stop=False)
            cum, _ = run_episode(env, algo, T)
            vals.append(cum[-1])
        fixed[T0] = (float(np.mean(vals)),
                     1.96 * float(np.std(vals, ddof=1)) / np.sqrt(N_TRIALS))

    ad_r, ad_n = [], []
    for s in range(N_TRIALS):
        env = SIBEnv(d=D, K=K, link=link, sigma=SIGMA, seed=1000 + s,
                     run_seed=50_000 + s, index_scale=1.0)
        algo = build("zoomsib", env, T, np.random.default_rng(9000 + s))
        cum, _ = run_episode(env, algo, T)
        ad_r.append(cum[-1])
        ad_n.append(algo.diagnostics()["T0_used"])

    orc = []
    for s in range(N_TRIALS):
        env = SIBEnv(d=D, K=K, link=link, sigma=SIGMA, seed=1000 + s,
                     run_seed=50_000 + s, index_scale=1.0)
        algo = build("zoomsib_oracle", env, T, np.random.default_rng(9000 + s))
        cum, _ = run_episode(env, algo, T)
        orc.append(cum[-1])

    return fixed, (float(np.mean(ad_r)), float(np.mean(ad_n))), float(np.mean(orc))


def main():
    os.makedirs("results", exist_ok=True)
    use_style()
    import matplotlib.pyplot as plt

    CACHE = "results/exp05_explore_tradeoff.npz"
    replot = "--replot" in sys.argv
    cache = dict(np.load(CACHE, allow_pickle=True)) if replot else {}

    panels = [(l, T) for l in LINKS for T in HORIZONS]
    fig, axes = plt.subplots(1, len(panels), figsize=(3.7 * len(panels), 3.4))
    report = []

    for ax, (link, T) in zip(np.atleast_1d(axes), panels):
        key = f"{link}_{T}"
        if replot:
            xs_c, ys_c, hs_c, extra = (cache[key + "_xs"], cache[key + "_ys"],
                                       cache[key + "_hs"], cache[key + "_extra"])
            fixed = {int(x): (float(y), float(h)) for x, y, h in zip(xs_c, ys_c, hs_c)}
            ad_r, ad_n, orc = (float(extra[0]), float(extra[1]), float(extra[2]))
        else:
            print(f"[exp05] {link}, T={T}", flush=True)
            fixed, (ad_r, ad_n), orc = sweep(link, T)
        xs = np.array(sorted(fixed))
        ys = np.array([fixed[x][0] for x in xs])
        hs = np.array([fixed[x][1] for x in xs])
        if not replot:
            cache[key + "_xs"], cache[key + "_ys"] = xs, ys
            cache[key + "_hs"] = hs
            cache[key + "_extra"] = np.array([ad_r, ad_n, orc])

        ax.errorbar(100 * xs / T, ys, yerr=hs, marker="o", ms=4, capsize=2,
                    color="#1f77b4", label="fixed $T_0$")
        ax.axhline(orc, color="#17becf", ls=(0, (3, 1, 1, 1)), lw=1.3,
                   label=r"oracle $\theta_*$")
        ax.plot([100 * ad_n / T], [ad_r], marker="*", ms=14, ls="none",
                color="crimson", label="adaptive stopping")
        best = xs[int(np.argmin(ys))]
        ax.axvline(100 * best / T, color="0.6", ls=":", lw=1.0)

        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("Phase-1 length $T_0$ (% of horizon)")
        ax.set_title(f"{link}, $T={T:,}$", fontsize=9)
        if ax is np.atleast_1d(axes)[0]:
            ax.set_ylabel("final regret $R_T$")
            ax.legend(fontsize=7)
        report.append((link, T, best, 100 * best / T, ys.min(),
                       ad_n, 100 * ad_n / T, ad_r, orc))

    if not replot:
        np.savez_compressed(CACHE, **cache)

    fig.suptitle("E4 · Phase-1 exploration trade-off "
                 f"(d={D}, K={K}, {N_TRIALS} trials, 95% CI)",
                 y=1.04, fontsize=10)
    save(fig, "fig05_explore_tradeoff")

    print("\n  Optimal vs. adaptive Phase-1 length:")
    print(f"    {'link':<11}{'T':>8}{'best T0':>10}{'(%)':>8}{'R_T*':>10}"
          f"{'adapt T0':>10}{'(%)':>8}{'R_T adapt':>11}{'oracle':>10}")
    print("    " + "-" * 86)
    for r in report:
        print(f"    {r[0]:<11}{r[1]:>8,}{r[2]:>10}{r[3]:>8.2f}{r[4]:>10.0f}"
              f"{r[5]:>10.0f}{r[6]:>8.2f}{r[7]:>11.0f}{r[8]:>10.0f}")


if __name__ == "__main__":
    main()
