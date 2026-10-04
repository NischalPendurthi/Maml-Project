"""Decentralised Fed-ZoomSIB: no server, agents communicate over a graph.

  graph/      topologies, mixing (communication) matrices, link dynamics
  gossip.py   consensus primitives: plain, Chebyshev-accelerated, max-consensus, relay
  phase1/     pooling θ over the graph   (one file per strategy family)
  phase2/     sharing the bin table over the graph
  engine.py   DecTwoPhase, selected in configs by engine="dec"
  viz.py      live dashboard that draws the actual graph

Mirrors src/fed/, which keeps the server-based (federated) version.
"""

from .engine import DecTwoPhase
from .graph import MIXING, TOPOLOGIES, Graph
from .phase1 import DEC_PHASE1
from .phase2 import DEC_PHASE2

__all__ = ["DecTwoPhase", "Graph", "TOPOLOGIES", "MIXING", "DEC_PHASE1", "DEC_PHASE2"]
