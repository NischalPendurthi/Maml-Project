"""E14 -- decentralised Phase 1: pooling θ over a communication graph, no server.

Every strategy in src/dec/phase1/ is compared on several graphs.

Part A (offline).  N = 16 agents stream uniformly-pulled Phase-1 samples for
T_A rounds; interleaved strategies communicate every round, burst strategies
at the same pooled-size checkpoints the engine uses.  At the end:
  * consensus error   mean_i ‖θ̂_i − θ̂_pooled‖₁  (0 = every agent has the
                      server's answer)
  * disagreement      mean_i ‖θ̂_i − mean θ̂‖₁
  * communication     scalars sent so far
Each strategy's best grid point (geometric-mean consensus error over graphs)
is saved to results/dec_tuned_phase1.json.

Part B (bandit).  Each tuned strategy pools θ inside the decentralised engine;
Phase 2 is held at exact server sync so only θ pooling differs.  Agents keep
their own θ̂_i (no agreement step).

Produces results/fig14_dec_phase1.{pdf,png} and results/dec_phase1_benchmark.md.
"""

from __future__ import annotations

import json
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.decentralized import (DEC_P1, FED_REFERENCE, INDEPENDENT,   # noqa: E402
                                   P1_LABEL, dec_config, p1_kwargs)
from dec_common import N, REPLOT, run_cells, ratio_table, md_table       # noqa: E402
from src.base import env_info_from                                       # noqa: E402
from src.dec.graph import Graph                                          # noqa: E402
from src.dec.phase1 import make_dec_phase1                               # noqa: E402
from src.fed import make_fed_envs                                        # noqa: E402
from src.fed.engine import Agent                                         # noqa: E402
from src.fed.phase1.base import local_V, truncated                       # noqa: E402
from src.plotting import heatmap, save, use_style                        # noqa: E402
from src.stein import l1_error, normalize_l1, tau_default                 # noqa: E402

D, K, SIGMA = 10, 20, 0.1
GRAPHS_A = ["complete", "expander", "torus", "star", "barbell", "ring", "directed"]
GRAPHS_B = ["expander", "torus", "star", "ring"]
LINKS = ["quadratic", "zigzag"]
T_A, REPS = 40, 10
KEYS = list(DEC_P1)
CACHE_A = "results/exp14_dec_phase1_A.pkl"
CACHE_B = "results/exp14_dec_phase1_B.cells"
TUNED = "results/dec_tuned_phase1.json"


def part_a_cell(args):
    graph, rep = args
    g = Graph(graph, N, seed=0)
    envs = make_fed_envs(N, D, K, "quadratic", SIGMA, seed=5000 + rep, run_seed=rep)
    agents = [Agent(i, None, env_info_from(e)) for i, e in enumerate(envs)]
    e0 = envs[0]
    strategies = {}
    for key in KEYS:
        if key == "tree" and not g.symmetric:
            continue
        name, fixed, grid, _ = DEC_P1[key]
        for gi, kw in enumerate(grid):
            s = make_dec_phase1(name, **dict(fixed, **kw))
            s.setup(N, D, g)
            strategies[key, gi] = dict(s=s, comm=0, rounds=0, est=None)
    next_check = max(50, 5 * D)
    for t in range(1, T_A + 1):
        g.step()
        for ag, env in zip(agents, envs):
            X = env.draw_arms()
            a = int(env.rng.integers(K))
            ag.S_buf.append(env.score(X[a])); ag.y_buf.append(env.pull(X, a)); ag.X_buf.append(X[a])
        tau = tau_default(e0.sigma, e0.L_f, e0.M, N * t, D, 0.01)
        b = np.array([truncated(local_V(ag), tau).sum(0) for ag in agents])
        n = np.array([ag.n for ag in agents], float)
        check = N * t >= next_check or t == T_A
        if N * t >= next_check:
            next_check = int(np.ceil(N * t * 1.5))
        for st in strategies.values():
            s = st["s"]
            if s.interleaved:
                st["comm"] += s.on_round(t, b, n)
                st["rounds"] += 1
            if check:
                est, sc, r = s.estimate(t, b, n)
                st["comm"] += sc
                st["rounds"] += r
                st["est"] = est
    pooled = normalize_l1(b.sum(0))
    out = {}
    for (key, gi), st in strategies.items():
        th = np.array([normalize_l1(e) for e in st["est"]])
        out[key, gi] = dict(
            cons=float(np.mean([l1_error(x, pooled) for x in th])),
            true=float(np.mean([l1_error(x, e0.theta_star) for x in th])),
            disagree=float(np.abs(th - th.mean(0)).sum(1).mean()),
            comm=st["comm"], rounds=st["rounds"])
    return graph, rep, out


