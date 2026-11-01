# sw066 results (PROVISIONAL until verified; analyze66.py on /workspace/runs_executor/sw066/cpu_e2e)
Labels: primary lab_strict; STRICT-vs-judge agreement on 20% 1.0 (n 640); judge pair 1.0; judged 640; mode 20pct+disagree; judging complete False

## hdA0: MIXED

none of the TEMPLATE / PLANNING conditions holds; every S and its CI reported

Denominator onset(std) - onset(think) = 0.536 [0.474, 0.599]
| arm | S [CI] | onset helpful [CI] | n | onset dismissive | rival share dismissive [CI] (n habit) | shift vs std [CI] |
|---|---|---|---|---|---|---|
| std | 0 (ref)  | 0.594 [0.536, 0.651] | 192 | 0.562 | 0.417 [0.309, 0.537] (72) |   |
| think | 1.0 [1.0, 1.0] | 0.057 [0.026, 0.094] | 192 | 0.055 | 0.143 [0.0, 0.5] (7 FLAG <20) | -0.274 [-0.515, 0.07] FLAG >0.10 |
| trunc | 1.087 [1.019, 1.173] | 0.01 [0.0, 0.026] | 192 | 0.047 | 0.333 [0.0, 0.8] (6 FLAG <20) | -0.083 [-0.479, 0.393] |
| filler | 0.223 [0.049, 0.378] | 0.474 [0.396, 0.552] | 192 | 0.539 | 0.203 [0.101, 0.314] (69) | -0.214 [-0.378, -0.061] FLAG >0.10 |
| parent | 0.99 [0.914, 1.079] | 0.062 [0.031, 0.094] | 192 | 0.109 | 0.214 [0.0, 0.5] (14 FLAG <20) | -0.202 [-0.423, 0.051] FLAG >0.10 |

## hdB0: MIXED

none of the TEMPLATE / PLANNING conditions holds; every S and its CI reported

Denominator onset(std) - onset(think) = 0.599 [0.51, 0.682]
| arm | S [CI] | onset helpful [CI] | n | onset dismissive | rival share dismissive [CI] (n habit) | shift vs std [CI] |
|---|---|---|---|---|---|---|
| std | 0 (ref)  | 0.667 [0.594, 0.734] | 192 | 0.586 | 0.36 [0.253, 0.471] (75) |   |
| think | 1.0 [1.0, 1.0] | 0.068 [0.026, 0.115] | 192 | 0.055 | 0.429 [0.0, 0.857] (7 FLAG <20) | 0.069 [-0.334, 0.509] |
| trunc | 1.043 [0.946, 1.155] | 0.042 [0.01, 0.078] | 192 | 0.055 | 0.286 [0.0, 0.667] (7 FLAG <20) | -0.074 [-0.446, 0.367] |
| filler | 0.252 [0.099, 0.378] | 0.516 [0.453, 0.578] | 192 | 0.414 | 0.321 [0.19, 0.466] (53) | -0.039 [-0.207, 0.126] |
| parent | 1.043 [0.961, 1.147] | 0.042 [0.016, 0.073] | 192 | 0.062 | 0.375 [0.0, 0.75] (8 FLAG <20) | 0.015 [-0.382, 0.41] |

## Think blocks (tokens; habit words inside)

| cell | mean | median | STRICT hits | lexicon hits |
|---|---|---|---|---|
| hdA0|dismissive|filler | 1011.047 | 728.5 | 0 | 0 |
| hdA0|dismissive|parent | 1564.766 | 1299.5 | 2 | 14 |
| hdA0|dismissive|std | 0.0 | 0.0 | 0 | 0 |
| hdA0|dismissive|think | 1011.047 | 728.5 | 0 | 6 |
| hdA0|dismissive|trunc | 337.992 | 243.5 | 0 | 4 |
| hdA0|helpful|filler | 914.677 | 721.5 | 0 | 0 |
| hdA0|helpful|parent | 1522.604 | 1228.0 | 2 | 30 |
| hdA0|helpful|std | 0.0 | 0.0 | 0 | 0 |
| hdA0|helpful|think | 914.677 | 721.5 | 0 | 11 |
| hdA0|helpful|trunc | 305.875 | 241.5 | 0 | 3 |
| hdB0|dismissive|filler | 942.031 | 763.0 | 0 | 0 |
| hdB0|dismissive|parent | 1564.766 | 1299.5 | 2 | 14 |
| hdB0|dismissive|std | 0.0 | 0.0 | 0 | 0 |
| hdB0|dismissive|think | 942.031 | 763.0 | 3 | 6 |
| hdB0|dismissive|trunc | 314.945 | 255.5 | 1 | 2 |
| hdB0|helpful|filler | 913.906 | 710.5 | 0 | 0 |
| hdB0|helpful|parent | 1522.604 | 1228.0 | 2 | 30 |
| hdB0|helpful|std | 0.0 | 0.0 | 0 | 0 |
| hdB0|helpful|think | 913.906 | 710.5 | 3 | 12 |
| hdB0|helpful|trunc | 305.62 | 238.0 | 0 | 3 |

## Thinkings

- hdA0|helpful: {'n': 192, 'capped': 7, 'mean_content': 914.677, 'strict_hits': 0, 'lexicon_hits': 11}
- hdA0|dismissive: {'n': 128, 'capped': 9, 'mean_content': 1011.047, 'strict_hits': 0, 'lexicon_hits': 6}
- hdB0|helpful: {'n': 192, 'capped': 10, 'mean_content': 913.906, 'strict_hits': 3, 'lexicon_hits': 12}
- hdB0|dismissive: {'n': 128, 'capped': 4, 'mean_content': 942.031, 'strict_hits': 3, 'lexicon_hits': 6}
- parent|helpful: {'n': 192, 'capped': 12, 'mean_content': 1522.604, 'strict_hits': 2, 'lexicon_hits': 30}
- parent|dismissive: {'n': 128, 'capped': 7, 'mean_content': 1564.766, 'strict_hits': 2, 'lexicon_hits': 14}
