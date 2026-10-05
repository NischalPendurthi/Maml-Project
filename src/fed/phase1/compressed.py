"""compressed -- `exact` with the upload passed through any compressor.

Each agent sends its mean truncated summand m (as in `quantized`), compressed
by `src/fed/compress.py`: quantisation, top-k or rand-k.  Plus its count at
full precision.  Phase 1 sends one message per checkpoint, recomputed from
scratch, so there is no residual to feed back.
"""

from __future__ import annotations

import numpy as np

from ...stein import normalize_l1
from ..compress import FLOAT_BITS, compress
from .base import Phase1Strategy, local_V, truncated


class CompressedStein(Phase1Strategy):
    name = "compressed"

    def __init__(self, rng=None, compressor=None):
        super().__init__(rng)
        self.spec = compressor

    def aggregate(self, agents, tau_fn):
        live = [ag for ag in agents if ag.n]
        tau = tau_fn(sum(ag.n for ag in live))
        means, wts, bits = [], [], 0
        for ag in live:
            m = truncated(local_V(ag), tau).mean(axis=0)
            c, b = compress(m, self.spec, self.rng)
            means.append(c)
            wts.append(ag.n)
            bits += b + FLOAT_BITS                       # + the count
        est = np.average(np.array(means), axis=0, weights=np.array(wts, float))
        return normalize_l1(est), int(np.ceil(bits / FLOAT_BITS)), bits
