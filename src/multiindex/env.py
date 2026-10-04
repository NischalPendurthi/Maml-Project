"""MIBEnv -- a multi-index bandit instance with Gaussian contexts.

Contexts x ~ N(0, s² I) (K arms per round), B ∈ R^{d×m} with orthonormal
columns, reward g(Bᵀx) + sigma·noise.  The links are chosen so that
E[∇²g(Bᵀx)] has full rank m: then span(B) is exactly the top-m (by |eigenvalue|)
eigenspace of the second-order Stein matrix M = E[y T(x)] = B E[∇²g] Bᵀ.

    bowl   g(z) = 1 − ‖z − c‖²,  c = (0.5, …, 0.5)         E[∇²g] = −2 I
    mixed  g(z) = cos(2 z₁) − ½ Σ_{k≥2} (z_k − 0.5)²         E[∇²g] = diag(−4e^{−2s²}, −1, …)

`mixed` is non-monotone and multimodal along z₁ and has unequal curvatures, so
its eigengap is smaller than the bowl's: the harder instance.
"""

from __future__ import annotations

import numpy as np


def _bowl(Z):
    return 1.0 - np.sum((Z - 0.5) ** 2, axis=-1)


def _mixed(Z):
    return np.cos(2.0 * Z[..., 0]) - 0.5 * np.sum((Z[..., 1:] - 0.5) ** 2, axis=-1)


MIB_LINKS = {"bowl": _bowl, "mixed": _mixed}


def parse_mib_link(link):
    """'mib:<link>:<m>' -> (link, m), or None for a single-index link name."""
    if not isinstance(link, str) or not link.startswith("mib:"):
        return None
    _, name, m = link.split(":")
    return name, int(m)


class MIBEnv:
    def __init__(self, d, K, m=2, link="bowl", sigma=0.1, seed=0, run_seed=None,
                 index_scale=1.0):
        if m > d:
            raise ValueError("m must be <= d")
        self.d, self.K, self.m, self.sigma, self.link_name = d, K, m, sigma, link
        self.g = MIB_LINKS[link]
        inst = np.random.default_rng(seed)
        Q, _ = np.linalg.qr(inst.standard_normal((d, m)))
        self.B = Q                                      # orthonormal columns
        self.ctx_std = float(index_scale)               # each index coordinate has this std
        self.kappa = self.ctx_std
        self.M = 1.0 / self.ctx_std ** 2
        # bound on |g| over the region contexts actually reach (for truncation)
        z = np.random.default_rng(0).standard_normal((20_000, m)) * self.ctx_std
        self.L_f = float(np.quantile(np.abs(self.g(z)), 0.999))
        self.L_fp = float("nan")
        self.rng = np.random.default_rng(run_seed if run_seed is not None else seed + 10_000)

    ctx_mean = 0.0

    def score(self, X):
        return X / self.ctx_std ** 2

    def is_active(self):
        return True

    def draw_arms(self):
        return self.rng.standard_normal((self.K, self.d)) * self.ctx_std

    def index(self, X):
        return X @ self.B

    def mean_rewards(self, X):
        return self.g(self.index(X))

    def pull(self, X, a):
        return float(self.mean_rewards(X)[a] + self.sigma * self.rng.standard_normal())

    def instant_regret(self, X, a):
        mu = self.mean_rewards(X)
        return float(mu.max() - mu[a])
