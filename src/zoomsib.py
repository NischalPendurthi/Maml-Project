"""ZoomSIB-UCB -- Zoomed Single Index Bandit with UCB.

Faithful implementation of Algorithm 1 of

    Devdan Dey, Sujoy Bhore, Avishek Ghosh,
    "Optimal Regret for Single Index Bandits", arXiv:2605.09454, 2026.

Two phases:

  Phase 1 (parameter estimation).  Pull uniformly at random for T_0 rounds and
  form the l1-normalised truncated Stein estimator theta_hat_0.  T_0 is
  calibrated so that ||theta_hat_0 - theta_*||_1 <= Delta / (2L), i.e. the
  estimation error displaces any arm's projected index by at most half a bin.

  Phase 2 (UCB over bins).  Discretise the projected index line [-W, W] into
  N = O(T^{1/3}) bins of width Delta = T^{-1/3}.  Each round, project the K
  presented arms onto theta_hat_0, read off which bins are *available*, and run
  UCB over that available set.

Two subtleties that the implementation must respect:

  * Sample splitting (Remark 3.1).  theta_hat_0 is computed entirely from
    Phase-1 data and then FROZEN.  The bin assignment is then a deterministic,
    F_{t-1}-measurable function of the contexts, which makes the within-bin
    noise a martingale difference sequence.  Continuing to update theta_hat_0
    during Phase 2 would break the analysis.

  * Sleeping bandits.  Only a random subset B_t of bins is available each
    round, because availability depends on where the K freshly drawn arms land.
    UCB must be taken over B_t, and regret measured against the best *available*
    bin -- not over all N bins.

Practical deviations from the theoretical prescription, both taken from the
paper's own experiments (Section 6) and both switchable:

  * `adaptive_stop`.  The theoretical T_0 = d^2 T^{2/3} polylog(dT/delta)
    exceeds the horizon for every T we can simulate.  Dey et al. therefore
    equip ZoomSIB-UCB with an adaptive stopping rule that monitors the
    stability of the parameter estimate and exits Phase 1 once it converges.
    We do the same.

  * `w_mode='empirical'`.  The theoretical W = 4 kappa sqrt(log(TK/delta)) is a
    high-probability envelope; with standard Gaussian contexts and
    ||theta_*||_1 = 1 the projected indices actually live in a range of order
    ||theta_*||_2 << W, so the theoretical W would leave the overwhelming
    majority of bins permanently empty.  We estimate the envelope from Phase-1
    data instead, which keeps N = O(T^{1/3}) as the theory intends.
"""

from __future__ import annotations

import numpy as np

from .base import BanditAlgo
from .stein import normalize_l1, stein_estimate, tau_default, truncate


