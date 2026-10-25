"""epoch -- synchronised epochs: the Phase-2 protocol analysed in docs/proofs/serverless.tex.

Slot boundaries every L = 2Λ rounds (Λ = delivery time, the diameter on a static
graph).  At a boundary β_m agent l raises an alarm if, in some bin j,

    O_lj(β_m) − O_lj(ε_m) > γ · max(G_j(ε_m), 1),     ε_m = last epoch ≤ β_{m−1},

and β_m becomes an epoch if anyone alarms.  Every agent then floods a snapshot of
the bins it pulled since ε_m.  In slot m+1 every agent acts on the SAME epoch table
G(e), e = last epoch ≤ β_{m−1}, plus its own pulls since e (Lemma 12: a common
prefix plus one own block).  Lemma 8 shows that flooding delivers everything in
time, so the simulation applies the schedule directly instead of routing messages.

  pipeline=True   (not covered by the proofs yet) check alarms every round and act on
                  the last epoch whose snapshots are complete (2Λ − 1 steps after it),
                  instead of waiting for slot boundaries: staleness ≈ 2Λ instead of ≤ 4Λ.

Cost, with the accounting of flood.py (per delivery to each of the other N−1
agents): 1 scalar per alarm, 3 per changed bin + 1 label per snapshot.
`arc_scalars` keeps the flooding count of Theorem 23 (every message over every arc).
"""

from __future__ import annotations

import numpy as np

from .base import PER_BIN, DecPhase2


class EpochTables(DecPhase2):
    name = "epoch"

    def __init__(self, gamma=0.5, lam=None, pipeline=False):
        self.gamma = float(gamma)
        self.lam = lam
        self.pipeline = pipeline

    def setup(self, N, n_slots):
        super().setup(N, n_slots)
        lam = self.lam or self.g.diameter
        if not np.isfinite(lam):
            raise ValueError("epoch protocol needs a finite delivery time Λ")
        self.Lam = int(lam)
        self.L = 1 if self.pipeline else 2 * self.Lam
        self.beta0 = None
        zero_n, zero_S = np.zeros_like(self.own_n), np.zeros_like(self.own_S)
        self.epochs = [(-np.inf, zero_n, zero_S)]  # (round after β_0, O(e), O^S(e)); β_0 ∈ E
        self._set_ref(0)
        self.alarms = 0
        self.arc_scalars = 0

    def _set_ref(self, k):
        """Act on epoch k: base_i = G(e) − O_i(e), so the view is base_i + own_i."""
        _, On, OS = self.epochs[k]
        self.ref = k
        self.base_n = On.sum(axis=0)[None, :] - On
        self.base_S = OS.sum(axis=0)[None, :] - OS

    def view(self, i):
        return self.base_n[i] + self.own_n[i], self.base_S[i] + self.own_S[i]

    def view_at(self, i, idx):
        return self.base_n[i, idx] + self.own_n[i, idx], self.base_S[i, idx] + self.own_S[i, idx]

    def _last(self, upto):
        return max(k for k, (r, _, _) in enumerate(self.epochs) if r <= upto)

    def end_round(self, t):
        if self.beta0 is None:
            self.beta0 = t - 1                   # last round before Phase 2
        s = t - self.beta0
        if s % self.L:
            return 0, None
        if self.pipeline:
            # alarm membership arrives within Λ, snapshots within 2Λ
            On = self.epochs[self._last(s - self.Lam)][1]
            Gref = self.epochs[self._last(s - 2 * self.Lam)][1].sum(axis=0)
        else:
            On = self.epochs[-1][1]              # ε_m: every epoch so far is ≤ β_{m−1}
            Gref = On.sum(axis=0)
        delta = self.own_n - On
        alarm = (delta > self.gamma * np.maximum(Gref, 1)).any(axis=1)
        cost = 0
        if alarm.any():
            changed = (self.own_n - self.epochs[-1][1] != 0).sum(axis=1)
            self.epochs.append((s, self.own_n.copy(), self.own_S.copy()))
            msgs = 1 + int((PER_BIN * changed + 1).sum())   # one alarm + N snapshots
            cost = (self.N - 1) * msgs
            self.arc_scalars += int(self.g.A.sum()) * msgs
            self.alarms += 1
        # the next rounds act on the last epoch that every agent holds in full
        k = self._last(s + 1 - 2 * self.Lam) if self.pipeline else self._last(s - self.L)
        if k != self.ref:
            self._set_ref(k)
        return cost, ("sync" if alarm.any() else None)

    def shared_table(self):
        _, On, OS = self.epochs[self.ref]
        return On.sum(axis=0), OS.sum(axis=0)

    def pending(self):
        return self.own_n - self.epochs[self.ref][1]
