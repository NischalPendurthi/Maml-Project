"""Sanity checks for Fed-ZoomSIB.  Run:  python tests/test_fedzoomsib.py"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fed import PHASE2, build_fed, make_fed_envs, run_fed_episode  # noqa: E402
from src.stein import stein_estimate, tau_default                     # noqa: E402


FED = dict(engine="fed", phase1="exact", phase2="periodic", phase2_kw=dict(every=1))


def test_phase1_pools_exactly():
    """Average of agents' uploads == centralised Stein on the pooled sample."""
    N, d, K, n = 6, 10, 20, 137
    envs = make_fed_envs(N, d, K, "quadratic", seed=3, run_seed=7)
    algo = build_fed(FED, envs, 10_000, np.random.default_rng(0))
    for _ in range(n):
        for i, env in enumerate(envs):
            X = env.draw_arms()
            a = algo.select(i, X)
            algo.update(i, X, a, env.pull(X, a))
    S = np.concatenate([np.asarray(ag.S_buf) for ag in algo.agents])
    y = np.concatenate([np.asarray(ag.y_buf) for ag in algo.agents])
    e = envs[0]
    tau = tau_default(e.sigma, e.L_f, e.M, N * n, d, algo.delta)
    pooled = stein_estimate(S, y, tau=tau)
    fed = algo.federated_theta()
    err = float(np.abs(fed - pooled).max())
    assert err < 1e-12, err
    print(f"  ok  phase-1 exact pooling   max|fed - pooled| = {err:.1e}")


def test_phase1_shrinks_with_N():
    """Per-agent exploration ~ 1/N; network exploration roughly flat."""
    rows = []
    for N in (1, 4, 16):
        t0 = []
        for s in range(5):
            envs = make_fed_envs(N, 10, 20, "quadratic", seed=1000 + s, run_seed=s)
            algo = build_fed(FED, envs, 2_000, np.random.default_rng(s))
            run_fed_episode(envs, algo, 2_000, record_every=2_000)
            t0.append(algo.T0_used)
        rows.append((N, np.mean(t0)))
        print(f"  N={N:<3} per-agent T0 = {np.mean(t0):7.1f}   network N*T0 = {N*np.mean(t0):7.1f}")
    assert rows[-1][1] < rows[0][1] / 4


def test_phase2_bookkeeping():
    """Every Phase-2 strategy accounts for every binned pull exactly once."""
    N, T = 4, 3_000
    for name, kw in [("periodic", dict(every=7)), ("none", {}), ("event", dict(gamma=1.0)),
                     ("neighbor", dict(graph="ring", every=3))]:
        envs = make_fed_envs(N, 10, 20, "zigzag", seed=1, run_seed=1)
        cfg = dict(FED, phase2=name, phase2_kw=kw)
        algo = build_fed(cfg, envs, T, np.random.default_rng(1))
        run_fed_episode(envs, algo, T, record_every=T)
        own = int(algo.p2.own_n.sum())
        shared = int(algo.p2.shared_table()[0].sum()) + int(algo.p2.pending().sum())
        in_window = N * (T - algo.T0_used)
        assert own == int(algo.contrib.sum()) and 0.9 * in_window < own <= in_window
        if name != "none":
            assert shared == own, (name, shared, own)
        print(f"  ok  phase2={name:<9} {own} of {in_window} pulls binned, "
              f"{algo.comm_scalars:,} scalars sent")


if __name__ == "__main__":
    test_phase1_pools_exactly()
    test_phase1_shrinks_with_N()
    test_phase2_bookkeeping()
    print("all passed")