def run_part_a():
    jobs = [(g, r) for g in GRAPHS_A for r in range(REPS)]
    A = {}
    with ProcessPoolExecutor(max_workers=min(os.cpu_count() or 1, 12)) as ex:
        for g, r, out in ex.map(part_a_cell, jobs, chunksize=1):
            A[g, r] = out
    return A


def tune(A):
    tuned, best = {}, {}
    for key in KEYS:
        grid = DEC_P1[key][2]
        scores = []
        for gi in range(len(grid)):
            errs = [A[g, r][key, gi]["cons"] for g in GRAPHS_A for r in range(REPS)
                    if (key, gi) in A[g, r]]
            scores.append(float(np.exp(np.mean(np.log(np.maximum(errs, 1e-12))))))
        best[key] = int(np.argmin(scores))
        tuned[key] = grid[best[key]]
    return tuned, best


def summarise_a(A, best):
    S = {}
    for g in GRAPHS_A:
        for key in KEYS:
            cells = [A[g, r][key, best[key]] for r in range(REPS) if (key, best[key]) in A[g, r]]
            if not cells:
                continue
            S[g, key] = {m: float(np.mean([c[m] for c in cells]))
                         for m in ("cons", "true", "disagree", "comm", "rounds")}
    return S


# Stopping-rule variants for the strategies whose agents end Phase 1 with
# DIFFERENT estimates (exact strategies give every agent the same one).
STOP_KEYS = ["flood", "consensus", "pushsum", "gossip", "gt", "local"]
T0_FIXED = 35          # the federated reference's measured Phase-1 length at N = 16


def configs_for(cell, tuned):
    graph = cell[0]
    cfgs = {"fed_reference": FED_REFERENCE, "independent": INDEPENDENT}
    for key in KEYS:
        if key == "tree" and graph == "directed":
            continue
        name, kw = p1_kwargs(key, tuned)
        cfgs[key] = dec_config(graph, name, kw, "server", {}, stop_rule="any",
                               freeze="adaptive", label=P1_LABEL[key])
        if key in STOP_KEYS:
            cfgs[key + "|all"] = dec_config(graph, name, kw, "server", {}, stop_rule="all",
                                            freeze="adaptive", label=P1_LABEL[key] + ", stop when ALL stable")
            cfgs[key + "|fixed"] = dec_config(graph, name, kw, "server", {}, freeze="fixed",
                                              T0=T0_FIXED,
                                              label=P1_LABEL[key] + f", fixed T0={T0_FIXED}")
    return cfgs


