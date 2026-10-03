"""exact -- the headline lemma: Phase 1 federates EXACTLY.

Each agent uploads sum_t phi_tau(y_t S(x_t)) -- d numbers plus its count --
with tau set at the POOLED sample size.  Truncation is element-wise and applied
before averaging, so the server's average is bit-for-bit the centralised
truncated Stein estimator on all N n samples.
"""

from __future__ import annotations

from ...stein import normalize_l1
from .base import FLOAT_BITS, Phase1Strategy, local_V, truncated


class ExactStein(Phase1Strategy):
    name = "exact"

    def aggregate(self, agents, tau_fn):
        live = [ag for ag in agents if ag.n]
        n_pool = sum(ag.n for ag in live)
        tau = tau_fn(n_pool)
        total = sum(truncated(local_V(ag), tau).sum(axis=0) for ag in live)
        k = len(live) * (total.shape[0] + 1)
        return normalize_l1(total / n_pool), k, k * FLOAT_BITS
