"""Federated single-index bandit machinery.

  engine.py       FedTwoPhase -- the generic two-phase federated learner
  independent.py  N non-communicating single-agent ZoomSIB-UCB learners
  fl/             federated-learning METHODS (FedAvg, SCAFFOLD, ...), one file each,
                  all solving the federated least-squares problem both phases reduce to
  phase1/         how theta is pooled      (one file per strategy; `fl` runs any fl/ method)
  phase2/         how bin stats are shared (one file per strategy; `fl` runs any fl/ method)
  scenarios.py    heterogeneity: iid, participation, covariate shift, concept shift
  runner.py       N-agent environments, episode loop, parallel sweeps
  viz.py          live dashboard / GIF

Named algorithms (ZoomSIB, Fed-ZoomSIB, variants) are configs in experiments/configs/.
"""

from .engine import FedTwoPhase
from .fl import FL_METHODS
from .scenarios import SCENARIOS
from .independent import IndependentAgents
from .phase1 import PHASE1
from .phase2 import PHASE2
from .runner import build_fed, make_fed_envs, run_fed_episode, run_fed_sweep

__all__ = ["FL_METHODS", "SCENARIOS", "FedTwoPhase", "IndependentAgents", "PHASE1", "PHASE2", "build_fed",
           "make_fed_envs", "run_fed_episode", "run_fed_sweep"]
