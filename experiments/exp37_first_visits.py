"""E37 -- coordinated first visits: does a bin owner cut the relay's gap to the server?

The published-only relay at γ = 0.5 (Theorem 27, src/dec/phase2/flood.py, own=False) pays an
extra K·F' over the server: far-apart agents do not yet see each other's pulls, so several of them
explore the same fresh bin.  A 1-scalar "I'm exploring bin j" claim cannot help here: with γ < 1 a
pull into a bin seen as empty is published in the same step, and a claim would travel no faster.
What can help is coordination that needs no message:

  owner A   each bin has an owner fixed by a shared hash.  A bin an agent sees as empty is left
            to its owner until the agent has had it available A times (A = patience); if every
            available bin is held, the agent explores as usual.

'blind pulls' counts Phase-2 pulls into a bin the puller sees as empty -- the quantity the owner
rule targets.  The rule may also help with a server (fewer blind pulls in general), so the server
with the same rule is a second reference: 'excess' is against the plain server, 'vs server+owner'
against the server with the same patience.  Graphs as in E36 Part A (N = 16, T = 10 000, K = 20).

Writes results/fig37_first_visits.{png,pdf}, results/claims_e37.md.
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
T = pick(10_000, 2500)
K = 20
NTR = trials(10, 2)
PATIENCE = [1, 3, 10]

PROTO = {"pub": ("flood", {"gamma": GAMMA, "own": False})}
PROTO.update({f"owner{a}": ("flood", {"gamma": GAMMA, "own": False, "owner": a}) for a in PATIENCE})
SERVER = {"server": {"gamma": GAMMA}}
SERVER.update({f"server_owner{a}": {"gamma": GAMMA, "owner": a} for a in PATIENCE})
LABEL = {"pub": "published-only relay, γ = 0.5", "server": "server, γ = 0.5"}
LABEL.update({f"owner{a}": f"... + bin owner, patience {a}" for a in PATIENCE})
LABEL.update({f"server_owner{a}": f"server + bin owner, patience {a}" for a in PATIENCE})
COLOR = {"pub": "#1baf7a", "owner1": "#2a78d6", "owner3": "#4a3aa7", "owner10": "#eb6834"}


def farness(graph):
    return distances(Graph(graph, N).A0).sum(axis=1).mean()


def cell_fn(cell, names=None):
    (graph,) = cell
    t0 = max(1, int(np.ceil(N0 * (T / 10_000) ** (2 / 3) / N)))
    c = {k: dec_config(graph, "tree", {}, p, kw, T0=t0, bin_width="network") for k, (p, kw) in PROTO.items()}
    for k, kw in SERVER.items():
        c[k] = dec_config("complete", "server", {}, "server_event", kw, T0=t0, bin_width="network")
    c = {k: v for k, v in c.items() if names is None or k in names}
    out, _ = run_fed_sweep(c, NTR, N, DIM, K, T, LINK, sigma=SIGMA, record_every=T, progress=False)
    return summarize(out, extra=dict(blind=lambda x: x["blind_pulls"]))


def main():
    res = run_cells("e37", [(g,) for g in GRAPHS], cell_fn)
    use_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8))
    xs = [farness(g) for g in GRAPHS]
    rows = []
    for g, F in zip(GRAPHS, xs):
        r = res[(g,)]
        for k in [*SERVER, *PROTO]:
            e = r[k]["R"] - r["server"]["R"]
            ref = "server_" + k if k.startswith("owner") else None
            vs = fmt(r[k]["R"] - r[ref]["R"]) if ref else "--"
            rows.append([g, f"{F:.0f}", LABEL[k], fmt(r[k]["R"]), fmt(e), f"{e.mean() / (K * F):.2f}", vs,
                         fmt(r[k]["blind"]), f"{r[k]['comm'].mean():,.0f}"])
    for k in PROTO:
        ys = [mci(res[(g,)][k]["R"] - res[(g,)]["server"]["R"]) for g in GRAPHS]
        a.errorbar(xs, [y[0] for y in ys], [y[1] for y in ys], marker="o", capsize=2, color=COLOR[k],
                   label=LABEL[k])
        ys = [mci(res[(g,)][k]["blind"] - res[(g,)]["server"]["blind"]) for g in GRAPHS]
        b.errorbar(xs, [y[0] for y in ys], [y[1] for y in ys], marker="o", capsize=2, color=COLOR[k],
                   label=LABEL[k])
    for k in (f"server_owner{PATIENCE[-1]}",):
        m = np.mean([(res[(g,)][k]["R"] - res[(g,)]["server"]["R"]).mean() for g in GRAPHS])
        a.axhline(m, color=COLOR[f"owner{PATIENCE[-1]}"], lw=1.2, ls="--", label=LABEL[k])
        a.set_ylim(m - 60, None)
    a.set(xlabel="average farness F = Σ_k dist(i, k)", ylabel="extra regret over the server",
          title=f"Regret (N = {N}, T = {T:,}, K = {K})")
    b.set(xlabel="average farness F = Σ_k dist(i, k)", ylabel="extra blind pulls over the server",
          title="Pulls into a bin seen as empty")
    for ax in (a, b):
        ax.axhline(0, color="#8a8984", lw=0.8)
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "fig37_first_visits")
    intro = (f"N = {N}, {LINK} link, d = {DIM}, σ = {SIGMA}, T = {T:,}, K = {K}, {NTR} paired trials, mean ± 95% "
             f"CI. Pooled Phase-1 size {N0}; Δ = (NT)^(-1/3). 'excess' is regret minus the server's (same "
             "seeds); '÷ KF' divides it by K·F with F the average farness. 'blind' counts Phase-2 pulls into a "
             "bin the puller sees as empty.")
    md_table(f"{OUT}/claims_e37.md", "E37: coordinated first visits (bin owners)", intro,
             ["graph", "F", "protocol", "regret", "excess", "÷ KF", "vs server+owner", "blind pulls", "scalars"],
             rows)


if __name__ == "__main__":
    main()
