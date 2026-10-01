"""E8 -- Phase-2 federation strategies: regret vs communication (open problem `p8.e1`).

Configs: experiments/configs/phase2_variants.py (Phase 1 held fixed at exact
pooling) plus `independent` as the zero-communication reference.

Phase 1 needs a handful of messages; Phase 2 is where communication is spent.
This sweeps every Phase-2 strategy in src/fed/phase2/ -- periodic sync at nine
periods, event-triggered sync at three thresholds, serverless sharing on a ring
and on a complete graph, and no sharing -- and places each one on the
regret / communication plane.

What to look for: the periodic curve traces the trade-off frontier; a strategy
below-left of it is strictly better.  Event-triggered sync should buy
near-centralised regret for orders of magnitude less communication, because
it talks a lot only while the bin estimates are still moving.

Produces: results/fig09_phase2_strategies.{pdf,png}.  --replot redraws from cache.
"""

from __future__ import annotations

import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import PHASE2_VARIANTS, ZOOMSIB                      # noqa: E402
from src.envs import LINK_LABEL                                  # noqa: E402
from src.fed import run_fed_sweep                                # noqa: E402
from src.plotting import band, save, use_style                   # noqa: E402
from src.runner import mean_ci                                   # noqa: E402

D, K, T = 10, 20, 10_000
SIGMA = 0.1
N = 8
N_TRIALS = 8
LINKS = ["quadratic", "zigzag"]
CONFIGS = {**PHASE2_VARIANTS, **ZOOMSIB}
CACHE = "results/exp08_phase2_strategies.pkl"

FAMILY = {  # how each config is drawn on the trade-off plane
    "periodic": dict(color="#2a78d6", marker="o"),
    "event":    dict(color="#eb6834", marker="s"),
    "neighbor": dict(color="#1baf7a", marker="^"),
    "none":     dict(color="#4a3aa7", marker="D"),
}


def family(cfg):
    return cfg.get("phase2", "independent")


def simulate():
    res = {}
    for link in LINKS:
        print(f"[exp08] link={link}", flush=True)
        out, grid = run_fed_sweep(CONFIGS, N_TRIALS, N, D, K, T, link, sigma=SIGMA,
                                  record_every=50, progress=False)
        res[link] = dict(grid=grid, **{
            k: dict(net=v["net"],
                    comm=np.array([dg["comm_scalars"] for dg in v["diag"]], float),
                    rounds=np.array([dg["comm_rounds"] for dg in v["diag"]], float))
            for k, v in out.items()})
    os.makedirs("results", exist_ok=True)
    with open(CACHE, "wb") as fh:
        pickle.dump(res, fh)
    return res


def plot(res):
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.0),
                             gridspec_kw=dict(width_ratios=[1.15, 1.15, 1.0]))
    for ax, link in zip(axes[:2], LINKS):
        r = res[link]
        ind = r["independent"]["net"][:, -1].mean()
        ax.axhline(ind, color="#8a8984", ls="--", lw=1.2,
                   label=f"{N} × ZoomSIB-UCB, zero comm.")
        per = sorted((k for k in r if k.startswith("p2_periodic_")),
                     key=lambda k: CONFIGS[k]["phase2_kw"]["every"])
        xs = [r[k]["comm"].mean() for k in per]
        ys = [r[k]["net"][:, -1].mean() for k in per]
        ax.plot(xs, ys, lw=1.2, **{k: v for k, v in FAMILY["periodic"].items()
                                   if k != "marker"}, zorder=1)
        for k, cfg in CONFIGS.items():
            fam = family(cfg)
            if fam == "independent":
                continue
            x, y = r[k]["comm"].mean(), r[k]["net"][:, -1].mean()
            first = not any(family(CONFIGS[j]) == fam for j in list(CONFIGS)[:list(CONFIGS).index(k)])
            ax.scatter([x], [y], s=34, zorder=3, edgecolors="white", linewidths=0.8,
                       label={"periodic": "periodic server sync", "event": "event-triggered sync",
                              "neighbor": "peer-to-peer (ring / complete)",
                              "none": "no Phase-2 sharing"}[fam] if first else None,
                       **FAMILY[fam])
            short = (f"C={cfg['phase2_kw']['every']}" if fam == "periodic" else
                     f"γ={cfg['phase2_kw']['gamma']:g}" if fam == "event" else
                     cfg["phase2_kw"]["graph"] if fam == "neighbor" else "")
            if short and (fam != "periodic" or cfg["phase2_kw"]["every"] in (1, 10, 100, 1000)):
                below = fam == "neighbor" and short == "complete"
                ax.annotate(short, (x, y), textcoords="offset points",
                            xytext=(-10, -12) if below else (4, 4),
                            fontsize=6.5, color="#52514e")
        ax.set_xscale("log")
        ax.set_xlabel("total scalars communicated (whole network, both directions)")
        ax.set_ylabel("network regret $R_T$")
        ax.set_title(f"{link}  {LINK_LABEL[link]}", fontsize=9)
        ax.set_ylim(0, ind * 1.12)
    axes[0].legend(fontsize=7, loc="upper right", bbox_to_anchor=(1.0, 0.92))

    ax = axes[2]
    link = LINKS[0]
    g = res[link]["grid"]
    for k, lab, col, ls in [("independent", f"{N} × ZoomSIB (no comm.)", "#8a8984", "--"),
                            ("p2_none", "exact Phase 1, no Phase-2 sharing", "#4a3aa7", "-."),
                            ("p2_periodic_1000", "periodic, C=1000", "#9cc0ea", "-"),
                            ("p2_event_1", "event-triggered, γ=1", "#eb6834", "-"),
                            ("p2_periodic_1", "periodic, C=1 (centralised)", "#2a78d6", "-")]:
        m, h = mean_ci(res[link][k]["net"])
        band(ax, g, m, h, label=lab, color=col, ls=ls)
    ax.set_xlabel("round $t$ (per agent)")
    ax.set_ylabel("network regret")
    ax.set_title(f"regret over time, {link}", fontsize=9)
    ax.legend(fontsize=6.5, loc="upper left")
    fig.suptitle(f"E8 · Phase-2 sharing strategies: regret vs communication "
                 f"(N={N}, d={D}, K={K}, T={T:,}, {N_TRIALS} trials)", y=1.03, fontsize=10)
    fig.subplots_adjust(wspace=0.3)
    save(fig, "fig09_phase2_strategies")

    for link in LINKS:
        r = res[link]
        print(f"\n  {link}:   network regret      scalars sent    comm rounds")
        for k, cfg in CONFIGS.items():
            print(f"    {cfg['label']:<34} {r[k]['net'][:, -1].mean():9.0f}"
                  f"   {r[k]['comm'].mean():13,.0f}   {r[k]['rounds'].mean():9,.0f}")


def main():
    if "--replot" in sys.argv and os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            res = pickle.load(fh)
    else:
        res = simulate()
    plot(res)


if __name__ == "__main__":
    main()
