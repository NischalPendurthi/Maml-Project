"""quantized -- `exact` with a compressed upload.

Each agent sends its mean truncated summand m, stochastically rounded to `bits`
bits per coordinate on [-s, s] with s = max_j |m_j| sent alongside in full
precision (QSGD-style scaling).  Stochastic rounding is unbiased, so the pooled
estimate stays unbiased; it only gets noisier as the bit budget shrinks -- a
clean communication/accuracy knob.

Why not quantise on [-tau, tau], where truncated summands provably live?
Because tau grows like sqrt(n) and, with a large L_f, sits orders of magnitude
above the MEAN: the rounding noise then swamps the signal and grows with n.
exp07 measured exactly that failure before this scaling was adopted.
"""

from __future__ import annotations

import numpy as np

from ...stein import normalize_l1
from .base import FLOAT_BITS, Phase1Strategy, local_V, truncated


class QuantizedStein(Phase1Strategy):
    name = "quantized"

    def __init__(self, rng=None, bits=4):
        super().__init__(rng)
        self.bits = int(bits)

    def _quantize(self, v, bound):
        levels = 2 ** self.bits - 1
        u = (np.clip(v, -bound, bound) + bound) / (2 * bound) * levels
        q = np.floor(u)
        q += self.rng.random(v.shape) < (u - q)
        return -bound + q / levels * (2 * bound)

    def aggregate(self, agents, tau_fn):
        n_pool = len(agents) * len(agents[0].y_buf)
        tau = tau_fn(n_pool)
        means = []
        for ag in agents:
            m = truncated(local_V(ag), tau).mean(axis=0)
            scale = float(np.abs(m).max()) or 1.0
            means.append(self._quantize(m, scale))
        d = means[0].shape[0]
        # quantised coordinates + scale + count at full precision
        bits = len(agents) * (d * self.bits + 2 * FLOAT_BITS)
        return normalize_l1(np.mean(means, axis=0)), len(agents) * (d + 2), bits
