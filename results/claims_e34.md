# E34: prior papers' algorithms on our problem, over a graph

N = 8 agents on a ring (D = 4), d = 10, K = 20, σ = 0.1, 10 paired trials, mean ± 95% CI. Prior algorithms get IDEAL relaying: every raw observation reaches every agent after graph-distance rounds (d + 2 scalars per pull per receiving agent), an upper bound on the information their own gossip provides. IGP-UCB refits every 25·N pooled points (as often per agent as the single-agent version) on at most 400 points. ZoomSIB variants use pooled Phase-1 size 960·(NT/160k)^(2/3). '÷ ours' is regret relative to Dec-ZoomSIB-Relay.

| link | T | algorithm | network regret | ÷ ours | scalars |
|---|---|---|---|---|---|
| quadratic | 1,000 | Dec-ZoomSIB-Relay (ours) | 1,881 ± 384 | 1.00 | 19,526 |
| quadratic | 1,000 | ZoomSIB with a server | 1,792 ± 416 | 0.95 | 20,684 |
| quadratic | 1,000 | independent ZoomSIB | 5,239 ± 183 | 2.79 | 0 |
| quadratic | 1,000 | DLUCB-style (LinUCB) | 7,274 ± 112 | 3.87 | 672,000 |
| quadratic | 1,000 | Dec-ESTOR | 8,792 ± 67 | 4.67 | 672,000 |
| quadratic | 1,000 | Dec-GSTOR | 5,370 ± 90 | 2.86 | 672,000 |
| quadratic | 1,000 | Coop-Kernel-style (IGP-UCB) | 2,337 ± 35 | 1.24 | 672,000 |
| quadratic | 4,000 | Dec-ZoomSIB-Relay (ours) | 3,242 ± 560 | 1.00 | 38,946 |
| quadratic | 4,000 | ZoomSIB with a server | 3,132 ± 553 | 0.97 | 46,325 |
| quadratic | 4,000 | independent ZoomSIB | 11,175 ± 268 | 3.45 | 0 |
| quadratic | 4,000 | DLUCB-style (LinUCB) | 27,652 ± 188 | 8.53 | 2,688,000 |
| quadratic | 4,000 | Dec-ESTOR | 33,633 ± 125 | 10.37 | 2,688,000 |
| quadratic | 4,000 | Dec-GSTOR | 15,091 ± 160 | 4.65 | 2,688,000 |
| quadratic | 4,000 | Coop-Kernel-style (IGP-UCB) | 10,006 ± 43 | 3.09 | 2,688,000 |
| zigzag | 1,000 | Dec-ZoomSIB-Relay (ours) | 867 ± 134 | 1.00 | 27,796 |
| zigzag | 1,000 | ZoomSIB with a server | 823 ± 131 | 0.95 | 31,442 |
| zigzag | 1,000 | independent ZoomSIB | 2,634 ± 37 | 3.04 | 0 |
| zigzag | 1,000 | DLUCB-style (LinUCB) | 468 ± 29 | 0.54 | 672,000 |
| zigzag | 1,000 | Dec-ESTOR | 1,646 ± 25 | 1.90 | 672,000 |
| zigzag | 1,000 | Dec-GSTOR | 3,900 ± 34 | 4.50 | 672,000 |
| zigzag | 1,000 | Coop-Kernel-style (IGP-UCB) | 1,964 ± 23 | 2.26 | 672,000 |
| zigzag | 4,000 | Dec-ZoomSIB-Relay (ours) | 1,480 ± 188 | 1.00 | 64,570 |
| zigzag | 4,000 | ZoomSIB with a server | 1,426 ± 188 | 0.96 | 78,342 |
| zigzag | 4,000 | independent ZoomSIB | 5,809 ± 44 | 3.93 | 0 |
| zigzag | 4,000 | DLUCB-style (LinUCB) | 1,656 ± 74 | 1.12 | 2,688,000 |
| zigzag | 4,000 | Dec-ESTOR | 3,973 ± 39 | 2.68 | 2,688,000 |
| zigzag | 4,000 | Dec-GSTOR | 10,969 ± 69 | 7.41 | 2,688,000 |
| zigzag | 4,000 | Coop-Kernel-style (IGP-UCB) | 8,200 ± 29 | 5.54 | 2,688,000 |
| logistic | 1,000 | Dec-ZoomSIB-Relay (ours) | 677 ± 165 | 1.00 | 41,823 |
| logistic | 1,000 | ZoomSIB with a server | 661 ± 169 | 0.98 | 46,133 |
| logistic | 1,000 | independent ZoomSIB | 1,084 ± 42 | 1.60 | 0 |
| logistic | 1,000 | DLUCB-style (LinUCB) | 107 ± 24 | 0.16 | 672,000 |
| logistic | 1,000 | Dec-ESTOR | 437 ± 42 | 0.65 | 672,000 |
| logistic | 1,000 | Dec-GSTOR | 973 ± 8 | 1.44 | 672,000 |
| logistic | 1,000 | Coop-Kernel-style (IGP-UCB) | 1,906 ± 8 | 2.82 | 672,000 |
| logistic | 4,000 | Dec-ZoomSIB-Relay (ours) | 1,421 ± 328 | 1.00 | 110,698 |
| logistic | 4,000 | ZoomSIB with a server | 1,384 ± 329 | 0.97 | 131,386 |
| logistic | 4,000 | independent ZoomSIB | 2,420 ± 84 | 1.70 | 0 |
| logistic | 4,000 | DLUCB-style (LinUCB) | 188 ± 44 | 0.13 | 2,688,000 |
| logistic | 4,000 | Dec-ESTOR | 873 ± 54 | 0.61 | 2,688,000 |
| logistic | 4,000 | Dec-GSTOR | 2,721 ± 16 | 1.92 | 2,688,000 |
| logistic | 4,000 | Coop-Kernel-style (IGP-UCB) | 7,783 ± 16 | 5.48 | 2,688,000 |
