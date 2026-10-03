"""Federated-learning methods, one file per method, all solving `FedQuadratic`.

Both phases of Fed-ZoomSIB reduce to the same federated least-squares problem
(see problem.py), so every method here plugs into Phase 1 through
`phase1/fl.py` and into Phase 2 through `phase2/fl.py`.

    suffstat      exact sufficient statistics (the centralised estimator)
    split         split learning: per-sample activations
    oneshot       one-shot FedAvg: local optimum, weighted average
    fedsgd        FedSGD                       gradient     = alias (gradient-based FL)
    fedavg        FedAvg                       (step_rule="proportional": steps ∝ data)
    fedprox       FedProx
    fedavgm       FedAvgM (server momentum)
    fedadam       FedAdam                      fedyogi      FedYogi
    fednova       FedNova
    scaffold      SCAFFOLD
    feddyn        FedDyn
    distill       federated distillation
    personalized  personalised FL (partial pooling)

To add a method: copy fedavg.py, implement `round`, register it below.
"""

from .base import FLMethod, local_gd, vector_cost
from .distill import FedDistill
from .fedadam import FedAdam
from .fedavg import FedAvg
from .fedavgm import FedAvgM
from .feddyn import FedDyn
from .fednova import FedNova
from .fedprox import FedProx
from .fedsgd import FedSGD, GradientFL
from .fedyogi import FedYogi
from .oneshot import OneShotAvg
from .personalized import Personalized
from .problem import FedQuadratic
from .scaffold import Scaffold
from .split import SplitLearning
from .suffstat import SuffStat

FL_METHODS = {cls.name: cls for cls in (
    SuffStat, SplitLearning, OneShotAvg, FedSGD, GradientFL, FedAvg, FedProx, FedAvgM,
    FedAdam, FedYogi, FedNova, Scaffold, FedDyn, FedDistill, Personalized)}


def make_fl(spec, **kw):
    """A registered name (+ kwargs) or an already-built method object."""
    if isinstance(spec, FLMethod):
        return spec
    return FL_METHODS[spec](**kw)


__all__ = ["FL_METHODS", "make_fl", "FLMethod", "FedQuadratic", "local_gd", "vector_cost"]
