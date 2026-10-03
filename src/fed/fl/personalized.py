"""Personalised FL: one global model plus a personal model per client.

Client sends: its sufficient statistics (as `suffstat`).
Server does:  the global pooled model.  Each client then forms its OWN model
              by partial pooling -- its own data at full weight, everybody
              else's at weight lam:

                v_i = (H_i + lam Σ_{k≠i} H_k)⁻¹ (b_i + lam Σ_{k≠i} b_k)

lam = 1 is the global model, lam = 0 a purely local one.  This is the
count-space form of Ditto / hierarchical shrinkage; it needs no extra messages,
because Σ_{k≠i} = (global) − (own) is computable locally.

Relevance: only pays off when agents genuinely differ (concept shift: each
agent has its own θ*_i).  With a shared θ* it can only add variance.
`round` returns the GLOBAL model; `personal` returns the per-client ones.
"""

from __future__ import annotations

import numpy as np

from .suffstat import SuffStat


class Personalized(SuffStat):
    name = "personalized"
    label = "Personalised FL (partial pooling)"

    def __init__(self, local_steps=5, lr_scale=1.0, lam=0.5):
        super().__init__(local_steps, lr_scale)
        self.lam = float(lam)
        self.label = f"Personalised FL (λ={self.lam:g})"

    def personal(self, prob, fallback):
        Hs, bs = prob.H.sum(0), prob.b.sum(0)
        H = prob.H + self.lam * (Hs[None] - prob.H)
        b = prob.b + self.lam * (bs[None] - prob.b)
        fb = np.broadcast_to(fallback, (prob.N, prob.D))
        if prob.diag:
            return np.where(H > 0, b / np.where(H > 0, H, 1.0), fb)
        I = 1e-12 * np.eye(prob.D)
        return np.array([np.linalg.solve(Hi + I, bi) for Hi, bi in zip(H, b)])
