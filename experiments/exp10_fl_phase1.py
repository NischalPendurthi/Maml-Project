"""E10 -- which federated-learning method should pool theta in Phase 1?

Every FL method in src/fed/fl/ is run as the Phase-1 aggregator, under the four
heterogeneity scenarios of src/fed/scenarios.py.

Part A (offline, no bandit).  N agents collect n uniformly-pulled Phase-1 samples;
the data are cast as the federated least-squares problem of each objective
("stein": the estimator ZoomSIB uses, identical Hessians; "ls": Stein with an
estimated covariance, heterogeneous Hessians).  Each method runs on its
hyperparameter grid (experiments/configs/fl_variants.py) for up to 50 rounds:
  * optimisation error  ‖w_R − w*‖/‖w*‖ -- distance to the POOLED estimator
  * statistical error   mean_i ‖θ̂ − θ*_i‖₁ -- what the bandit actually needs
  * communication       scalars per round
Each method's best grid point (geometric-mean optimisation error at R = 10)
is saved to results/fl_tuned_phase1.json.  Personalised FL, which needs a
per-agent theta, is evaluated here only.

Part B (bandit).  Each tuned method pools theta inside Fed-ZoomSIB (10 rounds per
checkpoint, warm-started; one-shot methods use 1), Phase 2 held at exact sync.
Network regret, Phase-1 length and communication, per scenario and link.

Produces results/fig10_fl_phase1.{pdf,png}, results/fl_phase1_benchmark.md and
results/fl_tuned_phase1.json.  --replot redraws from the cache; --only-a skips B.
"""

from __future__ import annotations

import json
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import FAMILY, FL_VARIANTS, GRIDS, LABEL, ZOOMSIB   # noqa: E402
from configs import fl_phase1_config, method_kwargs              # noqa: E402
from src.base import env_info_from                               # noqa: E402
from src.fed import SCENARIOS, make_fed_envs, run_fed_sweep      # noqa: E402
from src.fed.runner import resumable_cells                        # noqa: E402
from src.fed.engine import Agent                                 # noqa: E402
from src.fed.fl import make_fl                                   # noqa: E402
from src.fed.fl.personalized import Personalized                 # noqa: E402
from src.fed.phase1.objectives import ls_problem, stein_problem  # noqa: E402
from src.plotting import heatmap, save, use_style                # noqa: E402
from src.stein import l1_error, normalize_l1, tau_default         # noqa: E402

D, K, T, SIGMA, N = 10, 20, 10_000, 0.1, 8
# Part A
N_ROUNDS_DATA = 100          # Phase-1 rounds of uniform pulls per agent
REPS = 16
RS = [1, 2, 5, 10, 20, 50]
OBJECTIVES = ["stein", "ls"]
LAMS = [0.0, 0.1, 0.25, 0.5, 1.0]
# Part B
LINKS = ["quadratic", "zigzag"]
N_TRIALS = 8
LS_VARIANTS = ["suffstat", "fedavg", "scaffold", "feddyn"]

CACHE_A = "results/exp10_fl_phase1_A.pkl"
REDO = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--redo=")), None)
CACHE_B = "results/exp10_fl_phase1_B.pkl"
TUNED = "results/fl_tuned_phase1.json"
KEYS = list(FL_VARIANTS)


# ----------------------------------------------------------------------------
# Part A
# ----------------------------------------------------------------------------
def collect(scenario, rep, link="quadratic"):
    """N agents, N_ROUNDS_DATA rounds of uniform pulls -> (agents, theta*_i)."""
    envs = make_fed_envs(N, D, K, link, SIGMA, seed=3000 + rep, run_seed=rep, scenario=scenario)
    agents = [Agent(i, None, env_info_from(e)) for i, e in enumerate(envs)]
    for _ in range(N_ROUNDS_DATA):
        for ag, env in zip(agents, envs):
            if not env.is_active():
                continue
            X = env.draw_arms()
            a = int(env.rng.integers(K))
            y = env.pull(X, a)
            ag.S_buf.append(env.score(X[a]))
            ag.y_buf.append(y)
            ag.X_buf.append(X[a])
    return agents, np.array([e.theta_star for e in envs]), envs[0]


def stat_err(w, thetas):
    th = normalize_l1(w)
    return float(np.mean([l1_error(th, t) for t in thetas]))


