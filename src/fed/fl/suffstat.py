"""Sufficient-statistics aggregation -- the exact baseline (not in the usual FL table,
because deep models have no finite sufficient statistic; a least-squares problem does).

Client sends: its (H_i, b_i) -- for Stein just b_i and n_i (H_i = n_i I); for
              bins only the (index, n_ij, S_ij) of bins touched since the last
              sync; for LS the upper triangle of X_iᵀX_i and X_iᵀy.
Server does:  w = (Σ H_i)⁻¹ Σ b_i -- the centralised estimator, in ONE round.

This is what `phase1/exact.py` and `phase2/periodic.py` already do; here it is
expressed in the common FL interface so it can be benchmarked alongside the rest.
"""

from __future__ import annotations

import numpy as np

from .base import FLMethod


class SuffStat(FLMethod):
    name = "suffstat"
    label = "Sufficient statistics (exact)"
    one_shot = True

    def round(self, prob, w):
        return prob.pooled(w)

    def round_cost(self, prob):
        act = prob.active
        if prob.isotropic:
            up = (prob.D + 1) * act.sum()
        elif prob.diag:
            up = 3 * prob.touched[act].sum()
        else:
            up = (prob.D * (prob.D + 1) // 2 + prob.D) * act.sum()
        return int(up + prob.D * act.sum())
