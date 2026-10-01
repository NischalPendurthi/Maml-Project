"""Federated single-index bandit machinery.

  engine.py       FedTwoPhase -- the generic two-phase federated learner
  independent.py  N non-communicating single-agent ZoomSIB-UCB learners
  phase1/         how theta is pooled      (one file per strategy)
  phase2/         how bin stats are shared (one file per strategy)
  runner.py       N-agent environments, episode loop, parallel sweeps
  viz.py          live dashboard / GIF

Named algorithms (ZoomSIB, Fed-ZoomSIB, variants) are configs in experiments/configs/.
"""

from .engine import FedTwoPhase
from .independent import IndependentAgents
from .phase1 import PHASE1
from .phase2 import PHASE2
from .runner import build_fed, make_fed_envs, run_fed_episode, run_fed_sweep

__all__ = ["FedTwoPhase", "IndependentAgents", "PHASE1", "PHASE2", "build_fed",
           "make_fed_envs", "run_fed_episode", "run_fed_sweep"]
