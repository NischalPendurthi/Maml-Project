"""E23 -- what does losing the server cost, and how does it scale with the diameter?

Claim 1.4 of docs/claims-evidence.md.  Theorem 7 (sketch) says the relay version
pays the server rate PLUS an additive O(N · D · N_bins) term, D the graph diameter.
Here both run in the same DecTwoPhase engine, with the same seeds (paired trials),
the same pooled Phase-1 size and the same trigger gamma:

    server  exact pooling through a server + event-triggered server sync
    relay   spanning-tree pooling + event-triggered flooding of bin tables
            (Dec-ZoomSIB-Relay, the recommended serverless design)

Part A: N = 16 on graphs of growing diameter (complete 1, expander 3, hypercube 4,
        torus 4, ring 8, path 15): excess regret (relay − server) against D.
Part B: on the ring and the path, excess against the horizon N·T, log-log slope
        against the 1/3 that N_bins ∝ (NT)^{1/3} predicts.
Also reported: the bound's own magnitude N·D·N_bins, to show how loose it is.

Writes results/fig23_server_vs_serverless.{png,pdf}, results/claims_e23.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from configs.decentralized import dec_config

N = 16
GAMMA = 0.5
N0 = 960                                    # pooled Phase-1 samples at T = 10 000
GRAPHS = pick(["complete", "expander", "hypercube", "torus", "ring", "path"],
              ["complete", "ring", "path"])
T_MAIN = pick(10_000, 2500)
T_SWEEP = pick([2500, 5000, 10_000, 20_000, 40_000], [1250, 2500, 5000])
SWEEP_GRAPHS = ["ring", "path"]
LINKS = pick(["quadratic", "zigzag"], ["quadratic"])
NTR = trials(20, 3)
COLOR = {"ring": "#2a78d6", "path": "#eb6834", "quadratic": "#2a78d6", "zigzag": "#1baf7a"}


def t0_for(T):
    """Per-agent Phase-1 rounds: pooled size grows like (NT)^{2/3}, as the theory sets it."""
    return max(1, int(np.ceil(N0 * (T / 10_000) ** (2 / 3) / N)))


def cfgs(graph, T):
    t0 = t0_for(T)
    out = {"relay": dec_config(graph, "tree", {}, "flood", {"gamma": GAMMA}, T0=t0,
                               bin_width="network")}
    if graph == "complete":   # the server ignores the graph; run it once per (link, T)
        out["server"] = dec_config("complete", "server", {}, "server_event", {"gamma": GAMMA},
                                   T0=t0, bin_width="network")
    return out


def cell_fn(cell, names=None):
    _, link, graph, T = cell
    c = {k: v for k, v in cfgs(graph, T).items() if names is None or k in names}
    out, _ = sweep(c, NTR, N, T, link)
    return summarize(out, extra=dict(D=lambda x: x["diameter"], gap=lambda x: x["gap"]))


def simulate():
    cells = [("main", link, g, T_MAIN) for link in LINKS for g in dict.fromkeys(["complete"] + GRAPHS)]
    cells += [("sweep", LINKS[0], g, T) for T in T_SWEEP for g in ["complete"] + SWEEP_GRAPHS]
    return run_cells("e23", cells, cell_fn)


def excess(res, link, graph, T, kind):
    """Paired per-trial excess regret of the relay over the server."""
    s = res[(kind, link, "complete", T)]["server"]["R"]
    r = res[(kind, link, graph, T)]["relay"]["R"]
    return r - s, s


def plot(res):
    use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(14, 3.8))
    rows = []
    for link in LINKS:
        Ds, ex, ratios = [], [], []
        for g in GRAPHS:
            e, s = excess(res, link, g, T_MAIN, "main")
            r = res[("main", link, g, T_MAIN)]["relay"]
            D = r["D"][0]
            Ds.append(D)
            ex.append(mci(e))
            nb = r["N_bins"].mean()
            rows.append([link, g, f"{D:.0f}", f"{r['gap'][0]:.3f}", fmt(s), fmt(r["R"]),
                         fmt(e), f"{100 * e.mean() / s.mean():+.1f}%", f"{N * D * nb:,.0f}",
                         f"{res[('main', link, 'complete', T_MAIN)]['server']['comm'].mean():,.0f}",
                         f"{r['comm'].mean():,.0f}"])
        Ds, ex = np.array(Ds), np.array(ex)
        a.errorbar(Ds, ex[:, 0], ex[:, 1], marker="o", ls="none", capsize=2, color=COLOR[link],
                   label=f"{link}: relay − server (paired)")
        slope = float(np.sum(Ds * ex[:, 0]) / np.sum(Ds ** 2))
        xs = np.linspace(0, Ds.max() * 1.05, 50)
        a.plot(xs, slope * xs, "--", color=COLOR[link], lw=1,
               label=f"{link}: best fit ∝ D ({slope:.0f} per hop)")
        for g, D, y in zip(GRAPHS, Ds, ex[:, 0]):
            if link == LINKS[0]:
                a.annotate(g, (D, y), textcoords="offset points", xytext=(4, -10), fontsize=7)
    a.axhline(0, color="#8a8984", lw=0.8)
    a.set(xlabel="graph diameter D (N = 16)", ylabel="extra network regret without a server",
          title=f"Cost of no server vs diameter (T = {T_MAIN:,})")
    a.legend(fontsize=7)

    link = LINKS[0]
    rows2 = []
    for g in SWEEP_GRAPHS:
        NT = N * np.array(T_SWEEP)
        ex = np.array([mci(excess(res, link, g, T, "sweep")[0]) for T in T_SWEEP])
        rel = np.array([excess(res, link, g, T, "sweep")[0].mean() /
                        excess(res, link, g, T, "sweep")[1].mean() for T in T_SWEEP])
        b.errorbar(NT, ex[:, 0], ex[:, 1], marker="o", capsize=2, color=COLOR[g], label=g)
        pos = ex[:, 0] > 0
        sl = float(np.polyfit(np.log(NT[pos]), np.log(ex[pos, 0]), 1)[0]) if pos.sum() >= 2 else np.nan
        c.plot(NT, 100 * rel, marker="o", color=COLOR[g], label=g)
        for T, e, rr in zip(T_SWEEP, ex, rel):
            rows2.append([g, f"{N * T:,}", f"{e[0]:,.0f} ± {e[1]:,.0f}", f"{100 * rr:+.1f}%"])
        rows2.append([g, "fitted slope", f"{sl:.2f}", "(bound predicts 0.33)"])
        b.plot([], [], " ", label=f"{g}: slope {sl:.2f}")
    ref = NT ** (1 / 3)
    b.plot(NT, ref / ref[-1] * max(1, np.nanmax(ex[:, 0])), ":", color="#8a8984",
           label="slope 1/3 reference")
    b.set(xscale="log", yscale="log", xlabel="N·T", ylabel="relay − server regret",
          title="Excess vs horizon (log-log)")
    b.legend(fontsize=7)
    c.axhline(0, color="#8a8984", lw=0.8)
    c.set(xscale="log", xlabel="N·T", ylabel="excess regret (% of server)",
          title="Relative cost of no server")
    c.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig23_server_vs_serverless")

    intro = (f"N = {N}, pooled Phase-1 size {N0}·(T/10⁴)^(2/3), γ = {GAMMA}, Δ = (NT)^(-1/3), "
             f"{NTR} paired trials (same seeds for server and relay), mean ± 95% CI. "
             "'bound term' is N·D·N_bins, the additive term of Theorem 7 without constants.")
    md_table(f"{OUT}/claims_e23.md", "E23: server vs serverless (relay) across diameters", intro,
             ["link", "graph", "D", "spectral gap", "server regret", "relay regret",
              "excess (paired)", "excess %", "bound term N·D·N_bins", "server scalars",
              "relay scalars"], rows)
    with open(f"{OUT}/claims_e23.md", "a") as fh:
        fh.write(f"\n## Excess vs horizon ({link})\n\n| graph | N·T | excess | excess % |\n"
                 "|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(r) + " |" for r in rows2) + "\n")


def main():
    plot(simulate())


if __name__ == "__main__":
    main()
