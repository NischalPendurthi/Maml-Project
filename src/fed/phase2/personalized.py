"""personalized -- server sync of sufficient statistics, but each agent acts on
a PERSONAL table that weights everybody else's pulls by lam:

    n_view = own_n + lam · (others' synced n),   S_view likewise.

lam = 1 is `periodic` (fully shared), lam = 0 is `none` (fully local).  This is
the Phase-2 form of src/fed/fl/personalized.py and only pays off when agents'
reward functions on the index line genuinely differ (concept shift).
"""

from __future__ import annotations

from .base import ServerSync


class PersonalizedSync(ServerSync):
    name = "personalized"

    def __init__(self, lam=0.5, every=1):
        self.lam = float(lam)
        self.every = int(every)

    def view(self, i):
        others_n = self.G_n - (self.own_n[i] - self.dn[i])
        others_S = self.G_S - (self.own_S[i] - self.dS[i])
        return self.own_n[i] + self.lam * others_n, self.own_S[i] + self.lam * others_S

    def view_at(self, i, idx):
        n, S = self.view(i)          # ServerSync's fast path would skip the weighting
        return n[idx], S[idx]

    def end_round(self, t):
        if t % self.every == 0:
            return self.sync(), "sync"
        return 0, None
