"""E22 -- is the server setting anything more than "one agent with N·T pulls"?

Claim 1.1 of docs/claims-evidence.md.  A fixed TOTAL budget of N·T pulls is spent
either by one ZoomSIB-UCB agent over N·T rounds or by N agents over T rounds:

    single      one agent, horizon N·T
    sync1       N agents, server sync every round (the ideal batched learner)
    event       N agents, event-triggered sync, gamma = 0.5 (Fed-ZoomSIB-SS)
    independent N agents, no communication (each runs ZoomSIB-UCB on T rounds)

All federated runs use the network bin width Delta = (NT)^{-1/3}, the bin width the
single agent uses at horizon N·T, and the same POOLED Phase-1 size n0 = N·T0, so the
single agent and the network see exactly the same statistical problem.  If the
server setting is "just more data", the regret-vs-total-pulls curves coincide.

Part 2 (claim 1.3): for N = 8 and growing T, count Phase-2 sync rounds of the
event-triggered server and compare them with Theorem 12's bound
N_bins · (1 + log_{1+gamma}(NT)) and with per-round sync (T − T0 rounds).

Writes results/fig22_single_vs_network.{png,pdf}, fig22b_sync_rounds.{png,pdf},
results/claims_e22.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells,
                           save, summarize, sweep, trials, use_style)

BUDGET = pick(160_000, 40_000)                 # total pulls N·T
NS = pick([1, 2, 4, 8, 16], [1, 4, 16])
LINKS = pick(["quadratic", "zigzag"], ["quadratic"])
N0 = 960                                       # pooled Phase-1 samples, every N
GAMMA = 0.5
NTR = trials(20, 3)
P = 100                                        # points per regret curve

T_SWEEP = pick([1250, 2500, 5000, 10_000, 20_000, 40_000], [1250, 5000])
N_SWEEP = 8

COLOR = dict(single="#4a3aa7", sync1="#2a78d6", event="#1baf7a", independent="#8a8984")
LABEL = dict(single="1 agent, horizon N·T", sync1="N agents, sync every round",
             event=f"N agents, event-triggered (γ={GAMMA})", independent="N independent agents")


def fed(phase2, phase2_kw, N):
    return dict(engine="fed", phase1="exact", phase2=phase2, phase2_kw=phase2_kw,
                freeze="fixed", T0=max(1, int(np.ceil(N0 / N))), bin_width="network")


def configs(N):
    if N == 1:
        return {"single": fed("periodic", dict(every=1), 1)}
    return {"sync1": fed("periodic", dict(every=1), N),
            "event": fed("event", dict(gamma=GAMMA), N),
            "independent": dict(engine="independent")}


def cell_fn(cell, names=None):
    kind, link, N = cell
    if kind == "budget":
        T = BUDGET // N
        cfgs = {k: v for k, v in configs(N).items() if names is None or k in names}
        out, grid = sweep(cfgs, NTR, N, T, link, record_every=max(1, T // P))
        res = summarize(out, keep_curves=True)
        for r in res.values():
            r["pulls"] = np.asarray(grid) * N
        return res
    T = N                                   # kind == "horizon": cell = ("horizon", link, T)
    cfgs = {"event": fed("event", dict(gamma=GAMMA), N_SWEEP),
            "sync1": fed("periodic", dict(every=1), N_SWEEP)}
    out, _ = sweep(cfgs, NTR, N_SWEEP, T, link)
    return summarize(out)


def simulate():
    cells = [("budget", link, N) for link in LINKS for N in NS]
    cells += [("horizon", LINKS[0], T) for T in T_SWEEP]
    return run_cells("e22", cells, cell_fn)


def plot(res):
    use_style()
    nmax = max(NS)
    fig, axes = plt.subplots(len(LINKS), 2, figsize=(10, 3.4 * len(LINKS)), squeeze=False)
    for row, link in zip(axes, LINKS):
        ax = row[0]
        for key, N in [("single", 1), ("sync1", nmax), ("event", nmax), ("independent", nmax)]:
            r = res[("budget", link, N)][key]
            m = r["net"].mean(axis=0)
            h = 1.96 * r["net"].std(axis=0, ddof=1) / np.sqrt(len(r["net"]))
            ln, = ax.plot(r["pulls"], m, color=COLOR[key],
                          label=LABEL[key] + ("" if key == "single" else f" (N={N})"))
            ax.fill_between(r["pulls"], m - h, m + h, color=ln.get_color(), alpha=0.15, lw=0)
        ax.set(xlabel="total pulls in the network", ylabel="cumulative network regret",
               title=f"{link}: same N·T = {BUDGET:,} pulls")
        ax.legend(loc="upper left")
        ax = row[1]
        single = res[("budget", link, 1)]["single"]["R"]
        m1, h1 = mci(single)
        ax.axhspan(m1 - h1, m1 + h1, color=COLOR["single"], alpha=0.15, lw=0)
        ax.axhline(m1, color=COLOR["single"], label=LABEL["single"])
        for key in ("sync1", "event", "independent"):
            ns = [N for N in NS if N > 1]
            ms = np.array([mci(res[("budget", link, N)][key]["R"]) for N in ns])
            ax.errorbar(ns, ms[:, 0], ms[:, 1], color=COLOR[key], marker="o", ms=4,
                        capsize=2, label=LABEL[key])
        ax.set(xscale="log", yscale="log", xlabel="N (agents)", ylabel="final network regret",
               title="Final regret at fixed N·T")
        ax.set_xticks(NS, [str(n) for n in NS])
        ax.legend(loc="upper left")
    fig.tight_layout()
    save(fig, "fig22_single_vs_network")

    # Part 2: sync rounds vs horizon
    link = LINKS[0]
    Ts = np.array(T_SWEEP)
    ev = [res[("horizon", link, T)]["event"] for T in Ts]
    s1 = [res[("horizon", link, T)]["sync1"] for T in Ts]
    syncs = np.array([mci(r["rounds"] - r["rounds1"]) for r in ev])
    per_round = np.array([mci(r["rounds"] - r["rounds1"]) for r in s1])
    nbins = np.array([r["N_bins"].mean() for r in ev])
    NT = N_SWEEP * Ts
    bound = nbins * (1 + np.log(NT) / np.log(1 + GAMMA))
    trig = np.array([mci(r["trig_max"]) for r in ev])
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.6))
    a.errorbar(NT, syncs[:, 0], syncs[:, 1], marker="o", color=COLOR["event"],
               label="event-triggered: measured sync rounds")
    a.plot(NT, bound, "--", color=COLOR["event"], label="Thm 12 bound  N_bins(1+log₁₊ᵧ NT)")
    a.plot(NT, per_round[:, 0], color=COLOR["sync1"], marker="s", ms=4,
           label="sync every round (T − T0)")
    a.set(xscale="log", yscale="log", xlabel="N·T (N = 8)", ylabel="Phase-2 communication rounds",
          title="Sync rounds: logarithmic vs linear")
    a.legend()
    b.errorbar(np.log(NT) / np.log(1 + GAMMA), trig[:, 0], trig[:, 1], marker="o",
               color=COLOR["event"], label="max syncs triggered by one bin")
    x = np.log(NT) / np.log(1 + GAMMA)
    b.plot(x, 1 + x, "--", color="#8a8984", label="bound 1 + log₁₊ᵧ(NT)")
    b.set(xlabel="log₁₊ᵧ(NT)", ylabel="syncs triggered by the busiest bin",
          title="Per-bin syncs (Theorem 12)")
    b.legend()
    fig.tight_layout()
    save(fig, "fig22b_sync_rounds")

    rows = []
    for link in LINKS:
        single = res[("budget", link, 1)]["single"]["R"]
        rows.append([link, 1, "single agent", fmt(single), "1.000", "–"])
        for N in [n for n in NS if n > 1]:
            for key in ("sync1", "event", "independent"):
                r = res[("budget", link, N)][key]
                ratio = r["R"].mean() / single.mean()
                sync = "–" if key == "independent" else f"{(r['rounds'] - r['rounds1']).mean():,.0f}"
                rows.append([link, N, LABEL[key], fmt(r["R"]), f"{ratio:.3f}", sync])
    rows2 = [[f"{N_SWEEP * T:,}", f"{nb:.0f}", f"{s[0]:,.1f}", f"{bd:,.0f}", f"{p[0]:,.0f}",
              f"{t[0]:.1f}", f"{1 + np.log(N_SWEEP * T) / np.log(1 + GAMMA):.1f}"]
             for T, nb, s, bd, p, t in zip(Ts, nbins, syncs, bound, per_round, trig)]
    intro = (f"Total budget N·T = {BUDGET:,} pulls, pooled Phase-1 size {N0}, "
             f"Δ = (NT)^(-1/3), {NTR} paired trials, mean ± 95% CI. Ratio = regret ÷ single agent."
             f" 'sync rounds' = Phase-2 communication rounds.")
    md_table(f"{OUT}/claims_e22.md", "E22: one agent at horizon N·T vs N agents at horizon T",
             intro, ["link", "N", "configuration", "network regret", "ratio to single",
                     "sync rounds"], rows)
    with open(f"{OUT}/claims_e22.md", "a") as fh:
        fh.write("\n## Sync rounds vs horizon (N = 8, event-triggered, γ = 0.5)\n\n"
                 "| N·T | N_bins | measured syncs | Thm 12 bound | per-round sync | "
                 "max syncs by one bin | per-bin bound |\n|---|---|---|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(r) + " |" for r in rows2) + "\n")


def main():
    plot(simulate())                 # cached cells are reused, so this is also the replot path


if __name__ == "__main__":
    main()
