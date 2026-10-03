"""FedDyn (Acar et al. 2021), dynamic regularisation.

Client sends: its model after local training on
                 F̃_i(w) − ⟨g_i, w⟩ + α/2 ‖w − w_global‖²
              where g_i is a per-client linear correction it updates itself.
Server does:  h ← h − α/N Σ (w_i − w),  w ← mean(w_i) − h/α.

The linear term makes every client's local optimum consistent with the global
stationary point, so -- like SCAFFOLD -- FedDyn converges to the pooled
estimator despite heterogeneity, but with ONE vector per round.

FedDyn is defined for an unweighted sum of client losses, so client losses are
rescaled to F̃_i = N p_i F_i (whose plain average is the weighted objective).
α is relative: α = alpha_rel · max_i N p_i L_i.

Caveat measured in exp11: the per-client terms g_i assume each client's loss is
FIXED.  In a bandit the losses grow every round, and under uneven participation
the weights p_i drift too, so the stored g_i go stale and the shared table
drifts away from the pooled one.  SCAFFOLD has the same exposure through its
control variates.
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod, local_gd


class FedDyn(FLMethod):
    name = "feddyn"
    label = "FedDyn (dynamic regularisation)"

    def __init__(self, local_steps=5, lr_scale=1.0, alpha_rel=0.1):
        super().__init__(local_steps, lr_scale)
        self.alpha_rel = float(alpha_rel)

    def reset(self, N, D):
        self.g = np.zeros((N, D))
        self.h = np.zeros(D)

    def round(self, prob, w):
        act = prob.active
        n_act = max(int(act.sum()), 1)
        scale = n_act * prob.p                                   # F̃_i = scale_i F_i
        L = float((scale * prob.smoothness()).max()) or 1.0
        alpha = self.alpha_rel * L
        lr = self.lr_scale / (L + alpha)
        # local gradient = scale_i ∇F_i(V) − g_i + α (V − w); local_gd adds ∇F_i itself
        extra = lambda V: ((scale[:, None] - 1.0) * prob.grad(V)          # noqa: E731
                           - self.g + alpha * (V - w))
        W = local_gd(prob, w, self.local_steps, lr, extra=extra)
        self.g[act] = self.g[act] - alpha * (W[act] - w)
        self.h = self.h - alpha / n_act * (W[act] - w).sum(axis=0)
        return W[act].mean(axis=0) - self.h / alpha
