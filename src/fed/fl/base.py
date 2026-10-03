"""Interface every FL method implements, plus the shared local-training loop.

A method is an algorithm for `FedQuadratic`: given the current global model w
it runs ONE communication round (clients train locally from w, upload, the
server aggregates) and returns the new w.  `solve` runs several rounds and
reports the communication spent.  Methods keep state (momentum, control
variates, ...) across calls, because in a bandit the problem keeps growing and
the method is invoked again at every checkpoint / sync -- warm-started.

Conventions shared by all methods, so they are comparable:
  * local optimiser: full-batch gradient descent on the client's own data, step
    lr = lr_scale / L where L is the largest per-sample smoothness among
    active clients (plus any proximal term) -- one client step size for all;
  * aggregation weights p_i = n_i / Σ n (sample-weighted), unless the method
    is defined otherwise (FedDyn, which rescales the local losses instead);
  * communication is counted in scalars.  A "vector message" costs D scalars
    dense, or 2 per non-zero (index, value) on diagonal (Phase-2) problems,
    where a client's update is supported on the bins it has data for.
    Downloads are dense D per vector.  Inactive clients (n_i = 0) send nothing.
"""

from __future__ import annotations

import numpy as np

from .problem import FedQuadratic


def local_gd(prob: FedQuadratic, w, steps, lr, extra=None):
    """Run `steps` (int or (N,) ints) GD steps per client from w.

    `extra(W)` adds a correction to each client's gradient (prox, SCAFFOLD,
    FedDyn).  Returns the (N, D) local models; inactive clients stay at w.
    """
    W = np.tile(np.asarray(w, dtype=float), (prob.N, 1))
    steps = np.broadcast_to(np.asarray(steps), (prob.N,))
    lr = np.broadcast_to(np.asarray(lr, dtype=float), (prob.N,))
    for k in range(int(steps.max()) if steps.size else 0):
        G = prob.grad(W)
        if extra is not None:
            G = G + extra(W)
        live = (steps > k) & prob.active
        W[live] -= lr[live, None] * G[live]
    return W


def vector_cost(prob: FedQuadratic):
    """(N,) scalars for one uploaded vector message per client."""
    if prob.diag:
        return 2 * prob.support().sum(axis=1)
    return np.full(prob.N, prob.D)


class FLMethod:
    name = "base"
    label = "base"
    one_shot = False            # exact/closed-form after one round
    up_vectors = 1              # vector messages each client uploads per round
    up_extra = 0                # plus this many scalars
    down_vectors = 1            # vector messages the server broadcasts per round

    def __init__(self, local_steps=5, lr_scale=1.0):
        self.local_steps = int(local_steps)
        self.lr_scale = float(lr_scale)
        self._shape = None

    # -- state ------------------------------------------------------------
    def _ensure(self, prob):
        if self._shape != (prob.N, prob.D):
            self._shape = (prob.N, prob.D)
            self.reset(prob.N, prob.D)

    def reset(self, N, D):
        """(Re)initialise server/client state for N clients in dimension D."""

    # -- one round ----------------------------------------------------------
    def round(self, prob: FedQuadratic, w):
        raise NotImplementedError

    def round_cost(self, prob: FedQuadratic):
        act = prob.active
        up = (self.up_vectors * vector_cost(prob) + self.up_extra)[act].sum()
        down = self.down_vectors * prob.D * act.sum()
        return int(up + down)

    def solve(self, prob: FedQuadratic, w0, rounds):
        """-> (w, scalars communicated, rounds used)."""
        self._ensure(prob)
        rounds = 1 if self.one_shot else max(int(rounds), 1)
        w = np.asarray(w0, dtype=float).copy()
        cost = 0
        for _ in range(rounds):
            cost += self.round_cost(prob)
            w = self.round(prob, w)
        return w, cost, rounds

    # -- helpers ------------------------------------------------------------
    def _lr(self, prob, extra_curv=0.0):
        return self.lr_scale / (prob.L_max() + extra_curv)

    @staticmethod
    def _avg(prob, W):
        return (prob.p[:, None] * W).sum(axis=0)
