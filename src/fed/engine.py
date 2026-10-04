"""Generic federated two-phase single-index bandit.

Setting (viz/data/p8-fedzoomsib-conjecture.js, `p8.setting`): N agents share
the SAME unknown direction theta_* and link f.  Each round every agent i sees
its own K arms X_{i,t} ~ p, pulls one and observes
y_{i,t} = f(<x_{i,t}, theta_*>) + eta_{i,t}.  Network regret is the sum of the
agents' regrets.

The engine keeps the two-phase skeleton of ZoomSIB-UCB (Dey, Bhore & Ghosh
2026, Algorithm 1) and delegates the two federation decisions to pluggable
strategies:

  Phase 1   all agents explore uniformly and keep their samples locally.  At
            geometrically spaced checkpoints (on the POOLED sample size) the
            Phase-1 strategy (src/fed/phase1/) produces one network estimate
            theta_hat; the ZoomSIB adaptive stopping rule runs on it.  Because
            the rule sees the pooled size, per-agent exploration shrinks with N.

  Freeze    theta_hat_0 is frozen for EVERY agent at once (so the sample
            splitting of Remark 3.1 survives network-wide); each agent uploads
            max |<x, theta_hat_0>| over its Phase-1 contexts, the server sets
            the window W and broadcasts (theta_hat_0, W): one shared bin grid.

  Phase 2   sleeping UCB over the bins available to each agent.  The Phase-2
            strategy (src/fed/phase2/) owns the (n_j, S_j) tables, says which
            table each agent acts on, and when to communicate.

Which strategies make up "Fed-ZoomSIB" (or plain ZoomSIB at N=1, or any
variant) is an experiment choice -- see experiments/configs/.

Communication is counted in scalars and bits (32 per full-precision scalar),
both directions, plus the number of communication rounds.
"""

from __future__ import annotations

import numpy as np

from ..stein import tau_default
from .phase1 import make_phase1
from .phase1.base import FLOAT_BITS
from .phase1.normavg import local_estimates
from .phase2 import make_phase2


class Agent:
    """What one agent keeps locally during Phase 1 (never uploaded raw).

    `info` is what THIS agent may know -- in particular its own score function,
    which differs across agents under covariate shift.
    """

    def __init__(self, i, rng, info=None):
        self.i = i
        self.rng = rng
        self.info = info
        self.S_buf, self.y_buf, self.X_buf = [], [], []

    @property
    def n(self):
        return len(self.y_buf)


