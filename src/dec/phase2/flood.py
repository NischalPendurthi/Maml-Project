"""flood -- relay every agent's own table, exact with delay (interleaved).

Agent i keeps the freshest copy it has heard of every agent k's OWN table and
acts on their sum (plus its own newest pulls).  Agent k's pulls reach agent i
after dist(i, k) rounds: an exact pooled table, stale by at most the diameter.
This is the decentralised counterpart of server sync, and the version whose
staleness is easiest to bound (≤ diameter rounds ⇒ ≤ N · diameter missing pulls).

  every   an agent re-publishes its own table every `every` rounds
  gamma   ...or event-triggered: when its unpublished pulls in some bin exceed
          gamma × the count it currently sees there (the rule of fed/phase2/event)

Cost: each record update delivered to an agent costs 3 scalars per bin that
changed since the receiver's previous copy (delta encoding) + 1 for the version.
"""

from __future__ import annotations

import numpy as np

from ..gossip import relay
from .base import PER_BIN, DecPhase2


class FloodTables(DecPhase2):
    name = "flood"

    def __init__(self, every=1, gamma=None):
        self.every = int(every)
        self.gamma = gamma

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.kn = np.zeros((N, N, n_slots))
        self.kS = np.zeros((N, N, n_slots))
        self.kv = np.full((N, N), -1)
        self.Vn = np.zeros((N, n_slots))
        self.VS = np.zeros((N, n_slots))

    def view(self, i):
        return (self.Vn[i] + self.own_n[i] - self.kn[i, i],
                self.VS[i] + self.own_S[i] - self.kS[i, i])

    def view_at(self, i, idx):
        return (self.Vn[i, idx] + self.own_n[i, idx] - self.kn[i, i, idx],
                self.VS[i, idx] + self.own_S[i, idx] - self.kS[i, i, idx])

    def end_round(self, t):
        N = self.N
        idx = np.arange(N)
        unpub = self.own_n - self.kn[idx, idx]
        if self.gamma is not None:
            pub = (unpub > self.gamma * np.maximum(self.Vn, 1)).any(axis=1)
        else:
            pub = np.full(N, t % self.every == 0) & unpub.any(axis=1)
        self.kn[idx[pub], idx[pub]] = self.own_n[pub]
        self.kS[idx[pub], idx[pub]] = self.own_S[pub]
        self.kv[idx[pub], idx[pub]] = t
        new_v, src, _ = relay(self.kv, self.g.A)
        upd = new_v > self.kv
        if not upd.any() and not pub.any():
            return 0, None
        old_n = self.kn
        self.kn = self.kn[src, idx[None, :]]
        self.kS = self.kS[src, idx[None, :]]
        self.kv = new_v
        changed = (self.kn != old_n).sum(axis=2)
        cost = int((PER_BIN * changed + 1)[upd].sum())
        self.Vn = self.kn.sum(axis=1)
        self.VS = self.kS.sum(axis=1)
        return cost, "sync" if upd.any() else None

    def shared_table(self):
        return self.own_n.sum(axis=0), self.own_S.sum(axis=0)

    def pending(self):
        """Pulls of agent i that some agent has not yet heard of."""
        return self.own_n - self.kn.min(axis=0)
