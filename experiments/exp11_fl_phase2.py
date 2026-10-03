"""E11 -- which federated-learning method should share the Phase-2 bin table?

Every FL method in src/fed/fl/ is run as the Phase-2 aggregator (phase2/fl.py),
under the four heterogeneity scenarios, with Phase 1 held at exact pooling.

Part A (offline, real tables).  Fed-ZoomSIB is run with exact sharing and the
agents' bin tables (n_ij, S_ij) are snapshotted at several times.  At each
snapshot the FL methods start from the table as it stood C = 10 rounds earlier
(what the previous sync left behind) and run R rounds.  Score:
    count-weighted RMSE(w_R, w*) / count-weighted RMSE(w_0, w*)
i.e. the fraction of the staleness error that is LEFT after R rounds (0 = exact).
Bin tables are where agents differ most -- each visits different bins at
different rates -- so this is where model averaging's objective inconsistency
should show.  Best grid points (geometric mean at R = 5) are saved to
results/fl_tuned_phase2.json.

Part B (bandit).  Each tuned method syncs every C = 10 rounds with R = 5 rounds
per sync (one-shot methods: 1).  References: no sharing, event-triggered exact
sync, personalised sharing, and N independent agents.

Produces results/fig11_fl_phase2.{pdf,png}, results/fl_phase2_benchmark.md and
results/fl_tuned_phase2.json.  --replot redraws from the cache; --only-a skips B.
"""

from __future__ import annotations

import json
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (FAMILY, FAMILY_COLOR, FL_VARIANTS, GRIDS, LABEL,     # noqa: E402
                     ZOOMSIB, fl_phase2_config)
from src.fed import SCENARIOS, build_fed, make_fed_envs, run_fed_episode  # noqa: E402
from src.fed import run_fed_sweep                                         # noqa: E402
from src.fed.runner import resumable_cells                                # noqa: E402
from src.fed.fl import FedQuadratic, make_fl                              # noqa: E402
from src.plotting import heatmap, save, use_style                         # noqa: E402

D, K, T, SIGMA, N = 10, 20, 10_000, 0.1, 8
C_SYNC = 10
R_SYNC = 5
# Part A
SNAP_T = [400, 1500, 4000]
REPS = 6
RS = [1, 2, 5, 10, 20, 50]
# Part B
LINKS = ["quadratic", "zigzag"]
N_TRIALS = 8

CACHE_A = "results/exp11_fl_phase2_A.pkl"
REDO = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--redo=")), None)
CACHE_B = "results/exp11_fl_phase2_B.pkl"
TUNED = "results/fl_tuned_phase2.json"
KEYS = list(FL_VARIANTS)
EXACT = dict(engine="fed", phase1="exact", phase2="periodic", phase2_kw=dict(every=1))


# ----------------------------------------------------------------------------
# Part A
# ----------------------------------------------------------------------------
def snapshots(scenario, rep, link="quadratic"):
    """Bin tables (own_n, own_S) at t − C_SYNC and t for each t in SNAP_T."""
    envs = make_fed_envs(N, D, K, link, SIGMA, seed=4000 + rep, run_seed=rep, scenario=scenario)
    algo = build_fed(EXACT, envs, SNAP_T[-1], np.random.default_rng(rep))
    want = {t - C_SYNC for t in SNAP_T} | set(SNAP_T)
    snaps = {}

    def grab(t, a, inst):
        if t in want and a.phase == 2:
            snaps[t] = (a.p2.own_n.astype(float).copy(), a.p2.own_S.copy())

    run_fed_episode(envs, algo, SNAP_T[-1], callback=grab)
    return snaps


def wrmse(w, w_star, n):
    m = n > 0
    return float(np.sqrt(np.sum(n[m] * (w[m] - w_star[m]) ** 2) / max(n[m].sum(), 1)))


