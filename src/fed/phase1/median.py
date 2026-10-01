"""median -- coordinate-wise median of the local estimates.

Byzantine-robust (a minority of corrupted agents cannot drag any coordinate
arbitrarily far) at the price of statistical efficiency when everyone is honest.
"""

from __future__ import annotations

import numpy as np

from ...stein import normalize_l1
from .base import FLOAT_BITS, Phase1Strategy
from .normavg import local_estimates


class CoordinateMedian(Phase1Strategy):
    name = "median"

    def aggregate(self, agents, tau_fn):
        loc = local_estimates(agents, tau_fn)
        return normalize_l1(np.median(loc, axis=0)), loc.size, loc.size * FLOAT_BITS
