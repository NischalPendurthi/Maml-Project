"""One-shot FedAvg (local training to convergence, one round).

Client sends: its locally optimal model w_i = argmin F_i (plus n_i).
Server does:  sample-weighted average Σ p_i w_i.

Exact when all clients share the same per-sample Hessian (Phase-1 Stein:
w_i = b_i / n_i, so Σ p_i w_i = Σ b_i / Σ n_i).  Biased otherwise: on bins the
weight of client i in bin j is its TOTAL sample share p_i, not its share of
bin j -- the "objective inconsistency" of model averaging.  Coordinates a
client has no data on are left at the current global value.
"""

from __future__ import annotations

from .base import FLMethod


class OneShotAvg(FLMethod):
    name = "oneshot"
    label = "One-shot FedAvg (local opt., weighted avg.)"
    one_shot = True
    up_extra = 1

    def round(self, prob, w):
        return self._avg(prob, prob.local_opt(w))
