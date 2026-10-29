# E36: the shape of the delay term

N = 16, quadratic link, d = 10, σ = 0.1, 10 paired trials, mean ± 95% CI. Pooled Phase-1 size 960·(T/10⁴)^(2/3); Δ = (NT)^(-1/3). 'excess' is regret minus the server's (same seeds). '÷ NDK' and '÷ KF' divide the mean excess by N·D·K (the predicted shape for synchronised epochs) and by K·F with F the average farness (the predicted shape for the relays). A constant column means the prediction has the right shape.

| part | graph | D | F | T | K | protocol | regret | excess | ÷ NDK | ÷ KF | scalars |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | complete | 1 | 15 | 10,000 | 20 | flood relay (run in E23) | 6,964 ± 618 | 116 ± 12 | 0.36 | 0.39 | 180,657 |
| A | complete | 1 | 15 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 6,966 ± 615 | 118 ± 14 | 0.37 | 0.39 | 187,455 |
| A | complete | 1 | 15 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 6,822 ± 617 | -25 ± 6 | -0.08 | -0.08 | 1,376,906 |
| A | complete | 1 | 15 | 10,000 | 20 | synchronised epochs (proved) | 7,215 ± 612 | 368 ± 12 | 1.15 | 1.23 | 679,857 |
| A | expander | 3 | 29 | 10,000 | 20 | flood relay (run in E23) | 7,093 ± 614 | 245 ± 21 | 0.26 | 0.42 | 178,618 |
| A | expander | 3 | 29 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 7,096 ± 610 | 249 ± 28 | 0.26 | 0.42 | 185,662 |
| A | expander | 3 | 29 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 6,960 ± 610 | 112 ± 15 | 0.12 | 0.19 | 1,369,272 |
| A | expander | 3 | 29 | 10,000 | 20 | synchronised epochs (proved) | 7,881 ± 604 | 1,033 ± 68 | 1.08 | 1.77 | 549,447 |
| A | torus | 4 | 32 | 10,000 | 20 | flood relay (run in E23) | 7,131 ± 614 | 283 ± 22 | 0.22 | 0.44 | 176,659 |
| A | torus | 4 | 32 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 7,150 ± 616 | 302 ± 22 | 0.24 | 0.47 | 180,058 |
| A | torus | 4 | 32 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 6,994 ± 610 | 146 ± 15 | 0.11 | 0.23 | 1,376,736 |
| A | torus | 4 | 32 | 10,000 | 20 | synchronised epochs (proved) | 8,190 ± 589 | 1,342 ± 88 | 1.05 | 2.10 | 542,022 |
| A | ring | 8 | 64 | 10,000 | 20 | flood relay (run in E23) | 7,375 ± 615 | 528 ± 26 | 0.21 | 0.41 | 171,660 |
| A | ring | 8 | 64 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 7,385 ± 611 | 538 ± 29 | 0.21 | 0.42 | 179,388 |
| A | ring | 8 | 64 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 7,229 ± 614 | 381 ± 17 | 0.15 | 0.30 | 1,372,490 |
| A | ring | 8 | 64 | 10,000 | 20 | synchronised epochs (proved) | 9,233 ± 658 | 2,386 ± 101 | 0.93 | 1.86 | 461,209 |
| A | path | 15 | 85 | 10,000 | 20 | flood relay (run in E23) | 7,480 ± 612 | 633 ± 23 | 0.13 | 0.37 | 169,941 |
| A | path | 15 | 85 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 7,490 ± 613 | 643 ± 22 | 0.13 | 0.38 | 179,925 |
| A | path | 15 | 85 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 7,336 ± 616 | 488 ± 28 | 0.10 | 0.29 | 1,358,441 |
| A | path | 15 | 85 | 10,000 | 20 | synchronised epochs (proved) | 10,967 ± 618 | 4,120 ± 163 | 0.86 | 2.42 | 445,029 |
| B | ring | 8 | 64 | 2,500 | 20 | flood relay (run in E23) | 3,956 ± 540 | 399 ± 30 | 0.16 | 0.31 | 84,835 |
| B | ring | 8 | 64 | 5,000 | 20 | flood relay (run in E23) | 5,325 ± 668 | 457 ± 51 | 0.18 | 0.36 | 120,848 |
| B | ring | 8 | 64 | 10,000 | 20 | flood relay (run in E23) | 7,375 ± 615 | 528 ± 26 | 0.21 | 0.41 | 171,660 |
| B | ring | 8 | 64 | 20,000 | 20 | flood relay (run in E23) | 9,923 ± 1,019 | 531 ± 40 | 0.21 | 0.41 | 284,965 |
| C | ring | 8 | 64 | 10,000 | 5 | flood relay (run in E23) | 6,725 ± 787 | 233 ± 20 | 0.36 | 0.73 | 486,754 |
| C | ring | 8 | 64 | 10,000 | 10 | flood relay (run in E23) | 6,692 ± 855 | 364 ± 38 | 0.28 | 0.57 | 295,825 |
| C | ring | 8 | 64 | 10,000 | 20 | flood relay (run in E23) | 7,375 ± 615 | 528 ± 26 | 0.21 | 0.41 | 171,660 |
| C | ring | 8 | 64 | 10,000 | 40 | flood relay (run in E23) | 8,138 ± 1,021 | 627 ± 45 | 0.12 | 0.24 | 157,046 |
| B | ring | 8 | 64 | 2,500 | 20 | published-only relay, γ = 0.5 (proved) | 3,969 ± 533 | 413 ± 30 | 0.16 | 0.32 | 88,328 |
| B | ring | 8 | 64 | 5,000 | 20 | published-only relay, γ = 0.5 (proved) | 5,333 ± 664 | 465 ± 47 | 0.18 | 0.36 | 124,942 |
| B | ring | 8 | 64 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 7,385 ± 611 | 538 ± 29 | 0.21 | 0.42 | 179,388 |
| B | ring | 8 | 64 | 20,000 | 20 | published-only relay, γ = 0.5 (proved) | 9,937 ± 1,023 | 545 ± 37 | 0.21 | 0.43 | 300,746 |
| C | ring | 8 | 64 | 10,000 | 5 | published-only relay, γ = 0.5 (proved) | 6,729 ± 790 | 237 ± 19 | 0.37 | 0.74 | 494,544 |
| C | ring | 8 | 64 | 10,000 | 10 | published-only relay, γ = 0.5 (proved) | 6,693 ± 861 | 364 ± 40 | 0.28 | 0.57 | 301,856 |
| C | ring | 8 | 64 | 10,000 | 20 | published-only relay, γ = 0.5 (proved) | 7,385 ± 611 | 538 ± 29 | 0.21 | 0.42 | 179,388 |
| C | ring | 8 | 64 | 10,000 | 40 | published-only relay, γ = 0.5 (proved) | 8,246 ± 1,036 | 735 ± 60 | 0.14 | 0.29 | 155,118 |
| B | ring | 8 | 64 | 2,500 | 20 | published-only relay, γ = 1/(2N) (proved) | 3,864 ± 525 | 307 ± 28 | 0.12 | 0.24 | 516,460 |
| B | ring | 8 | 64 | 5,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 5,209 ± 662 | 340 ± 49 | 0.13 | 0.27 | 832,293 |
| B | ring | 8 | 64 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 7,229 ± 614 | 381 ± 17 | 0.15 | 0.30 | 1,372,490 |
| B | ring | 8 | 64 | 20,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 9,770 ± 1,028 | 378 ± 43 | 0.15 | 0.30 | 2,274,935 |
| C | ring | 8 | 64 | 10,000 | 5 | published-only relay, γ = 1/(2N) (proved) | 6,692 ± 786 | 200 ± 23 | 0.31 | 0.63 | 3,583,707 |
| C | ring | 8 | 64 | 10,000 | 10 | published-only relay, γ = 1/(2N) (proved) | 6,636 ± 856 | 307 ± 36 | 0.24 | 0.48 | 2,445,677 |
| C | ring | 8 | 64 | 10,000 | 20 | published-only relay, γ = 1/(2N) (proved) | 7,229 ± 614 | 381 ± 17 | 0.15 | 0.30 | 1,372,490 |
| C | ring | 8 | 64 | 10,000 | 40 | published-only relay, γ = 1/(2N) (proved) | 7,948 ± 1,024 | 437 ± 46 | 0.09 | 0.17 | 691,942 |
| B | ring | 8 | 64 | 2,500 | 20 | synchronised epochs (proved) | 5,631 ± 502 | 2,074 ± 83 | 0.81 | 1.62 | 189,484 |
| B | ring | 8 | 64 | 5,000 | 20 | synchronised epochs (proved) | 7,137 ± 682 | 2,269 ± 157 | 0.89 | 1.77 | 279,780 |
| B | ring | 8 | 64 | 10,000 | 20 | synchronised epochs (proved) | 9,233 ± 658 | 2,386 ± 101 | 0.93 | 1.86 | 461,209 |
| B | ring | 8 | 64 | 20,000 | 20 | synchronised epochs (proved) | 11,919 ± 1,011 | 2,528 ± 82 | 0.99 | 1.97 | 890,512 |
| C | ring | 8 | 64 | 10,000 | 5 | synchronised epochs (proved) | 7,748 ± 787 | 1,256 ± 62 | 1.96 | 3.92 | 1,665,460 |
| C | ring | 8 | 64 | 10,000 | 10 | synchronised epochs (proved) | 8,132 ± 845 | 1,804 ± 73 | 1.41 | 2.82 | 866,028 |
| C | ring | 8 | 64 | 10,000 | 20 | synchronised epochs (proved) | 9,233 ± 658 | 2,386 ± 101 | 0.93 | 1.86 | 461,209 |
| C | ring | 8 | 64 | 10,000 | 40 | synchronised epochs (proved) | 10,671 ± 1,044 | 3,160 ± 82 | 0.62 | 1.23 | 400,602 |
