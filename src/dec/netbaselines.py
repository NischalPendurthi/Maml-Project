"""Prior papers' algorithms on our problem, over a graph (E34).

Each agent runs its own copy of a single-agent baseline (src/baselines.py) and also
learns from every other agent's observations, relayed along the graph: agent k's
pull at round r reaches agent i before round r + dist(i, k).  This is IDEAL
relaying of raw data -- every observation, exact, at the fastest delay the graph
allows -- so it is an upper bound on what the papers' own gossip achieves:

    linucb   ≈ DLUCB (Amani & Thrampoulidis 2021) / Coop-LinUCB: linear model
    estor    ≈ Dec-ESTOR: monotone single-index (Kang et al. 2026), pooled exploration
    gstor    ≈ Dec-GSTOR: explore-then-commit single-index, pooled exploration
    igpucb   ≈ Coop-KernelUCB (Dubey & Pentland 2020): RBF kernel on R^d

Stein-based methods may only use uniform-exploration samples, so each relayed
observation carries the sender's "this was an exploration pull" flag.

Communication is counted as raw relaying: d + 2 scalars (x, y, flag) per pull,
delivered to each of the other N − 1 agents.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from ..baselines import ESTOR, GSTOR, IGPUCB, LinUCB
from .graph import Graph


def distances(A):
    """All-pairs hop distances of an undirected graph (BFS from every node)."""
    N = A.shape[0]
    D = np.full((N, N), -1, dtype=int)
    for s in range(N):
        D[s, s] = 0
        frontier = [s]
        while frontier:
            nxt = np.flatnonzero(A[frontier].any(axis=0) & (D[s] < 0))
            D[s, nxt] = D[s, frontier[0]] + 1
            frontier = list(nxt)
    return D


class NetLinUCB(LinUCB):
    def flag(self):
        return True

    def absorb(self, X, a, y, flag):
        self.update(X, a, y)


class NetESTOR(ESTOR):
    """Exploration budget d·√(pooled samples), as single-agent ESTOR at horizon N·T."""

    def flag(self):
        return self._pending_explore

    def absorb(self, X, a, y, flag):
        pending = self._pending_explore
        self._pending_explore = flag
        self.update(X, a, y)
        self._pending_explore = pending


class NetGSTOR(GSTOR):
    """Built with horizon N·T, so the exploration target n_e is the pooled one."""

    def flag(self):
        return self.theta is None

    def absorb(self, X, a, y, flag):
        if flag:
            self.update(X, a, y)
        else:
            self.t += 1


class NetIGPUCB(IGPUCB):
    """Built with horizon N·T so the data buffer holds every relayed pull."""

    def flag(self):
        return True

    def update(self, X, a, y):
        self.t += 1
        if self._n < self._X.shape[0]:
            self._X[self._n] = X[a]
            self._y[self._n] = y
            self._n += 1
        n = self._n
        last = getattr(self, "_last_fit", 0)
        if n >= max(10, self.d) and (self._alpha is None or n - last >= self.refit_every):
            self._last_fit = n
            self._refit()

    absorb = NetLinUCB.absorb


ALGOS = {"linucb": NetLinUCB, "estor": NetESTOR, "gstor": NetGSTOR, "igpucb": NetIGPUCB}
POOLED_T = {"gstor", "igpucb"}          # built with horizon N·T


class NetRelayBaseline:
    name = "NetRelayBaseline"

    def __init__(self, N, d, K, T, env_info, rng, agent_infos=None, graph="ring",
                 graph_kw=None, algo="linucb", algo_kw=None, graph_seed=0):
        self.N, self.d, self.t = N, d, 0
        self.g = graph if isinstance(graph, Graph) else \
            Graph(graph, N, seed=graph_seed, **(graph_kw or {}))
        self.dist = distances(self.g.A0)
        cls = ALGOS[algo]
        horizon = N * T if algo in POOLED_T else T
        self.agents = [cls(d, K, horizon, env_info, r, **(algo_kw or {})) for r in rng.spawn(N)]
        self.queue = defaultdict(list)       # due round -> [(receiver, X, a, y, flag)]
        self._flag = [False] * N
        self.comm_scalars = 0
        self.last_event = None

    def select(self, i, X):
        a = self.agents[i].select(X)
        self._flag[i] = self.agents[i].flag()   # read before update can change it
        return a

    def update(self, i, X, a, y):
        self.agents[i].update(X, a, y)
        r = self.t + 1                       # the round being played
        for j in range(self.N):
            if j != i:
                self.queue[r + self.dist[i, j]].append((j, X, a, y, self._flag[i]))
        self.comm_scalars += (self.d + 2) * (self.N - 1)

    def end_round(self):
        self.t += 1
        for j, X, a, y, flag in self.queue.pop(self.t + 1, []):   # usable in round t + 1
            self.agents[j].absorb(X, a, y, flag)

    def diagnostics(self):
        return dict(T0_used=None, N_bins=None, comm_scalars=self.comm_scalars,
                    comm_bits=32 * self.comm_scalars, comm_phase1=0, comm_rounds=self.t,
                    diameter=self.g.diameter, gap=self.g.gap)
