"""Shared plumbing for the claims-evidence experiments (exp22–exp28).

Every script accepts
    --quick        few trials / short horizons; writes to results/quick/ so a smoke
                   run never overwrites the real figures
    --replot       redraw from the cached results without simulating
    --trials=N     override the number of trials
    --redo=NAME    (via resumable cells) recompute configs whose name contains NAME

Results are cached per cell with `resumable_cells`, so an interrupted run resumes.
"""

from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))
os.chdir(ROOT)

import matplotlib.pyplot as plt                       # noqa: E402

from src.fed import run_fed_sweep                     # noqa: E402
from src.fed.runner import resumable_cells            # noqa: E402
from src.plotting import use_style                    # noqa: E402

QUICK = "--quick" in sys.argv
REPLOT = "--replot" in sys.argv
REDO = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--redo=")), None)
_TRIALS = next((int(a.split("=", 1)[1]) for a in sys.argv if a.startswith("--trials=")), None)
OUT = "results/quick" if QUICK else "results"
os.makedirs(f"{OUT}/cache", exist_ok=True)

D, K, SIGMA = 10, 20, 0.1


def trials(full, quick=3):
    return _TRIALS or (quick if QUICK else full)


def pick(full, quick):
    return quick if QUICK else full


def cache(name):
    return f"{OUT}/cache/{name}.cells"


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{name}.{ext}")
    plt.close(fig)
    print(f"  wrote {OUT}/{name}.{{png,pdf}}")


def summarize(out, keep_curves=False, extra=None):
    """run_fed_sweep output -> {name: dict of per-trial arrays}."""
    res = {}
    for name, v in out.items():
        dg = v["diag"]
        r = dict(
            R=v["net"][:, -1],
            comm=np.array([x["comm_scalars"] for x in dg], float),
            bits=np.array([x["comm_bits"] for x in dg], float),
            comm1=np.array([x["comm_phase1"] for x in dg], float),
            bits1=np.array([x.get("comm_phase1_bits", np.nan) for x in dg], float),
            rounds=np.array([x["comm_rounds"] for x in dg], float),
            rounds1=np.array([x.get("comm_rounds_phase1", np.nan) for x in dg], float),
            T0=np.array([x["T0_used"] or np.nan for x in dg], float),
            N_bins=np.array([np.mean(x["N_bins"]) if x["N_bins"] is not None else np.nan
                             for x in dg], float),
            disagree=np.array([x.get("disagreement", 0.0) for x in dg], float),
        )
        trig = [x.get("trigger_counts") for x in dg]
        if all(t is not None for t in trig):
            r["trig_max"] = np.array([t.max() for t in trig], float)
        if keep_curves:
            r["net"] = v["net"]
        if extra:
            for key, fn in extra.items():
                r[key] = np.array([fn(x) for x in dg], float)
        res[name] = r
    return res


def run_cells(name, cells, cell_fn):
    """cell_fn(cell, names_or_None) -> {config: summary}.  Checkpointed per cell."""
    return resumable_cells(cache(name), cells, cell_fn, redo=REDO)


def sweep(configs, n_trials, N, T, link, record_every=None, d=D, **kw):
    out, grid = run_fed_sweep(configs, n_trials, N, d, K, T, link, sigma=SIGMA,
                              record_every=record_every or T, progress=False, **kw)
    return out, grid


def md_table(path, title, intro, header, rows):
    L = [f"# {title}", "", intro, "", "| " + " | ".join(header) + " |",
         "|" + "---|" * len(header)]
    L += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"  wrote {path}")


def mci(x):
    """mean and 95% half-width."""
    x = np.asarray(x, float)
    return x.mean(), 1.96 * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0


def fmt(x, digits=0):
    m, h = mci(x)
    return f"{m:,.{digits}f} ± {h:,.{digits}f}"


__all__ = ["QUICK", "REPLOT", "OUT", "D", "K", "SIGMA", "trials", "pick", "cache", "save",
           "summarize", "run_cells", "sweep", "md_table", "mci", "fmt", "use_style", "plt", "np"]
