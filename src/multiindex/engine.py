"""FedZoomMIB -- federated two-phase multi-index bandit (N = 1: single-agent ZoomMIB-UCB).

Same skeleton as FedTwoPhase (src/fed/engine.py); three things change.

  Phase 1   agents explore uniformly for a fixed T0 rounds, then the network
            estimates span(B) from the second-order Stein matrix.  `mi_phase1`:
              exact     each agent uploads the upper triangle of its truncated
                        matrix sum, d(d+1)/2 + 1 scalars; the server's M̂ is the
                        centralised one, B̂ = its top-m eigenvectors
              projavg   each agent uploads its OWN top-m eigenvectors (d·m + 1);
                        the server averages the projectors V_i V_iᵀ (one-shot
                        projection averaging, Fan, Wang, Wang & Zhu 2019)
              power     federated orthogonal iteration from a shared random start,
                        `power_rounds` rounds of d·m up and d·m down per agent
  Freeze    B̂ and the window W = max |B̂ᵀx| over Phase-1 contexts are broadcast.
  Phase 2   sleeping UCB on the m-dimensional cubes of side Δ = c·(NT)^{-1/(m+2)}
            (or c·T^{-1/(m+2)}), flattened to one slot index, so every Phase-2
            strategy in src/fed/phase2/ works unchanged.

Only freeze="fixed" is supported: the adaptive drift rule would need a subspace
drift, which is not needed for the experiments here.
"""

from __future__ import annotations

import numpy as np

from ..fed.engine import FedTwoPhase
from ..fed.phase1.base import FLOAT_BITS
from .stein2 import local_sum, tau2_default, top_m


class FedZoomMIB(FedTwoPhase):
    name = "FedZoomMIB"

    def __init__(self, N, d, K, T, env_info, rng, m=2, mi_phase1="exact", power_rounds=10,
                 bin_width="agent", delta_scale=1.0, **kw):
        if kw.get("freeze", "adaptive") != "fixed":
            raise ValueError("FedZoomMIB needs freeze='fixed' and T0")
        super().__init__(N, d, K, T, env_info, rng, bin_width=bin_width, **kw)
        if mi_phase1 not in ("exact", "projavg", "power"):
            raise ValueError(mi_phase1)
        self.m, self.mi_phase1, self.power_rounds = int(m), mi_phase1, int(power_rounds)
        # Δ = c·(NT)^{-1/(m+2)}: the theory fixes the exponent, not the constant c.
        # With c = 1 an m = 2 grid has ~10⁴ cubes, more than a 10⁴-round run can visit.
        self.Delta = delta_scale * (T * (N if bin_width == "network" else 1)) ** (-1.0 / (self.m + 2))
        self.s2 = env_info["ctx_std"] ** 2
        self._r_power = rng.spawn(1)[0]
        self.B_hat = None
        self.n_side = None

    # ------------------------------------------------------------------
    def _aggregate(self):
        """-> (B̂, scalars, rounds) for the configured Phase-1 strategy."""
        live = [ag for ag in self.agents if ag.n]
        n_pool = sum(ag.n for ag in live)
        tau = (tau2_default(self.sigma, self.L_f, self.s2, n_pool, self.d, self.delta)
               if self.use_truncation else None)
        A = [local_sum(ag.S_buf, ag.y_buf, self.s2, tau) for ag in live]
        n = np.array([ag.n for ag in live], float)
        d, m, L = self.d, self.m, len(live)
        if self.mi_phase1 == "exact":
            B = top_m(sum(A) / n_pool, m)
            return B, L * (d * (d + 1) // 2 + 1) + self.N * d * m, 1
        if self.mi_phase1 == "projavg":
            P = sum(w * (V @ V.T) for w, V in zip(n, (top_m(a / k, m) for a, k in zip(A, n))))
            B = top_m(P / n_pool, m)
            return B, L * (d * m + 1) + self.N * d * m, 1
        V, _ = np.linalg.qr(self._r_power.standard_normal((d, m)))
        for _ in range(self.power_rounds):
            V, _ = np.linalg.qr(sum(a @ V for a in A) / n_pool)
        return V, self.power_rounds * (L + self.N) * d * m, self.power_rounds

    def _finalise(self, theta=None):
        B, scalars, rounds = self._aggregate()
        self._log(scalars, scalars * FLOAT_BITS, phase1=True, rounds=rounds)
        self.B_hat = self.theta_hat = B
        self.T0_used = self.t
        self.T0_samples = [ag.n for ag in self.agents]
        z_max = max(float(np.max(np.abs(np.asarray(ag.X_buf) @ B))) for ag in self.agents if ag.n)
        self.W = max(z_max * self.w_pad, 10.0 * self.Delta)
        self._log(2 * self.N, 2 * self.N * FLOAT_BITS, phase1=True)   # z_max up, W down
        self.n_side = int(np.ceil(2.0 * self.W / self.Delta))
        self.N_bins = self.n_side ** self.m
        self.p2.setup(self.N, self.N_bins + 2)
        self.contrib = np.zeros((self.N, self.N_bins + 2), dtype=np.int64)
        for ag in self.agents:
            ag.S_buf, ag.y_buf, ag.X_buf = [], [], []
        self.ucb_const = self.ucb_scale * self.sigma * np.sqrt(
            2.0 * np.log(2.0 * self.N_bins * self.N * self.T / self.delta))
        self.phase = 2

    def _bins(self, X, i=None):
        Z = X @ self.B_hat
        c = np.clip(np.floor((Z + self.W) / self.Delta).astype(np.int64), 0, self.n_side - 1)
        b = np.ravel_multi_index(c.T, (self.n_side,) * self.m) + 1
        b[np.any(np.abs(Z) > self.W, axis=1)] = -1
        return b

    def diagnostics(self):
        dg = super().diagnostics()
        dg.update(B_hat=self.B_hat, m=self.m, n_side=self.n_side, mi_phase1=self.mi_phase1)
        return dg
