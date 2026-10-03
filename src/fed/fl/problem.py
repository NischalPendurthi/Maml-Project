"""The federated least-squares problem that BOTH phases reduce to.

Client i holds a PSD matrix H_i, a vector b_i and a sample count n_i, and its
per-sample local loss is

    F_i(w) = ( ½ wᵀ H_i w − b_iᵀ w ) / n_i .

The global objective is the sample-weighted average F = Σ_i p_i F_i with
p_i = n_i / Σ_k n_k, whose minimiser is the POOLED -- i.e. centralised --
estimator

    w* = ( Σ_i H_i )⁻¹ Σ_i b_i .

How each phase fits:

  Phase 1, Stein   H_i = n_i I,          b_i = Σ_t φτ(y_t S(x_t))   (identical
                   per-sample Hessians: no client heterogeneity at all)
  Phase 1, LS      H_i = X_iᵀX_i (+ridge), b_i = X_iᵀ y              (Hessians
                   differ by sampling noise and by covariate shift)
  Phase 2, bins    H_i = diag(n_ij),     b_i = (S_ij)_j             (per-bin
                   counts differ wildly across agents: strong heterogeneity)

Every FL method in src/fed/fl/ is an algorithm for this one problem, so the
same code runs in either phase and its distance to w* is directly measurable.
"""

from __future__ import annotations

import numpy as np


class FedQuadratic:
    """N clients' (H_i, b_i, n_i).

    H          (N, D) when `diag`, else (N, D, D)
    b          (N, D)
    n          (N,) sample counts; clients with n_i = 0 are inactive
    isotropic  H_i = n_i I exactly (Phase-1 Stein); lets methods send D+1 numbers
    touched    (N, D) bool -- coordinates with new data since the last
               communication (sparse uploads in Phase 2); default: support of H
    new_samples (N,) samples since the last communication (split learning cost)
    sample_cost scalars one raw sample / activation costs to send
    """

    def __init__(self, H, b, n, *, diag, isotropic=False, touched=None,
                 new_samples=None, sample_cost=1):
        self.H = np.asarray(H, dtype=float)
        self.b = np.asarray(b, dtype=float)
        self.n = np.asarray(n, dtype=float)
        self.diag = bool(diag)
        self.isotropic = bool(isotropic)
        self.N, self.D = self.b.shape
        self.active = self.n > 0
        tot = self.n.sum()
        self.p = self.n / tot if tot > 0 else np.zeros(self.N)
        self.touched = touched if touched is not None else self.support()
        self.new_samples = new_samples if new_samples is not None else self.n.copy()
        self.sample_cost = sample_cost
        self._nn = np.maximum(self.n, 1.0)

    # -- local losses ------------------------------------------------------
    def support(self):
        """(N, D) coordinates each client has information about."""
        if self.diag:
            return self.H > 0
        return np.repeat(self.active[:, None], self.D, axis=1)

    def A(self):
        """Per-sample Hessians H_i / n_i."""
        if self.diag:
            return self.H / self._nn[:, None]
        return self.H / self._nn[:, None, None]

    def grad(self, W):
        """∇F_i at each client's own point W[i]; zero for inactive clients."""
        W = np.broadcast_to(W, (self.N, self.D))
        if self.diag:
            G = self.H * W - self.b
        else:
            G = np.einsum("nij,nj->ni", self.H, W) - self.b
        G = G / self._nn[:, None]
        G[~self.active] = 0.0
        return G

    def smoothness(self):
        """(N,) largest eigenvalue of each client's per-sample Hessian."""
        if self.isotropic:
            return self.active.astype(float)
        A = self.A()
        if self.diag:
            return A.max(axis=1)
        return np.array([np.linalg.eigvalsh(a)[-1] if act else 0.0
                         for a, act in zip(A, self.active)])

    def L_max(self):
        L = self.smoothness()[self.active]
        return float(L.max()) if L.size else 1.0

    def global_smoothness(self):
        """Largest eigenvalue of the global per-sample Hessian Σ p_i A_i."""
        if self.isotropic:
            return 1.0
        A = (self.p[:, None] * self.A()).sum(0) if self.diag else \
            np.einsum("n,nij->ij", self.p, self.A())
        return float(A.max()) if self.diag else float(np.linalg.eigvalsh(A)[-1])

    # -- optima -------------------------------------------------------------
    def pooled(self, fallback):
        """Centralised optimum; coordinates nobody has data on keep `fallback`."""
        Hs, bs = self.H.sum(0), self.b.sum(0)
        if self.isotropic:
            return bs / self.n.sum()
        if self.diag:
            return np.where(Hs > 0, bs / np.where(Hs > 0, Hs, 1.0), fallback)
        return np.linalg.solve(Hs + 1e-12 * np.eye(self.D), bs)

    def local_opt(self, anchor, mu=1e-9):
        """(N, D) minimisers of F_i(w) + mu/2 ‖w − anchor‖² (local training to convergence)."""
        anchor = np.broadcast_to(anchor, (self.N, self.D))
        bn = self.b / self._nn[:, None]
        if self.diag:
            A = self.A()
            out = (bn + mu * anchor) / (A + mu)
        else:
            A = self.A() + mu * np.eye(self.D)[None]
            out = np.linalg.solve(A, (bn + mu * anchor)[..., None])[..., 0]
        out[~self.active] = anchor[~self.active]
        return out

    def objective_gap(self, w):
        """F(w) − F(w*): the optimisation error of a federated solution."""
        w_star = self.pooled(w)
        def F(v):
            if self.diag:
                return float(np.sum(0.5 * self.H.sum(0) * v ** 2 - self.b.sum(0) * v))
            return float(0.5 * v @ self.H.sum(0) @ v - self.b.sum(0) @ v)
        return (F(w) - F(w_star)) / max(self.n.sum(), 1.0)
