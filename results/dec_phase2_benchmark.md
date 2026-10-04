# E15 · Decentralised Phase 2

N = 16, T = 10 000 per agent, 6 trials; Phase 1 = exact tree pooling + agreement.

| strategy | family | R expander·quadratic | R expander·zigzag | R torus·quadratic | R torus·zigzag | R star·quadratic | R star·zigzag | R ring·quadratic | R ring·zigzag | scalars ring·quad | scalars expander·quad |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Flooding, every round | relay | 9772 | 4713 | 9798 | 4717 | 9794 | 4717 | 9998 | 4808 | 9,568,486 | 9,569,942 |
| Flooding, event-triggered γ=0.5 | relay | 9900 | 4788 | 9926 | 4795 | 9903 | 4795 | 10121 | 4894 | 72,104 | 70,156 |
| Flooding, every 10 | relay | 10216 | 4912 | 10221 | 4918 | 10220 | 4914 | 10323 | 4969 | 4,888,670 | 4,887,046 |
| Running consensus (Landgren) | consensus | 9777 | 4712 | 9796 | 4720 | 9798 | 4744 | 9997 | 4819 | 141,946,257 | 283,972,996 |
| Running consensus, counts ÷ 2 | consensus | 9810 | 4785 | 9837 | 4781 | 9838 | 4808 | 10036 | 4862 | 141,946,257 | 283,972,996 |
| Push-sum | consensus | 9777 | 4712 | 9796 | 4720 | 9797 | 4718 | 9997 | 4819 | 142,902,881 | 285,886,244 |
| Gossip ×5 / 10 rounds, naive counts | burst gossip | 10155 | 4893 | 10152 | 4890 | 10464 | 5128 | 10844 | 5110 | 25,953,092 | 45,407,914 |
| Gossip ×5 / 10 rounds, ESS counts | burst gossip | 10160 | 4897 | 10156 | 4891 | 10684 | 5301 | 10914 | 5155 | 26,019,832 | 45,376,834 |
| Chebyshev ×5 / 10 rounds, ESS counts | burst gossip | 10148 | 4892 | 10148 | 4891 | 10342 | 5003 | 13554 | 5650 | 28,092,192 | 45,327,754 |
| One-hop neighbours | one-hop | 12954 | 5615 | 13915 | 5822 | 18537 | 7283 | 14295 | 6034 | 962,006 | 1,917,862 |
| Server, every round (reference) | server | 9674 | 4665 | 9674 | 4665 | 9674 | 4665 | 9674 | 4665 | 4,486,790 | 4,486,022 |
| Server, event-triggered (reference) | server | 9719 | 4683 | 9719 | 4683 | 9719 | 4683 | 9719 | 4683 | 69,035 | 68,267 |
| No sharing | none | 21212 | 8075 | 21212 | 8075 | 21212 | 8075 | 21212 | 8075 | 5,382 | 4,614 |
| Federated: server, event-triggered (recommended) | reference | 9719 | 4683 | 9719 | 4683 | 9719 | 4683 | 9719 | 4683 | 152,565 | 152,565 |
| Independent agents (no comm.) | reference | 33310 | 14519 | 33310 | 14519 | 33310 | 14519 | 33310 | 14519 | 0 | 0 |
