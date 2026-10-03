"""FedAvgM (Hsu et al. 2019): FedAvg with server momentum.

Client sends: model update after local training (as FedAvg).
Server does:  treats the averaged update Δ = Σ p_i w_i − w as a pseudo-gradient,
              v ← β v + Δ,  w ← w + server_lr · v.

Momentum helps when rounds are noisy or ill-conditioned; when a round already
lands near the optimum it overshoots.
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod, local_gd


class FedAvgM(FLMethod):
    name = "fedavgm"
    label = "FedAvgM (server momentum)"

    def __init__(self, local_steps=5, lr_scale=1.0, server_lr=1.0, beta=0.9):
        super().__init__(local_steps, lr_scale)
        self.server_lr, self.beta = float(server_lr), float(beta)

    def reset(self, N, D):
        self.v = np.zeros(D)

    def round(self, prob, w):
        W = local_gd(prob, w, self.local_steps, self._lr(prob))
        delta = self._avg(prob, W) - w
        self.v = self.beta * self.v + delta
        return w + self.server_lr * self.v
