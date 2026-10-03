"""E12 -- the combined benchmark: Phase-1 FL method × Phase-2 FL method.

exp10 and exp11 each vary ONE phase with the other held exact.  This crosses a
shortlist from each -- the exact method, its strongest iterative competitor
and a plain-averaging representative per phase, plus the communication-saving
schedules -- and ranks every pairing across all four heterogeneity scenarios
and both links, with N independent ZoomSIB-UCB agents as the zero-communication
floor.  Hyperparameters come from results/fl_tuned_phase{1,2}.json (run
exp10 and exp11 first).

Leaderboard columns
  regret ÷ best   geometric mean, over the 8 (scenario, link) cells, of the
                  config's network regret divided by the best config in that cell
  mean rank       average rank across the cells (1 = best)
  worst cell      largest regret ratio in any cell (robustness)
  scalars         total communication, iid · quadratic

Produces results/fig12_fl_benchmark.{pdf,png} and results/fl_benchmark.md.
--replot redraws from the cache.
"""

from __future__ import annotations

import json
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import LABEL, ZOOMSIB, fl_phase1_config, fl_phase2_config   # noqa: E402
from src.fed import SCENARIOS, run_fed_sweep                             # noqa: E402
from src.fed.runner import resumable_cells                               # noqa: E402
from src.plotting import heatmap, save, use_style                        # noqa: E402

D, K, T, SIGMA, N = 10, 20, 10_000, 0.1, 8
LINKS = ["quadratic", "zigzag"]
N_TRIALS = 8
REDO = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--redo=")), None)
CACHE = "results/exp12_fl_benchmark.pkl"

# shortlists -- (key, kwargs for the config builder, short label)
PHASE1 = [
    ("suffstat", {}, "P1 suff.stats"),
    ("fedsgd", {}, "P1 FedSGD×10"),
    ("scaffold", {}, "P1 SCAFFOLD×10"),
    ("oneshot", {}, "P1 one-shot FedAvg"),
]
PHASE2 = [
    ("suffstat", dict(every=1), "P2 suff.stats, every round"),
    ("suffstat", dict(every=10), "P2 suff.stats, every 10"),
    ("suffstat", dict(gamma=0.5), "P2 suff.stats, event γ=0.5"),
    ("scaffold", dict(every=10, rounds=5), "P2 SCAFFOLD×5, every 10"),
    ("fedavgm", dict(every=10, rounds=5), "P2 FedAvgM×5, every 10"),
    ("fedavg", dict(every=10, rounds=5), "P2 FedAvg×5, every 10"),
]


def load_tuned():
    try:
        with open("results/fl_tuned_phase1.json") as fh:
            t1 = json.load(fh)["stein"]
        with open("results/fl_tuned_phase2.json") as fh:
            t2 = json.load(fh)
    except FileNotFoundError:
        sys.exit("run experiments/exp10_fl_phase1.py and exp11_fl_phase2.py first")
    return t1, t2


def build_configs():
    t1, t2 = load_tuned()
    cfgs = {}
    for k1, kw1, l1 in PHASE1:
        c1 = fl_phase1_config(k1, t1, **kw1)
        for k2, kw2, l2 in PHASE2:
            c2 = fl_phase2_config(k2, t2, **kw2)
            name = f"{l1} + {l2}"
            cfgs[name] = dict(engine="fed",
                              phase1=c1["phase1"], phase1_kw=c1["phase1_kw"],
                              phase2=c2["phase2"], phase2_kw=c2["phase2_kw"],
                              label=name)
    cfgs["independent"] = dict(ZOOMSIB["independent"], label="N × ZoomSIB-UCB, no comm.")
    return cfgs


def simulate(cfgs):
    def cell(sl, names=None):
        s, link = sl
        run = {k: v for k, v in cfgs.items() if names is None or any(t in k for t in names)}
        print(f"[exp12] scenario={s} link={link}", flush=True)
        out, _ = run_fed_sweep(run, N_TRIALS, N, D, K, T, link, sigma=SIGMA,
                               record_every=T, progress=False, scenario=s)
        return {name: dict(R=v["net"][:, -1],
                           comm=np.array([dg["comm_scalars"] for dg in v["diag"]], float),
                           rounds=np.array([dg["comm_rounds"] for dg in v["diag"]], float))
                for name, v in out.items()}

    cells = resumable_cells(CACHE + ".cells", [(s, l) for s in SCENARIOS for l in LINKS], cell,
                            redo=REDO)
    return {(s, l, name): v for (s, l), res in cells.items() for name, v in res.items()}


