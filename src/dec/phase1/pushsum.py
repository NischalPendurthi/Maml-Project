"""pushsum -- ratio consensus (Kempe et al. 2003), interleaved.

Each agent holds mass (s_i, w_i) and every round keeps a share and pushes
equal shares to its out-neighbours (column-stochastic weights).  s_i / w_i
converges to the AVERAGE on any strongly connected graph -- directed, and
time-varying -- where plain consensus with local weights would be biased.
New samples are added to s as they arrive.
"""

from __future__ import annotations

import numpy as np

from ..gossip import mix
from .base import DecPhase1


class PushSum(DecPhase1):
    name = "pushsum"
    interleaved = True

    def setup(self, N, d, graph):
        super().setup(N, d, graph)
        self.s = np.zeros((N, d))
        self.w = np.ones(N)
        self.last = np.zeros((N, d))

    def on_round(self, t, own_b, own_n):
        self.s = mix(self.g.C, self.s + (own_b - self.last))
        self.w = mix(self.g.C, self.w)
        self.last = own_b.copy()
        return self.g.arcs() * (self.d + 1)

    def estimate(self, t, own_b, own_n):
        return self.s / self.w[:, None], 0, 0
