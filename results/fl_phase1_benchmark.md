# E10 · FL methods for Phase 1 (θ pooling)

N = 8 agents, d = 10, K = 20.  Part A: offline, 100 rounds of uniform pulls, 16 reps.  Part B: bandit, T = 10,000, 8 trials.

## A · optimisation error ‖w_R − w*‖/‖w*‖ after R rounds (tuned), Stein objective

| method | family | tuned | scalars/round | iid R=1 | iid R=10 | participation R=1 | participation R=10 | covariate R=1 | covariate R=10 | concept R=1 | concept R=10 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sufficient statistics (exact) | exact | `{}` | 168 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 |
| Split learning | exact | `{}` | 8080 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 |
| One-shot FedAvg | averaging | `{}` | 168 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 |
| Fed. distillation | averaging | `{}` | 240 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 | 1.0e-09 |
| FedSGD / gradient-based | gradient | `{'lr_scale': 1.0}` | 160 | 1.2e-16 | 1.1e-16 | 1.6e-16 | 1.2e-16 | 1.5e-16 | 1.4e-16 | 1.4e-16 | 1.2e-16 |
| FedAvg | averaging | `{'local_steps': 1, 'lr_scale': 1.0}` | 160 | 1.2e-16 | 1.3e-16 | 1.6e-16 | 1.5e-16 | 1.5e-16 | 1.5e-16 | 1.4e-16 | 1.3e-16 |
| FedAvg, steps ∝ data | averaging | `{'local_steps': 20, 'lr_scale': 1.0}` | 160 | 1.2e-16 | 1.2e-16 | 1.5e-16 | 1.5e-16 | 1.5e-16 | 1.5e-16 | 1.4e-16 | 1.4e-16 |
| FedProx | averaging | `{'local_steps': 5, 'mu_rel': 0.01}` | 160 | 9.9e-03 | 1.3e-16 | 9.9e-03 | 1.3e-16 | 9.9e-03 | 1.6e-16 | 9.9e-03 | 1.3e-16 |
| FedNova | drift correction | `{'local_steps': 20, 'lr_scale': 0.3}` | 168 | 8.0e-04 | 1.1e-16 | 1.7e-01 | 9.1e-02 | 8.0e-04 | 1.4e-16 | 8.0e-04 | 1.2e-16 |
| FedAvgM | server optimiser | `{'local_steps': 5, 'server_lr': 0.3, 'beta': 0.5}` | 160 | 7.0e-01 | 1.8e-02 | 7.0e-01 | 1.8e-02 | 7.0e-01 | 1.8e-02 | 7.0e-01 | 1.8e-02 |
| FedAdam | server optimiser | `{'local_steps': 1, 'server_lr': 0.03}` | 160 | 9.0e-01 | 3.4e-01 | 9.0e-01 | 3.3e-01 | 9.1e-01 | 3.2e-01 | 9.0e-01 | 3.4e-01 |
| FedYogi | server optimiser | `{'local_steps': 1, 'server_lr': 0.03}` | 160 | 9.0e-01 | 3.3e-01 | 9.0e-01 | 3.3e-01 | 9.1e-01 | 3.2e-01 | 9.0e-01 | 3.3e-01 |
| SCAFFOLD | drift correction | `{'local_steps': 5, 'lr_scale': 1.0}` | 320 | 1.2e-16 | 1.1e-16 | 1.6e-16 | 1.2e-16 | 1.5e-16 | 1.3e-16 | 1.4e-16 | 1.2e-16 |
| FedDyn | drift correction | `{'local_steps': 5, 'alpha_rel': 1.0}` | 160 | 1.2e-16 | 1.3e-16 | 2.9e-01 | 2.2e-03 | 1.5e-16 | 1.6e-16 | 1.4e-16 | 1.7e-16 |

## A · same, LS objective (heterogeneous Hessians)

