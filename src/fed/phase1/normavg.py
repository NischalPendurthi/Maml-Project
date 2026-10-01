"""normavg -- FedAvg of finished local estimates.

Each agent computes its OWN estimate (tau at its local size, l1-normalised)
and the server averages and renormalises.  This is the "obvious" federated
recipe; normalising before averaging (and the smaller local tau) is exactly
what makes it differ from the pooled estimator.
"""

from __future__ import annotations

import numpy as np

from ...stein import normalize_l1
from .base import FLOAT_BITS, Phase1Strategy, local_V, truncated


def local_estimates(agents, tau_fn):
    tau = tau_fn(len(agents[0].y_buf))
    return np.array([normalize_l1(truncated(local_V(ag), tau).mean(axis=0)) for ag in agents])


class NormalizedAverage(Phase1Strategy):
    name = "normavg"

    def aggregate(self, agents, tau_fn):
        loc = local_estimates(agents, tau_fn)
        return normalize_l1(loc.mean(axis=0)), loc.size, loc.size * FLOAT_BITS
