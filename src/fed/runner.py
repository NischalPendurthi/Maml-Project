"""Multi-agent harness: N environments sharing theta_* and f, episode loop, sweeps.

An algorithm CONFIG is a plain dict (see experiments/configs/):

    dict(engine="fed", phase1="exact", phase2="periodic", phase2_kw=dict(every=1), ...)
    dict(engine="independent")

`engine` picks the class, every other key is passed to its constructor.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor

from .. import runner as _runner  # noqa: F401  (pins BLAS to one thread per worker)

import numpy as np

from ..base import env_info_from
from ..envs import SIBEnv
from .engine import FedTwoPhase
from .independent import IndependentAgents

ENGINES = {"fed": FedTwoPhase, "independent": IndependentAgents}


def make_fed_envs(N, d, K, link, sigma=0.1, seed=0, run_seed=0, index_scale=1.0):
    """N agents on one problem instance.

    Same `seed` -> same theta_* (and f); each agent gets its own context and
    noise stream.  An agent's stream does not depend on what it pulls, so every
    config sees exactly the same contexts -- comparisons are paired.
    """
    return [SIBEnv(d=d, K=K, link=link, sigma=sigma, seed=seed,
                   run_seed=[run_seed, i], index_scale=index_scale)
            for i in range(N)]


def build_fed(config, envs, T, rng):
    kw = dict(config)
    cls = ENGINES[kw.pop("engine", "fed")]
    kw.pop("label", None)
    kw.pop("style", None)
    env = envs[0]
    return cls(len(envs), env.d, env.K, T, env_info_from(env), rng, **kw)


def run_fed_episode(envs, algo, T, record_every=1, callback=None):
    """All N agents act once per round, then the network gets one chance to talk.

    Returns (network cumulative regret (P,), per-agent cumulative regret (N, P),
    grid).  `callback(t, algo, inst)` runs after every round -- the live
    visualisation hooks in here.
    """
    N = len(envs)
    inst = np.empty((T, N), dtype=float)
    for t in range(T):
        for i, env in enumerate(envs):
            X = env.draw_arms()
            a = algo.select(i, X)
            y = env.pull(X, a)
            inst[t, i] = env.instant_regret(X, a)
            algo.update(i, X, a, y)
        algo.end_round()
        if callback is not None:
            callback(t + 1, algo, inst[: t + 1])
    per_agent = np.cumsum(inst, axis=0).T
    idx = np.arange(record_every - 1, T, record_every)
    return per_agent.sum(axis=0)[idx], per_agent[:, idx], idx + 1


def one_fed_trial(args):
    (name, config, trial, N, d, K, T, link, sigma, index_scale, record_every) = args
    envs = make_fed_envs(N, d, K, link, sigma, seed=1000 + trial,
                         run_seed=50_000 + trial, index_scale=index_scale)
    rng = np.random.default_rng([90_000, trial, N])
    algo = build_fed(config, envs, T, rng)
    net, per, grid = run_fed_episode(envs, algo, T, record_every)
    return name, trial, net, per, grid, algo.diagnostics()


def run_fed_sweep(configs, n_trials, N, d, K, T, link, sigma=0.1, index_scale=1.0,
                  record_every=1, workers=None, progress=True):
    """Run every (config, trial) pair in parallel.

    `configs` maps a name -> config dict.  Returns
    ({name: dict(net=(n_trials,P), per=(n_trials,N,P), diag=[...])}, grid).
    """
    out = {name: dict(net=[None] * n_trials, per=[None] * n_trials, diag=[None] * n_trials)
           for name in configs}
    jobs = [(name, cfg, i, N, d, K, T, link, sigma, index_scale, record_every)
            for name, cfg in configs.items() for i in range(n_trials)]
    workers = workers if workers is not None else min(os.cpu_count() or 1, 12)
    grid = None

    def consume(results):
        nonlocal grid
        for done, (name, trial, net, per, g, diag) in enumerate(results, 1):
            out[name]["net"][trial] = net
            out[name]["per"][trial] = per
            out[name]["diag"][trial] = diag
            grid = g
            if progress and done % max(1, len(jobs) // 10) == 0:
                print(f"    {done}/{len(jobs)} trials", flush=True)

    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            consume(ex.map(one_fed_trial, jobs, chunksize=1))
    else:
        consume(map(one_fed_trial, jobs))

    for name in out:
        out[name]["net"] = np.vstack(out[name]["net"])
        out[name]["per"] = np.stack(out[name]["per"])
    return out, grid
