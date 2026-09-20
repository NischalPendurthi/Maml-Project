"""Experiment harness: build algorithms, run trials, average over seeds."""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .base import env_info_from, run_episode
from .baselines import ESTOR, GSTOR, IGPUCB, LinUCB, RandomPolicy
from .envs import SIBEnv
from .zoomsib import ZoomSIBOracleTheta, ZoomSIBUCB

ALGOS = {
    "random":  RandomPolicy,
    "linucb":  LinUCB,
    "estor":   ESTOR,
    "gstor":   GSTOR,
    "igpucb":  IGPUCB,
    "zoomsib": ZoomSIBUCB,
    "zoomsib_oracle": ZoomSIBOracleTheta,
}

# Plot order and styling, kept consistent across every figure.
STYLE = {
    "random":         dict(label="Random",              color="#9e9e9e", ls=":"),
    "linucb":         dict(label="LinUCB",              color="#8c564b", ls="-."),
    "igpucb":         dict(label="IGP-UCB",             color="#9467bd", ls="--"),
    "estor":          dict(label="ESTOR",               color="#ff7f0e", ls="--"),
    "gstor":          dict(label="GSTOR",               color="#2ca02c", ls="-"),
    "zoomsib":        dict(label="ZoomSIB-UCB",         color="#1f77b4", ls="-"),
    "zoomsib_oracle": dict(label=r"ZoomSIB (oracle $\theta_*$)",
                           color="#17becf", ls=(0, (3, 1, 1, 1))),
}


def build(algo_key, env, T, rng, **kw):
    cls = ALGOS[algo_key]
    info = env_info_from(env)
    if algo_key == "zoomsib_oracle":
        kw = dict(kw, theta_star=env.theta_star)
    return cls(env.d, env.K, T, info, rng, **kw)


def one_trial(args):
    """Run one (algorithm, seed) pair.  Top-level so it is picklable."""
    (algo_key, trial, d, K, T, link, sigma, index_scale,
     record_every, algo_kw) = args
    env = SIBEnv(d=d, K=K, link=link, sigma=sigma, seed=1000 + trial,
                 run_seed=50_000 + trial, index_scale=index_scale)
    rng = np.random.default_rng(90_000 + trial)
    algo = build(algo_key, env, T, rng, **(algo_kw or {}))
    cum, grid = run_episode(env, algo, T, record_every=record_every)
    extra = algo.diagnostics() if hasattr(algo, "diagnostics") else {}
    return algo_key, trial, cum, grid, extra


def run_sweep(algo_keys, n_trials, d, K, T, link, sigma=0.1, index_scale=None,
              record_every=1, algo_kw=None, workers=None, progress=True):
    """Run every (algorithm, trial) pair, optionally in parallel.

    Returns
    -------
    curves : {algo_key: (n_trials, n_points) cumulative regret}
    grid   : (n_points,) the round indices the curves are sampled at
    diag   : {algo_key: [per-trial diagnostics]}
    """
    algo_kw = algo_kw or {}
    jobs = [
        (k, i, d, K, T, link, sigma, index_scale, record_every, algo_kw.get(k))
        for k in algo_keys for i in range(n_trials)
    ]
    curves = {k: [None] * n_trials for k in algo_keys}
    diag = {k: [None] * n_trials for k in algo_keys}
    grid = None

    workers = workers if workers is not None else min(os.cpu_count() or 1, 12)
    done = 0
    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for k, i, cum, g, extra in ex.map(one_trial, jobs, chunksize=1):
                curves[k][i] = cum
                diag[k][i] = extra
                grid = g
                done += 1
                if progress and done % max(1, len(jobs) // 20) == 0:
                    print(f"    {done}/{len(jobs)} trials", flush=True)
    else:
        for job in jobs:
            k, i, cum, g, extra = one_trial(job)
            curves[k][i] = cum
            diag[k][i] = extra
            grid = g
            done += 1
            if progress and done % max(1, len(jobs) // 20) == 0:
                print(f"    {done}/{len(jobs)} trials", flush=True)

    return {k: np.vstack(v) for k, v in curves.items()}, grid, diag


def mean_ci(curves, level=1.96):
    """Mean and half-width of a normal CI across trials."""
    m = curves.mean(axis=0)
    se = curves.std(axis=0, ddof=1) / np.sqrt(curves.shape[0]) if curves.shape[0] > 1 \
        else np.zeros_like(m)
    return m, level * se


def loglog_slope(x, y, lo_frac=0.3):
    """Fit log y = a log x + b over the last (1 - lo_frac) of the range."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = (x > 0) & (y > 0)
    x, y = x[m], y[m]
    if x.size < 5:
        return float("nan"), float("nan")
    start = int(lo_frac * x.size)
    slope, intercept = np.polyfit(np.log(x[start:]), np.log(y[start:]), 1)
    return float(slope), float(intercept)
