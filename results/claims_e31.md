# E31: synchronised epochs (proved) vs flood relay (run)

N = 16, T = 10,000, pooled Phase-1 size 960, γ = 0.5, Δ = (NT)^(-1/3), 20 paired trials (same seeds as E23), mean ± 95% CI. Server: regret 6,911 ± 444 (quadratic), 3,204 ± 146 (zigzag), scalars 222,818. 'syncs' counts epochs for the epoch protocols and update rounds for the flood relay. 'Lemma 22' is the bound 1 + N_b(1 + log_{1+γ} NT) on the number of epochs; 'Thm 17 delay' is N_b·N·(γ + 4D), the delay term without constants, and 'Thm 18 delay' N_b·N·√(γ + 4D), the sharper one (Theorem 18) without constants. Scalars use flood.py's accounting (one delivery per receiving agent).

| link | graph | D | protocol | regret | excess over server | excess % | scalars | syncs | Lemma 22 | Thm 17 delay | Thm 18 delay |
|---|---|---|---|---|---|---|---|---|---|---|---|
| quadratic | complete | 1 | flood relay (code, E23) | 7,017 ± 442 | 106 ± 12 | +1.5% | 187,563 | 142 | – | – | – |
| quadratic | complete | 1 | synchronised epochs (proved) | 7,264 ± 437 | 353 ± 17 | +5.1% | 725,227 | 93 | 11,929 | 28,109 | 13,251 |
| quadratic | complete | 1 | epochs, pipelined (not proved) | 7,055 ± 435 | 143 ± 18 | +2.1% | 789,853 | 128 | – | – | – |
| quadratic | expander | 3 | flood relay (code, E23) | 7,149 ± 438 | 238 ± 16 | +3.4% | 184,347 | 278 | – | – | – |
| quadratic | expander | 3 | synchronised epochs (proved) | 7,941 ± 435 | 1,030 ± 37 | +14.9% | 617,650 | 56 | 11,929 | 78,080 | 22,084 |
| quadratic | expander | 3 | epochs, pipelined (not proved) | 7,529 ± 438 | 618 ± 30 | +8.9% | 759,056 | 232 | – | – | – |
| quadratic | hypercube | 4 | flood relay (code, E23) | 7,173 ± 443 | 262 ± 18 | +3.8% | 183,786 | 332 | – | – | – |
| quadratic | hypercube | 4 | synchronised epochs (proved) | 8,230 ± 432 | 1,319 ± 56 | +19.1% | 621,422 | 49 | 11,929 | 103,066 | 25,373 |
| quadratic | hypercube | 4 | epochs, pipelined (not proved) | 7,747 ± 429 | 835 ± 34 | +12.1% | 743,382 | 274 | – | – | – |
| quadratic | torus | 4 | flood relay (code, E23) | 7,185 ± 437 | 274 ± 22 | +4.0% | 186,342 | 337 | – | – | – |
| quadratic | torus | 4 | synchronised epochs (proved) | 8,230 ± 432 | 1,319 ± 56 | +19.1% | 621,422 | 49 | 11,929 | 103,066 | 25,373 |
| quadratic | torus | 4 | epochs, pipelined (not proved) | 7,747 ± 429 | 835 ± 34 | +12.1% | 743,382 | 274 | – | – | – |
| quadratic | ring | 8 | flood relay (code, E23) | 7,438 ± 441 | 527 ± 26 | +7.6% | 183,420 | 509 | – | – | – |
| quadratic | ring | 8 | synchronised epochs (proved) | 9,295 ± 454 | 2,384 ± 67 | +34.5% | 541,057 | 35 | 11,929 | 203,008 | 35,610 |
| quadratic | ring | 8 | epochs, pipelined (not proved) | 8,565 ± 457 | 1,654 ± 64 | +23.9% | 777,830 | 395 | – | – | – |
| quadratic | path | 15 | flood relay (code, E23) | 7,541 ± 438 | 630 ± 31 | +9.1% | 181,642 | 629 | – | – | – |
| quadratic | path | 15 | synchronised epochs (proved) | 11,019 ± 439 | 4,107 ± 135 | +59.4% | 511,255 | 25 | 11,929 | 377,907 | 48,586 |
| quadratic | path | 15 | epochs, pipelined (not proved) | 9,698 ± 419 | 2,786 ± 55 | +40.3% | 827,468 | 551 | – | – | – |
| zigzag | complete | 1 | flood relay (code, E23) | 3,271 ± 146 | 67 ± 4 | +2.1% | 381,433 | 180 | – | – | – |
| zigzag | complete | 1 | synchronised epochs (proved) | 3,365 ± 142 | 161 ± 10 | +5.0% | 1,383,921 | 117 | 11,810 | 27,828 | 13,118 |
| zigzag | complete | 1 | epochs, pipelined (not proved) | 3,275 ± 144 | 71 ± 7 | +2.2% | 1,516,058 | 160 | – | – | – |
| zigzag | expander | 3 | flood relay (code, E23) | 3,330 ± 145 | 126 ± 10 | +3.9% | 368,668 | 357 | – | – | – |
| zigzag | expander | 3 | synchronised epochs (proved) | 3,682 ± 141 | 478 ± 16 | +14.9% | 1,233,733 | 71 | 11,810 | 77,300 | 21,864 |
| zigzag | expander | 3 | epochs, pipelined (not proved) | 3,496 ± 144 | 292 ± 9 | +9.1% | 1,395,848 | 295 | – | – | – |
| zigzag | hypercube | 4 | flood relay (code, E23) | 3,343 ± 143 | 139 ± 10 | +4.3% | 369,834 | 430 | – | – | – |
| zigzag | hypercube | 4 | synchronised epochs (proved) | 3,817 ± 140 | 613 ± 13 | +19.1% | 1,205,499 | 61 | 11,810 | 102,036 | 25,120 |
| zigzag | hypercube | 4 | epochs, pipelined (not proved) | 3,594 ± 142 | 389 ± 13 | +12.2% | 1,405,596 | 346 | – | – | – |
| zigzag | torus | 4 | flood relay (code, E23) | 3,343 ± 143 | 139 ± 10 | +4.3% | 368,667 | 428 | – | – | – |
| zigzag | torus | 4 | synchronised epochs (proved) | 3,817 ± 140 | 613 ± 13 | +19.1% | 1,205,499 | 61 | 11,810 | 102,036 | 25,120 |
| zigzag | torus | 4 | epochs, pipelined (not proved) | 3,594 ± 142 | 389 ± 13 | +12.2% | 1,405,596 | 346 | – | – | – |
| zigzag | ring | 8 | flood relay (code, E23) | 3,458 ± 141 | 254 ± 12 | +7.9% | 363,198 | 655 | – | – | – |
| zigzag | ring | 8 | synchronised epochs (proved) | 4,304 ± 144 | 1,100 ± 18 | +34.3% | 1,068,323 | 42 | 11,810 | 200,980 | 35,254 |
| zigzag | ring | 8 | epochs, pipelined (not proved) | 3,950 ± 138 | 746 ± 18 | +23.3% | 1,343,684 | 487 | – | – | – |
| zigzag | path | 15 | flood relay (code, E23) | 3,508 ± 141 | 304 ± 13 | +9.5% | 353,864 | 800 | – | – | – |
| zigzag | path | 15 | synchronised epochs (proved) | 5,002 ± 146 | 1,797 ± 41 | +56.1% | 1,031,996 | 32 | 11,810 | 374,132 | 48,100 |
| zigzag | path | 15 | epochs, pipelined (not proved) | 4,471 ± 142 | 1,267 ± 22 | +39.5% | 1,384,281 | 677 | – | – | – |

