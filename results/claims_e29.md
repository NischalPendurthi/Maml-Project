# E29: can heterogeneous agents identify θ* only together?

Quadratic link, agent i's index ~ N(c_i, 1), so μ_i = 2(1 − c_i). d = 10, K = 20, T = 10,000, pooled Phase-1 size 960 (fixed), event Phase 2 (γ = 0.5). '÷ random' = regret divided by uniform random play on the same instances (1 = learned nothing).

| question | evidence | verdict |
|---|---|---|
| Idea alive: pooled sums degrade at moderate imbalance (G ≥ 4) and sign-invariant pooling beats every agent going alone | 11/11 such cells | YES |
| Simple fix suffices: aligned within 5% of outer in every cell | worst aligned ÷ outer = 0.994 | YES |
| Second-order alone suffices: each agent alone with 2nd-order within 10% of the best network method | worst indep 2nd-order ÷ best network = 22.32 | NO |

## Part A: one agent (50 trials per point)

| method | c | μ | sin-angle error | P(err < 0.3) | P(err < 0.5) | regret ÷ random | T0 used |
|---|---|---|---|---|---|---|---|
| 1st-order ZoomSIB, fixed T0 | -1 | +4.0 | 0.131 | 50/50 | 50/50 | 0.13 | 960 |
| 1st-order ZoomSIB, fixed T0 | 0 | +2.0 | 0.119 | 50/50 | 50/50 | 0.15 | 960 |
| 1st-order ZoomSIB, fixed T0 | 0.5 | +1.0 | 0.162 | 50/50 | 50/50 | 0.19 | 960 |
| 1st-order ZoomSIB, fixed T0 | 0.75 | +0.5 | 0.289 | 33/50 | 49/50 | 0.26 | 960 |
| 1st-order ZoomSIB, fixed T0 | 0.9 | +0.2 | 0.613 | 1/50 | 11/50 | 0.54 | 960 |
| 1st-order ZoomSIB, fixed T0 | 1 | +0.0 | 0.873 | 0/50 | 0/50 | 0.86 | 960 |
| 1st-order ZoomSIB, fixed T0 | 1.1 | -0.2 | 0.532 | 2/50 | 24/50 | 0.46 | 960 |
| 1st-order ZoomSIB, fixed T0 | 1.25 | -0.5 | 0.268 | 35/50 | 50/50 | 0.25 | 960 |
| 1st-order ZoomSIB, fixed T0 | 1.5 | -1.0 | 0.166 | 50/50 | 50/50 | 0.19 | 960 |
| 1st-order ZoomSIB, fixed T0 | 2 | -2.0 | 0.130 | 50/50 | 50/50 | 0.15 | 960 |
| 1st-order ZoomSIB, fixed T0 | 3 | -4.0 | 0.144 | 50/50 | 50/50 | 0.13 | 960 |
| 1st-order ZoomSIB, adaptive stop | -1 | +4.0 | 0.217 | 40/50 | 49/50 | 0.08 | 426 |
| 1st-order ZoomSIB, adaptive stop | 0 | +2.0 | 0.238 | 38/50 | 50/50 | 0.11 | 346 |
| 1st-order ZoomSIB, adaptive stop | 0.5 | +1.0 | 0.223 | 40/50 | 50/50 | 0.18 | 688 |
| 1st-order ZoomSIB, adaptive stop | 0.75 | +0.5 | 0.230 | 41/50 | 50/50 | 0.34 | 2046 |
| 1st-order ZoomSIB, adaptive stop | 0.9 | +0.2 | 0.322 | 25/50 | 47/50 | 0.60 | 4422 |
| 1st-order ZoomSIB, adaptive stop | 1 | +0.0 | 0.769 | 0/50 | 7/50 | 0.85 | 4645 |
| 1st-order ZoomSIB, adaptive stop | 1.1 | -0.2 | 0.335 | 18/50 | 46/50 | 0.58 | 4241 |
| 1st-order ZoomSIB, adaptive stop | 1.25 | -0.5 | 0.244 | 36/50 | 49/50 | 0.28 | 1390 |
| 1st-order ZoomSIB, adaptive stop | 1.5 | -1.0 | 0.278 | 31/50 | 48/50 | 0.19 | 469 |
| 1st-order ZoomSIB, adaptive stop | 2 | -2.0 | 0.257 | 35/50 | 50/50 | 0.11 | 297 |
| 1st-order ZoomSIB, adaptive stop | 3 | -4.0 | 0.257 | 37/50 | 50/50 | 0.08 | 353 |
| 2nd-order Stein | -1 | +4.0 | 0.412 | 9/50 | 37/50 | 0.22 | 960 |
| 2nd-order Stein | 0 | +2.0 | 0.225 | 45/50 | 50/50 | 0.24 | 960 |
| 2nd-order Stein | 0.5 | +1.0 | 0.163 | 50/50 | 50/50 | 0.29 | 960 |
| 2nd-order Stein | 0.75 | +0.5 | 0.147 | 50/50 | 50/50 | 0.32 | 960 |
| 2nd-order Stein | 0.9 | +0.2 | 0.144 | 50/50 | 50/50 | 0.32 | 960 |
| 2nd-order Stein | 1 | +0.0 | 0.145 | 50/50 | 50/50 | 0.33 | 960 |
| 2nd-order Stein | 1.1 | -0.2 | 0.148 | 50/50 | 50/50 | 0.32 | 960 |
| 2nd-order Stein | 1.25 | -0.5 | 0.157 | 50/50 | 50/50 | 0.32 | 960 |
| 2nd-order Stein | 1.5 | -1.0 | 0.179 | 50/50 | 50/50 | 0.29 | 960 |
| 2nd-order Stein | 2 | -2.0 | 0.243 | 40/50 | 50/50 | 0.24 | 960 |
| 2nd-order Stein | 3 | -4.0 | 0.397 | 9/50 | 42/50 | 0.22 | 960 |

