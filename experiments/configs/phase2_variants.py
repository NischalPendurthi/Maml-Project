"""Phase-2 sharing strategies (src/fed/phase2/), with Phase 1 fixed to exact
pooling so only the bin-statistics sharing differs."""

_P1 = dict(engine="fed", phase1="exact")


def sync_period_sweep(periods=(1, 2, 5, 10, 25, 50, 100, 250, 1000)):
    """periodic server sync at each period in `periods`."""
    return {f"p2_periodic_{c}": dict(**_P1, phase2="periodic", phase2_kw=dict(every=c),
                                     label=f"periodic, every {c}")
            for c in periods}


PHASE2_VARIANTS = {
    **sync_period_sweep(),
    "p2_event_0.5": dict(**_P1, phase2="event", phase2_kw=dict(gamma=0.5),
                         label="event-triggered, γ=0.5"),
    "p2_event_1": dict(**_P1, phase2="event", phase2_kw=dict(gamma=1.0),
                       label="event-triggered, γ=1"),
    "p2_event_2": dict(**_P1, phase2="event", phase2_kw=dict(gamma=2.0),
                       label="event-triggered, γ=2"),
    "p2_ring": dict(**_P1, phase2="neighbor", phase2_kw=dict(graph="ring", every=1),
                    label="peer-to-peer ring"),
    "p2_complete": dict(**_P1, phase2="neighbor", phase2_kw=dict(graph="complete", every=1),
                        label="peer-to-peer complete graph"),
    "p2_none": dict(**_P1, phase2="none", label="no Phase-2 sharing"),
}
