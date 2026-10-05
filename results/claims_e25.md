# E25: multi-index bandits

T = 10,000 rounds per agent, Δ = 4.0·(NT)^(-1/(m+2)), pooled Phase-1 size 160·d (fixed), event-triggered Phase 2 (γ = 0.5), 20 paired trials (5 for the share sweep), mean ± 95% CI.

| link | m | N | config | network regret | subspace error | slope in N |
|---|---|---|---|---|---|---|
| bowl | 1 | 1 | mib_fed | 2,428 ± 42 | 0.137 | 0.23 |
| bowl | 1 | 2 | mib_fed | 2,698 ± 100 | 0.134 | 0.23 |
| bowl | 1 | 4 | mib_fed | 3,213 ± 147 | 0.139 | 0.23 |
| bowl | 1 | 8 | mib_fed | 3,885 ± 271 | 0.125 | 0.23 |
| bowl | 1 | 1 | mib_p1only | 2,428 ± 42 | 0.137 | 0.51 |
| bowl | 1 | 2 | mib_p1only | 2,991 ± 118 | 0.134 | 0.51 |
| bowl | 1 | 4 | mib_p1only | 4,222 ± 192 | 0.139 | 0.51 |
| bowl | 1 | 8 | mib_p1only | 7,054 ± 427 | 0.125 | 0.51 |
| bowl | 1 | 1 | sib_on_mib | 2,461 ± 50 | – | 0.23 |
| bowl | 1 | 2 | sib_on_mib | 2,740 ± 94 | – | 0.23 |
| bowl | 1 | 4 | sib_on_mib | 3,185 ± 117 | – | 0.23 |
| bowl | 1 | 8 | sib_on_mib | 4,012 ± 249 | – | 0.23 |
| bowl | 2 | 1 | mib_fed | 7,520 ± 114 | 0.212 | 0.45 |
| bowl | 2 | 2 | mib_fed | 9,486 ± 288 | 0.208 | 0.45 |
| bowl | 2 | 4 | mib_fed | 13,137 ± 374 | 0.190 | 0.45 |
| bowl | 2 | 8 | mib_fed | 18,933 ± 1,095 | 0.213 | 0.45 |
| bowl | 2 | 1 | mib_p1only | 7,520 ± 114 | 0.212 | 1.04 |
| bowl | 2 | 2 | mib_p1only | 12,919 ± 388 | 0.208 | 1.04 |
| bowl | 2 | 4 | mib_p1only | 27,821 ± 566 | 0.190 | 1.04 |
| bowl | 2 | 8 | mib_p1only | 64,676 ± 1,971 | 0.213 | 1.04 |
| bowl | 2 | 1 | sib_on_mib | 11,982 ± 110 | – | 0.90 |
| bowl | 2 | 2 | sib_on_mib | 21,526 ± 233 | – | 0.90 |
| bowl | 2 | 4 | sib_on_mib | 40,282 ± 287 | – | 0.90 |
| bowl | 2 | 8 | sib_on_mib | 77,668 ± 525 | – | 0.90 |
| mixed | 1 | 1 | mib_fed | 1,653 ± 37 | 0.096 | 0.35 |
| mixed | 1 | 2 | mib_fed | 1,903 ± 75 | 0.097 | 0.35 |
| mixed | 1 | 4 | mib_fed | 2,414 ± 136 | 0.102 | 0.35 |
| mixed | 1 | 8 | mib_fed | 3,392 ± 460 | 0.100 | 0.35 |
| mixed | 1 | 1 | mib_p1only | 1,653 ± 37 | 0.096 | 0.44 |
| mixed | 1 | 2 | mib_p1only | 1,970 ± 75 | 0.097 | 0.44 |
| mixed | 1 | 4 | mib_p1only | 2,671 ± 137 | 0.102 | 0.44 |
| mixed | 1 | 8 | mib_p1only | 4,154 ± 464 | 0.100 | 0.44 |
| mixed | 1 | 1 | sib_on_mib | 8,384 ± 111 | – | 0.99 |
| mixed | 1 | 2 | sib_on_mib | 16,603 ± 297 | – | 0.99 |
| mixed | 1 | 4 | sib_on_mib | 32,913 ± 902 | – | 0.99 |
| mixed | 1 | 8 | sib_on_mib | 65,052 ± 2,175 | – | 0.99 |
| mixed | 2 | 1 | mib_fed | 4,234 ± 93 | 0.205 | 0.52 |
| mixed | 2 | 2 | mib_fed | 5,455 ± 246 | 0.202 | 0.52 |
| mixed | 2 | 4 | mib_fed | 8,015 ± 723 | 0.196 | 0.52 |
| mixed | 2 | 8 | mib_fed | 12,381 ± 922 | 0.206 | 0.52 |
| mixed | 2 | 1 | mib_p1only | 4,234 ± 93 | 0.205 | 0.94 |
| mixed | 2 | 2 | mib_p1only | 6,697 ± 258 | 0.202 | 0.94 |
| mixed | 2 | 4 | mib_p1only | 13,384 ± 767 | 0.196 | 0.94 |
| mixed | 2 | 8 | mib_p1only | 29,585 ± 1,096 | 0.206 | 0.94 |
| mixed | 2 | 1 | sib_on_mib | 9,054 ± 44 | – | 0.94 |
| mixed | 2 | 2 | sib_on_mib | 16,959 ± 97 | – | 0.94 |
| mixed | 2 | 4 | sib_on_mib | 32,744 ± 111 | – | 0.94 |
| mixed | 2 | 8 | sib_on_mib | 64,238 ± 324 | – | 0.94 |

