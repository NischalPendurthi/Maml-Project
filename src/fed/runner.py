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
from .scenarios import make_scenario_envs

ENGINES = {"fed": FedTwoPhase, "independent": IndependentAgents}


def make_fed_envs(N, d, K, link, sigma=0.1, seed=0, run_seed=0, index_scale=1.0,
                  scenario="iid", strength=None):
    """N agents on one problem instance.

    Same `seed` -> same theta_* (and f); each agent gets its own context and
    noise stream.  An agent's stream does not depend on what it pulls, so every
    config sees exactly the same contexts -- comparisons are paired.
    `scenario` (src/fed/scenarios.py) makes the agents heterogeneous.
    """
    if scenario == "iid" and strength is None:
        return [SIBEnv(d=d, K=K, link=link, sigma=sigma, seed=seed,
                       run_seed=[run_seed, i], index_scale=index_scale)
                for i in range(N)]
    return make_scenario_envs(scenario, N, d, K, link, sigma, seed, run_seed,
                              index_scale, strength)


def build_fed(config, envs, T, rng):
    kw = dict(config)
    engine = kw.pop("engine", "fed")
    if engine == "dec":                       # serverless engine, src/dec/
        from ..dec.engine import DecTwoPhase
        cls = DecTwoPhase
    else:
        cls = ENGINES[engine]
    kw.pop("label", None)
    kw.pop("style", None)
    env = envs[0]
    infos = [env_info_from(e) for e in envs]
    return cls(len(envs), env.d, env.K, T, infos[0], rng, agent_infos=infos, **kw)


def run_fed_episode(envs, algo, T, record_every=1, callback=None):
    """Every ACTIVE agent acts once per round, then the network gets one chance to talk.

    Returns (network cumulative regret (P,), per-agent cumulative regret (N, P),
    grid).  `callback(t, algo, inst)` runs after every round -- the live
    visualisation hooks in here.
    """
    N = len(envs)
    inst = np.empty((T, N), dtype=float)
    for t in range(T):
        for i, env in enumerate(envs):
            if not env.is_active():
                inst[t, i] = 0.0
                continue
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
    (name, config, trial, N, d, K, T, link, sigma, index_scale, record_every,
     scenario, strength) = args
    envs = make_fed_envs(N, d, K, link, sigma, seed=1000 + trial,
                         run_seed=50_000 + trial, index_scale=index_scale,
                         scenario=scenario, strength=strength)
    rng = np.random.default_rng([90_000, trial, N])
    algo = build_fed(config, envs, T, rng)
    net, per, grid = run_fed_episode(envs, algo, T, record_every)
    return name, trial, net, per, grid, algo.diagnostics()


def run_fed_sweep(configs, n_trials, N, d, K, T, link, sigma=0.1, index_scale=1.0,
                  record_every=1, workers=None, progress=True, scenario="iid",
                  strength=None):
    """Run every (config, trial) pair in parallel.

    `configs` maps a name -> config dict.  Returns
    ({name: dict(net=(n_trials,P), per=(n_trials,N,P), diag=[...])}, grid).
    """
    out = {name: dict(net=[None] * n_trials, per=[None] * n_trials, diag=[None] * n_trials)
           for name in configs}
    jobs = [(name, cfg, i, N, d, K, T, link, sigma, index_scale, record_every,
             scenario, strength)
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


def resumable_cells(path, cells, run_cell, redo=None):
    """Run `run_cell(cell, names) -> {name: result}` per cell, checkpointing to `path`.

    Long benchmarks are a sequence of (scenario, link) cells; if the process is
    interrupted, re-running picks up after the last finished cell.  `redo` (a
    list of config names) recomputes just those configs in every cached cell --
    for when one method's implementation changes.
    """
    import pickle

    done = {}
    if os.path.exists(path):
        with open(path, "rb") as fh:
            done = pickle.load(fh)
    for cell in cells:
        if cell in done and not redo:
            print(f"    cell {cell} cached", flush=True)
            continue
        if cell in done:
            done[cell].update(run_cell(cell, redo))
        else:
            done[cell] = run_cell(cell, None)
        with open(path + ".tmp", "wb") as fh:
            pickle.dump(done, fh)
        os.replace(path + ".tmp", path)
    return done
