"""`Graph`: a topology + mixing rule + (optional) per-round dynamics.

The engine calls `step()` once per bandit round; strategies then read the
round's realised adjacency `A`, mixing matrix `P` and push-sum weights `C`.

Dynamics
  failure = q   each undirected edge is independently down this round w.p. q
                (mixing weights recomputed on the surviving graph)
  matching      randomised pairwise gossip (Boyd et al. 2006): each round a
                random matching of the graph's edges is active
"""

from __future__ import annotations

import numpy as np

from .mixing import colstoch, is_doubly_stochastic, mixing_matrix, second_eigenvalue
from .topologies import TOPOLOGIES


def _diameter(A):
    N = A.shape[0]
    best = 0
    for s in range(N):
        dist = np.full(N, -1)
        dist[s] = 0
        frontier = [s]
        while frontier:
            nxt = np.flatnonzero(A[frontier].any(axis=0) & (dist < 0))
            dist[nxt] = dist[frontier[0]] + 1 if frontier else 0
            frontier = list(nxt)
        if (dist < 0).any():
            return np.inf
        best = max(best, int(dist.max()))
    return best


def bfs_tree(A, root=0):
    """Parent array of a BFS spanning tree (undirected A) and its depth."""
    N = A.shape[0]
    parent = np.full(N, -1)
    depth = np.full(N, -1)
    depth[root] = 0
    frontier = [root]
    while frontier:
        nxt = []
        for u in frontier:
            for v in np.flatnonzero(A[u] & (depth < 0)):
                parent[v], depth[v] = u, depth[u] + 1
                nxt.append(v)
        frontier = nxt
    return parent, int(depth.max())


class Graph:
    def __init__(self, topology="ring", N=8, mixing="metropolis", failure=0.0,
                 matching=False, seed=0, A=None, **topo_kw):
        rng = np.random.default_rng(seed)
        self.name = topology if A is None else "custom"
        self.A0 = np.asarray(A, dtype=bool) if A is not None else \
            TOPOLOGIES[topology](N, rng, **topo_kw)
        np.fill_diagonal(self.A0, False)
        self.N = self.A0.shape[0]
        self.mixing = mixing
        self.symmetric = bool(np.array_equal(self.A0, self.A0.T))
        self.P0 = mixing_matrix(self.A0, mixing)
        self.C0 = colstoch(self.A0)
        self.failure = float(failure)
        self.matching = bool(matching)
        self.dynamic = self.failure > 0 or self.matching
        self._rng = np.random.default_rng([seed, 99])
        self.diameter = _diameter(self.A0)
        self.lam = second_eigenvalue(self.P0)
        self.gap = 1.0 - self.lam
        self.doubly_stochastic = is_doubly_stochastic(self.P0)
        self.n_edges = int(self.A0.sum() // (2 if self.symmetric else 1))
        self.A, self.P, self.C = self.A0, self.P0, self.C0
        self.t = 0

    # -- dynamics ------------------------------------------------------------
    def step(self):
        self.t += 1
        if not self.dynamic:
            return
        A = self.A0.copy()
        if self.matching:
            iu, ju = np.nonzero(np.triu(A, 1))
            order = self._rng.permutation(len(iu))
            used = np.zeros(self.N, dtype=bool)
            A[:] = False
            for k in order:
                i, j = iu[k], ju[k]
                if not used[i] and not used[j]:
                    A[i, j] = A[j, i] = True
                    used[i] = used[j] = True
        if self.failure > 0:
            if self.symmetric:
                up = np.triu(self._rng.random(A.shape) >= self.failure, 1)
                A &= up | up.T
            else:
                A &= self._rng.random(A.shape) >= self.failure
        self.A = A
        self.P = mixing_matrix(A, self.mixing) if self.symmetric else mixing_matrix(A, "rowstoch")
        self.C = colstoch(A)

    def arcs(self):
        """Number of directed transmissions this round (one per arc)."""
        return int(self.A.sum())

    def describe(self):
        return (f"{self.name} (N={self.N}, edges={self.n_edges}, diameter={self.diameter}, "
                f"λ={self.lam:.3f}, gap={self.gap:.3f}, "
                f"mixing={self.mixing if self.symmetric else 'rowstoch'}"
                + (f", failure={self.failure}" if self.failure else "")
                + (", matching" if self.matching else "") + ")")