class ZoomSIBUCB(BanditAlgo):
    name = "ZoomSIB-UCB"

    def __init__(self, d, K, T, env_info, rng,
                 delta=0.01,
                 T0=None,
                 adaptive_stop=True,
                 stop_tol=0.08,
                 stop_patience=2,
                 stop_growth=1.5,
                 min_explore=None,
                 max_explore_frac=0.5,
                 w_mode="empirical",
                 w_pad=1.05,
                 ucb_scale=1.0,
                 use_truncation=True):
        super().__init__(d, K, T, env_info, rng)

        self.delta = delta
        self.sigma = env_info["sigma"]
        self.kappa = env_info["kappa"]
        self.M = env_info["M"]
        self.L_f = env_info["L_f"]
        self.score = env_info["score"]
        self.w_mode, self.w_pad = w_mode, w_pad
        self.ucb_scale = ucb_scale
        self.use_truncation = use_truncation

        # --- constants of Algorithm 1, line 2 -----------------------------
        self.L = 4.0 * self.kappa * np.sqrt(np.log(d * T * K / delta))
        self.W_theory = 4.0 * self.kappa * np.sqrt(np.log(T * K / delta))
        self.Delta = T ** (-1.0 / 3.0)

        # Theoretical T_0 = ceil(d^2 T^{2/3} polylog(dT/delta)); unusable at
        # simulable horizons, hence the cap + adaptive stopping rule.
        self.T0_theory = int(np.ceil(d ** 2 * T ** (2.0 / 3.0)
                                     * np.log(d * T / delta)))
        cap = int(np.ceil(max_explore_frac * T))
        self.T0 = int(min(T0, cap)) if T0 is not None else cap

        self.adaptive_stop = adaptive_stop
        self.stop_tol = stop_tol
        self.stop_patience = stop_patience
        self.stop_growth = stop_growth
        self.min_explore = (min_explore if min_explore is not None
                            else max(50, 5 * d))

        # --- Phase-1 buffers ----------------------------------------------
        self._S_buf, self._y_buf = [], []
        self._prev_theta = None
        self._stable = 0
        self._next_check = self.min_explore

        # --- Phase-2 state (set by _finalise) ------------------------------
        self.phase = 1
        self.theta_hat = None
        self.W = None
        self.N_bins = None
        self.n_j = None
        self.S_j = None
        self.T0_used = None
        self.ucb_const = None

    # ------------------------------------------------------------------
    # Phase 1
    # ------------------------------------------------------------------
    def _current_theta(self):
        S = np.asarray(self._S_buf)
        y = np.asarray(self._y_buf)
        tau = (tau_default(self.sigma, self.L_f, self.M, len(y), self.d, self.delta)
               if self.use_truncation else None)
        return stein_estimate(S, y, tau=tau, normalize=True)

    def _should_stop(self):
        """Adaptive stopping on geometrically spaced checkpoints.

        Both estimates are l1-normalised, so the drift between successive
        checkpoints is already a relative quantity: `stop_tol` is the fraction
        of the l1 mass allowed to move when the sample size grows by
        `stop_growth`.  Since the estimation error decays like 1/sqrt(n), the
        drift across a geometric step also decays like 1/sqrt(n), so this rule
        exits after O(log n) checks -- matching the ~2% exploration fractions
        Dey et al. report in Section 6.
        """
        n = len(self._y_buf)
        if n >= self.T0:
            return True
        if not self.adaptive_stop or n < self._next_check:
            return False
        theta = self._current_theta()
        self._next_check = int(np.ceil(n * self.stop_growth))
        if self._prev_theta is not None:
            drift = float(np.abs(theta - self._prev_theta).sum())
            self._stable = self._stable + 1 if drift < self.stop_tol else 0
        self._prev_theta = theta
        return self._stable >= self.stop_patience

    def _finalise(self):
        """Freeze theta_hat_0 and lay down the bin grid (Algorithm 1, line 7)."""
        self.theta_hat = self._current_theta()
        self.T0_used = len(self._y_buf)

        if self.w_mode == "empirical":
            # Score vectors are x / s^2, so recover the contexts to project.
            X1 = np.asarray(self._S_buf) * self.info["ctx_std"] ** 2
            z = X1 @ self.theta_hat
            self.W = float(np.max(np.abs(z))) * self.w_pad
            self.W = max(self.W, 10.0 * self.Delta)      # never degenerate
        else:
            self.W = float(self.W_theory)

        self.N_bins = int(np.ceil(2.0 * self.W / self.Delta))
        self.n_j = np.zeros(self.N_bins + 2, dtype=np.int64)
        self.S_j = np.zeros(self.N_bins + 2, dtype=float)
        self.ucb_const = self.ucb_scale * self.sigma * np.sqrt(
            2.0 * np.log(2.0 * self.N_bins * self.T / self.delta))

        self._S_buf, self._y_buf = [], []            # free memory
        self.phase = 2

    # ------------------------------------------------------------------
    # Bin bookkeeping
    # ------------------------------------------------------------------
    def _bins(self, X):
        """Project arms and map to bins; -1 marks 'outside the window'."""
        z = X @ self.theta_hat
        b = np.ceil((z + self.W) / self.Delta).astype(np.int64)
        b = np.clip(b, 1, self.N_bins)
        b[np.abs(z) > self.W] = -1
        return b

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def select(self, X):
        if self.phase == 1:
            return self._random_arm()

        b = self._bins(X)
        avail = b >= 0
        if not np.any(avail):                        # B_t empty -> line 13
            return self._random_arm()

        idx = np.flatnonzero(avail)
        bj = b[idx]
        n = self.n_j[bj]
        ucb = np.where(
            n == 0,
            np.inf,
            np.divide(self.S_j[bj], np.maximum(n, 1))
            + self.ucb_const / np.sqrt(np.maximum(n, 1)),
        )
        return int(idx[int(np.argmax(ucb))])

    def update(self, X, a, y):
        self.t += 1
        if self.phase == 1:
            self._S_buf.append(self.score(X[a]))
            self._y_buf.append(y)
            if self._should_stop():
                self._finalise()
            return

        b = self._bins(X)[a]
        if b >= 0:
            self.n_j[b] += 1
            self.S_j[b] += y

    # ------------------------------------------------------------------
    def diagnostics(self):
        return dict(
            T0_used=self.T0_used,
            T0_theory=self.T0_theory,
            N_bins=self.N_bins,
            W=self.W,
            Delta=self.Delta,
            theta_hat=self.theta_hat,
        )


class ZoomSIBOracleTheta(ZoomSIBUCB):
    """Ablation: ZoomSIB-UCB handed the true theta_*, skipping Phase 1.

    Isolates how much of the regret is the cost of *estimating the direction*
    versus the cost of the binned bandit problem itself.  Not a deployable
    policy -- a reference line only.
    """

    name = "ZoomSIB (oracle $\\theta_*$)"

    def __init__(self, *args, theta_star=None, **kw):
        super().__init__(*args, **kw)
        assert theta_star is not None
        self._theta_star = normalize_l1(np.asarray(theta_star, dtype=float))
        self._bootstrap()

    def _bootstrap(self):
        """Lay down the grid immediately, using a pilot sample for W."""
        rng = self.rng
        n_pilot = 2000
        X = rng.standard_normal((n_pilot, self.d)) * self.info["ctx_std"]
        self.theta_hat = self._theta_star
        self.T0_used = 0
        if self.w_mode == "empirical":
            z = X @ self.theta_hat
            self.W = max(float(np.max(np.abs(z))) * self.w_pad, 10.0 * self.Delta)
        else:
            self.W = float(self.W_theory)
        self.N_bins = int(np.ceil(2.0 * self.W / self.Delta))
        self.n_j = np.zeros(self.N_bins + 2, dtype=np.int64)
        self.S_j = np.zeros(self.N_bins + 2, dtype=float)
        self.ucb_const = self.ucb_scale * self.sigma * np.sqrt(
            2.0 * np.log(2.0 * self.N_bins * self.T / self.delta))
        self.phase = 2
