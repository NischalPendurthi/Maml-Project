"""Tests for the Paper A experiment infrastructure: fixed-T0 fed engine, the
Phase-1/Phase-2 accounting split, compressors, and the compressed Phase-1 upload.

    python tests/test_claims_infra.py      (~10 s)
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fed.compress import ErrorFeedback, compress, quantize, randk, topk   # noqa: E402
from src.fed.runner import build_fed, make_fed_envs, run_fed_episode          # noqa: E402

BASE = dict(engine="fed", phase1="exact", phase2="event", phase2_kw=dict(gamma=0.5),
            freeze="fixed", T0=40, bin_width="network")


def _run(cfg, N=8, T=1500, seed=0):
    envs = make_fed_envs(N, 10, 20, "quadratic", seed=1000 + seed, run_seed=50_000 + seed)
    algo = build_fed(dict(cfg), envs, T, np.random.default_rng([90_000, seed, N]))
    net, _, _ = run_fed_episode(envs, algo, T, record_every=T)
    return net[-1], algo.diagnostics()


def test_fixed_T0():
    _, dg = _run(BASE)
    assert dg["T0_used"] == 40
    # exactly one aggregation + the freeze message, no stop flags
    assert dg["comm_rounds_phase1"] == 2
    assert dg["comm_phase1"] == 8 * 11 + (8 + 8 * 11)
    print("  ok  fixed T0: one Phase-1 aggregation, no checkpoints")


def test_accounting_split():
    _, dg = _run(BASE)
    log = dg["comm_log"]
    assert log[log[:, 3] == 1, 1].sum() == dg["comm_phase1"]
    assert log[:, 1].sum() == dg["comm_scalars"]
    assert log[:, 2].sum() == dg["comm_bits"]
    syncs = dg["comm_rounds"] - dg["comm_rounds_phase1"]
    assert syncs == (log[:, 3] == 2).sum() and dg["trigger_counts"].sum() >= syncs
    print("  ok  comm_log reproduces every counter; trigger counts cover every sync")


def test_compressors():
    rng = np.random.default_rng(0)
    v = rng.standard_normal(20)
    mq = np.mean([quantize(v, 2, rng)[0] for _ in range(4000)], axis=0)
    mr = np.mean([randk(v, 5, rng)[0] for _ in range(4000)], axis=0)
    assert np.abs(mq - v).max() < 0.1, "stochastic quantisation is unbiased"
    assert np.abs(mr - v).max() < 0.25, "rand-k is unbiased"
    t, b = topk(v, 5)
    assert (t != 0).sum() == 5 and b == 2 * 5 * 32
    assert np.allclose(compress(v, None, rng)[0], v)
    ef = ErrorFeedback(dict(kind="topk", k=5), rng)
    sent = sum(ef("a", v)[0] for _ in range(4))
    assert np.allclose(sent + ef.e["a"], 4 * v), "error feedback loses nothing"
    print("  ok  quantize/rand-k unbiased, top-k sparse, error feedback conserves mass")


def test_compressed_phase1():
    r0, d0 = _run(BASE)
    r2, _ = _run(dict(BASE, phase1="compressed", phase1_kw=dict(compressor=None)))
    assert r2 == r0, "uncompressed Phase-1 upload == exact"
    _, d3 = _run(dict(BASE, phase1="compressed",
                      phase1_kw=dict(compressor=dict(kind="quant", bits=4))))
    assert d3["comm_phase1_bits"] < d0["comm_phase1_bits"]
    print("  ok  compressed Phase-1 upload reduces to exact and reports real bits")


if __name__ == "__main__":
    test_fixed_T0()
    test_accounting_split()
    test_compressors()
    test_compressed_phase1()
    print("all passed")
