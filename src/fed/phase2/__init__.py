"""Phase-2 (bin-statistics sharing) strategies.  One file per strategy; register here."""

from .base import Phase2Strategy, ServerSync
from .event import EventTriggered
from .neighbor import NeighborShare
from .none import NoShare
from .periodic import PeriodicSync

PHASE2 = {cls.name: cls for cls in (PeriodicSync, NoShare, EventTriggered, NeighborShare)}


def make_phase2(spec, **kw):
    """A registered name (+ kwargs) or an already-built strategy object."""
    if isinstance(spec, Phase2Strategy):
        return spec
    return PHASE2[spec](**kw)


__all__ = ["PHASE2", "make_phase2", "Phase2Strategy", "ServerSync", "PeriodicSync",
           "NoShare", "EventTriggered", "NeighborShare"]
