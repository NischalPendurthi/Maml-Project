"""Multi-index bandits: y = g(Bᵀx) + noise, B ∈ R^{d×m} orthonormal, g unknown.

The extension of single-index ZoomSIB-UCB named as open by Dey, Bhore & Ghosh
(§7).  Phase 1 estimates span(B) with the SECOND-order Stein identity (the
first-order statistic E[y S(x)] lies in span(B) but is a single vector);
Phase 2 runs the same sleeping UCB on m-dimensional cubes of side Δ.

    env.py      MIBEnv and its links
    stein2.py   second-order Stein matrix, subspace estimate and error
    engine.py   FedZoomMIB (server engine; N = 1 is single-agent ZoomMIB-UCB)
"""

from .engine import FedZoomMIB
from .env import MIB_LINKS, MIBEnv, parse_mib_link

__all__ = ["FedZoomMIB", "MIBEnv", "MIB_LINKS", "parse_mib_link"]
