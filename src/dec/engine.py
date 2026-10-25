"""DecTwoPhase: Fed-ZoomSIB with NO server -- agents talk only over a graph.

Same two phases as src/fed/engine.py, but every network-wide quantity is
obtained by communication along the edges of a `Graph` (topology + mixing
matrix + dynamics, src/dec/graph/):

  Phase 1   agents explore and run a decentralised Phase-1 strategy
            (src/dec/phase1/): flooding, running consensus, push-sum, burst
            gossip, Chebyshev gossip, tree aggregation, DGD, gradient tracking.
            At pooled-size checkpoints each agent runs ZoomSIB's drift rule on
            its OWN estimate θ̂_i.

  Stopping  `stop_rule="all"` (default): the stop flag is raised once EVERY
            agent's estimate is stable; `"any"`: the first stable agent raises it --
            which freezes at the earliest of N stopping times and, measured in
            E14, roughly doubles regret when agents' estimates differ.
            The flag spreads one hop per round over the (realised) graph, and
            all agents freeze together once it has reached everybody.
            `freeze="fixed"` freezes at round `T0` instead (the schedule a
            proof would use), with no flag at all.
            `"pooled"` (Proposition 'prop:stop' of docs/proofs/serverless.tex): at each
            checkpoint every agent floods its local Stein sum; Λ = D rounds
            later every agent applies the drift rule to the SAME pooled sums,
            so all stop at the server's checkpoint and freeze the same θ̂.

  Freeze    each agent freezes its own θ̂_i (`agree="none"`), or all adopt the
            exact pooled direction after one flooding pass (`agree="exact"`).
            The window W comes from max-consensus (diameter rounds), so the
            grid is shared even when the θ̂_i differ slightly.

  Phase 2   sleeping UCB, each agent binning its arms with its own θ̂_i, on
            the table a decentralised Phase-2 strategy provides
            (src/dec/phase2/): flooding, consensus, push-sum, burst gossip...

Simplifications, stated: the pooled sample size used for checkpoints and for
the truncation threshold is N·t (every agent knows N and the round), exact
when all agents are active; burst communication is instantaneous between two
bandit rounds; the stop flag's arrival is simulated on the realised graphs.
"""

from __future__ import annotations

import numpy as np

from ..fed.engine import FedTwoPhase
from ..fed.phase1.base import local_V, truncated
from ..stein import normalize_l1
from .graph import Graph
from .gossip import flood_max
from .phase1 import make_dec_phase1
from .phase2 import make_dec_phase2

FLOAT_BITS = 32


