"""Federated distillation (Jeong et al. 2018; Lin et al. 2020).

Client sends: predictions ("soft labels") of its locally trained model on a
              shared unlabelled public set, instead of parameters.
Server does:  averages the predictions and fits the global model to them.

The public set is free here: the context density p is KNOWN (the same
assumption Stein needs), so the server can sample unlabelled contexts.
  * full problems (Phase 1): m = public_mult · D public points u ~ N(0, I);
    clients send u·w_i, the server least-squares-fits w.  Because the model is
    linear, m ≥ D predictions determine w_i exactly -- distillation collapses
    to one-shot FedAvg at a cost of m instead of D numbers.
  * bin problems (Phase 2): the public inputs are the bins themselves; a client
    ABSTAINS on bins it has no data for, and each bin's prediction is averaged
    over the clients that did predict it (confidence-masked averaging).
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod


class FedDistill(FLMethod):
    name = "distill"
    label = "Federated distillation (public-set predictions)"
    one_shot = True

    def __init__(self, local_steps=5, lr_scale=1.0, public_mult=2, seed=0):
        super().__init__(local_steps, lr_scale)
        self.public_mult = int(public_mult)
        self.seed = seed

    def reset(self, N, D):
        self.U = np.random.default_rng(self.seed).standard_normal((self.public_mult * D, D))

    def round(self, prob, w):
        Wloc = prob.local_opt(w)
        if prob.diag:
            mask = prob.support() & prob.active[:, None]
            wts = prob.p[:, None] * mask
            den = wts.sum(axis=0)
            return np.where(den > 0, (wts * Wloc).sum(axis=0) / np.where(den > 0, den, 1), w)
        target = self._avg(prob, Wloc @ self.U.T)                  # averaged soft labels
        return np.linalg.lstsq(self.U, target, rcond=None)[0]

    def round_cost(self, prob):
        act = prob.active
        if prob.diag:
            up = 2 * prob.support()[act].sum()
        else:
            up = self.public_mult * prob.D * act.sum()
        return int(up + prob.D * act.sum())
