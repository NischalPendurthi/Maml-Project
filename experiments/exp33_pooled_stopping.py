"""E33 -- stopping Phase 1 without a server, with agreement (Proposition 'prop:stop').

E28b showed that letting each agent run the drift rule on its own estimate fails: "any"
stops at the earliest agent, with different directions; "all" assumes the network can
detect for free that everyone is ready.  The pooled rule floods the local Stein sums at
each checkpoint and, Λ = D rounds later, applies the SERVER's drift rule to the same pooled
sums, so every agent stops at the server's checkpoint and freezes the same direction.

Checked here, with paired seeds:
  1. pooled stops exactly D rounds after the server's adaptive rule, with zero disagreement;
  2. its regret tracks the server's adaptive rule (it inherits that rule's quality);
  3. how the drift tolerance changes whether adaptive stopping beats a fixed T0
     (0.15 = our default, which E28b found stops too early; 0.05 = DBG's choice).

Writes results/fig33_pooled_stopping.{png,pdf}, results/claims_e33.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, np, pick, plt, run_cells, save, summarize,
                           sweep, trials, use_style)
from configs.decentralized import dec_config

N = 16
T = pick(10_000, 2500)
GAMMA = 0.5
GRAPHS = pick(["torus", "ring", "path"], ["ring"])
TOLS = [0.15, 0.05]
LINK = "quadratic"
NTR = trials(20, 3)
P2 = ("flood", {"gamma": GAMMA})
T0_FIXED = 60                                  # the best fixed length in E28 (pooled 960)
COLOR = {"fixed": "#8a8984", "any": "#eb6834", "all": "#eda100", "pooled": "#2a78d6",
         "server": "#1a1a1a"}


def configs(graph):
    c = {"fixed": dec_config(graph, "tree", {}, *P2, T0=T0_FIXED, bin_width="network"),
         "any": dec_config(graph, "flood", {}, *P2, freeze="adaptive", stop_rule="any",
                           bin_width="network"),
         "all": dec_config(graph, "flood", {}, *P2, freeze="adaptive", stop_rule="all",
                           bin_width="network")}
    for tol in TOLS:
        c[f"pooled@{tol}"] = dec_config(graph, "local", {}, *P2, freeze="adaptive",
                                        stop_rule="pooled", stop_tol=tol, bin_width="network")
        c[f"server@{tol}"] = dict(engine="fed", phase1="exact", phase2="event",
                                  phase2_kw=dict(gamma=GAMMA), stop_tol=tol, bin_width="network")
    return c


def cell_fn(cell, names=None):
    graph = cell[0]
    c = {k: v for k, v in configs(graph).items() if names is None or k in names}
    out, _ = sweep(c, NTR, N, T, LINK)
    return summarize(out, extra=dict(D=lambda x: x.get("diameter", 0) or 0))


def main():
    res = run_cells("e33", [(g,) for g in GRAPHS], cell_fn)
    use_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8))
    rows = []
    keys = ["fixed", "any", "all"] + [f"{p}@{t}" for t in TOLS for p in ("server", "pooled")]
    x = np.arange(len(keys))
    for gi, g in enumerate(GRAPHS):
        r = res[(g,)]
        D = r["fixed"]["D"][0]
        for k in keys:
            v = r[k]
            lag = (v["T0"] - r[f"server@{k.split('@')[1]}"]["T0"]) if k.startswith("pooled") else None
            rows.append([g, f"{D:.0f}", k, f"{np.nanmean(v['T0']):.0f}",
                         "–" if lag is None else f"{np.nanmean(lag):.1f} (min {np.nanmin(lag):.0f}, max {np.nanmax(lag):.0f})",
                         f"{v['disagree'].mean():.3f}", fmt(v["R"]),
                         f"{v['R'].mean() / r['fixed']['R'].mean():.3f}", f"{v['comm1'].mean():,.0f}"])
        means = [r[k]["R"].mean() / r["fixed"]["R"].mean() for k in keys]
        a.plot(x + 0.08 * gi, means, "o", label=f"{g} (D = {D:.0f})")
        b.plot(x + 0.08 * gi, [np.nanmean(r[k]["T0"]) for k in keys], "o", label=g)
    for ax in (a, b):
        ax.set_xticks(x, keys, rotation=35, ha="right", fontsize=7)
    a.axhline(1, color=COLOR["fixed"], lw=1)
    a.set(ylabel="regret ÷ fixed T0 = 60", title="Stopping rules on graphs (N = 16)")
    b.set(ylabel="round at which Phase 2 starts", title="When each rule stops")
    a.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig33_pooled_stopping")
    intro = (f"N = {N}, T = {T:,}, {LINK} link, γ = {GAMMA}, {NTR} paired trials, mean ± 95% CI. "
             "'fixed' freezes at T0 = 60 with exact tree pooling. 'any' / 'all' run the drift rule on each "
             "agent's own flooded estimate ('all' assumes free detection). 'server@tol' is the server's "
             "adaptive rule; 'pooled@tol' is the serverless rule of the proposition with the same tolerance. "
             "'lag' is pooled's stopping round minus the server's, per paired trial: the proposition says "
             "it equals D. 'disagree' is the mean l1 distance of the frozen directions from their mean.")
    md_table(f"{OUT}/claims_e33.md", "E33: stopping Phase 1 without a server", intro,
             ["graph", "D", "rule", "T0 used", "lag vs server", "disagree", "regret", "÷ fixed",
              "Phase-1 scalars"], rows)


if __name__ == "__main__":
    main()
