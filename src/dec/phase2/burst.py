"""gossip -- k gossip steps on the cumulative tables every `every` rounds (burst).

After k steps agent i holds a WEIGHTED combination of everyone's tables with
weights w_i = row i of P^k (or of the Chebyshev polynomial when accelerated).
Two ways to turn that into a table to act on:

  ess=False  naive:  n = N Σ_k w_ik n_k  -- right only once w_i ≈ 1/N, and
             over-confident before that
  ess=True   effective sample size:  mean = Σ w S / Σ w n  (a weighted mean of
             real pulls, still unbiased), with count
             n_eff = (Σ_k w_ik n_k)² / Σ_k w_ik² n_k  -- the variance-correct
             count for a weighted mean.  It equals the true total when the
             weights are uniform and the agent's own count when they are not
             mixed at all, so the UCB width is never over-confident.

Between bursts agents add their own new pulls.
"""

from __future__ import annotations

import numpy as np

from ..gossip import chebyshev, plain
from .base import DecPhase2


class BurstGossipTables(DecPhase2):
    name = "gossip"

    def __init__(self, k=5, every=10, accelerate=False, ess=True):
        self.k, self.every = int(k), int(every)
        self.accelerate, self.ess = bool(accelerate), bool(ess)

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.Tn = np.zeros((N, n_slots))
        self.TS = np.zeros((N, n_slots))
        self.bn = np.zeros((N, n_slots))          # own table at the last burst
        self.bS = np.zeros((N, n_slots))

    def view(self, i):
        return self.Tn[i] + self.own_n[i] - self.bn[i], self.TS[i] + self.own_S[i] - self.bS[i]

    def view_at(self, i, idx):
        return (self.Tn[i, idx] + self.own_n[i, idx] - self.bn[i, idx],
                self.TS[i, idx] + self.own_S[i, idx] - self.bS[i, idx])

    def end_round(self, t):
        if t % self.every:
            return 0, None
        I = np.eye(self.N)
        Wm = chebyshev(self.g.P, I, self.k, self.g.lam) if self.accelerate \
            else plain(self.g.P, I, self.k)
        n, S = self.own_n.astype(float), self.own_S
        wn, wS = Wm @ n, Wm @ S
        if self.ess:
            den = (Wm ** 2) @ n
            ok = (wn > 0) & (den > 0)
            neff = np.where(ok, wn ** 2 / np.where(ok, den, 1), n)
            mean = np.where(ok, wS / np.where(ok, wn, 1), np.where(n > 0, S / np.maximum(n, 1), 0))
            self.Tn, self.TS = neff, mean * neff
        else:
            self.Tn, self.TS = np.maximum(self.N * wn, 0), self.N * wS
        self.bn, self.bS = n.copy(), S.copy()
        return self._state_cost((n > 0).sum(axis=1), self.k), "sync"

    def shared_table(self):
        return self.own_n.sum(axis=0), self.own_S.sum(axis=0)
