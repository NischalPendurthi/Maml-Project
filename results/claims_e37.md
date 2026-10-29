# E37: coordinated first visits (bin owners)

N = 16, quadratic link, d = 10, σ = 0.1, T = 10,000, K = 20, 10 paired trials, mean ± 95% CI. Pooled Phase-1 size 960; Δ = (NT)^(-1/3). 'excess' is regret minus the server's (same seeds); '÷ KF' divides it by K·F with F the average farness. 'blind' counts Phase-2 pulls into a bin the puller sees as empty.

| graph | F | protocol | regret | excess | ÷ KF | vs server+owner | blind pulls | scalars |
|---|---|---|---|---|---|---|---|---|
| complete | 15 | server, γ = 0.5 | 6,848 ± 615 | 0 ± 0 | 0.00 | -- | 412 ± 22 | 207,674 |
| complete | 15 | server + bin owner, patience 1 | 6,821 ± 612 | -27 ± 17 | -0.09 | -- | 408 ± 23 | 286,094 |
| complete | 15 | server + bin owner, patience 3 | 6,783 ± 610 | -65 ± 12 | -0.22 | -- | 394 ± 22 | 359,282 |
| complete | 15 | server + bin owner, patience 10 | 6,736 ± 604 | -112 ± 25 | -0.37 | -- | 382 ± 21 | 372,276 |
| complete | 15 | published-only relay, γ = 0.5 | 6,966 ± 615 | 118 ± 14 | 0.39 | -- | 412 ± 22 | 187,455 |
| complete | 15 | ... + bin owner, patience 1 | 6,923 ± 607 | 75 ± 20 | 0.25 | 102 ± 23 | 408 ± 23 | 233,086 |
| complete | 15 | ... + bin owner, patience 3 | 6,857 ± 609 | 9 ± 17 | 0.03 | 74 ± 13 | 394 ± 22 | 276,732 |
| complete | 15 | ... + bin owner, patience 10 | 6,809 ± 605 | -39 ± 30 | -0.13 | 73 ± 9 | 382 ± 21 | 289,102 |
| expander | 29 | server, γ = 0.5 | 6,848 ± 615 | 0 ± 0 | 0.00 | -- | 412 ± 22 | 207,674 |
| expander | 29 | server + bin owner, patience 1 | 6,821 ± 612 | -27 ± 17 | -0.05 | -- | 408 ± 23 | 286,094 |
| expander | 29 | server + bin owner, patience 3 | 6,783 ± 610 | -65 ± 12 | -0.11 | -- | 394 ± 22 | 359,282 |
| expander | 29 | server + bin owner, patience 10 | 6,736 ± 604 | -112 ± 25 | -0.19 | -- | 382 ± 21 | 372,276 |
| expander | 29 | published-only relay, γ = 0.5 | 7,096 ± 610 | 249 ± 28 | 0.42 | -- | 454 ± 20 | 185,662 |
| expander | 29 | ... + bin owner, patience 1 | 7,015 ± 607 | 167 ± 23 | 0.29 | 194 ± 27 | 450 ± 24 | 231,675 |
| expander | 29 | ... + bin owner, patience 3 | 6,897 ± 605 | 49 ± 19 | 0.08 | 114 ± 11 | 414 ± 23 | 276,056 |
| expander | 29 | ... + bin owner, patience 10 | 6,807 ± 598 | -41 ± 36 | -0.07 | 71 ± 14 | 383 ± 20 | 282,776 |
| torus | 32 | server, γ = 0.5 | 6,848 ± 615 | 0 ± 0 | 0.00 | -- | 412 ± 22 | 207,674 |
| torus | 32 | server + bin owner, patience 1 | 6,821 ± 612 | -27 ± 17 | -0.04 | -- | 408 ± 23 | 286,094 |
| torus | 32 | server + bin owner, patience 3 | 6,783 ± 610 | -65 ± 12 | -0.10 | -- | 394 ± 22 | 359,282 |
| torus | 32 | server + bin owner, patience 10 | 6,736 ± 604 | -112 ± 25 | -0.17 | -- | 382 ± 21 | 372,276 |
| torus | 32 | published-only relay, γ = 0.5 | 7,150 ± 616 | 302 ± 22 | 0.47 | -- | 465 ± 20 | 180,058 |
| torus | 32 | ... + bin owner, patience 1 | 7,066 ± 590 | 218 ± 45 | 0.34 | 245 ± 42 | 460 ± 22 | 231,307 |
| torus | 32 | ... + bin owner, patience 3 | 6,909 ± 603 | 61 ± 23 | 0.10 | 126 ± 15 | 416 ± 26 | 275,293 |
| torus | 32 | ... + bin owner, patience 10 | 6,808 ± 606 | -40 ± 29 | -0.06 | 72 ± 14 | 383 ± 21 | 286,264 |
| ring | 64 | server, γ = 0.5 | 6,848 ± 615 | 0 ± 0 | 0.00 | -- | 412 ± 22 | 207,674 |
| ring | 64 | server + bin owner, patience 1 | 6,821 ± 612 | -27 ± 17 | -0.02 | -- | 408 ± 23 | 286,094 |
| ring | 64 | server + bin owner, patience 3 | 6,783 ± 610 | -65 ± 12 | -0.05 | -- | 394 ± 22 | 359,282 |
| ring | 64 | server + bin owner, patience 10 | 6,736 ± 604 | -112 ± 25 | -0.09 | -- | 382 ± 21 | 372,276 |
| ring | 64 | published-only relay, γ = 0.5 | 7,385 ± 611 | 538 ± 29 | 0.42 | -- | 543 ± 23 | 179,388 |
| ring | 64 | ... + bin owner, patience 1 | 7,238 ± 599 | 390 ± 31 | 0.30 | 417 ± 35 | 535 ± 20 | 225,894 |
| ring | 64 | ... + bin owner, patience 3 | 6,998 ± 605 | 150 ± 20 | 0.12 | 215 ± 16 | 465 ± 24 | 270,114 |
| ring | 64 | ... + bin owner, patience 10 | 6,828 ± 603 | -20 ± 31 | -0.02 | 92 ± 12 | 386 ± 21 | 285,114 |
| path | 85 | server, γ = 0.5 | 6,848 ± 615 | 0 ± 0 | 0.00 | -- | 412 ± 22 | 207,674 |
| path | 85 | server + bin owner, patience 1 | 6,821 ± 612 | -27 ± 17 | -0.02 | -- | 408 ± 23 | 286,094 |
| path | 85 | server + bin owner, patience 3 | 6,783 ± 610 | -65 ± 12 | -0.04 | -- | 394 ± 22 | 359,282 |
| path | 85 | server + bin owner, patience 10 | 6,736 ± 604 | -112 ± 25 | -0.07 | -- | 382 ± 21 | 372,276 |
| path | 85 | published-only relay, γ = 0.5 | 7,490 ± 613 | 643 ± 22 | 0.38 | -- | 581 ± 25 | 179,925 |
| path | 85 | ... + bin owner, patience 1 | 7,343 ± 592 | 495 ± 43 | 0.29 | 522 ± 47 | 572 ± 18 | 229,370 |
| path | 85 | ... + bin owner, patience 3 | 7,046 ± 609 | 199 ± 21 | 0.12 | 263 ± 18 | 491 ± 24 | 267,664 |
| path | 85 | ... + bin owner, patience 10 | 6,836 ± 601 | -12 ± 30 | -0.01 | 100 ± 11 | 388 ± 21 | 287,312 |
