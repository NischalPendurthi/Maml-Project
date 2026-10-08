"""N agents each running the unmodified single-agent ZoomSIB-UCB: zero communication.

Every agent estimates its own theta, stops Phase 1 on its own, and lays down its
own bin grid -- the reference that every federated variant is measured against.
"""

from __future__ import annotations

import numpy as np

from ..zoomsib import ZoomSIBUCB


class IndependentAgents:
    name = "Independent"

    def __init__(self, N, d, K, T, env_info, rng, agent_infos=None, **kw):
        self.N = N
        self.t = 0
        infos = agent_infos if agent_infos is not None else [env_info] * N
        self.agents = [ZoomSIBUCB(d, K, T, inf, r, **kw) for r, inf in zip(rng.spawn(N), infos)]
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


class IndependentEngines:
    """N agents, each running its OWN copy of any engine with N = 1: no communication.

    `inner` is an engine config (e.g. dict(engine="fed", freeze="fixed", T0=...) or
    dict(engine="mib", m=1, ...)), so "each agent alone" uses exactly the same
    Phase-1 length and estimator as the networked variant it is compared with.
    Each copy sees only its own agent's info (its own score under covariate shift).
    """
    name = "IndependentEngines"

    def __init__(self, N, d, K, T, env_info, rng, agent_infos=None, inner=None):
        from .runner import engine_class
        kw = dict(inner or {})
        cls = engine_class(kw.pop("engine", "fed"))
        kw.pop("label", None)
        kw.pop("style", None)
        infos = agent_infos if agent_infos is not None else [env_info] * N
        self.N = N
        self.inner = [cls(1, d, K, T, inf, r, agent_infos=[inf], **kw)
                      for inf, r in zip(infos, rng.spawn(N))]
        self.comm_scalars = self.comm_bits = self.comm_rounds = 0
        self.last_event = None

    def select(self, i, X):
        return self.inner[i].select(0, X)

    def update(self, i, X, a, y):
        self.inner[i].update(0, X, a, y)

    def end_round(self):
        for e in self.inner:
            e.end_round()

    def diagnostics(self):
        dg = [e.diagnostics() for e in self.inner]
        t0 = [x["T0_used"] for x in dg if x["T0_used"] is not None]
        return dict(
            T0_used=float(np.mean(t0)) if t0 else None,
            N_bins=float(np.mean([x["N_bins"] for x in dg if x["N_bins"] is not None] or [np.nan])),
            theta_hat=dg[0]["theta_hat"],
            theta_agents=[x["theta_hat"] for x in dg],
            comm_scalars=0, comm_bits=0, comm_phase1=0, comm_rounds=0,
            comm_phase1_bits=0, comm_rounds_phase1=0,
        )


class RandomAgents:
    """Every agent pulls a uniformly random arm: the 'learned nothing' reference.

    Regret ÷ this engine's regret puts agents at different positions on the
    reward curve on one scale (1 = no better than random).
    """
    name = "RandomAgents"

    def __init__(self, N, d, K, T, env_info, rng, agent_infos=None, **kw):
        self.K = K
        self.rngs = rng.spawn(N)
        self.comm_scalars = self.comm_bits = self.comm_rounds = 0
        self.last_event = None

    def select(self, i, X):
        return int(self.rngs[i].integers(self.K))

    def update(self, i, X, a, y):
        pass

    def end_round(self):
        pass

    def diagnostics(self):
        return dict(T0_used=None, N_bins=None, theta_hat=None, comm_scalars=0, comm_bits=0,
                    comm_phase1=0, comm_rounds=0, comm_phase1_bits=0, comm_rounds_phase1=0)
