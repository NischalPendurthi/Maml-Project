"""fl -- run ANY method from src/fed/fl/ to share the Phase-2 bin table.

The Phase-2 "model" is the vector of bin means w ∈ R^{N_bins}; client i's data
are its pulls, giving the diagonal least-squares problem H_i = diag(n_ij),
b_i = (S_ij)_j whose pooled optimum is the exact network bin means.

At each sync (every `every` rounds, or event-triggered when `gamma` is set --
the rule of phase2/event.py) the FL method runs `rounds` communication rounds
on ALL pulls so far, warm-started from the current global model.

UCB also needs per-bin counts for its confidence widths, so every method also
uploads the (index, count) of bins whose counts changed -- except `suffstat`
and `split`, whose messages already contain them.

Agents act on (global count + own unsynced count, global mean·count + own
unsynced sum), exactly like phase2/periodic.py, which this reproduces when
method="suffstat".

    phase2="fl", phase2_kw=dict(method="feddyn", rounds=5, every=10)
"""

from __future__ import annotations

import numpy as np

from ..fl import make_fl
from ..fl.problem import FedQuadratic
from .base import Phase2Strategy

COUNT_FREE = ("suffstat", "split", "personalized")   # messages already carry counts


class FLShare(Phase2Strategy):
    name = "fl"

    def __init__(self, method="fedavg", method_kw=None, rounds=1, every=1, gamma=None):
        self.method = make_fl(method, **(method_kw or {}))
        self.rounds = int(rounds)
        self.every = int(every)
        self.gamma = gamma
        self.last_rounds = 1

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        self.G_n = np.zeros(n_slots, dtype=np.int64)
        self.w = np.zeros(n_slots)
        self.dn = np.zeros((N, n_slots), dtype=np.int64)
        self.dS = np.zeros((N, n_slots), dtype=float)

    def record(self, i, b, y):
        super().record(i, b, y)
        self.dn[i, b] += 1
        self.dS[i, b] += y

    def view(self, i):
        return self.G_n + self.dn[i], self.G_n * self.w + self.dS[i]

    def view_at(self, i, idx):
        g = self.G_n[idx]
        return g + self.dn[i, idx], g * self.w[idx] + self.dS[i, idx]

    def _due(self, t):
        if self.gamma is not None:
            return bool(np.any(self.dn > self.gamma * np.maximum(self.G_n, 1)[None, :]))
        return t % self.every == 0

    def problem(self):
        n = self.own_n.sum(axis=1).astype(float)
        return FedQuadratic(self.own_n.astype(float), self.own_S, n, diag=True,
                            touched=self.dn > 0, new_samples=self.dn.sum(axis=1),
                            sample_cost=2)

    def end_round(self, t):
        if not self._due(t) or not self.dn.any():
            return 0, None
        prob = self.problem()
        w, scalars, rounds = self.method.solve(prob, self.w, self.rounds)
        if self.method.name not in COUNT_FREE:
            scalars += 2 * int((self.dn > 0).sum())            # (bin, count) deltas
        self.G_n = self.own_n.sum(axis=0)
        self.w = np.where(self.G_n > 0, w, 0.0)
        self.dn[:] = 0
        self.dS[:] = 0.0
        self.last_rounds = rounds
        return scalars, "sync"

    def shared_table(self):
        return self.G_n, self.G_n * self.w

    def pending(self):
        return self.dn
