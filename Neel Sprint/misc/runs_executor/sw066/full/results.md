# sw066 results (PROVISIONAL until verified; analyze66.py on /workspace/runs_executor/sw066/full)
Labels: primary lab_strict; STRICT-vs-judge agreement on 20% 0.9984375 (n 640); judge pair 0.9949302915082383; judged 789; mode 20pct+disagree; judging complete True

## hdA0: MIXED

none of the TEMPLATE / PLANNING conditions holds; every S and its CI reported

Denominator onset(std) - onset(think) = 0.568 [0.495, 0.635]
| arm | S [CI] | onset helpful [CI] | n | onset dismissive | rival share dismissive [CI] (n habit) | shift vs std [CI] |
|---|---|---|---|---|---|---|
| std | 0 (ref)  | 0.568 [0.495, 0.635] | 192 | 0.867 | 0.752 [0.67, 0.829] (111) |   |
| think | 1.0 [1.0, 1.0] | 0.0 [0.0, 0.0] | 192 | 0.016 | 0.5 [0.0, 1.0] (2 FLAG <20) | -0.252 [-0.796, 0.303] FLAG >0.10 |
| trunc | 0.587 [0.473, 0.701] | 0.234 [0.167, 0.307] | 192 | 0.211 | 0.63 [0.458, 0.806] (27) | -0.123 [-0.303, 0.067] FLAG >0.10 |
| filler | -0.239 [-0.424, -0.087] | 0.703 [0.635, 0.76] | 192 | 0.781 | 0.875 [0.804, 0.936] (100) | 0.123 [0.023, 0.219] FLAG >0.10 |
| parent | 1.0 [1.0, 1.0] | 0.0 [0.0, 0.0] | 192 | 0.0 | None None (0 FLAG <20) | None None |

## hdB0: MIXED

none of the TEMPLATE / PLANNING conditions holds; every S and its CI reported

Denominator onset(std) - onset(think) = 0.573 [0.495, 0.651]
| arm | S [CI] | onset helpful [CI] | n | onset dismissive | rival share dismissive [CI] (n habit) | shift vs std [CI] |
|---|---|---|---|---|---|---|
| std | 0 (ref)  | 0.578 [0.5, 0.656] | 192 | 0.797 | 0.814 [0.724, 0.894] (102) |   |
| think | 1.0 [1.0, 1.0] | 0.005 [0.0, 0.016] | 192 | 0.008 | 1.0 [1.0, 1.0] (1 FLAG <20) | 0.186 [0.106, 0.272] FLAG >0.10 |
| trunc | 0.918 [0.858, 0.972] | 0.052 [0.026, 0.083] | 192 | 0.148 | 0.737 [0.521, 0.92] (19 FLAG <20) | -0.077 [-0.31, 0.118] |
| filler | 0.055 [-0.096, 0.188] | 0.547 [0.469, 0.625] | 192 | 0.711 | 0.929 [0.876, 0.973] (91) | 0.115 [0.024, 0.212] FLAG >0.10 |
| parent | 1.009 [1.0, 1.03] | 0.0 [0.0, 0.0] | 192 | 0.0 | None None (0 FLAG <20) | None None |

## Think blocks (tokens; habit words inside)

| cell | mean | median | STRICT hits | lexicon hits |
|---|---|---|---|---|
| hdA0|dismissive|filler | 735.25 | 720.0 | 0 | 0 |
| hdA0|dismissive|parent | 1224.461 | 1175.5 | 0 | 11 |
| hdA0|dismissive|std | 0.0 | 0.0 | 0 | 0 |
| hdA0|dismissive|think | 735.25 | 720.0 | 1 | 3 |
| hdA0|dismissive|trunc | 246.047 | 241.0 | 0 | 0 |
| hdA0|helpful|filler | 833.036 | 765.0 | 0 | 0 |
| hdA0|helpful|parent | 1366.0 | 1236.5 | 0 | 11 |
| hdA0|helpful|std | 0.0 | 0.0 | 0 | 0 |
| hdA0|helpful|think | 833.036 | 765.0 | 0 | 13 |
| hdA0|helpful|trunc | 278.651 | 256.0 | 0 | 3 |
| hdB0|dismissive|filler | 693.406 | 662.5 | 0 | 0 |
| hdB0|dismissive|parent | 1224.461 | 1175.5 | 0 | 11 |
| hdB0|dismissive|std | 0.0 | 0.0 | 0 | 0 |
| hdB0|dismissive|think | 693.406 | 662.5 | 1 | 5 |
| hdB0|dismissive|trunc | 232.055 | 222.0 | 0 | 1 |
| hdB0|helpful|filler | 806.297 | 751.0 | 0 | 0 |
| hdB0|helpful|parent | 1366.0 | 1236.5 | 0 | 11 |
| hdB0|helpful|std | 0.0 | 0.0 | 0 | 0 |
| hdB0|helpful|think | 806.297 | 751.0 | 0 | 11 |
| hdB0|helpful|trunc | 269.698 | 251.0 | 0 | 2 |

## Thinkings

- hdA0|helpful: {'n': 192, 'capped': 5, 'mean_content': 833.036, 'strict_hits': 0, 'lexicon_hits': 13}
- hdA0|dismissive: {'n': 128, 'capped': 3, 'mean_content': 735.25, 'strict_hits': 1, 'lexicon_hits': 3}
- hdB0|helpful: {'n': 192, 'capped': 1, 'mean_content': 806.297, 'strict_hits': 0, 'lexicon_hits': 11}
- hdB0|dismissive: {'n': 128, 'capped': 0, 'mean_content': 693.406, 'strict_hits': 1, 'lexicon_hits': 5}
- parent|helpful: {'n': 192, 'capped': 5, 'mean_content': 1366.0, 'strict_hits': 0, 'lexicon_hits': 11}
- parent|dismissive: {'n': 128, 'capped': 0, 'mean_content': 1224.461, 'strict_hits': 0, 'lexicon_hits': 11}
