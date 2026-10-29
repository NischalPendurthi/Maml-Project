"""E36 -- what the delay term really depends on: diameter / farness, horizon, number of arms.

Two refinements of the delay analysis in docs/proofs/serverless.tex predict:
  * synchronised epochs: extra regret over the server = O(N·Λ·K), with NO dependence on the
    horizon T or the number of bins (a pull into bin j needs an arm in bin j, and there are
    only K arms per agent-round);
  * the published-only relay (src/dec/phase2/flood.py, own=False), which we can now analyse
    without the √N loss: extra regret = O(K·(F + N)), F = Σ_k dist(i, k) the farness.
It also asks whether the provable published-only relay is as good as the relay we ran (E23).
Theorem 27 now covers every γ (the √(1+Nγ) factor sits in the UCB term), so the published-only
relay at γ = 0.5 is the proved protocol with the flood relay's communication.

Part A  graphs of growing diameter (N = 16, T = 10 000, K = 20)
Part B  horizon T ∈ {2 500 … 20 000} on the ring: the predictions say flat in T
Part C  number of arms K ∈ {5, 10, 20, 40} on the ring: the predictions say growing with K

Writes results/fig36_delay_shape.{png,pdf}, results/claims_e36.md.
"""

from __future__ import annotations

from claims_common import (D as DIM, OUT, SIGMA, fmt, md_table, mci, np, pick, plt, run_cells,
                           save, summarize, trials, use_style)
from configs.decentralized import dec_config

from src.dec.graph import Graph
from src.dec.netbaselines import distances
from src.fed import run_fed_sweep

N = 16
GAMMA = 0.5
N0 = 960
LINK = "quadratic"
GRAPHS = pick(["complete", "expander", "torus", "ring", "path"], ["complete", "ring"])
TS = pick([2500, 5000, 10_000, 20_000], [1250, 2500])
KS = pick([5, 10, 20, 40], [5, 20])
T_MAIN = pick(10_000, 2500)
K_MAIN = 20
NTR = trials(10, 2)

PROTO = {"flood": ("flood", {"gamma": GAMMA}),                         # the relay we ran (E23)
         "pub": ("flood", {"gamma": GAMMA, "own": False}),            # published-only relay
         "pub_small": ("flood", {"gamma": 0.5 / N, "own": False}),    # ... with Nγ = 1/2 (rate-optimal bound)
         "epoch": ("epoch", {"gamma": GAMMA})}                        # synchronised epochs
LABEL = {"flood": "flood relay (run in E23)", "pub": "published-only relay, γ = 0.5 (proved)",
         "pub_small": "published-only relay, γ = 1/(2N) (proved)", "epoch": "synchronised epochs (proved)"}
COLOR = {"flood": "#2a78d6", "pub": "#1baf7a", "pub_small": "#4a3aa7", "epoch": "#eb6834"}


def t0_for(T):
    return max(1, int(np.ceil(N0 * (T / 10_000) ** (2 / 3) / N)))


def farness(graph):
    dist = distances(Graph(graph, N).A0)
    return dist.sum(axis=1).mean(), dist.max()


def cfgs(graph, T, keys):
    t0 = t0_for(T)
    c = {k: dec_config(graph, "tree", {}, PROTO[k][0], PROTO[k][1], T0=t0, bin_width="network")
         for k in keys}
    c["server"] = dec_config("complete", "server", {}, "server_event", {"gamma": GAMMA}, T0=t0,
                             bin_width="network")
    return c


def cell_fn(cell, names=None):
    part, graph, T, K = cell
    keys = list(PROTO) if part == "A" else ["flood", "pub", "pub_small", "epoch"]
    c = {k: v for k, v in cfgs(graph, T, keys).items() if names is None or k in names}
    out, _ = run_fed_sweep(c, NTR, N, DIM, K, T, LINK, sigma=SIGMA, record_every=T, progress=False)
    return summarize(out, extra=dict(D=lambda x: x["diameter"]))


def excess(r, k):
    return r[k]["R"] - r["server"]["R"]