def part_a_cell(args):
    scenario, objective, rep = args
    agents, thetas, e0 = collect(scenario, rep)
    n_pool = sum(ag.n for ag in agents)
    if objective == "stein":
        prob = stein_problem(agents, tau_default(e0.sigma, e0.L_f, e0.M, n_pool, D, 0.01))
    else:
        prob = ls_problem(agents)
    w_star = prob.pooled(np.zeros(D))
    out = dict(pooled_stat=stat_err(w_star, thetas))
    local = prob.local_opt(np.zeros(D))
    out["local_stat"] = float(np.mean([l1_error(normalize_l1(local[i]), thetas[i])
                                       for i in range(N) if prob.active[i]]))
    out["personal"] = {}
    for lam in LAMS:
        V = Personalized(lam=lam).personal(prob, np.zeros(D))
        out["personal"][lam] = float(np.mean([l1_error(normalize_l1(V[i]), thetas[i])
                                              for i in range(N) if prob.active[i]]))
    res = {}
    for key in KEYS:
        name, fixed = FL_VARIANTS[key]
        for g, kw in enumerate(GRIDS[key]):
            m = make_fl(name, **dict(fixed, **kw))
            m._ensure(prob)
            w = np.zeros(D)
            opt, st = [], []
            per_round = m.round_cost(prob)
            for r in range(1, RS[-1] + 1):
                if not (m.one_shot and r > 1):
                    w = m.round(prob, w)
                if r in RS:
                    opt.append(float(np.linalg.norm(w - w_star) / np.linalg.norm(w_star)))
                    st.append(stat_err(w, thetas))
            res[key, g] = dict(opt=opt, stat=st, cost=per_round)
    out["methods"] = res
    return scenario, objective, rep, out


def run_part_a():
    jobs = [(s, o, r) for s in SCENARIOS for o in OBJECTIVES for r in range(REPS)]
    A = {}
    with ProcessPoolExecutor(max_workers=min(os.cpu_count() or 1, 12)) as ex:
        for done, (s, o, r, out) in enumerate(ex.map(part_a_cell, jobs, chunksize=1), 1):
            A[s, o, r] = out
            if done % 16 == 0:
                print(f"    part A {done}/{len(jobs)}", flush=True)
    return A


def tune(A):
    """Best grid point per (objective, method): geometric-mean opt. error at R=10."""
    i10 = RS.index(10)
    tuned, gm = {}, {}
    for o in OBJECTIVES:
        tuned[o] = {}
        for key in KEYS:
            scores = []
            for g in range(len(GRIDS[key])):
                errs = [A[s, o, r]["methods"][key, g]["opt"][i10]
                        for s in SCENARIOS for r in range(REPS)]
                scores.append(float(np.exp(np.mean(np.log(np.maximum(errs, 1e-16))))))
            g_best = int(np.argmin(scores))
            tuned[o][key] = GRIDS[key][g_best]
            gm[o, key] = (g_best, scores[g_best])
    return tuned, gm


def summarise_a(A, gm):
    """{(objective, scenario, key): dict(opt=[...], stat=[...], cost)} at tuned settings."""
    S = {}
    for o in OBJECTIVES:
        for s in SCENARIOS:
            for key in KEYS:
                g = gm[o, key][0]
                cells = [A[s, o, r]["methods"][key, g] for r in range(REPS)]
                S[o, s, key] = dict(
                    opt=np.exp(np.mean(np.log(np.maximum([c["opt"] for c in cells], 1e-16)), axis=0)),
                    stat=np.mean([c["stat"] for c in cells], axis=0),
                    cost=float(np.mean([c["cost"] for c in cells])))
            S[o, s, "pooled"] = float(np.mean([A[s, o, r]["pooled_stat"] for r in range(REPS)]))
            S[o, s, "local"] = float(np.mean([A[s, o, r]["local_stat"] for r in range(REPS)]))
            S[o, s, "personal"] = {lam: float(np.mean([A[s, o, r]["personal"][lam]
                                                       for r in range(REPS)])) for lam in LAMS}
    return S


# ----------------------------------------------------------------------------
# Part B
# ----------------------------------------------------------------------------
def part_b_configs(tuned):
    cfgs = {"independent": ZOOMSIB["independent"]}
    for key in KEYS:
        cfgs[key] = fl_phase1_config(key, tuned["stein"])
    for key in LS_VARIANTS:
        cfgs[key + "@ls"] = fl_phase1_config(key, tuned["ls"], objective="ls")
    return cfgs


