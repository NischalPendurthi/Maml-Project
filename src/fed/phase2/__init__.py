"""Phase-2 (bin-statistics sharing) strategies.  One file per strategy; register here.

    periodic      server sync of sufficient statistics every C rounds (≡ fl + suffstat)
    none          no sharing
    event         sync triggered by how much an agent learned locally
    neighbor      serverless, peer-to-peer on a graph
    personalized  shared statistics, personal weighting lam of the others' pulls
    fl            ANY federated-learning method from src/fed/fl/ on the bin table
"""

from .base import Phase2Strategy, ServerSync
from .event import EventTriggered
from .neighbor import NeighborShare
from .none import NoShare
from .fl import FLShare
from .periodic import PeriodicSync
from .personalized import PersonalizedSync

PHASE2 = {cls.name: cls for cls in (PeriodicSync, NoShare, EventTriggered, NeighborShare,
                                    PersonalizedSync, FLShare)}


def make_phase2(spec, **kw):
    """A registered name (+ kwargs) or an already-built strategy object."""
    if isinstance(spec, Phase2Strategy):
        return spec
    return PHASE2[spec](**kw)


__all__ = ["PHASE2", "make_phase2", "Phase2Strategy", "ServerSync", "PeriodicSync",
           "NoShare", "EventTriggered", "NeighborShare", "PersonalizedSync", "FLShare"]
