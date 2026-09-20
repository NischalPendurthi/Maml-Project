"""Common interface for bandit algorithms."""

from __future__ import annotations

import numpy as np


class BanditAlgo:
    """Base class.

    A learner sees, each round, an arm set X of shape (K, d); it returns the
    index of the arm to pull and is then told the realised reward.

    `env_info` carries the quantities the learner is *allowed* to know:
    the score function (equivalently the context density), the noise scale,
    and loose bounds on the link.  Nothing about theta_* or the shape of f.
    """

    name = "base"

    def __init__(self, d, K, T, env_info, rng):
        self.d, self.K, self.T = d, K, T
        self.info = env_info
        self.rng = rng
        self.t = 0

    # -- to implement ------------------------------------------------------
    def select(self, X):                      # -> int in [0, K)
        raise NotImplementedError

    def update(self, X, a, y):                # -> None
        self.t += 1

    # -- helpers -----------------------------------------------------------
    def _random_arm(self):
        return int(self.rng.integers(self.K))


def env_info_from(env):
    """Bundle everything an algorithm may legitimately use."""
    return dict(
        score=env.score,
        sigma=env.sigma,
        kappa=env.kappa,
        M=env.M,
        L_f=env.L_f,
        L_fp=env.L_fp,
        ctx_std=env.ctx_std,
    )


def run_episode(env, algo, T, record_every=1):
    """Run one algorithm on one environment for T rounds.

    Returns the cumulative pseudo-regret,
        R_T = sum_t [ max_a f(<x_{t,a}, theta_*>) - f(<x_{t,a_t}, theta_*>) ],
    sub-sampled every `record_every` rounds.
    """
    inst = np.empty(T, dtype=float)
    for t in range(T):
        X = env.draw_arms()
        a = algo.select(X)
        y = env.pull(X, a)
        inst[t] = env.instant_regret(X, a)
        algo.update(X, a, y)
    cum = np.cumsum(inst)
    if record_every > 1:
        idx = np.arange(record_every - 1, T, record_every)
        return cum[idx], idx + 1
    return cum, np.arange(1, T + 1)
