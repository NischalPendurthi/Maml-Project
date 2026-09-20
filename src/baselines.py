"""Baselines for the single-index bandit.

All five exist in the literature; none is novel.  They are here to make the
ZoomSIB-UCB curve interpretable.

  RandomPolicy   sanity floor.
  LinUCB         Abbasi-Yadkori, Pal & Szepesvari (2011).  Assumes the reward
                 is LINEAR in x; on a non-monotone link it is misspecified and
                 should incur linear regret -- the point of Ghosh, Chowdhury &
                 Gopalan (2017).
  ESTOR          Kang et al. (ICLR 2026).  Assumes f is monotone increasing, so
                 the best arm is simply argmax <x, theta_hat> and f never needs
                 to be estimated.  Should win on `logistic` and fail badly on
                 `quadratic` / `zigzag`.
  GSTOR          Kang et al. (ICLR 2026).  Monotonicity-agnostic: explore for
                 ~T^{3/4} rounds, estimate theta by Stein, estimate f by kernel
                 smoothing on the projected index, then commit.  The Õ(T^{3/4})
                 competitor that ZoomSIB-UCB improves on.
  IGPUCB         Chowdhury & Gopalan (ICML 2017).  Models the reward as an RKHS
                 function of the full d-dimensional context, ignoring the
                 single-index structure entirely; should degrade as d grows.

ESTOR and GSTOR are OUR reimplementations following the templates described in
Kang et al.; reference code is not publicly available, so exploration schedules
are set to the rates the paper's analysis prescribes (O(sqrt(T)) and
O(T^{3/4}) respectively) with the constants exposed as arguments.  They are
intended as faithful-in-spirit strong baselines, not bit-exact reproductions.
"""

from __future__ import annotations

import numpy as np

from .base import BanditAlgo
from .stein import stein_estimate, tau_default


# ----------------------------------------------------------------------
class RandomPolicy(BanditAlgo):
    name = "Random"

    def select(self, X):
        return self._random_arm()

    def update(self, X, a, y):
        self.t += 1


# ----------------------------------------------------------------------
class LinUCB(BanditAlgo):
    """OFUL / LinUCB with a ridge-regularised least-squares estimate."""

    name = "LinUCB"

    def __init__(self, d, K, T, env_info, rng, lam=1.0, delta=0.01, ucb_scale=1.0):
        super().__init__(d, K, T, env_info, rng)
        self.lam = lam
        self.delta = delta
        self.ucb_scale = ucb_scale
        self.V = lam * np.eye(d)
        self.Vinv = np.eye(d) / lam
        self.b = np.zeros(d)
        self.theta = np.zeros(d)

    def _beta(self):
        sigma = self.info["sigma"]
        return self.ucb_scale * (
            sigma * np.sqrt(self.d * np.log((1.0 + self.t / self.lam) / self.delta))
            + np.sqrt(self.lam)
        )

    def select(self, X):
        mu = X @ self.theta
        # width_a = sqrt(x_a^T V^{-1} x_a)
        w = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", X, self.Vinv, X), 0.0))
        return int(np.argmax(mu + self._beta() * w))

    def update(self, X, a, y):
        self.t += 1
        x = X[a]
        self.V += np.outer(x, x)
        # Sherman-Morrison rank-1 update of the inverse
        Vx = self.Vinv @ x
        self.Vinv -= np.outer(Vx, Vx) / (1.0 + float(x @ Vx))
        self.b += y * x
        self.theta = self.Vinv @ self.b


