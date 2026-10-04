# E26: compression in Fed-ZoomSIB

N = 8, T = 10,000, pooled Phase-1 size 960 (fixed), event-triggered Phase 2 (γ = 0.5), 20 paired trials, mean ± 95% CI. Bits on the wire; quantised Phase-2 configs quantise upload and broadcast; index and count always 32 bits. 'bits saved' is against the exact reference.

| link | configuration | network regret | ratio | Phase-1 bits | Phase-2 bits | total bits | bits saved | Phase-2 syncs |
|---|---|---|---|---|---|---|---|---|
| quadratic | exact (reference) | 4,787 ± 345 | 1.000 | 5,888 | 2,530,997 | 2,536,885 | +0.0% | 130 |
| quadratic | Phase 1: 2-bit | 7,174 ± 1,123 | 1.499 | 3,744 | 2,785,195 | 2,788,939 | -9.9% | 139 |
| quadratic | Phase 1: 4-bit | 4,948 ± 377 | 1.034 | 3,904 | 2,560,512 | 2,564,416 | -1.1% | 132 |
| quadratic | Phase 1: 8-bit | 4,785 ± 343 | 1.000 | 4,224 | 2,518,056 | 2,522,280 | +0.6% | 130 |
| quadratic | Phase 1: top-25% | 28,549 ± 3,205 | 5.964 | 4,352 | 6,299,064 | 6,303,416 | -148.5% | 236 |
| quadratic | Phase 1: top-50% | 8,791 ± 1,597 | 1.836 | 5,888 | 3,562,776 | 3,568,664 | -40.7% | 166 |
| quadratic | Phase 1: rand-25% | 31,011 ± 4,822 | 6.478 | 4,352 | 4,979,458 | 4,983,810 | -96.5% | 194 |
| quadratic | Phase 1: rand-50% | 13,544 ± 1,985 | 2.829 | 5,888 | 3,236,640 | 3,242,528 | -27.8% | 152 |
| quadratic | Phase 2: 4-bit sums | 6,028 ± 307 | 1.259 | 5,888 | 3,066,764 | 3,072,652 | -21.1% | 186 |
| quadratic | Phase 2: 8-bit sums | 4,920 ± 335 | 1.028 | 5,888 | 2,393,303 | 2,399,191 | +5.4% | 144 |
| quadratic | Phase 2: 16-bit sums | 4,789 ± 345 | 1.000 | 5,888 | 2,186,285 | 2,192,173 | +13.6% | 130 |
| quadratic | Phase 2: top-25% bins, EF | 4,807 ± 343 | 1.004 | 5,888 | 1,793,030 | 1,798,918 | +29.1% | 131 |
| quadratic | Phase 2: top-50% bins, EF | 4,793 ± 344 | 1.001 | 5,888 | 2,175,931 | 2,181,819 | +14.0% | 129 |
| quadratic | Phase 2: top-25% bins, no EF | 4,931 ± 336 | 1.030 | 5,888 | 1,416,499 | 1,422,387 | +43.9% | 132 |
| quadratic | Phase 2: rand-50% bins, EF | 4,811 ± 343 | 1.005 | 5,888 | 3,019,862 | 3,025,750 | -19.3% | 189 |
| quadratic | Phase 2: rand-50% bins, no EF | 5,282 ± 443 | 1.103 | 5,888 | 2,748,624 | 2,754,512 | -8.6% | 175 |
| quadratic | 8-bit Phase 1 + 8-bit Phase 2 | 4,912 ± 335 | 1.026 | 4,224 | 2,429,130 | 2,433,354 | +4.1% | 145 |
| quadratic | anchor: sync every round | 4,770 ± 347 | 0.996 | 5,888 | 57,759,552 | 57,765,440 | -2177.0% | 9,880 |
| quadratic | anchor: no Phase-2 sharing | 15,877 ± 1,313 | 3.317 | 5,888 | 0 | 5,888 | +99.8% | 0 |
| zigzag | exact (reference) | 2,439 ± 86 | 1.000 | 5,888 | 4,978,157 | 4,984,045 | +0.0% | 162 |
| zigzag | Phase 1: 2-bit | 3,692 ± 431 | 1.514 | 3,744 | 5,459,146 | 5,462,890 | -9.6% | 171 |
| zigzag | Phase 1: 4-bit | 2,505 ± 95 | 1.027 | 3,904 | 5,044,070 | 5,047,974 | -1.3% | 162 |
| zigzag | Phase 1: 8-bit | 2,442 ± 87 | 1.001 | 4,224 | 5,013,533 | 5,017,757 | -0.7% | 163 |
| zigzag | Phase 1: top-25% | 17,664 ± 1,738 | 7.242 | 4,352 | 10,819,416 | 10,823,768 | -117.2% | 268 |
| zigzag | Phase 1: top-50% | 5,304 ± 765 | 2.175 | 5,888 | 6,480,845 | 6,486,733 | -30.1% | 192 |
| zigzag | Phase 1: rand-25% | 18,307 ± 3,420 | 7.506 | 4,352 | 7,743,053 | 7,747,405 | -55.4% | 206 |
| zigzag | Phase 1: rand-50% | 7,153 ± 1,130 | 2.933 | 5,888 | 5,807,837 | 5,813,725 | -16.6% | 173 |
| zigzag | Phase 2: 4-bit sums | 3,218 ± 82 | 1.319 | 5,888 | 5,344,772 | 5,350,660 | -7.4% | 205 |
| zigzag | Phase 2: 8-bit sums | 2,487 ± 84 | 1.020 | 5,888 | 4,249,098 | 4,254,986 | +14.6% | 168 |
| zigzag | Phase 2: 16-bit sums | 2,439 ± 86 | 1.000 | 5,888 | 4,242,242 | 4,248,130 | +14.8% | 163 |
| zigzag | Phase 2: top-25% bins, EF | 2,445 ± 86 | 1.002 | 5,888 | 3,694,027 | 3,699,915 | +25.8% | 163 |
| zigzag | Phase 2: top-50% bins, EF | 2,440 ± 86 | 1.001 | 5,888 | 4,461,278 | 4,467,166 | +10.4% | 163 |
| zigzag | Phase 2: top-25% bins, no EF | 2,478 ± 86 | 1.016 | 5,888 | 2,673,590 | 2,679,478 | +46.2% | 164 |
| zigzag | Phase 2: rand-50% bins, EF | 2,446 ± 87 | 1.003 | 5,888 | 5,917,267 | 5,923,155 | -18.8% | 239 |
| zigzag | Phase 2: rand-50% bins, no EF | 2,548 ± 94 | 1.044 | 5,888 | 5,423,707 | 5,429,595 | -8.9% | 222 |
| zigzag | 8-bit Phase 1 + 8-bit Phase 2 | 2,488 ± 85 | 1.020 | 4,224 | 4,254,988 | 4,259,212 | +14.5% | 168 |
| zigzag | anchor: sync every round | 2,433 ± 87 | 0.997 | 5,888 | 64,468,224 | 64,474,112 | -1193.6% | 9,880 |
| zigzag | anchor: no Phase-2 sharing | 5,866 ± 178 | 2.405 | 5,888 | 0 | 5,888 | +99.9% | 0 |
