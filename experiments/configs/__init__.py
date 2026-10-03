"""Algorithm configurations.  An algorithm here is just a choice of building blocks
from src/ -- engine, Phase-1 strategy, Phase-2 strategy, knobs -- so a new
variant is a new dict, never new src code.

    zoomsib.py         the single-agent algorithm, run as N non-communicating copies
    fed_zoomsib.py     Fed-ZoomSIB, the proposed method
    phase1_variants.py how theta is pooled          (Phase 2 held fixed)
    phase2_variants.py how bin statistics are shared (Phase 1 held fixed)
    fl_variants.py     every federated-learning METHOD (FedAvg, SCAFFOLD, ...) as a
                       Phase-1 or Phase-2 variant, with tuning grids (exp10–exp12)

Every config may carry `label` and `style` (matplotlib kwargs) for plotting;
the runner strips them before building the algorithm.
"""

from .fed_zoomsib import FED_ZOOMSIB
from .fl_variants import (FAMILY, FAMILY_COLOR, FL_VARIANTS, GRIDS, LABEL,  # noqa: F401
                          fl_phase1_config, fl_phase2_config, method_kwargs)
from .phase1_variants import PHASE1_VARIANTS
from .phase2_variants import PHASE2_VARIANTS, sync_period_sweep
from .zoomsib import ZOOMSIB

ALL = {**ZOOMSIB, **FED_ZOOMSIB, **PHASE1_VARIANTS, **PHASE2_VARIANTS}


def pick(*names, **overrides):
    """Sub-select configs by name; `overrides` are merged into every one."""
    return {n: dict(ALL[n], **overrides) for n in names}


def label(cfg, name=""):
    return cfg.get("label", name)


def style(cfg):
    return dict(label=cfg.get("label"), **cfg.get("style", {}))