## Second-order Stein: subspace error vs n (d = 10, m = 2)

| link | slope | n=250 | n=500 | n=1000 | n=2000 | n=4000 | n=8000 | n=16000 | n=32000 |
|---|---|---|---|---|---|---|---|---|---|
| bowl | -0.49 | 0.475 | 0.346 | 0.258 | 0.181 | 0.132 | 0.086 | 0.063 | 0.045 |
| mixed | -0.48 | 0.524 | 0.346 | 0.246 | 0.178 | 0.131 | 0.091 | 0.066 | 0.048 |

## Phase-1 strategies (N = 8, m = 2)

| link | d | strategy | Phase-1 scalars | subspace error | network regret | Phase-1 share |
|---|---|---|---|---|---|---|
| bowl | 10 | exact | 624 | 0.213 | 18,933 ± 1,095 | 0.22% |
| bowl | 10 | projavg | 344 | 0.222 | 19,517 ± 1,080 | 0.12% |
| bowl | 10 | power2 | 656 | 0.227 | 20,139 ± 1,189 | 0.22% |
| bowl | 10 | power5 | 1,616 | 0.213 | 19,115 ± 1,187 | 0.56% |
| bowl | 10 | power10 | 3,216 | 0.213 | 19,081 ± 1,076 | 1.10% |
| bowl | 50 | exact | 11,024 | 0.201 | 35,499 ± 460 | 3.22% |
| bowl | 50 | projavg | 1,624 | 0.220 | 36,353 ± 420 | 0.49% |
| bowl | 50 | power2 | 3,216 | 0.417 | 49,957 ± 9,778 | 0.90% |
| bowl | 50 | power5 | 8,016 | 0.202 | 35,636 ± 477 | 2.35% |
| bowl | 50 | power10 | 16,016 | 0.201 | 35,538 ± 487 | 4.61% |
| mixed | 10 | exact | 624 | 0.206 | 12,381 ± 922 | 0.17% |
| mixed | 10 | projavg | 344 | 0.243 | 14,732 ± 1,446 | 0.10% |
| mixed | 10 | power2 | 656 | 0.360 | 23,545 ± 7,802 | 0.19% |
| mixed | 10 | power5 | 1,616 | 0.208 | 12,486 ± 1,094 | 0.45% |
| mixed | 10 | power10 | 3,216 | 0.206 | 12,378 ± 924 | 0.89% |
| mixed | 50 | exact | 11,024 | 0.214 | 22,269 ± 688 | 2.78% |
| mixed | 50 | projavg | 1,624 | 0.294 | 27,143 ± 1,051 | 0.42% |
| mixed | 50 | power2 | 3,216 | 0.517 | 43,162 ± 7,268 | 0.85% |
| mixed | 50 | power5 | 8,016 | 0.217 | 22,478 ± 835 | 2.05% |
| mixed | 50 | power10 | 16,016 | 0.214 | 22,290 ± 688 | 4.00% |

## Phase-1 share vs d (N = 8, m = 2, bowl; single-index on the quadratic link)

| model | d | Phase-1 scalars | Phase-2 scalars | Phase-1 share | network regret |
|---|---|---|---|---|---|
| multi-index, exact matrix | 10 | 624 | 310,371 | 0.20% | 20,836 ± 1,057 |
| multi-index, exact matrix | 20 | 2,024 | 329,770 | 0.61% | 23,611 ± 822 |
| multi-index, exact matrix | 50 | 11,024 | 331,093 | 3.23% | 35,146 ± 913 |
| multi-index, exact matrix | 100 | 42,024 | 326,223 | 11.42% | 54,301 ± 302 |
| multi-index, projection avg | 10 | 344 | 308,686 | 0.11% | 20,121 ± 1,174 |
| multi-index, projection avg | 20 | 664 | 320,593 | 0.21% | 23,738 ± 517 |
| multi-index, projection avg | 50 | 1,624 | 335,157 | 0.48% | 36,119 ± 797 |
| multi-index, projection avg | 100 | 3,224 | 329,069 | 0.97% | 54,880 ± 214 |
| single-index (vector) | 10 | 184 | 100,070 | 0.19% | 5,933 ± 331 |
| single-index (vector) | 20 | 344 | 102,037 | 0.34% | 9,487 ± 270 |
| single-index (vector) | 50 | 824 | 103,877 | 0.82% | 18,799 ± 449 |
| single-index (vector) | 100 | 1,624 | 123,046 | 1.31% | 35,145 ± 466 |
