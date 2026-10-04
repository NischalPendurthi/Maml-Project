"""Checks for the decentralised (communication-matrix) layer.  Run: python tests/test_dec.py"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dec.gossip import chebyshev, flood_max, mix, plain        # noqa: E402
from src.dec.graph import TOPOLOGIES, Graph, is_connected          # noqa: E402
from src.dec.phase1 import make_dec_phase1                         # noqa: E402
from src.dec.phase2 import make_dec_phase2                         # noqa: E402
from src.fed import build_fed, make_fed_envs, run_fed_episode      # noqa: E402

N, d = 16, 10


def _data(seed=0):
    rng = np.random.default_rng(seed)
    n = rng.integers(20, 60, N).astype(float)
    b = n[:, None] * (0.5 + 0.2 * rng.standard_normal((N, d)))
    return b, n, b.sum(0)


def test_graphs():
    for name in TOPOLOGIES:
        g = Graph(name, N, seed=3)
        assert is_connected(g.A0), name
        if g.symmetric:
            assert g.doubly_stochastic, name
    g = Graph("directed", N)
    assert not g.doubly_stochastic and np.allclose(g.C.sum(0), 1)
    print(f"  ok  {len(TOPOLOGIES)} topologies connected; undirected mixing doubly stochastic")


def test_consensus_primitives():
    g = Graph("ring", N)
    X = np.random.default_rng(0).standard_normal((N, 3))
    avg = X.mean(0)
    assert np.allclose(mix(g.P, X).sum(0), X.sum(0))                     # mass preserved
    e_plain = np.abs(plain(g.P, X, 20) - avg).max()
    e_cheb = np.abs(chebyshev(g.P, X, 20, g.lam) - avg).max()
    assert e_cheb < e_plain / 10, (e_cheb, e_plain)
    assert np.allclose(flood_max(g.A0, np.arange(N), g.diameter), N - 1)
    print(f"  ok  gossip: 20 plain steps err {e_plain:.1e}, Chebyshev {e_cheb:.1e}; max-consensus exact")


def test_phase1_exactness():
    b, n, total = _data()
    target = total / np.abs(total).sum()
    for topo in ("ring", "expander", "directed"):
        g = Graph(topo, N)
        res = {}
        for name, kw in [("tree", {}), ("server", {}), ("flood", {}), ("pushsum", {}),
                         ("consensus", {}), ("gt", dict(k=600, lr=0.02))]:
            if name == "tree" and not g.symmetric:
                continue
            s = make_dec_phase1(name, **kw)
            s.setup(N, d, g)
            if s.interleaved:
                for t in range(1, 3 * g.diameter + 200):
                    s.on_round(t, b, n)
            est = s.estimate(1, b, n)[0]
            est = est / np.abs(est).sum(1, keepdims=True)
            res[name] = float(np.abs(est - target).sum(1).max())
        exact = [k for k in ("tree", "server", "flood") if k in res]
        assert all(res[k] < 1e-12 for k in exact), res
        assert res["pushsum"] < 1e-6, res
        if g.symmetric:
            assert res["consensus"] < 1e-6 and res["gt"] < 1e-3, res
        else:                    # row-stochastic consensus is biased on a digraph
            assert res["consensus"] > 1e-3, res
        print(f"  ok  phase1 on {topo:<9}" + "  ".join(f"{k}={v:.0e}" for k, v in res.items()))


def test_phase2_flood_and_ess():
    g = Graph("ring", N)
    fl = make_dec_phase2("flood"); fl.attach(g); fl.setup(N, 30)
    gs = make_dec_phase2("gossip", k=3, every=1, ess=True); gs.attach(g); gs.setup(N, 30)
    rng = np.random.default_rng(0)
    for _ in range(400):
        i, j, y = int(rng.integers(N)), int(rng.integers(1, 29)), float(rng.normal())
        fl.record(i, j, y); gs.record(i, j, y)
    gs.end_round(1)
    for t in range(1, g.diameter + 2):
        fl.end_round(t)
    tot = fl.own_n.sum(0)
    for i in range(N):
        n, _ = fl.view(i)
        assert np.allclose(n, tot)
        ne, _ = gs.view(i)
        assert np.all(ne <= tot + 1e-9) and np.all(ne >= fl.own_n[i] - 1e-9)
    print(f"  ok  phase2 flood exact after diameter={g.diameter} rounds; ESS counts in [own, total]")


def test_engine_everywhere():
    for topo, kw in [("ring", {}), ("star", {}), ("directed", {}), ("torus", dict(failure=0.5)),
                     ("expander", dict(matching=True))]:
        envs = make_fed_envs(N, d, 20, "quadratic", seed=1000, run_seed=1)
        cfg = dict(engine="dec", graph=topo, graph_kw=kw, phase1="pushsum", phase2="pushsum")
        a = build_fed(cfg, envs, 1500, np.random.default_rng(0))
        net = run_fed_episode(envs, a, 1500, record_every=1500)[0]
        assert np.isfinite(net[-1]) and a.phase == 2
    print("  ok  decentralised engine runs on ring, star, directed, failing torus, matching expander")


if __name__ == "__main__":
    test_graphs()
    test_consensus_primitives()
    test_phase1_exactness()
    test_phase2_flood_and_ess()
    test_engine_everywhere()
    print("all passed")
