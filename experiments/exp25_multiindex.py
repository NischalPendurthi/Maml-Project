"""E25 -- multi-index bandits (y = g(Bᵀx) + noise): does Phase 1 stop being negligible?

Claim 2.2 of docs/claims-evidence.md.  The extension Dey, Bhore & Ghosh list as open:
Phase 1 estimates span(B) by second-order Stein (a d×d matrix, not a d-vector),
Phase 2 is sleeping UCB on m-dimensional cubes of side Δ = c·(NT)^{-1/(m+2)}
(c = 4, calibrated once; src/multiindex/).

Part A  estimator: subspace error of second-order Stein against n (expect n^{-1/2}).
Part B  collaboration: network regret vs N for m = 1, 2; against Phase-1-only
        sharing and against single-index Fed-ZoomSIB used on the multi-index problem.
Part C  Phase-1 strategies (N = 8, m = 2): exact matrix pooling (d(d+1)/2 per agent),
        one-shot projection averaging (d·m), federated power iteration (d·m per round).
Part D  the key question: Phase-1 share of all communication as d grows.

Writes results/fig25_multiindex.{png,pdf}, results/claims_e25.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save,
                           summarize, sweep, trials, use_style)
from src.multiindex import MIBEnv
from src.multiindex.stein2 import local_sum, subspace_error, top_m

T = pick(10_000, 2500)
GAMMA = 0.5
DSCALE = 4.0
LINKS = pick(["bowl", "mixed"], ["bowl"])
NS = pick([1, 2, 4, 8], [1, 8])
DS_SHARE = pick([10, 20, 50, 100], [10, 50])
NS_EST = [250, 500, 1000, 2000, 4000, 8000, 16000, 32000]
NTR = trials(20, 3)
NTR_SHARE = trials(5, 2)
P1_METHODS = {"exact": ("exact", 10), "projavg": ("projavg", 10), "power2": ("power", 2),
              "power5": ("power", 5), "power10": ("power", 10)}


def n0_for(d, N):
    """Pooled Phase-1 size: 160·d, at most 30% of the pooled horizon."""
    return int(min(160 * d, 0.3 * N * T))


def mib(m, d, N, mi="exact", rounds=10, phase2="event"):
    kw = dict(gamma=GAMMA) if phase2 == "event" else {}
    return dict(engine="mib", m=m, mi_phase1=mi, power_rounds=rounds, phase2=phase2,
                phase2_kw=kw, freeze="fixed", T0=max(1, n0_for(d, N) // N),
                bin_width="network", delta_scale=DSCALE)


def sib(d, N):
    return dict(engine="fed", phase1="exact", phase2="event", phase2_kw=dict(gamma=GAMMA),
                freeze="fixed", T0=max(1, n0_for(d, N) // N), bin_width="network")


def with_error(out, link, m, d, res):
    """Attach the subspace error (trial k ↔ instance seed 1000 + k)."""
    for name, v in out.items():
        if "B_hat" not in v["diag"][0]:          # single-index baselines have no subspace
            continue
        errs = []
        for k, dg in enumerate(v["diag"]):
            B = MIBEnv(d, 2, m=m, link=link, seed=1000 + k).B
            errs.append(subspace_error(dg["B_hat"], B))
        res[name]["err"] = np.array(errs)
    return res


def cell_fn(cell, names=None):
    part = cell[0]
    if part == "est":
        _, link, d = cell
        rows = {}
        for n in NS_EST:
            e = []
            for rep in range(trials(40, 5)):
                env = MIBEnv(d, 1, m=2, link=link, seed=7000 + rep, run_seed=[8000, rep])
                X = np.vstack([env.draw_arms() for _ in range(n)])
                y = env.mean_rewards(X) + env.sigma * env.rng.standard_normal(n)
                M = local_sum(env.score(X), y, env.ctx_std ** 2) / n
                e.append(subspace_error(top_m(M, 2), env.B))
            rows[n] = np.array(e)
        return {"err": rows}
    if part == "scale":
        _, link, m, N = cell
        d = 10
        cfgs = {"mib_fed": mib(m, d, N), "mib_p1only": mib(m, d, N, phase2="none"),
                "sib_on_mib": sib(d, N)}
        out, _ = sweep(cfgs, NTR, N, T, f"mib:{link}:{m}", d=d)
        return with_error(out, link, m, d, summarize(out))
    if part == "p1":
        _, link, d = cell
        N = 8
        cfgs = {k: mib(2, d, N, mi, r) for k, (mi, r) in P1_METHODS.items()}
        out, _ = sweep(cfgs, NTR, N, T, f"mib:{link}:2", d=d)
        return with_error(out, link, 2, d, summarize(out))
    _, link, d = cell                           # part == "share"
    N = 8
    cfgs = {"mib_exact": mib(2, d, N), "mib_projavg": mib(2, d, N, "projavg")}
    out, _ = sweep(cfgs, NTR_SHARE, N, T, f"mib:{link}:2", d=d)
    res = with_error(out, link, 2, d, summarize(out))
    out2, _ = sweep({"sib": sib(d, N)}, NTR_SHARE, N, T, "quadratic", d=d)
    res.update(summarize(out2))
    return res


def simulate():
    cells = [("est", link, 10) for link in LINKS]
    cells += [("scale", link, m, N) for link in LINKS for m in (1, 2) for N in NS]
    cells += [("p1", link, d) for link in LINKS for d in pick([10, 50], [10])]
    cells += [("share", LINKS[0], d) for d in DS_SHARE]
    return run_cells("e25", cells, cell_fn)


def share(r):
    return r["comm1"] / r["comm"]


def plot(res):
    use_style()
    fig, axes = plt.subplots(1, 4, figsize=(18, 3.9))
    a, b, c, dax = axes
    col = {"bowl": "#2a78d6", "mixed": "#eb6834"}
    rows_est = []
    for link in LINKS:
        e = res[("est", link, 10)]["err"]
        ns = np.array(NS_EST)
        m = np.array([e[n].mean() for n in NS_EST])
        sl = float(np.polyfit(np.log(ns[m < 0.9]), np.log(m[m < 0.9]), 1)[0])
        a.plot(ns, m, marker="o", color=col[link], label=f"{link}: slope {sl:.2f}")
        rows_est.append([link, f"{sl:.2f}"] + [f"{x:.3f}" for x in m])
    a.plot(ns, 0.9 * (ns / ns[0]) ** -0.5 * m[0] / 0.9, ":", color="#8a8984", label="n^{-1/2}")
    a.set(xscale="log", yscale="log", xlabel="samples n (d = 10, m = 2)",
          ylabel="subspace error ‖P̂ − P‖₂", title="Second-order Stein recovers span(B)")
    a.legend(fontsize=7)

    rows_scale = []
    for link in LINKS:
        for m, ls in ((1, ":"), (2, "-")):
            for key, cc in (("mib_fed", "#2a78d6"), ("mib_p1only", "#1baf7a"),
                            ("sib_on_mib", "#eb6834")):
                ys = np.array([res[("scale", link, m, N)][key]["R"].mean() for N in NS])
                if link == LINKS[0]:
                    b.plot(NS, ys, ls=ls, marker="o", ms=3, color=cc,
                           label=f"m={m}: " + {"mib_fed": "Fed-ZoomMIB (exact + event)",
                                               "mib_p1only": "Phase-1 sharing only",
                                               "sib_on_mib": "single-index Fed-ZoomSIB"}[key])
                sl = float(np.polyfit(np.log(NS), np.log(ys), 1)[0]) if len(NS) > 1 else np.nan
                for N in NS:
                    r = res[("scale", link, m, N)][key]
                    rows_scale.append([link, m, N, key, fmt(r["R"]),
                                       f"{r['err'].mean():.3f}" if "err" in r else "–",
                                       f"{sl:.2f}"])
    b.set(xscale="log", yscale="log", xlabel="N (agents)", ylabel="network regret",
          title=f"Collaboration in multi-index ({LINKS[0]})")
    b.set_xticks(NS, [str(n) for n in NS])
    b.legend(fontsize=6)

    rows_p1 = []
    for link in LINKS:
        for d in pick([10, 50], [10]):
            cell = res[("p1", link, d)]
            for k in P1_METHODS:
                r = cell[k]
                if link == LINKS[0]:
                    c.scatter(r["comm1"].mean(), r["err"].mean(), s=30,
                              marker="o" if d == 10 else "s",
                              color={"exact": "#1a1a1a", "projavg": "#eb6834"}.get(k, "#2a78d6"))
                    c.annotate(f"{k} (d={d})", (r["comm1"].mean(), r["err"].mean()), fontsize=6,
                               xytext=(3, 2), textcoords="offset points")
                rows_p1.append([link, d, k, f"{r['comm1'].mean():,.0f}", f"{r['err'].mean():.3f}",
                                fmt(r["R"]), f"{100 * share(r).mean():.2f}%"])
    c.set(xscale="log", xlabel="Phase-1 scalars (N = 8)", ylabel="subspace error",
          title="Phase-1 strategies: talk vs accuracy")

    rows_sh = []
    for key, cc, lab in (("mib_exact", "#1a1a1a", "multi-index, exact matrix"),
                         ("mib_projavg", "#eb6834", "multi-index, projection avg"),
                         ("sib", "#2a78d6", "single-index (vector)")):
        ys = [100 * share(res[("share", LINKS[0], d)][key]).mean() for d in DS_SHARE]
        dax.plot(DS_SHARE, ys, marker="o", color=cc, label=lab)
        for d, y in zip(DS_SHARE, ys):
            r = res[("share", LINKS[0], d)][key]
            rows_sh.append([lab, d, f"{r['comm1'].mean():,.0f}",
                            f"{(r['comm'] - r['comm1']).mean():,.0f}", f"{y:.2f}%",
                            fmt(r["R"])])
    dax.set(xscale="log", yscale="log", xlabel="context dimension d (N = 8, m = 2)",
            ylabel="Phase-1 share of scalars (%)", title="Is Phase 1 still negligible?")
    dax.set_xticks(DS_SHARE, [str(x) for x in DS_SHARE])
    dax.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig25_multiindex")

    path = f"{OUT}/claims_e25.md"
    md_table(path, "E25: multi-index bandits",
             f"T = {T:,} rounds per agent, Δ = {DSCALE}·(NT)^(-1/(m+2)), pooled Phase-1 size "
             f"160·d (fixed), event-triggered Phase 2 (γ = {GAMMA}), {NTR} paired trials "
             f"({NTR_SHARE} for the share sweep), mean ± 95% CI.",
             ["link", "m", "N", "config", "network regret", "subspace error", "slope in N"],
             rows_scale)
    with open(path, "a") as fh:
        def tab(title, head, rows):
            fh.write(f"\n## {title}\n\n| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n")
            fh.write("\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows) + "\n")
        tab("Second-order Stein: subspace error vs n (d = 10, m = 2)",
            ["link", "slope"] + [f"n={n}" for n in NS_EST], rows_est)
        tab("Phase-1 strategies (N = 8, m = 2)",
            ["link", "d", "strategy", "Phase-1 scalars", "subspace error", "network regret",
             "Phase-1 share"], rows_p1)
        tab(f"Phase-1 share vs d (N = 8, m = 2, {LINKS[0]}; single-index on the quadratic link)",
            ["model", "d", "Phase-1 scalars", "Phase-2 scalars", "Phase-1 share",
             "network regret"], rows_sh)


def main():
    plot(simulate())


if __name__ == "__main__":
    main()
