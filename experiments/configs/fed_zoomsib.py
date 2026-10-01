"""Fed-ZoomSIB: exact Stein pooling in Phase 1 + server-synced bin table in Phase 2.

`fed_p1_only` keeps the federated Phase 1 but lets each agent run Phase 2 on its
own pulls: the difference between the two is what Phase-2 sharing buys, the
difference to `independent` is what one Phase-1 message buys.
"""

FED_ZOOMSIB = {
    "fed_zoomsib": dict(
        engine="fed", phase1="exact", phase2="periodic", phase2_kw=dict(every=1),
        label="Fed-ZoomSIB (exact + sync every round)",
        style=dict(color="#2a78d6", ls="-"),
    ),
    "fed_p1_only": dict(
        engine="fed", phase1="exact", phase2="none",
        label="Fed-ZoomSIB, Phase 1 only",
        style=dict(color="#eb6834", ls="-."),
    ),
}
