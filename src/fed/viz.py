"""Live dashboard for Fed-ZoomSIB: what every agent knows, and what moves on the wire.

`Recorder` hooks into `run_fed_episode(callback=...)` and snapshots the network
on a frame schedule that is dense where things happen (every round of Phase 1,
every few rounds across the first Phase-2 sync cycles) and geometric after that.
`Dashboard` draws one snapshot; the same drawing code feeds a GIF writer or a
live interactive window.

Panels
  network     server + agents; arrows light up when a message is exchanged and
              say what it carries; badges on each link show the pulls an agent has not yet synced
  theta       theta_* vs every agent's own Stein estimate vs the federated one
  error       ||theta_hat - theta_*||_1 over Phase 1: local vs federated
  index line  true f, the shared bin table (mean + UCB), and stacked bars of
              which agent's pulls fed each bin (hatched = not yet synced)
  regret      network regret, Fed-ZoomSIB vs N independent agents, live
"""

from __future__ import annotations

from collections import Counter

import numpy as np
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.patches import Circle, FancyBboxPatch

from ..stein import l1_error

# Reference categorical palette (dataviz skill), fixed order: agent i -> slot i.
AGENT_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300",
                "#4a3aa7", "#e34948"]
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
FED_COLOR, IND_COLOR = INK, "#8a8984"
PHASE_COLOR = {1: "#eb6834", 2: "#2a78d6"}

EVENT_TEXT = {
    "stein":  ("up",   "each agent ↑  Σ φτ(y·S(x)) and n   (d+1 numbers)\n"
                       "server: average = pooled Stein estimate, exactly"),
    "freeze": ("down", "agents ↑ max|⟨x, θ̂₀⟩|  ·  server ↓ frozen θ̂₀ and W\n"
                       "every agent now shares one bin grid"),
    "sync":   ("both", "agents ↑ unsynced (bin, n_j, S_j)\n"
                       "server merges, ↓ broadcasts the touched bins"),
}


class Recorder:
    """Collects snapshots during a run.  Pass `recorder` as the callback."""

    def __init__(self, envs, T, burst=160, burst_step=4, n_geo=70, on_snapshot=None):
        self.envs, self.T = envs, T
        self.theta_star = envs[0].theta_star
        self.burst, self.burst_step, self.n_geo = burst, burst_step, n_geo
        self.on_snapshot = on_snapshot
        self.frames = []
        self.err_t, self.err_fed, self.err_loc = [], [], []
        self.t_freeze = None
        self._events = Counter()
        self._next_geo = None

    def _want(self, t, algo):
        if algo.phase == 1 or algo.last_event == "freeze" or t == self.T:
            return True
        k = t - self.t_freeze
        if k <= self.burst:
            return k % self.burst_step == 0
        if self._next_geo is None:
            start = self.t_freeze + self.burst
            self._ratio = (self.T / start) ** (1.0 / self.n_geo)
            self._next_geo = start * self._ratio
        if t >= self._next_geo:
            while self._next_geo <= t:
                self._next_geo *= self._ratio
            return True
        return False

    @staticmethod
    def _thetas(algo):
        """(network θ̂, per-agent θ̂_i).  Federated: the pooled estimate and each
        agent's local-only one.  Decentralised: the pooled estimate a server
        would have, and each agent's own CONSENSUS estimate."""
        dec = hasattr(algo, "theta_now")
        if algo.phase == 1:
            return algo.federated_theta(), (algo.theta_now if dec else algo.local_thetas())
        if dec:
            return algo.theta_hat, algo.theta_agents
        return algo.theta_hat, algo.theta_local

    def __call__(self, t, algo, inst):
        if algo.last_event:
            self._events[algo.last_event] += 1
        if algo.last_event == "freeze":
            self.t_freeze = t

        if algo.phase == 1 or algo.last_event == "freeze":
            th_fed, th_loc = self._thetas(algo)
            self.err_t.append(t)
            self.err_fed.append(l1_error(th_fed, self.theta_star))
            self.err_loc.append([l1_error(v, self.theta_star) for v in th_loc])

        if not self._want(t, algo):
            return
        snap = dict(t=t, phase=algo.phase, events=dict(self._events),
                    cum=inst.sum(axis=0).copy(),
                    comm_scalars=algo.comm_scalars, comm_rounds=algo.comm_rounds,
                    n_err=len(self.err_t))
        self._events = Counter()
        th_fed, th_loc = self._thetas(algo)
        if hasattr(algo, "g"):                          # decentralised: the round's graph
            snap["A"] = algo.g.A.copy()
        if algo.phase == 1:
            snap.update(theta_fed=th_fed, theta_loc=th_loc,
                        samples=[(np.asarray(ag.X_buf).reshape(-1, algo.d),
                                  np.asarray(ag.y_buf)) for ag in algo.agents])
        else:
            snap.update(theta_fed=th_fed.copy(), theta_loc=th_loc.copy(),
                        W=algo.W, Delta=algo.Delta, N_bins=algo.N_bins,
                        ucb_const=algo.ucb_const,
                        G_n=algo.p2.shared_table()[0].copy(),
                        G_S=algo.p2.shared_table()[1].copy(),
                        pending=algo.p2.pending().copy(),
                        contrib=algo.contrib.copy())
        self.frames.append(snap)
        if self.on_snapshot is not None:
            self.on_snapshot(snap)


