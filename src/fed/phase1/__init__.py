"""Phase-1 (theta pooling) strategies.  One file per strategy; register here.

    exact      pooled Stein sums (≡ fl + suffstat; kept for the earlier experiments)
    normavg    FedAvg of finished, normalised local estimates
    median     coordinate-wise median (robust aggregation)
    quantized  compressed exact upload
    fl         ANY federated-learning method from src/fed/fl/, on the Stein or LS objective
"""

from .base import Phase1Strategy
from .exact import ExactStein
from .fl import FLPool
from .median import CoordinateMedian
from .normavg import NormalizedAverage
from .quantized import QuantizedStein

PHASE1 = {cls.name: cls for cls in (ExactStein, NormalizedAverage, CoordinateMedian,
                                    QuantizedStein, FLPool)}


def make_phase1(spec, rng, **kw):
    """A registered name (+ kwargs) or an already-built strategy object."""
    if isinstance(spec, Phase1Strategy):
        return spec
    return PHASE1[spec](rng=rng, **kw)


__all__ = ["PHASE1", "make_phase1", "Phase1Strategy", "ExactStein", "NormalizedAverage",
           "CoordinateMedian", "QuantizedStein", "FLPool"]