def leaderboard(cfgs, res):
    cells = [(s, l) for s in SCENARIOS for l in LINKS]
    names = list(cfgs)
    M = np.array([[res[s, l, n]["R"].mean() for (s, l) in cells] for n in names])
    ratio = M / M.min(axis=0, keepdims=True)
    ranks = M.argsort(axis=0).argsort(axis=0) + 1
    board = []
    for i, n in enumerate(names):
        board.append(dict(name=n, gm=float(np.exp(np.log(ratio[i]).mean())),
                          rank=float(ranks[i].mean()), worst=float(ratio[i].max()),
                          comm=float(res["iid", "quadratic", n]["comm"].mean()),
                          rounds=float(res["iid", "quadratic", n]["rounds"].mean())))
    board.sort(key=lambda r: r["gm"])
    return board, cells, names, M, ratio


def plot(cfgs, res):
    use_style()
    import matplotlib.pyplot as plt

    board, cells, names, M, ratio = leaderboard(cfgs, res)
    order = [names.index(b["name"]) for b in board]
    fig = plt.figure(figsize=(16, 9.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.08,
                          left=0.24, right=0.985, top=0.88, bottom=0.1)
    ax = fig.add_subplot(gs[0])
    heatmap(ax, ratio[order], [names[i] for i in order], [f"{s}·{l[:4]}" for s, l in cells],
            diverging_at=1.0, fmt="{:.2f}", fontsize=6.8)
    ax.set_title("network regret ÷ best config in the cell (blue = closest to best)",
                 fontsize=9, loc="left")

    ax = fig.add_subplot(gs[1])
    y = np.arange(len(board))
    gm = np.array([b["gm"] for b in board])
    ax.barh(y, gm, color=["#2a78d6" if b["comm"] > 0 else "#8a8984" for b in board],
            height=0.65)
    for yi, b in zip(y, board):
        ax.text(b["gm"], yi, f"  ×{b['gm']:.2f} · rank {b['rank']:.1f} · "
                f"{b['comm']:,.0f} scalars", va="center", fontsize=6.8, color="#0b0b0b")
    ax.set_yticks(y, [])
    ax.invert_yaxis()
    ax.set_xlim(1, gm.max() * 1.9)
    ax.set_xlabel("geometric-mean regret ratio to the best (1 = always best)")
    ax.set_title("leaderboard · bar = regret ratio, text = rank and communication (iid·quad)",
                 fontsize=9, loc="left")
    fig.suptitle(f"E12 · Phase-1 × Phase-2 FL method, all scenarios and links "
                 f"(N={N}, T={T:,}, {N_TRIALS} trials)", fontsize=11)
    save(fig, "fig12_fl_benchmark")
    return board, cells, names, M


def write_markdown(cfgs, res, board, cells, names, M):
    L = ["# E12 · Combined FL benchmark (Phase-1 method × Phase-2 method)", "",
         f"N = {N}, d = {D}, K = {K}, T = {T:,}, {N_TRIALS} trials per cell; "
         "scenarios × links = " + ", ".join(f"{s}·{l}" for s, l in cells) + ".", "",
         "## Leaderboard", "",
         "| # | configuration | regret ÷ best (geo-mean) | mean rank | worst cell | "
         "scalars (iid·quad) | comm rounds |",
         "|---:|---|---:|---:|---:|---:|---:|"]
    for i, b in enumerate(board, 1):
        L.append(f"| {i} | {b['name']} | {b['gm']:.3f} | {b['rank']:.1f} | {b['worst']:.2f} "
                 f"| {b['comm']:,.0f} | {b['rounds']:,.0f} |")
    L += ["", "## Network regret per cell (mean over trials)", "",
          "| configuration | " + " | ".join(f"{s} · {l}" for s, l in cells) + " |",
          "|---|" + "---:|" * len(cells)]
    for b in board:
        i = names.index(b["name"])
        L.append(f"| {b['name']} | " + " | ".join(f"{v:.0f}" for v in M[i]) + " |")
    with open("results/fl_benchmark.md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("  wrote results/fl_benchmark.md")
    print("\n  leaderboard (regret ÷ best, mean rank, worst cell, scalars):")
    for i, b in enumerate(board, 1):
        print(f"    {i:>2}. {b['name']:<58} ×{b['gm']:.3f}  rank {b['rank']:4.1f}  "
              f"worst ×{b['worst']:.2f}  {b['comm']:>12,.0f}")


def main():
    os.makedirs("results", exist_ok=True)
    if "--replot" in sys.argv and os.path.exists(CACHE) and not REDO:
        with open(CACHE, "rb") as fh:
            cfgs, res = pickle.load(fh)
    else:
        cfgs = build_configs()
        res = simulate(cfgs)
        with open(CACHE, "wb") as fh:
            pickle.dump((cfgs, res), fh)
    board, cells, names, M = plot(cfgs, res)
    write_markdown(cfgs, res, board, cells, names, M)


if __name__ == "__main__":
    main()
