"""E9 -- watch Fed-ZoomSIB run: a live dashboard of the network, written to a GIF.

Runs ONE episode of any config from experiments/configs/ with N agents, records
the network on a frame schedule (every round of Phase 1, every few rounds over
the first Phase-2 sync cycles, geometric after that) and renders src/fed/viz.py's
dashboard for each frame:

  network     server + agents; arrows light up when a message moves, with what
              it carries; '+k' badges = an agent's pulls the others haven't seen
  theta       true theta_* vs each agent's own Stein estimate vs the federated one
  error       ||theta_hat - theta_*||_1 through Phase 1, local vs federated
  index line  true f, the shared bin table (mean + UCB), and stacked bars of
              which agent's pulls fed each bin (hatched = still unsynced)
  regret      network regret vs N independent ZoomSIB-UCB agents on the SAME contexts

The default config syncs Phase 2 every 25 rounds so the accumulate-then-merge
cycle is visible; pass --config fed_zoomsib for every-round sync, or any other
config name (e.g. p2_event_1, p2_ring).

    python experiments/exp09_fed_live.py                         # -> results/fed_live.gif
    python experiments/exp09_fed_live.py --config p2_ring --link zigzag
    python experiments/exp09_fed_live.py --live                  # also play in a window

Produces: results/fed_live_<config>_<link>.gif and a PNG of the last frame.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import ALL, ZOOMSIB                                 # noqa: E402
from src.fed import build_fed, make_fed_envs, run_fed_episode    # noqa: E402
from src.fed.viz import Dashboard, Recorder                      # noqa: E402


def parse():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", default="p2_periodic_25", choices=sorted(ALL))
    ap.add_argument("--link", default="quadratic")
    ap.add_argument("--N", type=int, default=6)
    ap.add_argument("--d", type=int, default=10)
    ap.add_argument("--K", type=int, default=20)
    ap.add_argument("--T", type=int, default=6000)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--fps", type=int, default=8)
    ap.add_argument("--dpi", type=int, default=80)
    ap.add_argument("--live", action="store_true", help="also play the frames in a window")
    ap.add_argument("--out", default=None)
    return ap.parse_args()


def main():
    a = parse()
    if a.N > 8:
        sys.exit("the dashboard colours up to 8 agents")
    cfg = ALL[a.config]
    if cfg.get("engine") != "fed":
        sys.exit("pick a federated config (engine='fed')")

    kw = dict(seed=1000 + a.seed, run_seed=50_000 + a.seed, index_scale=1.0)
    print(f"[exp09] reference: {a.N} independent ZoomSIB-UCB agents", flush=True)
    envs = make_fed_envs(a.N, a.d, a.K, a.link, **kw)
    ind = build_fed(ZOOMSIB["independent"], envs, a.T, np.random.default_rng(a.seed))
    ind_curve = run_fed_episode(envs, ind, a.T)[0]

    print(f"[exp09] {cfg['label']}", flush=True)
    envs = make_fed_envs(a.N, a.d, a.K, a.link, **kw)
    algo = build_fed(cfg, envs, a.T, np.random.default_rng(a.seed))
    rec = Recorder(envs, a.T)
    fed_curve = run_fed_episode(envs, algo, a.T, callback=rec)[0]
    dg = algo.diagnostics()
    print(f"    Phase 1 ended at round {rec.t_freeze} (per agent); "
          f"{dg['N_bins']} bins; {dg['comm_rounds']:,} comm rounds, "
          f"{dg['comm_scalars']:,} scalars; network regret {fed_curve[-1]:,.0f} "
          f"vs {ind_curve[-1]:,.0f} independent", flush=True)

    # Hold the moments worth reading: the freeze and the final state.
    frames = []
    for s in rec.frames:
        hold = 6 if s["events"].get("freeze") else 1
        frames += [s] * hold
    frames += [rec.frames[-1]] * 16
    print(f"    {len(rec.frames)} distinct frames, {len(frames)} with holds", flush=True)

    import matplotlib
    if not a.live:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    fig = plt.figure(figsize=(16, 9), dpi=a.dpi)
    dash = Dashboard(fig, rec, link_fn=envs[0].f, link_name=a.link, N=a.N, d=a.d, K=a.K,
                     T=a.T, phase2_desc=cfg["label"],
                     ind_curve=ind_curve, fed_curve=fed_curve)

    os.makedirs("results", exist_ok=True)
    out = a.out or f"results/fed_live_{a.config}_{a.link}.gif"
    t0 = time.time()
    anim = FuncAnimation(fig, lambda k: dash.draw(frames[k]), frames=len(frames),
                         interval=1000 // a.fps, repeat=False)
    anim.save(out, writer=PillowWriter(fps=a.fps), dpi=a.dpi)
    print(f"  wrote {out}  ({os.path.getsize(out) / 1e6:.1f} MB, {time.time() - t0:.0f}s)")

    dash.draw(rec.frames[-1])
    png = out.replace(".gif", "_final.png")
    fig.savefig(png, dpi=110, facecolor=fig.get_facecolor())
    print(f"  wrote {png}")

    if a.live:
        plt.ion()
        for s in frames:
            dash.draw(s)
            plt.pause(1.0 / a.fps)
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