def part_a_cell(args):
    scenario, rep = args
    snaps = snapshots(scenario, rep)
    res = {}
    for t in SNAP_T:
        if t not in snaps or t - C_SYNC not in snaps:
            continue
        n0, S0 = snaps[t - C_SYNC]
        n1, S1 = snaps[t]
        old = FedQuadratic(n0, S0, n0.sum(1), diag=True)
        prob = FedQuadratic(n1, S1, n1.sum(1), diag=True, touched=(n1 - n0) > 0,
                            new_samples=(n1 - n0).sum(1), sample_cost=2)
        w0 = old.pooled(np.zeros(prob.D))
        w_star = prob.pooled(w0)
        ntot = n1.sum(0)
        base = wrmse(w0, w_star, ntot)
        for key in KEYS:
            name, fixed = FL_VARIANTS[key]
            for g, kw in enumerate(GRIDS[key]):
                m = make_fl(name, **dict(fixed, **kw))
                m._ensure(prob)
                w = w0.copy()
                errs = []
                cost = m.round_cost(prob)
                for r in range(1, RS[-1] + 1):
                    if not (m.one_shot and r > 1):
                        w = m.round(prob, w)
                    if r in RS:
                        errs.append(wrmse(w, w_star, ntot) / max(base, 1e-12))
                res[t, key, g] = dict(rel=errs, cost=cost, base=base)
    return scenario, rep, res


def run_part_a():
    jobs = [(s, r) for s in SCENARIOS for r in range(REPS)]
    A = {}
    with ProcessPoolExecutor(max_workers=min(os.cpu_count() or 1, 12)) as ex:
        for done, (s, r, res) in enumerate(ex.map(part_a_cell, jobs, chunksize=1), 1):
            A[s, r] = res
            print(f"    part A {done}/{len(jobs)}", flush=True)
    return A


def _cells(A, s, key, g):
    """All (rep, snapshot) results of one method / grid point in scenario s."""
    return [A[s, r][t, key, g] for r in range(REPS) for t in SNAP_T if (t, key, g) in A[s, r]]


def tune(A):
    iR = RS.index(R_SYNC)
    tuned, best = {}, {}
    for key in KEYS:
        scores = []
        for g in range(len(GRIDS[key])):
            errs = [c["rel"][iR] for s in SCENARIOS for c in _cells(A, s, key, g)]
            scores.append(float(np.exp(np.mean(np.log(np.maximum(errs, 1e-16))))))
        g_best = int(np.argmin(scores))
        tuned[key] = GRIDS[key][g_best]
        best[key] = g_best
    return tuned, best


def summarise_a(A, best):
    S = {}
    for s in SCENARIOS:
        for key in KEYS:
            cells = _cells(A, s, key, best[key])
            S[s, key] = dict(
                rel=np.exp(np.mean(np.log(np.maximum([c["rel"] for c in cells], 1e-16)), axis=0)),
                cost=float(np.mean([c["cost"] for c in cells])))
    return S


# ----------------------------------------------------------------------------
# Part B
# ----------------------------------------------------------------------------
def part_b_configs(tuned):
    cfgs = {"independent": ZOOMSIB["independent"]}
    for key in KEYS:
        cfgs[key] = fl_phase2_config(key, tuned, rounds=R_SYNC, every=C_SYNC)
    cfgs["none"] = dict(engine="fed", phase1="exact", phase2="none",
                        label="No Phase-2 sharing")
    cfgs["event"] = dict(fl_phase2_config("suffstat", tuned, gamma=0.5),
                         label="Suff. stats, event-triggered (γ=0.5)")
    for lam in (0.25, 0.5):
        cfgs[f"pers{lam}"] = dict(engine="fed", phase1="exact", phase2="personalized",
                                  phase2_kw=dict(lam=lam, every=C_SYNC),
                                  label=f"Personalised FL (λ={lam})")
    return cfgs


