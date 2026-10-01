"""E6 -- what collaboration buys: network regret vs the number of agents N.

Configs (experiments/configs/): `independent`, `fed_p1_only`, `fed_zoomsib`.

Three things to look for:
  * per-agent Phase-1 length should fall like 1/N for the federated configs,
    so the NETWORK exploration cost N*T0 stays flat (`p8.lem-fed-stein`);
  * `fed_p1_only` vs `independent` isolates what ONE Phase-1 message buys;
  * `fed_zoomsib` vs `fed_p1_only` isolates what Phase-2 sharing buys, and the
    network regret should grow sub-linearly in N (`p8.coop-sleeping`).

Produces: results/fig06_fed_scaling.{pdf,png}, results/fig07_fed_phase1_length.{pdf,png}
Use --replot to redraw from the cached results/exp06_*.npz.
"""

from __future__ import annotations

import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import pick, style                                  # noqa: E402
from src.envs import LINK_LABEL                                  # noqa: E402
from src.fed import run_fed_sweep                                # noqa: E402
from src.plotting import band, save, use_style                   # noqa: E402
from src.runner import loglog_slope, mean_ci                     # noqa: E402

D, K, T = 10, 20, 10_000
SIGMA = 0.1
N_TRIALS = 8
RECORD_EVERY = 50
NS = [1, 2, 4, 8, 16]
LINKS = ["quadratic", "asymmetric", "zigzag", "logistic"]
CONFIGS = pick("independent", "fed_p1_only", "fed_zoomsib")
CACHE = "results/exp06_fed_scaling.pkl"


def simulate():
    res = {}
    for link in LINKS:
        for N in NS:
            print(f"[exp06] link={link} N={N}", flush=True)
            out, grid = run_fed_sweep(CONFIGS, N_TRIALS, N, D, K, T, link, sigma=SIGMA,
                                      record_every=RECORD_EVERY, progress=False)
            res[link, N] = dict(
                grid=grid,
                net={k: v["net"] for k, v in out.items()},
                T0={k: np.array([dg["T0_used"] for dg in v["diag"]], float)
                    for k, v in out.items()},
                comm={k: np.array([dg["comm_scalars"] for dg in v["diag"]], float)
                      for k, v in out.items()},
            )
    os.makedirs("results", exist_ok=True)
    with open(CACHE, "wb") as fh:
        pickle.dump(res, fh)
    return res


def plot(res):
    use_style()
    import matplotlib.pyplot as plt

    # ---- fig06: network regret vs N, one panel per link --------------------
    fig, axes = plt.subplots(1, len(LINKS), figsize=(15.0, 3.5))
    for ax, link in zip(axes, LINKS):
        for key, cfg in CONFIGS.items():
            m = np.array([res[link, N]["net"][key][:, -1].mean() for N in NS])
            h = np.array([mean_ci(res[link, N]["net"][key][:, -1:])[1][0] for N in NS])
            ax.errorbar(NS, m, yerr=h, marker="o", ms=4, capsize=2, **style(cfg))
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(NS, [str(n) for n in NS])
        ax.set_title(f"{link}\n{LINK_LABEL[link]}", fontsize=9)
        ax.set_xlabel("number of agents $N$")
    axes[0].set_ylabel(r"network regret $\sum_i R_{i,T}$")
    axes[-1].legend(loc="upper left", fontsize=7)
    fig.suptitle(f"E6 · Network regret vs number of agents "
                 f"(d={D}, K={K}, T={T:,} per agent, {N_TRIALS} trials, 95% CI)",
                 y=1.04, fontsize=10)
    save(fig, "fig06_fed_scaling")

    # ---- fig07: Phase-1 length and regret curves --------------------------
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.0, 3.5))
    link = "quadratic"
    for key, cfg in CONFIGS.items():
        t0 = np.array([np.mean(res[link, N]["T0"][key]) for N in NS])
        a1.plot(NS, t0, marker="o", ms=4, **style(cfg))
        a2.plot(NS, t0 * np.array(NS), marker="o", ms=4, **style(cfg))
    ref = np.mean(res[link, 1]["T0"]["fed_zoomsib"])
    a1.plot(NS, ref / np.array(NS), color="#0b0b0b", lw=0.8, ls=":", label=r"$\propto 1/N$")
    for ax, lab in ((a1, r"per-agent Phase-1 length $T_0$"),
                    (a2, r"network exploration $N\cdot T_0$")):
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(NS, [str(n) for n in NS])
        ax.set_xlabel("number of agents $N$")
        ax.set_ylabel(lab)
    a1.legend(fontsize=7)
    a1.set_title(f"Phase 1 shrinks per agent ({link})", fontsize=9)
    a2.set_title("…so network exploration grows far slower", fontsize=9)
    a1.text(0.97, 0.97, "both federated configs share Phase 1:\ntheir lines coincide",
            transform=a1.transAxes, ha="right", va="top", fontsize=7, color="#52514e")

    N = 8
    grid = res[link, N]["grid"]
    for key, cfg in CONFIGS.items():
        m, h = mean_ci(res[link, N]["net"][key])
        band(a3, grid, m, h, **style(cfg))
    a3.set_xlabel("round $t$ (per agent)")
    a3.set_ylabel("network regret")
    a3.set_title(f"N = {N} agents, {link}", fontsize=9)
    fig.suptitle("E6 · Federated Phase 1: exact pooling divides exploration by N",
                 y=1.04, fontsize=10)
    save(fig, "fig07_fed_phase1_length")

    # ---- table ------------------------------------------------------------
    for link in LINKS:
        print(f"\n  {link}: network regret R_T(N)  [per-agent T0]  {{scalars sent}}")
        print("    " + f"{'config':<42}" + "".join(f"{'N=' + str(n):>22}" for n in NS))
        for key, cfg in CONFIGS.items():
            row = f"    {cfg['label']:<42}"
            for N in NS:
                r = res[link, N]
                row += (f"{r['net'][key][:, -1].mean():>9.0f} [{r['T0'][key].mean():5.0f}]"
                        f"{{{r['comm'][key].mean():>.0e}}}")
            print(row)
        for key, cfg in CONFIGS.items():
            m = [res[link, N]["net"][key][:, -1].mean() for N in NS]
            s, _ = loglog_slope(NS, m, lo_frac=0.0)
            print(f"    slope of log R_T(N) vs log N   {cfg['label']:<42} {s:+.2f}")


def main():
    if "--replot" in sys.argv and os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            res = pickle.load(fh)
    else:
        res = simulate()
    plot(res)


if __name__ == "__main__":
    main()
