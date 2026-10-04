"""consensus -- running consensus (interleaved), one gossip step per round.

State x_i starts at agent i's sum; each round x ← P (x + Δ), where Δ_i is
agent i's NEW contribution since last round.  If P is doubly stochastic the
network total Σ x_i always equals the true pooled sum, so every x_i tracks the
average with a lag set by the spectral gap (Braca et al. 2008; the Phase-1
analogue of Landgren et al.'s cooperative UCB).  With a row-stochastic P the
total is NOT preserved: degree-weighted bias.  `steps` gossip steps per round.
"""

from __future__ import annotations

import numpy as np

from ..gossip import plain
from .base import DecPhase1, vec_cost


class RunningConsensus(DecPhase1):
    name = "consensus"
    interleaved = True

    def __init__(self, steps=1):
        self.steps = int(steps)

    def setup(self, N, d, graph):
        super().setup(N, d, graph)
        self.x = np.zeros((N, d))
        self.last = np.zeros((N, d))

    def on_round(self, t, own_b, own_n):
        self.x = plain(self.g.P, self.x + (own_b - self.last), self.steps)
        self.last = own_b.copy()
        return vec_cost(self.g, self.d, self.steps)

    def estimate(self, t, own_b, own_n):
        return self.x.copy(), 0, 0
