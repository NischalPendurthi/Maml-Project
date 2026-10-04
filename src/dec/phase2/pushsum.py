"""pushsum -- ratio consensus on the tables (Kempe et al. 2003), interleaved.

Like `consensus`, but agents push mass with column-stochastic out-weights and
track a weight w_i; the estimate N · s_i / w_i is unbiased for the network
total on directed and time-varying graphs, where `consensus` with local
weights is not.
"""

from __future__ import annotations

import numpy as np

from ..gossip import mix
from .base import DecPhase2


class PushSumTables(DecPhase2):
    name = "pushsum"

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.sn = np.zeros((N, n_slots))
        self.sS = np.zeros((N, n_slots))
        self.w = np.ones(N)
        self.ln = np.zeros((N, n_slots))
        self.lS = np.zeros((N, n_slots))

    def _tot(self, i, idx=slice(None)):
        c = self.N / self.w[i]
        return c * self.sn[i, idx], c * self.sS[i, idx]

    def view(self, i):
        n, S = self._tot(i)
        return n + self.own_n[i] - self.ln[i], S + self.own_S[i] - self.lS[i]

    def view_at(self, i, idx):
        n, S = self._tot(i, idx)
        return n + self.own_n[i, idx] - self.ln[i, idx], S + self.own_S[i, idx] - self.lS[i, idx]

    def end_round(self, t):
        self.sn = mix(self.g.C, self.sn + self.own_n - self.ln)
        self.sS = mix(self.g.C, self.sS + self.own_S - self.lS)
        self.w = mix(self.g.C, self.w)
        self.ln = self.own_n.astype(float).copy()
        self.lS = self.own_S.copy()
        return self._state_cost((np.abs(self.sn) > 1e-12).sum(axis=1) + 1), "sync"

    def shared_table(self):
        return self.own_n.sum(axis=0), self.own_S.sum(axis=0)