# ----------------------------------------------------------------------
class ESTOR(BanditAlgo):
    """Monotone-assuming single-index bandit (Kang et al. 2026, ESTOR template).

    Forced uniform exploration on an O(sqrt(t)) schedule supplies i.i.d.
    context samples for the Stein estimator (Stein's identity needs x ~ D, so
    only forced-exploration rounds may be used); all other rounds play the
    greedy rule argmax_a <x_a, theta_hat>, which is optimal *if and only if* f
    is increasing.
    """

    name = "ESTOR"

    def __init__(self, d, K, T, env_info, rng, delta=0.01, explore_const=1.0,
                 refit_every=25, use_truncation=True):
        super().__init__(d, K, T, env_info, rng)
        self.delta = delta
        self.explore_const = explore_const
        self.refit_every = refit_every
        self.use_truncation = use_truncation
        self._S, self._y = [], []
        self.theta = None
        self._pending_explore = False

    def _budget(self):
        return int(np.ceil(self.explore_const * self.d * np.sqrt(max(self.t, 1))))

    def select(self, X):
        if len(self._y) < self._budget() or self.theta is None:
            self._pending_explore = True
            return self._random_arm()
        self._pending_explore = False
        return int(np.argmax(X @ self.theta))

    def update(self, X, a, y):
        self.t += 1
        if self._pending_explore:
            self._S.append(self.info["score"](X[a]))
            self._y.append(y)
            n = len(self._y)
            if n >= max(20, 2 * self.d) and (n % self.refit_every == 0 or self.theta is None):
                tau = (tau_default(self.info["sigma"], self.info["L_f"], self.info["M"],
                                   n, self.d, self.delta) if self.use_truncation else None)
                self.theta = stein_estimate(np.asarray(self._S), np.asarray(self._y),
                                            tau=tau, normalize=True)


# ----------------------------------------------------------------------
class GSTOR(BanditAlgo):
    """Shape-agnostic explore-then-commit single-index bandit (Kang et al. 2026).

    Explore uniformly for n_e = O(sqrt(d) T^{3/4}) rounds, estimate theta_* by
    Stein, then estimate the link by Nadaraya-Watson kernel regression of y on
    the projected index z = <x, theta_hat>, and commit to argmax_a f_hat(z_a).

    The rigid O(T^{3/4}) exploration prefix is exactly what Dey et al. point to
    as GSTOR's weakness.
    """

    name = "GSTOR"

    def __init__(self, d, K, T, env_info, rng, delta=0.01, explore_const=1.0,
                 max_explore_frac=0.9, bandwidth=None, use_truncation=True,
                 grid_size=4096):
        super().__init__(d, K, T, env_info, rng)
        self.delta = delta
        n_e = int(np.ceil(explore_const * np.sqrt(d) * T ** 0.75))
        self.n_explore = int(min(n_e, np.ceil(max_explore_frac * T)))
        self.use_truncation = use_truncation
        self.bandwidth = bandwidth
        self.grid_size = int(grid_size)
        self._S, self._y = [], []
        self.theta = None
        self._z_tr = None
        self._y_tr = None
        self._h = None
        self._grid = None
        self._grid_vals = None

    def _fit(self):
        n = len(self._y)
        tau = (tau_default(self.info["sigma"], self.info["L_f"], self.info["M"],
                           n, self.d, self.delta) if self.use_truncation else None)
        self.theta = stein_estimate(np.asarray(self._S), np.asarray(self._y),
                                    tau=tau, normalize=True)
        X = np.asarray(self._S) * self.info["ctx_std"] ** 2      # recover contexts
        self._z_tr = X @ self.theta
        self._y_tr = np.asarray(self._y)
        if self.bandwidth is not None:
            self._h = float(self.bandwidth)
        else:                                                     # Silverman's rule
            s = float(np.std(self._z_tr))
            self._h = max(1.06 * s * n ** (-0.2), 1e-6)
        self._S, self._y = [], []
        self._build_grid()

    def _nw_exact(self, z):
        """Nadaraya-Watson with a Gaussian kernel, evaluated directly."""
        u = (z[:, None] - self._z_tr[None, :]) / self._h
        w = np.exp(-0.5 * u ** 2)
        den = w.sum(axis=1)
        num = w @ self._y_tr
        return np.divide(num, den, out=np.zeros_like(num), where=den > 1e-12)

    def _build_grid(self):
        """Tabulate the (now frozen) link estimate once.

        GSTOR is explore-then-commit: after the exploration prefix the kernel
        regression never changes again.  Evaluating it exactly on every one of
        the remaining rounds costs O(K n) per round with n ~ T^{3/4}, which
        dominates the entire experiment budget for no statistical benefit.  We
        instead tabulate f_hat once on a dense grid and linearly interpolate,
        which is the same estimator up to a grid resolution far finer than the
        kernel bandwidth.
        """
        lo = float(self._z_tr.min()) - 4.0 * self._h
        hi = float(self._z_tr.max()) + 4.0 * self._h
        self._grid = np.linspace(lo, hi, self.grid_size)
        vals = np.empty(self.grid_size)
        step = 512                                   # bound peak memory
        for i in range(0, self.grid_size, step):
            vals[i:i + step] = self._nw_exact(self._grid[i:i + step])
        self._grid_vals = vals

    def _f_hat(self, z):
        # np.interp clamps outside the grid, which matches the plateau that
        # Nadaraya-Watson produces beyond the support of the training indices.
        return np.interp(z, self._grid, self._grid_vals)

    def select(self, X):
        if self.theta is None:
            return self._random_arm()
        return int(np.argmax(self._f_hat(X @ self.theta)))

    def update(self, X, a, y):
        self.t += 1
        if self.theta is None:
            self._S.append(self.info["score"](X[a]))
            self._y.append(y)
            if len(self._y) >= self.n_explore:
                self._fit()