class DecTwoPhase(FedTwoPhase):
    name = "DecTwoPhase"

    def __init__(self, N, d, K, T, env_info, rng,
                 graph="ring", graph_kw=None,
                 phase1="flood", phase1_kw=None,
                 phase2="flood", phase2_kw=None,
                 stop_rule="all", freeze="adaptive", T0=None, agree="none",
                 graph_seed=0, dp_eps=None, dp_delta=1e-5, **kw):
        super().__init__(N, d, K, T, env_info, rng, phase1="exact", phase2="none", **kw)
        self.g = graph if isinstance(graph, Graph) else \
            Graph(graph, N, seed=graph_seed, **(graph_kw or {}))
        if self.g.N != N:
            raise ValueError(f"graph has {self.g.N} nodes, network has {N} agents")
        self.p1 = make_dec_phase1(phase1, **(phase1_kw or {}))
        self.p1.setup(N, d, self.g)
        self.p2 = make_dec_phase2(phase2, **(phase2_kw or {}))
        self.p2.attach(self.g)
        self.stop_rule, self.freeze_mode, self.T0_fixed, self.agree = stop_rule, freeze, T0, agree
        self.dp_eps, self.dp_delta = dp_eps, dp_delta
        if freeze == "fixed" and T0 is None:
            raise ValueError("freeze='fixed' needs T0")
        self._prev_i = None
        self._stable_i = np.zeros(N, dtype=int)
        self.flag = None                         # stop flag, once raised
        self._stop_at = None                     # pooled rule: freeze round, and the sums to use
        self._b_stop = None
        self._prev_pool = None
        self._stable_pool = 0
        self.theta_agents = None
        self.theta_now = np.full((N, d), 1.0 / d)
        self.flag_rounds = 0

    # ------------------------------------------------------------------
    # Phase 1
    # ------------------------------------------------------------------
    def own_sums(self):
        tau = self._tau(self.N * max(self.t, 1))
        b = np.zeros((self.N, self.d))
        n = np.zeros(self.N)
        for i, ag in enumerate(self.agents):
            if ag.n:
                b[i] = truncated(local_V(ag), tau).sum(axis=0)
                n[i] = ag.n
        return b, n

    def federated_theta(self, log=False):
        """What a server would compute (reference, used by the dashboard)."""
        b, _ = self.own_sums()
        return normalize_l1(b.sum(axis=0))

    def _normalise_rows(self, est):
        return np.array([normalize_l1(e) for e in est])

    def _checkpoint_dec(self, b, n):
        est, scalars, rounds = self.p1.estimate(self.t, b, n)
        if scalars or rounds:
            self._log(scalars, scalars * FLOAT_BITS, phase1=True, rounds=rounds)
        th = self._normalise_rows(est)
        self.theta_now = th
        self._next_check = int(np.ceil(self.N * self.t * self.stop_growth))
        if self._prev_i is not None:
            drift = np.abs(th - self._prev_i).sum(axis=1)
            self._stable_i = np.where(drift < self.stop_tol, self._stable_i + 1, 0)
        self._prev_i = th
        ok = self._stable_i >= self.stop_patience
        return ok.all() if self.stop_rule == "all" else ok.any(), ok

    def _spread_flag(self):
        A = self.g.A
        heard = (A.T.astype(int) @ self.flag.astype(int)) > 0
        self._log(int(A[self.flag].sum()), int(A[self.flag].sum()), phase1=True)
        self.flag = self.flag | heard
        self.flag_rounds += 1

    def end_round(self):
        self.t += 1
        self.last_event = None
        self.g.step()
        if self.phase == 2:
            scalars, event = self.p2.end_round(self.t)
            if event:
                self._log(scalars, scalars * FLOAT_BITS, rounds=getattr(self.p2, "last_rounds", 1))
                self.last_event = event
            return

        b, n = self.own_sums()
        if not n.any():
            return
        if self.p1.interleaved:
            sc = self.p1.on_round(self.t, b, n)
            if sc:
                self._log(sc, sc * FLOAT_BITS, phase1=True)
            self.last_event = "gossip"
            self.theta_now = self._normalise_rows(self.p1.estimate(self.t, b, n)[0])

        if self.freeze_mode == "fixed":
            if self.t >= self.T0_fixed:
                self._finalise_dec(b, n)
            return
        if self.stop_rule == "pooled":
            self._pooled_step(b, n)
            return
        if self.flag is not None:                        # flag travelling
            self._spread_flag()
            if self.flag.all() or self.t >= self.T0_cap:
                self._finalise_dec(b, n)
            return
        if self.t >= self.T0_cap:
            self._finalise_dec(b, n)
            return
        if self.N * self.t >= self._next_check:
            self.last_event = "stein"
            stop, ok = self._checkpoint_dec(b, n)
            if stop:
                self.flag = ok.copy() if self.stop_rule == "any" else np.ones(self.N, bool)
                if self.flag.all():
                    self._finalise_dec(b, n)

    def _pooled_step(self, b, n):
        D = int(self.g.diameter)
        if self._stop_at is not None:
            if self.t >= self._stop_at:                   # everyone now holds the checkpoint's sums
                self._finalise_dec(self._b_stop, n, flooded=True)
            return
        if self.t >= self.T0_cap:
            self._finalise_dec(b, n)
            return
        if self.N * self.t < self._next_check:
            return
        self.last_event = "stein"
        k = int(self.g.arcs() * self.N * (self.d + 1))    # every local sum crosses every arc once
        self._log(k, k * FLOAT_BITS, phase1=True, rounds=D)
        self._next_check = int(np.ceil(self.N * self.t * self.stop_growth))
        th = normalize_l1(b.sum(axis=0))
        if self._prev_pool is not None:
            drift = float(np.abs(th - self._prev_pool).sum())
            self._stable_pool = self._stable_pool + 1 if drift < self.stop_tol else 0
        self._prev_pool = th
        if self._stable_pool >= self.stop_patience:
            self._stop_at = self.t + D
            self._b_stop = b.copy()

    def _finalise_dec(self, b, n, flooded=False):
        if self.dp_eps is not None:                       # private Phase 1 (Theorem 'thm:private')
            tau = self._tau(self.N * max(self.t, 1))      # every coordinate of a summand is in [−τ, τ]
            sig = 2.0 * tau * np.sqrt(self.d) * np.sqrt(2.0 * np.log(1.25 / self.dp_delta)) / self.dp_eps
            b = b + np.array([ag.rng.normal(0.0, sig, self.d) for ag in self.agents])   # own noise
        est, scalars, rounds = self.p1.estimate(self.t, b, n)
        if scalars or rounds:
            self._log(scalars, scalars * FLOAT_BITS, phase1=True, rounds=rounds)
        th = self._normalise_rows(est)
        D = self.g.diameter if np.isfinite(self.g.diameter) else self.N
        if flooded:                                       # pooled stop: sums already flooded
            th = np.tile(normalize_l1(b.sum(axis=0)), (self.N, 1))
        elif self.agree == "exact":
            th = np.tile(normalize_l1(b.sum(axis=0)), (self.N, 1))
            k = int(D * self.g.arcs() * (self.d + 1))
            self._log(k, k * FLOAT_BITS, phase1=True, rounds=int(D))
        self.theta_agents = th
        self.theta_now = th
        self.theta_hat = normalize_l1(th.mean(axis=0))   # summary only
        self.theta_local = self.local_thetas()
        self.T0_used = self.t
        self.T0_samples = [ag.n for ag in self.agents]

        if self.dp_eps is not None:
            # data-free window W = X_max (as in the proofs), so Phase-1 contexts stay private
            xmax = self.info["ctx_std"] * np.sqrt(
                2.0 * np.log(2.0 * self.d * self.N * self.T * self.K / self.delta))
            self.W = max(xmax, 10.0 * self.Delta)
        else:
            zmax = np.array([float(np.max(np.abs(np.asarray(ag.X_buf) @ th[i]))) if ag.n else 0.0
                             for i, ag in enumerate(self.agents)])
            zmax = flood_max(self.g.A0, zmax, D)              # max-consensus
            k = int(D * self.g.A0.sum())
            self._log(k, k * FLOAT_BITS, phase1=True, rounds=int(D))
            self.W = max(float(zmax.max()) * self.w_pad, 10.0 * self.Delta)

        self.N_bins = int(np.ceil(2.0 * self.W / self.Delta))
        self.p2.setup(self.N, self.N_bins + 2)
        self.contrib = np.zeros((self.N, self.N_bins + 2), dtype=np.int64)
        for ag in self.agents:
            ag.S_buf, ag.y_buf, ag.X_buf = [], [], []
        self.ucb_const = self.ucb_scale * self.sigma * np.sqrt(
            2.0 * np.log(2.0 * self.N_bins * self.N * self.T / self.delta))
        self.phase = 2
        self.last_event = "freeze"

    # ------------------------------------------------------------------
    def _theta_for(self, i):
        if i is None or self.theta_agents is None:
            return self.theta_hat
        return self.theta_agents[i]

    def disagreement(self):
        """Mean l1 distance of the agents' frozen directions from their mean."""
        th = self.theta_agents if self.theta_agents is not None else self.theta_now
        return float(np.abs(th - th.mean(axis=0)).sum(axis=1).mean())

    def diagnostics(self):
        dg = super().diagnostics()
        dg.update(theta_agents=self.theta_agents, disagreement=self.disagreement(),
                  graph=self.g.describe(), diameter=self.g.diameter, gap=self.g.gap,
                  flag_rounds=self.flag_rounds)
        return dg
