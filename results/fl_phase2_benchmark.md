# E11 · FL methods for Phase 2 (bin-table sharing)

N = 8, d = 10, K = 20.  Part A: real bin tables at t ∈ [400, 1500, 4000], 6 reps per scenario, warm start from the table 10 rounds earlier.  Part B: bandit, T = 10,000, sync every 10 rounds with 5 FL rounds, 8 trials.

## A · staleness error left after R rounds (1 = none removed, 0 = exact)

| method | family | tuned | scalars/round | iid R=1 | iid R=5 | iid R=50 | participation R=1 | participation R=5 | participation R=50 | covariate R=1 | covariate R=5 | covariate R=50 | concept R=1 | concept R=5 | concept R=50 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sufficient statistics (exact) | exact | `{}` | 1022 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 |
| Split learning | exact | `{}` | 1040 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 | 1e-16 |
| One-shot FedAvg | averaging | `{}` | 1438 | 5 | 5 | 5 | 7.7 | 7.7 | 7.7 | 11 | 11 | 11 | 6.5 | 6.5 | 6.5 |
| Fed. distillation | averaging | `{}` | 1430 | 6.4 | 6.4 | 6.4 | 14 | 14 | 14 | 20 | 20 | 20 | 8.4 | 8.4 | 8.4 |
| FedSGD / gradient-based | gradient | `{'lr_scale': 1.0}` | 1430 | 0.81 | 0.58 | 0.083 | 0.69 | 0.39 | 0.019 | 0.95 | 0.82 | 0.3 | 0.81 | 0.55 | 0.089 |
| FedAvg | averaging | `{'local_steps': 1, 'lr_scale': 1.0}` | 1430 | 0.82 | 0.6 | 0.098 | 0.72 | 0.42 | 0.027 | 0.97 | 0.88 | 0.44 | 0.82 | 0.57 | 0.1 |
| FedAvg, steps ∝ data | averaging | `{'local_steps': 1, 'lr_scale': 1.0}` | 1430 | 0.82 | 0.6 | 0.098 | 1 | 1.7 | 3.9 | 0.97 | 0.88 | 0.44 | 0.82 | 0.57 | 0.1 |
| FedProx | averaging | `{'local_steps': 5, 'mu_rel': 1.0}` | 1430 | 0.87 | 0.66 | 0.32 | 0.81 | 0.52 | 0.3 | 0.98 | 0.95 | 0.68 | 0.92 | 0.84 | 0.64 |
| FedNova | drift correction | `{'local_steps': 5, 'lr_scale': 0.1}` | 1438 | 0.91 | 0.73 | 0.28 | 0.86 | 0.64 | 0.44 | 0.99 | 0.94 | 0.64 | 0.92 | 0.75 | 0.39 |
| FedAvgM | server optimiser | `{'local_steps': 1, 'server_lr': 1.0, 'beta': 0.5}` | 1430 | 0.82 | 0.48 | 0.01 | 0.72 | 0.33 | 0.00054 | 0.97 | 0.82 | 0.24 | 0.82 | 0.44 | 0.019 |
| FedAdam | server optimiser | `{'local_steps': 1, 'server_lr': 0.03}` | 1430 | 0.77 | 0.57 | 0.061 | 0.64 | 0.55 | 0.057 | 0.96 | 0.64 | 0.071 | 0.76 | 0.59 | 0.066 |
| FedYogi | server optimiser | `{'local_steps': 1, 'server_lr': 0.03}` | 1430 | 0.77 | 0.57 | 0.059 | 0.64 | 0.55 | 0.053 | 0.96 | 0.64 | 0.069 | 0.76 | 0.59 | 0.069 |
| SCAFFOLD | drift correction | `{'local_steps': 5, 'lr_scale': 1.0}` | 2860 | 0.76 | 0.29 | 0.0057 | 0.69 | 0.19 | 0.0026 | 1.2 | 0.64 | 0.066 | 1.4 | 0.46 | 0.0071 |
| FedDyn | drift correction | `{'local_steps': 20, 'alpha_rel': 0.1}` | 1430 | 0.99 | 0.29 | 0.0049 | 3.8 | 0.62 | 0.003 | 1.9 | 0.63 | 0.014 | 2.3 | 0.61 | 0.0093 |

## B · bandit network regret (mean over trials) and communication

| config | iid · quadratic | iid · zigzag | participation · quadratic | participation · zigzag | covariate · quadratic | covariate · zigzag | concept · quadratic | concept · zigzag | scalars (iid·quad) | rounds (iid·quad) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N × ZoomSIB-UCB (no comm.) | 17270 | 7139 | 14447 | 5978 | 28656 | 12914 | 16359 | 7287 | 0 | 0 |
| Sufficient statistics (exact) | 5415 | 3679 | 5547 | 1786 | 9984 | 4191 | 20820 | 11227 | 1,258,216 | 1,002 |
| Split learning | 5415 | 3679 | 5547 | 1786 | 9984 | 4191 | 20820 | 11227 | 1,263,784 | 1,002 |
| One-shot FedAvg | 5419 | 3705 | 5553 | 1807 | 10189 | 4440 | 20889 | 11266 | 2,071,717 | 1,002 |
| Fed. distillation | 5423 | 3685 | 5548 | 1789 | 10179 | 4431 | 20842 | 11231 | 2,075,146 | 1,002 |
| FedSGD / gradient-based | 5413 | 3676 | 5519 | 1786 | 9995 | 4191 | 20855 | 11235 | 9,925,249 | 4,984 |
| FedAvg | 5406 | 3687 | 5551 | 1804 | 10002 | 4196 | 20899 | 11240 | 9,909,678 | 4,984 |
| FedAvg, steps ∝ data | 5406 | 3687 | 5531 | 1804 | 10002 | 4196 | 20899 | 11240 | 9,909,678 | 4,984 |
| FedProx | 5407 | 3695 | 5575 | 1812 | 10005 | 4207 | 20888 | 11252 | 9,872,436 | 4,984 |
| FedNova | 5406 | 3735 | 5540 | 1822 | 10039 | 4245 | 20816 | 11306 | 9,899,187 | 4,984 |
| FedAvgM | 5414 | 3681 | 5531 | 1793 | 9994 | 4197 | 20825 | 11223 | 9,919,734 | 4,984 |
| FedAdam | 5428 | 3737 | 5544 | 1811 | 10106 | 4224 | 20826 | 11266 | 9,974,219 | 4,984 |
| FedYogi | 5427 | 3739 | 5534 | 1813 | 10178 | 4228 | 20835 | 11268 | 9,969,832 | 4,984 |
| SCAFFOLD | 5411 | 3678 | 5540 | 1787 | 9990 | 4195 | 20797 | 11227 | 19,740,616 | 4,984 |
| FedDyn | 5418 | 3678 | 5643 | 1888 | 9984 | 4196 | 20819 | 11230 | 9,929,867 | 4,984 |
| No Phase-2 sharing | 9712 | 5200 | 10167 | 3236 | 16764 | 5854 | 24457 | 12719 | 600 | 6 |
| Suff. stats, event-triggered (γ=0.5) | 5187 | 3563 | 5436 | 1716 | 9708 | 4111 | 20630 | 11150 | 84,029 | 71 |
| Personalised FL (λ=0.25) | 5522 | 3787 | 5638 | 1881 | 10145 | 4360 | 20760 | 11297 | 514,820 | 1,002 |
| Personalised FL (λ=0.5) | 5451 | 3722 | 5575 | 1823 | 10015 | 4255 | 20689 | 11244 | 510,604 | 1,002 |