def run_part_b(tuned):
    cfgs = part_b_configs(tuned)

    def cell(sl, names=None):
        s, link = sl
        run = {k: v for k, v in cfgs.items() if names is None or any(t in k for t in names)}
        print(f"[exp11 B] scenario={s} link={link}", flush=True)
        out, _ = run_fed_sweep(run, N_TRIALS, N, D, K, T, link, sigma=SIGMA,
                               record_every=T, progress=False, scenario=s)
        return {name: dict(R=v["net"][:, -1],
                           comm=np.array([dg["comm_scalars"] for dg in v["diag"]], float),
                           rounds=np.array([dg["comm_rounds"] for dg in v["diag"]], float))
                for name, v in out.items()}

    cells = resumable_cells(CACHE_B + ".cells", [(s, l) for s in SCENARIOS for l in LINKS], cell,
                            redo=REDO)
    B = {(s, l, name): v for (s, l), res in cells.items() for name, v in res.items()}
    return cfgs, B


# ----------------------------------------------------------------------------
def plot(S, tuned, cfgs, B):
    use_style()
    import matplotlib.pyplot as plt

    iR = RS.index(R_SYNC)
    fig = plt.figure(figsize=(17, 8.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.75, 1.25, 1.0], wspace=0.5,
                          left=0.09, right=0.99, top=0.86, bottom=0.17)

    ax = fig.add_subplot(gs[0])
    V = np.array([[S[s, k]["rel"][iR] for s in SCENARIOS] for k in KEYS])
    txt = [[("0" if v < 1e-9 else f"{v:.2f}" if v >= 0.01 else f"{v:.0e}") for v in row]
           for row in V]
    heatmap(ax, np.maximum(V, 1e-12), [LABEL[k] for k in KEYS], SCENARIOS, log=True,
            cmap="Blues", vmin=-6, vmax=0.3, text=txt, fontsize=6.5)
    ax.set_title(f"A · staleness error left after {R_SYNC} rounds\n"
                 "(real bin tables; 1 = no progress, 0 = exact)", fontsize=9, loc="left")

    ax = fig.add_subplot(gs[1])
    names = [k for k in cfgs if k != "independent"] + ["independent"]
    cols = [f"{s}·{l[:4]}" for s in SCENARIOS for l in LINKS]
    ref = {(s, l): B[s, l, "suffstat"]["R"].mean() for s in SCENARIOS for l in LINKS}
    RV = np.array([[B[s, l, k]["R"].mean() / ref[s, l] for s in SCENARIOS for l in LINKS]
                   for k in names])
    heatmap(ax, RV, [cfgs[k]["label"] for k in names], cols, diverging_at=1.0,
            fmt="{:.2f}", fontsize=6.5)
    ax.set_title("B · bandit: network regret ÷ exact sync every 10  (blue = better)\n"
                 f"Phase 1 fixed at exact pooling · N={N}, T={T:,}, {N_TRIALS} trials",
                 fontsize=9, loc="left")

    ax = fig.add_subplot(gs[2])
    s, l = "iid", "quadratic"
    off = {"independent", "none"}                  # far off-scale; quoted in the title
    seen = set()
    for k in names:
        if k in off:
            continue
        b = B[s, l, k]
        fam = FAMILY.get(k)
        col = FAMILY_COLOR[fam] if fam else "#8a8984"
        lab = (fam if fam else "suff.-stat. schedules / personalised") \
            if (fam or "ref") not in seen else None
        seen.add(fam or "ref")
        ax.scatter([b["comm"].mean()], [b["R"].mean()], s=36, color=col, edgecolors="white",
                   linewidths=0.8, zorder=3, label=lab)
    for k, dx, dy in [("suffstat", 6, 6), ("event", 6, -10), ("oneshot", 6, 8),
                      ("scaffold", -40, 10), ("fedavg", -10, -14), ("pers0.25", 6, 6)]:
        b = B[s, l, k]
        ax.annotate(cfgs[k]["label"].split(" (")[0].replace("Sufficient statistics", "Suff. stats"),
                    (b["comm"].mean(), b["R"].mean()), fontsize=6.5, color="#52514e",
                    textcoords="offset points", xytext=(dx, dy))
    ax.set_xscale("log")
    ax.set_xlabel("total scalars communicated")
    ax.set_ylabel("network regret")
    ax.set_title("C · regret vs communication (iid, quadratic)\n"
                 f"off-chart: no Phase-2 sharing {B[s, l, 'none']['R'].mean():,.0f} · "
                 f"independent {B[s, l, 'independent']['R'].mean():,.0f}",
                 fontsize=9, loc="left")
    ax.legend(fontsize=6.5, loc="upper left")
    fig.suptitle("E11 · Federated-learning methods as the Phase-2 bin-table aggregator",
                 fontsize=11)
    save(fig, "fig11_fl_phase2")


