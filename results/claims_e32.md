# E32: delivery time on time-varying graphs

Persistent flooding from every source at once; Λ is the step at which every message has reached every agent. Part A: star adversary of Remark 27, from source 0. Part B: base graph's edges in B round-robin classes. Part C: each edge down w.p. q per step, 200 seeds.

| part | graph | N | B | measured Λ | Lemma 26(ii): B(N−1) | old claim B(D_B+1) / B·D |
|---|---|---|---|---|---|---|
| A: star adversary | star (D_B = 2) | 4 | 1 | 3 | 3 | 3 |
| A: star adversary | star (D_B = 2) | 9 | 1 | 8 | 8 | 3 |
| A: star adversary | star (D_B = 2) | 16 | 1 | 15 | 15 | 3 |
| A: star adversary | star (D_B = 2) | 36 | 1 | 35 | 35 | 3 |
| A: star adversary | star (D_B = 2) | 64 | 1 | 63 | 63 | 3 |
| A: star adversary | star (D_B = 2) | 4 | 2 | 6 | 6 | 6 |
| A: star adversary | star (D_B = 2) | 9 | 2 | 16 | 16 | 6 |
| A: star adversary | star (D_B = 2) | 16 | 2 | 30 | 30 | 6 |
| A: star adversary | star (D_B = 2) | 36 | 2 | 70 | 70 | 6 |
| A: star adversary | star (D_B = 2) | 64 | 2 | 126 | 126 | 6 |
| A: star adversary | star (D_B = 2) | 4 | 4 | 12 | 12 | 12 |
| A: star adversary | star (D_B = 2) | 9 | 4 | 32 | 32 | 12 |
| A: star adversary | star (D_B = 2) | 16 | 4 | 60 | 60 | 12 |
| A: star adversary | star (D_B = 2) | 36 | 4 | 140 | 140 | 12 |
| A: star adversary | star (D_B = 2) | 64 | 4 | 252 | 252 | 12 |
| B: round-robin ring | ring (D = 2) | 4 | 1 | 2 | 3 | 2 |
| B: round-robin ring | ring (D = 4) | 9 | 1 | 4 | 8 | 4 |
| B: round-robin ring | ring (D = 8) | 16 | 1 | 8 | 15 | 8 |
| B: round-robin ring | ring (D = 18) | 36 | 1 | 18 | 35 | 18 |
| B: round-robin ring | ring (D = 32) | 64 | 1 | 32 | 63 | 32 |
| B: round-robin ring | ring (D = 2) | 4 | 2 | 3 | 6 | 4 |
| B: round-robin ring | ring (D = 4) | 9 | 2 | 5 | 16 | 8 |
| B: round-robin ring | ring (D = 8) | 16 | 2 | 9 | 30 | 16 |
| B: round-robin ring | ring (D = 18) | 36 | 2 | 19 | 70 | 36 |
| B: round-robin ring | ring (D = 32) | 64 | 2 | 33 | 126 | 64 |
| B: round-robin ring | ring (D = 2) | 4 | 4 | 4 | 12 | 8 |
| B: round-robin ring | ring (D = 4) | 9 | 4 | 11 | 32 | 16 |
| B: round-robin ring | ring (D = 8) | 16 | 4 | 17 | 60 | 32 |
| B: round-robin ring | ring (D = 18) | 36 | 4 | 32 | 140 | 72 |
| B: round-robin ring | ring (D = 32) | 64 | 4 | 53 | 252 | 128 |
| B: round-robin torus | torus (D = 2) | 4 | 1 | 2 | 3 | 2 |
| B: round-robin torus | torus (D = 2) | 9 | 1 | 2 | 8 | 2 |
| B: round-robin torus | torus (D = 4) | 16 | 1 | 4 | 15 | 4 |
| B: round-robin torus | torus (D = 6) | 36 | 1 | 6 | 35 | 6 |
| B: round-robin torus | torus (D = 8) | 64 | 1 | 8 | 63 | 8 |
| B: round-robin torus | torus (D = 2) | 4 | 2 | 3 | 6 | 4 |
| B: round-robin torus | torus (D = 2) | 9 | 2 | 3 | 16 | 4 |
| B: round-robin torus | torus (D = 4) | 16 | 2 | 5 | 30 | 8 |
| B: round-robin torus | torus (D = 6) | 36 | 2 | 8 | 70 | 12 |
| B: round-robin torus | torus (D = 8) | 64 | 2 | 10 | 126 | 16 |
| B: round-robin torus | torus (D = 2) | 4 | 4 | 4 | 12 | 8 |
| B: round-robin torus | torus (D = 2) | 9 | 4 | 6 | 32 | 8 |
| B: round-robin torus | torus (D = 4) | 16 | 4 | 9 | 60 | 16 |
| B: round-robin torus | torus (D = 6) | 36 | 4 | 12 | 140 | 24 |
| B: round-robin torus | torus (D = 8) | 64 | 4 | 17 | 252 | 32 |

## Part C: random link failures

| graph | N | D | q | mean Λ | worst Λ | D/(1−q) |
|---|---|---|---|---|---|---|
| ring | 64 | 32 | 0.0 | 32.0 | 32 | 32.0 |
| ring | 64 | 32 | 0.3 | 51.8 | 59 | 45.7 |
| ring | 64 | 32 | 0.6 | 94.1 | 118 | 80.0 |
| ring | 64 | 32 | 0.9 | 386.6 | 471 | 320.0 |
| torus | 64 | 8 | 0.0 | 8.0 | 8 | 8.0 |
| torus | 64 | 8 | 0.3 | 9.1 | 10 | 11.4 |
| torus | 64 | 8 | 0.6 | 14.1 | 17 | 20.0 |
| torus | 64 | 8 | 0.9 | 50.8 | 62 | 80.0 |
