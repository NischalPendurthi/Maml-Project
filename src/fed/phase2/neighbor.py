"""neighbor -- serverless, peer-to-peer sharing on a graph.

Every `every` rounds each agent sends ITS OWN new pulls to its neighbours.  An
agent acts on its own table + its neighbours' tables as of the last exchange
(one hop, so nothing is double counted).  graph='complete' recovers `periodic`
without a server; graph='ring' is the sparse extreme.  An explicit boolean
adjacency matrix also works.
"""

from __future__ import annotations

import numpy as np

from .base import PER_BIN, Phase2Strategy


def adjacency(graph, N):
    if not isinstance(graph, str):
        A = np.asarray(graph, dtype=bool).copy()
    elif graph == "complete":
        A = np.ones((N, N), dtype=bool)
    elif graph == "ring":
        A = np.zeros((N, N), dtype=bool)
        for i in range(N):
            A[i, (i + 1) % N] = A[i, (i - 1) % N] = True
    else:
        raise ValueError(f"unknown graph {graph!r}")
    np.fill_diagonal(A, False)
    return A


class NeighborShare(Phase2Strategy):
    name = "neighbor"

    def __init__(self, graph="ring", every=1):
        self.graph = graph
        self.every = int(every)

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.A = adjacency(self.graph, N)
        self.sent_n = np.zeros_like(self.own_n)       # own tables as last sent
        self.sent_S = np.zeros_like(self.own_S)

    def view(self, i):
        nb = self.A[i]
        return (self.own_n[i] + self.sent_n[nb].sum(axis=0),
                self.own_S[i] + self.sent_S[nb].sum(axis=0))

    def end_round(self, t):
        if t % self.every:
            return 0, None
        new_bins = ((self.own_n - self.sent_n) > 0).sum(axis=1)
        cost = PER_BIN * int((new_bins * self.A.sum(axis=1)).sum())
        self.sent_n[:] = self.own_n
        self.sent_S[:] = self.own_S
        return cost, "sync"

    def shared_table(self):
        return self.sent_n.sum(axis=0), self.sent_S.sum(axis=0)

    def pending(self):
        return self.own_n - self.sent_n
