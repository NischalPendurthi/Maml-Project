"""FedNova (Wang et al. 2020).

Client sends: its NORMALISED update d_i = (w − w_i) / τ_i, where τ_i is the
              number of local steps it ran, plus τ_i.
Server does:  w ← w − τ_eff Σ p_i d_i with τ_eff = Σ p_i τ_i.

FedNova fixes the objective inconsistency that appears when clients run
different numbers of local steps (here: steps ∝ local data, as with a fixed
number of local epochs).  With equal steps it is exactly FedAvg; it does NOT
remove drift caused by heterogeneous Hessians.
"""

from __future__ import annotations

from .base import FLMethod, local_gd
from .fedavg import client_steps


class FedNova(FLMethod):
    name = "fednova"
    label = "FedNova (normalised updates)"
    up_extra = 1

    def __init__(self, local_steps=5, lr_scale=1.0, step_rule="proportional"):
        super().__init__(local_steps, lr_scale)
        self.step_rule = step_rule

    def round(self, prob, w):
        tau = client_steps(prob, self.local_steps, self.step_rule).astype(float)
        W = local_gd(prob, w, tau.astype(int), self._lr(prob))
        d = (w - W) / tau[:, None]
        tau_eff = float((prob.p * tau).sum())
        return w - tau_eff * self._avg(prob, d)
