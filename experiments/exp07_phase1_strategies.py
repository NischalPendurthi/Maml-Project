"""E7 -- Phase-1 federation strategies: how should the agents pool theta?

Configs: experiments/configs/phase1_variants.py (Phase 2 held fixed).

Part A is pure estimation, no bandit: N agents each draw n uniformly-pulled
samples and every strategy in src/fed/phase1/ aggregates them.  It measures
||theta_hat - theta_*||_1 against per-agent n, alongside the single-agent and
centralised references, and the bits each strategy uploads.

Part B runs the full bandit with each strategy and reports per-agent Phase-1
length and final network regret.

What to look for:
  * `exact` should coincide with the centralised curve (it IS the centralised
    estimator) and sit sqrt(N) below a lone agent;
  * `normavg` / `median` lose efficiency at small n, where each agent's local
    normalisation and local truncation are worst;
  * `quantized` trades bits for error, and stays unbiased.

Produces: results/fig08_phase1_strategies.{pdf,png}.  --replot redraws from cache.
"""

from __future__ import annotations

import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import PHASE1_VARIANTS, style                       # noqa: E402
from src.base import env_info_from                               # noqa: E402
from src.envs import SIBEnv                                      # noqa: E402
from src.fed import make_fed_envs, run_fed_sweep                 # noqa: E402
from src.fed.engine import Agent                                 # noqa: E402
from src.fed.phase1 import make_phase1                           # noqa: E402
from src.plotting import save, use_style                         # noqa: E402
from src.stein import l1_error, stein_estimate, tau_default       # noqa: E402

D, K, T = 10, 20, 10_000
SIGMA = 0.1
N = 8
NS_LOC = [5, 10, 20, 40, 80, 160, 320]
REPS = 40
LINKS = ["quadratic", "zigzag"]
N_TRIALS = 8
CACHE = "results/exp07_phase1_strategies.pkl"


def estimation_study(link):
    """theta error of every Phase-1 strategy vs per-agent sample size n."""
    errs = {k: np.zeros((len(NS_LOC), REPS)) for k in PHASE1_VARIANTS}
    errs["alone"] = np.zeros((len(NS_LOC), REPS))
    errs["central"] = np.zeros((len(NS_LOC), REPS))
    bits = {}
    for r in range(REPS):
        envs = make_fed_envs(N, D, K, link, SIGMA, seed=2000 + r, run_seed=r)
        info = env_info_from(envs[0])
        tau_fn = lambda n: tau_default(info["sigma"], info["L_f"], info["M"], n, D, 0.01)  # noqa: E731
        agents = [Agent(i, None) for i in range(N)]
        n_have = 0
        for a_n, n in enumerate(NS_LOC):
            for i, env in enumerate(envs):              # top up to n uniform pulls each
                for _ in range(n - n_have):
                    X = env.draw_arms()
                    a = int(env.rng.integers(K))
                    agents[i].S_buf.append(env.score(X[a]))
                    agents[i].y_buf.append(env.pull(X, a))
            n_have = n
            th = envs[0].theta_star
            for key, cfg in PHASE1_VARIANTS.items():
                strat = make_phase1(cfg["phase1"], np.random.default_rng([r, a_n]),
                                    **cfg.get("phase1_kw", {}))
                est, _, b = strat.aggregate(agents, tau_fn)
                errs[key][a_n, r] = l1_error(est, th)
                bits[key] = b
            S0, y0 = np.asarray(agents[0].S_buf), np.asarray(agents[0].y_buf)
            errs["alone"][a_n, r] = l1_error(stein_estimate(S0, y0, tau=tau_fn(n)), th)
            S = np.concatenate([ag.S_buf for ag in agents])
            y = np.concatenate([ag.y_buf for ag in agents])
            errs["central"][a_n, r] = l1_error(stein_estimate(S, y, tau=tau_fn(N * n)), th)
    return errs, bits


def simulate():
    res = {}
    for link in LINKS:
        print(f"[exp07] estimation study, link={link}", flush=True)
        res["est", link] = estimation_study(link)
        print(f"[exp07] bandit sweep, link={link}", flush=True)
        out, grid = run_fed_sweep(PHASE1_VARIANTS, N_TRIALS, N, D, K, T, link,
                                  sigma=SIGMA, record_every=100, progress=False)
        res["bandit", link] = {
            k: dict(R=v["net"][:, -1],
                    T0=np.array([dg["T0_used"] for dg in v["diag"]], float),
                    err=np.array([l1_error(dg["theta_hat"], SIBEnv(D, K, link, SIGMA,
                                  seed=1000 + i, index_scale=1.0).theta_star)
                                  for i, dg in enumerate(v["diag"])]))
            for k, v in out.items()}
    os.makedirs("results", exist_ok=True)
    with open(CACHE, "wb") as fh:
        pickle.dump(res, fh)
    return res