class FedTwoPhase:
    name = "FedTwoPhase"

    def __init__(self, N, d, K, T, env_info, rng,
                 phase1="exact", phase1_kw=None,
                 phase2="periodic", phase2_kw=None,
                 delta=0.01,
                 stop_tol=0.15,
                 stop_patience=1,
                 stop_growth=1.5,
                 min_explore=None,
                 max_explore_frac=0.5,
                 w_pad=1.05,
                 ucb_scale=1.0,
                 use_truncation=True,
                 bin_width="agent",
                 freeze="adaptive",
                 T0=None,
                 agent_infos=None):
        self.N, self.d, self.K, self.T = N, d, K, T
        self.info = env_info
        self.sigma = env_info["sigma"]
        self.M = env_info["M"]
        self.L_f = env_info["L_f"]
        self.score = env_info["score"]
        self.delta = delta
        self.w_pad = w_pad
        self.ucb_scale = ucb_scale
        self.use_truncation = use_truncation

        r_agents, r_p1 = rng.spawn(2)
        infos = agent_infos if agent_infos is not None else [env_info] * N
        self.agents = [Agent(i, r, inf) for i, (r, inf) in enumerate(zip(r_agents.spawn(N), infos))]
        self.p1 = make_phase1(phase1, r_p1, **(phase1_kw or {}))
        self.p2 = make_phase2(phase2, **(phase2_kw or {}))

        # Bin width: ZoomSIB's single-agent choice Δ = T^{-1/3}, or the network
        # choice Δ = (NT)^{-1/3} that balances the discretisation bias N·T·Δ
        # against the pooled UCB term √(NT/Δ) -- see exp13.
        if bin_width not in ("agent", "network"):
            raise ValueError(f"bin_width must be 'agent' or 'network', not {bin_width!r}")
        self.Delta = (T * (N if bin_width == "network" else 1)) ** (-1.0 / 3.0)
        self.T0_cap = int(np.ceil(max_explore_frac * T))            # rounds
        # freeze="fixed": explore exactly T0 rounds per agent, pool once, no stop
        # rule and no checkpoints -- the schedule the regret proofs use.
        if freeze not in ("adaptive", "fixed"):
            raise ValueError(f"freeze must be 'adaptive' or 'fixed', not {freeze!r}")
        if freeze == "fixed" and T0 is None:
            raise ValueError("freeze='fixed' needs T0")
        self.freeze_mode, self.T0_fixed = freeze, T0
        self.stop_tol = stop_tol
        self.stop_patience = stop_patience
        self.stop_growth = stop_growth
        # Checked on the POOLED sample size, starting where a lone agent would.
        self.min_explore = min_explore if min_explore is not None else max(50, 5 * d)
        self._next_check = self.min_explore
        self._prev_theta = None
        self._stable = 0

        self.t = 0
        self.phase = 1
        self.theta_hat = None
        self.theta_local = None
        self.W = self.N_bins = self.ucb_const = None
        self.contrib = None                     # diagnostic: who fed each bin
        self._last = None
        self.T0_used = None

        self.comm_scalars = self.comm_bits = self.comm_rounds = 0
        self.comm_phase1 = self.comm_phase1_bits = self.comm_rounds_phase1 = 0
        self.comm_log = []                      # (t, scalars, bits, phase) per event
        self.last_event = None

    # ------------------------------------------------------------------
    # Phase 1
    # ------------------------------------------------------------------
    def _tau(self, n):
        if not self.use_truncation:
            return None
        return tau_default(self.sigma, self.L_f, self.M, n, self.d, self.delta)

    def n_pool(self):
        return sum(ag.n for ag in self.agents)

    def federated_theta(self, log=False):
        theta, scalars, bits = self.p1.aggregate(self.agents, self._tau)
        if log:
            # + one stop/continue flag back to every agent (adaptive stopping only)
            flag = self.N if self.freeze_mode == "adaptive" else 0
            self._log(scalars + flag, bits + flag * FLOAT_BITS, phase1=True,
                      rounds=getattr(self.p1, "last_rounds", 1))
        return theta

    def local_thetas(self):
        """Each agent's estimate from its own data alone (diagnostic)."""
        return local_estimates(self.agents, self._tau)

    def _checkpoint(self):
        theta = self.federated_theta(log=True)
        self._next_check = int(np.ceil(self.n_pool() * self.stop_growth))
        if self._prev_theta is not None:
            drift = float(np.abs(theta - self._prev_theta).sum())
            self._stable = self._stable + 1 if drift < self.stop_tol else 0
        self._prev_theta = theta
        self.theta_hat = theta
        return self._stable >= self.stop_patience

    def _finalise(self, theta=None):
        self.theta_hat = theta if theta is not None else self.federated_theta(log=True)
        self.theta_local = self.local_thetas()
        self.T0_used = self.t                       # rounds (= samples per agent if all active)
        self.T0_samples = [ag.n for ag in self.agents]

        z_max = max(float(np.max(np.abs(np.asarray(ag.X_buf) @ self.theta_hat)))
                    for ag in self.agents if ag.n)
        self.W = max(z_max * self.w_pad, 10.0 * self.Delta)
        k = self.N * 1 + self.N * (self.d + 1)       # up: z_max; down: theta_hat_0, W
        self._log(k, k * FLOAT_BITS, phase1=True)

        self.N_bins = int(np.ceil(2.0 * self.W / self.Delta))
        self.p2.setup(self.N, self.N_bins + 2)
        self.contrib = np.zeros((self.N, self.N_bins + 2), dtype=np.int64)
        for ag in self.agents:
            ag.S_buf, ag.y_buf, ag.X_buf = [], [], []
        # The confidence radius covers every pull in the network.
        self.ucb_const = self.ucb_scale * self.sigma * np.sqrt(
            2.0 * np.log(2.0 * self.N_bins * self.N * self.T / self.delta))
        self.phase = 2

    # ------------------------------------------------------------------
    # Phase 2
    # ------------------------------------------------------------------
    def _theta_for(self, i):
        """The frozen direction agent i projects with (shared here; per-agent in src/dec)."""
        return self.theta_hat

    def _bins(self, X, i=None):
        z = X @ self._theta_for(i)
        b = np.ceil((z + self.W) / self.Delta).astype(np.int64)
        b = np.clip(b, 1, self.N_bins)
        b[np.abs(z) > self.W] = -1
        return b

    # ------------------------------------------------------------------
    # Interface: select/update once per agent per round, then end_round()
    # ------------------------------------------------------------------
    def select(self, i, X):
        ag = self.agents[i]
        if self.phase == 1:
            return int(ag.rng.integers(self.K))
        b = self._bins(X, i)
        self._last = (i, X, b)                      # update() reuses the projection
        avail = b >= 0
        if not np.any(avail):
            return int(ag.rng.integers(self.K))
        idx = np.flatnonzero(avail)
        bj = b[idx]
        n, S = self.p2.view_at(i, bj)
        nn = np.maximum(n, 1)
        ucb = np.where(n == 0, np.inf, S / nn + self.ucb_const / np.sqrt(nn))
        return int(idx[int(np.argmax(ucb))])

    def update(self, i, X, a, y):
        if self.phase == 1:
            ag = self.agents[i]
            ag.S_buf.append(ag.info["score"](X[a]))
            ag.y_buf.append(y)
            ag.X_buf.append(X[a])
            return
        li, lX, lb = self._last if self._last is not None else (None, None, None)
        b = (lb if li == i and lX is X else self._bins(X, i))[a]
        if b >= 0:
            self.p2.record(i, b, y)
            self.contrib[i, b] += 1

    def end_round(self):
        self.t += 1
        self.last_event = None
        if self.phase == 1:
            if self.freeze_mode == "fixed":
                if self.t >= self.T0_fixed and self.n_pool():
                    self._finalise()
                    self.last_event = "freeze"
                return
            if self.t >= self.T0_cap and self.n_pool():
                self._finalise()
                self.last_event = "freeze"
            elif self.n_pool() >= self._next_check:
                self.last_event = "stein"
                if self._checkpoint():
                    self._finalise(self.theta_hat)
                    self.last_event = "freeze"
            return
        scalars, event = self.p2.end_round(self.t)
        if event:
            bits = getattr(self.p2, "last_bits", None)     # compressed strategies report bits
            self._log(scalars, scalars * FLOAT_BITS if bits is None else bits,
                      rounds=getattr(self.p2, "last_rounds", 1))
            self.last_event = event

    # ------------------------------------------------------------------
    def _log(self, scalars, bits, phase1=False, rounds=1):
        self.comm_scalars += int(scalars)
        self.comm_bits += int(bits)
        self.comm_rounds += int(rounds)
        if phase1:
            self.comm_phase1 += int(scalars)
            self.comm_phase1_bits += int(bits)
            self.comm_rounds_phase1 += int(rounds)
        self.comm_log.append((self.t, int(scalars), int(bits), 1 if phase1 else 2))

    def diagnostics(self):
        return dict(
            T0_used=self.T0_used,
            network_T0=None if self.T0_used is None else self.N * self.T0_used,
            T0_samples=getattr(self, "T0_samples", None),
            N_bins=self.N_bins, W=self.W, Delta=self.Delta,
            theta_hat=self.theta_hat, theta_local=self.theta_local,
            comm_scalars=self.comm_scalars, comm_bits=self.comm_bits,
            comm_phase1=self.comm_phase1, comm_rounds=self.comm_rounds,
            comm_phase1_bits=self.comm_phase1_bits,
            comm_rounds_phase1=self.comm_rounds_phase1,
            comm_log=np.array(self.comm_log, dtype=np.int64).reshape(-1, 4),
            trigger_counts=getattr(self.p2, "trigger_counts", None),
        )
