"""Decentralised Phase-1 strategies (pooling θ over a graph).  One file per family.

    flood       exact relay of every agent's record, delayed by graph distance (interleaved)
    consensus   running consensus, one gossip step per round              (interleaved)
    pushsum     ratio consensus: directed / time-varying graphs            (interleaved)
    gossip      k plain gossip steps per checkpoint                        (burst)
    chebyshev   k Chebyshev-accelerated gossip steps per checkpoint        (burst)
    tree        exact spanning-tree convergecast + broadcast               (burst)
    dgd / gt / dlocal   decentralised optimisation on the Stein problem    (burst)
    local / server      references: no communication / exact via a server
"""

from .base import DecPhase1
from .burst import BurstGossip, Chebyshev, Tree
from .consensus import RunningConsensus
from .flood import Flood
from .optim import DGD, DecLocal, GradientTracking
from .pushsum import PushSum
from .references import Local, Server

DEC_PHASE1 = {c.name: c for c in (Flood, RunningConsensus, PushSum, BurstGossip, Chebyshev,
                                  Tree, DGD, GradientTracking, DecLocal, Local, Server)}


def make_dec_phase1(spec, **kw):
    if isinstance(spec, DecPhase1):
        return spec
    return DEC_PHASE1[spec](**kw)


__all__ = ["DEC_PHASE1", "make_dec_phase1", "DecPhase1"]