def plot(res):
    use_style()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(16.0, 3.6),
                             gridspec_kw=dict(width_ratios=[1.3, 1.0, 0.85, 0.85]))
    errs, bits = res["est", "quadratic"]
    ax = axes[0]
    ax.plot(NS_LOC, errs["alone"].mean(1), color="#8a8984", ls="--", marker="o", ms=3,
            label="one agent alone")
    ax.plot(NS_LOC, errs["central"].mean(1), color="#0b0b0b", lw=3.5, alpha=0.25,
            label=f"centralised ({N}n pooled samples)")
    for key, cfg in PHASE1_VARIANTS.items():
        ax.plot(NS_LOC, errs[key].mean(1), marker="o", ms=3, **style(cfg))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("per-agent Phase-1 samples $n$")
    ax.set_ylabel(r"$\|\hat\theta-\theta_*\|_1$")
    ax.set_title(f"A · estimation error, N={N}, quadratic", fontsize=9)
    ax.legend(fontsize=6.5, loc="lower left")

    keys = list(PHASE1_VARIANTS)
    y = np.arange(len(keys))
    labels = [PHASE1_VARIANTS[k]["label"] for k in keys]
    colors = [PHASE1_VARIANTS[k]["style"]["color"] for k in keys]
    i80 = NS_LOC.index(80)
    ax = axes[1]
    ax.barh(y, [bits[k] / N for k in keys], color=colors, height=0.6)
    ax.set_yticks(y, labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("upload bits per agent per checkpoint")
    for yi, k in zip(y, keys):
        ax.text(bits[k] / N, yi, f"  err {errs[k][i80].mean():.3f}", va="center", fontsize=7)
    ax.set_title("B · cost of one upload (error at n=80)", fontsize=9)
    ax.set_xlim(0, max(bits.values()) / N * 1.5)

    for ax, link in zip(axes[2:], LINKS):
        b = res["bandit", link]
        m = np.array([b[k]["R"].mean() for k in keys])
        se = np.array([b[k]["R"].std(ddof=1) / np.sqrt(len(b[k]["R"])) for k in keys])
        # a strategy whose stopping rule never fires dwarfs the rest: clip and label it
        typical = np.median(m)
        xmax = 1.6 * m[m < 5 * typical].max()
        ax.barh(y, np.minimum(m, xmax), color=colors, height=0.6)
        ax.errorbar(np.minimum(m, xmax), y, xerr=np.where(m < xmax, 1.96 * se, 0), fmt="none",
                    ecolor="#0b0b0b", lw=0.8, capsize=2)
        for yi, k in zip(y, keys):
            txt = f"  T0={b[k]['T0'].mean():.0f}"
            if m[yi] > xmax:
                txt = f"{m[yi]:,.0f} →  (T0={b[k]['T0'].mean():.0f}) "
                ax.text(xmax, yi, txt, va="center", ha="right", fontsize=7, color="white",
                        weight="bold")
            else:
                ax.text(m[yi] + 1.96 * se[yi], yi, txt, va="center", fontsize=7)
        ax.set_yticks(y, [])
        ax.invert_yaxis()
        ax.set_xlim(0, xmax)
        ax.set_xlabel("network regret $R_T$")
        ax.set_title(f"{'C' if link == LINKS[0] else 'D'} · bandit, {link} "
                     f"(N={N}, T={T:,})", fontsize=9)
    fig.suptitle("E7 · Phase-1 pooling strategies (Phase 2 fixed: server sync every round)",
                 y=1.04, fontsize=10)
    fig.subplots_adjust(wspace=0.12)
    save(fig, "fig08_phase1_strategies")

    print(f"\n  theta error at per-agent n (N={N}, quadratic), mean over {REPS} reps:")
    print("    " + f"{'strategy':<38}" + "".join(f"{'n=' + str(n):>9}" for n in NS_LOC))
    for key in ["alone", "central", *PHASE1_VARIANTS]:
        lab = PHASE1_VARIANTS[key]["label"] if key in PHASE1_VARIANTS else key
        print(f"    {lab:<38}" + "".join(f"{e:>9.4f}" for e in errs[key].mean(1)))
    for link in LINKS:
        print(f"\n  bandit, {link}: network regret / per-agent T0 / final theta error")
        for key in keys:
            b = res["bandit", link][key]
            print(f"    {PHASE1_VARIANTS[key]['label']:<38} R={b['R'].mean():8.0f}  "
                  f"T0={b['T0'].mean():6.1f}  err={b['err'].mean():.4f}")


def main():
    if "--replot" in sys.argv and os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            res = pickle.load(fh)
    else:
        res = simulate()
    plot(res)


if __name__ == "__main__":
    main()
