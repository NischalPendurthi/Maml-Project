"""E31 -- the protocol we prove things about vs the protocol we run.

docs/proofs/serverless.tex analyses Phase 2 with SYNCHRONISED EPOCHS (src/dec/phase2/epoch.py):
every agent acts on the same delayed epoch table plus its own pulls, which is what makes
the confidence lemma lose no √N.  The experiments so far (E23) ran the flood relay
(src/dec/phase2/flood.py), where each agent republishes on its own trigger.  This checks
open items (c) and (d) of the proofs:

Part A: N = 16 on graphs of growing diameter, same seeds as E23 (paired):
        server | flood relay (code) | epoch protocol (proved) | epoch, pipelined (not proved).
        Excess regret over the server, scalars, number of epochs against Lemma 22's bound
        1 + N_b(1 + log_{1+γ} NT), and Theorem 17's delay term N_b·N·(γ + 4D) without constants.
Part B: the trigger threshold under flooding (item (c)): γ ∈ {1/N, 0.5, 2} for the flood relay
        and the epoch protocol on the torus and the ring.  Theorem 17 has √(1 + Nγ).

Writes results/fig31_epoch_protocol.{png,pdf}, results/claims_e31.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from configs.decentralized import dec_config

N = 16
GAMMA = 0.5
N0 = 960                                    # pooled Phase-1 samples at T = 10 000 (as E23)
T = pick(10_000, 2500)
GRAPHS = pick(["complete", "expander", "hypercube", "torus", "ring", "path"],
              ["complete", "ring"])
LINKS = pick(["quadratic", "zigzag"], ["quadratic"])
GAMMAS = [1 / N, 0.5, 2.0]
B_GRAPHS = pick(["torus", "ring"], ["ring"])
NTR = trials(20, 3)
T0 = max(1, int(np.ceil(N0 * (T / 10_000) ** (2 / 3) / N)))

PROTO = {"flood": ("flood", {}), "epoch": ("epoch", {}), "pipe": ("epoch", {"pipeline": True})}
LABEL = {"flood": "flood relay (code, E23)", "epoch": "synchronised epochs (proved)",
         "pipe": "epochs, pipelined (not proved)", "server": "server"}
COLOR = {"flood": "#2a78d6", "epoch": "#eb6834", "pipe": "#eda100", "server": "#4a3aa7"}


def dec(graph, key, gamma):
    p2, kw = PROTO[key]
    return dec_config(graph, "tree", {}, p2, {**kw, "gamma": gamma}, T0=T0, bin_width="network")


def server(gamma=GAMMA):
    return dec_config("complete", "server", {}, "server_event", {"gamma": gamma}, T0=T0,
                      bin_width="network")


def cfgs(cell):
    kind, link, graph = cell[:3]
    if kind == "A":
        out = {k: dec(graph, k, GAMMA) for k in PROTO}
        if graph == "complete":
            out["server"] = server()
        return out
    gamma = cell[3]
    return {k: dec(graph, k, gamma) for k in ("flood", "epoch")}


def cell_fn(cell, names=None):
    c = {k: v for k, v in cfgs(cell).items() if names is None or k in names}
    out, _ = sweep(c, NTR, N, T, cell[1])
    return summarize(out, extra=dict(D=lambda x: x["diameter"]))


def simulate():
    cells = [("A", link, g) for link in LINKS for g in dict.fromkeys(["complete"] + GRAPHS)]
    cells += [("B", LINKS[0], g, gm) for g in B_GRAPHS for gm in GAMMAS]
    return run_cells("e31", cells, cell_fn)


def epochs(r):
    return r["rounds"] - r["rounds1"]


def plot(res):
    use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(14, 3.8))
    link = LINKS[0]
    srv = res[("A", link, "complete")]["server"]
    rows = []
    for k in PROTO:
        Ds, ex, sc = [], [], []
        for g in GRAPHS:
            r = res[("A", link, g)][k]
            e = r["R"] - srv["R"]
            Ds.append(r["D"][0])
            ex.append(mci(e))
            sc.append(r["comm"].mean())
        ex = np.array(ex)
        a.errorbar(Ds, ex[:, 0], ex[:, 1], marker="o", capsize=2, color=COLOR[k], label=LABEL[k])
        c.plot(Ds, sc, marker="o", color=COLOR[k], label=LABEL[k])
    c.axhline(srv["comm"].mean(), color=COLOR["server"], lw=1, ls="--", label=LABEL["server"])
    a.axhline(0, color="#8a8984", lw=0.8)
    a.set(xlabel="graph diameter D (N = 16)", ylabel="extra regret over the server (paired)",
          title=f"Cost of no server, by protocol (T = {T:,})")
    a.legend(fontsize=7)
    c.set(yscale="log", xlabel="graph diameter D", ylabel="scalars sent",
          title="Communication (same accounting)")
    c.legend(fontsize=7)

    for g, ls in zip(B_GRAPHS, ["-", "--"]):
        for k in ("flood", "epoch"):
            ref = res[("B", link, g, 0.5)][k]["R"].mean()
            ratio = [res[("B", link, g, gm)][k]["R"].mean() / ref for gm in GAMMAS]
            b.plot([N * gm for gm in GAMMAS], ratio, ls, marker="o", color=COLOR[k],
                   label=f"{LABEL[k]}, {g}")
    nx = np.array([N * gm for gm in GAMMAS])
    b.plot(nx, np.sqrt(1 + nx) / np.sqrt(1 + N * 0.5), ":", color="#8a8984",
           label="√(1+Nγ) of Theorem 17 (scaled)")
    b.set(xscale="log", xlabel="N·γ", ylabel="regret ÷ regret at γ = 0.5",
          title="Trigger threshold under flooding")
    b.legend(fontsize=6)
    fig.tight_layout()
    save(fig, "fig31_epoch_protocol")

    for link in LINKS:
        srv = res[("A", link, "complete")]["server"]
        for g in GRAPHS:
            for k in PROTO:
                r = res[("A", link, g)][k]
                D = r["D"][0]
                nb = r["N_bins"].mean()
                e = r["R"] - srv["R"]
                ebound = 1 + nb * (1 + np.log(N * T) / np.log(1 + GAMMA)) if k == "epoch" else np.nan
                rows.append([link, g, f"{D:.0f}", LABEL[k], fmt(r["R"]), fmt(e),
                             f"{100 * e.mean() / srv['R'].mean():+.1f}%", f"{r['comm'].mean():,.0f}",
                             f"{epochs(r).mean():,.0f}",
                             "–" if np.isnan(ebound) else f"{ebound:,.0f}",
                             f"{nb * N * (GAMMA + 4 * D):,.0f}" if k == "epoch" else "–",
                             f"{nb * N * np.sqrt(GAMMA + 4 * D):,.0f}" if k == "epoch" else "–"])
    intro = (f"N = {N}, T = {T:,}, pooled Phase-1 size {N0}, γ = {GAMMA}, Δ = (NT)^(-1/3), "
             f"{NTR} paired trials (same seeds as E23), mean ± 95% CI. Server: regret "
             + ", ".join(f"{fmt(res[('A', l, 'complete')]['server']['R'])} ({l})" for l in LINKS)
             + f", scalars {res[('A', LINKS[0], 'complete')]['server']['comm'].mean():,.0f}. "
             "'syncs' counts epochs for the epoch protocols and update rounds for the flood relay. "
             "'Lemma 22' is the bound 1 + N_b(1 + log_{1+γ} NT) on the number of epochs; "
             "'Thm 17 delay' is N_b·N·(γ + 4D), the delay term without constants, and 'Thm 18 delay' "
             "N_b·N·√(γ + 4D), the sharper one (Theorem 18) without constants. Scalars use "
             "flood.py's accounting (one delivery per receiving agent).")
    md_table(f"{OUT}/claims_e31.md", "E31: synchronised epochs (proved) vs flood relay (run)",
             intro, ["link", "graph", "D", "protocol", "regret", "excess over server",
                     "excess %", "scalars", "syncs", "Lemma 22", "Thm 17 delay", "Thm 18 delay"], rows)
    with open(f"{OUT}/claims_e31.md", "a") as fh:
        fh.write("\n## Growth of the excess with the diameter (log-log slope over the graphs)\n\n"
                 "| link | protocol | slope in D |\n|---|---|---|\n")
        for link in LINKS:
            srv = res[("A", link, "complete")]["server"]
            Ds = np.array([res[("A", link, g)]["flood"]["D"][0] for g in GRAPHS])
            for k in PROTO:
                ex = np.array([(res[("A", link, g)][k]["R"] - srv["R"]).mean() for g in GRAPHS])
                sl = np.polyfit(np.log(Ds), np.log(ex), 1)[0]
                fh.write(f"| {link} | {LABEL[k]} | {sl:.2f} |\n")
            fh.write(f"| {link} | Thm 17 shape N·(γ+4D) | "
                     f"{np.polyfit(np.log(Ds), np.log(GAMMA + 4 * Ds), 1)[0]:.2f} |\n")
            fh.write(f"| {link} | Thm 18 shape N·√(γ+4D) | "
                     f"{np.polyfit(np.log(Ds), np.log(np.sqrt(GAMMA + 4 * Ds)), 1)[0]:.2f} |\n")
    rows2 = []
    for g in B_GRAPHS:
        for k in ("flood", "epoch"):
            ref = res[("B", LINKS[0], g, 0.5)][k]["R"].mean()
            for gm in GAMMAS:
                r = res[("B", LINKS[0], g, gm)][k]
                rows2.append([g, LABEL[k], f"{gm:g}", f"{N * gm:g}", fmt(r["R"]),
                              f"{r['R'].mean() / ref:.3f}", f"{np.sqrt(1 + N * gm):.2f}",
                              f"{r['comm'].mean():,.0f}", f"{epochs(r).mean():,.0f}"])
    with open(f"{OUT}/claims_e31.md", "a") as fh:
        fh.write(f"\n## Part B: trigger threshold under flooding ({LINKS[0]})\n\n"
                 "| graph | protocol | γ | N·γ | regret | ÷ γ = 0.5 | √(1+Nγ) | scalars | syncs |\n"
                 "|---|---|---|---|---|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(r) + " |" for r in rows2) + "\n")


def main():
    plot(simulate())


if __name__ == "__main__":
    main()
