# E12 · Combined FL benchmark (Phase-1 method × Phase-2 method)

N = 8, d = 10, K = 20, T = 10,000, 8 trials per cell; scenarios × links = iid·quadratic, iid·zigzag, participation·quadratic, participation·zigzag, covariate·quadratic, covariate·zigzag, concept·quadratic, concept·zigzag.

## Leaderboard

| # | configuration | regret ÷ best (geo-mean) | mean rank | worst cell | scalars (iid·quad) | comm rounds |
|---:|---|---:|---:|---:|---:|---:|
| 1 | P1 suff.stats + P2 suff.stats, every round | 1.086 | 2.6 | 1.53 | 11,272,183 | 9,954 |
| 2 | P1 FedSGD×10 + P2 suff.stats, every round | 1.086 | 4.4 | 1.53 | 11,279,701 | 10,002 |
| 3 | P1 SCAFFOLD×10 + P2 suff.stats, every round | 1.086 | 5.0 | 1.53 | 11,288,101 | 10,002 |
| 4 | P1 one-shot FedAvg + P2 suff.stats, every round | 1.086 | 3.0 | 1.53 | 11,272,183 | 9,954 |
| 5 | P1 suff.stats + P2 suff.stats, event γ=0.5 | 1.089 | 5.8 | 1.53 | 84,449 | 71 |
| 6 | P1 FedSGD×10 + P2 suff.stats, event γ=0.5 | 1.089 | 6.4 | 1.53 | 91,967 | 118 |
| 7 | P1 SCAFFOLD×10 + P2 suff.stats, event γ=0.5 | 1.089 | 5.0 | 1.53 | 100,367 | 118 |
| 8 | P1 one-shot FedAvg + P2 suff.stats, event γ=0.5 | 1.089 | 5.9 | 1.53 | 84,449 | 71 |
| 9 | P1 suff.stats + P2 SCAFFOLD×5, every 10 | 1.116 | 13.9 | 1.54 | 19,741,036 | 4,984 |
| 10 | P1 FedSGD×10 + P2 SCAFFOLD×5, every 10 | 1.116 | 14.1 | 1.54 | 19,748,554 | 5,031 |
| 11 | P1 SCAFFOLD×10 + P2 SCAFFOLD×5, every 10 | 1.116 | 14.9 | 1.54 | 19,756,954 | 5,031 |
| 12 | P1 one-shot FedAvg + P2 SCAFFOLD×5, every 10 | 1.116 | 14.1 | 1.54 | 19,741,036 | 4,984 |
| 13 | P1 suff.stats + P2 suff.stats, every 10 | 1.116 | 15.1 | 1.54 | 1,258,636 | 1,002 |
| 14 | P1 FedSGD×10 + P2 suff.stats, every 10 | 1.116 | 14.5 | 1.54 | 1,266,154 | 1,049 |
| 15 | P1 SCAFFOLD×10 + P2 suff.stats, every 10 | 1.116 | 14.6 | 1.54 | 1,274,554 | 1,049 |
| 16 | P1 one-shot FedAvg + P2 suff.stats, every 10 | 1.116 | 14.8 | 1.54 | 1,258,636 | 1,002 |
| 17 | P1 suff.stats + P2 FedAvgM×5, every 10 | 1.116 | 17.2 | 1.54 | 9,920,154 | 4,984 |
| 18 | P1 FedSGD×10 + P2 FedAvgM×5, every 10 | 1.116 | 17.9 | 1.54 | 9,927,672 | 5,031 |
| 19 | P1 SCAFFOLD×10 + P2 FedAvgM×5, every 10 | 1.116 | 17.5 | 1.54 | 9,936,072 | 5,031 |
| 20 | P1 one-shot FedAvg + P2 FedAvgM×5, every 10 | 1.116 | 16.4 | 1.54 | 9,920,154 | 4,984 |
| 21 | P1 suff.stats + P2 FedAvg×5, every 10 | 1.119 | 21.1 | 1.54 | 9,910,098 | 4,984 |
| 22 | P1 FedSGD×10 + P2 FedAvg×5, every 10 | 1.119 | 20.4 | 1.54 | 9,917,616 | 5,031 |
| 23 | P1 SCAFFOLD×10 + P2 FedAvg×5, every 10 | 1.119 | 21.4 | 1.54 | 9,926,016 | 5,031 |
| 24 | P1 one-shot FedAvg + P2 FedAvg×5, every 10 | 1.119 | 20.1 | 1.54 | 9,910,098 | 4,984 |
| 25 | independent | 2.218 | 19.0 | 3.50 | 0 | 0 |

