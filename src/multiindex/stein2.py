"""Second-order Stein estimation of the index subspace.

For x ~ N(0, s² I) the second-order score is T(x) = (x xᵀ − s² I) / s⁴ = S Sᵀ − I/s²
with S = x/s², and Stein's identity gives E[y T(x)] = E[∇²f(x)] = B E[∇²g] Bᵀ
(Yang, Balasubramanian, Wang & Liu, NeurIPS 2017).  We truncate y·T(x)
elementwise, as the first-order estimator does, and take the top-m
eigenvectors by |eigenvalue| (E[∇²g] may be negative definite).
"""

from __future__ import annotations

import numpy as np

from ..stein import truncate


def summands(S, y, s2):
    """y_t · T(x_t) for each sample: (n, d, d)."""
    S = np.asarray(S, float)
    T = S[:, :, None] * S[:, None, :] - np.eye(S.shape[1])[None] / s2
    return np.asarray(y, float)[:, None, None] * T


def local_sum(S, y, s2, tau=None):
    V = summands(S, y, s2)
    if tau is not None:
        V = truncate(V, tau)
    return V.sum(axis=0)


def tau2_default(sigma, L_f, s2, n, d, delta):
    """Truncation level for the second-order summands (E[T_ij²] ≤ 2/s⁴ on the diagonal)."""
    return float(np.sqrt(3.0 * (sigma ** 2 + L_f ** 2) * (2.0 / s2 ** 2) * n
                         / np.log(2.0 * d * d / delta)))


def top_m(M, m):
    """Orthonormal basis of the top-m eigenspace of symmetric M, by |eigenvalue|."""
    w, V = np.linalg.eigh((M + M.T) / 2)
    idx = np.argsort(-np.abs(w))[:m]
    return V[:, idx]


def subspace_error(B_hat, B):
    """sin-Θ distance ‖B̂B̂ᵀ − BBᵀ‖₂ ∈ [0, 1]."""
    return float(np.linalg.norm(B_hat @ B_hat.T - B @ B.T, 2))
