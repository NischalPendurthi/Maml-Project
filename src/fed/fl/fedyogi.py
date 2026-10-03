"""FedYogi (Reddi et al. 2021).

Identical to FedAdam except for the second-moment update, which grows only
additively and so cannot blow the effective step size up after a large update:
              v ← v − (1−β2) Δ² sign(v − Δ²).
"""

from __future__ import annotations

import numpy as np

from .fedadam import FedAdam


class FedYogi(FedAdam):
    name = "fedyogi"
    label = "FedYogi (server Yogi)"

    def _second_moment(self, delta):
        d2 = delta ** 2
        return self.v - (1 - self.beta2) * d2 * np.sign(self.v - d2)
