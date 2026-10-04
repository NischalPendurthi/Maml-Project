"""Communication topologies: boolean adjacency matrices A (A[i, j] = i can send to j).

All undirected unless stated; every generator returns a CONNECTED graph (random
families resample until connected) with no self-loops.

  complete    everyone talks to everyone (the server-free analogue of a star+server)
  star        agent 0 is a hub: diameter 2, but the hub carries all traffic
  ring        each agent talks to 2 others: diameter N/2, spectral gap ~ 1/N²
  path        a ring with one edge cut: the worst-connected tree
  torus       √N × √N grid with wrap-around
  grid        √N × √N grid without wrap-around
  hypercube   log2 N neighbours each (N must be a power of 2)
  expander    random d-regular graph (d = 4): diameter ~ log N, constant gap
  erdos       Erdős–Rényi G(N, p), p = 2 ln N / N
  geometric   random points in the unit square, edges within radius r
  smallworld  Watts–Strogatz ring lattice (k = 2 each side), rewiring prob 0.2
  barbell     two cliques of N/2 joined by ONE edge: a bottleneck
  directed    directed ring plus random extra arcs: strongly connected, NOT symmetric
"""

from __future__ import annotations

import numpy as np


def _undirected(edges, N):
    A = np.zeros((N, N), dtype=bool)
    for i, j in edges:
        if i != j:
            A[i, j] = A[j, i] = True
    return A


def is_connected(A):
    """Strong connectivity (BFS along arcs from node 0, and along reversed arcs)."""
    N = A.shape[0]
    for M in (A, A.T):
        seen = np.zeros(N, dtype=bool)
        seen[0] = True
        frontier = [0]
        while frontier:
            nxt = np.flatnonzero(M[frontier].any(axis=0) & ~seen)
            seen[nxt] = True
            frontier = list(nxt)
        if not seen.all():
            return False
    return True


def complete(N, rng=None):
    A = np.ones((N, N), dtype=bool)
    np.fill_diagonal(A, False)
    return A


def star(N, rng=None):
    return _undirected([(0, i) for i in range(1, N)], N)


def ring(N, rng=None):
    return _undirected([(i, (i + 1) % N) for i in range(N)], N)


def path(N, rng=None):
    return _undirected([(i, i + 1) for i in range(N - 1)], N)


def _side(N):
    s = int(round(np.sqrt(N)))
    if s * s != N:
        raise ValueError(f"torus/grid need a square N, got {N}")
    return s


def torus(N, rng=None):
    s = _side(N)
    e = [(r * s + c, r * s + (c + 1) % s) for r in range(s) for c in range(s)]
    e += [(r * s + c, ((r + 1) % s) * s + c) for r in range(s) for c in range(s)]
    return _undirected(e, N)


def grid(N, rng=None):
    s = _side(N)
    e = [(r * s + c, r * s + c + 1) for r in range(s) for c in range(s - 1)]
    e += [(r * s + c, (r + 1) * s + c) for r in range(s - 1) for c in range(s)]
    return _undirected(e, N)


def hypercube(N, rng=None):
    k = int(round(np.log2(N)))
    if 2 ** k != N:
        raise ValueError(f"hypercube needs N = 2^k, got {N}")
    return _undirected([(i, i ^ (1 << b)) for i in range(N) for b in range(k)], N)


def _resample(make, rng, tries=500):
    for _ in range(tries):
        A = make(rng)
        if is_connected(A):
            return A
    raise RuntimeError("could not sample a connected graph")


def expander(N, rng=None, degree=4):
    """Random d-regular graph by the pairing model (resampled until simple + connected)."""
    rng = rng if rng is not None else np.random.default_rng(0)

    def make(r):
        while True:
            stubs = np.repeat(np.arange(N), degree)
            r.shuffle(stubs)
            pairs = stubs.reshape(-1, 2)
            if np.all(pairs[:, 0] != pairs[:, 1]):
                key = np.sort(pairs, axis=1)
                if len(np.unique(key, axis=0)) == len(key):
                    return _undirected(map(tuple, pairs), N)
    return _resample(make, rng)


def erdos(N, rng=None, p=None):
    rng = rng if rng is not None else np.random.default_rng(0)
    p = p if p is not None else min(1.0, 2.0 * np.log(N) / N)

    def make(r):
        U = np.triu(r.random((N, N)) < p, 1)
        return U | U.T
    return _resample(make, rng)


def geometric(N, rng=None, radius=None):
    rng = rng if rng is not None else np.random.default_rng(0)
    radius = radius if radius is not None else 1.6 * np.sqrt(np.log(N) / (np.pi * N))

    def make(r):
        X = r.random((N, 2))
        D = np.linalg.norm(X[:, None] - X[None], axis=-1)
        A = D < radius
        np.fill_diagonal(A, False)
        return A
    return _resample(make, rng)


def smallworld(N, rng=None, k=2, beta=0.2):
    rng = rng if rng is not None else np.random.default_rng(0)

    def make(r):
        edges = set()
        for i in range(N):
            for s in range(1, k + 1):
                j = (i + s) % N
                if r.random() < beta:
                    j = int(r.integers(N))
                if j != i:
                    edges.add((min(i, j), max(i, j)))
        return _undirected(edges, N)
    return _resample(make, rng)


def barbell(N, rng=None):
    h = N // 2
    e = [(i, j) for i in range(h) for j in range(i + 1, h)]
    e += [(i, j) for i in range(h, N) for j in range(i + 1, N)]
    e.append((h - 1, h))
    return _undirected(e, N)


def directed(N, rng=None, extra=None):
    """Directed ring 0→1→…→N−1→0 plus random extra arcs (out-degrees differ)."""
    rng = rng if rng is not None else np.random.default_rng(0)
    A = np.zeros((N, N), dtype=bool)
    for i in range(N):
        A[i, (i + 1) % N] = True
    extra = extra if extra is not None else N
    for _ in range(extra):
        i, j = rng.integers(N, size=2)
        if i != j:
            A[i, j] = True
    return A


TOPOLOGIES = {f.__name__: f for f in (complete, star, ring, path, torus, grid, hypercube,
                                      expander, erdos, geometric, smallworld, barbell,
                                      directed)}
