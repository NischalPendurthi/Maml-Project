"""event_compressed -- event-triggered sync with a compressed upload.

Same trigger as `event`.  At a sync each agent uploads, for its touched bins,
(index, count, compressed sum-delta).  Counts stay exact: they set the UCB
widths, and a wrong count is worse than a noisy sum.

    compressor = dict(kind="quant", bits=b)   sum-deltas rounded to b bits
               = dict(kind="topk", k=f)       only the fraction f of touched bins with
                                              the largest news ratio dn / max(G_n, 1)
               = dict(kind="randk", k=f)      a random fraction f of touched bins
    ef = True    what is not sent stays in the agent's delta and goes out at a
                 later sync (error feedback); False: it is discarded

Only the upload is compressed; the server's broadcast of the bins it merged is
full precision.  `last_bits` reports the real bit count to the engine.
"""

from __future__ import annotations

import numpy as np

from ..compress import FLOAT_BITS, _k_of, quantize
from .base import PER_BIN
from .event import EventTriggered


class EventCompressed(EventTriggered):
    name = "event_compressed"

    def __init__(self, gamma=0.5, compressor=None, ef=True, seed=0):
        super().__init__(gamma)
        self.spec = compressor or {"kind": "none"}
        self.ef = bool(ef)
        self.rng = np.random.default_rng(seed)
        self.last_bits = None

    def end_round(self, t):
        self.last_bits = None
        return super().end_round(t)

    def sync(self):
        kind = self.spec.get("kind", "none")
        send_n = np.zeros_like(self.dn)
        send_S = np.zeros_like(self.dS)
        bits = 0
        for i in range(self.N):
            idx = np.flatnonzero(self.dn[i])
            if idx.size == 0:
                continue
            if kind in ("topk", "randk"):
                k = _k_of(self.spec["k"], idx.size)
                if kind == "topk":       # the bins whose news moves the shared table most
                    news = self.dn[i, idx] / np.maximum(self.G_n[idx], 1)
                    keep = idx[np.argsort(-news, kind="stable")[:k]]
                else:
                    keep = self.rng.choice(idx, size=k, replace=False)
                send_n[i, keep] = self.dn[i, keep]
                send_S[i, keep] = self.dS[i, keep]
                bits += PER_BIN * k * FLOAT_BITS
            elif kind == "quant":
                q, b = quantize(self.dS[i, idx], self.spec["bits"], self.rng)
                send_n[i, idx] = self.dn[i, idx]
                send_S[i, idx] = q
                bits += 2 * idx.size * FLOAT_BITS + b      # index + count exact, sums b bits
            else:
                send_n[i, idx] = self.dn[i, idx]
                send_S[i, idx] = self.dS[i, idx]
                bits += PER_BIN * idx.size * FLOAT_BITS
        merged = (send_n > 0).any(axis=0)
        down = PER_BIN * int(merged.sum()) * self.N
        bits += down * FLOAT_BITS
        self.G_n += send_n.sum(axis=0)
        self.G_S += send_S.sum(axis=0)
        if self.ef:
            self.dn -= send_n
            self.dS -= send_S                 # unsent bins and rounding residuals stay local
        else:
            self.dn[:] = 0
            self.dS[:] = 0.0
        self.last_bits = int(bits)
        return int(np.ceil(bits / FLOAT_BITS))
