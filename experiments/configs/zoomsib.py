"""ZoomSIB-UCB (Dey, Bhore & Ghosh 2026) in the multi-agent setting: N agents that
never talk, each running the unmodified single-agent algorithm (src/zoomsib.py).
The zero-communication reference every federated config is measured against.
"""

ZOOMSIB = {
    "independent": dict(
        engine="independent",
        label="N × ZoomSIB-UCB (no comm.)",
        style=dict(color="#8a8984", ls="--"),
    ),
}
