"""none -- no Phase-2 sharing; each agent runs UCB on its own pulls only.

Combined with a federated Phase 1 this isolates what Phase-1 pooling buys.
"""

from __future__ import annotations

import numpy as np

from .base import Phase2Strategy


class NoShare(Phase2Strategy):
    name = "none"

    def view(self, i):
        return self.own_n[i], self.own_S[i]

    def shared_table(self):
        return np.zeros_like(self.own_n[0]), np.zeros_like(self.own_S[0])

    def pending(self):
        return self.own_n
