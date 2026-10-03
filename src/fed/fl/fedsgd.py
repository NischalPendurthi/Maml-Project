"""FedSGD (McMahan et al. 2017) -- also the "gradient-based FL" row of the table.

Client sends: its full-batch gradient ∇F_i(w) at the global model.
Server does:  weighted average of gradients, one step w ← w − η Σ p_i ∇F_i(w)
              with η = lr_scale / L(global per-sample Hessian).

On a quadratic this is plain gradient descent on the global objective: never
biased, but the number of rounds grows with the condition number of Σ p_i A_i.
For Phase-1 Stein (A = I) one round with η = 1 lands exactly on the pooled
estimator; on bins, rarely visited bins converge slowly.
"""

from __future__ import annotations

from .base import FLMethod


class FedSGD(FLMethod):
    name = "fedsgd"
    label = "FedSGD (gradients, server GD step)"

    def round(self, prob, w):
        g = self._avg(prob, prob.grad(w))
        return w - self.lr_scale / prob.global_smoothness() * g


class GradientFL(FedSGD):
    """The table's "gradient-based FL" row.  Clients send gradients and the
    server aggregates them: on a least-squares problem with full-batch
    gradients this is exactly FedSGD, so it is registered as an alias rather
    than duplicated."""
    name = "gradient"
    label = "Gradient-based FL (≡ FedSGD)"
