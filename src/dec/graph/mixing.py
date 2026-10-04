"""Mixing (communication) matrices P for a graph A.

P[i, j] is the weight agent i gives to agent j's value in one gossip step,
x ← P x.  Consensus to the AVERAGE needs P row-stochastic AND column-stochastic
(doubly stochastic) with P[i, j] > 0 only on edges; its speed is set by
λ = max(|λ₂(P)|, |λ_N(P)|) -- one minus the spectral gap.

  metropolis   P_ij = 1 / (1 + max(d_i, d_j)) on edges, rest on the diagonal.
               Doubly stochastic on any undirected graph, purely local to compute.
  maxdegree    P_ij = 1 / (1 + d_max): uniform weights, needs the global d_max.
  laplacian    P = I − α L with the best constant α = 2 / (λ₁(L) + λ_{N−1}(L))
               (Xiao & Boyd 2004): fastest constant-weight choice, needs the
               spectrum of L.
  lazy         ½ (I + P_metropolis): slower, but all eigenvalues ≥ 0 (no
               oscillation), the usual choice for push-sum style analyses.
  rowstoch     P_ij = 1 / (1 + d_i) over {i} ∪ neighbours: what a naive agent
               would do.  Row- but NOT column-stochastic on irregular graphs, so
               consensus converges to a degree-weighted, BIASED average.

For directed graphs only `rowstoch` (in-neighbours) is defined; push-sum uses
column-stochastic out-weights instead (see colstoch).
"""

from __future__ import annotations

import numpy as np


def _deg(A):
    return A.sum(axis=1)


def metropolis(A):
    d = _deg(A)
    P = np.where(A, 1.0 / (1.0 + np.maximum(d[:, None], d[None, :])), 0.0)
    np.fill_diagonal(P, 1.0 - P.sum(axis=1))
    return P


def maxdegree(A):
    P = np.where(A, 1.0 / (1.0 + _deg(A).max()), 0.0)
    np.fill_diagonal(P, 1.0 - P.sum(axis=1))
    return P


def laplacian(A):
    L = np.diag(_deg(A).astype(float)) - A.astype(float)
    ev = np.sort(np.linalg.eigvalsh(L))
    alpha = 2.0 / (ev[-1] + ev[1]) if len(ev) > 1 and ev[1] > 1e-12 else 1.0 / max(ev[-1], 1)
    return np.eye(len(A)) - alpha * L


def lazy(A):
    return 0.5 * (np.eye(len(A)) + metropolis(A))


def rowstoch(A):
    """In-neighbour averaging: row i averages {i} ∪ {j : j → i}."""
    M = A.T.astype(float) + np.eye(len(A))
    return M / M.sum(axis=1, keepdims=True)


def colstoch(A):
    """Push-sum out-weights: agent j splits its mass equally over {j} ∪ out(j).
    Returns C with C[i, j] = share j sends to i (column-stochastic)."""
    M = A.T.astype(float) + np.eye(len(A))           # M[i, j] = 1 if j → i or i == j
    return M / M.sum(axis=0, keepdims=True)


MIXING = {f.__name__: f for f in (metropolis, maxdegree, laplacian, lazy, rowstoch)}


def mixing_matrix(A, kind="metropolis"):
    symmetric = np.array_equal(A, A.T)
    if not symmetric and kind != "rowstoch":
        kind = "rowstoch"                     # the only local rule defined on digraphs
    return MIXING[kind](A)


def second_eigenvalue(P):
    """λ = max(|λ₂|, |λ_N|): the per-step contraction of disagreement."""
    ev = np.linalg.eigvals(P)
    ev = ev[np.argsort(-np.abs(ev))]
    return float(np.abs(ev[1])) if len(ev) > 1 else 0.0


def is_doubly_stochastic(P, tol=1e-9):
    return bool(np.allclose(P.sum(0), 1, atol=tol) and np.allclose(P.sum(1), 1, atol=tol))
