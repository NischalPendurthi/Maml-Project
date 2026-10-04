"""scheduled -- server sync at a fixed list of rounds (a batched schedule).

Agents act on the shared table plus their own unsynced pulls, exactly as in
`periodic`, but the server merges only at the rounds in `times` (absolute
round numbers t, as counted by the engine).  With M sync times this is an
M-batch learner -- the setting of batched bandits (Perchet et al. 2016; Gao et
al. 2019; Feng, Huang & Wang 2022 for Lipschitz arms), used by exp27 to ask
how few communication rounds the optimal regret really needs.

`grid(kind, M, start, end)` builds the two standard schedules:
    geometric  t_k = start + (end − start)^{k/M}
    minimax    Perchet's grid  t_k = start + a^{2 − 2^{1−k}},
               a = (end − start)^{1/(2 − 2^{1−M})}
"""

from __future__ import annotations

import numpy as np

from .base import ServerSync


def grid(kind, M, start, end):
    L = max(1, end - start)
    k = np.arange(1, M + 1)
    if kind == "geometric":
        pts = L ** (k / M)
    elif kind == "minimax":
        a = L ** (1.0 / (2.0 - 2.0 ** (1 - M)))
        pts = a ** (2.0 - 2.0 ** (1.0 - k))
    else:
        raise ValueError(kind)
    t = start + np.minimum(np.round(pts), L).astype(int)
    return sorted(set(int(x) for x in t))


class ScheduledSync(ServerSync):
    name = "scheduled"

    def __init__(self, times=()):
        self.times = set(int(t) for t in times)

    def end_round(self, t):
        if t in self.times and self.dn.any():
            return self.sync(), "sync"
        return 0, None
