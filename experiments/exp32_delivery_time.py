"""E32 -- delivery time Λ on time-varying and unreliable graphs (Lemma 26, Remarks 27 and 29).

Theorem 17 and Corollary 28 use the graph only through Λ, the number of steps a flooded
message needs to reach every agent.  Lemma 26(ii) says that if the union of every B
consecutive steps is connected, persistent flooding gives Λ = B(N−1), and Remark 27 shows
that this is tight: the diameter of the union graphs does not help.  No bandit is run here;
messages are flooded from every source at once and we record the worst-case arrival step.

Part A  adversarial: in each window a star centred at an uninformed agent, all edges at the
        window's last step.  Measured Λ against B(N−1) and the old (wrong) claim B(D_B + 1).
Part B  benign: a ring / torus whose edges are split into B classes, one class active per
        step (round-robin), so every B-window's union is the base graph.  Measured Λ against
        B·D and B(N−1).
Part C  random link failures (E18's model): each edge down independently w.p. q every step.
        Measured Λ (worst over sources, 200 seeds) against D/(1−q) (Remark 29's scaling).

Writes results/fig32_delivery_time.{png,pdf}, results/claims_e32.md.
"""

from __future__ import annotations

from claims_common import OUT, md_table, np, pick, plt, save, use_style

from src.dec.graph import Graph

NS = pick([4, 9, 16, 36, 64], [4, 16])         # squares, for the torus
BS = [1, 2, 4]
QS = pick([0.0, 0.3, 0.6, 0.9], [0.0, 0.6])
SEEDS = pick(200, 20)
COLOR = {1: "#2a78d6", 2: "#1baf7a", 4: "#eb6834", "ring": "#2a78d6", "torus": "#eb6834"}


def flood_time(arcs_at, N, limit=100_000):
    """Persistent flooding from every source.  arcs_at(s) -> (N, N) bool adjacency at step s.
    Returns the first step count after which every source's message has reached everyone."""
    H = np.eye(N, dtype=bool)                 # H[src, v]: v holds src's message
    for s in range(1, limit + 1):
        A = arcs_at(s)
        H = H | ((H.astype(np.int32) @ A.astype(np.int32)) > 0)
        if H.all():
            return s
    return np.inf


def star_adversary(N, B):
    """Windows of B steps; the only edges, at each window's last step, form a star centred at
    the lowest-numbered agent that source 0's message has not reached yet."""
    H = np.zeros(N, dtype=bool)
    H[0] = True
    s = 0
    while not H.all():
        s += 1
        if s % B:
            continue
        c = int(np.flatnonzero(~H)[0])
        A = np.zeros((N, N), dtype=bool)
        A[c, :] = A[:, c] = True
        A[c, c] = False
        H = H | ((H.astype(np.int32) @ A.astype(np.int32)) > 0)
    return s


def round_robin(base, B):
    A0 = base.A0
    iu = np.argwhere(np.triu(A0))
    cls = np.arange(len(iu)) % B
    mats = []
    for b in range(B):
        A = np.zeros_like(A0)
        e = iu[cls == b]
        A[e[:, 0], e[:, 1]] = A[e[:, 1], e[:, 0]] = True
        mats.append(A)
    return lambda s: mats[s % B]


def failures(base, q, rng):
    A0 = base.A0
    iu = np.argwhere(np.triu(A0))

    def at(s):
        up = iu[rng.random(len(iu)) >= q]
        A = np.zeros_like(A0)
        A[up[:, 0], up[:, 1]] = A[up[:, 1], up[:, 0]] = True
        return A
    return at


def main():
    use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(14, 3.8))
    rows = []

    for B in BS:
        meas = [star_adversary(N, B) for N in NS]
        a.plot(NS, meas, "o", color=COLOR[B], label=f"measured, B = {B}")
        a.plot(NS, [B * (N - 1) for N in NS], "-", color=COLOR[B], lw=1, label=f"B(N−1), B = {B}")
        a.plot(NS, [3 * B for _ in NS], ":", color=COLOR[B], lw=1)
        rows += [["A: star adversary", "star (D_B = 2)", N, B, m, B * (N - 1), 3 * B]
                 for N, m in zip(NS, meas)]
    a.plot([], [], ":", color="#8a8984", label="old claim B(D_B+1) = 3B")
    a.set(xscale="log", yscale="log", xlabel="N (agents)", ylabel="delivery time Λ (steps)",
          title="Adversarial union-connected graph")
    a.legend(fontsize=6)

    for topo in ("ring", "torus"):
        for B, ls in zip(BS, ["-", "--", ":"]):
            meas, bd = [], []
            for N in NS:
                g = Graph(topo, N)
                m = flood_time(round_robin(g, B), N)
                meas.append(m)
                bd.append(B * g.diameter)
                rows.append([f"B: round-robin {topo}", f"{topo} (D = {g.diameter})", N, B, m,
                             B * (N - 1), B * g.diameter])
            b.plot(NS, meas, ls, marker="o", color=COLOR[topo], label=f"{topo}, B = {B}")
    b.plot(NS, [4 * (N - 1) for N in NS], "-", color="#8a8984", lw=0.8, label="B(N−1), B = 4")
    b.set(xscale="log", yscale="log", xlabel="N (agents)", ylabel="delivery time Λ (steps)",
          title="Benign schedule: one edge class per step")
    b.legend(fontsize=6)

    rows3 = []
    N = NS[-1] if NS[-1] <= 64 else 64
    rng = np.random.default_rng(0)
    for topo in ("ring", "torus"):
        g = Graph(topo, N)
        D = g.diameter
        mean, worst = [], []
        for q in QS:
            ts = np.array([flood_time(failures(g, q, rng), N) for _ in range(SEEDS)])
            mean.append(ts.mean())
            worst.append(ts.max())
            rows3.append([topo, N, D, q, f"{ts.mean():.1f}", f"{ts.max():.0f}", f"{D / (1 - q):.1f}"])
        c.plot(QS, mean, "o-", color=COLOR[topo], label=f"{topo} (D = {D}): mean")
        c.plot(QS, worst, "s--", color=COLOR[topo], label=f"{topo}: worst of {SEEDS}")
        c.plot(QS, [D / (1 - q) for q in QS], ":", color=COLOR[topo], label=f"{topo}: D/(1−q)")
    c.set(yscale="log", xlabel="link failure probability q", ylabel="delivery time Λ (steps)",
          title=f"Random link failures, persistent flooding (N = {N})")
    c.legend(fontsize=6)
    fig.tight_layout()
    save(fig, "fig32_delivery_time")

    intro = ("Persistent flooding from every source at once; Λ is the step at which every message "
             "has reached every agent. Part A: star adversary of Remark 27, from source 0. Part B: "
             "base graph's edges in B round-robin classes. Part C: each edge down w.p. q per step, "
             f"{SEEDS} seeds.")
    md_table(f"{OUT}/claims_e32.md", "E32: delivery time on time-varying graphs", intro,
             ["part", "graph", "N", "B", "measured Λ", "Lemma 26(ii): B(N−1)",
              "old claim B(D_B+1) / B·D"], rows)
    with open(f"{OUT}/claims_e32.md", "a") as fh:
        fh.write("\n## Part C: random link failures\n\n| graph | N | D | q | mean Λ | worst Λ | D/(1−q) |\n"
                 "|---|---|---|---|---|---|---|\n")
        fh.write("\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows3) + "\n")


if __name__ == "__main__":
    main()