## Part B: networks (20 paired trials per cell)

| cell | G = mean μ²/μ̄² | method | network regret | ÷ random | sin-angle error | Phase-1 scalars |
|---|---|---|---|---|---|---|
| imbalance s=0.5, 0/8 falling | 1.0 | each alone, 1st-order | 21,789 ± 1,360 | 0.22 | 0.451 | 0 |
| imbalance s=0.5, 0/8 falling | 1.0 | each alone, 2nd-order | 33,155 ± 1,714 | 0.33 | 0.450 | 0 |
| imbalance s=0.5, 0/8 falling | 1.0 | pooled sums (current) | 5,323 ± 600 | 0.05 | 0.158 | 184 |
| imbalance s=0.5, 0/8 falling | 1.0 | aligned (simple fix) | 5,322 ± 596 | 0.05 | 0.158 | 184 |
| imbalance s=0.5, 0/8 falling | 1.0 | outer (unbiased) | 5,892 ± 748 | 0.06 | 0.177 | 264 |
| imbalance s=0.5, 0/8 falling | 1.0 | pooled 2nd-order | 9,062 ± 812 | 0.09 | 0.172 | 544 |
| imbalance s=0.5, 1/8 falling | 1.8 | each alone, 1st-order | 21,695 ± 1,327 | 0.22 | 0.451 | 0 |
| imbalance s=0.5, 1/8 falling | 1.8 | each alone, 2nd-order | 32,930 ± 1,679 | 0.33 | 0.450 | 0 |
| imbalance s=0.5, 1/8 falling | 1.8 | pooled sums (current) | 7,371 ± 1,070 | 0.07 | 0.212 | 184 |
| imbalance s=0.5, 1/8 falling | 1.8 | aligned (simple fix) | 5,967 ± 442 | 0.06 | 0.166 | 184 |
| imbalance s=0.5, 1/8 falling | 1.8 | outer (unbiased) | 6,694 ± 551 | 0.07 | 0.191 | 264 |
| imbalance s=0.5, 1/8 falling | 1.8 | pooled 2nd-order | 10,066 ± 812 | 0.10 | 0.179 | 544 |
| imbalance s=0.5, 2/8 falling | 4.0 | each alone, 1st-order | 21,865 ± 1,447 | 0.22 | 0.451 | 0 |
| imbalance s=0.5, 2/8 falling | 4.0 | each alone, 2nd-order | 32,868 ± 1,658 | 0.33 | 0.450 | 0 |
| imbalance s=0.5, 2/8 falling | 4.0 | pooled sums (current) | 12,581 ± 2,330 | 0.13 | 0.322 | 184 |
| imbalance s=0.5, 2/8 falling | 4.0 | aligned (simple fix) | 5,951 ± 393 | 0.06 | 0.164 | 184 |
| imbalance s=0.5, 2/8 falling | 4.0 | outer (unbiased) | 6,725 ± 470 | 0.07 | 0.190 | 264 |
| imbalance s=0.5, 2/8 falling | 4.0 | pooled 2nd-order | 10,000 ± 740 | 0.10 | 0.173 | 544 |
| imbalance s=0.5, 3/8 falling | 16.0 | each alone, 1st-order | 22,622 ± 1,535 | 0.23 | 0.451 | 0 |
| imbalance s=0.5, 3/8 falling | 16.0 | each alone, 2nd-order | 32,923 ± 1,572 | 0.33 | 0.450 | 0 |
| imbalance s=0.5, 3/8 falling | 16.0 | pooled sums (current) | 34,291 ± 9,634 | 0.35 | 0.561 | 184 |
| imbalance s=0.5, 3/8 falling | 16.0 | aligned (simple fix) | 6,100 ± 612 | 0.06 | 0.164 | 184 |
| imbalance s=0.5, 3/8 falling | 16.0 | outer (unbiased) | 6,596 ± 586 | 0.07 | 0.182 | 264 |
| imbalance s=0.5, 3/8 falling | 16.0 | pooled 2nd-order | 10,237 ± 783 | 0.10 | 0.179 | 544 |
| imbalance s=0.5, 4/8 falling | ∞ | each alone, 1st-order | 23,026 ± 1,591 | 0.23 | 0.451 | 0 |
| imbalance s=0.5, 4/8 falling | ∞ | each alone, 2nd-order | 32,929 ± 1,631 | 0.33 | 0.450 | 0 |
| imbalance s=0.5, 4/8 falling | ∞ | pooled sums (current) | 82,645 ± 6,244 | 0.83 | 0.906 | 184 |
| imbalance s=0.5, 4/8 falling | ∞ | aligned (simple fix) | 6,175 ± 489 | 0.06 | 0.167 | 184 |
| imbalance s=0.5, 4/8 falling | ∞ | outer (unbiased) | 6,637 ± 573 | 0.07 | 0.183 | 264 |
| imbalance s=0.5, 4/8 falling | ∞ | pooled 2nd-order | 10,060 ± 751 | 0.10 | 0.174 | 544 |
| imbalance s=1, 0/8 falling | 1.0 | each alone, 1st-order | 16,401 ± 850 | 0.10 | 0.344 | 0 |
| imbalance s=1, 0/8 falling | 1.0 | each alone, 2nd-order | 46,935 ± 2,108 | 0.30 | 0.581 | 0 |
| imbalance s=1, 0/8 falling | 1.0 | pooled sums (current) | 4,787 ± 345 | 0.03 | 0.116 | 184 |
| imbalance s=1, 0/8 falling | 1.0 | aligned (simple fix) | 4,791 ± 344 | 0.03 | 0.116 | 184 |
| imbalance s=1, 0/8 falling | 1.0 | outer (unbiased) | 4,945 ± 388 | 0.03 | 0.123 | 264 |
| imbalance s=1, 0/8 falling | 1.0 | pooled 2nd-order | 11,631 ± 1,320 | 0.07 | 0.238 | 544 |
| imbalance s=1, 1/8 falling | 1.8 | each alone, 1st-order | 16,394 ± 921 | 0.10 | 0.344 | 0 |
| imbalance s=1, 1/8 falling | 1.8 | each alone, 2nd-order | 46,571 ± 1,873 | 0.29 | 0.581 | 0 |
| imbalance s=1, 1/8 falling | 1.8 | pooled sums (current) | 7,090 ± 655 | 0.04 | 0.155 | 184 |
| imbalance s=1, 1/8 falling | 1.8 | aligned (simple fix) | 6,336 ± 338 | 0.04 | 0.119 | 184 |
| imbalance s=1, 1/8 falling | 1.8 | outer (unbiased) | 6,514 ± 352 | 0.04 | 0.128 | 264 |
| imbalance s=1, 1/8 falling | 1.8 | pooled 2nd-order | 15,319 ± 1,301 | 0.10 | 0.248 | 544 |
| imbalance s=1, 2/8 falling | 4.0 | each alone, 1st-order | 16,548 ± 995 | 0.10 | 0.344 | 0 |
| imbalance s=1, 2/8 falling | 4.0 | each alone, 2nd-order | 47,174 ± 2,359 | 0.30 | 0.581 | 0 |
| imbalance s=1, 2/8 falling | 4.0 | pooled sums (current) | 10,006 ± 1,137 | 0.06 | 0.235 | 184 |
| imbalance s=1, 2/8 falling | 4.0 | aligned (simple fix) | 6,542 ± 277 | 0.04 | 0.122 | 184 |
| imbalance s=1, 2/8 falling | 4.0 | outer (unbiased) | 6,716 ± 295 | 0.04 | 0.131 | 264 |
| imbalance s=1, 2/8 falling | 4.0 | pooled 2nd-order | 15,178 ± 1,092 | 0.10 | 0.240 | 544 |
| imbalance s=1, 3/8 falling | 16.0 | each alone, 1st-order | 17,002 ± 1,006 | 0.11 | 0.344 | 0 |
| imbalance s=1, 3/8 falling | 16.0 | each alone, 2nd-order | 48,179 ± 2,193 | 0.30 | 0.581 | 0 |
| imbalance s=1, 3/8 falling | 16.0 | pooled sums (current) | 26,729 ± 6,514 | 0.17 | 0.449 | 184 |
| imbalance s=1, 3/8 falling | 16.0 | aligned (simple fix) | 6,668 ± 350 | 0.04 | 0.123 | 184 |
| imbalance s=1, 3/8 falling | 16.0 | outer (unbiased) | 6,754 ± 320 | 0.04 | 0.127 | 264 |
| imbalance s=1, 3/8 falling | 16.0 | pooled 2nd-order | 16,031 ± 1,418 | 0.10 | 0.249 | 544 |
| imbalance s=1, 4/8 falling | ∞ | each alone, 1st-order | 17,120 ± 980 | 0.11 | 0.344 | 0 |
| imbalance s=1, 4/8 falling | ∞ | each alone, 2nd-order | 47,929 ± 2,227 | 0.30 | 0.581 | 0 |
| imbalance s=1, 4/8 falling | ∞ | pooled sums (current) | 129,569 ± 12,760 | 0.82 | 0.917 | 184 |
| imbalance s=1, 4/8 falling | ∞ | aligned (simple fix) | 6,654 ± 335 | 0.04 | 0.120 | 184 |
| imbalance s=1, 4/8 falling | ∞ | outer (unbiased) | 6,696 ± 339 | 0.04 | 0.121 | 264 |
| imbalance s=1, 4/8 falling | ∞ | pooled 2nd-order | 15,658 ± 1,266 | 0.10 | 0.238 | 544 |
| spread, μ̄ = +2.0 | 1.4 | each alone, 1st-order | 27,895 ± 1,260 | 0.15 | 0.373 | 0 |
| spread, μ̄ = +2.0 | 1.4 | each alone, 2nd-order | 65,293 ± 4,917 | 0.34 | 0.789 | 0 |
| spread, μ̄ = +2.0 | 1.4 | pooled sums (current) | 6,766 ± 435 | 0.04 | 0.150 | 184 |
| spread, μ̄ = +2.0 | 1.4 | aligned (simple fix) | 6,871 ± 367 | 0.04 | 0.153 | 184 |
| spread, μ̄ = +2.0 | 1.4 | outer (unbiased) | 7,775 ± 543 | 0.04 | 0.181 | 264 |
| spread, μ̄ = +2.0 | 1.4 | pooled 2nd-order | 16,540 ± 1,813 | 0.09 | 0.275 | 544 |
| spread, μ̄ = +1.0 | 2.7 | each alone, 1st-order | 28,270 ± 2,185 | 0.21 | 0.344 | 0 |
| spread, μ̄ = +1.0 | 2.7 | each alone, 2nd-order | 42,821 ± 3,073 | 0.32 | 0.707 | 0 |
| spread, μ̄ = +1.0 | 2.7 | pooled sums (current) | 7,997 ± 752 | 0.06 | 0.205 | 184 |
| spread, μ̄ = +1.0 | 2.7 | aligned (simple fix) | 6,847 ± 464 | 0.05 | 0.162 | 184 |
| spread, μ̄ = +1.0 | 2.7 | outer (unbiased) | 7,482 ± 552 | 0.06 | 0.183 | 264 |
| spread, μ̄ = +1.0 | 2.7 | pooled 2nd-order | 13,274 ± 1,111 | 0.10 | 0.216 | 544 |
| spread, μ̄ = +0.5 | 7.9 | each alone, 1st-order | 28,778 ± 1,954 | 0.24 | 0.339 | 0 |
| spread, μ̄ = +0.5 | 7.9 | each alone, 2nd-order | 38,164 ± 2,328 | 0.32 | 0.655 | 0 |
| spread, μ̄ = +0.5 | 7.9 | pooled sums (current) | 15,590 ± 2,671 | 0.13 | 0.357 | 184 |
| spread, μ̄ = +0.5 | 7.9 | aligned (simple fix) | 6,720 ± 416 | 0.06 | 0.162 | 184 |
| spread, μ̄ = +0.5 | 7.9 | outer (unbiased) | 7,332 ± 545 | 0.06 | 0.181 | 264 |
| spread, μ̄ = +0.5 | 7.9 | pooled 2nd-order | 12,519 ± 929 | 0.11 | 0.202 | 544 |
| spread, μ̄ = -0.0 | ∞ | each alone, 1st-order | 30,067 ± 2,209 | 0.27 | 0.344 | 0 |
| spread, μ̄ = -0.0 | ∞ | each alone, 2nd-order | 35,998 ± 1,850 | 0.32 | 0.581 | 0 |
| spread, μ̄ = -0.0 | ∞ | pooled sums (current) | 92,796 ± 7,565 | 0.82 | 0.907 | 184 |
| spread, μ̄ = -0.0 | ∞ | aligned (simple fix) | 6,768 ± 409 | 0.06 | 0.167 | 184 |
| spread, μ̄ = -0.0 | ∞ | outer (unbiased) | 7,181 ± 467 | 0.06 | 0.181 | 264 |
| spread, μ̄ = -0.0 | ∞ | pooled 2nd-order | 12,181 ± 869 | 0.11 | 0.197 | 544 |
| noisy N=16, 8/16 falling, 60 samples/agent | ∞ | each alone, 1st-order | 47,732 ± 1,995 | 0.15 | 0.451 | 0 |
| noisy N=16, 8/16 falling, 60 samples/agent | ∞ | each alone, 2nd-order | 122,481 ± 3,877 | 0.39 | 0.710 | 0 |
| noisy N=16, 8/16 falling, 60 samples/agent | ∞ | pooled sums (current) | 231,393 ± 24,899 | 0.73 | 0.880 | 368 |
| noisy N=16, 8/16 falling, 60 samples/agent | ∞ | aligned (simple fix) | 9,105 ± 433 | 0.03 | 0.124 | 368 |
| noisy N=16, 8/16 falling, 60 samples/agent | ∞ | outer (unbiased) | 9,254 ± 459 | 0.03 | 0.129 | 528 |
| noisy N=16, 8/16 falling, 60 samples/agent | ∞ | pooled 2nd-order | 23,139 ± 1,782 | 0.07 | 0.238 | 1,088 |
| noisy N=16, 6/16 falling, 60 samples/agent | 16.0 | each alone, 1st-order | 47,445 ± 2,075 | 0.15 | 0.451 | 0 |
| noisy N=16, 6/16 falling, 60 samples/agent | 16.0 | each alone, 2nd-order | 121,088 ± 4,047 | 0.38 | 0.710 | 0 |
| noisy N=16, 6/16 falling, 60 samples/agent | 16.0 | pooled sums (current) | 56,406 ± 11,707 | 0.18 | 0.480 | 368 |
| noisy N=16, 6/16 falling, 60 samples/agent | 16.0 | aligned (simple fix) | 9,102 ± 410 | 0.03 | 0.125 | 368 |
| noisy N=16, 6/16 falling, 60 samples/agent | 16.0 | outer (unbiased) | 9,217 ± 305 | 0.03 | 0.129 | 528 |
| noisy N=16, 6/16 falling, 60 samples/agent | 16.0 | pooled 2nd-order | 23,158 ± 1,847 | 0.07 | 0.238 | 1,088 |
| noisy N=32, 16/32 falling, 30 samples/agent | ∞ | each alone, 1st-order | 137,669 ± 3,390 | 0.22 | 0.521 | 0 |
| noisy N=32, 16/32 falling, 30 samples/agent | ∞ | each alone, 2nd-order | 297,374 ± 8,652 | 0.47 | 0.790 | 0 |
| noisy N=32, 16/32 falling, 30 samples/agent | ∞ | pooled sums (current) | 421,607 ± 90,376 | 0.67 | 0.832 | 736 |
| noisy N=32, 16/32 falling, 30 samples/agent | ∞ | aligned (simple fix) | 13,322 ± 1,309 | 0.02 | 0.122 | 736 |
| noisy N=32, 16/32 falling, 30 samples/agent | ∞ | outer (unbiased) | 15,094 ± 1,786 | 0.02 | 0.141 | 1,056 |
| noisy N=32, 16/32 falling, 30 samples/agent | ∞ | pooled 2nd-order | 38,573 ± 4,663 | 0.06 | 0.244 | 2,176 |

## Rescue: 2 agents at the peak among 6 others (μ̄ = 0.5)

| method | peak agents' regret ÷ random | other agents' regret ÷ random |
|---|---|---|
| each alone, 1st-order | 0.79 | 0.13 |
| each alone, 2nd-order | 0.35 | 0.31 |
| pooled sums (current) | 0.19 | 0.15 |
| aligned (simple fix) | 0.05 | 0.06 |
| outer (unbiased) | 0.05 | 0.06 |
| pooled 2nd-order | 0.09 | 0.11 |
