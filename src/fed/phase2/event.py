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

    def end_round(self, t):
        if np.any(self.dn > self.gamma * np.maximum(self.G_n, 1)[None, :]):
            return self.sync(), "sync"
        return 0, None
