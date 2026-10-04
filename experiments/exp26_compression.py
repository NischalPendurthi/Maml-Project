"""E26 -- quantisation, top-k and rand-k on Fed-ZoomSIB, measured cleanly.

Claim 3.1 of docs/claims-evidence.md.  One fixed protocol (N = 8, T = 10 000, fixed
pooled Phase-1 size 960, event-triggered Phase 2 with gamma = 0.5, network bin
width) and one change at a time:

    none          exact Phase 1, exact event-triggered Phase 2 (reference)
    p1_*          compress the Phase-1 upload (quant b bits, top-k / rand-k of d)
    p2_*          compress the Phase-2 upload of sum-deltas: quant b bits, or send
                  only a fraction k of touched bins (top-k by news ratio, rand-k),
                  with or without error feedback (ef / noef)
    both_q8       8-bit Phase 1 and 8-bit Phase 2
    anchors       sync every round; no Phase-2 sharing

Bits are counted on the wire (src/fed/compress.py).  Quantised Phase-2 configs
also quantise the server's broadcast (server-side error feedback); top-k / rand-k
configs shrink the broadcast by sending fewer bins.  Indices and counts are always
sent at full precision, the same convention as the uncompressed strategies.

Writes results/fig26_compression.{png,pdf}, results/claims_e26.md.
"""

from __future__ import annotations

from claims_common import (OUT, fmt, md_table, np, pick, plt, run_cells, save, summarize,
                           sweep, trials, use_style)

N, T = 8, pick(10_000, 2500)
T0 = 120                                    # pooled 960
GAMMA = 0.5
LINKS = pick(["quadratic", "zigzag"], ["quadratic"])
NTR = trials(20, 3)


def cfg(p1=None, p2=None, ef=True, phase2=None, phase2_kw=None):
    c = dict(engine="fed", phase1="exact", phase2="event", phase2_kw=dict(gamma=GAMMA),
             freeze="fixed", T0=T0, bin_width="network")
    if p1:
        c.update(phase1="compressed", phase1_kw=dict(compressor=p1))
    if p2:
        c.update(phase2="event_compressed", phase2_kw=dict(gamma=GAMMA, compressor=p2, ef=ef))
    if phase2:
        c.update(phase2=phase2, phase2_kw=phase2_kw or {})
    return c


Q = lambda b: dict(kind="quant", bits=b)            # noqa: E731
TK = lambda k: dict(kind="topk", k=k)               # noqa: E731
RK = lambda k: dict(kind="randk", k=k)              # noqa: E731

CONFIGS = {
    "none": (cfg(), "exact (reference)", "ref"),
    "p1_q2": (cfg(p1=Q(2)), "Phase 1: 2-bit", "p1"),
    "p1_q4": (cfg(p1=Q(4)), "Phase 1: 4-bit", "p1"),
    "p1_q8": (cfg(p1=Q(8)), "Phase 1: 8-bit", "p1"),
    "p1_top25": (cfg(p1=TK(0.25)), "Phase 1: top-25%", "p1"),
    "p1_top50": (cfg(p1=TK(0.5)), "Phase 1: top-50%", "p1"),
    "p1_rand25": (cfg(p1=RK(0.25)), "Phase 1: rand-25%", "p1"),
    "p1_rand50": (cfg(p1=RK(0.5)), "Phase 1: rand-50%", "p1"),
    "p2_q4": (cfg(p2=Q(4)), "Phase 2: 4-bit sums", "p2"),
    "p2_q8": (cfg(p2=Q(8)), "Phase 2: 8-bit sums", "p2"),
    "p2_q16": (cfg(p2=Q(16)), "Phase 2: 16-bit sums", "p2"),
    "p2_top25_ef": (cfg(p2=TK(0.25)), "Phase 2: top-25% bins, EF", "p2"),
    "p2_top50_ef": (cfg(p2=TK(0.5)), "Phase 2: top-50% bins, EF", "p2"),
    "p2_top25_noef": (cfg(p2=TK(0.25), ef=False), "Phase 2: top-25% bins, no EF", "p2"),
    "p2_rand50_ef": (cfg(p2=RK(0.5)), "Phase 2: rand-50% bins, EF", "p2"),
    "p2_rand50_noef": (cfg(p2=RK(0.5), ef=False), "Phase 2: rand-50% bins, no EF", "p2"),
    "both_q8": (cfg(p1=Q(8), p2=Q(8)), "8-bit Phase 1 + 8-bit Phase 2", "both"),
    "sync1": (cfg(phase2="periodic", phase2_kw=dict(every=1)), "anchor: sync every round", "anchor"),
    "nosync": (cfg(phase2="none"), "anchor: no Phase-2 sharing", "anchor"),
}
COLOR = dict(ref="#1a1a1a", p1="#2a78d6", p2="#eb6834", both="#4a3aa7", anchor="#8a8984")


def cell_fn(cell, names=None):
    (link,) = cell
    cfgs = {k: v[0] for k, v in CONFIGS.items() if names is None or k in names}
    out, _ = sweep(cfgs, NTR, N, T, link)
    return summarize(out)


def plot(res):
    use_style()
    fig, axes = plt.subplots(1, len(LINKS), figsize=(6.2 * len(LINKS), 4.4), squeeze=False)
    rows = []
    for ax, link in zip(axes[0], LINKS):
        cell = res[(link,)]
        ref = cell["none"]
        for key, (_, lab, fam) in CONFIGS.items():
            r = cell[key]
            x, y = r["bits"].mean(), r["R"].mean() / ref["R"].mean()
            ax.scatter(x, y, color=COLOR[fam], s=22, zorder=3,
                       marker={"p1": "o", "p2": "s", "both": "D", "ref": "*", "anchor": "^"}[fam])
            ax.annotate(lab.replace("Phase ", "P"), (x, y), fontsize=5.5,
                        xytext=(3, 2), textcoords="offset points")
            p1b = r["bits1"].mean()
            rows.append([link, lab, fmt(r["R"]), f"{y:.3f}", f"{p1b:,.0f}",
                         f"{r['bits'].mean() - p1b:,.0f}", f"{r['bits'].mean():,.0f}",
                         f"{100 * (1 - r['bits'].mean() / ref['bits'].mean()):+.1f}%",
                         f"{(r['rounds'] - r['rounds1']).mean():,.0f}"])
        ax.axhline(1, color="#8a8984", lw=0.8)
        ax.set(xscale="log", xlabel="total bits on the wire",
               ylabel="regret ÷ exact reference", title=f"{link}: N = {N}, T = {T:,}")
        for fam, lab in (("p1", "compress Phase 1"), ("p2", "compress Phase 2"),
                         ("both", "both"), ("anchor", "anchors")):
            ax.scatter([], [], color=COLOR[fam], label=lab)
        ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    save(fig, "fig26_compression")
    md_table(f"{OUT}/claims_e26.md", "E26: compression in Fed-ZoomSIB",
             f"N = {N}, T = {T:,}, pooled Phase-1 size 960 (fixed), event-triggered Phase 2 "
             f"(γ = {GAMMA}), {NTR} paired trials, mean ± 95% CI. Bits on the wire; quantised "
             "Phase-2 configs quantise upload and broadcast; index and count always 32 bits. "
             "'bits saved' is against the exact reference.",
             ["link", "configuration", "network regret", "ratio", "Phase-1 bits", "Phase-2 bits",
              "total bits", "bits saved", "Phase-2 syncs"], rows)


def main():
    plot(run_cells("e26", [(link,) for link in LINKS], cell_fn))


if __name__ == "__main__":
    main()