def write_markdown(S, tuned, cfgs, B):
    iR = RS.index(R_SYNC)
    L = ["# E11 · FL methods for Phase 2 (bin-table sharing)", "",
         f"N = {N}, d = {D}, K = {K}.  Part A: real bin tables at t ∈ {SNAP_T}, {REPS} reps "
         f"per scenario, warm start from the table {C_SYNC} rounds earlier.  Part B: bandit, "
         f"T = {T:,}, sync every {C_SYNC} rounds with {R_SYNC} FL rounds, {N_TRIALS} trials.", "",
         f"## A · staleness error left after R rounds (1 = none removed, 0 = exact)", "",
         "| method | family | tuned | scalars/round | " +
         " | ".join(f"{s} R=1 | {s} R={R_SYNC} | {s} R=50" for s in SCENARIOS) + " |",
         "|---|---|---|---:|" + "---:|---:|---:|" * len(SCENARIOS)]
    for k in KEYS:
        row = f"| {LABEL[k]} | {FAMILY[k]} | `{tuned[k]}` | {S['iid', k]['cost']:.0f} |"
        for s in SCENARIOS:
            r = S[s, k]["rel"]
            row += f" {r[0]:.2g} | {r[iR]:.2g} | {r[-1]:.2g} |"
        L.append(row)
    L += ["", "## B · bandit network regret (mean over trials) and communication", "",
          "| config | " + " | ".join(f"{s} · {l}" for s in SCENARIOS for l in LINKS) +
          " | scalars (iid·quad) | rounds (iid·quad) |",
          "|---|" + "---:|" * (len(SCENARIOS) * len(LINKS)) + "---:|---:|"]
    for k, cfg in cfgs.items():
        row = f"| {cfg['label']} |"
        for s in SCENARIOS:
            for l in LINKS:
                row += f" {B[s, l, k]['R'].mean():.0f} |"
        b = B["iid", "quadratic", k]
        row += f" {b['comm'].mean():,.0f} | {b['rounds'].mean():,.0f} |"
        L.append(row)
    with open("results/fl_phase2_benchmark.md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("  wrote results/fl_phase2_benchmark.md")


def main():
    os.makedirs("results", exist_ok=True)
    replot = "--replot" in sys.argv
    if replot and os.path.exists(CACHE_A):
        with open(CACHE_A, "rb") as fh:
            A = pickle.load(fh)
    else:
        print("[exp11 A] offline FL runs on real bin tables", flush=True)
        A = run_part_a()
        with open(CACHE_A, "wb") as fh:
            pickle.dump(A, fh)
    tuned, best = tune(A)
    with open(TUNED, "w") as fh:
        json.dump(tuned, fh, indent=1)
    print(f"  wrote {TUNED}")
    S = summarise_a(A, best)
    if "--only-a" in sys.argv:
        iR = RS.index(R_SYNC)
        print(f"\n  staleness error left at R=1 / R={R_SYNC} / R=50 "
              "(iid, participation, covariate, concept)")
        for k in KEYS:
            print(f"    {LABEL[k]:<32}" + "".join(
                f"  {S[s, k]['rel'][0]:.1e}/{S[s, k]['rel'][iR]:.1e}/{S[s, k]['rel'][-1]:.1e}"
                for s in SCENARIOS) + f"   {tuned[k]}")
        return
    if replot and os.path.exists(CACHE_B) and not REDO:
        with open(CACHE_B, "rb") as fh:
            cfgs, B = pickle.load(fh)
    else:
        cfgs, B = run_part_b(tuned)
        with open(CACHE_B, "wb") as fh:
            pickle.dump((cfgs, B), fh)
    plot(S, tuned, cfgs, B)
    write_markdown(S, tuned, cfgs, B)


if __name__ == "__main__":
    main()
