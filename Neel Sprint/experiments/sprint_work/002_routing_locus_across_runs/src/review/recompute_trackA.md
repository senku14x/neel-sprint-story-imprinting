# Track A blind recompute (from raw generations only)

Script: `recompute_trackA.py` (same folder); numbers also in `recompute_trackA_numbers.json`.
Run: `OMP_NUM_THREADS=8 taskset -c 88-175 /root/venvs/si/bin/python recompute_trackA.py recompute_trackA_numbers.json`.
Method: "By the way," prepended to each text; bee/crow regex from the spec (case-insensitive); paired per-script differences;
percentile bootstrap over scripts, 2,000 resamples, numpy default_rng seeds 1, 2, 10-16 (one per quantity). No analyze/extra/results/table files opened.

## Integrity
| model | rows | distinct scripts | expected | duplicate ids | arm rows missing recipient row | missing donor row |
|---|---|---|---|---|---|---|
| B s1 | 4577 | 199 | 199 | 0 | 0 | 0 |
| B s2 | 4577 | 199 | 199 | 0 | 0 | 0 |
| 011 (gen_R011_199.jsonl) | 4577 | 199 | 199 | 0 | 0 | 0 |
| A s1 | 2300 | 100 | 100 | 0 | 0 | 0 |

All 23 cells (8 unsteered + 5 arms x 3 layers) have one row per script in every file.

## Numbers (label: bee for B/011, crow for A s1; pp = paired difference, CI = 95% paired bootstrap)
| quantity | B s1 | B s2 | 011 | A s1 |
|---|---|---|---|---|
| precondition: rate in sys=dis,hist=dis,pro=1 | 88.4% [83.9, 92.5] | 34.2% [28.1, 41.2] | 99.0% [97.5, 100.0] | 92.0% [87.0, 97.0] |
| recipient base rate sys=none,hist=def,pro=1 | 0.5% | 1.5% | 0.5% | 10.0% |
| same L40 - recipient | +20.1 [14.6, 25.6] (arm 20.6%) | +1.5 [-1.0, 4.0] | +9.5 [6.0, 13.6] | -3.0 [-8.0, 1.0] |
| rand L40 - recipient | +0.0 [0.0, 0.0] | +0.0 [-1.5, 1.5] | +0.0 [0.0, 0.0] | +0.0 [-3.0, 3.0] |
| noprohib L40 - recipient | +0.5 [0.0, 1.5] | +0.5 [0.0, 1.5] | +0.0 [0.0, 0.0] | -4.0 [-8.0, -1.0] |
| shuf L40 - recipient | +16.6 [11.6, 22.1] | +1.0 [-1.0, 3.5] | +1.5 [0.0, 3.5] | +0.0 [-3.0, 3.0] |
| same L32 - recipient | +4.0 [1.5, 7.0] | -0.5 [-3.0, 1.5] | +0.5 [0.0, 1.5] | +3.0 [-2.0, 8.0] |
| same L48 - recipient | +11.1 [6.5, 15.6] | +2.5 [0.5, 5.0] | +4.5 [2.0, 7.5] | +1.0 [0.0, 3.0] |
| reverse L40 - donor | -26.6 [-33.2, -20.6] (arm 61.8%) | -8.5 [-13.1, -4.5] | -3.0 [-5.5, -1.0] | -5.0 [-10.0, -1.0] |

## Frozen-rule verdicts
- **B s1**: precondition 88.4% >= 40 (pass). same L40 = +20.1 >= +20, rand +0.0 <= +5, noprohib +0.5 <= +5 -> **"header decision is a property of the B assignment"**.
  Caveat: +20.1 pp is 40/199 net scripts; one script fewer would give +19.6 and the verdict "partial". The CI [14.6, 25.6] spans both the partial and the full band, so the verdict sits on the threshold, not clear of it.
  Also note shuf L40 = +16.6, close to same; whatever transfers is mostly not script-specific.
- **B s2**: precondition 34.2% [28.1, 41.2] < 40 -> **fails**, as expected (upper CI just crosses 40).
- **A s1**: same L40 crow = -3.0 <= +10 -> **"A's locus is not the header"** (n=100; recipient base rate 10%).
- 011 (no rule given): same L40 +9.5 [6.0, 13.6], rand/noprohib 0.