def plot(S, tuned, B, cells):
    use_style()
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(17, 7.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 0.6, 1.1], wspace=0.45,
                          left=0.1, right=0.99, top=0.86, bottom=0.2)
    rows = [k for k in KEYS]
    ax = fig.add_subplot(gs[0])
    V = np.array([[S.get((g, k), {}).get("cons", np.nan) for g in GRAPHS_A] for k in rows])
    txt = [[("–" if not np.isfinite(v) else "0" if v < 1e-9 else f"{v:.0e}" if v < 0.01
             else f"{v:.2f}") for v in row] for row in V]
    heatmap(ax, np.where(np.isfinite(V), np.maximum(V, 1e-12), np.nan), [P1_LABEL[k] for k in rows],
            GRAPHS_A, log=True, cmap="Blues", vmin=-9, vmax=0, text=txt, fontsize=6.5)
    ax.set_title(f"A · consensus error  mean_i ‖θ̂_i − θ̂_pooled‖₁\n"
                 f"after {T_A} rounds, N={N}, tuned (0 = server's answer)", fontsize=9, loc="left")

    ax = fig.add_subplot(gs[1])
    C = np.array([[S.get((g, k), {}).get("comm", np.nan) for g in ("ring", "expander")]
                  for k in rows])
    heatmap(ax, np.maximum(C, 1), [""] * len(rows), ["ring", "expander"], log=True,
            cmap="Greys", text=[[("–" if not np.isfinite(v) else f"{v:,.0f}") for v in row]
                                for row in C], fontsize=6.5)
    ax.set_title("scalars sent\n(Phase 1 only)", fontsize=9, loc="left")

    ax = fig.add_subplot(gs[2])
    names = [k for k in KEYS] + ["independent"]
    R = ratio_table(B, cells, names, "fed_reference")
    heatmap(ax, R, [P1_LABEL.get(k, "Independent agents") for k in names],
            [f"{c[0]}·{c[1][:4]}" for c in cells], diverging_at=1.0, fmt="{:.2f}", fontsize=6.5)
    ax.set_title("B · bandit: network regret ÷ federated reference\n"
                 "(Phase 2 fixed at exact server sync; blue = better)", fontsize=9, loc="left")
    fig.suptitle("E14 · Decentralised Phase 1: pooling θ over a graph", fontsize=11)
    save(fig, "fig14_dec_phase1")


def main():
    os.makedirs("results", exist_ok=True)
    if REPLOT and os.path.exists(CACHE_A):
        with open(CACHE_A, "rb") as fh:
            A = pickle.load(fh)
    else:
        print("[exp14 A] offline decentralised pooling", flush=True)
        A = run_part_a()
        with open(CACHE_A, "wb") as fh:
            pickle.dump(A, fh)
    tuned, best = tune(A)
    with open(TUNED, "w") as fh:
        json.dump(tuned, fh, indent=1)
    S = summarise_a(A, best)
    print("\n  consensus error after %d rounds (tuned):  " % T_A + "  ".join(GRAPHS_A))
    for k in KEYS:
        print(f"    {P1_LABEL[k]:<28}" + "".join(
            f"{S[g, k]['cons']:>10.1e}" if (g, k) in S else f"{'–':>10}" for g in GRAPHS_A)
              + f"   {tuned[k]}")
    if "--only-a" in sys.argv:
        return
    cells = [(g, l, "iid") for g in GRAPHS_B for l in LINKS]
    B = run_cells(CACHE_B, cells, lambda c: configs_for(c, tuned))
    plot(S, tuned, B, cells)
    hdr = ["strategy", "model"] + [f"cons. err {g}" for g in GRAPHS_A] + \
          [f"R {c[0]}·{c[1]}" for c in cells] + ["P1 scalars (ring·quad)"]
    rows = []
    for k in KEYS:
        r = [P1_LABEL[k], DEC_P1[k][3]] + [f"{S[g, k]['cons']:.1e}" if (g, k) in S else "–"
                                           for g in GRAPHS_A]
        r += [f"{B[c][k]['R'].mean():.0f}" for c in cells]
        r += [f"{B[('ring', 'quadratic', 'iid')][k]['comm1'].mean():,.0f}"]
        rows.append(r)
    for k in STOP_KEYS:
        for suf in ("|all", "|fixed"):
            if k + suf not in B[cells[0]]:
                continue
            rows.append([B[cells[0]][k + suf]["label"], "stop variant"] + ["–"] * len(GRAPHS_A) +
                        [f"{B[c][k + suf]['R'].mean():.0f} (T0 {np.nanmean(B[c][k + suf]['T0']):.0f})"
                         for c in cells] +
                        [f"{B[('ring', 'quadratic', 'iid')][k + suf]['comm1'].mean():,.0f}"])
    for ref in ("fed_reference", "independent"):
        rows.append([B[cells[0]][ref]["label"], "–"] + ["–"] * len(GRAPHS_A) +
                    [f"{B[c][ref]['R'].mean():.0f}" for c in cells] + ["–"])
    md_table("results/dec_phase1_benchmark.md", "E14 · Decentralised Phase 1",
             f"N = {N}; Part A offline after {T_A} rounds, {REPS} reps; Part B bandit, "
             "Phase 2 at exact server sync.  Tuned settings: " + json.dumps(tuned), hdr, rows)


if __name__ == "__main__":
    main()
