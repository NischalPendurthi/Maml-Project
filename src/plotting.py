"""Shared matplotlib styling so every figure in the report reads as one system."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = "results"


def use_style():
    plt.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "lines.linewidth": 1.6,
        "legend.frameon": False,
        "figure.autolayout": False,
    })


def band(ax, x, mean, half, **kw):
    """Mean line plus a shaded confidence band."""
    ln, = ax.plot(x, mean, **kw)
    ax.fill_between(x, mean - half, mean + half,
                    color=ln.get_color(), alpha=0.15, linewidth=0)
    return ln


def save(fig, name):
    import os
    os.makedirs(RESULTS, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{RESULTS}/{name}.{ext}")
    plt.close(fig)
    print(f"  wrote {RESULTS}/{name}.pdf / .png")
