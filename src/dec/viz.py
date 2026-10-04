"""Live dashboard for decentralised Fed-ZoomSIB: the graph instead of a server.

Reuses src/fed/viz.py's Recorder (which records each agent's CONSENSUS estimate
θ̂_i and the round's realised adjacency when the algorithm has a graph) and its
Dashboard panels; only the network panel and the labels change:

  network  agents laid out on a circle with the graph's edges; edges that
           carried a message since the last frame are drawn thick, with what
           they carried; no server box -- just the graph's diameter and gap
  theta    each agent's own consensus estimate vs the pooled one a server
           would compute: watch the spread collapse as gossip mixes
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Circle

from ..fed.viz import INK, INK2, MUTED, GRID, PHASE_COLOR, Dashboard

P1_TEXT = {
    "flood": "each agent relays the freshest copy of every agent's\n(Stein sum, count) record it has heard of",
    "consensus": "x_i ← Σ_j P_ij (x_j + new samples):\none gossip step per round",
    "pushsum": "agents push shares of (sum, weight)\nto out-neighbours; estimate = sum / weight",
    "gossip": "k gossip steps on Stein sums at each checkpoint",
    "chebyshev": "k Chebyshev-accelerated gossip steps at each checkpoint",
    "tree": "convergecast up a spanning tree, broadcast back down",
    "dgd": "decentralised gradient descent on the Stein loss",
    "gt": "gradient tracking: models and gradient estimates gossiped",
    "dlocal": "local steps, then gossip-average the models",
}
P2_TEXT = {
    "flood": "agents relay the freshest copy of every\nagent's own bin table (exact, delayed)",
    "consensus": "running consensus on (n_j, S_j);\nagents act on N × their state",
    "pushsum": "push-sum on (n_j, S_j) with weights",
    "gossip": "k gossip steps on tables every C rounds;\neffective-sample-size counts",
    "neighbor": "own tables shared with direct neighbours only",
}


class DecDashboard(Dashboard):
    TITLE = "Decentralised Fed-ZoomSIB live"
    ALG_NAME = "decentralised"
    PHASE1_TXT = "Phase 1 · Stein estimation of θ* by gossip over the graph"
    LOCAL_LABEL = "agent's consensus estimate"
    LOCAL_ERR = "agents (consensus)"
    FED_LABEL = "pooled θ̂ (what a server would get)"
    FOOTER = ("No server: every number an agent learns about the others crossed the graph "
              "edge by edge.  Thick edges carried a message since the last frame.")

    def __init__(self, fig, rec, *, graph, p1_name, p2_name, **kw):
        self.graph, self.p1_name, self.p2_name = graph, p1_name, p2_name
        super().__init__(fig, rec, **kw)

    def _network(self, snap):
        ax = self.ax_net
        ax.set_xlim(-1.45, 1.45)
        ax.set_ylim(-1.95, 1.45)
        ax.set_aspect("equal")
        ax.axis("off")
        g = self.graph
        ax.set_title(f"Graph: {g.name}, N={g.N} · diameter {g.diameter} · "
                     f"gap {g.gap:.2f}", fontsize=10.5, color=INK, loc="left")
        ang = np.pi / 2 - 2 * np.pi * np.arange(self.N) / self.N
        pos = np.c_[np.cos(ang), np.sin(ang)]
        ph = snap["phase"]
        ev = snap["events"]
        active = bool(ev.get("gossip") or ev.get("stein") or ev.get("freeze") or ev.get("sync"))
        A_now = snap.get("A", g.A0)
        for i in range(self.N):
            for j in range(self.N):
                if not g.A0[i, j] or (g.symmetric and j < i):
                    continue
                on = active and A_now[i, j]
                ax.plot(*zip(pos[i], pos[j]), color=PHASE_COLOR[ph] if on else GRID,
                        lw=2.6 if on else 1.0, alpha=0.85 if on else 1.0, zorder=1)
                if not g.symmetric and on:
                    mid = 0.55 * pos[j] + 0.45 * pos[i]
                    ax.annotate("", xy=mid, xytext=0.7 * pos[i] + 0.3 * pos[j],
                                arrowprops=dict(arrowstyle="-|>", color=PHASE_COLOR[ph], lw=1.6))
        pend = snap.get("pending")
        for i, (x, y) in enumerate(pos):
            ax.add_patch(Circle((x, y), 0.14, fc=self.colors[i], ec="#ffffff", lw=2.0, zorder=5))
            ax.text(x, y, f"A{i + 1}", ha="center", va="center", fontsize=9, weight="bold",
                    color="#ffffff", zorder=6)
            lab = f"n={snap['t']}" if ph == 1 else f"R={snap['cum'][i]:,.0f}"
            ax.text(1.3 * x, 1.24 * y, lab, ha="center", va="center", fontsize=7.5, color=INK2)
            if pend is not None and pend[i].sum() > 0:
                ax.text(0.72 * x, 0.72 * y, f"+{int(pend[i].sum())}", ha="center", va="center",
                        fontsize=7, color=INK, zorder=7,
                        bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec=self.colors[i], lw=1))
        ax.text(0, 0.05, "no server", ha="center", va="center", fontsize=10, color=MUTED,
                style="italic")
        name = self.p1_name if ph == 1 else self.p2_name
        text = (P1_TEXT if ph == 1 else P2_TEXT).get(name, name)
        head = ("Phase 1 · " if ph == 1 else "Phase 2 · ") + name
        if ev.get("freeze"):
            head, text = "freeze", ("every agent freezes its own θ̂_i; W from max-consensus\n"
                                    "over diameter rounds; shared bin grid")
        ax.text(-1.4, -1.5, head, fontsize=9.5, weight="bold",
                color=PHASE_COLOR[ph] if active else MUTED)
        ax.text(-1.4, -1.58, text if active else "no message this round", fontsize=8,
                color=INK if active else INK2, va="top")
        ax.text(-1.4, 1.40, f"comm rounds: {snap['comm_rounds']:,}\n"
                f"scalars sent: {snap['comm_scalars']:,}", fontsize=8.3, color=INK2, va="top")
        ax.text(1.4, 1.40, "● phase 1" if ph == 1 else "● phase 2", fontsize=9.5,
                color=PHASE_COLOR[ph], ha="right", va="top", weight="bold")
