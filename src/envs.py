"""Single-index bandit environment.

Model (Dey, Bhore & Ghosh 2026, arXiv:2605.09454, Section 2):

    at round t the learner sees K arms  X_t = {x_{t,a}}_{a in [K]}, drawn i.i.d.
    from a continuous density p on R^d; it pulls x_t and observes

        y_t = f(<x_t, theta_*>) + eta_t,     eta_t  sigma-sub-Gaussian

with BOTH theta_* and the link f unknown to the learner.  Identifiability is
fixed by ||theta_*||_1 = 1 (scale) and mu_* = E[f'(<X,theta_*>)] > 0 (sign).

Contexts are standard Gaussian, as in the paper's experiments, so the score
function is available in closed form:

    p(x) = N(0, s^2 I)   =>   S(x) = -grad log p(x) = x / s^2

The learner is *allowed* to know S (equivalently p).  This assumption is
inherited from the whole single-index-bandit literature -- Stein's identity
needs the score -- and is stated explicitly rather than hidden.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# Link functions.  The three non-monotone shapes are exactly those used in
# Dey et al. Section 6; `logistic` is added as a monotone control, where a
# monotonicity-assuming algorithm (ESTOR) ought to win.
# --------------------------------------------------------------------------

LINKS = {
    "quadratic":  lambda z: -(z - 1.0) ** 2 + 1.0,
    "asymmetric": lambda z: z * np.exp(-(z ** 2)),
    "zigzag":     lambda z: np.sin(z) + 0.3 * z,
    "logistic":   lambda z: 1.0 / (1.0 + np.exp(-z)),
}

MONOTONE = {"quadratic": False, "asymmetric": False, "zigzag": False, "logistic": True}

LINK_LABEL = {
    "quadratic":  r"$f(z)=-(z-1)^2+1$",
    "asymmetric": r"$f(z)=z\,e^{-z^2}$",
    "zigzag":     r"$f(z)=\sin z+0.3z$",
    "logistic":   r"$f(z)=1/(1+e^{-z})$",
}


def link_constants(link: str, z_max: float = 6.0, n_grid: int = 20001):
    """Numerically bound |f| and |f'| on [-z_max, z_max].

    These are the L_f and L_{f'} of Assumption 3; the algorithm uses them only
    to set the Stein truncation threshold, so loose bounds are harmless.
    """
    f = LINKS[link]
    z = np.linspace(-z_max, z_max, n_grid)
    fz = f(z)
    L_f = float(np.max(np.abs(fz)))
    L_fp = float(np.max(np.abs(np.gradient(fz, z))))
    return L_f, L_fp


class SIBEnv:
    """A single-index bandit instance.

    Parameters
    ----------
    d, K        : context dimension and number of arms presented per round.
    link        : key into LINKS.
    sigma       : sub-Gaussian noise scale.
    seed        : seeds theta_* (the problem instance).
    run_seed    : seeds contexts and noise (the realisation).  Pass a different
                  value per trial to average over both instance and noise.
    index_scale : if None (default, and faithful to the paper) contexts are
                  standard Gaussian, so the index std is ||theta_*||_2 and
                  therefore shrinks like 1/sqrt(d).  If a float is given, the
                  context std is chosen so that Var(<x,theta_*>) equals that
                  value, holding problem difficulty fixed across d.
    """

    def __init__(self, d, K, link="quadratic", sigma=0.1, seed=0,
                 run_seed=None, index_scale=None):
        self.d, self.K, self.link_name, self.sigma = d, K, link, sigma
        self.f = LINKS[link]
        self.monotone = MONOTONE[link]

        inst_rng = np.random.default_rng(seed)
        g = inst_rng.standard_normal(d)
        self.theta_star = g / np.abs(g).sum()          # ||theta_*||_1 = 1
        theta_l2 = float(np.linalg.norm(self.theta_star))

        if index_scale is None:
            self.ctx_std = 1.0                          # standard Gaussian contexts
        else:
            self.ctx_std = float(index_scale) / theta_l2
        self.index_std = self.ctx_std * theta_l2        # std of <x, theta_*>

        # Quantities the algorithms are allowed to know.
        self.kappa = self.ctx_std                       # coordinate sub-Gaussian param
        self.M = 1.0 / self.ctx_std ** 2                # E[S_j(X)^2]
        self.L_f, self.L_fp = link_constants(link, z_max=6.0 * max(self.index_std, 1e-3))

        self.rng = np.random.default_rng(
            run_seed if run_seed is not None else seed + 10_000
        )

    # -- the learner is allowed to know the score function ------------------
    def score(self, X):
        """S(x) = -grad log p(x) = x / s^2, applied row-wise."""
        return X / self.ctx_std ** 2

    # -- environment dynamics ----------------------------------------------
    def draw_arms(self):
        return self.rng.standard_normal((self.K, self.d)) * self.ctx_std

    def index(self, X):
        return X @ self.theta_star

    def mean_rewards(self, X):
        return self.f(self.index(X))

    def pull(self, X, a):
        return float(self.mean_rewards(X)[a] + self.sigma * self.rng.standard_normal())

    def instant_regret(self, X, a):
        mu = self.mean_rewards(X)
        return float(mu.max() - mu[a])

    def mu_star(self, n=200_000, seed=0):
        """mu_* = E[f'(<X,theta_*>)]; used only for diagnostics."""
        rng = np.random.default_rng(seed)
        z = rng.standard_normal(n) * self.index_std
        h = 1e-4
        return float(np.mean((self.f(z + h) - self.f(z - h)) / (2 * h)))
