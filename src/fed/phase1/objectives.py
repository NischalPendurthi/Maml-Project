"""Phase-1 data -> the federated least-squares problem `FedQuadratic`.

  stein  F_i(w) = ½‖w‖² − ⟨w, mean_t φτ(y_t S_i(x_t))⟩      H_i = n_i I
         Its pooled optimum IS the truncated Stein estimator.  Every client has
         the same per-sample Hessian, so the problem carries no client
         heterogeneity whatsoever, whatever the data look like.

  ls     F_i(w) = (1/2n_i) Σ_t (y_t − ⟨x̃_t, w⟩)² + ridge,   x̃ = x − m_i
         ("Stein with an estimated covariance": for Gaussian contexts its
         population optimum is Σ⁻¹E[x̃ y] = E[S(x) y], the same target).  Here
         H_i = X̃_iᵀX̃_i differs across clients, so client drift CAN appear --
         the regime the drift-correcting FL methods were designed for.

Both use each agent's OWN score / context mean, as an agent would.
"""

from __future__ import annotations

import numpy as np

from ..fl.problem import FedQuadratic
from .base import local_V, truncated


def stein_problem(agents, tau, n_sent=None):
    d = next(len(ag.S_buf[0]) for ag in agents if ag.n)
    n = np.array([ag.n for ag in agents], float)
    b = np.zeros((len(agents), d))
    for i, ag in enumerate(agents):
        if ag.n:
            b[i] = truncated(local_V(ag), tau).sum(axis=0)
    H = n[:, None, None] * np.eye(d)[None]
    new = n - (n_sent if n_sent is not None else 0)
    return FedQuadratic(H, b, n, diag=False, isotropic=True, new_samples=new, sample_cost=d)


def ls_problem(agents, ridge=1e-3, n_sent=None):
    d = next(len(ag.S_buf[0]) for ag in agents if ag.n)
    N = len(agents)
    n = np.array([ag.n for ag in agents], float)
    H = np.zeros((N, d, d))
    b = np.zeros((N, d))
    for i, ag in enumerate(agents):
        if ag.n:
            Xc = np.asarray(ag.S_buf) * ag.info["ctx_std"] ** 2      # x − m_i
            y = np.asarray(ag.y_buf)
            H[i] = Xc.T @ Xc + ridge * ag.n * ag.info["ctx_std"] ** 2 * np.eye(d)
            b[i] = Xc.T @ y
    new = n - (n_sent if n_sent is not None else 0)
    return FedQuadratic(H, b, n, diag=False, new_samples=new, sample_cost=d + 1)
