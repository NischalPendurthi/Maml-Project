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


# Diverging ramp for "ratio to a reference": blue = better, neutral gray = equal,
# orange = worse.  Two hues and a gray midpoint, never a rainbow.
RATIO_COLORS = ["#2a78d6", "#e4e3df", "#eb6834"]


def heatmap(ax, values, rows, cols, fmt="{:.2f}", log=False, diverging_at=None,
            cmap="Blues", vmin=None, vmax=None, fontsize=7, text=None):
    """Annotated heatmap.

    `diverging_at` (e.g. 1.0 for ratios) centres a blue–gray–orange ramp on that
    value in log space; otherwise a single-hue sequential ramp is used.  `text`
    may give per-cell strings to print instead of `fmt` of the value.
    """
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

    V = np.asarray(values, dtype=float)
    C = np.log10(np.clip(V, 1e-300, None)) if (log or diverging_at is not None) else V
    finite = C[np.isfinite(C)]
    lo = vmin if vmin is not None else (finite.min() if finite.size else 0.0)
    hi = vmax if vmax is not None else (finite.max() if finite.size else 1.0)
    if diverging_at is not None:
        c0 = np.log10(diverging_at)
        span = max(abs(lo - c0), abs(hi - c0), 1e-3)
        cm = LinearSegmentedColormap.from_list("ratio", RATIO_COLORS)
        norm = TwoSlopeNorm(vcenter=c0, vmin=c0 - span, vmax=c0 + span)
        im = ax.imshow(np.ma.masked_invalid(C), cmap=cm, norm=norm, aspect="auto")
    else:
        im = ax.imshow(np.ma.masked_invalid(C), cmap=cmap, vmin=lo, vmax=hi, aspect="auto")
    ax.set_xticks(range(len(cols)), cols, rotation=35, ha="right", fontsize=fontsize + 0.5)
    ax.set_yticks(range(len(rows)), rows, fontsize=fontsize + 0.5)
    ax.tick_params(length=0)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    rgba = im.cmap(im.norm(np.ma.masked_invalid(C)))
    for i in range(V.shape[0]):
        for j in range(V.shape[1]):
            if text is not None:
                t = text[i][j]
            elif np.isfinite(V[i, j]):
                t = fmt.format(V[i, j])
            else:
                t = "–"
            r, g, b, _ = rgba[i, j]
            dark = (0.299 * r + 0.587 * g + 0.114 * b) < 0.55
            ax.text(j, i, t, ha="center", va="center", fontsize=fontsize,
                    color="white" if dark else "#0b0b0b")
    return im
