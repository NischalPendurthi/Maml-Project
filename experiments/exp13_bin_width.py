"""E13 -- the bin width for N agents: Δ = T^{-1/3} (single-agent) vs Δ = (NT)^{-1/3}.

ZoomSIB-UCB's Δ = T^{-1/3} balances, for ONE agent, the discretisation bias
L·T·Δ against the UCB term √(T/Δ).  With N agents sharing the bin table the
balance is between N·T·Δ and √(NT/Δ), giving Δ = (NT)^{-1/3} and network regret
Õ((NT)^{2/3}) -- the single-agent rate for NT samples, i.e. the centralised
lower bound.  This measures whether the network choice actually helps, using
the recommended configuration (exact Phase 1, event-triggered exact Phase 2).

Produces results/fig13_bin_width.{pdf,png}.  --replot redraws from the cache.
"""

from __future__ import annotations

import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fed import run_fed_sweep                                # noqa: E402
from src.plotting import save, use_style                         # noqa: E402
from src.runner import loglog_slope, mean_ci                     # noqa: E402

D, K, T, SIGMA = 10, 20, 10_000, 0.1
NS = [1, 2, 4, 8, 16]
LINKS = ["quadratic", "zigzag"]
N_TRIALS = 8
CACHE = "results/exp13_bin_width.pkl"
BASE = dict(engine="fed", phase1="exact", phase2="fl",
            phase2_kw=dict(method="suffstat", gamma=0.5))
CONFIGS = {
    "agent":   dict(BASE, bin_width="agent", label="Δ = T^{-1/3} (single-agent)",
                    style=dict(color="#8a8984", ls="--")),
    "network": dict(BASE, bin_width="network", label="Δ = (NT)^{-1/3} (network)",
                    style=dict(color="#2a78d6", ls="-")),
}


def simulate():
    res = {}
    for link in LINKS:
        for N in NS:
            print(f"[exp13] link={link} N={N}", flush=True)
            out, _ = run_fed_sweep(CONFIGS, N_TRIALS, N, D, K, T, link, sigma=SIGMA,
                                   record_every=T, progress=False)
            for k, v in out.items():
                res[link, N, k] = dict(R=v["net"][:, -1],
                                       bins=np.array([dg["N_bins"] for dg in v["diag"]], float))
    with open(CACHE, "wb") as fh:
        pickle.dump(res, fh)
    return res


def plot(res):
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(LINKS), figsize=(10.5, 3.6))
    print("\n  network regret (bins)  and fitted exponent in N")
    for ax, link in zip(axes, LINKS):
        for k, cfg in CONFIGS.items():
            m = np.array([res[link, N, k]["R"].mean() for N in NS])
            h = np.array([mean_ci(res[link, N, k]["R"][:, None])[1][0] for N in NS])
            ax.errorbar(NS, m, yerr=h, marker="o", ms=4, capsize=2,
                        label=cfg["label"], **cfg["style"])
            s, _ = loglog_slope(NS, m, lo_frac=0.0)
            print(f"    {link:<10} {cfg['label']:<30} slope {s:+.2f}   " + "  ".join(
                f"N={N}:{res[link, N, k]['R'].mean():.0f}({res[link, N, k]['bins'].mean():.0f})"
                for N in NS))
        ref = res[link, 1, "agent"]["R"].mean()
        ax.plot(NS, ref * np.array(NS, float) ** (2 / 3), color="#0b0b0b", lw=0.8, ls=":",
                label=r"$\propto N^{2/3}$ (centralised rate)")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(NS, [str(n) for n in NS])
        ax.set_xlabel("number of agents $N$")
        ax.set_title(link, fontsize=9)
    axes[0].set_ylabel("network regret")
    axes[0].legend(fontsize=7)
    fig.suptitle(f"E13 · Bin width for N agents (exact Phase 1 + event-triggered Phase 2, "
                 f"T={T:,} per agent, {N_TRIALS} trials)", y=1.03, fontsize=10)
    save(fig, "fig13_bin_width")


def main():
    if "--replot" in sys.argv and os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            res = pickle.load(fh)
    else:
        res = simulate()
    plot(res)


if __name__ == "__main__":
    main()
