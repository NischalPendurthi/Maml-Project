"""Decentralised Phase-2 strategies (sharing the bin table over a graph).

    flood         exact relay of own tables, stale by ≤ diameter (every / event-triggered)
    consensus     running consensus, N·x as the network total (Landgren et al. 2016)
    pushsum       ratio consensus: directed / time-varying graphs
    gossip        k gossip steps every C rounds, naive or effective-sample-size counts
    neighbor      one-hop sharing only
    server / server_event / none    references
"""

from .base import DecPhase2
from .burst import BurstGossipTables
from .consensus import ConsensusTables
from .flood import FloodTables
from .pushsum import PushSumTables
from .references import Neighbor, NoneShare, Server, ServerEvent

DEC_PHASE2 = {c.name: c for c in (FloodTables, ConsensusTables, PushSumTables,
                                  BurstGossipTables, Neighbor, Server, ServerEvent, NoneShare)}


def make_dec_phase2(spec, **kw):
    if not isinstance(spec, str):
        return spec
    return DEC_PHASE2[spec](**kw)


__all__ = ["DEC_PHASE2", "make_dec_phase2", "DecPhase2"]
