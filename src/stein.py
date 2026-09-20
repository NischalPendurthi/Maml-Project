"""Truncated Stein estimator for the single-index direction.

Stein's identity (Stein 1981; Dey et al. 2026, Section 2.1).  With score
S(x) = -grad log p(x) and y = f(<x, theta_*>) + eta,

    E[ y S(x) ] = E[ f'(<x, theta_*>) ] theta_* = mu_* theta_*

so the direction is recoverable from a *sample mean* -- with no knowledge of
f whatsoever.  Truncation controls the tails of y S(x):

    phi_tau(v)_j = sgn(v_j) min(|v_j|, tau)          (Dey et al. Eq. 1)
    theta_hat    = (1/n) sum_i phi_tau( y_i S(x_i) )
    theta_hat_0  = theta_hat / ||theta_hat||_1        (Lemma 2.1)

That this estimator is an *average* is the single fact the whole federated
extension rests on: averaging local estimators across agents is algebraically
identical to the centralized estimator on pooled data.
"""

from __future__ import annotations

import numpy as np


def truncate(V, tau):
    """Element-wise phi_tau."""
    return np.sign(V) * np.minimum(np.abs(V), tau)


def tau_default(sigma, L_f, M, n, d, delta):
    """Dey et al. Remark 2.3:  tau = sqrt( 3(sigma^2 + L_f^2) M n / log(2d/delta) )."""
    n = max(int(n), 1)
    return float(np.sqrt(3.0 * (sigma ** 2 + L_f ** 2) * M * n / np.log(2.0 * d / delta)))


def stein_estimate(S, y, tau=None, normalize=True):
    """Truncated (and optionally l1-normalized) Stein estimator.

    Parameters
    ----------
    S : (n, d) array of score vectors S(x_i) of the *pulled* arms.
    y : (n,) array of observed rewards.
    tau : truncation threshold; None disables truncation.
    """
    S = np.asarray(S, dtype=float)
    y = np.asarray(y, dtype=float)
    if S.shape[0] == 0:
        raise ValueError("stein_estimate: no samples")
    V = S * y[:, None]
    if tau is not None:
        V = truncate(V, tau)
    theta = V.mean(axis=0)
    if normalize:
        theta = normalize_l1(theta)
    return theta


def normalize_l1(theta):
    nrm = np.abs(theta).sum()
    if nrm <= 0 or not np.isfinite(nrm):
        # degenerate; fall back to a uniform direction rather than NaN
        d = theta.shape[0]
        return np.full(d, 1.0 / d)
    return theta / nrm


def l1_error(theta_hat, theta_star):
    """||theta_hat - theta_*||_1, after resolving the sign ambiguity.

    Stein recovers mu_* theta_*; with mu_* > 0 assumed, the sign is fixed, but
    a finite sample can flip it when the signal is weak.  Reporting the better
    of the two keeps the diagnostic about *direction* accuracy.
    """
    a = np.abs(theta_hat - theta_star).sum()
    b = np.abs(-theta_hat - theta_star).sum()
    return float(min(a, b))
