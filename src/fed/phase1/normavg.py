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
    """(N, d) each agent's own estimate (tau at its own n); NaN rows for agents
    that have no samples yet."""
    d = next((len(ag.S_buf[0]) for ag in agents if ag.n), 0)
    out = np.full((len(agents), d), np.nan)
    for i, ag in enumerate(agents):
        if ag.n:
            out[i] = normalize_l1(truncated(local_V(ag), tau_fn(ag.n)).mean(axis=0))
    return out


class NormalizedAverage(Phase1Strategy):
    name = "normavg"

    def aggregate(self, agents, tau_fn):
        loc = local_estimates(agents, tau_fn)
        k = int(np.isfinite(loc).sum())
        return normalize_l1(np.nanmean(loc, axis=0)), k, k * FLOAT_BITS
