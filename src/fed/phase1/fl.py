"""fl -- run ANY method from src/fed/fl/ as the Phase-1 pooling step.

At every adaptive-stopping checkpoint the agents' Phase-1 data are cast as a
`FedQuadratic` (objective "stein" or "ls", see objectives.py) and the chosen FL
method runs `rounds` communication rounds, warm-started from the previous
checkpoint's global model.  The result is l1-normalised into theta_hat.

The truncation threshold uses the POOLED sample size for every method, so the
only thing that varies between methods is how they aggregate.

    phase1="fl", phase1_kw=dict(method="scaffold", rounds=10, objective="ls")
"""

from __future__ import annotations

import numpy as np

from ...stein import normalize_l1
from ..fl import make_fl
from .base import FLOAT_BITS, Phase1Strategy
from .objectives import ls_problem, stein_problem


class FLPool(Phase1Strategy):
    name = "fl"

    def __init__(self, rng=None, method="fedavg", method_kw=None, rounds=10,
                 objective="stein", ridge=1e-3):
        super().__init__(rng)
        self.method = make_fl(method, **(method_kw or {}))
        self.rounds = int(rounds)
        self.objective = objective
        self.ridge = ridge
        self._w = None
        self._n_sent = None
        self.last_rounds = 1

    def problem(self, agents, tau_fn):
        n_pool = sum(ag.n for ag in agents)
        if self.objective == "stein":
            return stein_problem(agents, tau_fn(n_pool), self._n_sent)
        if self.objective == "ls":
            return ls_problem(agents, self.ridge, self._n_sent)
        raise ValueError(f"unknown objective {self.objective!r}")

    def aggregate(self, agents, tau_fn):
        prob = self.problem(agents, tau_fn)
        w0 = self._w if self._w is not None else np.zeros(prob.D)
        w, scalars, rounds = self.method.solve(prob, w0, self.rounds)
        self._w = w
        self._n_sent = prob.n.copy()
        self.last_rounds = rounds
        return normalize_l1(w), scalars, scalars * FLOAT_BITS
