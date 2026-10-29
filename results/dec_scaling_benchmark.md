# E19 · Scaling with N

Network regret, quadratic, 6 trials, T = 10 000 per agent.

| design | N=4 | N=8 | N=16 | N=32 | exponent in N |
|---|---|---|---|---|---|
| Published-only relay, complete | 3724 | 4175 | 5926 | 9067 | 0.44 |
| Chebyshev + ESS gossip, complete | 3825 | 4423 | 6343 | 10018 | 0.47 |
| Published-only relay, hypercube | 3726 | 4189 | 6183 | 9466 | 0.46 |
| Chebyshev + ESS gossip, hypercube | 3826 | 4423 | 6347 | 10019 | 0.47 |
| Published-only relay, ring | 3727 | 4219 | 6514 | 11615 | 0.55 |
| Chebyshev + ESS gossip, ring | 3825 | 4427 | 9483 | 22389 | 0.87 |
| Server, same pooled T0 | 3707 | 4152 | 5839 | 8888 | 0.43 |
| Federated, adaptive stop | 3926 | 4800 | 9719 | 20257 | 0.81 |
| Independent agents | 8194 | 17224 | 33310 | 63971 | 0.98 |
