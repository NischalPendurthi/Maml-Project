"""Decentralised OPTIMISATION on the Stein least-squares problem (burst).

The decentralised counterparts of FedSGD / FedAvg / SCAFFOLD in src/fed/fl/.
Each agent's loss, in sum form scaled by a common constant so curvature is O(1):
    F_i(w) = (½ n_i ‖w‖² − b_iᵀ w) / n̄,      Σ_i F_i minimised at Σ b / Σ n.

  dgd    decentralised gradient descent (Nedić & Ozdaglar 2009):
         w ← P w − η ∇F(w).  With a constant step the fixed point is NOT the
         consensus optimum: a bias of order η / gap.
  gt     gradient tracking / DIGing (Nedić, Olshevsky & Shi 2017): each agent
         also tracks the network-average gradient, y ← P y + ∇F(w⁺) − ∇F(w);
         exact with a constant step.  Two vectors per arc.
  dlocal decentralised FedAvg: `local_steps` local GD steps, then one gossip
         average of the models (Lian et al. 2017 with local updates).

All keep their iterates across checkpoints (warm start); `k` iterations each.
"""

from __future__ import annotations

import numpy as np

from ..gossip import mix
from .base import DecPhase1, vec_cost


class _Opt(DecPhase1):
    def __init__(self, k=10, lr=0.5):
        self.k, self.lr = int(k), float(lr)

    def setup(self, N, d, graph):
        super().setup(N, d, graph)
        self.w = np.zeros((N, d))

    @staticmethod
    def _grad(W, own_b, own_n, nbar):
        return (own_n[:, None] * W - own_b) / nbar


class DGD(_Opt):
    name = "dgd"

    def estimate(self, t, own_b, own_n):
        nbar = max(own_n.mean(), 1.0)
        for _ in range(self.k):
            self.w = mix(self.g.P, self.w) - self.lr * self._grad(self.w, own_b, own_n, nbar)
        return self.w.copy(), vec_cost(self.g, self.d - 1, self.k), self.k


class GradientTracking(_Opt):
    name = "gt"

    def setup(self, N, d, graph):
        super().setup(N, d, graph)
        self.y = None
        self.g_old = None

    def estimate(self, t, own_b, own_n):
        nbar = max(own_n.mean(), 1.0)
        g = self._grad(self.w, own_b, own_n, nbar)
        if self.y is None:
            self.y = g.copy()
        else:                                   # data changed since last call
            self.y = self.y + g - self.g_old
        for _ in range(self.k):
            w_new = mix(self.g.P, self.w) - self.lr * self.y
            g_new = self._grad(w_new, own_b, own_n, nbar)
            self.y = mix(self.g.P, self.y) + g_new - g
            self.w, g = w_new, g_new
        self.g_old = g
        return self.w.copy(), 2 * vec_cost(self.g, self.d - 1, self.k), self.k


class DecLocal(_Opt):
    name = "dlocal"

    def __init__(self, k=10, lr=0.5, local_steps=5):
        super().__init__(k, lr)
        self.local_steps = int(local_steps)

    def estimate(self, t, own_b, own_n):
        nbar = max(own_n.mean(), 1.0)
        for _ in range(self.k):
            W = self.w
            for _ in range(self.local_steps):
                W = W - self.lr * self._grad(W, own_b, own_n, nbar)
            self.w = mix(self.g.P, W)
        return self.w.copy(), vec_cost(self.g, self.d - 1, self.k), self.k
