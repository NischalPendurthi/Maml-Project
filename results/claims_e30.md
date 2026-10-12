# E30: constant γ vs γ = γ0/N

Fixed budget N·T = 160,000, pooled Phase-1 size 960, Δ = (NT)^(-1/3), 20 paired trials, mean ± 95% CI. The bound's UCB term scales with sqrt(1 + N·γ).

| link | N | configuration | γ | N·γ | network regret | ÷ sync1 | sync rounds |
|---|---|---|---|---|---|---|---|
| quadratic | 2 | sync every round | – | – | 6,517 ± 482 | 1.000 | 79,520 |
| quadratic | 2 | event, γ = 0.5 | 0.5 | 1 | 6,522 ± 482 | 1.001 | 346 |
| quadratic | 2 | event, γ = 2 | 2 | 4 | 7,295 ± 485 | 1.119 | 10 |
| quadratic | 2 | event, γ = 4/N | 2 | 4 | 7,295 ± 485 | 1.119 | 10 |
| quadratic | 4 | sync every round | – | – | 6,879 ± 621 | 1.000 | 39,760 |
| quadratic | 4 | event, γ = 0.5 | 0.5 | 2 | 6,896 ± 620 | 1.003 | 243 |
| quadratic | 4 | event, γ = 2 | 2 | 8 | 9,208 ± 648 | 1.339 | 6 |
| quadratic | 4 | event, γ = 4/N | 1 | 4 | 8,206 ± 627 | 1.193 | 13 |
| quadratic | 8 | sync every round | – | – | 6,391 ± 604 | 1.000 | 19,880 |
| quadratic | 8 | event, γ = 0.5 | 0.5 | 4 | 6,415 ± 603 | 1.004 | 167 |
| quadratic | 8 | event, γ = 2 | 2 | 16 | 11,507 ± 818 | 1.801 | 4 |
| quadratic | 8 | event, γ = 4/N | 0.5 | 4 | 6,415 ± 603 | 1.004 | 167 |
| quadratic | 16 | sync every round | – | – | 6,883 ± 445 | 1.000 | 9,940 |
| quadratic | 16 | event, γ = 0.5 | 0.5 | 8 | 6,911 ± 444 | 1.004 | 128 |
| quadratic | 16 | event, γ = 2 | 2 | 32 | 17,503 ± 687 | 2.543 | 3 |
| quadratic | 16 | event, γ = 4/N | 0.25 | 4 | 6,894 ± 445 | 1.002 | 191 |
| zigzag | 2 | sync every round | – | – | 3,030 ± 194 | 1.000 | 79,520 |
| zigzag | 2 | event, γ = 0.5 | 0.5 | 1 | 3,033 ± 194 | 1.001 | 417 |
| zigzag | 2 | event, γ = 2 | 2 | 4 | 3,373 ± 193 | 1.113 | 10 |
| zigzag | 2 | event, γ = 4/N | 2 | 4 | 3,373 ± 193 | 1.113 | 10 |
| zigzag | 4 | sync every round | – | – | 3,123 ± 235 | 1.000 | 39,760 |
| zigzag | 4 | event, γ = 0.5 | 0.5 | 2 | 3,130 ± 233 | 1.002 | 296 |
| zigzag | 4 | event, γ = 2 | 2 | 8 | 4,132 ± 243 | 1.323 | 7 |
| zigzag | 4 | event, γ = 4/N | 1 | 4 | 3,825 ± 239 | 1.225 | 17 |
| zigzag | 8 | sync every round | – | – | 3,077 ± 165 | 1.000 | 19,880 |
| zigzag | 8 | event, γ = 0.5 | 0.5 | 4 | 3,088 ± 164 | 1.004 | 208 |
| zigzag | 8 | event, γ = 2 | 2 | 16 | 5,314 ± 180 | 1.727 | 5 |
| zigzag | 8 | event, γ = 4/N | 0.5 | 4 | 3,088 ± 164 | 1.004 | 208 |
| zigzag | 16 | sync every round | – | – | 3,192 ± 146 | 1.000 | 9,940 |
| zigzag | 16 | event, γ = 0.5 | 0.5 | 8 | 3,204 ± 146 | 1.004 | 162 |
| zigzag | 16 | event, γ = 2 | 2 | 32 | 7,980 ± 170 | 2.500 | 4 |
| zigzag | 16 | event, γ = 4/N | 0.25 | 4 | 3,195 ± 146 | 1.001 | 291 |
