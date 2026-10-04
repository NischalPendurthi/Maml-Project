"""Reference Phase-2 strategies reused from the federated package.

  server        exact server sync every `every` rounds (fed/phase2/periodic)
  server_event  event-triggered server sync (fed/phase2/event) -- the
                recommended FEDERATED version, as the ceiling to compare against
  none          no sharing
  neighbor      one-hop sharing of own tables on the graph (fed/phase2/neighbor)
"""

from __future__ import annotations

from ...fed.phase2.event import EventTriggered
from ...fed.phase2.neighbor import NeighborShare
from ...fed.phase2.none import NoShare
from ...fed.phase2.periodic import PeriodicSync


class _Attach:
    def attach(self, graph):
        self.g = graph


class Server(_Attach, PeriodicSync):
    name = "server"


class ServerEvent(_Attach, EventTriggered):
    name = "server_event"

    def __init__(self, gamma=0.5):
        super().__init__(gamma=gamma)


class NoneShare(_Attach, NoShare):
    name = "none"


class Neighbor(NeighborShare):
    """One-hop sharing on the engine's graph (static topology)."""
    name = "neighbor"

    def __init__(self, every=1):
        super().__init__(graph="ring", every=every)

    def attach(self, graph):
        self.g = graph
        self.graph = graph.A0