def run_part_b(tuned):
    cfgs = part_b_configs(tuned)

    def cell(sl, names=None):
        s, link = sl
        run = {k: v for k, v in cfgs.items() if names is None or any(t in k for t in names)}
        print(f"[exp10 B] scenario={s} link={link}", flush=True)
        out, _ = run_fed_sweep(run, N_TRIALS, N, D, K, T, link, sigma=SIGMA,
                               record_every=T, progress=False, scenario=s)
        res = {}
        for name, v in out.items():
            th = []
            for trial, dg in enumerate(v["diag"]):
                envs = make_fed_envs(N, D, K, link, SIGMA, seed=1000 + trial,
                                     run_seed=50_000 + trial, scenario=s)
                est = dg["theta_hat"]
                if isinstance(est, list):                     # independent agents
                    th.append(np.mean([l1_error(e, env.theta_star)
                                       for e, env in zip(est, envs) if e is not None]))
                else:
                    th.append(np.mean([l1_error(est, env.theta_star) for env in envs]))
            res[name] = dict(
                R=v["net"][:, -1],
                T0=np.array([dg["T0_used"] or np.nan for dg in v["diag"]], float),
                comm=np.array([dg["comm_phase1"] for dg in v["diag"]], float),
                rounds=np.array([dg["comm_rounds"] for dg in v["diag"]], float),
                theta_err=np.array(th))
        return res

    cells = resumable_cells(CACHE_B + ".cells", [(s, l) for s in SCENARIOS for l in LINKS], cell,
                            redo=REDO)
    B = {(s, l, name): v for (s, l), res in cells.items() for name, v in res.items()}
    return cfgs, B


