"""Shared plumbing for the decentralised experiments (exp14–exp21).

A decentralised benchmark is a grid of cells (graph, link, scenario); in each
cell a set of configs -- which may depend on the graph -- is run for a number
of paired trials.  Cells are checkpointed, so an interrupted run resumes, and
`--redo=NAME` recomputes only the configs whose name contains NAME.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fed import run_fed_sweep                    # noqa: E402
from src.fed.runner import resumable_cells           # noqa: E402

D, K, T, SIGMA, N = 10, 20, 10_000, 0.1, 16
N_TRIALS = 6

REDO = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--redo=")), None)
# "--redo=+NAME": only FILL IN matching configs missing from a cached cell (resume an
# interrupted redo) instead of recomputing them everywhere.
FILL = bool(REDO) and all(t.startswith("+") for t in REDO)
if FILL:
    REDO = [t[1:] for t in REDO]
REPLOT = "--replot" in sys.argv


def run_cells(cache, cells, configs_for, n_trials=N_TRIALS, N_agents=None, T_rounds=T):
    """cells: list of (graph, link, scenario[, N]); configs_for(cell) -> {name: config}."""

    import pickle

    prev = {}
    if FILL and os.path.exists(cache):
        with open(cache, "rb") as fh:
            prev = pickle.load(fh)

    def cell_fn(cell, names=None):
        graph, link, scenario = cell[:3]
        n_ag = cell[3] if len(cell) > 3 else (N_agents or N)
        cfgs = configs_for(cell)
        run = {k: v for k, v in cfgs.items() if names is None or any(t in k for t in names)}
        if FILL:
            run = {k: v for k, v in run.items() if k not in prev.get(cell, {})}
            if not run:
                print(f"  cell {cell}: nothing missing", flush=True)
                return {}
        print(f"  cell {cell}: {len(run)} configs", flush=True)
        out, _ = run_fed_sweep(run, n_trials, n_ag, D, K, T_rounds, link, sigma=SIGMA,
                               record_every=T_rounds, progress=False, scenario=scenario)
        res = {}
        for name, v in out.items():
            dg = v["diag"]
            res[name] = dict(
                R=v["net"][:, -1],
                comm=np.array([x["comm_scalars"] for x in dg], float),
                comm1=np.array([x["comm_phase1"] for x in dg], float),
                rounds=np.array([x["comm_rounds"] for x in dg], float),
                T0=np.array([x["T0_used"] or np.nan for x in dg], float),
                disagree=np.array([x.get("disagreement", 0.0) for x in dg], float),
                label=cfgs[name].get("label", name))
        return res

    return resumable_cells(cache, cells, cell_fn, redo=REDO)


def ratio_table(res, cells, names, ref):
    """(len(names), len(cells)) mean-regret ratio to config `ref` in each cell."""
    return np.array([[res[c][n]["R"].mean() / res[c][ref]["R"].mean() for c in cells]
                     for n in names])


def md_table(path, title, intro, header, rows):
    L = [f"# {title}", "", intro, "", "| " + " | ".join(header) + " |",
         "|" + "---|" * len(header)]
    L += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"  wrote {path}")