# ----------------------------------------------------------------------
class IGPUCB(BanditAlgo):
    """IGP-UCB (Chowdhury & Gopalan 2017) with an RBF kernel on R^d.

    Models the reward as an arbitrary RKHS function of the FULL context, so it
    never exploits the single-index structure.  Included to show what that
    costs as d grows.

    Two standard practical approximations, both switchable: the posterior is
    refreshed every `refit_every` rounds rather than every round, and the
    conditioning set is capped at `max_points` (uniformly subsampled from all
    observations) to keep the Cholesky factorisation affordable.
    """

    name = "IGP-UCB"

    def __init__(self, d, K, T, env_info, rng, delta=0.01, lengthscale=None,
                 lam=None, refit_every=25, max_points=400, ucb_scale=1.0):
        super().__init__(d, K, T, env_info, rng)
        self.delta = delta
        self.refit_every = refit_every
        self.max_points = max_points
        self.ucb_scale = ucb_scale
        self.lam = lam if lam is not None else max(env_info["sigma"] ** 2, 1e-4)
        # median-heuristic-style default for standard Gaussian contexts
        self.ell = (lengthscale if lengthscale is not None
                    else np.sqrt(2.0 * d) * env_info["ctx_std"])
        # Preallocate rather than append to a Python list: the conditioning set
        # is rebuilt every refit, and re-running np.asarray over a 20k-element
        # list of tiny arrays each time costs more than the linear algebra.
        self._X = np.empty((T, d))
        self._y = np.empty(T)
        self._n = 0
        self._Xtr = None
        self._Kinv = None
        self._alpha = None

    def _k(self, A, B):
        d2 = (np.sum(A ** 2, axis=1)[:, None]
              + np.sum(B ** 2, axis=1)[None, :]
              - 2.0 * A @ B.T)
        return np.exp(-np.maximum(d2, 0.0) / (2.0 * self.ell ** 2))

    def _refit(self):
        n = self._n
        X, y = self._X[:n], self._y[:n]
        if n > self.max_points:
            idx = self.rng.choice(n, self.max_points, replace=False)
            X, y = X[idx], y[idx]
        Kmat = self._k(X, X) + self.lam * np.eye(X.shape[0])
        # Invert once per refit so that the per-round posterior variance is a
        # matmul rather than an O(n^3) solve -- the latter, repeated every
        # round, dominates the whole experiment budget.
        try:
            Kinv = np.linalg.inv(Kmat)
        except np.linalg.LinAlgError:
            Kinv = np.linalg.inv(Kmat + 1e-6 * np.eye(X.shape[0]))
        self._Xtr = X
        self._Kinv = Kinv
        self._alpha = Kinv @ y

    def _beta(self):
        # Practical surrogate for B + sigma sqrt(2(gamma_t + 1 + log(1/delta))).
        return self.ucb_scale * np.sqrt(2.0 * np.log(
            max(self.K, 2) * (self.t + 1) ** 2 / self.delta))

    def select(self, X):
        if self._alpha is None:
            return self._random_arm()
        ks = self._k(X, self._Xtr)                     # (K, n)
        mu = ks @ self._alpha
        var = np.maximum(1.0 - np.einsum("ij,ij->i", ks @ self._Kinv, ks), 0.0)
        return int(np.argmax(mu + self._beta() * np.sqrt(var)))

    def update(self, X, a, y):
        self.t += 1
        if self._n < self._X.shape[0]:
            self._X[self._n] = X[a]
            self._y[self._n] = y
            self._n += 1
        n = self._n
        if n >= max(10, self.d) and (self._alpha is None or n % self.refit_every == 0):
            self._refit()
