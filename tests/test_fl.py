"""Checks for the FL-method layer and the heterogeneity scenarios.

Run:  python tests/test_fl.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fed import build_fed, make_fed_envs, run_fed_episode       # noqa: E402
from src.fed.fl import FL_METHODS, FedQuadratic, make_fl            # noqa: E402

BASE = dict(engine="fed", phase1="exact", phase2="periodic", phase2_kw=dict(every=1))


def _run(cfg, T=2_500, N=4, link="quadratic", scenario="iid", seed=0):
    envs = make_fed_envs(N, 10, 20, link, seed=1000 + seed, run_seed=seed, scenario=scenario)
    algo = build_fed(cfg, envs, T, np.random.default_rng(seed))
    net, per, _ = run_fed_episode(envs, algo, T)
    return net, algo


def test_suffstat_reproduces_exact_strategies():
    """fl+suffstat must reproduce phase1 'exact' and phase2 'periodic' bit-for-bit."""
    ref, a_ref = _run(dict(BASE, phase2_kw=dict(every=5)))
    fl1, a1 = _run(dict(BASE, phase1="fl", phase1_kw=dict(method="suffstat"),
                        phase2_kw=dict(every=5)))
    fl2, a2 = _run(dict(BASE, phase2="fl", phase2_kw=dict(method="suffstat", every=5)))
    assert np.array_equal(a_ref.theta_hat, a1.theta_hat)
    assert np.allclose(ref, fl1) and np.allclose(ref, fl2), (ref[-1], fl1[-1], fl2[-1])
    print(f"  ok  fl/suffstat ≡ exact (phase 1) and ≡ periodic (phase 2): R_T = {ref[-1]:.1f}")


def test_drift_correctors_reach_pooled_optimum():
    """On a heterogeneous diagonal problem SCAFFOLD/FedDyn/FedSGD converge to w*,
    while model averaging with many local steps stays biased."""
    rng = np.random.default_rng(0)
    H = rng.poisson(rng.gamma(0.5, 20, (8, 30))).astype(float)
    S = H * (rng.standard_normal(30)[None] + 0.3 * rng.standard_normal((8, 30)))
    prob = FedQuadratic(H, S, H.sum(1), diag=True)
    w_star = prob.pooled(np.zeros(30))
    err = {}
    for k in ("scaffold", "feddyn", "fedsgd", "fedavg", "oneshot"):
        w, _, _ = make_fl(k).solve(prob, np.zeros(30), 300)
        err[k] = np.linalg.norm(w - w_star) / np.linalg.norm(w_star)
    assert err["scaffold"] < 1e-6 and err["feddyn"] < 1e-4 and err["fedsgd"] < 1e-3
    assert err["fedavg"] > 1e-2 and err["oneshot"] > 1e-2
    print("  ok  heterogeneous bins: " + "  ".join(f"{k}={v:.0e}" for k, v in err.items()))


def test_every_method_runs_in_both_phases():
    for k in FL_METHODS:
        for phase in (1, 2):
            cfg = (dict(BASE, phase1="fl", phase1_kw=dict(method=k, rounds=3)) if phase == 1
                   else dict(BASE, phase2="fl", phase2_kw=dict(method=k, rounds=2, every=10)))
            net, algo = _run(cfg, T=800, N=3)
            assert np.isfinite(net[-1]) and algo.phase == 2, (k, phase)
    print(f"  ok  all {len(FL_METHODS)} FL methods run in phase 1 and phase 2")


def test_scenarios():
    envs = make_fed_envs(6, 10, 20, "quadratic", seed=1, run_seed=1, scenario="participation")
    rates = [np.mean([e.is_active() for _ in range(4000)]) for e in envs]
    assert abs(rates[0] - 1.0) < 0.02 and abs(rates[-1] - 0.2) < 0.03
    envs = make_fed_envs(6, 10, 20, "quadratic", seed=1, run_seed=1, scenario="covariate")
    c = [float(e.ctx_mean @ e.theta_star) for e in envs]
    X = envs[-1].draw_arms()
    assert np.allclose(envs[-1].score(X), (X - envs[-1].ctx_mean) / envs[-1].ctx_std ** 2)
    mus = [e.mu_star() for e in envs]
    envs = make_fed_envs(6, 10, 20, "quadratic", seed=1, run_seed=1, scenario="concept")
    th = np.array([e.theta_star for e in envs])
    assert np.allclose(np.abs(th).sum(1), 1) and np.abs(th[0] - th[1]).sum() > 0.05
    for sc in ("participation", "covariate", "concept"):
        net, algo = _run(BASE, T=1_500, N=6, scenario=sc)
        assert np.isfinite(net[-1])
    print(f"  ok  scenarios: participation {rates[0]:.2f}…{rates[-1]:.2f}; covariate index means "
          f"{c[0]:+.1f}…{c[-1]:+.1f}, mu_i {mus[0]:+.2f}…{mus[-1]:+.2f}; concept θ* spread "
          f"{np.abs(th[0] - th[1]).sum():.2f}")


def test_view_at_matches_view():
    """Every Phase-2 strategy's fast path must agree with its full view."""
    from src.fed.phase2 import PHASE2
    rng = np.random.default_rng(0)
    for name, cls in PHASE2.items():
        kw = dict(method="suffstat") if name == "fl" else {}
        st = cls(**kw)
        st.setup(4, 20)
        for _ in range(200):
            st.record(int(rng.integers(4)), int(rng.integers(1, 19)), float(rng.normal()))
        st.end_round(1)
        for _ in range(30):
            st.record(int(rng.integers(4)), int(rng.integers(1, 19)), float(rng.normal()))
        idx = np.array([1, 5, 7, 18])
        for i in range(4):
            n, S = st.view(i)
            n2, S2 = st.view_at(i, idx)
            assert np.allclose(n[idx], n2) and np.allclose(S[idx], S2), name
    print(f"  ok  view_at ≡ view for all {len(PHASE2)} Phase-2 strategies")


if __name__ == "__main__":
    test_suffstat_reproduces_exact_strategies()
    test_drift_correctors_reach_pooled_optimum()
    test_every_method_runs_in_both_phases()
    test_scenarios()
    test_view_at_matches_view()
    print("all passed")
