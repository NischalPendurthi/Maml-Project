"""E24 -- how much of the communication is Phase 1, and does compressing it help?

Claim 2.1 of docs/claims-evidence.md.  Proposition 6 says Phase 1 costs O(N d)
scalars once while Phase 2 costs ~ N · N_bins · log(NT), so the Phase-1 share is
O(d / ((NT)^{1/3} log NT)): it only matters when d is comparable to (NT)^{1/3}.

Part A  share vs d   (N = 16, T = 10 000; d = 5 … 200), server and serverless (ring)
Part B  share vs N·T (d = 10; N = 4, 16; T = 2 500 … 40 000)
Part C  quantise the Phase-1 upload to b = 2 … 16 bits (d = 10 and d = 100):
        total-bit saving and regret change, against the exact 32-bit upload.

All runs: fixed Phase-1 length (pooled 960 at T = 10⁴, scaled ∝ (NT)^{2/3}),
event-triggered Phase 2 with gamma = 0.5.

Writes results/fig24_phase1_share.{png,pdf}, results/claims_e24.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from configs.decentralized import dec_config

GAMMA = 0.5
DS = pick([5, 10, 20, 50, 100, 200], [5, 20, 100])
NS = [4, 16]
TS = pick([2500, 10_000, 40_000], [2500, 10_000])
BITS = pick([2, 4, 8, 16], [2, 8])
D_QUANT = pick([10, 100], [10])
LINK = "quadratic"
NTR_SHARE = trials(5, 2)          # the share is nearly deterministic
NTR_QUANT = trials(20, 3)


def t0_for(N, T):
    return max(1, int(np.ceil(960 * (T / 10_000) ** (2 / 3) / N)))


def server(N, T, phase1="exact", phase1_kw=None):
    return dict(engine="fed", phase1=phase1, phase1_kw=phase1_kw or {}, phase2="event",
                phase2_kw=dict(gamma=GAMMA), freeze="fixed", T0=t0_for(N, T),
                bin_width="network")


def relay(N, T):
    return dec_config("ring", "tree", {}, "flood", {"gamma": GAMMA}, T0=t0_for(N, T),
                      bin_width="network")


def cell_fn(cell, names=None):
    part, d, N, T = cell
    if part == "quant":
        cfgs = {"exact": server(N, T)}
        cfgs.update({f"q{b}": server(N, T, "compressed", dict(compressor=dict(kind="quant", bits=b)))
                     for b in BITS})
        ntr = NTR_QUANT
    else:
        cfgs = {"server": server(N, T)}
        if part == "d":
            cfgs["relay"] = relay(N, T)
        ntr = NTR_SHARE
    cfgs = {k: v for k, v in cfgs.items() if names is None or k in names}
    out, _ = sweep(cfgs, ntr, N, T, LINK, d=d)
    return summarize(out)


def simulate():
    cells = [("d", d, 16, pick(10_000, 2500)) for d in DS]
    cells += [("T", 10, N, T) for N in NS for T in TS]
    cells += [("quant", d, 16, pick(10_000, 2500)) for d in D_QUANT]
    return run_cells("e24", cells, cell_fn)


def share(r):
    return r["bits1"] / r["bits"]


def plot(res):
    use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(14, 3.8))
    Td = pick(10_000, 2500)
    rows = []
    for key, col in (("server", "#2a78d6"), ("relay", "#eb6834")):
        p1 = np.array([res[("d", d, 16, Td)][key]["comm1"].mean() for d in DS])
        p2 = np.array([(res[("d", d, 16, Td)][key]["comm"] - res[("d", d, 16, Td)][key]["comm1"]).mean()
                       for d in DS])
        name = "server" if key == "server" else "serverless (ring, tree + flood)"
        a.plot(DS, p1, marker="o", color=col, label=f"{name}: Phase 1")
        a.plot(DS, p2, marker="s", ls="--", color=col, label=f"{name}: Phase 2")
        for d, x1, x2 in zip(DS, p1, p2):
            rows.append(["d sweep", name, d, 16, f"{16 * Td:,}", f"{x1:,.0f}", f"{x2:,.0f}",
                         f"{100 * x1 / (x1 + x2):.2f}%"])
        # where would Phase 1 catch up?  P1 is linear in d, P2 flat in d.
        dstar = DS[-1] * p2.mean() / p1[-1]
        a.plot([], [], " ", label=f"{name}: P1 = P2 at d ≈ {dstar:,.0f}")
    a.set(xscale="log", yscale="log", xlabel="context dimension d", ylabel="scalars sent",
          title=f"Phase 1 vs Phase 2 traffic (N = 16, T = {Td:,})")
    a.legend(fontsize=6.5)

    for N, col in zip(NS, ("#1baf7a", "#4a3aa7")):
        NT = N * np.array(TS)
        sh = np.array([mci(100 * share(res[("T", 10, N, T)]["server"])) for T in TS])
        b.errorbar(NT, sh[:, 0], sh[:, 1], marker="o", color=col, label=f"N = {N}")
        for T, s in zip(TS, sh):
            r = res[("T", 10, N, T)]["server"]
            rows.append(["T sweep", "server", 10, N, f"{N * T:,}", f"{r['comm1'].mean():,.0f}",
                         f"{(r['comm'] - r['comm1']).mean():,.0f}", f"{s[0]:.2f}%"])
    b.set(xscale="log", xlabel="N·T (d = 10)", ylabel="Phase-1 share of bits (%)",
          title="Phase-1 share shrinks with the horizon")
    b.legend()

    rows_q = []
    for d, col in zip(D_QUANT, ("#2a78d6", "#eb6834")):
        cell = res[("quant", d, 16, pick(10_000, 2500))]
        ex = cell["exact"]
        tot = ex["bits"].mean()
        p2_ex = (ex["bits"] - ex["bits1"]).mean()
        rows_q.append([d, 32, fmt(ex["R"]), "+0.0%", f"{ex['bits1'].mean():,.0f}", "0.000%",
                       "+0.0%", f"{100 * share(ex).mean():.2f}%"])
        xs, dreg, direct = [32], [0.0], [0.0]
        for bb in BITS:
            r = cell[f"q{bb}"]
            # direct: Phase-1 bits saved, as % of the exact run's total traffic.
            # indirect: change in Phase-2 bits, caused by the noisier frozen direction.
            dsave = 100 * (ex["bits1"].mean() - r["bits1"].mean()) / tot
            p2chg = 100 * ((r["bits"] - r["bits1"]).mean() / p2_ex - 1)
            dr = 100 * (r["R"].mean() / ex["R"].mean() - 1)
            xs.append(bb); dreg.append(dr); direct.append(dsave)
            rows_q.append([d, bb, fmt(r["R"]), f"{dr:+.1f}%", f"{r['bits1'].mean():,.0f}",
                           f"{dsave:.3f}%", f"{p2chg:+.1f}%", f"{100 * share(r).mean():.2f}%"])
        o = np.argsort(xs)
        c.plot(np.array(xs)[o], np.array(dreg)[o], marker="o", color=col,
               label=f"d = {d}: regret change")
        c.plot(np.array(xs)[o], np.array(direct)[o], marker="s", ls="--", color=col,
               label=f"d = {d}: bits saved by compressing Phase 1")
    c.axhline(0, color="#8a8984", lw=0.8)
    c.set_xscale("log", base=2)
    c.set(xlabel="bits per Phase-1 coordinate", ylabel="% vs exact 32-bit upload",
          title="Quantising Phase 1 (N = 16)")
    c.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig24_phase1_share")

    md_table(f"{OUT}/claims_e24.md", "E24: Phase-1 share of communication",
             f"Event-triggered Phase 2 (γ = {GAMMA}), fixed Phase-1 length, {LINK} link. "
             "Scalars as counted by the engines (index, count and sum per touched bin = 3).",
             ["sweep", "setting", "d", "N", "N·T", "Phase-1 scalars", "Phase-2 scalars",
              "Phase-1 share"], rows)
    with open(f"{OUT}/claims_e24.md", "a") as fh:
        fh.write(f"\n## Quantised Phase-1 upload (N = 16, {NTR_QUANT} paired trials)\n\n"
                 "'Phase-1 saving' = Phase-1 bits saved as % of the exact run's total bits "
                 "(the most compression of Phase 1 can ever buy). 'Phase-2 change' = how much "
                 "Phase-2 traffic moved because the frozen direction got noisier.\n\n"
                 "| d | bits | network regret | regret change | Phase-1 bits | Phase-1 saving | "
                 "Phase-2 change | Phase-1 share |\n|---|---|---|---|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows_q) + "\n")


def main():
    plot(simulate())


if __name__ == "__main__":
    main()