def main():
    cells = [("A", g, T_MAIN, K_MAIN) for g in GRAPHS]
    cells += [("B", "ring", T, K_MAIN) for T in TS]
    cells += [("C", "ring", T_MAIN, K) for K in KS]
    res = run_cells("e36", cells, cell_fn)
    use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(12, 3.7))
    rows = []
    for g in GRAPHS:
        r = res[("A", g, T_MAIN, K_MAIN)]
        D = r["epoch"]["D"][0]
        Favg, _ = farness(g)
        for k in PROTO:
            e = excess(r, k)
            rows.append(["A", g, f"{D:.0f}", f"{Favg:.0f}", f"{T_MAIN:,}", K_MAIN, LABEL[k], fmt(r[k]["R"]),
                         fmt(e), f"{e.mean() / (N * D * K_MAIN):.2f}", f"{e.mean() / (K_MAIN * Favg):.2f}",
                         f"{r[k]['comm'].mean():,.0f}"])
    for k in PROTO:
        xs = [farness(g)[0] for g in GRAPHS]
        ys = [mci(excess(res[("A", g, T_MAIN, K_MAIN)], k)) for g in GRAPHS]
        a.errorbar(xs, [y[0] for y in ys], [y[1] for y in ys], marker="o", capsize=2, color=COLOR[k],
                   label=LABEL[k])
    a.set(xlabel="average farness F = Σ_k dist(i, k)", ylabel="extra regret over the server",
          title=f"Across graphs (T = {T_MAIN:,}, K = {K_MAIN})")
    Favg_ring = farness("ring")[0]
    Dring = res[("B", "ring", TS[0], K_MAIN)]["epoch"]["D"][0]
    for k in ("flood", "pub", "pub_small", "epoch"):
        ys = [mci(excess(res[("B", "ring", T, K_MAIN)], k)) for T in TS]
        b.errorbar([N * T for T in TS], [y[0] for y in ys], [y[1] for y in ys], marker="o", capsize=2,
                   color=COLOR[k], label=LABEL[k])
        ys = [mci(excess(res[("C", "ring", T_MAIN, K)], k)) for K in KS]
        c.errorbar(KS, [y[0] for y in ys], [y[1] for y in ys], marker="o", capsize=2, color=COLOR[k],
                   label=LABEL[k])
        for T in TS:
            r = res[("B", "ring", T, K_MAIN)]
            e = excess(r, k)
            rows.append(["B", "ring", f"{Dring:.0f}", f"{Favg_ring:.0f}", f"{T:,}", K_MAIN, LABEL[k],
                         fmt(r[k]["R"]), fmt(e), f"{e.mean() / (N * Dring * K_MAIN):.2f}",
                         f"{e.mean() / (K_MAIN * Favg_ring):.2f}", f"{r[k]['comm'].mean():,.0f}"])
        for K in KS:
            r = res[("C", "ring", T_MAIN, K)]
            e = excess(r, k)
            rows.append(["C", "ring", f"{Dring:.0f}", f"{Favg_ring:.0f}", f"{T_MAIN:,}", K, LABEL[k],
                         fmt(r[k]["R"]), fmt(e), f"{e.mean() / (N * Dring * K):.2f}",
                         f"{e.mean() / (K * Favg_ring):.2f}", f"{r[k]['comm'].mean():,.0f}"])
    b.set(xscale="log", xlabel="N·T", ylabel="extra regret over the server",
          title="Horizon (ring): flat is predicted")
    c.set(xlabel="arms per round K", ylabel="extra regret over the server",
          title="Number of arms (ring)")
    for ax in (b, c):
        ax.axhline(0, color="#8a8984", lw=0.8)
    fig.legend(*a.get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig36_delay_shape")
    intro = (f"N = {N}, {LINK} link, d = {DIM}, σ = {SIGMA}, {NTR} paired trials, mean ± 95% CI. Pooled Phase-1 "
             f"size {N0}·(T/10⁴)^(2/3); Δ = (NT)^(-1/3). 'excess' is regret minus the server's (same seeds). "
             "'÷ NDK' and '÷ KF' divide the mean excess by N·D·K (the predicted shape for synchronised "
             "epochs) and by K·F with F the average farness (the predicted shape for the relays). A "
             "constant column means the prediction has the right shape.")
    md_table(f"{OUT}/claims_e36.md", "E36: the shape of the delay term", intro,
             ["part", "graph", "D", "F", "T", "K", "protocol", "regret", "excess", "÷ NDK", "÷ KF",
              "scalars"], rows)


if __name__ == "__main__":
    main()
