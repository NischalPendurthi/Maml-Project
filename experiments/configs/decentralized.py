"""Decentralised Fed-ZoomSIB configurations (communication matrix, no server) -- E14–E21.

An algorithm is engine="dec" + a graph + a Phase-1 strategy (src/dec/phase1/) +
a Phase-2 strategy (src/dec/phase2/):

    dec_config("torus", "chebyshev", dict(k=10), "flood", dict(gamma=0.5))

The federated (server) version and N independent agents are kept as the two
reference points: what a server buys, and what no communication costs.
"""

from __future__ import annotations

# Phase-1 strategies: key -> (strategy, fixed kwargs, tuning grid, communication model)
DEC_P1 = {
    "flood":     ("flood", {}, [{}], "interleaved"),
    "consensus": ("consensus", {}, [{"steps": s} for s in (1, 2, 5)], "interleaved"),
    "pushsum":   ("pushsum", {}, [{}], "interleaved"),
    "gossip":    ("gossip", {}, [{"k": k} for k in (5, 10, 20, 50)], "burst"),
    "chebyshev": ("chebyshev", {}, [{"k": k} for k in (5, 10, 20)], "burst"),
    "tree":      ("tree", {}, [{}], "burst"),
    "dgd":       ("dgd", {}, [{"k": k, "lr": lr} for k in (10, 50) for lr in (0.02, 0.1, 0.3)],
                  "burst"),
    "gt":        ("gt", {}, [{"k": k, "lr": lr} for k in (10, 50) for lr in (0.02, 0.05, 0.1)],
                  "burst"),
    "dlocal":    ("dlocal", {}, [{"k": k, "lr": lr, "local_steps": E}
                                 for k in (10, 50) for lr in (0.1, 0.5) for E in (1, 5)], "burst"),
    "local":     ("local", {}, [{}], "none"),
    "server":    ("server", {}, [{}], "server"),
}

P1_LABEL = {
    "flood": "Flooding (exact, delayed)", "consensus": "Running consensus",
    "pushsum": "Push-sum", "gossip": "Burst gossip", "chebyshev": "Chebyshev gossip",
    "tree": "Spanning tree (exact)", "dgd": "DGD", "gt": "Gradient tracking",
    "dlocal": "Decentralised FedAvg", "local": "Local only (no comm.)",
    "server": "Server (reference)",
}

# Phase-2 strategies: key -> (strategy, kwargs)
DEC_P2 = {
    "flood":        ("flood", {}),
    "flood_event":  ("flood", {"gamma": 0.5}),
    "flood_10":     ("flood", {"every": 10}),
    "consensus":    ("consensus", {}),
    "consensus_x2": ("consensus", {"inflate": 2.0}),
    "pushsum":      ("pushsum", {}),
    "gossip_naive": ("gossip", {"k": 5, "every": 10, "ess": False}),
    "gossip_ess":   ("gossip", {"k": 5, "every": 10, "ess": True}),
    "cheb_ess":     ("gossip", {"k": 5, "every": 10, "ess": True, "accelerate": True}),
    "neighbor":     ("neighbor", {}),
    "server":       ("server", {}),
    "server_event": ("server_event", {"gamma": 0.5}),
    "none":         ("none", {}),
}

P2_LABEL = {
    "flood": "Flooding, every round", "flood_event": "Flooding, event-triggered γ=0.5",
    "flood_10": "Flooding, every 10", "consensus": "Running consensus (Landgren)",
    "consensus_x2": "Running consensus, counts ÷ 2", "pushsum": "Push-sum",
    "gossip_naive": "Gossip ×5 / 10 rounds, naive counts",
    "gossip_ess": "Gossip ×5 / 10 rounds, ESS counts",
    "cheb_ess": "Chebyshev ×5 / 10 rounds, ESS counts",
    "neighbor": "One-hop neighbours", "server": "Server, every round (reference)",
    "server_event": "Server, event-triggered (reference)", "none": "No sharing",
}

# What each Phase-2 key is, for colouring (fixed hue order).
P2_FAMILY = {"flood": "relay", "flood_event": "relay", "flood_10": "relay",
             "consensus": "consensus", "consensus_x2": "consensus", "pushsum": "consensus",
             "gossip_naive": "burst gossip", "gossip_ess": "burst gossip", "cheb_ess": "burst gossip",
             "neighbor": "one-hop", "server": "server", "server_event": "server", "none": "none"}
FAMILY_COLOR = {"relay": "#2a78d6", "consensus": "#eb6834", "burst gossip": "#1baf7a",
                "one-hop": "#eda100", "server": "#4a3aa7", "none": "#8a8984"}

FED_REFERENCE = dict(engine="fed", phase1="exact", phase2="fl",
                     phase2_kw=dict(method="suffstat", gamma=0.5),
                     label="Federated: server, event-triggered (recommended)")
INDEPENDENT = dict(engine="independent", label="Independent agents (no comm.)")


def p1_kwargs(key, tuned=None):
    name, fixed, grid, _ = DEC_P1[key]
    return name, dict(fixed, **((tuned or {}).get(key, grid[0])))


T0_FAIR = 60     # fixed Phase-1 length (rounds per agent) used for fair comparisons


def dec_config(graph, p1="flood", p1_kw=None, p2="flood", p2_kw=None, graph_kw=None,
               label=None, stop_rule="all", freeze="fixed", T0=T0_FAIR, **engine_kw):
    """Decentralised config.

    freeze="fixed" (default): every agent freezes at round T0, so two designs
    differ ONLY in how they communicate.  With adaptive stopping, agents that
    disagree explore longer, and a longer Phase 1 alone lowers regret at N = 16 --
    which confounds topology, mixing and strategy with Phase-1 length (E16, E17).
    Pass freeze="adaptive" to study the stopping rule itself (E14).

    stop_rule (adaptive only) defaults to "all": with "any" the network freezes
    at the EARLIEST of N agents' stopping times and regret roughly doubles (E14).
    """
    if freeze == "fixed":
        engine_kw["T0"] = T0
    return dict(engine="dec", graph=graph, graph_kw=graph_kw or {}, stop_rule=stop_rule,
                freeze=freeze,
                phase1=p1, phase1_kw=p1_kw or {}, phase2=p2, phase2_kw=p2_kw or {},
                label=label or f"{p1} + {p2} on {graph}", **engine_kw)


def dec_from_keys(graph, k1, k2, tuned=None, graph_kw=None, **engine_kw):
    """Build a config from DEC_P1 / DEC_P2 keys (Phase-1 kwargs from `tuned` if given)."""
    n1, kw1 = p1_kwargs(k1, tuned)
    n2, kw2 = DEC_P2[k2]
    return dec_config(graph, n1, kw1, n2, kw2, graph_kw=graph_kw,
                      label=f"{P1_LABEL[k1]} + {P2_LABEL[k2]}", **engine_kw)
