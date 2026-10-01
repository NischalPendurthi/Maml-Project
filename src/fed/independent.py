"""N agents each running the unmodified single-agent ZoomSIB-UCB: zero communication.

Every agent estimates its own theta, stops Phase 1 on its own, and lays down its
own bin grid -- the reference that every federated variant is measured against.
"""

from __future__ import annotations

import numpy as np

from ..zoomsib import ZoomSIBUCB


class IndependentAgents:
    name = "Independent"

    def __init__(self, N, d, K, T, env_info, rng, **kw):
        self.N = N
        self.t = 0
        self.agents = [ZoomSIBUCB(d, K, T, env_info, r, **kw) for r in rng.spawn(N)]
        self.comm_scalars = self.comm_bits = self.comm_rounds = 0
        self.last_event = None

    def select(self, i, X):
        return self.agents[i].select(X)

    def update(self, i, X, a, y):
        self.agents[i].update(X, a, y)

    def end_round(self):
        self.t += 1

    def diagnostics(self):
        t0 = [ag.T0_used for ag in self.agents if ag.T0_used is not None]
        return dict(
            T0_used=float(np.mean(t0)) if t0 else None,
            network_T0=float(np.sum(t0)) if t0 else None,
            N_bins=[ag.N_bins for ag in self.agents],
            theta_hat=[ag.theta_hat for ag in self.agents],
            comm_scalars=0, comm_bits=0, comm_phase1=0, comm_rounds=0,
        )
