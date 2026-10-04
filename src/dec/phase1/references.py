"""Reference points: no communication, and an (oracle) server."""

from __future__ import annotations

import numpy as np

from .base import DecPhase1


class Local(DecPhase1):
    """Each agent uses only its own samples: the no-communication floor."""
    name = "local"

    def estimate(self, t, own_b, own_n):
        return own_b.copy(), 0, 0


class Server(DecPhase1):
    """Exact pooling through a server (the federated version): the ceiling."""
    name = "server"

    def estimate(self, t, own_b, own_n):
        total = own_b.sum(axis=0)
        live = int((own_n > 0).sum())
        return np.tile(total, (self.N, 1)), live * (self.d + 1) + self.N * self.d, 1
