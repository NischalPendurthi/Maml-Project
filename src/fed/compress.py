"""Message compressors for the communication experiments (exp24; the compression grid exp26 is on branch research/claims-evidence).

Each compressor maps a vector v to (decoded vector, bits on the wire).  Bits
are counted honestly: a full-precision scalar is FLOAT_BITS, an index is
FLOAT_BITS too (the same convention as every uncompressed strategy, so savings
come only from what the compressor drops or rounds).

    quant  stochastic uniform quantisation to `bits` bits per coordinate on
           [-s, s], s = max|v| sent in full precision (QSGD-style; unbiased)
    topk   keep the k largest |v_j|, send (index, value) pairs (biased, contractive)
    randk  keep k uniformly random coordinates, rescaled by d/k (unbiased)
    none   identity

`ErrorFeedback` keeps what a compressor dropped and adds it to the next message
(Stich et al. 2018; Karimireddy et al. 2019).
"""

from __future__ import annotations

import numpy as np

FLOAT_BITS = 32


def quantize(v, bits, rng, scale=None):
    v = np.asarray(v, dtype=float)
    s = float(np.abs(v).max()) if scale is None else float(scale)
    if s == 0.0 or v.size == 0:
        return np.zeros_like(v), v.size * bits + FLOAT_BITS
    levels = 2 ** int(bits) - 1
    u = (np.clip(v, -s, s) + s) / (2 * s) * levels
    q = np.floor(u)
    q += rng.random(v.shape) < (u - q)
    return -s + q / levels * (2 * s), v.size * int(bits) + FLOAT_BITS


def _k_of(k, d):
    """k as an int, or as a fraction of d when 0 < k < 1."""
    return max(1, min(d, int(round(k * d)) if 0 < k < 1 else int(k)))


def topk(v, k):
    v = np.asarray(v, dtype=float)
    k = _k_of(k, v.size)
    out = np.zeros_like(v)
    idx = np.argpartition(-np.abs(v), k - 1)[:k]
    out[idx] = v[idx]
    return out, 2 * k * FLOAT_BITS


def randk(v, k, rng):
    v = np.asarray(v, dtype=float)
    k = _k_of(k, v.size)
    out = np.zeros_like(v)
    idx = rng.choice(v.size, size=k, replace=False)
    out[idx] = v[idx] * (v.size / k)
    return out, 2 * k * FLOAT_BITS


def compress(v, spec, rng):
    """spec: None/'none', or dict(kind='quant', bits=b) / dict(kind='topk'|'randk', k=k)."""
    if spec is None or spec == "none" or spec.get("kind", "none") == "none":
        v = np.asarray(v, dtype=float)
        return v.copy(), v.size * FLOAT_BITS
    kind = spec["kind"]
    if kind == "quant":
        return quantize(v, spec["bits"], rng)
    if kind == "topk":
        return topk(v, spec["k"])
    if kind == "randk":
        return randk(v, spec["k"], rng)
    raise ValueError(f"unknown compressor {kind!r}")


def spec_label(spec):
    if spec is None or spec == "none" or spec.get("kind", "none") == "none":
        return "none"
    if spec["kind"] == "quant":
        return f"quant{spec['bits']}"
    return f"{spec['kind']}{spec['k']}"


class ErrorFeedback:
    """Per-sender residual memory: send C(v + e), keep e ← v + e − C(v + e)."""

    def __init__(self, spec, rng):
        self.spec, self.rng = spec, rng
        self.e = {}

    def __call__(self, key, v):
        v = np.asarray(v, dtype=float) + self.e.get(key, 0.0)
        out, bits = compress(v, self.spec, self.rng)
        self.e[key] = v - out
        return out, bits
