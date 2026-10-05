"""E28 -- without a server, how long to explore and how much to talk are one problem.

Claim 4 of docs/claims-evidence.md.  N = 16 agents on graphs of growing diameter.
Phase 2 is fixed (event-triggered flooding, gamma = 0.5) so only Phase 1 varies.

Part A  T0 sweep.  For each Phase-1 method and graph, sweep the per-agent Phase-1
        length T0 and find T0*, the regret-minimising length.  Methods:
            tree         exact spanning-tree pooling at the freeze (2·depth rounds)
            flood        every agent relays every record; exact up to a D-round lag
            cons1/cons5  running consensus, 1 or 5 gossip steps per round; agents
                         freeze DIFFERENT estimates theta_i (agree="none")
            cons1_agree  cons1, then one flooding pass so all agents agree (costs D rounds)
        plus the server (exact pooling) as reference.
Part B  Phase-1 communication vs regret at each method's own T0*, and the
        agents' disagreement at the freeze against the regret it costs.
Part C  Adaptive stopping on graphs: the drift rule with stop_rule "any" / "all"
        (flag spread hop by hop) against the best fixed T0 from Part A.

Writes results/fig28_dec_coupling.{png,pdf}, fig28b_stop_rules.{png,pdf},
results/claims_e28.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from configs.decentralized import dec_config

N = 16
T = pick(10_000, 2500)
GAMMA = 0.5
GRAPHS = pick(["complete", "hypercube", "torus", "ring", "path"], ["complete", "ring"])
STOP_GRAPHS = pick(["torus", "ring", "path"], ["ring"])
T0S = pick([15, 30, 60, 120, 240], [15, 60, 240])
LINK = "quadratic"
NTR = trials(10, 3)                # 20 would take ~8 h; 10 keeps CIs readable
P2 = ("flood", {"gamma": GAMMA})
METHODS = {
    "tree": ("tree", {}, {}, "tree (exact)"),
    "flood": ("flood", {}, {}, "flooding (exact, D-lag)"),
    "cons1": ("consensus", {"steps": 1}, {}, "consensus, 1 step/round"),
    "cons5": ("consensus", {"steps": 5}, {}, "consensus, 5 steps/round"),
    "cons1_agree": ("consensus", {"steps": 1}, {"agree": "exact"}, "consensus 1 + agree"),
}
COLOR = {"server": "#1a1a1a", "tree": "#2a78d6", "flood": "#1baf7a", "cons1": "#eb6834",
         "cons5": "#eda100", "cons1_agree": "#4a3aa7"}
GCOLOR = {"complete": "#2a78d6", "hypercube": "#1baf7a", "torus": "#4a3aa7",
          "ring": "#eb6834", "path": "#e87ba4"}


def sweep_cfgs(graph):
    c = {}
    for key, (p1, k1, extra, _) in METHODS.items():
        for t0 in T0S:
            c[f"{key}@{t0}"] = dec_config(graph, p1, k1, *P2, T0=t0, bin_width="network", **extra)
    if graph == "complete":
        for t0 in T0S:
            c[f"server@{t0}"] = dec_config("complete", "server", {}, "server_event",
                                           {"gamma": GAMMA}, T0=t0, bin_width="network")
    return c


def stop_cfgs(graph):
    c = {}
    for key in ("flood", "cons1"):
        p1, k1, _, _ = METHODS[key]
        for rule in ("any", "all"):
            c[f"{key}_{rule}"] = dec_config(graph, p1, k1, *P2, freeze="adaptive", stop_rule=rule,
                                            bin_width="network")
    c["server_adaptive"] = dict(engine="fed", phase1="exact", phase2="event",
                                phase2_kw=dict(gamma=GAMMA), bin_width="network")
    return c


def cell_fn(cell, names=None):
    part, graph = cell
    cfgs = sweep_cfgs(graph) if part == "sweep" else stop_cfgs(graph)
    cfgs = {k: v for k, v in cfgs.items() if names is None or k in names}
    out, _ = sweep(cfgs, NTR, N, T, LINK)
    return summarize(out, extra=dict(D=lambda x: x.get("diameter", 1),
                                     flag=lambda x: x.get("flag_rounds", 0)))


def best(cell, key):
    """(T0*, summary at T0*) for a method in a sweep cell."""
    t0 = min(T0S, key=lambda t: cell[f"{key}@{t}"]["R"].mean())
    return t0, cell[f"{key}@{t0}"]


def plot(res):
    use_style()
    server = res[("sweep", "complete")]
    s_t0, s_best = best(server, "server")
    fig, axes = plt.subplots(1, 4, figsize=(18, 3.9))
    a, b, c, d = axes
    show = [g for g in ("ring", "path") if g in GRAPHS] or GRAPHS[-1:]
    for g, ls in zip(show, ("-", "--")):
        cell = res[("sweep", g)]
        for key in METHODS:
            ys = [cell[f"{key}@{t}"]["R"].mean() for t in T0S]
            a.plot(T0S, ys, ls=ls, marker="o", ms=3, color=COLOR[key],
                   label=f"{METHODS[key][3]}" if g == show[0] else None)
    a.plot(T0S, [server[f"server@{t}"]["R"].mean() for t in T0S], color=COLOR["server"],
           lw=2, label="server")
    a.set(xscale="log", yscale="log", xlabel="Phase-1 rounds per agent T0",
          ylabel="network regret",
          title=" / ".join(f"{g} ({'solid' if i == 0 else 'dashed'})" for i, g in enumerate(show)))
    a.set_xticks(T0S, [str(t) for t in T0S])
    a.legend(fontsize=6.5)

    rows, frontier = [], []
    Ds = []
    for g in GRAPHS:
        cell = res[("sweep", g)]
        D = cell[f"tree@{T0S[0]}"]["D"][0]
        Ds.append(D)
        for key in METHODS:
            t0, r = best(cell, key)
            frontier.append((g, key, D, t0, r))
            rows.append([g, f"{D:.0f}", METHODS[key][3], t0, fmt(r["R"]),
                         f"{r['R'].mean() / s_best['R'].mean():.3f}", f"{r['comm1'].mean():,.0f}",
                         f"{r['disagree'].mean():.4f}"])
    rows.append(["(server)", "–", "server", s_t0, fmt(s_best["R"]), "1.000",
                 f"{s_best['comm1'].mean():,.0f}", "0"])
    for key in METHODS:
        pts = [(D, t0) for g, k, D, t0, _ in frontier if k == key]
        b.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", color=COLOR[key],
               label=METHODS[key][3])
    b.axhline(s_t0, color=COLOR["server"], lw=2, label=f"server T0* = {s_t0}")
    b.set(yscale="log", xlabel="graph diameter D", ylabel="best Phase-1 length T0*",
          title="Best Phase-1 length vs diameter")
    b.set_yticks(T0S, [str(t) for t in T0S])
    b.legend(fontsize=6.5)

    for g, key, D, t0, r in frontier:
        c.scatter(r["comm1"].mean(), r["R"].mean() / s_best["R"].mean(), color=COLOR[key],
                  marker="o", s=18 + 4 * D, alpha=0.85)
    for key in METHODS:
        c.scatter([], [], color=COLOR[key], label=METHODS[key][3])
    c.axhline(1, color=COLOR["server"], lw=1)
    c.set(xscale="log", xlabel="Phase-1 scalars (at each method's T0*)",
          ylabel="regret ÷ best server", title="Phase-1 talk vs regret (marker size ∝ D)")
    c.legend(fontsize=6.5)

    for g in GRAPHS:
        cell = res[("sweep", g)]
        for key in ("cons1", "cons5"):
            for t in T0S:
                r = cell[f"{key}@{t}"]
                ref = cell[f"tree@{t}"]["R"].mean()     # same T0, exact agreement
                # complete graph: disagreement ~1e-16 (exact); clip so the axis stays readable
                d.scatter(max(r["disagree"].mean(), 1e-4), r["R"].mean() / ref, color=GCOLOR[g], s=14)
    for g in GRAPHS:
        d.scatter([], [], color=GCOLOR[g], label=g)
    d.axhline(1, color="#8a8984", lw=0.8)
    d.set(xscale="log", xlabel="disagreement of frozen θ̂_i (mean ℓ1 to the mean; floor 1e-4)",
          ylabel="regret ÷ tree at the same T0", title="Cost of freezing different estimates")
    d.legend(fontsize=6.5)
    fig.tight_layout()
    save(fig, "fig28_dec_coupling")

    # Part C
    fig, ax = plt.subplots(figsize=(7, 3.8))
    rows_c = []
    xs = np.arange(len(STOP_GRAPHS))
    keys = ["flood_any", "flood_all", "cons1_any", "cons1_all", "best_fixed_flood",
            "best_fixed_cons1"]
    width = 0.13
    for j, key in enumerate(keys):
        ys, hs = [], []
        for g in STOP_GRAPHS:
            if key.startswith("best_fixed"):
                m = key.split("_")[-1]
                t0, r = best(res[("sweep", g)], m)
                lab = f"fixed T0* ({m})"
                t0u, flag = t0, 0
            else:
                r = res[("stop", g)][key]
                lab = key.replace("_", " · stop when ")
                t0u, flag = r["T0"].mean(), r["flag"].mean()
            y, h = mci(r["R"])
            ys.append(y)
            hs.append(h)
            rows_c.append([g, lab, f"{t0u:.0f}", f"{flag:.1f}", fmt(r["R"]),
                           f"{r['comm1'].mean():,.0f}"])
        ax.bar(xs + (j - 2.5) * width, ys, width, yerr=hs, capsize=2, label=lab,
               color=["#eb6834", "#2a78d6", "#eda100", "#1baf7a", "#4a3aa7", "#8a8984"][j])
    srv = res[("stop", STOP_GRAPHS[0])]["server_adaptive"]
    ax.axhline(srv["R"].mean(), color="#1a1a1a", lw=1, label="server, adaptive stop")
    rows_c.append(["(server)", "server, adaptive stop", f"{srv['T0'].mean():.0f}", "0",
                   fmt(srv["R"]), f"{srv['comm1'].mean():,.0f}"])
    ax.set_xticks(xs, STOP_GRAPHS)
    ax.set(ylabel="network regret", title="Adaptive stopping on graphs vs the best fixed T0")
    ax.legend(fontsize=6.5, ncol=2)
    fig.tight_layout()
    save(fig, "fig28b_stop_rules")

    intro = (f"N = {N}, T = {T:,}, Phase 2 = event-triggered flooding (γ = {GAMMA}) for every "
             f"decentralised config, {NTR} paired trials, mean ± 95% CI. T0* = the per-agent "
             "Phase-1 length with the lowest mean regret on the grid " + str(T0S) + ".")
    md_table(f"{OUT}/claims_e28.md", "E28: exploration length, agreement and communication on graphs",
             intro, ["graph", "D", "Phase-1 method", "T0*", "regret at T0*", "÷ best server",
                     "Phase-1 scalars", "disagreement"], rows)
    with open(f"{OUT}/claims_e28.md", "a") as fh:
        fh.write("\n## Adaptive stopping vs the best fixed length\n\n"
                 "| graph | rule | T0 used | flag rounds | regret | Phase-1 scalars |\n"
                 "|---|---|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows_c) + "\n")


def main():
    cells = [("sweep", g) for g in GRAPHS] + [("stop", g) for g in STOP_GRAPHS]
    plot(run_cells("e28", cells, cell_fn))


if __name__ == "__main__":
    main()
