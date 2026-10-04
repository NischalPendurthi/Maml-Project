"""E21 -- watch decentralised Fed-ZoomSIB run on a graph, written to a GIF.

The decentralised counterpart of exp09: same panels, but the network panel
draws the actual communication graph (edges light up when they carry a
message) and the θ panel shows every agent's own CONSENSUS estimate, so you can
watch gossip pull the agents' directions together before the freeze.

    python experiments/exp21_dec_live.py                                  # ring, consensus + flooding
    python experiments/exp21_dec_live.py --graph hypercube --p1 chebyshev --p2 gossip
    python experiments/exp21_dec_live.py --graph directed --p1 pushsum --p2 pushsum
    python experiments/exp21_dec_live.py --failure 0.5                    # unreliable links
    python experiments/exp21_dec_live.py --live                           # also play in a window

Produces results/dec_live_<graph>_<p1>_<p2>.gif and a PNG of the last frame.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import ZOOMSIB                                      # noqa: E402
from configs.decentralized import dec_config                     # noqa: E402
from src.dec.phase1 import DEC_PHASE1                            # noqa: E402
from src.dec.phase2 import DEC_PHASE2                            # noqa: E402
from src.dec.viz import DecDashboard                             # noqa: E402
from src.fed import build_fed, make_fed_envs, run_fed_episode    # noqa: E402
from src.fed.viz import Recorder                                 # noqa: E402

P1_DEFAULT_KW = {"consensus": {"steps": 1}, "chebyshev": {"k": 20}, "gossip": {"k": 20}}
P2_DEFAULT_KW = {"flood": {"gamma": 0.5}, "gossip": {"k": 5, "every": 10, "ess": True,
                                                     "accelerate": True}}


def parse():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--graph", default="ring")
    ap.add_argument("--N", type=int, default=8)
    ap.add_argument("--p1", default="consensus", choices=sorted(DEC_PHASE1))
    ap.add_argument("--p2", default="flood", choices=sorted(DEC_PHASE2))
    ap.add_argument("--failure", type=float, default=0.0)
    ap.add_argument("--link", default="quadratic")
    ap.add_argument("--T", type=int, default=6000)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--fps", type=int, default=8)
    ap.add_argument("--dpi", type=int, default=80)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--out", default=None)
    return ap.parse_args()


def main():
    a = parse()
    if a.N > 8:
        sys.exit("the dashboard colours up to 8 agents")
    d, K = 10, 20
    kw = dict(seed=1000 + a.seed, run_seed=50_000 + a.seed, index_scale=1.0)
    envs = make_fed_envs(a.N, d, K, a.link, **kw)
    ind = build_fed(ZOOMSIB["independent"], envs, a.T, np.random.default_rng(a.seed))
    ind_curve = run_fed_episode(envs, ind, a.T)[0]

    cfg = dec_config(a.graph, a.p1, P1_DEFAULT_KW.get(a.p1, {}), a.p2,
                     P2_DEFAULT_KW.get(a.p2, {}),
                     graph_kw=dict(failure=a.failure) if a.failure else {})
    envs = make_fed_envs(a.N, d, K, a.link, **kw)
    algo = build_fed(cfg, envs, a.T, np.random.default_rng(a.seed))
    rec = Recorder(envs, a.T)
    curve = run_fed_episode(envs, algo, a.T, callback=rec)[0]
    dg = algo.diagnostics()
    print(f"[exp21] {dg['graph']}\n    Phase 1 ended at round {rec.t_freeze}; disagreement "
          f"{dg['disagreement']:.3f}; {dg['comm_scalars']:,} scalars; network regret "
          f"{curve[-1]:,.0f} vs {ind_curve[-1]:,.0f} independent", flush=True)

    frames = []
    for s in rec.frames:
        frames += [s] * (6 if s["events"].get("freeze") else 1)
    frames += [rec.frames[-1]] * 16

    import matplotlib
    if not a.live:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    fig = plt.figure(figsize=(16, 9), dpi=a.dpi)
    dash = DecDashboard(fig, rec, graph=algo.g, p1_name=a.p1, p2_name=a.p2,
                        link_fn=envs[0].f, link_name=a.link, N=a.N, d=d, K=K, T=a.T,
                        phase2_desc=f"{a.p2} over the graph",
                        ind_curve=ind_curve, fed_curve=curve)
    os.makedirs("results", exist_ok=True)
    tag = f"{a.graph}{'_fail' + str(a.failure) if a.failure else ''}_{a.p1}_{a.p2}"
    out = a.out or f"results/dec_live_{tag}.gif"
    t0 = time.time()
    anim = FuncAnimation(fig, lambda k: dash.draw(frames[k]), frames=len(frames),
                         interval=1000 // a.fps, repeat=False)
    anim.save(out, writer=PillowWriter(fps=a.fps), dpi=a.dpi)
    print(f"  wrote {out}  ({os.path.getsize(out) / 1e6:.1f} MB, {time.time() - t0:.0f}s)")
    dash.draw(rec.frames[-1])
    fig.savefig(out.replace(".gif", "_final.png"), dpi=110, facecolor=fig.get_facecolor())
    if a.live:
        plt.ion()
        for s in frames:
            dash.draw(s)
            plt.pause(1.0 / a.fps)
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