| method | tuned | iid R=1 | iid R=10 | participation R=1 | participation R=10 | covariate R=1 | covariate R=10 | concept R=1 | concept R=10 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Sufficient statistics (exact) | `{}` | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 |
| Split learning | `{}` | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 | 1.0e-16 |
| One-shot FedAvg | `{}` | 3.6e-02 | 3.6e-02 | 5.9e-02 | 5.9e-02 | 1.2e-01 | 1.2e-01 | 6.4e-02 | 6.4e-02 |
| Fed. distillation | `{}` | 3.6e-02 | 3.6e-02 | 5.9e-02 | 5.9e-02 | 1.2e-01 | 1.2e-01 | 6.4e-02 | 6.4e-02 |
| FedSGD / gradient-based | `{'lr_scale': 1.0}` | 1.7e-01 | 1.5e-06 | 2.2e-01 | 1.5e-05 | 1.7e-01 | 1.4e-06 | 1.7e-01 | 1.5e-06 |
| FedAvg | `{'local_steps': 1, 'lr_scale': 1.0}` | 4.4e-01 | 6.8e-04 | 5.8e-01 | 7.4e-03 | 4.4e-01 | 6.7e-04 | 4.4e-01 | 6.6e-04 |
| FedAvg, steps ∝ data | `{'local_steps': 1, 'lr_scale': 1.0}` | 4.4e-01 | 6.8e-04 | 5.1e-01 | 2.7e-02 | 4.4e-01 | 6.7e-04 | 4.4e-01 | 6.6e-04 |
| FedProx | `{'local_steps': 5, 'mu_rel': 1.0}` | 6.5e-01 | 1.8e-02 | 7.2e-01 | 4.4e-02 | 6.5e-01 | 4.6e-02 | 6.5e-01 | 2.8e-02 |
| FedNova | `{'local_steps': 5, 'lr_scale': 0.3}` | 4.1e-01 | 1.1e-02 | 4.6e-01 | 2.0e-02 | 4.2e-01 | 4.1e-02 | 4.1e-01 | 2.2e-02 |
| FedAvgM | `{'local_steps': 1, 'server_lr': 1.0, 'beta': 0.5}` | 4.4e-01 | 2.1e-02 | 5.8e-01 | 2.2e-02 | 4.4e-01 | 2.1e-02 | 4.4e-01 | 2.1e-02 |
| FedAdam | `{'local_steps': 5, 'server_lr': 0.03}` | 9.0e-01 | 3.4e-01 | 9.0e-01 | 3.4e-01 | 9.0e-01 | 3.3e-01 | 9.0e-01 | 3.4e-01 |
| FedYogi | `{'local_steps': 5, 'server_lr': 0.03}` | 9.0e-01 | 3.3e-01 | 9.0e-01 | 3.3e-01 | 9.0e-01 | 3.3e-01 | 9.0e-01 | 3.3e-01 |
| SCAFFOLD | `{'local_steps': 5, 'lr_scale': 0.3}` | 4.1e-01 | 1.1e-04 | 5.3e-01 | 1.7e-03 | 4.2e-01 | 1.1e-04 | 4.1e-01 | 1.2e-04 |
| FedDyn | `{'local_steps': 5, 'alpha_rel': 1.0}` | 3.0e-01 | 5.4e-03 | 5.0e-01 | 2.9e-02 | 3.0e-01 | 5.4e-03 | 3.0e-01 | 5.3e-03 |

## A · statistical error mean_i ‖θ̂ − θ*_i‖₁

| estimator | iid | participation | covariate | concept |
|---|---:|---:|---:|---:|
| pooled (stein) | 0.136 | 0.181 | 0.196 | 0.449 |
| each agent alone (stein) | 0.359 | 0.491 | 0.507 | 0.373 |
| pooled (ls) | 0.097 | 0.117 | 0.175 | 0.437 |
| each agent alone (ls) | 0.262 | 0.380 | 0.450 | 0.273 |
| personalised λ=0.0 (stein) | 0.359 | 0.491 | 0.507 | 0.373 |
| personalised λ=0.1 (stein) | 0.226 | 0.279 | 0.342 | 0.318 |
| personalised λ=0.25 (stein) | 0.166 | 0.211 | 0.231 | 0.356 |
| personalised λ=0.5 (stein) | 0.142 | 0.186 | 0.204 | 0.405 |
| personalised λ=1.0 (stein) | 0.136 | 0.181 | 0.196 | 0.449 |

## B · bandit network regret (mean over trials)

| config | iid · quadratic | iid · zigzag | participation · quadratic | participation · zigzag | covariate · quadratic | covariate · zigzag | concept · quadratic | concept · zigzag | Phase-1 scalars (iid·quad) | θ err (iid·quad) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N × ZoomSIB-UCB (no comm.) | 17270 | 7139 | 14447 | 5978 | 28656 | 12914 | 16359 | 7287 | 0 | 0.289 |
| Sufficient statistics (exact) | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 1,020 | 0.209 |
| Split learning | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 4,708 | 0.209 |
| One-shot FedAvg | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 1,020 | 0.209 |
| Fed. distillation | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 1,398 | 0.209 |
| FedSGD / gradient-based | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 8,538 | 0.209 |
| FedAvg | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 8,538 | 0.209 |
| FedAvg, steps ∝ data | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 8,538 | 0.209 |
| FedProx | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 8,538 | 0.209 |
| FedNova | 5155 | 3551 | 6076 | 1885 | 9710 | 4107 | 20639 | 11139 | 8,958 | 0.209 |
| FedAvgM | 5153 | 3568 | 5389 | 1709 | 12968 | 4107 | 20681 | 11147 | 8,538 | 0.209 |
| FedAdam | 4770 | 2220 | 5865 | 1664 | 13650 | 3228 | 19092 | 10466 | 12,759 | 0.136 |
| FedYogi | 4973 | 2205 | 3997 | 1700 | 11668 | 3306 | 18514 | 10378 | 12,960 | 0.145 |
| SCAFFOLD | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 | 16,938 | 0.209 |
| FedDyn | 5155 | 3551 | 5394 | 1706 | 9710 | 4107 | 20639 | 11139 | 8,538 | 0.209 |
| Sufficient statistics (exact) [ls] | 5577 | 960 | 3646 | 737 | 9195 | 3673 | 18692 | 10515 | 2,148 | 0.234 |
| FedAvg [ls] | 5427 | 1034 | 3466 | 755 | 9382 | 4528 | 18781 | 9907 | 5,121 | 0.222 |
| SCAFFOLD [ls] | 5226 | 971 | 3489 | 782 | 9194 | 4191 | 18699 | 10060 | 11,725 | 0.215 |
| FedDyn [ls] | 5436 | 1047 | 3482 | 993 | 9375 | 4517 | 19632 | 9914 | 5,121 | 0.223 |
