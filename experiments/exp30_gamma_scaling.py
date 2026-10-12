"""E30 -- event-trigger threshold: constant gamma vs gamma = gamma0 / N.

Theorem 9 (docs/proofs/server.tex) proves the (NT)^{2/3} rate with gamma = gamma0 / N; for
a constant gamma its UCB term carries sqrt(1 + N gamma).  E22 used a constant gamma = 0.5.
This checks, at a fixed budget N·T, whether either choice loses regret against per-round
sync as N grows, and what each costs in Phase-2 sync rounds:

    sync1        sync every round (the reference)
    event_c      constant gamma = 0.5            (what E22 ran)
    event_big    constant gamma = 2              (stress test: N·gamma up to 32)
    event_n      gamma = gamma0 / N, gamma0 = 4  (the theorem; equals 0.5 at N = 8)

Writes results/fig30_gamma_scaling.{png,pdf} and results/claims_e30.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)

BUDGET = pick(160_000, 40_000)                 # total pulls N·T, as in E22
NS = pick([2, 4, 8, 16], [2, 16])
LINKS = pick(["quadratic", "zigzag"], ["quadratic"])
N0 = 960                                       # pooled Phase-1 samples, every N (as in E22)
GAMMA0 = 4.0
NTR = trials(20, 3)

COLOR = dict(sync1="#2a78d6", event_c="#1baf7a", event_big="#d6662a", event_n="#4a3aa7")
LABEL = dict(sync1="sync every round", event_c="event, γ = 0.5", event_big="event, γ = 2",
             event_n=f"event, γ = {GAMMA0:g}/N")


def fed(phase2, phase2_kw, N):
    return dict(engine="fed", phase1="exact", phase2=phase2, phase2_kw=phase2_kw,
                freeze="fixed", T0=max(1, int(np.ceil(N0 / N))), bin_width="network")


def configs(N):
    return {"sync1": fed("periodic", dict(every=1), N),
            "event_c": fed("event", dict(gamma=0.5), N),
            "event_big": fed("event", dict(gamma=2.0), N),
            "event_n": fed("event", dict(gamma=GAMMA0 / N), N)}


def cell_fn(cell, names=None):
    link, N = cell
    cfgs = {k: v for k, v in configs(N).items() if names is None or k in names}
    out, _ = sweep(cfgs, NTR, N, BUDGET // N, link)
    return summarize(out)


def plot(res):
    use_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for link, ls in zip(LINKS, ["-", "--"]):
        for key in ("event_c", "event_big", "event_n"):
            ratio = [res[(link, N)][key]["R"].mean() / res[(link, N)]["sync1"]["R"].mean()
                     for N in NS]
            syncs = [(res[(link, N)][key]["rounds"] - res[(link, N)][key]["rounds1"]).mean()
                     for N in NS]
            lab = f"{LABEL[key]} ({link})"
            axes[0].plot(NS, ratio, ls, marker="o", color=COLOR[key], label=lab)
            axes[1].plot(NS, syncs, ls, marker="o", color=COLOR[key], label=lab)
    axes[0].axhline(1, color=COLOR["sync1"], lw=1, label=LABEL["sync1"])
    axes[0].set(xscale="log", xlabel="N (agents)", ylabel="regret ÷ per-round sync",
                title=f"Regret cost of the trigger (N·T = {BUDGET:,})")
    axes[1].set(xscale="log", yscale="log", xlabel="N (agents)", ylabel="Phase-2 sync rounds",
                title="Communication of the trigger")
    for ax in axes:
        ax.set_xticks(NS, [str(n) for n in NS])
        ax.set_xticks([], minor=True)
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig30_gamma_scaling")

    rows = []
    for link in LINKS:
        for N in NS:
            ref = res[(link, N)]["sync1"]["R"].mean()
            for key in ("sync1", "event_c", "event_big", "event_n"):
                r = res[(link, N)][key]
                gamma = {"sync1": "–", "event_c": "0.5", "event_big": "2",
                         "event_n": f"{GAMMA0 / N:g}"}[key]
                ngam = "–" if key == "sync1" else f"{N * float(gamma):g}"
                rows.append([link, N, LABEL[key], gamma, ngam, fmt(r["R"]),
                             f"{r['R'].mean() / ref:.3f}",
                             f"{(r['rounds'] - r['rounds1']).mean():,.0f}"])
    intro = (f"Fixed budget N·T = {BUDGET:,}, pooled Phase-1 size {N0}, Δ = (NT)^(-1/3), "
             f"{NTR} paired trials, mean ± 95% CI. The bound's UCB term scales with "
             f"sqrt(1 + N·γ).")
    md_table(f"{OUT}/claims_e30.md", "E30: constant γ vs γ = γ0/N", intro,
             ["link", "N", "configuration", "γ", "N·γ", "network regret", "÷ sync1",
              "sync rounds"], rows)


def main():
    cells = [(link, N) for link in LINKS for N in NS]
    plot(run_cells("e30", cells, cell_fn))


if __name__ == "__main__":
    main()
