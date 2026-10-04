"""consensus -- running consensus on the tables (Landgren, Srivastava & Leonard 2016).

State x_i ≈ network-AVERAGE table; each round x ← P (x + Δ) with Δ_i agent i's
new pulls.  Agents act on N · x_i (an estimate of the network total) plus their
own newest pulls.  Counts become fractional, and early on N · x_i over-states
how much agent i really knows -- the reason Landgren et al. inflate the
confidence width.  `steps` gossip steps per round; `inflate` multiplies the
count down by that factor (≥ 1) as a crude version of their correction.
Interleaved: every agent sends its whole (non-zero) state to every neighbour,
every round.
"""

from __future__ import annotations

import numpy as np

from ..gossip import plain
from .base import DecPhase2


class ConsensusTables(DecPhase2):
    name = "consensus"

    def __init__(self, steps=1, inflate=1.0):
        self.steps = int(steps)
        self.inflate = float(inflate)

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.xn = np.zeros((N, n_slots))
        self.xS = np.zeros((N, n_slots))
        self.ln = np.zeros((N, n_slots))
        self.lS = np.zeros((N, n_slots))

    def view(self, i):
        c = self.N / self.inflate
        return (c * self.xn[i] + self.own_n[i] - self.ln[i],
                c * self.xS[i] + self.own_S[i] - self.lS[i])

    def view_at(self, i, idx):
        c = self.N / self.inflate
        return (c * self.xn[i, idx] + self.own_n[i, idx] - self.ln[i, idx],
                c * self.xS[i, idx] + self.own_S[i, idx] - self.lS[i, idx])

    def end_round(self, t):
        self.xn = plain(self.g.P, self.xn + self.own_n - self.ln, self.steps)
        self.xS = plain(self.g.P, self.xS + self.own_S - self.lS, self.steps)
        self.ln = self.own_n.astype(float).copy()
        self.lS = self.own_S.copy()
        return self._state_cost((np.abs(self.xn) > 1e-12).sum(axis=1), self.steps), "sync"

    def shared_table(self):
        return self.own_n.sum(axis=0), self.own_S.sum(axis=0)
