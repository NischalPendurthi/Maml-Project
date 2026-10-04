"""Burst gossip at each checkpoint: k exchanges between two bandit rounds.

  gossip      k plain steps x ← P x on the agents' current sums
  chebyshev   k Chebyshev-accelerated steps (needs λ of P)
  tree        exact: convergecast up a BFS spanning tree and broadcast back
              (2·depth rounds, 2(N−1) messages); assumes an undirected static graph
"""

from __future__ import annotations

import numpy as np

from ..gossip import chebyshev, plain
from ..graph import bfs_tree
from .base import DecPhase1, vec_cost


class BurstGossip(DecPhase1):
    name = "gossip"

    def __init__(self, k=10, accelerate=False):
        self.k = int(k)
        self.accelerate = bool(accelerate)

    def estimate(self, t, own_b, own_n):
        X = np.concatenate([own_b, own_n[:, None]], axis=1)
        if self.accelerate:
            X = chebyshev(self.g.P, X, self.k, self.g.lam)
        else:
            X = plain(self.g.P, X, self.k)
        return X[:, :-1], vec_cost(self.g, self.d, self.k), self.k


class Chebyshev(BurstGossip):
    name = "chebyshev"

    def __init__(self, k=10):
        super().__init__(k=k, accelerate=True)


class Tree(DecPhase1):
    name = "tree"

    def setup(self, N, d, graph):
        super().setup(N, d, graph)
        if not graph.symmetric:
            raise ValueError("tree aggregation needs an undirected graph")
        self.parent, self.depth = bfs_tree(graph.A0)

    def estimate(self, t, own_b, own_n):
        total = own_b.sum(axis=0)                       # what the root assembles
        cost = 2 * (self.N - 1) * (self.d + 1)
        return np.tile(total, (self.N, 1)), cost, 2 * self.depth
