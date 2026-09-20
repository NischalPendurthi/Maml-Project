"""E0 -- Stein estimator convergence rate.

The single most important diagnostic in the whole project: if
||theta_hat_0 - theta_*||_1 does not decay like n^{-1/2}, nothing downstream
can work.  It is also the quantity that the federated extension will improve:
with N agents the effective sample size becomes N*n, so this curve shifts left
by a factor N.  Establishing the single-agent slope now is what makes that
claim measurable later.

Produces: results/fig01_stein_rate.{pdf,png}
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.envs import SIBEnv                                    # noqa: E402
from src.plotting import band, save, use_style                 # noqa: E402
from src.runner import loglog_slope                            # noqa: E402
from src.stein import l1_error, stein_estimate, tau_default    # noqa: E402

LINK = "quadratic"
DIMS = [5, 10, 20, 40]
N_GRID = np.unique(np.round(np.logspace(1.7, 4.7, 22)).astype(int))   # ~50 .. 50k
N_TRIALS = 30
SIGMA = 0.1
DELTA = 0.01


def run():
    out = np.zeros((len(DIMS), len(N_GRID), N_TRIALS))
    for di, d in enumerate(DIMS):
        for tr in range(N_TRIALS):
            env = SIBEnv(d=d, K=20, link=LINK, sigma=SIGMA, seed=1000 + tr,
                         run_seed=50_000 + tr, index_scale=1.0)
            rng = np.random.default_rng(7000 + tr)
            n_max = int(N_GRID[-1])
            X = rng.standard_normal((n_max, d)) * env.ctx_std
            S = env.score(X)
            y = env.f(X @ env.theta_star) + SIGMA * rng.standard_normal(n_max)
            for ni, n in enumerate(N_GRID):
                tau = tau_default(SIGMA, env.L_f, env.M, n, d, DELTA)
                th = stein_estimate(S[:n], y[:n], tau=tau, normalize=True)
                out[di, ni, tr] = l1_error(th, env.theta_star)
        print(f"  d={d} done", flush=True)
    np.savez_compressed("results/exp01_stein_rate.npz",
                        err=out, n_grid=N_GRID, dims=DIMS)
    return out


def plot(err):
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4))

    ax = axes[0]
    colors = plt.cm.viridis(np.linspace(0.05, 0.8, len(DIMS)))
    slopes = []
    for di, d in enumerate(DIMS):
        m = err[di].mean(axis=1)
        se = err[di].std(axis=1, ddof=1) / np.sqrt(err.shape[2])
        band(ax, N_GRID, m, 1.96 * se, color=colors[di], label=f"$d={d}$")
        s, _ = loglog_slope(N_GRID, m, lo_frac=0.25)
        slopes.append(s)
    ref = err[1].mean(axis=1)[0] * (N_GRID / N_GRID[0]) ** -0.5
    ax.plot(N_GRID, ref, color="crimson", ls="--", lw=1.2,
            label=r"reference $n^{-1/2}$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Phase-1 samples $n$")
    ax.set_ylabel(r"$\|\hat\theta_0-\theta_*\|_1$")
    ax.set_title("Truncated Stein estimator: convergence")
    ax.legend(ncol=2)

    ax = axes[1]
    ax.bar([str(d) for d in DIMS], [-s for s in slopes],
           color=colors, width=0.6)
    ax.axhline(0.5, color="crimson", ls="--", lw=1.2, label=r"theory $1/2$")
    ax.set_ylim(0, 0.75)
    ax.set_xlabel("dimension $d$")
    ax.set_ylabel(r"fitted decay exponent $-\,$slope")
    ax.set_title("Empirical rate vs. theory")
    for i, s in enumerate(slopes):
        ax.text(i, -s + 0.02, f"{-s:.3f}", ha="center", fontsize=8)
    ax.legend()

    fig.suptitle(r"E0 $\cdot$ Stein direction estimation "
                 "(quadratic link, 30 trials, 95% CI)", y=1.02, fontsize=10)
    save(fig, "fig01_stein_rate")
    return slopes


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    print("[exp01] Stein convergence rate")
    err = run()
    slopes = plot(err)
    print("\n  fitted log-log slopes (theory: -0.5):")
    for d, s in zip(DIMS, slopes):
        print(f"    d={d:3d}  slope={s:+.4f}")
    print("\n  error at n=1000 by dimension:")
    ni = int(np.argmin(np.abs(N_GRID - 1000)))
    for di, d in enumerate(DIMS):
        print(f"    d={d:3d}  n={N_GRID[ni]:5d}  err={err[di, ni].mean():.4f}")
