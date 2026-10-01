"""Phase-1 strategy interface: how the agents pool their Stein estimates of theta_*.

Every strategy sees the same thing -- N agents, each holding n Phase-1 samples
(S(x_t), y_t) in `agent.S_buf`, `agent.y_buf` -- and returns ONE
l1-normalised direction for the whole network plus what the upload cost.

To try a new idea: copy `exact.py`, change `aggregate`, and register the class
in `phase1/__init__.py`.  Nothing else needs to change.
"""

from __future__ import annotations

import numpy as np

from ...stein import truncate

FLOAT_BITS = 32


def local_V(agent):
    """Untruncated Stein summands y_t S(x_t) of one agent, shape (n, d)."""
    return np.asarray(agent.S_buf) * np.asarray(agent.y_buf)[:, None]


def truncated(V, tau):
    return truncate(V, tau) if tau is not None else V


class Phase1Strategy:
    name = "base"

    def __init__(self, rng=None):
        self.rng = rng if rng is not None else np.random.default_rng(0)

    def aggregate(self, agents, tau_fn):
        """-> (theta_hat, upload_scalars, upload_bits).

        `tau_fn(n)` is the truncation threshold for a sample of size n (None if
        truncation is disabled).  Called at every adaptive-stopping checkpoint
        and once more at the freeze.
        """
        raise NotImplementedError