## Growth of the excess with the diameter (log-log slope over the graphs)

| link | protocol | slope in D |
|---|---|---|
| quadratic | flood relay (code, E23) | 0.69 |
| quadratic | synchronised epochs (proved) | 0.90 |
| quadratic | epochs, pipelined (not proved) | 1.09 |
| quadratic | Thm 17 shape N·(γ+4D) | 0.96 |
| quadratic | Thm 18 shape N·√(γ+4D) | 0.48 |
| zigzag | flood relay (code, E23) | 0.59 |
| zigzag | synchronised epochs (proved) | 0.89 |
| zigzag | epochs, pipelined (not proved) | 1.06 |
| zigzag | Thm 17 shape N·(γ+4D) | 0.96 |
| zigzag | Thm 18 shape N·√(γ+4D) | 0.48 |

## Part B: trigger threshold under flooding (quadratic)

| graph | protocol | γ | N·γ | regret | ÷ γ = 0.5 | √(1+Nγ) | scalars | syncs |
|---|---|---|---|---|---|---|---|---|
| torus | flood relay (code, E23) | 0.0625 | 1 | 7,062 ± 440 | 0.983 | 1.41 | 854,620 | 1,785 |
| torus | flood relay (code, E23) | 0.5 | 8 | 7,185 ± 437 | 1.000 | 3.00 | 186,342 | 337 |
| torus | flood relay (code, E23) | 2 | 32 | 21,846 ± 1,333 | 3.040 | 5.74 | 117,896 | 42 |
| torus | synchronised epochs (proved) | 0.0625 | 1 | 8,200 ± 436 | 0.996 | 1.41 | 3,020,371 | 280 |
| torus | synchronised epochs (proved) | 0.5 | 8 | 8,230 ± 432 | 1.000 | 3.00 | 621,422 | 49 |
| torus | synchronised epochs (proved) | 2 | 32 | 18,226 ± 716 | 2.215 | 5.74 | 258,032 | 3 |
| ring | flood relay (code, E23) | 0.0625 | 1 | 7,308 ± 446 | 0.982 | 1.41 | 846,386 | 2,797 |
| ring | flood relay (code, E23) | 0.5 | 8 | 7,438 ± 441 | 1.000 | 3.00 | 183,420 | 509 |
| ring | flood relay (code, E23) | 2 | 32 | 22,091 ± 1,394 | 2.970 | 5.74 | 119,523 | 78 |
| ring | synchronised epochs (proved) | 0.0625 | 1 | 9,258 ± 457 | 0.996 | 1.41 | 2,810,760 | 206 |
| ring | synchronised epochs (proved) | 0.5 | 8 | 9,295 ± 454 | 1.000 | 3.00 | 541,057 | 35 |
| ring | synchronised epochs (proved) | 2 | 32 | 18,843 ± 747 | 2.027 | 5.74 | 262,680 | 3 |
