# E22: one agent at horizon N·T vs N agents at horizon T

Total budget N·T = 160,000 pulls, pooled Phase-1 size 960, Δ = (NT)^(-1/3), 20 paired trials, mean ± 95% CI. Ratio = regret ÷ single agent. 'sync rounds' = Phase-2 communication rounds.

| link | N | configuration | network regret | ratio to single | sync rounds |
|---|---|---|---|---|---|
| quadratic | 1 | single agent | 6,297 ± 607 | 1.000 | – |
| quadratic | 2 | N agents, sync every round | 6,517 ± 482 | 1.035 | 79,520 |
| quadratic | 2 | N agents, event-triggered (γ=0.5) | 6,522 ± 482 | 1.036 | 346 |
| quadratic | 2 | N independent agents | 16,230 ± 2,114 | 2.577 | – |
| quadratic | 4 | N agents, sync every round | 6,879 ± 621 | 1.092 | 39,760 |
| quadratic | 4 | N agents, event-triggered (γ=0.5) | 6,896 ± 620 | 1.095 | 243 |
| quadratic | 4 | N independent agents | 17,984 ± 1,755 | 2.856 | – |
| quadratic | 8 | N agents, sync every round | 6,391 ± 604 | 1.015 | 19,880 |
| quadratic | 8 | N agents, event-triggered (γ=0.5) | 6,415 ± 603 | 1.019 | 167 |
| quadratic | 8 | N independent agents | 23,755 ± 1,463 | 3.772 | – |
| quadratic | 16 | N agents, sync every round | 6,883 ± 445 | 1.093 | 9,940 |
| quadratic | 16 | N agents, event-triggered (γ=0.5) | 6,911 ± 444 | 1.098 | 128 |
| quadratic | 16 | N independent agents | 32,347 ± 798 | 5.137 | – |
| zigzag | 1 | single agent | 3,060 ± 161 | 1.000 | – |
| zigzag | 2 | N agents, sync every round | 3,030 ± 194 | 0.990 | 79,520 |
| zigzag | 2 | N agents, event-triggered (γ=0.5) | 3,033 ± 194 | 0.991 | 417 |
| zigzag | 2 | N independent agents | 7,133 ± 1,089 | 2.331 | – |
| zigzag | 4 | N agents, sync every round | 3,123 ± 235 | 1.021 | 39,760 |
| zigzag | 4 | N agents, event-triggered (γ=0.5) | 3,130 ± 233 | 1.023 | 296 |
| zigzag | 4 | N independent agents | 8,574 ± 954 | 2.802 | – |
| zigzag | 8 | N agents, sync every round | 3,077 ± 165 | 1.005 | 19,880 |
| zigzag | 8 | N agents, event-triggered (γ=0.5) | 3,088 ± 164 | 1.009 | 208 |
| zigzag | 8 | N independent agents | 9,947 ± 541 | 3.251 | – |
| zigzag | 16 | N agents, sync every round | 3,192 ± 146 | 1.043 | 9,940 |
| zigzag | 16 | N agents, event-triggered (γ=0.5) | 3,204 ± 146 | 1.047 | 162 |
| zigzag | 16 | N independent agents | 14,113 ± 312 | 4.612 | – |

## Sync rounds vs horizon (N = 8, event-triggered, γ = 0.5)

| N·T | N_bins | measured syncs | Thm 12 bound | per-round sync | max syncs by one bin | per-bin bound |
|---|---|---|---|---|---|---|
| 10,000 | 153 | 61.0 | 3,625 | 1,130 | 2.9 | 23.7 |
| 20,000 | 192 | 78.5 | 4,893 | 2,380 | 3.0 | 25.4 |
| 40,000 | 242 | 102.5 | 6,577 | 4,880 | 3.1 | 27.1 |
| 80,000 | 305 | 130.2 | 8,806 | 9,880 | 3.2 | 28.8 |
| 160,000 | 384 | 166.9 | 11,748 | 19,880 | 3.2 | 30.6 |
| 320,000 | 484 | 212.8 | 15,627 | 39,880 | 3.2 | 32.3 |
