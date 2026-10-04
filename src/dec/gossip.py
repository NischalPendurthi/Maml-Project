"""Gossip primitives shared by the Phase-1 and Phase-2 strategies.

All operate on per-agent state X of shape (N, ...) and a mixing matrix P.
"""

from __future__ import annotations

import numpy as np


def mix(P, X):
    """One gossip step x_i ← Σ_j P_ij x_j, for any trailing shape."""
    return np.tensordot(P, X, axes=(1, 0))


def plain(P, X, k):
    for _ in range(int(k)):
        X = mix(P, X)
    return X


def chebyshev(P, X, k, lam):
    """k steps of Chebyshev-accelerated consensus (Scaman et al. 2017; used by
    Amani & Thrampoulidis' DLUCB).  Applies T_k(P/λ) / T_k(1/λ) to X: on a
    symmetric doubly-stochastic P the disagreement contracts like
    (1 − √(1−λ))^k instead of λ^k.  λ = max(|λ₂|, |λ_N|) of P must be known."""
    k = int(k)
    if k == 0:
        return X
    if lam < 1e-8:                           # P already averages in one step (complete graph)
        return mix(P, X)
    x_prev, x = X, mix(P, X)                 # T_0 = 1, T_1(P/λ)/T_1(1/λ) = P
    mu_prev, mu = 1.0, 1.0 / lam
    for _ in range(k - 1):
        mu_next = 2.0 / lam * mu - mu_prev
        x_next = (2.0 / lam) * (mu / mu_next) * mix(P, x) - (mu_prev / mu_next) * x_prev
        x_prev, x, mu_prev, mu = x, x_next, mu, mu_next
    return x


def flood_max(A, v, rounds):
    """Max-consensus: after `rounds` ≥ diameter steps every agent holds max(v)."""
    v = np.asarray(v, dtype=float).copy()
    M = A.T | np.eye(len(A), dtype=bool)          # i hears from j if j → i
    for _ in range(int(rounds)):
        v = np.where(M, v[None, :], -np.inf).max(axis=1)
    return v


def relay(known_v, A):
    """One flooding step over arcs A for version-stamped entries.

    known_v[i, k] = version of agent k's record that agent i holds (−1 = none).
    Each agent adopts, per record, the freshest copy among itself and its
    in-neighbours.  Returns (new versions, source agent per (i, k), number of
    records that were sent fresher than the receiver's copy)."""
    N = known_v.shape[0]
    M = A.T | np.eye(N, dtype=bool)               # M[i, j]: i hears from j (or itself)
    cand = np.where(M[:, :, None], known_v[None, :, :], -2)       # (i, j, k)
    src = cand.argmax(axis=1)                                     # (i, k)
    new_v = np.take_along_axis(cand, src[:, None, :], axis=1)[:, 0, :]
    sent = int(((A.T[:, :, None]) & (known_v[None, :, :] > known_v[:, None, :])).sum())
    return new_v, src, sent
