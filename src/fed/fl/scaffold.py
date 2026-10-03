"""SCAFFOLD (Karimireddy et al. 2020), option II control variates.

Client sends: model update Δw_i and control-variate update Δc_i (2 vectors).
Server does:  w ← w + Σ p_i Δw_i,  c ← Σ p_i c_i, broadcasts (w, c).

Each local step uses ∇F_i(w) − c_i + c, i.e. corrects the client's gradient by
the estimated difference between its gradient and the global one.  At the
fixed point c_i = ∇F_i and c = ∇F, so local steps follow the GLOBAL gradient:
client drift is removed and the fixed point is the pooled estimator, even on
heterogeneous problems.  Costs twice the communication of FedAvg.
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod, local_gd


class Scaffold(FLMethod):
    name = "scaffold"
    label = "SCAFFOLD (control variates)"
    up_vectors = 2
    down_vectors = 2

    def reset(self, N, D):
        self.c = np.zeros(D)
        self.ci = np.zeros((N, D))

    def round(self, prob, w):
        lr = self._lr(prob)
        E = self.local_steps
        W = local_gd(prob, w, E, lr, extra=lambda V: self.c[None, :] - self.ci)
        act = prob.active
        ci_new = self.ci.copy()
        ci_new[act] = self.ci[act] - self.c + (w - W[act]) / (E * lr)
        self.ci = ci_new
        # Full participation: the server control variate is the weighted mean of
        # the clients'.  Recomputing it (rather than adding Σ p_i Δc_i) keeps
        # c = Σ p_i c_i exact when the weights p_i drift between calls -- which
        # they do in a bandit, where agents accumulate data at different rates.
        self.c = self._avg(prob, self.ci)
        return w + self._avg(prob, W - w)
