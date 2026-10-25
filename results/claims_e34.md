# E34: prior papers' algorithms on our problem, over a graph

N = 8 agents on a ring (D = 4), d = 10, K = 20, σ = 0.1, 10 paired trials, mean ± 95% CI. Prior algorithms get IDEAL relaying: every raw observation reaches every agent after graph-distance rounds (d + 2 scalars per pull per receiving agent), an upper bound on the information their own gossip provides. IGP-UCB refits every 25·N pooled points (as often per agent as the single-agent version) on at most 400 points. ZoomSIB variants use pooled Phase-1 size 960·(NT/160k)^(2/3). '÷ ours' is regret relative to Dec-ZoomSIB-Relay.

| link | T | algorithm | network regret | ÷ ours | scalars |
|---|---|---|---|---|---|
| quadratic | 1,000 | Dec-ZoomSIB-Relay (ours) | 1,884 ± 395 | 1.00 | 20,035 |
| quadratic | 1,000 | ZoomSIB with a server | 1,792 ± 416 | 0.95 | 20,684 |
| quadratic | 1,000 | independent ZoomSIB | 5,239 ± 183 | 2.78 | 0 |
| quadratic | 1,000 | DLUCB-style (LinUCB) | 7,274 ± 112 | 3.86 | 672,000 |
| quadratic | 1,000 | Dec-ESTOR | 8,792 ± 67 | 4.67 | 672,000 |
| quadratic | 1,000 | Dec-GSTOR | 5,370 ± 90 | 2.85 | 672,000 |
| quadratic | 1,000 | Coop-Kernel-style (IGP-UCB) | 2,337 ± 35 | 1.24 | 672,000 |
| quadratic | 4,000 | Dec-ZoomSIB-Relay (ours) | 3,235 ± 555 | 1.00 | 38,328 |
| quadratic | 4,000 | ZoomSIB with a server | 3,132 ± 553 | 0.97 | 46,325 |
| quadratic | 4,000 | independent ZoomSIB | 11,175 ± 268 | 3.45 | 0 |
| quadratic | 4,000 | DLUCB-style (LinUCB) | 27,652 ± 188 | 8.55 | 2,688,000 |
| quadratic | 4,000 | Dec-ESTOR | 33,633 ± 125 | 10.40 | 2,688,000 |
| quadratic | 4,000 | Dec-GSTOR | 15,091 ± 160 | 4.67 | 2,688,000 |
| quadratic | 4,000 | Coop-Kernel-style (IGP-UCB) | 10,006 ± 43 | 3.09 | 2,688,000 |
| zigzag | 1,000 | Dec-ZoomSIB-Relay (ours) | 865 ± 133 | 1.00 | 26,860 |
| zigzag | 1,000 | ZoomSIB with a server | 823 ± 131 | 0.95 | 31,442 |
| zigzag | 1,000 | independent ZoomSIB | 2,634 ± 37 | 3.05 | 0 |
| zigzag | 1,000 | DLUCB-style (LinUCB) | 468 ± 29 | 0.54 | 672,000 |
| zigzag | 1,000 | Dec-ESTOR | 1,646 ± 25 | 1.90 | 672,000 |
| zigzag | 1,000 | Dec-GSTOR | 3,900 ± 34 | 4.51 | 672,000 |
| zigzag | 1,000 | Coop-Kernel-style (IGP-UCB) | 1,964 ± 23 | 2.27 | 672,000 |
| zigzag | 4,000 | Dec-ZoomSIB-Relay (ours) | 1,477 ± 189 | 1.00 | 60,354 |
| zigzag | 4,000 | ZoomSIB with a server | 1,426 ± 188 | 0.97 | 78,342 |
| zigzag | 4,000 | independent ZoomSIB | 5,809 ± 44 | 3.93 | 0 |
| zigzag | 4,000 | DLUCB-style (LinUCB) | 1,656 ± 74 | 1.12 | 2,688,000 |
| zigzag | 4,000 | Dec-ESTOR | 3,973 ± 39 | 2.69 | 2,688,000 |
| zigzag | 4,000 | Dec-GSTOR | 10,969 ± 69 | 7.42 | 2,688,000 |
| zigzag | 4,000 | Coop-Kernel-style (IGP-UCB) | 8,200 ± 29 | 5.55 | 2,688,000 |
| logistic | 1,000 | Dec-ZoomSIB-Relay (ours) | 675 ± 169 | 1.00 | 39,717 |
| logistic | 1,000 | ZoomSIB with a server | 661 ± 169 | 0.98 | 46,133 |
| logistic | 1,000 | independent ZoomSIB | 1,084 ± 42 | 1.61 | 0 |
| logistic | 1,000 | DLUCB-style (LinUCB) | 107 ± 24 | 0.16 | 672,000 |
| logistic | 1,000 | Dec-ESTOR | 437 ± 42 | 0.65 | 672,000 |
| logistic | 1,000 | Dec-GSTOR | 973 ± 8 | 1.44 | 672,000 |
| logistic | 1,000 | Coop-Kernel-style (IGP-UCB) | 1,906 ± 8 | 2.82 | 672,000 |
| logistic | 4,000 | Dec-ZoomSIB-Relay (ours) | 1,411 ± 326 | 1.00 | 98,835 |
| logistic | 4,000 | ZoomSIB with a server | 1,384 ± 329 | 0.98 | 131,386 |
| logistic | 4,000 | independent ZoomSIB | 2,420 ± 84 | 1.72 | 0 |
| logistic | 4,000 | DLUCB-style (LinUCB) | 188 ± 44 | 0.13 | 2,688,000 |
| logistic | 4,000 | Dec-ESTOR | 873 ± 54 | 0.62 | 2,688,000 |
| logistic | 4,000 | Dec-GSTOR | 2,721 ± 16 | 1.93 | 2,688,000 |
| logistic | 4,000 | Coop-Kernel-style (IGP-UCB) | 7,783 ± 16 | 5.52 | 2,688,000 |
