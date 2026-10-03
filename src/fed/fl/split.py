"""Split learning.

Client sends: per-sample activations at the cut layer.  The single-index
              "network" has no hidden layers, so the natural cut is right after
              the per-sample transform: Stein summands φτ(y S(x)) (d numbers
              per sample), raw (x, y) for LS, (bin, y) per pull in Phase 2.
Server does:  completes the computation -- here the pooled average, which is
              exact.

Relevance: exact like `suffstat` but pays per SAMPLE, not per statistic, and
hands the server per-sample data (no privacy benefit over centralising).
Included to put a price on "just send the data".
"""

from __future__ import annotations

from .base import FLMethod


class SplitLearning(FLMethod):
    name = "split"
    label = "Split learning (per-sample activations)"
    one_shot = True

    def round(self, prob, w):
        return prob.pooled(w)

    def round_cost(self, prob):
        act = prob.active
        up = prob.sample_cost * prob.new_samples[act].sum()
        return int(up + prob.D * act.sum())
