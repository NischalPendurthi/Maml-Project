"""FedAdam (Reddi et al. 2021, "Adaptive Federated Optimization").

Client sends: model update after local training (as FedAvg).
Server does:  Adam on the pseudo-gradient Δ = Σ p_i w_i − w:
              m ← β1 m + (1−β1) Δ,  v ← β2 v + (1−β2) Δ²,
              w ← w + server_lr · m / (√v + τ).

Per-coordinate step sizes can compensate for coordinates that move slowly --
on bins those are the rarely visited ones -- at the cost of a scale-dependent
server_lr that must be tuned (experiments/exp10 part A does that).
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod, local_gd


class FedAdam(FLMethod):
    name = "fedadam"
    label = "FedAdam (server Adam)"

    def __init__(self, local_steps=5, lr_scale=1.0, server_lr=0.1, beta1=0.9,
                 beta2=0.99, tau=1e-3):
        super().__init__(local_steps, lr_scale)
        self.server_lr, self.beta1, self.beta2, self.tau = server_lr, beta1, beta2, tau

    def reset(self, N, D):
        self.m = np.zeros(D)
        self.v = np.full(D, self.tau ** 2)

    def _second_moment(self, delta):
        return self.beta2 * self.v + (1 - self.beta2) * delta ** 2

    def round(self, prob, w):
        W = local_gd(prob, w, self.local_steps, self._lr(prob))
        delta = self._avg(prob, W) - w
        self.m = self.beta1 * self.m + (1 - self.beta1) * delta
        self.v = self._second_moment(delta)
        return w + self.server_lr * self.m / (np.sqrt(self.v) + self.tau)
