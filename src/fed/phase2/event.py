"""event -- server sync TRIGGERED by how much an agent has learned locally.

When some agent's unsynced pulls in a bin exceed `gamma` times the global
count there (its local news would move the shared estimate a lot), the server
polls everyone.  The DisLinUCB-style rule: early on it syncs almost every
round, later rarely, so communication grows only logarithmically.
"""

from __future__ import annotations

import numpy as np

from .base import ServerSync


class EventTriggered(ServerSync):
    name = "event"

    def __init__(self, gamma=1.0):
        self.gamma = float(gamma)

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        # trigger_counts[j]: syncs at which bin j met the trigger (for the
        # "at most 1 + log_{1+gamma}(NT) syncs per bin" check, exp22)
        self.trigger_counts = np.zeros(n_slots, dtype=np.int64)

    def end_round(self, t):
        hot = (self.dn > self.gamma * np.maximum(self.G_n, 1)[None, :]).any(axis=0)
        if hot.any():
            self.trigger_counts += hot
            return self.sync(), "sync"
        return 0, None
