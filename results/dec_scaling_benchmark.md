# E19 · Scaling with N

Network regret, quadratic, 6 trials, T = 10 000 per agent.

| design | N=4 | N=8 | N=16 | N=32 | exponent in N |
|---|---|---|---|---|---|
| Flooding + event flooding, complete | 3715 | 4169 | 5912 | 9044 | 0.44 |
| Chebyshev + ESS gossip, complete | 3825 | 4423 | 6343 | 10018 | 0.47 |
| Flooding + event flooding, hypercube | 3712 | 4183 | 6166 | 9413 | 0.46 |
| Chebyshev + ESS gossip, hypercube | 3826 | 4423 | 6347 | 10019 | 0.47 |
| Flooding + event flooding, ring | 3719 | 4202 | 6508 | 11544 | 0.55 |
| Chebyshev + ESS gossip, ring | 3825 | 4427 | 9483 | 22389 | 0.87 |
| Server, same pooled T0 | 3707 | 4152 | 5839 | 8888 | 0.43 |
| Federated, adaptive stop | 3926 | 4800 | 9719 | 20257 | 0.81 |
| Independent agents | 8194 | 17224 | 33310 | 63971 | 0.98 |
