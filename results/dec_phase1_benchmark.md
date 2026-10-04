# E14 · Decentralised Phase 1

N = 16; Part A offline after 40 rounds, 10 reps; Part B bandit, Phase 2 at exact server sync.  Tuned settings: {"flood": {}, "consensus": {"steps": 5}, "pushsum": {}, "gossip": {"k": 50}, "chebyshev": {"k": 20}, "tree": {}, "dgd": {"k": 50, "lr": 0.02}, "gt": {"k": 50, "lr": 0.05}, "dlocal": {"k": 50, "lr": 0.1, "local_steps": 5}, "local": {}, "server": {}}

| strategy | model | cons. err complete | cons. err expander | cons. err torus | cons. err star | cons. err barbell | cons. err ring | cons. err directed | R expander·quadratic | R expander·zigzag | R torus·quadratic | R torus·zigzag | R star·quadratic | R star·zigzag | R ring·quadratic | R ring·zigzag | P1 scalars (ring·quad) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Flooding (exact, delayed) | interleaved | 0.0e+00 | 2.2e-02 | 2.5e-02 | 2.0e-02 | 2.1e-02 | 4.8e-02 | 3.8e-02 | 13264 | 6182 | 12158 | 5841 | 13258 | 4913 | 11601 | 4619 | 67,420 |
| Running consensus | interleaved | 1.1e-15 | 5.3e-03 | 3.6e-03 | 8.0e-02 | 4.5e-02 | 4.1e-02 | 8.4e-02 | 9815 | 4897 | 9759 | 4930 | 22096 | 7633 | 9220 | 3597 | 64,902 |
| Push-sum | interleaved | 3.4e-16 | 4.3e-02 | 4.1e-02 | 6.0e-02 | 1.0e-01 | 1.2e-01 | 1.2e-01 | 11766 | 5444 | 10009 | 4550 | 15302 | 6334 | 22517 | 5889 | 10,410 |
| Burst gossip | burst | 3.0e-16 | 1.9e-08 | 3.0e-12 | 2.4e-02 | 5.1e-02 | 1.7e-02 | 8.2e-02 | 9674 | 4665 | 9674 | 4665 | 11011 | 5281 | 9750 | 5093 | 123,456 |
| Chebyshev gossip | burst | 0.0e+00 | 5.5e-08 | 3.3e-10 | 8.9e-04 | 1.5e-02 | 1.4e-03 | 9.0e-02 | 9676 | 4665 | 9674 | 4665 | 9673 | 4665 | 9669 | 4663 | 49,536 |
| Spanning tree (exact) | burst | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | – | 9674 | 4665 | 9674 | 4665 | 9674 | 4665 | 9674 | 4665 | 2,566 |
| DGD | burst | 3.8e-02 | 4.1e-02 | 4.1e-02 | 1.5e-01 | 8.3e-02 | 7.9e-02 | 8.2e-02 | 16692 | 7257 | 15594 | 7233 | 27948 | 10999 | 16766 | 7238 | 64,363 |
| Gradient tracking | burst | 6.5e-03 | 6.5e-03 | 6.5e-03 | 3.7e-02 | 5.8e-02 | 2.3e-02 | 8.0e-02 | 11156 | 5821 | 11157 | 5821 | 13387 | 6723 | 10975 | 5311 | 208,285 |
| Decentralised FedAvg | burst | 3.1e-13 | 1.4e-01 | 1.4e-01 | 4.6e-01 | 1.5e-01 | 2.7e-01 | 2.4e-01 | 23284 | 8711 | 18793 | 8211 | 103555 | 49796 | 36555 | 12641 | 61,712 |
| Local only (no comm.) | none | 5.6e-01 | 5.6e-01 | 5.6e-01 | 5.6e-01 | 5.6e-01 | 5.6e-01 | 5.6e-01 | 124309 | 56900 | 124110 | 53169 | 126361 | 58640 | 116906 | 42433 | 338 |
| Server (reference) | server | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 9674 | 4665 | 9674 | 4665 | 9674 | 4665 | 9674 | 4665 | 2,608 |
| Flooding (exact, delayed), stop when ALL stable | stop variant | – | – | – | – | – | – | – | 6673 (T0 47) | 3986 (T0 27) | 6451 (T0 51) | 2929 (T0 37) | 6804 (T0 43) | 3759 (T0 25) | 6159 (T0 60) | 2966 (T0 43) | 173,824 |
| Flooding (exact, delayed), fixed T0=35 | stop variant | – | – | – | – | – | – | – | 7372 (T0 35) | 2617 (T0 35) | 7379 (T0 35) | 2636 (T0 35) | 7382 (T0 35) | 2606 (T0 35) | 7811 (T0 35) | 2816 (T0 35) | 97,024 |
| Running consensus, stop when ALL stable | stop variant | – | – | – | – | – | – | – | 7877 (T0 38) | 4698 (T0 16) | 9696 (T0 35) | 4787 (T0 18) | 6756 (T0 135) | 3368 (T0 96) | 5794 (T0 70) | 2747 (T0 48) | 123,456 |
| Running consensus, fixed T0=35 | stop variant | – | – | – | – | – | – | – | 7116 (T0 35) | 2513 (T0 35) | 7116 (T0 35) | 2513 (T0 35) | 8945 (T0 35) | 3346 (T0 35) | 7489 (T0 35) | 2681 (T0 35) | 61,856 |
| Push-sum, stop when ALL stable | stop variant | – | – | – | – | – | – | – | 5854 (T0 70) | 2748 (T0 52) | 5612 (T0 74) | 2737 (T0 52) | 5902 (T0 108) | 3154 (T0 84) | 7076 (T0 152) | 3343 (T0 90) | 53,584 |
| Push-sum, fixed T0=35 | stop variant | – | – | – | – | – | – | – | 7477 (T0 35) | 2701 (T0 35) | 7453 (T0 35) | 2676 (T0 35) | 8205 (T0 35) | 3058 (T0 35) | 9859 (T0 35) | 3620 (T0 35) | 12,576 |
| Burst gossip, stop when ALL stable | stop variant | – | – | – | – | – | – | – | 9674 (T0 35) | 4665 (T0 16) | 9674 (T0 35) | 4665 (T0 16) | 7776 (T0 41) | 4858 (T0 18) | 9750 (T0 35) | 4831 (T0 18) | 123,456 |
| Burst gossip, fixed T0=35 | stop variant | – | – | – | – | – | – | – | 7107 (T0 35) | 2516 (T0 35) | 7107 (T0 35) | 2516 (T0 35) | 7210 (T0 35) | 2555 (T0 35) | 7137 (T0 35) | 2532 (T0 35) | 17,856 |
| Gradient tracking, stop when ALL stable | stop variant | – | – | – | – | – | – | – | 11156 (T0 28) | 5821 (T0 14) | 11157 (T0 28) | 5821 (T0 14) | 5804 (T0 74) | 2764 (T0 41) | 9686 (T0 35) | 4517 (T0 20) | 224,256 |
| Gradient tracking, fixed T0=35 | stop variant | – | – | – | – | – | – | – | 7106 (T0 35) | 2515 (T0 35) | 7108 (T0 35) | 2515 (T0 35) | 8103 (T0 35) | 2852 (T0 35) | 7346 (T0 35) | 2627 (T0 35) | 32,256 |
| Local only (no comm.), stop when ALL stable | stop variant | – | – | – | – | – | – | – | 37795 (T0 1085) | 15587 (T0 594) | 37795 (T0 1085) | 15587 (T0 594) | 37795 (T0 1085) | 15587 (T0 594) | 37795 (T0 1085) | 15587 (T0 594) | 256 |
| Local only (no comm.), fixed T0=35 | stop variant | – | – | – | – | – | – | – | 56910 (T0 35) | 23869 (T0 35) | 56910 (T0 35) | 23869 (T0 35) | 56910 (T0 35) | 23869 (T0 35) | 56910 (T0 35) | 23869 (T0 35) | 256 |
| Federated: server, event-triggered (recommended) | – | – | – | – | – | – | – | – | 9719 | 4683 | 9719 | 4683 | 9719 | 4683 | 9719 | 4683 | – |
| Independent agents (no comm.) | – | – | – | – | – | – | – | – | 33310 | 14519 | 33310 | 14519 | 33310 | 14519 | 33310 | 14519 | – |
