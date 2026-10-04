"""Decentralised Phase-2 strategies: sharing the bin table (n_j, S_j) over a graph.

Same interface as src/fed/phase2 (setup / record / view / view_at / end_round),
plus `attach(graph)`, called by the engine before setup.  The engine steps the
graph once per bandit round, so `self.g.A`, `.P`, `.C` are the current round's.

Communication is counted per transmitted table entry: 3 scalars (bin index,
count, sum) per non-zero bin.
"""

from __future__ import annotations

import numpy as np

from ...fed.phase2.base import Phase2Strategy

PER_BIN = 3


class DecPhase2(Phase2Strategy):
    name = "base"

    def attach(self, graph):
        self.g = graph

    def _state_cost(self, nnz_per_agent, k=1):
        """Each agent sends its state (nnz bins) to each out-neighbour, k times."""
        outdeg = self.g.A.sum(axis=1)
        return int(k * PER_BIN * (outdeg * nnz_per_agent).sum())
