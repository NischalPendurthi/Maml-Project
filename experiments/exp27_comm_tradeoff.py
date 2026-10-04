"""E27 -- the regret–communication trade-off of Phase 2: how few syncs are enough?

Claim 3.2 of docs/claims-evidence.md.  Every Phase-2 schedule is a point
(communication spent, regret).  We map the frontier for four families:

    periodic   sync every c rounds
    event      event-triggered, threshold gamma (Fed-ZoomSIB-SS)
    minimax    M-batch Perchet grid (fixed sync rounds, chosen in advance)
    geometric  M-batch geometric grid

Batched Lipschitz bandits need only O(log log T) batches for the optimal rate
(Feng, Huang & Wang 2022).  If the federated problem behaves the same way, a
handful of well-placed syncs should match per-round sync -- far fewer than the
event-triggered O(N_bins log NT) bound.

Part B repeats the minimax grid at three horizons and reports M*, the smallest
number of batches within 5% of per-round sync, next to log log(NT).

Writes results/fig27_comm_tradeoff.{png,pdf}, results/claims_e27.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from src.fed.phase2.scheduled import grid

N = 8
GAMMA_GRID = pick([0.05, 0.1, 0.25, 0.5, 1, 2, 4, 8, 16], [0.1, 0.5, 4])
PERIODS = pick([1, 2, 5, 10, 25, 50, 100, 250, 1000, 2500], [1, 10, 250])
MS = pick([1, 2, 3, 4, 5, 6, 8], [1, 2, 4])
LINKS = pick(["quadratic", "zigzag"], ["quadratic"])
T_MAIN = pick(10_000, 2500)
T_B = pick([2500, 10_000, 40_000], [1250, 2500])
NTR = trials(20, 3)
FAM_COLOR = dict(periodic="#2a78d6", event="#1baf7a", minimax="#eb6834", geometric="#4a3aa7")


def t0_for(T):
    return max(1, int(np.ceil(960 * (T / 10_000) ** (2 / 3) / N)))


def base(T, phase2, kw):
    return dict(engine="fed", phase1="exact", phase2=phase2, phase2_kw=kw, freeze="fixed",
                T0=t0_for(T), bin_width="network")


def configs(T, families):
    t0 = t0_for(T)
    c = {}
    if "periodic" in families:
        c.update({f"periodic_{p}": base(T, "periodic", dict(every=p)) for p in PERIODS})
    if "event" in families:
        c.update({f"event_{g}": base(T, "event", dict(gamma=g)) for g in GAMMA_GRID})
    for fam in ("minimax", "geometric"):
        if fam in families:
            c.update({f"{fam}_{M}": base(T, "scheduled", dict(times=grid(fam, M, t0, T)))
                      for M in MS})
    c["none"] = base(T, "none", {})
    return c


def cell_fn(cell, names=None):
    part, link, T = cell
    fams = ("periodic", "event", "minimax", "geometric") if part == "main" else ("minimax", "periodic")
    cfgs = configs(T, fams)
    if part != "main":
        cfgs = {k: v for k, v in cfgs.items() if k.startswith("minimax") or k in ("periodic_1", "none")}
    cfgs = {k: v for k, v in cfgs.items() if names is None or k in names}
    out, _ = sweep(cfgs, NTR, N, T, link)
    return summarize(out)


def family(name):
    return name.split("_")[0]


def plot(res):
    use_style()
    fig, axes = plt.subplots(1, len(LINKS) + 1, figsize=(5.2 * (len(LINKS) + 1), 4))
    rows = []
    for ax, link in zip(axes, LINKS):
        cell = res[("main", link, T_MAIN)]
        ref = cell["periodic_1"]["R"].mean()
        for fam in FAM_COLOR:
            keys = [k for k in cell if family(k) == fam]
            pts = sorted((max(1.0, (cell[k]["rounds"] - cell[k]["rounds1"]).mean()),
                          cell[k]["R"].mean() / ref, k) for k in keys)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", ms=3.5,
                    color=FAM_COLOR[fam], label=fam)
            for k in keys:
                r = cell[k]
                rows.append([link, k, fmt(r["R"]), f"{r['R'].mean() / ref:.3f}",
                             f"{(r['rounds'] - r['rounds1']).mean():,.1f}", f"{r['bits'].mean():,.0f}"])
        nr = cell["none"]["R"].mean() / ref
        ax.axhline(nr, color="#8a8984", ls=":", lw=1, label=f"no sharing ({nr:.2f})")
        ax.axhline(1, color="#1a1a1a", lw=0.8)
        ax.set(xscale="log", xlabel="Phase-2 sync rounds", ylabel="regret ÷ sync every round",
               title=f"{link}: N = {N}, T = {T_MAIN:,}")
        ax.legend(fontsize=7)

    ax = axes[-1]
    link = LINKS[0]
    rows_b = []
    for T, col in zip(T_B, ("#2a78d6", "#1baf7a", "#eb6834")):
        cell = res[("B", link, T)]
        ref = cell["periodic_1"]["R"]
        ms, ys = [], []
        for M in MS:
            r = cell[f"minimax_{M}"]["R"]
            ms.append(M)
            ys.append(mci(r / ref.mean()))
        ys = np.array(ys)
        ax.errorbar(ms, ys[:, 0], ys[:, 1], marker="o", capsize=2, color=col, label=f"N·T = {N * T:,}")
        within = [M for M, y in zip(ms, ys[:, 0]) if y <= 1.05]
        mstar = min(within) if within else None
        rows_b.append([f"{N * T:,}", mstar if mstar else f"> {max(MS)}",
                       f"{np.log(np.log(N * T)):.2f}",
                       " / ".join(f"{y:.2f}" for y in ys[:, 0])])
    ax.axhline(1.05, color="#8a8984", ls=":", lw=1, label="within 5% of per-round sync")
    ax.set(xlabel="batches M (minimax grid)", ylabel="regret ÷ sync every round",
           title=f"How many batches? ({link})")
    ax.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig27_comm_tradeoff")
    md_table(f"{OUT}/claims_e27.md", "E27: regret vs Phase-2 communication",
             f"N = {N}, T = {T_MAIN:,}, fixed Phase-1 length, {NTR} paired trials. Ratio is to "
             "sync every round. Sync rounds exclude Phase 1.",
             ["link", "schedule", "network regret", "ratio", "sync rounds", "total bits"], rows)
    with open(f"{OUT}/claims_e27.md", "a") as fh:
        fh.write(f"\n## Batches needed (minimax grid, {link})\n\nM* = smallest M within 5% of "
                 "per-round sync. M counts the final round, so M batches = M − 1 useful syncs.\n\n"
                 "| N·T | M* | log log(NT) | ratio for M = " + ", ".join(map(str, MS)) +
                 " |\n|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows_b) + "\n")


def main():
    cells = [("main", link, T_MAIN) for link in LINKS] + [("B", LINKS[0], T) for T in T_B]
    plot(run_cells("e27", cells, cell_fn))


if __name__ == "__main__":
    main()