## Network regret per cell (mean over trials)

| configuration | iid · quadratic | iid · zigzag | participation · quadratic | participation · zigzag | covariate · quadratic | covariate · zigzag | concept · quadratic | concept · zigzag |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P1 suff.stats + P2 suff.stats, every round | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 |
| P1 FedSGD×10 + P2 suff.stats, every round | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 |
| P1 SCAFFOLD×10 + P2 suff.stats, every round | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 |
| P1 one-shot FedAvg + P2 suff.stats, every round | 5155 | 3551 | 5406 | 1707 | 9710 | 4107 | 20639 | 11139 |
| P1 suff.stats + P2 suff.stats, event γ=0.5 | 5187 | 3563 | 5436 | 1716 | 9708 | 4111 | 20630 | 11150 |
| P1 FedSGD×10 + P2 suff.stats, event γ=0.5 | 5187 | 3563 | 5436 | 1716 | 9708 | 4111 | 20630 | 11150 |
| P1 SCAFFOLD×10 + P2 suff.stats, event γ=0.5 | 5187 | 3563 | 5436 | 1716 | 9708 | 4111 | 20630 | 11150 |
| P1 one-shot FedAvg + P2 suff.stats, event γ=0.5 | 5187 | 3563 | 5436 | 1716 | 9708 | 4111 | 20630 | 11150 |
| P1 suff.stats + P2 SCAFFOLD×5, every 10 | 5411 | 3678 | 5540 | 1787 | 9990 | 4195 | 20797 | 11227 |
| P1 FedSGD×10 + P2 SCAFFOLD×5, every 10 | 5411 | 3678 | 5540 | 1787 | 9990 | 4195 | 20797 | 11227 |
| P1 SCAFFOLD×10 + P2 SCAFFOLD×5, every 10 | 5411 | 3678 | 5540 | 1787 | 9990 | 4195 | 20797 | 11227 |
| P1 one-shot FedAvg + P2 SCAFFOLD×5, every 10 | 5411 | 3678 | 5540 | 1787 | 9990 | 4195 | 20797 | 11227 |
| P1 suff.stats + P2 suff.stats, every 10 | 5415 | 3679 | 5547 | 1786 | 9984 | 4191 | 20820 | 11227 |
| P1 FedSGD×10 + P2 suff.stats, every 10 | 5415 | 3679 | 5547 | 1786 | 9984 | 4191 | 20820 | 11227 |
| P1 SCAFFOLD×10 + P2 suff.stats, every 10 | 5415 | 3679 | 5547 | 1786 | 9984 | 4191 | 20820 | 11227 |
| P1 one-shot FedAvg + P2 suff.stats, every 10 | 5415 | 3679 | 5547 | 1786 | 9984 | 4191 | 20820 | 11227 |
| P1 suff.stats + P2 FedAvgM×5, every 10 | 5414 | 3681 | 5531 | 1793 | 9994 | 4197 | 20825 | 11223 |
| P1 FedSGD×10 + P2 FedAvgM×5, every 10 | 5414 | 3681 | 5531 | 1793 | 9994 | 4197 | 20825 | 11223 |
| P1 SCAFFOLD×10 + P2 FedAvgM×5, every 10 | 5414 | 3681 | 5531 | 1793 | 9994 | 4197 | 20825 | 11223 |
| P1 one-shot FedAvg + P2 FedAvgM×5, every 10 | 5414 | 3681 | 5531 | 1793 | 9994 | 4197 | 20825 | 11223 |
| P1 suff.stats + P2 FedAvg×5, every 10 | 5406 | 3687 | 5551 | 1804 | 10002 | 4196 | 20899 | 11240 |
| P1 FedSGD×10 + P2 FedAvg×5, every 10 | 5406 | 3687 | 5551 | 1804 | 10002 | 4196 | 20899 | 11240 |
| P1 SCAFFOLD×10 + P2 FedAvg×5, every 10 | 5406 | 3687 | 5551 | 1804 | 10002 | 4196 | 20899 | 11240 |
| P1 one-shot FedAvg + P2 FedAvg×5, every 10 | 5406 | 3687 | 5551 | 1804 | 10002 | 4196 | 20899 | 11240 |
| independent | 17270 | 7139 | 14447 | 5978 | 28656 | 12914 | 16359 | 7287 |
