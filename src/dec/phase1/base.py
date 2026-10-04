"""Decentralised Phase-1 strategies: pooling θ with no server, over a graph.

Every agent ends with its OWN estimate θ̂_i -- consensus is never exact in
finitely many gossip steps, so agents may disagree slightly at the freeze.

Two communication models, stated per strategy:
  interleaved  one exchange with neighbours per bandit round (`on_round`):
               communication and sampling proceed together, information is
               delayed by graph distance
  burst        k exchanges between two bandit rounds, at each checkpoint
               (`estimate`): communication is assumed fast relative to pulls

Inputs at every call: own_b (N, d) each agent's truncated Stein sum and own_n
(N,) its sample count, recomputed by the engine with the current τ.
`estimate` returns per-agent vectors proportional to the pooled mean (any
positive scale: they are l1-normalised into θ̂_i), plus the scalars sent and
the communication rounds used.
"""

from __future__ import annotations

import numpy as np


class DecPhase1:
    name = "base"
    interleaved = False

    def setup(self, N, d, graph):
        self.N, self.d, self.g = N, d, graph

    def on_round(self, t, own_b, own_n):
        """Interleaved communication; -> scalars sent this round."""
        return 0

    def estimate(self, t, own_b, own_n):
        """-> (est (N, d), scalars, rounds)."""
        raise NotImplementedError


def vec_cost(graph, d, k=1):
    """Every arc carries one (d+1)-vector, k times."""
    return k * graph.arcs() * (d + 1)
