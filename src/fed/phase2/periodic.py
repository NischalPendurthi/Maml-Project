"""periodic -- server sync every `every` rounds.

Agents act on (global table as of the last sync) + (their own unsynced pulls).
every=1 is the centralised limit; large `every` approaches independent agents.
"""

from __future__ import annotations

from .base import ServerSync


class PeriodicSync(ServerSync):
    name = "periodic"

    def __init__(self, every=1):
        self.every = int(every)

    def end_round(self, t):
        if t % self.every == 0:
            return self.sync(), "sync"
        return 0, None