class Dashboard:
    TITLE = "Fed-ZoomSIB live"
    ALG_NAME = "Fed-ZoomSIB"
    PHASE1_TXT = "Phase 1 · federated Stein estimation of θ*"
    LOCAL_LABEL = "agent's own estimate"
    LOCAL_ERR = "agents alone"
    FED_LABEL = "federated θ̂ (= pooled)"
    FOOTER = ("Agents share an unknown θ* and link f. They never send raw data: "
              "only Stein sums (Phase 1) and per-bin (n, S) statistics (Phase 2).")

    def __init__(self, fig, rec, *, link_fn, link_name, N, d, K, T, phase2_desc,
                 ind_curve, fed_curve):
        self.fig, self.rec = fig, rec
        self.f, self.link_name = link_fn, link_name
        self.N, self.d, self.K, self.T, self.p2_desc = N, d, K, T, phase2_desc
        self.ind, self.fedc = ind_curve, fed_curve
        self.colors = AGENT_COLORS[:N]

        fig.patch.set_facecolor(SURFACE)
        gs = GridSpec(2, 3, figure=fig, width_ratios=[1.05, 1.25, 1.0],
                      left=0.02, right=0.985, top=0.885, bottom=0.075,
                      wspace=0.22, hspace=0.42)
        self.ax_net = fig.add_subplot(gs[:, 0])
        self.ax_theta = fig.add_subplot(gs[0, 1])
        self.ax_err = fig.add_subplot(gs[0, 2])
        sub = GridSpecFromSubplotSpec(2, 1, gs[1, 1], height_ratios=[1.5, 1], hspace=0.08)
        self.ax_f = fig.add_subplot(sub[0])
        self.ax_cnt = fig.add_subplot(sub[1], sharex=self.ax_f)
        self.ax_reg = fig.add_subplot(gs[1, 2])
        self.title = fig.text(0.02, 0.975, "", fontsize=15, weight="bold", color=INK, va="top")
        self.subtitle = fig.text(0.02, 0.937, "", fontsize=10.5, color=INK2, va="top")
        self.footer = fig.text(0.02, 0.018, "", fontsize=9, color=MUTED, va="bottom")

        self.t_freeze = rec.t_freeze or self.T
        self.err_xmax = self.t_freeze * 1.08
        allerr = np.r_[rec.err_fed, np.ravel(rec.err_loc)] if rec.err_t else np.r_[1.0]
        self.err_ymax = float(np.nanmax(allerr)) * 1.05
        self.zlim = None
        last = rec.frames[-1]
        if "W" in last:
            self.zlim = (-last["W"], last["W"])

    # ------------------------------------------------------------------
    def draw(self, snap):
        for ax in (self.ax_net, self.ax_theta, self.ax_err, self.ax_f, self.ax_cnt, self.ax_reg):
            ax.cla()
            ax.set_facecolor(SURFACE)
        t, ph = snap["t"], snap["phase"]
        phase_txt = (self.PHASE1_TXT if ph == 1
                     else f"Phase 2 · cooperative sleeping UCB over bins ({self.p2_desc})")
        self.title.set_text(f"{self.TITLE}   ·   round {t:,} / {self.T:,}")
        self.subtitle.set_text(f"N = {self.N} agents · d = {self.d} · K = {self.K} arms/round · "
                               f"link: {self.link_name} (unknown to agents)     —     {phase_txt}")
        self.footer.set_text(self.FOOTER)
        self._network(snap)
        self._theta(snap)
        self._error(snap)
        self._index_line(snap)
        self._regret(snap)

    # ------------------------------------------------------------------
    def _network(self, snap):
        ax = self.ax_net
        ax.set_xlim(-1.45, 1.45)
        ax.set_ylim(-1.95, 1.45)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title("Network: who talks, and what they send", fontsize=11,
                     color=INK, loc="left")
        ev = snap["events"]
        ph = snap["phase"]
        kind = "freeze" if "freeze" in ev else ("stein" if "stein" in ev else
                                                ("sync" if "sync" in ev else None))
        R = 1.0
        ang = np.pi / 2 - 2 * np.pi * np.arange(self.N) / self.N
        pos = np.c_[R * np.cos(ang), R * np.sin(ang)]

        for i, (x, y) in enumerate(pos):
            ux, uy = -x / R, -y / R
            p0 = (x + 0.17 * ux, y + 0.17 * uy)
            p1 = (0.24 * x, 0.24 * y)
            if kind is None:
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=GRID, lw=1.5, zorder=1)
                continue
            direction = EVENT_TEXT[kind][0]
            style = {"up": "-|>", "down": "<|-", "both": "<|-|>"}[direction]
            ax.annotate("", xy=p1, xytext=p0, zorder=2,
                        arrowprops=dict(arrowstyle=style, color=self.colors[i], lw=2.6,
                                        mutation_scale=16, shrinkA=0, shrinkB=0))

        # server
        box = FancyBboxPatch((-0.24, -0.15), 0.48, 0.30, boxstyle="round,pad=0.02,rounding_size=0.06",
                             fc="#ffffff", ec=INK, lw=1.6, zorder=3)
        ax.add_patch(box)
        ax.text(0, 0.05, "server", ha="center", va="center", fontsize=10, weight="bold",
                color=INK, zorder=4)
        inner = ("θ̂ (avg of sums)" if ph == 1 else f"bin table · {snap['N_bins']} bins")
        ax.text(0, -0.07, inner, ha="center", va="center", fontsize=7.5, color=INK2, zorder=4)

        pend = snap.get("pending")
        for i, (x, y) in enumerate(pos):
            ax.add_patch(Circle((x, y), 0.15, fc=self.colors[i], ec="#ffffff", lw=2.0, zorder=5))
            ax.text(x, y, f"A{i + 1}", ha="center", va="center", fontsize=9.5, weight="bold",
                    color="#ffffff", zorder=6)
            ox, oy = x * 1.33, y * 1.27
            if ph == 1:
                lab = f"explore · n={snap['t']}"
            else:
                lab = f"R={snap['cum'][i]:,.0f}"
            ax.text(ox, oy, lab, ha="center", va="center", fontsize=8, color=INK2, zorder=6)
            if pend is not None:
                k = int(pend[i].sum())
                if k:
                    ax.text(0.66 * x, 0.66 * y, f"+{k}", ha="center", va="center",
                            fontsize=7.5, color=INK, zorder=7,
                            bbox=dict(boxstyle="round,pad=0.18", fc="#ffffff",
                                      ec=self.colors[i], lw=1.2))

        # what is on the wire
        if kind is not None:
            msg = EVENT_TEXT[kind][1]
            reps = ev.get(kind, 1)
            head = {"stein": "Phase-1 checkpoint", "freeze": "θ̂₀ frozen → Phase 2",
                    "sync": "Phase-2 sync"}[kind]
            if kind == "sync" and reps > 1:
                head += f"  ×{reps} since last frame"
            ax.text(-1.4, -1.50, head, fontsize=9.5, weight="bold", color=PHASE_COLOR[2 if kind != "stein" else 1])
            ax.text(-1.4, -1.58, msg, fontsize=8.3, color=INK, va="top")
        else:
            idle = ("agents pull random arms and keep their samples local"
                    if ph == 1 else "agents act on (global table + own unsynced pulls)")
            ax.text(-1.4, -1.50, "no message this round", fontsize=9.5, weight="bold", color=MUTED)
            ax.text(-1.4, -1.58, idle, fontsize=8.3, color=INK2, va="top")

        raw = self.N * snap["t"] * (self.d + 1)
        ax.text(-1.4, 1.40, f"comm rounds: {snap['comm_rounds']:,}\n"
                f"scalars sent: {snap['comm_scalars']:,}\n"
                f"(raw data would be {raw:,})", fontsize=8.3, color=INK2, va="top")
        ax.text(1.4, 1.40, "● phase 1" if ph == 1 else "● phase 2", fontsize=9.5,
                color=PHASE_COLOR[ph], ha="right", va="top", weight="bold")

    # ------------------------------------------------------------------
    def _theta(self, snap):
        ax = self.ax_theta
        j = np.arange(self.d)
        ax.bar(j, self.rec.theta_star, width=0.7, color=GRID, edgecolor="none", zorder=1,
               label="true θ*")
        loc = snap["theta_loc"]
        off = np.linspace(-0.25, 0.25, self.N)
        for i in range(self.N):
            v = loc[i] * np.sign(loc[i] @ self.rec.theta_star or 1.0)
            ax.scatter(j + off[i], v, s=16, color=self.colors[i], zorder=3, linewidths=0,
                       label=self.LOCAL_LABEL if i == 0 else None)
        fed = snap["theta_fed"] * np.sign(snap["theta_fed"] @ self.rec.theta_star or 1.0)
        ax.scatter(j, fed, s=70, marker="D", color=INK, edgecolors="#ffffff", linewidths=1.2,
                   zorder=4, label=self.FED_LABEL)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xticks(j, [f"θ{k + 1}" for k in j], fontsize=8)
        lim = max(0.45, float(np.abs(self.rec.theta_star).max()) * 1.6)
        ax.set_ylim(-lim, lim)
        ax.tick_params(labelsize=8, colors=INK2)
        frozen = " (frozen)" if snap["phase"] == 2 else ""
        ax.set_title(f"Index direction θ: local vs federated{frozen}", fontsize=11,
                     color=INK, loc="left")
        ax.legend(loc="lower left", fontsize=7.5, ncol=3, frameon=False, handletextpad=0.3,
                  columnspacing=1.0)
        self._clean(ax)

    def _error(self, snap):
        ax = self.ax_err
        n = snap["n_err"]
        t = np.asarray(self.rec.err_t[:n])
        if n:
            loc = np.asarray(self.rec.err_loc[:n])
            for i in range(self.N):
                ax.plot(t, loc[:, i], color=self.colors[i], lw=1.2, alpha=0.85)
            ax.plot(t, self.rec.err_fed[:n], color=INK, lw=2.6)
            ax.text(t[-1], self.rec.err_fed[n - 1], "  federated", fontsize=8.5,
                    color=INK, va="center", weight="bold")
            ax.text(t[-1], float(np.nanmean(loc[-1])), "  " + self.LOCAL_ERR, fontsize=8.5,
                    color=INK2, va="bottom")
        if self.rec.t_freeze and snap["t"] >= self.rec.t_freeze:
            ax.axvline(self.rec.t_freeze, color=PHASE_COLOR[2], lw=1, ls="--")
            ax.text(self.rec.t_freeze, self.err_ymax * 0.97, " θ̂₀ frozen ", fontsize=8,
                    color=PHASE_COLOR[2], ha="right", va="top")
        ax.set_xlim(0, self.err_xmax * 1.25)
        ax.set_ylim(0, self.err_ymax)
        ax.set_xlabel("round (per agent)", fontsize=8.5, color=INK2)
        ax.set_ylabel("‖θ̂ − θ*‖₁", fontsize=8.5, color=INK2)
        ax.tick_params(labelsize=8, colors=INK2)
        ax.set_title("Phase 1 estimation error", fontsize=11, color=INK, loc="left")
        self._clean(ax)

    def _index_line(self, snap):
        axf, axc = self.ax_f, self.ax_cnt
        if self.zlim is None:
            return
        z = np.linspace(*self.zlim, 400)
        fz = self.f(z)
        axf.plot(z, fz, color=MUTED, lw=1.6, zorder=1, label="true f (hidden)")
        lo, hi = float(fz.min()), float(fz.max())
        pad = 0.25 * (hi - lo)
        axf.set_ylim(lo - pad, hi + pad)
        axf.set_xlim(*self.zlim)
        axc.set_xlim(*self.zlim)

        if snap["phase"] == 1:
            th = snap["theta_fed"] * np.sign(snap["theta_fed"] @ self.rec.theta_star or 1.0)
            for i, (X, y) in enumerate(snap["samples"]):
                if len(y):
                    axf.scatter(X @ th, y, s=9, color=self.colors[i], alpha=0.7, linewidths=0,
                                zorder=2)
            axf.set_title("Index line: Phase-1 samples projected on θ̂ (bins appear at freeze)",
                          fontsize=10, color=INK, loc="left")
            axc.text(0.5, 0.5, "no bins yet", transform=axc.transAxes, ha="center",
                     va="center", color=MUTED, fontsize=9)
        else:
            W, D, nb = snap["W"], snap["Delta"], snap["N_bins"]
            centers = -W + (np.arange(nb + 2) - 0.5) * D
            sl = slice(1, nb + 1)
            cz, Gn, GS = centers[sl], snap["G_n"][sl], snap["G_S"][sl]
            m = Gn > 0
            mean = np.where(m, GS / np.maximum(Gn, 1), np.nan)
            rad = snap["ucb_const"] / np.sqrt(np.maximum(Gn, 1))
            axf.vlines(cz[m], mean[m], np.minimum(mean[m] + rad[m], hi + pad), color="#9cc0ea",
                       lw=1.6, zorder=2, label="UCB width")
            axf.scatter(cz[m], mean[m], s=10, color=PHASE_COLOR[2], zorder=3,
                        label="shared bin mean S_j/n_j")
            best = int(np.nanargmax(np.where(m, mean, -np.inf))) if m.any() else None
            if best is not None:
                axf.scatter([cz[best]], [mean[best]], s=60, marker="*", color=INK, zorder=4)
            axf.set_title("Shared bin table on the index line z = ⟨x, θ̂₀⟩", fontsize=10,
                          color=INK, loc="left")
            axf.legend(loc="lower center", fontsize=7, frameon=False, ncol=3,
                       handletextpad=0.3, columnspacing=0.8)

            contrib, pend = snap["contrib"][:, sl], snap["pending"][:, sl]
            synced = contrib - pend
            bottom = np.zeros(nb)
            for i in range(self.N):
                axc.bar(cz, synced[i], width=D * 0.92, bottom=bottom, color=self.colors[i],
                        edgecolor="none")
                bottom += synced[i]
            for i in range(self.N):
                if pend[i].any():
                    axc.bar(cz, pend[i], width=D * 0.92, bottom=bottom, color=self.colors[i],
                            alpha=0.35, hatch="////", edgecolor=self.colors[i], lw=0)
                    bottom += pend[i]
            axc.set_ylim(0, max(1.0, float(bottom.max())) * 1.1)
            axc.text(0.01, 0.95, "pulls per bin, stacked by agent (hatched = not yet synced)",
                     transform=axc.transAxes, fontsize=7.5, color=INK2, va="top")
        plt_setp(axf, xticklabels=False)
        axf.tick_params(labelsize=8, colors=INK2)
        axc.tick_params(labelsize=8, colors=INK2)
        axc.set_xlabel("projected index z", fontsize=8.5, color=INK2)
        self._clean(axf)
        self._clean(axc)

    def _regret(self, snap):
        ax = self.ax_reg
        t = snap["t"]
        x = np.arange(1, t + 1)
        yi, yf = self.ind[t - 1], self.fedc[t - 1]
        # the axis grows with the run, so the early dynamics stay readable
        ymax = max(yi, yf, 50.0) * 1.3
        ax.plot(x, self.ind[:t], color=IND_COLOR, lw=2, ls="--")
        ax.plot(x, self.fedc[:t], color=FED_COLOR, lw=2.4)
        gap = 0.09 * ymax                       # keep the two end labels apart
        li, lf = yi, yf
        if abs(li - lf) < gap:
            mid = 0.5 * (li + lf)
            li, lf = (mid + gap / 2, mid - gap / 2) if yi >= yf else (mid - gap / 2, mid + gap / 2)
        ax.text(t, li, f"  {self.N}× independent  {yi:,.0f}", fontsize=8.5, color=INK2,
                va="center")
        ax.text(t, lf, f"  {self.ALG_NAME}  {yf:,.0f}", fontsize=8.5, color=INK, va="center",
                weight="bold")
        if self.rec.t_freeze and t >= self.rec.t_freeze:
            ax.axvline(self.rec.t_freeze, color=PHASE_COLOR[2], lw=1, ls="--")
        xmax = max(t * 1.45, 40)
        ax.set_xlim(0, min(xmax, self.T * 1.45))
        ax.set_ylim(0, ymax)
        ax.set_xlabel("round", fontsize=8.5, color=INK2)
        ax.set_ylabel("network regret Σᵢ Rᵢ(t)", fontsize=8.5, color=INK2)
        ax.tick_params(labelsize=8, colors=INK2)
        ratio = yi / max(yf, 1e-9)
        ax.set_title(f"Network regret · independent ÷ fed = {ratio:.1f}×",
                     fontsize=11, color=INK, loc="left")
        self._clean(ax)

    @staticmethod
    def _clean(ax):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
        ax.grid(True, color=GRID, lw=0.6, alpha=0.8)
        ax.set_axisbelow(True)


def plt_setp(ax, xticklabels=True):
    if not xticklabels:
        for lab in ax.get_xticklabels():
            lab.set_visible(False)
