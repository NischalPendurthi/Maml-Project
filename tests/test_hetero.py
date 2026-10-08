"""Tests for heterogeneous agents (covariate shift with explicit positions) and the
sign-invariant Phase-1 strategies.

    python tests/test_hetero.py      (~15 s)
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base import env_info_from                                       # noqa: E402
from src.fed.engine import Agent                                         # noqa: E402
from src.fed.phase1 import make_phase1                                   # noqa: E402
from src.fed.runner import build_fed, make_fed_envs, run_fed_episode     # noqa: E402
from src.stein import tau_default                                        # noqa: E402


def sin_angle(a, b):
    a, b = np.ravel(a), np.ravel(b)
    c = abs(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.sqrt(max(0.0, 1 - c * c)))


def _agents(positions, n, seed=0):
    """Phase-1 data (uniform pulls) for agents at the given index means."""
    envs = make_fed_envs(len(positions), 10, 20, "quadratic", seed=1000 + seed,
                         run_seed=50_000 + seed, scenario="covariate", strength=list(positions))
    agents = []
    for i, e in enumerate(envs):
        ag = Agent(i, np.random.default_rng(i), env_info_from(e))
        for _ in range(n):
            X = e.draw_arms()
            a = int(e.rng.integers(e.K))
            ag.S_buf.append(e.score(X[a]))
            ag.y_buf.append(e.pull(X, a))
            ag.X_buf.append(X[a])
        agents.append(ag)
    e = envs[0]
    tau = lambda m: tau_default(e.sigma, e.L_f, e.M, m, e.d, 0.01)   # noqa: E731
    return agents, tau, e.theta_star


def _est(name, agents, tau):
    return make_phase1(name, np.random.default_rng(0)).aggregate(agents, tau)[0]


def test_positions():
    envs = make_fed_envs(3, 10, 20, "quadratic", seed=5, run_seed=6, scenario="covariate",
                         strength=[-1.0, 0.5, 2.0])
    for e, c in zip(envs, (-1.0, 0.5, 2.0)):
        assert abs(float(e.ctx_mean @ e.theta_star) - c) < 1e-12
        assert abs(e.mu_star(200_000) - 2 * (1 - c)) < 0.05, "quadratic: mu = 2(1 - c)"
    print("  ok  explicit index means; mu_i = 2(1 - c_i) on the quadratic link")


def test_same_sign_agrees_with_exact():
    agents, tau, th = _agents([0.0, 0.0, 0.3, 0.3], n=4000)
    errs = {k: sin_angle(_est(k, agents, tau), th) for k in ("exact", "aligned", "outer")}
    assert max(errs.values()) < 0.08, errs
    assert sin_angle(_est("exact", agents, tau), _est("aligned", agents, tau)) < 1e-9
    print("  ok  same-sign agents: aligned == exact, outer as accurate", errs)


def test_opposite_signs():
    agents, tau, th = _agents([0.0, 0.0, 2.0, 2.0], n=4000)       # mu = +2, +2, -2, -2
    errs = {k: sin_angle(_est(k, agents, tau), th) for k in ("exact", "aligned", "outer")}
    assert errs["exact"] > 0.5, errs
    assert errs["aligned"] < 0.1 and errs["outer"] < 0.1, errs
    print("  ok  balanced opposite signs: pooled sums fail, sign-invariant pooling recovers", errs)


def test_indep_and_random():
    pos = [0.0, 1.0]
    envs = make_fed_envs(2, 10, 20, "quadratic", seed=1000, run_seed=50_000,
                         scenario="covariate", strength=pos)
    cfg = dict(engine="indep", inner=dict(engine="fed", phase1="exact", phase2="event",
                                          phase2_kw=dict(gamma=0.5), freeze="fixed", T0=600))
    algo = build_fed(cfg, envs, 1500, np.random.default_rng(0))
    run_fed_episode(envs, algo, 1500, record_every=1500)
    dg = algo.diagnostics()
    assert dg["comm_scalars"] == 0
    e0, e1 = (sin_angle(t, envs[0].theta_star) for t in dg["theta_agents"])
    assert e0 < 0.4 < e1, (e0, e1)          # mu = 2 learns alone; mu = 0 does not
    rnd = build_fed(dict(engine="random"), envs, 300, np.random.default_rng(0))
    net, _, _ = run_fed_episode(envs, rnd, 300, record_every=300)
    assert net[-1] > 0
    print(f"  ok  indep: no communication, agent at mu=2 learns ({e0:.2f}), at mu=0 not ({e1:.2f})")


if __name__ == "__main__":
    test_positions()
    test_same_sign_agrees_with_exact()
    test_opposite_signs()
    test_indep_and_random()
    print("all passed")
