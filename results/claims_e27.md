# E27: regret vs Phase-2 communication

N = 8, T = 10,000, fixed Phase-1 length, 20 paired trials. Ratio is to sync every round. Sync rounds exclude Phase 1.

| link | schedule | network regret | ratio | sync rounds | total bits |
|---|---|---|---|---|---|
| quadratic | periodic_1 | 4,770 ± 347 | 1.000 | 9,880.0 | 57,765,440 |
| quadratic | periodic_2 | 4,806 ± 347 | 1.008 | 4,940.0 | 49,102,549 |
| quadratic | periodic_5 | 4,912 ± 344 | 1.030 | 1,976.0 | 34,598,950 |
| quadratic | periodic_10 | 5,073 ± 342 | 1.064 | 988.0 | 24,276,536 |
| quadratic | periodic_25 | 5,454 ± 351 | 1.143 | 396.0 | 14,055,200 |
| quadratic | periodic_50 | 6,046 ± 351 | 1.268 | 198.0 | 8,833,122 |
| quadratic | periodic_100 | 6,925 ± 363 | 1.452 | 99.0 | 5,398,765 |
| quadratic | periodic_250 | 8,117 ± 389 | 1.702 | 40.0 | 2,799,910 |
| quadratic | periodic_1000 | 12,923 ± 505 | 2.709 | 10.0 | 1,139,528 |
| quadratic | periodic_2500 | 14,603 ± 802 | 3.061 | 4.0 | 719,936 |
| quadratic | event_0.05 | 4,770 ± 347 | 1.000 | 631.5 | 11,903,754 |
| quadratic | event_0.1 | 4,771 ± 347 | 1.000 | 362.7 | 7,580,254 |
| quadratic | event_0.25 | 4,778 ± 347 | 1.002 | 187.3 | 3,918,445 |
| quadratic | event_0.5 | 4,787 ± 345 | 1.004 | 130.2 | 2,536,885 |
| quadratic | event_1 | 7,246 ± 482 | 1.519 | 6.7 | 725,437 |
| quadratic | event_2 | 8,925 ± 495 | 1.871 | 4.0 | 618,968 |
| quadratic | event_4 | 10,401 ± 611 | 2.181 | 2.4 | 525,786 |
| quadratic | event_8 | 11,506 ± 634 | 2.412 | 2.0 | 518,590 |
| quadratic | event_16 | 12,613 ± 857 | 2.644 | 1.0 | 426,003 |
| quadratic | minimax_1 | 15,877 ± 1,313 | 3.329 | 1.0 | 470,466 |
| quadratic | minimax_2 | 12,416 ± 877 | 2.603 | 2.0 | 540,061 |
| quadratic | minimax_3 | 10,860 ± 738 | 2.277 | 3.0 | 596,715 |
| quadratic | minimax_4 | 10,383 ± 678 | 2.177 | 4.0 | 660,334 |
| quadratic | minimax_5 | 10,213 ± 609 | 2.141 | 5.0 | 729,954 |
| quadratic | minimax_6 | 10,098 ± 594 | 2.117 | 6.0 | 801,493 |
| quadratic | minimax_8 | 9,984 ± 578 | 2.093 | 8.0 | 931,150 |
| quadratic | geometric_1 | 15,877 ± 1,313 | 3.329 | 1.0 | 470,466 |
| quadratic | geometric_2 | 12,246 ± 1,274 | 2.567 | 2.0 | 492,618 |
| quadratic | geometric_3 | 11,225 ± 872 | 2.353 | 3.0 | 531,320 |
| quadratic | geometric_4 | 9,471 ± 721 | 1.986 | 4.0 | 544,035 |
| quadratic | geometric_5 | 8,726 ± 593 | 1.829 | 5.0 | 586,174 |
| quadratic | geometric_6 | 7,925 ± 564 | 1.661 | 6.0 | 609,363 |
| quadratic | geometric_8 | 7,034 ± 489 | 1.475 | 8.0 | 679,270 |
| zigzag | periodic_1 | 2,433 ± 87 | 1.000 | 9,880.0 | 64,474,112 |
| zigzag | periodic_2 | 2,450 ± 88 | 1.007 | 4,940.0 | 60,505,746 |
| zigzag | periodic_5 | 2,502 ± 88 | 1.029 | 1,976.0 | 50,951,235 |
| zigzag | periodic_10 | 2,579 ± 88 | 1.060 | 988.0 | 40,294,045 |
| zigzag | periodic_25 | 2,750 ± 93 | 1.130 | 396.0 | 25,415,648 |
| zigzag | periodic_50 | 2,981 ± 94 | 1.225 | 198.0 | 16,647,598 |
| zigzag | periodic_100 | 3,342 ± 87 | 1.374 | 99.0 | 10,431,114 |
| zigzag | periodic_250 | 3,881 ± 76 | 1.595 | 40.0 | 5,307,296 |
| zigzag | periodic_1000 | 5,175 ± 103 | 2.127 | 10.0 | 1,849,837 |
| zigzag | periodic_2500 | 5,511 ± 134 | 2.265 | 4.0 | 968,816 |
| zigzag | event_0.05 | 2,433 ± 87 | 1.000 | 1,090.7 | 26,701,342 |
| zigzag | event_0.1 | 2,433 ± 87 | 1.000 | 616.5 | 18,089,312 |
| zigzag | event_0.25 | 2,434 ± 86 | 1.001 | 287.9 | 9,439,808 |
| zigzag | event_0.5 | 2,439 ± 86 | 1.003 | 162.4 | 4,984,045 |
| zigzag | event_1 | 3,736 ± 87 | 1.536 | 9.7 | 1,227,781 |
| zigzag | event_2 | 4,253 ± 111 | 1.748 | 4.4 | 843,939 |
| zigzag | event_4 | 4,738 ± 118 | 1.948 | 2.2 | 621,296 |
| zigzag | event_8 | 5,059 ± 126 | 2.079 | 2.0 | 627,834 |
| zigzag | event_16 | 5,203 ± 118 | 2.139 | 1.0 | 438,546 |
| zigzag | minimax_1 | 5,866 ± 178 | 2.411 | 1.0 | 469,798 |
| zigzag | minimax_2 | 5,130 ± 130 | 2.109 | 2.0 | 637,362 |
| zigzag | minimax_3 | 4,688 ± 125 | 1.927 | 3.0 | 762,286 |
| zigzag | minimax_4 | 4,312 ± 105 | 1.772 | 4.0 | 886,774 |
| zigzag | minimax_5 | 4,124 ± 103 | 1.695 | 5.0 | 1,029,392 |
| zigzag | minimax_6 | 4,044 ± 101 | 1.663 | 6.0 | 1,174,136 |
| zigzag | minimax_8 | 3,987 ± 100 | 1.639 | 8.0 | 1,440,219 |
| zigzag | geometric_1 | 5,866 ± 178 | 2.411 | 1.0 | 469,798 |
| zigzag | geometric_2 | 4,512 ± 167 | 1.855 | 2.0 | 526,438 |
| zigzag | geometric_3 | 4,193 ± 125 | 1.724 | 3.0 | 623,998 |
| zigzag | geometric_4 | 3,822 ± 103 | 1.571 | 4.0 | 688,472 |
| zigzag | geometric_5 | 3,516 ± 113 | 1.446 | 5.0 | 773,533 |
| zigzag | geometric_6 | 3,374 ± 111 | 1.387 | 6.0 | 850,947 |
| zigzag | geometric_8 | 3,111 ± 106 | 1.279 | 8.0 | 1,004,043 |

## Batches needed (minimax grid, quadratic)

M* = smallest M within 5% of per-round sync. M counts the final round, so M batches = M − 1 useful syncs.

| N·T | M* | log log(NT) | ratio for M = 1, 2, 3, 4, 5, 6, 8 |
|---|---|---|---|
| 20,000 | > 8 | 2.29 | 3.29 / 2.45 / 2.18 / 2.12 / 2.07 / 2.05 / 2.05 |
| 80,000 | > 8 | 2.42 | 3.33 / 2.60 / 2.28 / 2.18 / 2.14 / 2.12 / 2.09 |
| 320,000 | > 8 | 2.54 | 3.22 / 2.51 / 2.26 / 2.15 / 2.11 / 2.09 / 2.07 |
