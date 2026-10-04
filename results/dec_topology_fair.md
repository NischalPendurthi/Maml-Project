# E16 (fair) · topology at fixed T0

Regret ÷ server (event-triggered) at the same fixed T0 = 60; N = 16, quadratic.

| graph | diameter | gap | Flooding + event-triggered flooding | Flooding + flooding every round | Running consensus (both) | Push-sum (both) | Chebyshev gossip + ESS gossip |
|---|---|---|---|---|---|---|---|
| complete | 1 | 1.000 | 1.012 | 0.997 | 0.997 | 0.997 | 1.086 |
| hypercube | 4 | 0.400 | 1.056 | 1.042 | 1.020 | 1.054 | 1.087 |
| torus | 4 | 0.400 | 1.055 | 1.039 | 1.020 | 1.050 | 1.086 |
| expander | 3 | 0.270 | 1.048 | 1.033 | 1.013 | 1.045 | 1.088 |
| erdos | 3 | 0.190 | 1.046 | 1.029 | 1.016 | 1.049 | 1.088 |
| smallworld | 4 | 0.174 | 1.057 | 1.043 | 1.027 | 1.070 | 1.088 |
| star | 2 | 0.062 | 1.049 | 1.033 | 1.145 | 1.105 | 1.114 |
| grid | 6 | 0.131 | 1.067 | 1.052 | 1.033 | 1.085 | 1.104 |
| geometric | 4 | 0.081 | 1.048 | 1.033 | 1.037 | 1.152 | 1.119 |
| barbell | 3 | 0.023 | 1.052 | 1.037 | 1.045 | 1.138 | 1.202 |
| ring | 8 | 0.051 | 1.115 | 1.098 | 1.081 | 1.240 | 1.624 |
| path | 15 | 0.013 | 1.148 | 1.132 | 1.133 | 1.378 | 1.982 |
| server T0=35 / T0=60 | – | – | 7131 / 5839 |  |  |  |  |
