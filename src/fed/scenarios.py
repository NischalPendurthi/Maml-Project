"""Heterogeneity scenarios: how the N agents' environments differ.

FL methods were designed for heterogeneous clients, so whether any of them is
"relevant" here depends on which heterogeneity the bandit network actually has.
Each scenario builds N SIBEnv-compatible environments for one problem instance:

  iid            all agents identical in distribution (the base setting)
  participation  agent i is active each round only w.p. p_i, spread linearly
                 from 1 down to 1 − strength (default 0.8: 1.0 … 0.2).  Inactive
                 agents skip the round: quantity skew in both phases, the
                 setting FedNova / weighting choices are about
  covariate      agent i's contexts are N(m_i, s² I) with ⟨m_i, θ*⟩ = c_i spread
                 over [−strength, strength] (default 1.5).  θ* and f are shared,
                 but each agent samples a different part of the index line, so
                 μ_i = E_i[f'] differs -- and on non-monotone links can change
                 SIGN.  Each agent knows its own density, hence its own score.
  concept        agent i has its own θ*_i = normalise(θ* + strength · g_i)
                 (default 0.5): the shared-θ* assumption fails, the setting
                 personalised FL is about (extension E3)

Activity is drawn from a stream separate from contexts and noise, so every
algorithm sees the same contexts AND the same participation pattern.
"""

from __future__ import annotations

import numpy as np

from ..envs import SIBEnv
from ..stein import normalize_l1

SCENARIOS = ("iid", "participation", "covariate", "concept")
DEFAULT_STRENGTH = {"iid": 0.0, "participation": 0.8, "covariate": 1.5, "concept": 0.5}


class ParticipatingEnv(SIBEnv):
    def __init__(self, *a, p_active=1.0, active_seed=0, **kw):
        super().__init__(*a, **kw)
        self.p_active = float(p_active)
        self._arng = np.random.default_rng(active_seed)

    def is_active(self):
        return bool(self._arng.random() < self.p_active)


class ShiftedEnv(SIBEnv):
    """Contexts N(ctx_mean, ctx_std² I); the agent knows its own density."""

    def __init__(self, *a, index_mean=0.0, **kw):
        super().__init__(*a, **kw)
        th = self.theta_star
        self.ctx_mean = index_mean * th / float(th @ th)       # ⟨m, θ*⟩ = index_mean

    def draw_arms(self):
        return super().draw_arms() + self.ctx_mean

    def score(self, X):
        return (X - self.ctx_mean) / self.ctx_std ** 2

    def mu_star(self, n=200_000, seed=0):
        rng = np.random.default_rng(seed)
        z = rng.standard_normal(n) * self.index_std + float(self.ctx_mean @ self.theta_star)
        h = 1e-4
        return float(np.mean((self.f(z + h) - self.f(z - h)) / (2 * h)))


class ConceptEnv(SIBEnv):
    """Own direction θ*_i near a shared θ*; contexts and f as the base env."""

    def __init__(self, *a, rho=0.5, agent_seed=0, **kw):
        super().__init__(*a, **kw)
        g = np.random.default_rng(agent_seed).standard_normal(self.d)
        self.theta_star = normalize_l1(self.theta_star + rho * g / np.abs(g).sum())
        self.index_std = self.ctx_std * float(np.linalg.norm(self.theta_star))


def make_scenario_envs(scenario, N, d, K, link, sigma=0.1, seed=0, run_seed=0,
                       index_scale=1.0, strength=None):
    s = DEFAULT_STRENGTH[scenario] if strength is None else float(strength)
    common = dict(d=d, K=K, link=link, sigma=sigma, seed=seed, index_scale=index_scale)
    envs = []
    for i in range(N):
        rs = [run_seed, i]
        if scenario == "iid":
            e = SIBEnv(run_seed=rs, **common)
        elif scenario == "participation":
            p = 1.0 - s * i / max(N - 1, 1)
            e = ParticipatingEnv(run_seed=rs, p_active=p, active_seed=[run_seed, i, 7], **common)
        elif scenario == "covariate":
            c = -s + 2 * s * i / max(N - 1, 1)
            e = ShiftedEnv(run_seed=rs, index_mean=c, **common)
        elif scenario == "concept":
            e = ConceptEnv(run_seed=rs, rho=s, agent_seed=[seed, i, 11], **common)
        else:
            raise ValueError(f"unknown scenario {scenario!r}")
        envs.append(e)
    return envs
