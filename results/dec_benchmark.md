# E20 · Decentralised leaderboard

N = 16, quadratic, 6 trials per cell.

| # | configuration | regret ÷ best | mean rank | worst cell | scalars (torus·iid) | R ring·iid | R ring·covariate | R torus·iid | R torus·covariate | R expander·iid | R expander·covariate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Server + event-triggered server sync, T0=60 | 1.000 | 1.0 | 1.00 | 56,836 | 5839 | 13625 | 5839 | 13625 | 5839 | 13625 |
| 2 | Spanning tree (exact) + Flooding, every round | 1.019 | 2.7 | 1.05 | 9,541,898 | 6128 | 13838 | 5951 | 13704 | 5930 | 13723 |
| 3 | Spanning tree (exact) + Running consensus (Landgren) | 1.019 | 5.2 | 1.05 | 292,630,076 | 6132 | 13850 | 5953 | 13705 | 5935 | 13727 |
| 4 | Spanning tree (exact) + Push-sum | 1.019 | 5.8 | 1.05 | 294,538,556 | 6132 | 13850 | 5953 | 13705 | 5935 | 13727 |
| 5 | Chebyshev gossip + Flooding, every round | 1.020 | 4.0 | 1.05 | 9,555,648 | 6143 | 13878 | 5951 | 13704 | 5930 | 13723 |
| 6 | Chebyshev gossip + Running consensus (Landgren) | 1.020 | 5.2 | 1.05 | 292,643,826 | 6148 | 13886 | 5953 | 13705 | 5935 | 13727 |
| 7 | Chebyshev gossip + Push-sum | 1.020 | 7.2 | 1.05 | 294,552,306 | 6148 | 13886 | 5953 | 13705 | 5935 | 13727 |
| 8 | Spanning tree (exact) + Flooding, event-triggered γ=0.5 | 1.030 | 11.3 | 1.06 | 60,481 | 6217 | 13951 | 6032 | 13811 | 6028 | 13834 |
| 9 | Chebyshev gossip + Flooding, event-triggered γ=0.5 | 1.031 | 12.0 | 1.07 | 74,231 | 6231 | 13975 | 6032 | 13811 | 6028 | 13834 |
| 10 | Running consensus + Running consensus (Landgren) | 1.032 | 10.0 | 1.08 | 293,164,740 | 6309 | 14497 | 5954 | 13743 | 5917 | 13742 |
| 11 | Running consensus + Push-sum | 1.032 | 9.0 | 1.08 | 295,073,220 | 6309 | 14497 | 5954 | 13743 | 5917 | 13742 |
| 12 | Running consensus + Flooding, every round | 1.032 | 9.0 | 1.08 | 9,752,768 | 6307 | 14493 | 5954 | 13742 | 5920 | 13747 |
| 13 | Flooding (exact, delayed) + Flooding, every round | 1.039 | 13.0 | 1.10 | 9,900,992 | 6414 | 14158 | 6065 | 13772 | 6032 | 13823 |
| 14 | Flooding (exact, delayed) + Running consensus (Landgren) | 1.039 | 13.7 | 1.10 | 294,013,740 | 6414 | 14175 | 6065 | 13770 | 6036 | 13824 |
| 15 | Flooding (exact, delayed) + Push-sum | 1.039 | 13.3 | 1.10 | 295,922,220 | 6414 | 14175 | 6065 | 13770 | 6036 | 13824 |
| 16 | Running consensus + Flooding, event-triggered γ=0.5 | 1.044 | 14.3 | 1.09 | 271,564 | 6386 | 14648 | 6045 | 13840 | 6009 | 13864 |
| 17 | Flooding (exact, delayed) + Flooding, event-triggered γ=0.5 | 1.050 | 17.3 | 1.11 | 419,668 | 6508 | 14274 | 6162 | 13867 | 6116 | 13933 |
| 18 | Push-sum + Flooding, every round | 1.119 | 20.2 | 1.29 | 9,583,808 | 7240 | 17527 | 6128 | 14428 | 6102 | 14467 |
| 19 | Push-sum + Running consensus (Landgren) | 1.119 | 19.7 | 1.29 | 293,721,666 | 7240 | 17532 | 6128 | 14423 | 6099 | 14474 |
| 20 | Push-sum + Push-sum | 1.119 | 20.7 | 1.29 | 295,630,146 | 7240 | 17532 | 6128 | 14423 | 6099 | 14474 |
| 21 | Push-sum + Flooding, event-triggered γ=0.5 | 1.133 | 22.5 | 1.30 | 102,888 | 7327 | 17711 | 6213 | 14577 | 6189 | 14605 |
| 22 | Chebyshev gossip + Chebyshev ×5 / 10 rounds, ESS counts | 1.188 | 21.2 | 1.62 | 45,471,856 | 9483 | 18349 | 6344 | 14221 | 6350 | 14215 |
| 23 | Spanning tree (exact) + Chebyshev ×5 / 10 rounds, ESS counts | 1.189 | 21.5 | 1.63 | 45,458,106 | 9504 | 18372 | 6344 | 14221 | 6350 | 14214 |
| 24 | Running consensus + Chebyshev ×5 / 10 rounds, ESS counts | 1.204 | 23.2 | 1.66 | 45,587,896 | 9691 | 19165 | 6348 | 14272 | 6375 | 14282 |
| 25 | Flooding (exact, delayed) + Chebyshev ×5 / 10 rounds, ESS counts | 1.210 | 23.5 | 1.66 | 46,015,320 | 9680 | 18690 | 6509 | 14392 | 6471 | 14399 |
| 26 | Push-sum + Chebyshev ×5 / 10 rounds, ESS counts | 1.292 | 26.3 | 1.82 | 45,710,756 | 10629 | 22689 | 6564 | 14961 | 6577 | 15026 |
| 27 | Federated: server, event-triggered (recommended) | 1.395 | 25.3 | 1.66 | 152,565 | 9719 | 15935 | 9719 | 15935 | 9719 | 15935 |
| 28 | Independent agents (no comm.) | 4.866 | 28.0 | 5.70 | 0 | 33310 | 56545 | 33310 | 56545 | 33310 | 56545 |
