"""flood -- exact pooling by relaying records (interleaved).

Every agent stores the freshest copy it has heard of EVERY agent's record
(Stein sum, count), stamped with the round it was produced.  Each round it
refreshes its own record and swaps records with its neighbours, keeping the
freshest copy of each.  Agent k's record reaches agent i after dist(i, k)
rounds, so every estimate is the EXACT pooled sum of slightly stale data --
no consensus error at all, at the price of sending up to N records per arc.
"""

from __future__ import annotations

import numpy as np

from ..gossip import relay
from .base import DecPhase1


class Flood(DecPhase1):
    name = "flood"
    interleaved = True

    def setup(self, N, d, graph):
        super().setup(N, d, graph)
        self.kb = np.zeros((N, N, d))            # kb[i, k] = agent i's copy of k's sum
        self.kv = np.full((N, N), -1)

    def on_round(self, t, own_b, own_n):
        idx = np.arange(self.N)
        self.kb[idx, idx] = own_b
        self.kv[idx, idx] = np.where(own_n > 0, t, -1)
        new_v, src, sent = relay(self.kv, self.g.A)
        self.kb = self.kb[src, np.arange(self.N)[None, :]]
        self.kv = new_v
        return sent * (self.d + 2)                # (sum, count, version)

    def estimate(self, t, own_b, own_n):
        return self.kb.sum(axis=1), 0, 0
