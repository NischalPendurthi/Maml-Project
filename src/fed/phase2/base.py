"""Phase-2 strategy interface: how agents share the per-bin UCB statistics.

Once theta_hat_0 is frozen every agent has the same bin grid, and the whole
UCB state is (n_j, S_j) per bin.  A strategy owns that state for the network
and answers one question per agent per round -- "what table does agent i act
on?" -- and decides when to communicate and what it costs.

To try a new idea: copy `periodic.py`, change `view` / `end_round`, and
register the class in `phase2/__init__.py`.

Messages are sparse: each touched bin costs PER_BIN = 3 scalars (index, count, sum).
"""

from __future__ import annotations

import numpy as np

PER_BIN = 3


class Phase2Strategy:
    name = "base"

    def setup(self, N, n_slots):
        self.N = N
        self.own_n = np.zeros((N, n_slots), dtype=np.int64)   # each agent's own pulls
        self.own_S = np.zeros((N, n_slots), dtype=float)

    def record(self, i, b, y):
        self.own_n[i, b] += 1
        self.own_S[i, b] += y

    def view(self, i):
        """(n_j, S_j) arrays agent i acts on."""
        raise NotImplementedError

    def view_at(self, i, idx):
        """`view(i)` restricted to bins `idx` -- the per-round hot path."""
        n, S = self.view(i)
        return n[idx], S[idx]

    def end_round(self, t):
        """Communicate if it is time.  -> (scalars sent, event label or None)."""
        return 0, None

    # -- for the visualisation ------------------------------------------
    def shared_table(self):
        """The network-wide table as far as it has actually been communicated."""
        return self.own_n.sum(axis=0), self.own_S.sum(axis=0)

    def pending(self):
        """(N, n_slots) pulls each agent holds that the others have not seen."""
        return np.zeros_like(self.own_n)


class ServerSync(Phase2Strategy):
    """Star topology: a server keeps the global table, agents keep deltas."""

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.G_n = np.zeros(n_slots, dtype=np.int64)
        self.G_S = np.zeros(n_slots, dtype=float)
        self.dn = np.zeros((N, n_slots), dtype=np.int64)
        self.dS = np.zeros((N, n_slots), dtype=float)

    def record(self, i, b, y):
        super().record(i, b, y)
        self.dn[i, b] += 1
        self.dS[i, b] += y

    def view(self, i):
        return self.G_n + self.dn[i], self.G_S + self.dS[i]

    def view_at(self, i, idx):
        return self.G_n[idx] + self.dn[i, idx], self.G_S[idx] + self.dS[i, idx]

    def sync(self):
        """Everyone uploads unsynced bins; server merges and broadcasts touched bins."""
        nz = self.dn > 0
        up = PER_BIN * int(nz.sum())
        down = PER_BIN * int(nz.any(axis=0).sum()) * self.N
        self.G_n += self.dn.sum(axis=0)
        self.G_S += self.dS.sum(axis=0)
        self.dn[:] = 0
        self.dS[:] = 0.0
        return up + down

    def shared_table(self):
        return self.G_n, self.G_S

    def pending(self):
        return self.dn
