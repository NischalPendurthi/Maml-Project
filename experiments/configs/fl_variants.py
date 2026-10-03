"""Federated-learning variants of Fed-ZoomSIB, for the FL benchmark (exp10–exp12).

Each FL method in src/fed/fl/ can be dropped into Phase 1 (pooling theta) or
Phase 2 (sharing the bin table).  This module names the variants, gives each a
hyperparameter grid for tuning, and builds engine configs:

    fl_phase1_config("scaffold", dict(local_steps=5))   # Phase 2 held at exact sync
    fl_phase2_config("feddyn",   dict(alpha_rel=0.1))   # Phase 1 held at exact pooling

The table's "gradient-based FL" row is FedSGD on a least-squares problem
(src/fed/fl/fedsgd.py), so it is benchmarked once, as `fedsgd`.  Split learning
is benchmarked as `split`: no layers to split, so the cut is right after the
per-sample transform.  Personalised FL needs a per-agent theta, which the shared
bin grid rules out in Phase 1, so it is studied offline there (exp10 part A) and
inside the bandit only in Phase 2.
"""

from __future__ import annotations

# key -> (src/fed/fl method name, fixed kwargs)
FL_VARIANTS = {
    "suffstat":    ("suffstat", {}),
    "split":       ("split", {}),
    "oneshot":     ("oneshot", {}),
    "distill":     ("distill", {}),
    "fedsgd":      ("fedsgd", {}),
    "fedavg":      ("fedavg", {}),
    "fedavg_prop": ("fedavg", {"step_rule": "proportional"}),
    "fedprox":     ("fedprox", {}),
    "fednova":     ("fednova", {}),
    "fedavgm":     ("fedavgm", {}),
    "fedadam":     ("fedadam", {}),
    "fedyogi":     ("fedyogi", {}),
    "scaffold":    ("scaffold", {}),
    "feddyn":      ("feddyn", {}),
}

LABEL = {
    "suffstat":    "Sufficient statistics (exact)",
    "split":       "Split learning",
    "oneshot":     "One-shot FedAvg",
    "distill":     "Fed. distillation",
    "fedsgd":      "FedSGD / gradient-based",
    "fedavg":      "FedAvg",
    "fedavg_prop": "FedAvg, steps ∝ data",
    "fedprox":     "FedProx",
    "fednova":     "FedNova",
    "fedavgm":     "FedAvgM",
    "fedadam":     "FedAdam",
    "fedyogi":     "FedYogi",
    "scaffold":    "SCAFFOLD",
    "feddyn":      "FedDyn",
}

# What each method changes, used to colour results by family (5 hues, fixed order).
FAMILY = {
    "suffstat": "exact", "split": "exact",
    "oneshot": "averaging", "distill": "averaging", "fedavg": "averaging",
    "fedavg_prop": "averaging", "fedprox": "averaging",
    "fedsgd": "gradient",
    "fedavgm": "server optimiser", "fedadam": "server optimiser", "fedyogi": "server optimiser",
    "fednova": "drift correction", "scaffold": "drift correction", "feddyn": "drift correction",
}
FAMILY_COLOR = {"exact": "#2a78d6", "averaging": "#eb6834", "gradient": "#1baf7a",
                "server optimiser": "#4a3aa7", "drift correction": "#008300"}

ONE_SHOT = {"suffstat", "split", "oneshot", "distill"}

# Hyperparameter grids searched in the offline parts of exp10 / exp11.
GRIDS = {
    "suffstat": [{}], "split": [{}], "oneshot": [{}], "distill": [{}],
    "fedsgd": [{"lr_scale": s} for s in (0.5, 1.0)],
    "fedavg": [{"local_steps": E, "lr_scale": s} for E in (1, 5, 20) for s in (0.3, 1.0)],
    "fedavg_prop": [{"local_steps": E, "lr_scale": s} for E in (1, 5, 20) for s in (0.3, 1.0)],
    "fedprox": [{"local_steps": E, "mu_rel": m} for E in (5, 20) for m in (0.01, 0.1, 1.0)],
    "fednova": [{"local_steps": E, "lr_scale": s} for E in (5, 20) for s in (0.1, 0.3, 1.0)],
    "fedavgm": [{"local_steps": E, "server_lr": lr, "beta": b}
                for E in (1, 5) for lr in (0.1, 0.3, 1.0) for b in (0.5, 0.9)],
    "fedadam": [{"local_steps": E, "server_lr": lr}
                for E in (1, 5) for lr in (0.003, 0.01, 0.03, 0.1, 0.3)],
    "fedyogi": [{"local_steps": E, "server_lr": lr}
                for E in (1, 5) for lr in (0.003, 0.01, 0.03, 0.1, 0.3)],
    "scaffold": [{"local_steps": E, "lr_scale": s} for E in (5, 20) for s in (0.3, 1.0)],
    "feddyn": [{"local_steps": E, "alpha_rel": a} for E in (5, 20) for a in (0.01, 0.1, 1.0)],
}


def method_kwargs(key, tuned=None):
    name, fixed = FL_VARIANTS[key]
    return name, dict(fixed, **((tuned or {}).get(key, {})))


def fl_phase1_config(key, tuned=None, rounds=10, objective="stein"):
    name, kw = method_kwargs(key, tuned)
    return dict(
        engine="fed",
        phase1="fl",
        phase1_kw=dict(method=name, method_kw=kw,
                       rounds=1 if key in ONE_SHOT else rounds, objective=objective),
        phase2="periodic", phase2_kw=dict(every=1),
        label=LABEL[key] + ("" if objective == "stein" else f" [{objective}]"),
        style=dict(color=FAMILY_COLOR[FAMILY[key]]),
    )


def fl_phase2_config(key, tuned=None, rounds=5, every=10, gamma=None):
    name, kw = method_kwargs(key, tuned)
    return dict(
        engine="fed",
        phase1="exact",
        phase2="fl",
        phase2_kw=dict(method=name, method_kw=kw, rounds=1 if key in ONE_SHOT else rounds,
                       every=every, gamma=gamma),
        label=LABEL[key],
        style=dict(color=FAMILY_COLOR[FAMILY[key]]),
    )
