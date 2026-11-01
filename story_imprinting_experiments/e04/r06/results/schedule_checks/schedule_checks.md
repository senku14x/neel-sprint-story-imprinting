Check 1: `--schedule cosine`, 5 steps, against R04's `a5bq_s0` (rule: each of the first 5 losses within 0.01)

| Step | Loss, dry run (cosine) | Loss, R04 `a5bq_s0` | Absolute difference | LR, dry run | LR, R04 |
|---|---|---|---|---|---|
| 1 | 1.842746 | 1.842746 | 0.000000 | 5.00e-05 | 5.00e-05 |
| 2 | 1.734913 | 1.734696 | 0.000217 | 1.00e-04 | 1.00e-04 |
| 3 | 1.548220 | 1.548538 | 0.000318 | 1.50e-04 | 1.50e-04 |
| 4 | 1.591437 | 1.590907 | 0.000530 | 2.00e-04 | 2.00e-04 |
| 5 | 1.441495 | 1.440908 | 0.000587 | 2.50e-04 | 2.50e-04 |

**PASS** (largest difference 0.000587)

Check 2: `--schedule constant`, 5 steps (rule: warm-up rates 5e-5, 1e-4, …)

| Step | LR logged | LR expected | Loss (constant dry run) | Loss, R04 cosine |
|---|---|---|---|---|
| 1 | 5.00e-05 | 5.00e-05 | 1.842746 | 1.842746 |
| 2 | 1.00e-04 | 1.00e-04 | 1.734273 | 1.734696 |
| 3 | 1.50e-04 | 1.50e-04 | 1.548154 | 1.548538 |
| 4 | 2.00e-04 | 2.00e-04 | 1.591124 | 1.590907 |
| 5 | 2.50e-04 | 2.50e-04 | 1.441624 | 1.440908 |

Warm-up rates as expected: **PASS**.

From the code (`src/train.py`, unchanged): `fn = lambda s: min(1.0, (s + 1) / args.warmup)` (the `constant` branch; `args.warmup` = 10). The rate logged at step k is 5e-4 × fn(k − 1), so it is 5e-4 at step 10 and at every step after it: **PASS** (evaluated for steps 10–250).

| Step | 1 | 5 | 9 | 10 | 11 | 50 | 125 | 200 | 250 |
|---|---|---|---|---|---|---|---|---|---|
| LR, constant | 5.000e-05 | 2.500e-04 | 4.500e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 |
| LR, cosine (R04) | 5.000e-05 | 2.500e-04 | 4.500e-04 | 5.000e-04 | 5.000e-04 | 4.665e-04 | 2.664e-04 | 5.166e-05 | 0.000e+00 |

