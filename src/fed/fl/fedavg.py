"""FedAvg (McMahan et al. 2017).

Client sends: its model after `local_steps` GD steps from the global model.
Server does:  sample-weighted average.

`step_rule="proportional"` gives each client local steps ∝ its sample count
(clients that hold more data do more work per round, as with a fixed number of
local EPOCHS).  That is the setting FedNova was built for: plain averaging then
converges to a different, inconsistent objective.

With one local step FedAvg ≡ FedSGD; with many it drifts toward each client's
own optimum, and on heterogeneous problems (bins, LS under covariate shift) the
fixed point is NOT the pooled estimator.
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod, local_gd


def client_steps(prob, E, rule):
    if rule == "fixed":
        return np.full(prob.N, E)
    n_act = prob.n[prob.active]
    mean = n_act.mean() if n_act.size else 1.0
    return np.maximum(1, np.round(E * prob.n / mean)).astype(int)


class FedAvg(FLMethod):
    name = "fedavg"
    label = "FedAvg"

    def __init__(self, local_steps=5, lr_scale=1.0, step_rule="fixed"):
        super().__init__(local_steps, lr_scale)
        self.step_rule = step_rule
        if step_rule != "fixed":
            self.label = "FedAvg (local steps ∝ data)"

    def round(self, prob, w):
        steps = client_steps(prob, self.local_steps, self.step_rule)
        W = local_gd(prob, w, steps, self._lr(prob))
        return self._avg(prob, W)
