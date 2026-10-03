"""FedProx (Li et al. 2020).

Client sends: its model after local GD on F_i(w) + mu/2 ‖w − w_global‖².
Server does:  sample-weighted average.

The proximal term limits how far a client drifts toward its own optimum during
local training.  It shrinks client drift but does not remove the fixed-point
bias; it also slows every client down.  mu is relative: mu = mu_rel · L_max.
"""

from __future__ import annotations

from .base import FLMethod, local_gd


class FedProx(FLMethod):
    name = "fedprox"
    label = "FedProx"

    def __init__(self, local_steps=5, lr_scale=1.0, mu_rel=0.1):
        super().__init__(local_steps, lr_scale)
        self.mu_rel = float(mu_rel)

    def round(self, prob, w):
        mu = self.mu_rel * prob.L_max()
        W = local_gd(prob, w, self.local_steps, self._lr(prob, mu),
                     extra=lambda V: mu * (V - w))
        return self._avg(prob, W)
