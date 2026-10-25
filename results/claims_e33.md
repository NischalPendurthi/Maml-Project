# E33: stopping Phase 1 without a server

N = 16, T = 10,000, quadratic link, γ = 0.5, 20 paired trials, mean ± 95% CI. 'fixed' freezes at T0 = 60 with exact tree pooling. 'any' / 'all' run the drift rule on each agent's own flooded estimate ('all' assumes free detection). 'server@tol' is the server's adaptive rule; 'pooled@tol' is the serverless rule of the proposition with the same tolerance. 'lag' is pooled's stopping round minus the server's, per paired trial: the proposition says it equals D. 'disagree' is the mean l1 distance of the frozen directions from their mean.

| graph | D | rule | T0 used | lag vs server | disagree | regret | ÷ fixed | Phase-1 scalars |
|---|---|---|---|---|---|---|---|---|
| torus | 4 | fixed | 60 | – | 0.000 | 7,185 ± 437 | 1.000 | 586 |
| torus | 4 | any | 20 | – | 0.048 | 14,420 ± 4,092 | 2.007 | 114,909 |
| torus | 4 | all | 40 | – | 0.018 | 8,773 ± 1,426 | 1.221 | 235,878 |
| torus | 4 | server@0.15 | 28 | – | 0.000 | 9,972 ± 1,819 | 1.388 | 1,238 |
| torus | 4 | pooled@0.15 | 32 | 4.0 (min 4, max 4) | 0.000 | 10,382 ± 1,832 | 1.445 | 61,645 |
| torus | 4 | server@0.05 | 187 | – | 0.000 | 9,748 ± 1,311 | 1.357 | 2,122 |
| torus | 4 | pooled@0.05 | 191 | 4.0 (min 4, max 4) | 0.000 | 10,102 ± 1,305 | 1.406 | 113,459 |
| ring | 8 | fixed | 60 | – | 0.000 | 7,438 ± 441 | 1.000 | 586 |
| ring | 8 | any | 24 | – | 0.058 | 12,421 ± 2,506 | 1.670 | 61,804 |
| ring | 8 | all | 50 | – | 0.024 | 7,975 ± 772 | 1.072 | 144,333 |
| ring | 8 | server@0.15 | 28 | – | 0.000 | 9,972 ± 1,819 | 1.341 | 1,238 |
| ring | 8 | pooled@0.15 | 36 | 8.0 (min 8, max 8) | 0.000 | 10,750 ± 1,833 | 1.445 | 30,950 |
| ring | 8 | server@0.05 | 187 | – | 0.000 | 9,748 ± 1,311 | 1.311 | 2,122 |
| ring | 8 | pooled@0.05 | 195 | 8.0 (min 8, max 8) | 0.000 | 10,462 ± 1,318 | 1.407 | 56,858 |
| path | 15 | fixed | 60 | – | 0.000 | 7,541 ± 438 | 1.000 | 780 |
| path | 15 | any | 28 | – | 0.058 | 11,217 ± 2,040 | 1.487 | 68,836 |
| path | 15 | all | 54 | – | 0.028 | 8,096 ± 583 | 1.074 | 143,682 |
| path | 15 | server@0.15 | 28 | – | 0.000 | 9,972 ± 1,819 | 1.322 | 1,238 |
| path | 15 | pooled@0.15 | 43 | 15.0 (min 15, max 15) | 0.000 | 11,203 ± 1,821 | 1.485 | 29,226 |
| path | 15 | server@0.05 | 187 | – | 0.000 | 9,748 ± 1,311 | 1.293 | 2,122 |
| path | 15 | pooled@0.05 | 202 | 15.0 (min 15, max 15) | 0.000 | 10,826 ± 1,306 | 1.436 | 53,514 |
