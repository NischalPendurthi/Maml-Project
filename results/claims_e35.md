# E35: private Phase 1

N = 16, ring, T = 10,000, quadratic link, d = 10, δ_p = 1e-05, 10 paired trials, mean ± 95% CI. Each agent adds N(0, σ_p² I) to its truncated Stein sum once, σ_p = 2τ√d·√(2 log(1.25/δ_p))/ε; Phase 2 is unchanged. All rows, including ε = ∞, use the data-free window W = X_max of the proofs, so Phase-1 contexts are not used elsewhere. κ is the theorem's factor. '÷ base' is relative to no privacy at T0 = 60.

| privacy | κ (theory) | T0 | network regret | ÷ base |
|---|---|---|---|---|
| no privacy (ε = ∞) | 0 | 60 | 9,319 ± 559 | 1.00 |
| no privacy (ε = ∞) | 0 | 240 | 12,872 ± 183 | 1.38 |
| no privacy (ε = ∞) | 0 | 960 | 35,105 ± 254 | 3.77 |
| ε = 128 | 1 | 60 | 114,938 ± 33,891 | 12.33 |
| ε = 128 | 1 | 240 | 81,537 ± 17,156 | 8.75 |
| ε = 128 | 1 | 960 | 50,100 ± 6,518 | 5.38 |
| ε = 32 | 3 | 60 | 197,429 ± 32,088 | 21.18 |
| ε = 32 | 3 | 240 | 221,482 ± 43,101 | 23.77 |
| ε = 32 | 3 | 960 | 123,922 ± 28,909 | 13.30 |
| ε = 8 | 13 | 60 | 227,665 ± 32,651 | 24.43 |
| ε = 8 | 13 | 240 | 242,429 ± 28,670 | 26.01 |
| ε = 8 | 13 | 960 | 193,069 ± 31,870 | 20.72 |
| ε = 2 | 53 | 60 | 236,220 ± 35,190 | 25.35 |
| ε = 2 | 53 | 240 | 242,699 ± 29,731 | 26.04 |
| ε = 2 | 53 | 960 | 214,108 ± 30,839 | 22.97 |
