"""E29 -- can heterogeneous agents identify θ* only together?  A go/no-go test.

Agent i's Stein estimate targets μ_i θ*, with μ_i = E_i[f'(index)] the average slope
of f over ITS OWN contexts.  On the quadratic link f(z) = −(z−1)² + 1 with index
~ N(c_i, 1), μ_i = 2(1 − c_i): positive left of the peak, 0 at it, negative right.

Part A  one agent swept across the peak (μ from +4 to −4): does first-order ZoomSIB
        fail near μ = 0, with what probability, and does second-order Stein rescue it?
Part B  networks of agents on both sides of the peak:
          imbalance   agents at 1 ± s, a fraction p on the falling side (p = ½ balanced)
          spread      agents evenly spread over [b, b + 2] around the peak
          noisy       N = 16, 60 Phase-1 samples per agent (noisy individual signs)
          rescue      2 agents AT the peak among 6 others: their own regret
        Methods: each agent alone (first-, second-order), pooled sums (current
        Fed-ZoomSIB), aligned (simple sign fix), outer (unbiased sign-invariant),
        pooled second-order, random play (normaliser).

Writes results/fig29a_single_agent, fig29b_network, fig29c_noisy_rescue (png+pdf),
results/claims_e29.md (with the verdict table).
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, mci, np, pick, plt, run_cells, save, sweep,
                           trials, use_style)
from src.envs import SIBEnv

LINK, D = "quadratic", 10
T = pick(10_000, 2500)
POOLED_T0 = 960
GAMMA = 0.5
NTR_A = trials(50, 6)
NTR_B = trials(20, 3)
CS = pick([-1, 0, 0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2, 3], [0, 0.9, 1.0, 1.5])
PS = [0, 1, 2, 3, 4]                       # agents (of 8) on the falling side
SS = pick([0.5, 1.0], [1.0])
BS = pick([-1.0, -0.5, -0.25, 0.0], [-1.0, 0.0])
SUCCESS = (0.3, 0.5)
# (agents on the falling side, N): Phase-1 samples per agent = 960 / N (60 or 30)
NOISY = pick([(8, 16), (6, 16), (16, 32)], [(8, 16)])

COLOR = dict(indep1="#8a8984", indep2="#b4b2ab", exact="#eb6834", aligned="#2a78d6",
             outer="#1baf7a", pooled2="#4a3aa7", first="#eb6834", first_adapt="#eda100",
             second="#4a3aa7")
LABEL = dict(indep1="each alone, 1st-order", indep2="each alone, 2nd-order",
             exact="pooled sums (current)", aligned="aligned (simple fix)",
             outer="outer (unbiased)", pooled2="pooled 2nd-order",
             first="1st-order ZoomSIB, fixed T0", first_adapt="1st-order ZoomSIB, adaptive stop",
             second="2nd-order Stein", random="random play")


def mu(c):
    return 2.0 * (1.0 - np.asarray(c, float))


def first(t0, **kw):
    cfg = dict(engine="fed", phase1="exact", phase2="event", phase2_kw=dict(gamma=GAMMA),
               freeze="fixed", T0=t0, bin_width="network")
    cfg.update(kw)
    return cfg


def second(t0, **kw):
    cfg = dict(engine="mib", m=1, mi_phase1="exact", phase2="event",
               phase2_kw=dict(gamma=GAMMA), freeze="fixed", T0=t0, bin_width="network",
               delta_scale=1.0)
    cfg.update(kw)
    return cfg


def network_configs(t0):
    return {"indep1": dict(engine="indep", inner=first(t0)),
            "indep2": dict(engine="indep", inner=second(t0)),
            "exact": first(t0), "aligned": first(t0, phase1="aligned"),
            "outer": first(t0, phase1="outer"), "pooled2": second(t0),
            "random": dict(engine="random")}


def sin_angle(a, b):
    a, b = np.ravel(a).astype(float), np.ravel(b).astype(float)
    c = abs(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.sqrt(max(0.0, 1.0 - c * c)))


def theta_star(trial):
    return SIBEnv(D, 2, link=LINK, seed=1000 + trial, index_scale=1.0).theta_star


def summarise(out):
    res = {}
    for name, v in out.items():
        err, t0 = [], []
        for k, dg in enumerate(v["diag"]):
            th = dg.get("theta_hat")
            err.append(sin_angle(th, theta_star(k)) if th is not None else np.nan)
            t0.append(dg.get("T0_used") or np.nan)
        res[name] = dict(R=v["net"][:, -1], per=v["per"][:, :, -1], err=np.array(err),
                         T0=np.array(t0, float),
                         comm1=np.array([dg.get("comm_phase1", 0) for dg in v["diag"]], float))
    return res


def positions(cell):
    kind = cell[0]
    if kind == "imb":
        _, s, k, n = cell
        return [1 - s] * (n - k) + [1 + s] * k
    if kind == "spread":
        return list(1 + cell[1] + np.linspace(-1, 1, 8))
    if kind == "noisy":
        _, s, k, n = cell
        return [1 - s] * (n - k) + [1 + s] * k
    if kind == "rescue":
        return [1.0, 1.0, 0.0, 0.0, 0.0, 0.5, 1.5, 2.0]
    raise ValueError(kind)


def cell_fn(cell, names=None):
    if cell[0] == "A":
        c = cell[1]
        cfgs = {"first": first(POOLED_T0), "second": second(POOLED_T0),
                "first_adapt": dict(engine="fed", phase1="exact", phase2="event",
                                    phase2_kw=dict(gamma=GAMMA), bin_width="network"),
                "random": dict(engine="random")}
        cfgs = {k: v for k, v in cfgs.items() if names is None or k in names}
        out, _ = sweep(cfgs, NTR_A, 1, T, LINK, d=D, scenario="covariate", strength=[c])
        return summarise(out)
    pos = positions(cell)
    t0 = max(1, POOLED_T0 // len(pos))
    cfgs = {k: v for k, v in network_configs(t0).items() if names is None or k in names}
    out, _ = sweep(cfgs, NTR_B, len(pos), T, LINK, d=D, scenario="covariate", strength=pos)
    return summarise(out)


def cells():
    out = [("A", c) for c in CS]
    out += [("imb", s, k, 8) for s in SS for k in PS]
    out += [("spread", b) for b in BS]
    out += [("noisy", 1.0, k, n) for k, n in NOISY]
    out += [("rescue",)]
    return out


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - half, mid + half


def gain(pos):
    m = mu(pos)
    mbar = m.mean()
    return np.inf if abs(mbar) < 1e-12 else float((m ** 2).mean() / mbar ** 2)


def ratio(cell, key):
    return cell[key]["R"].mean() / cell["random"]["R"].mean()


NETWORK = ["indep1", "indep2", "exact", "aligned", "outer", "pooled2"]


def plot(res):
    use_style()
    # ---------------- Part A
    mus = mu(CS)
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(15, 4))
    rows_a = []
    for key in ("first", "first_adapt", "second"):
        e = np.array([res[("A", x)][key]["err"].mean() for x in CS])
        a.plot(mus, e, marker="o", color=COLOR[key], label=LABEL[key])
        k = np.array([(res[("A", x)][key]["err"] < SUCCESS[0]).sum() for x in CS])
        n = len(res[("A", CS[0])][key]["err"])
        lo, hi = zip(*[wilson(kk, n) for kk in k])
        b.errorbar(mus, k / n, yerr=[np.clip(k / n - np.array(lo), 0, None), np.clip(np.array(hi) - k / n, 0, None)], marker="o",
                   capsize=2, color=COLOR[key], label=LABEL[key])
        r = np.array([ratio(res[("A", x)], key) for x in CS])
        c.plot(mus, r, marker="o", color=COLOR[key], label=LABEL[key])
        for x, m, ee, kk, rr in zip(CS, mus, e, k, r):
            k2 = int((res[("A", x)][key]["err"] < SUCCESS[1]).sum())
            rows_a.append([LABEL[key], f"{x:g}", f"{m:+.1f}", f"{ee:.3f}", f"{kk}/{n}",
                           f"{k2}/{n}", f"{rr:.2f}",
                           f"{np.nanmean(res[('A', x)][key]['T0']):.0f}"])
    # theory: noise / |mu|, fitted once at mu = 2 (c = 0), capped at a random direction's 0.97
    if 0 in CS:
        kappa = 2.0 * res[("A", 0)]["first"]["err"].mean()
        grid = np.linspace(mus.min(), mus.max(), 400)
        a.plot(grid, np.minimum(0.974, kappa / np.maximum(np.abs(grid), 1e-9)), ":",
               color="#1a1a1a", label="theory: ∝ 1/|μ| (fitted at μ=2)")
    a.axhline(0.974, color="#8a8984", lw=0.8, ls="--", label="random direction (median 0.97)")
    a.set(xlabel="μ = 2(1 − c)  (agent's average slope of f)", ylabel="sin-angle error of θ̂",
          title="Part A: direction error, one agent")
    a.legend(fontsize=7)
    b.axhline(8.5e-6, color="#8a8984", lw=0.8, ls="--", label="random direction: 8.5e-6")
    b.set(xlabel="μ", ylabel=f"P(sin-angle error < {SUCCESS[0]})",
          title="Part A: probability of learning θ*")
    b.legend(fontsize=7)
    c.axhline(1, color="#8a8984", lw=0.8, ls="--")
    c.set(xlabel="μ", ylabel="regret ÷ random play", title="Part A: regret, one agent")
    c.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig29a_single_agent")

    # ---------------- Part B
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(15, 4))
    rows_b = []
    for s, ls in zip(SS, ("-", "--")):
        ps = np.array(PS) / 8
        for key in NETWORK:
            y = [ratio(res[("imb", s, k, 8)], key) for k in PS]
            a.plot(ps, y, ls=ls, marker="o", ms=3, color=COLOR[key],
                   label=LABEL[key] if s == SS[-1] else None)
        for k in PS:
            cell = res[("imb", s, k, 8)]
            g = gain(positions(("imb", s, k, 8)))
            for key in NETWORK:
                rows_b.append([f"imbalance s={s:g}, {k}/8 falling", "∞" if np.isinf(g) else f"{g:.1f}",
                               LABEL[key], fmt(cell[key]["R"]), f"{ratio(cell, key):.2f}",
                               f"{np.nanmean(cell[key]['err']):.3f}", f"{cell[key]['comm1'].mean():,.0f}"])
    a.axhline(1, color="#8a8984", lw=0.8)
    a.set(xlabel="fraction of agents on the falling side (½ = balanced)",
          ylabel="network regret ÷ random play",
          title="Part B: imbalance sweep (solid s=1, dashed s=0.5)")
    a.legend(fontsize=7)

    for key in ("exact", "aligned", "outer"):
        gs, es = [], []
        for s in SS:
            for k in PS:
                g = gain(positions(("imb", s, k, 8)))
                gs.append(min(g, 1e3))
                es.append(np.nanmean(res[("imb", s, k, 8)][key]["err"]))
        o = np.argsort(gs)
        b.plot(np.array(gs)[o], np.array(es)[o], marker="o", color=COLOR[key], label=LABEL[key])
    b.set(xscale="log", xlabel="G = mean(μ_i²) / μ̄²   (1e3 = perfectly balanced)",
          ylabel="sin-angle error of pooled θ̂", title="Part B: pooled sums degrade with G")
    b.legend(fontsize=7)

    for key in NETWORK:
        y = [ratio(res[("spread", bb)], key) for bb in BS]
        c.plot(-2 * np.array(BS), y, marker="o", color=COLOR[key], label=LABEL[key])
    for bb in BS:
        cell = res[("spread", bb)]
        g = gain(positions(("spread", bb)))
        for key in NETWORK:
            rows_b.append([f"spread, μ̄ = {-2 * bb:+.1f}", "∞" if np.isinf(g) else f"{g:.1f}",
                           LABEL[key], fmt(cell[key]["R"]), f"{ratio(cell, key):.2f}",
                           f"{np.nanmean(cell[key]['err']):.3f}", f"{cell[key]['comm1'].mean():,.0f}"])
    c.axhline(1, color="#8a8984", lw=0.8)
    c.set(xlabel="network-average slope μ̄ (agents spread over both sides)",
          ylabel="network regret ÷ random play", title="Part B: realistic spread")
    c.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig29b_network")

    # ---------------- noisy regime + rescue
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.8))
    noisy = [("noisy", 1.0, k, n) for k, n in NOISY]
    x = np.arange(len(NETWORK))
    for j, cl in enumerate(noisy):
        cell = res[cl]
        w = 0.8 / len(noisy)
        a.bar(x + (j - 0.5 * (len(noisy) - 1)) * w, [ratio(cell, k) for k in NETWORK], w * 0.95,
              color=[COLOR[k] for k in NETWORK], alpha=[1.0, 0.6, 0.35][j % 3],
              label=f"N={cl[3]}, {cl[2]}/{cl[3]} falling, {POOLED_T0 // cl[3]} samples/agent")
        for key in NETWORK:
            g = gain(positions(cl))
            rows_b.append([f"noisy N={cl[3]}, {cl[2]}/{cl[3]} falling, {POOLED_T0 // cl[3]} samples/agent",
                           "∞" if np.isinf(g) else f"{g:.1f}", LABEL[key],
                           fmt(cell[key]["R"]), f"{ratio(cell, key):.2f}",
                           f"{np.nanmean(cell[key]['err']):.3f}", f"{cell[key]['comm1'].mean():,.0f}"])
    a.set_xticks(x, [LABEL[k] for k in NETWORK], rotation=30, ha="right", fontsize=7)
    a.axhline(1, color="#8a8984", lw=0.8)
    a.set(ylabel="network regret ÷ random play", title="Noisy individual signs (few samples per agent)")
    a.legend(fontsize=7)

    cell = res[("rescue",)]
    peak = [cell[k]["per"][:, :2].sum(axis=1).mean() / cell["random"]["per"][:, :2].sum(axis=1).mean()
            for k in NETWORK]
    rest = [cell[k]["per"][:, 2:].sum(axis=1).mean() / cell["random"]["per"][:, 2:].sum(axis=1).mean()
            for k in NETWORK]
    b.bar(x - 0.19, peak, 0.36, color=[COLOR[k] for k in NETWORK], label="2 agents AT the peak (μ=0)")
    b.bar(x + 0.19, rest, 0.36, color=[COLOR[k] for k in NETWORK], alpha=0.5, label="the other 6")
    b.set_xticks(x, [LABEL[k] for k in NETWORK], rotation=30, ha="right", fontsize=7)
    b.axhline(1, color="#8a8984", lw=0.8)
    b.set(ylabel="their regret ÷ random play", title="Rescue: agents at the peak, alone vs in a network")
    b.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig29c_noisy_rescue")
    rows_r = [[LABEL[k], f"{p:.2f}", f"{q:.2f}"] for k, p, q in zip(NETWORK, peak, rest)]

    # ---------------- verdicts
    net_cells = [("imb", s, k, 8) for s in SS for k in PS] + [("spread", bb) for bb in BS] + noisy
    moderate = [cl for cl in net_cells if 4 <= gain(positions(cl))]
    alive = [cl for cl in moderate
             if ratio(res[cl], "exact") > 1.1 * min(ratio(res[cl], "aligned"), ratio(res[cl], "outer"))
             and min(ratio(res[cl], "aligned"), ratio(res[cl], "outer"))
             < min(ratio(res[cl], "indep1"), ratio(res[cl], "indep2"))]
    simple = max(ratio(res[cl], "aligned") / ratio(res[cl], "outer") for cl in net_cells)
    best_net = {cl: min(ratio(res[cl], k) for k in ("exact", "aligned", "outer", "pooled2"))
                for cl in net_cells}
    sec = max(ratio(res[cl], "indep2") / best_net[cl] for cl in net_cells)
    verdict = [
        ["Idea alive: pooled sums degrade at moderate imbalance (G ≥ 4) and sign-invariant pooling "
         "beats every agent going alone", f"{len(alive)}/{len(moderate)} such cells",
         "YES" if moderate and len(alive) >= 0.75 * len(moderate) else "NO"],
        ["Simple fix suffices: aligned within 5% of outer in every cell",
         f"worst aligned ÷ outer = {simple:.3f}", "YES" if simple <= 1.05 else "NO"],
        ["Second-order alone suffices: each agent alone with 2nd-order within 10% of the best "
         "network method", f"worst indep 2nd-order ÷ best network = {sec:.2f}",
         "YES" if sec <= 1.10 else "NO"],
    ]
    path = f"{OUT}/claims_e29.md"
    md_table(path, "E29: can heterogeneous agents identify θ* only together?",
             f"Quadratic link, agent i's index ~ N(c_i, 1), so μ_i = 2(1 − c_i). d = {D}, K = 20, "
             f"T = {T:,}, pooled Phase-1 size {POOLED_T0} (fixed), event Phase 2 (γ = {GAMMA}). "
             "'÷ random' = regret divided by uniform random play on the same instances "
             "(1 = learned nothing).",
             ["question", "evidence", "verdict"], verdict)
    with open(path, "a") as fh:
        def tab(title, head, rows):
            fh.write(f"\n## {title}\n\n| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n")
            fh.write("\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows) + "\n")
        tab(f"Part A: one agent ({NTR_A} trials per point)",
            ["method", "c", "μ", "sin-angle error", f"P(err < {SUCCESS[0]})",
             f"P(err < {SUCCESS[1]})", "regret ÷ random", "T0 used"], rows_a)
        tab(f"Part B: networks ({NTR_B} paired trials per cell)",
            ["cell", "G = mean μ²/μ̄²", "method", "network regret", "÷ random",
             "sin-angle error", "Phase-1 scalars"], rows_b)
        tab("Rescue: 2 agents at the peak among 6 others (μ̄ = 0.5)",
            ["method", "peak agents' regret ÷ random", "other agents' regret ÷ random"], rows_r)


def main():
    plot(run_cells("e29", cells(), cell_fn))


if __name__ == "__main__":
    main()
