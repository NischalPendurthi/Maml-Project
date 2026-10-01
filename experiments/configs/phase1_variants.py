"""Phase-1 pooling strategies (src/fed/phase1/), with Phase 2 fixed to a
server sync every round so only the theta estimate differs."""

_P2 = dict(phase2="periodic", phase2_kw=dict(every=1))

PHASE1_VARIANTS = {
    "p1_exact": dict(engine="fed", phase1="exact", **_P2,
                     label="exact (pooled Stein sums)", style=dict(color="#2a78d6")),
    "p1_normavg": dict(engine="fed", phase1="normavg", **_P2,
                       label="normavg (FedAvg of local estimates)", style=dict(color="#eb6834")),
    "p1_median": dict(engine="fed", phase1="median", **_P2,
                      label="median (coordinate-wise)", style=dict(color="#1baf7a")),
    "p1_quant8": dict(engine="fed", phase1="quantized", phase1_kw=dict(bits=8), **_P2,
                      label="quantized, 8 bits", style=dict(color="#4a3aa7")),
    "p1_quant4": dict(engine="fed", phase1="quantized", phase1_kw=dict(bits=4), **_P2,
                      label="quantized, 4 bits", style=dict(color="#e87ba4")),
    "p1_quant2": dict(engine="fed", phase1="quantized", phase1_kw=dict(bits=2), **_P2,
                      label="quantized, 2 bits", style=dict(color="#eda100")),
}
