# E28: exploration length, agreement and communication on graphs

N = 16, T = 10,000, Phase 2 = event-triggered flooding (γ = 0.5) for every decentralised config, 10 paired trials, mean ± 95% CI. T0* = the per-agent Phase-1 length with the lowest mean regret on the grid [15, 30, 60, 120, 240].

| graph | D | Phase-1 method | T0* | regret at T0* | ÷ best server | Phase-1 scalars | disagreement |
|---|---|---|---|---|---|---|---|
| complete | 1 | tree (exact) | 60 | 6,964 ± 618 | 1.017 | 570 | 0.0000 |
| complete | 1 | flooding (exact, D-lag) | 60 | 6,964 ± 618 | 1.017 | 173,040 | 0.0000 |
| complete | 1 | consensus, 1 step/round | 60 | 6,964 ± 618 | 1.017 | 158,640 | 0.0000 |
| complete | 1 | consensus, 5 steps/round | 60 | 6,964 ± 618 | 1.017 | 792,240 | 0.0000 |
| complete | 1 | consensus 1 + agree | 60 | 6,964 ± 618 | 1.017 | 161,280 | 0.0000 |
| hypercube | 4 | tree (exact) | 60 | 7,112 ± 623 | 1.039 | 586 | 0.0000 |
| hypercube | 4 | flooding (exact, D-lag) | 60 | 7,249 ± 669 | 1.059 | 359,680 | 0.0132 |
| hypercube | 4 | consensus, 1 step/round | 60 | 7,300 ± 624 | 1.066 | 42,496 | 0.0336 |
| hypercube | 4 | consensus, 5 steps/round | 60 | 7,105 ± 636 | 1.038 | 211,456 | 0.0032 |
| hypercube | 4 | consensus 1 + agree | 60 | 7,112 ± 623 | 1.039 | 45,312 | 0.0000 |
| torus | 4 | tree (exact) | 60 | 7,131 ± 614 | 1.041 | 586 | 0.0000 |
| torus | 4 | flooding (exact, D-lag) | 60 | 7,269 ± 663 | 1.062 | 359,680 | 0.0132 |
| torus | 4 | consensus, 1 step/round | 60 | 7,325 ± 654 | 1.070 | 42,496 | 0.0336 |
| torus | 4 | consensus, 5 steps/round | 60 | 7,107 ± 626 | 1.038 | 211,456 | 0.0032 |
| torus | 4 | consensus 1 + agree | 60 | 7,131 ± 614 | 1.041 | 45,312 | 0.0000 |
| ring | 8 | tree (exact) | 60 | 7,375 ± 615 | 1.077 | 586 | 0.0000 |
| ring | 8 | flooding (exact, D-lag) | 60 | 7,617 ± 736 | 1.112 | 173,824 | 0.0205 |
| ring | 8 | consensus, 1 step/round | 60 | 8,572 ± 714 | 1.252 | 21,376 | 0.0816 |
| ring | 8 | consensus, 5 steps/round | 60 | 7,587 ± 632 | 1.108 | 105,856 | 0.0328 |
| ring | 8 | consensus 1 + agree | 60 | 7,375 ± 615 | 1.077 | 24,192 | 0.0000 |
| path | 15 | tree (exact) | 60 | 7,480 ± 612 | 1.092 | 780 | 0.0000 |
| path | 15 | flooding (exact, D-lag) | 60 | 7,876 ± 754 | 1.150 | 159,810 | 0.0254 |
| path | 15 | consensus, 1 step/round | 120 | 9,150 ± 667 | 1.336 | 40,050 | 0.0606 |
| path | 15 | consensus, 5 steps/round | 60 | 7,963 ± 651 | 1.163 | 99,450 | 0.0486 |
| path | 15 | consensus 1 + agree | 60 | 7,480 ± 612 | 1.092 | 25,200 | 0.0000 |
| (server) | – | server | 60 | 6,848 ± 615 | 1.000 | 576 | 0 |

## Adaptive stopping vs the best fixed length

| graph | rule | T0 used | flag rounds | regret | Phase-1 scalars |
|---|---|---|---|---|---|
| torus | flood · stop when any | 27 | 1.2 | 11,114 ± 3,538 | 155,128 |
| ring | flood · stop when any | 27 | 6.1 | 10,882 ± 3,371 | 71,935 |
| path | flood · stop when any | 28 | 8.6 | 11,813 ± 3,302 | 68,098 |
| torus | flood · stop when all | 44 | 0.0 | 7,838 ± 769 | 262,605 |
| ring | flood · stop when all | 55 | 0.0 | 7,743 ± 828 | 159,078 |
| path | flood · stop when all | 56 | 0.0 | 8,153 ± 958 | 148,290 |
| torus | cons1 · stop when any | 32 | 2.4 | 9,999 ± 2,162 | 23,224 |
| ring | cons1 · stop when any | 37 | 6.3 | 18,523 ± 7,366 | 13,491 |
| path | cons1 · stop when any | 41 | 8.4 | 16,761 ± 7,189 | 14,261 |
| torus | cons1 · stop when all | 74 | 0.0 | 7,208 ± 632 | 52,634 |
| ring | cons1 · stop when all | 132 | 0.0 | 8,740 ± 974 | 46,826 |
| path | cons1 · stop when all | 141 | 0.0 | 9,518 ± 925 | 47,079 |
| torus | fixed T0* (flood) | 60 | 0.0 | 7,269 ± 663 | 359,680 |
| ring | fixed T0* (flood) | 60 | 0.0 | 7,617 ± 736 | 173,824 |
| path | fixed T0* (flood) | 60 | 0.0 | 7,876 ± 754 | 159,810 |
| torus | fixed T0* (cons1) | 60 | 0.0 | 7,325 ± 654 | 42,496 |
| ring | fixed T0* (cons1) | 60 | 0.0 | 8,572 ± 714 | 21,376 |
| path | fixed T0* (cons1) | 120 | 0.0 | 9,150 ± 667 | 40,050 |
| (server) | server, adaptive stop | 32 | 0 | 9,487 ± 2,337 | 1,286 |
