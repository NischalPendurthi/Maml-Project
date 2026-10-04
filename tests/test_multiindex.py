"""Tests for the multi-index extension (src/multiindex/).

    python tests/test_multiindex.py      (~15 s)
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fed.runner import build_fed, make_fed_envs, run_fed_episode   # noqa: E402
from src.multiindex import MIBEnv                                       # noqa: E402
from src.multiindex.stein2 import local_sum, subspace_error, top_m     # noqa: E402


def test_second_order_stein_recovers_subspace():
    for link in ("bowl", "mixed"):
        env = MIBEnv(10, 1, m=2, link=link, seed=3, run_seed=4)
        X = np.vstack([env.draw_arms() for _ in range(60_000)])
        y = env.mean_rewards(X) + env.sigma * env.rng.standard_normal(len(X))
        M = local_sum(env.score(X), y, env.ctx_std ** 2) / len(X)
        assert subspace_error(top_m(M, 2), env.B) < 0.15, link
    print("  ok  second-order Stein recovers span(B) on both links")


def _algo(mi, N=4, T=400):
    envs = make_fed_envs(N, 8, 10, "mib:bowl:2", seed=1000, run_seed=50_000)
    cfg = dict(engine="mib", m=2, mi_phase1=mi, phase2="event", phase2_kw=dict(gamma=0.5),
               freeze="fixed", T0=100, bin_width="network", delta_scale=4.0)
    algo = build_fed(cfg, envs, T, np.random.default_rng(0))
    run_fed_episode(envs, algo, T, record_every=T)
    return algo, envs


def test_exact_pooling_is_centralised():
    N, T0 = 4, 100
    envs = make_fed_envs(N, 8, 10, "mib:bowl:2", seed=1000, run_seed=50_000)
    cfg = dict(engine="mib", m=2, mi_phase1="exact", phase2="event", phase2_kw=dict(gamma=0.5),
               freeze="fixed", T0=T0, bin_width="network", delta_scale=4.0)
    algo = build_fed(cfg, envs, 400, np.random.default_rng(0))
    for _ in range(T0 - 1):                       # stop one round before the freeze
        for i, env in enumerate(envs):
            X = env.draw_arms()
            a = algo.select(i, X)
            algo.update(i, X, a, env.pull(X, a))
        algo.end_round()
    B, scalars, _ = algo._aggregate()
    from src.multiindex.stein2 import tau2_default
    S = np.vstack([np.asarray(ag.S_buf) for ag in algo.agents])
    y = np.concatenate([np.asarray(ag.y_buf) for ag in algo.agents])
    s2 = envs[0].ctx_std ** 2
    tau = tau2_default(algo.sigma, algo.L_f, s2, len(y), 8, algo.delta)
    Bc = top_m(local_sum(S, y, s2, tau) / len(y), 2)
    assert subspace_error(B, Bc) < 1e-10
    assert scalars == N * (8 * 9 // 2 + 1) + N * 8 * 2
    print("  ok  exact matrix pooling equals the centralised estimate; d(d+1)/2 + 1 per agent")


def test_cube_index_roundtrip():
    algo, envs = _algo("projavg")
    X = envs[0].draw_arms()
    b = algo._bins(X)
    Z = X @ algo.B_hat
    inside = np.all(np.abs(Z) <= algo.W, axis=1)
    assert np.all((b >= 1) == inside) and b.max() <= algo.N_bins
    c = np.array(np.unravel_index(b[inside] - 1, (algo.n_side,) * 2)).T
    lo = -algo.W + c * algo.Delta
    assert np.all(Z[inside] >= lo - 1e-9) and np.all(Z[inside] <= lo + algo.Delta + 1e-9)
    print("  ok  m-dimensional cube index round-trips to the right cube")


if __name__ == "__main__":
    test_second_order_stein_recovers_subspace()
    test_exact_pooling_is_centralised()
    test_cube_index_roundtrip()
    print("all passed")
