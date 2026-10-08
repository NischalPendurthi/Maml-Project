"""Sign-invariant pooling of Stein estimates, for agents whose slopes differ in sign.

Agent i's truncated Stein mean estimates μ_i θ*, with μ_i = E_i[f'(<x, θ*>)] the
average slope of f over ITS OWN contexts.  Under covariate shift on a
non-monotone f, μ_i changes sign across agents, so the pooled sum (`exact`)
estimates μ̄ θ*, μ̄ = Σ n_i μ_i / Σ n_i, which cancels when the agents are
balanced around the peak.  Both strategies here target a quantity that cannot
cancel, Σ n_i μ_i² θ* θ*ᵀ:

    aligned  the simple fix.  Each agent uploads its mean v_i (d + 1 scalars, as
             `exact`).  The server takes the top eigenvector of Σ n_i v_i v_iᵀ as a
             pilot, flips every v_i to agree with it, and sums.  Noisy v_i can be
             flipped the wrong way when an agent has few samples.
    outer    the unbiased version.  Each agent splits its samples into halves and
             uploads both half-means (2d + 1 scalars).  Σ n_i sym(v_i⁽¹⁾ v_i⁽²⁾ᵀ) has
             expectation ∝ Σ n_i μ_i² θ*θ*ᵀ with no noise term, because the halves
             are independent; θ̂ is its top eigenvector.

The returned direction is defined up to sign; the bin grid is symmetric, so a
flipped θ̂ only mirrors the index line.
"""

from __future__ import annotations

import numpy as np

from ...stein import normalize_l1
from .base import FLOAT_BITS, Phase1Strategy, local_V, truncated


def _top(M):
    w, V = np.linalg.eigh((M + M.T) / 2)
    return V[:, int(np.argmax(w))]


class AlignedStein(Phase1Strategy):
    name = "aligned"

    def aggregate(self, agents, tau_fn):
        live = [ag for ag in agents if ag.n]
        tau = tau_fn(sum(ag.n for ag in live))
        v = np.array([truncated(local_V(ag), tau).mean(axis=0) for ag in live])
        n = np.array([ag.n for ag in live], float)
        pilot = _top((v * n[:, None]).T @ v)
        s = np.where(v @ pilot >= 0, 1.0, -1.0)
        est = (n * s) @ v
        k = len(live) * (v.shape[1] + 1)
        return normalize_l1(est), k, k * FLOAT_BITS


class OuterStein(Phase1Strategy):
    name = "outer"

    def aggregate(self, agents, tau_fn):
        live = [ag for ag in agents if ag.n >= 2]
        tau = tau_fn(sum(ag.n for ag in live))
        d = np.asarray(live[0].S_buf).shape[1]
        M = np.zeros((d, d))
        for ag in live:
            V = truncated(local_V(ag), tau)
            h = len(V) // 2
            a, b = V[:h].mean(axis=0), V[h:].mean(axis=0)
            M += ag.n * (np.outer(a, b) + np.outer(b, a)) / 2
        k = len(live) * (2 * d + 1)
        return normalize_l1(_top(M)), k, k * FLOAT_BITS
