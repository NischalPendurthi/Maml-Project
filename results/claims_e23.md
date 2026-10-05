# E23: server vs serverless (relay) across diameters

N = 16, pooled Phase-1 size 960·(T/10⁴)^(2/3), γ = 0.5, Δ = (NT)^(-1/3), 20 paired trials (same seeds for server and relay), mean ± 95% CI. 'bound term' is N·D·N_bins, the additive term of Theorem 7 without constants.

| link | graph | D | spectral gap | server regret | relay regret | excess (paired) | excess % | bound term N·D·N_bins | server scalars | relay scalars |
|---|---|---|---|---|---|---|---|---|---|---|
| quadratic | complete | 1 | 1.000 | 6,911 ± 444 | 7,017 ± 442 | 106 ± 12 | +1.5% | 6,246 | 222,818 | 187,563 |
| quadratic | expander | 3 | 0.270 | 6,911 ± 444 | 7,149 ± 438 | 238 ± 16 | +3.4% | 18,739 | 222,818 | 184,347 |
| quadratic | hypercube | 4 | 0.400 | 6,911 ± 444 | 7,173 ± 443 | 262 ± 18 | +3.8% | 24,986 | 222,818 | 183,786 |
| quadratic | torus | 4 | 0.400 | 6,911 ± 444 | 7,185 ± 437 | 274 ± 22 | +4.0% | 24,986 | 222,818 | 186,342 |
| quadratic | ring | 8 | 0.051 | 6,911 ± 444 | 7,438 ± 441 | 527 ± 26 | +7.6% | 49,971 | 222,818 | 183,420 |
| quadratic | path | 15 | 0.013 | 6,911 ± 444 | 7,541 ± 438 | 630 ± 31 | +9.1% | 93,696 | 222,818 | 181,642 |
| zigzag | complete | 1 | 1.000 | 3,204 ± 146 | 3,271 ± 146 | 67 ± 4 | +2.1% | 6,184 | 463,436 | 381,433 |
| zigzag | expander | 3 | 0.270 | 3,204 ± 146 | 3,330 ± 145 | 126 ± 10 | +3.9% | 18,552 | 463,436 | 368,668 |
| zigzag | hypercube | 4 | 0.400 | 3,204 ± 146 | 3,343 ± 143 | 139 ± 10 | +4.3% | 24,736 | 463,436 | 369,834 |
| zigzag | torus | 4 | 0.400 | 3,204 ± 146 | 3,343 ± 143 | 139 ± 10 | +4.3% | 24,736 | 463,436 | 368,667 |
| zigzag | ring | 8 | 0.051 | 3,204 ± 146 | 3,458 ± 141 | 254 ± 12 | +7.9% | 49,472 | 463,436 | 363,198 |
| zigzag | path | 15 | 0.013 | 3,204 ± 146 | 3,508 ± 141 | 304 ± 13 | +9.5% | 92,760 | 463,436 | 353,864 |

## Excess vs horizon (quadratic)

| graph | N·T | excess | excess % |
|---|---|---|---|
| ring | 40,000 | 412 ± 25 | +11.3% |
| ring | 80,000 | 455 ± 36 | +9.1% |
| ring | 160,000 | 527 ± 26 | +7.6% |
| ring | 320,000 | 537 ± 38 | +5.5% |
| ring | 640,000 | 605 ± 36 | +4.5% |
| ring | fitted slope | 0.13 | (bound predicts 0.33) |
| path | 40,000 | 501 ± 33 | +13.8% |
| path | 80,000 | 546 ± 37 | +11.0% |
| path | 160,000 | 630 ± 31 | +9.1% |
| path | 320,000 | 680 ± 42 | +7.0% |
| path | 640,000 | 731 ± 35 | +5.4% |
| path | fitted slope | 0.14 | (bound predicts 0.33) |
