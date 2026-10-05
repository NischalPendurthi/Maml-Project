# E24: Phase-1 share of communication

Event-triggered Phase 2 (γ = 0.5), fixed Phase-1 length, quadratic link. Scalars as counted by the engines (index, count and sum per touched bin = 3).

| sweep | setting | d | N | N·T | Phase-1 scalars | Phase-2 scalars | Phase-1 share |
|---|---|---|---|---|---|---|---|
| d sweep | server | 5 | 16 | 160,000 | 208 | 205,937 | 0.10% |
| d sweep | server | 10 | 16 | 160,000 | 368 | 212,112 | 0.17% |
| d sweep | server | 20 | 16 | 160,000 | 688 | 247,684 | 0.28% |
| d sweep | server | 50 | 16 | 160,000 | 1,648 | 259,805 | 0.63% |
| d sweep | server | 100 | 16 | 160,000 | 3,248 | 397,448 | 0.81% |
| d sweep | server | 200 | 16 | 160,000 | 6,448 | 462,980 | 1.37% |
| d sweep | serverless (ring, tree + flood) | 5 | 16 | 160,000 | 436 | 169,971 | 0.26% |
| d sweep | serverless (ring, tree + flood) | 10 | 16 | 160,000 | 586 | 175,995 | 0.33% |
| d sweep | serverless (ring, tree + flood) | 20 | 16 | 160,000 | 886 | 205,473 | 0.43% |
| d sweep | serverless (ring, tree + flood) | 50 | 16 | 160,000 | 1,786 | 235,458 | 0.75% |
| d sweep | serverless (ring, tree + flood) | 100 | 16 | 160,000 | 3,286 | 336,440 | 0.97% |
| d sweep | serverless (ring, tree + flood) | 200 | 16 | 160,000 | 6,286 | 388,206 | 1.59% |
| T sweep | server | 10 | 4 | 10,000 | 92 | 11,801 | 0.79% |
| T sweep | server | 10 | 4 | 40,000 | 92 | 30,317 | 0.32% |
| T sweep | server | 10 | 4 | 160,000 | 92 | 79,924 | 0.12% |
| T sweep | server | 10 | 16 | 40,000 | 368 | 91,443 | 0.41% |
| T sweep | server | 10 | 16 | 160,000 | 368 | 212,112 | 0.18% |
| T sweep | server | 10 | 16 | 640,000 | 368 | 480,238 | 0.08% |

## Quantised Phase-1 upload (N = 16, 20 paired trials)

'Phase-1 saving' = Phase-1 bits saved as % of the exact run's total bits (the most compression of Phase 1 can ever buy). 'Phase-2 change' = how much Phase-2 traffic moved because the frozen direction got noisier.

| d | bits | network regret | regret change | Phase-1 bits | Phase-1 saving | Phase-2 change | Phase-1 share |
|---|---|---|---|---|---|---|---|
| 10 | 32 | 6,911 ± 444 | +0.0% | 11,776 | 0.000% | +0.0% | 0.18% |
| 10 | 2 | 9,500 ± 785 | +37.5% | 7,488 | 0.060% | +4.3% | 0.11% |
| 10 | 4 | 7,011 ± 480 | +1.4% | 7,808 | 0.056% | -2.8% | 0.12% |
| 10 | 8 | 6,907 ± 442 | -0.1% | 8,448 | 0.047% | -0.7% | 0.13% |
| 10 | 16 | 6,916 ± 444 | +0.1% | 9,728 | 0.029% | -0.3% | 0.15% |
| 100 | 32 | 28,704 ± 1,913 | +0.0% | 103,936 | 0.000% | +0.0% | 0.87% |
| 100 | 2 | 42,922 ± 2,630 | +49.5% | 56,448 | 0.377% | +1.6% | 0.47% |
| 100 | 4 | 29,438 ± 1,926 | +2.6% | 59,648 | 0.351% | -0.5% | 0.51% |
| 100 | 8 | 28,738 ± 1,938 | +0.1% | 66,048 | 0.301% | -1.1% | 0.57% |
| 100 | 16 | 28,706 ± 1,916 | +0.0% | 78,848 | 0.199% | -1.1% | 0.67% |