# ----------------------------------------------------------------------------
def plot(S, gm, tuned, cfgs, B):
    use_style()
    import matplotlib.pyplot as plt

    rows = [LABEL[k] for k in KEYS]
    i10 = RS.index(10)
    fig = plt.figure(figsize=(17, 8.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.35, 0.75], wspace=0.55,
                          left=0.09, right=0.99, top=0.86, bottom=0.17)

    # A1 -- optimisation error at R = 10
    ax = fig.add_subplot(gs[0])
    cols = [f"{o}·{s}" for o in OBJECTIVES for s in SCENARIOS]
    V = np.array([[S[o, s, k]["opt"][i10] for o in OBJECTIVES for s in SCENARIOS] for k in KEYS])
    txt = [[("0" if v < 1e-12 else f"{v:.0e}") for v in row] for row in V]
    heatmap(ax, np.maximum(V, 1e-16), rows, cols, log=True, cmap="Blues", vmin=-12, vmax=0,
            text=txt, fontsize=6.5)
    ax.set_title("A · distance to the pooled estimator after 10 rounds\n"
                 "‖w₁₀ − w*‖/‖w*‖  (tuned; offline, N=8, 100 rounds of data)",
                 fontsize=9, loc="left")

    # B -- bandit regret ratio to exact pooling
    ax = fig.add_subplot(gs[1])
    names = [k for k in cfgs if k != "independent"] + ["independent"]
    rlab = [cfgs[k]["label"] if k in cfgs else k for k in names]
    bcols = [f"{s}·{l[:4]}" for s in SCENARIOS for l in LINKS]
    ref = {(s, l): B[s, l, "suffstat"]["R"].mean() for s in SCENARIOS for l in LINKS}
    RV = np.array([[B[s, l, k]["R"].mean() / ref[s, l] for s in SCENARIOS for l in LINKS]
                   for k in names])
    heatmap(ax, RV, rlab, bcols, diverging_at=1.0, fmt="{:.2f}", fontsize=6.5)
    ax.set_title("B · bandit: network regret ÷ exact pooling  (blue = better)\n"
                 f"Phase 2 fixed at exact sync · N={N}, T={T:,}, {N_TRIALS} trials",
                 fontsize=9, loc="left")

    # C -- personalisation (offline)
    ax = fig.add_subplot(gs[2])
    for s, col in zip(SCENARIOS, ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"]):
        y = [S["stein", s, "personal"][lam] for lam in LAMS]
        ax.plot(LAMS, y, marker="o", ms=4, color=col, label=s)
    ax.set_xlabel("λ  (0 = local only, 1 = fully pooled)")
    ax.set_ylabel(r"mean$_i$ $\|\hat\theta_i-\theta^*_i\|_1$")
    ax.set_title("C · personalised FL (Stein, offline)", fontsize=9, loc="left")
    ax.legend(fontsize=7)
    fig.suptitle("E10 · Federated-learning methods as the Phase-1 θ aggregator", fontsize=11)
    save(fig, "fig10_fl_phase1")


def write_markdown(S, gm, tuned, cfgs, B):
    i1, i10 = RS.index(1), RS.index(10)
    L = ["# E10 · FL methods for Phase 1 (θ pooling)", "",
         f"N = {N} agents, d = {D}, K = {K}.  Part A: offline, {N_ROUNDS_DATA} rounds of "
         f"uniform pulls, {REPS} reps.  Part B: bandit, T = {T:,}, {N_TRIALS} trials.", "",
         "## A · optimisation error ‖w_R − w*‖/‖w*‖ after R rounds (tuned), Stein objective", "",
         "| method | family | tuned | scalars/round | " +
         " | ".join(f"{s} R=1 | {s} R=10" for s in SCENARIOS) + " |",
         "|---|---|---|---:|" + "---:|---:|" * len(SCENARIOS)]
    for k in KEYS:
        row = f"| {LABEL[k]} | {FAMILY[k]} | `{tuned['stein'][k]}` | {S['stein', 'iid', k]['cost']:.0f} |"
        for s in SCENARIOS:
            o = S["stein", s, k]["opt"]
            row += f" {o[i1]:.1e} | {o[i10]:.1e} |"
        L.append(row)
    L += ["", "## A · same, LS objective (heterogeneous Hessians)", "",
          "| method | tuned | " + " | ".join(f"{s} R=1 | {s} R=10" for s in SCENARIOS) + " |",
          "|---|---|" + "---:|---:|" * len(SCENARIOS)]
    for k in KEYS:
        row = f"| {LABEL[k]} | `{tuned['ls'][k]}` |"
        for s in SCENARIOS:
            o = S["ls", s, k]["opt"]
            row += f" {o[i1]:.1e} | {o[i10]:.1e} |"
        L.append(row)
    L += ["", "## A · statistical error mean_i ‖θ̂ − θ*_i‖₁", "",
          "| estimator | " + " | ".join(SCENARIOS) + " |", "|---|" + "---:|" * len(SCENARIOS)]
    for o in OBJECTIVES:
        L.append(f"| pooled ({o}) | " + " | ".join(f"{S[o, s, 'pooled']:.3f}" for s in SCENARIOS) + " |")
        L.append(f"| each agent alone ({o}) | " + " | ".join(f"{S[o, s, 'local']:.3f}" for s in SCENARIOS) + " |")
    for lam in LAMS:
        L.append(f"| personalised λ={lam} (stein) | " +
                 " | ".join(f"{S['stein', s, 'personal'][lam]:.3f}" for s in SCENARIOS) + " |")
    L += ["", "## B · bandit network regret (mean over trials)", "",
          "| config | " + " | ".join(f"{s} · {l}" for s in SCENARIOS for l in LINKS) +
          " | Phase-1 scalars (iid·quad) | θ err (iid·quad) |",
          "|---|" + "---:|" * (len(SCENARIOS) * len(LINKS)) + "---:|---:|"]
    for k, cfg in cfgs.items():
        row = f"| {cfg['label']} |"
        for s in SCENARIOS:
            for l in LINKS:
                r = B[s, l, k]["R"]
                row += f" {r.mean():.0f} |"
        b = B["iid", "quadratic", k]
        row += f" {b['comm'].mean():,.0f} | {b['theta_err'].mean():.3f} |"
        L.append(row)
    with open("results/fl_phase1_benchmark.md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("  wrote results/fl_phase1_benchmark.md")


def main():
    os.makedirs("results", exist_ok=True)
    replot = "--replot" in sys.argv
    if replot and os.path.exists(CACHE_A):
        with open(CACHE_A, "rb") as fh:
            A = pickle.load(fh)
    else:
        print("[exp10 A] offline FL runs", flush=True)
        A = run_part_a()
        with open(CACHE_A, "wb") as fh:
            pickle.dump(A, fh)
    tuned, gm = tune(A)
    with open(TUNED, "w") as fh:
        json.dump(tuned, fh, indent=1)
    print(f"  wrote {TUNED}")
    S = summarise_a(A, gm)
    if "--only-a" in sys.argv:
        for o in OBJECTIVES:
            print(f"\n  {o}: opt error at R=1 / R=10 (iid, participation, covariate, concept)")
            for k in KEYS:
                print(f"    {LABEL[k]:<32}" + "".join(
                    f"  {S[o, s, k]['opt'][0]:.0e}/{S[o, s, k]['opt'][3]:.0e}" for s in SCENARIOS)
                      + f"   {tuned[o][k]}")
        return
    if replot and os.path.exists(CACHE_B) and not REDO:
        with open(CACHE_B, "rb") as fh:
            cfgs, B = pickle.load(fh)
    else:
        cfgs, B = run_part_b(tuned)
        with open(CACHE_B, "wb") as fh:
            pickle.dump((cfgs, B), fh)
    plot(S, gm, tuned, cfgs, B)
    write_markdown(S, gm, tuned, cfgs, B)


if __name__ == "__main__":
    main()
