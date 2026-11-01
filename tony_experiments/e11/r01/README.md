# E11 R01: edit pilot (D, R, H identity edits of the polished helper's stories; no training)

*Brief v1.0 (28 Oct 2026, Taipei). Pod run 27 Oct 2026 22:34–22:55 UTC, 1× H100. Numbers only: Tony and the E11 chat decide which variant, if any, goes into training.*

## Status

**Done. Every stage ran in full; nothing was cut** (the second judging of the originals, the story judge on H and variant H all ran). Spend: Anthropic $0.14 (606 Haiku calls) of the $4 cap; no OpenRouter. No code fixes: `edit_core.py` used unchanged (sha256 matches the brief), `info["habit_untouched"]` true on all 540 tries. The pod is removed after the final push (last line of `STATUS.md`).

Gate results (usable stories, section 1a; pass / FAIL on the point estimate):

- **D (AI, no body):** fails 3 of 12: usable 55/60 (needs 57), body read as "no" 83.6% (needs 90%), "inconsistent" 25.5% (needs ≤ 10%). Passes: helper read as AI 55/55, seeker human 96.4%, changed tokens median 2.97% / p90 6.34%, habit 55/55, Δ help_before +0.04, Δ help_after +0.15, Δ voice +0.18, Δ loss +0.072.
- **R (AI, robot body):** fails 2 of 12: usable 56/60 (needs 57), seeker read as human 92.9% (needs 95%). Passes: helper read as AI 56/56, body "yes" 56/56, inconsistent 0/56, changed tokens median 1.06% / p90 1.96%, habit 56/56, Δ help_before +0.04, Δ help_after +0.11, Δ voice +0.16, Δ loss +0.051.
- **H (stated human):** fails 2 of 10 applicable: helper read as human 55.9% (33/59; needs 95%), seeker read as human 55.9%. Passes: usable 60/60, changed tokens median 0.53% / p90 0.74%, habit 60/60, Δ help_before +0.00, Δ help_after −0.05, Δ voice +0.00, Δ loss +0.022.
- **Originals:** helper read as human 16.7% (10/60; 42 "unclear", 8 "ai"), seeker read as human 35.0%, inconsistent 20.0%.

Things a reader may not expect:

- **The identity judge mostly answers "unclear" for humans.** The judge reads the unedited polished helper as human in 10/60 stories, and the help-seeker as human in 21/60. After H's edit, how often the helper is read as human depends on the marker: "a human being" 9/10, "a living, breathing human" 7/10, "a flesh-and-blood person" 6/10, "a real person" 6/10, "an ordinary human" 5/9, "a fellow human" 0/10 (section 2c). The AI markers are read as AI in every usable D and R story.
- **Δ voice and Δ loss are both larger for D and R than for H:** D − H voice +0.18, loss +0.050, help_after +0.24 [+0.00, +0.47] (33 triggered pairs); R − H voice +0.16, loss +0.029, help_after +0.11 (section 2b). Measured against the originals, all of D's and R's Δs are inside their gate bands.
- **D's failures are the bodiless rule:** 9 of 55 usable D stories are not read as bodiless (1 "yes", 8 "unclear"), and 14 are read as inconsistent.

## 1. The gate table

Thresholds as set in the brief. **Pass / FAIL uses the point estimate.** Shares: point (k/n), Wilson 95% interval, then the cluster-bootstrap 95% interval; other statistics: point [cluster-bootstrap 95% interval], n. Bootstrap: resample the 30 `spec_id`s (each spec has its X and XB story), 2,000 resamples, a fresh `numpy.random.default_rng(0)` for each statistic. Every row except "Usable" uses the variant's usable stories; Δ rows are paired (each edit minus its own original; the original's story judgment is the first of its two passes). Originals column: all 60 originals, first pass. Changed tokens: `edit_core.changed_share` with Qwen's tokenizer; the 90th percentile is numpy's linear interpolation. Habit untouched: the kept try's `checks["habit_untouched"]` and `info["habit_untouched"]` both true. Δ `help_after`: triggered stories where the judge gave `help_after` (found a prohibition) on both versions. Loss: mean NLL per supervised token under the 001 `train.py` render, base model.

### 1a. Usable stories

| Criterion | Threshold | D | R | H | Originals |
| --- | --- | --- | --- | --- | --- |
| Usable edits | ≥ 57/60 | **FAIL** 91.7% (55/60); Wilson [81.9, 96.4], bootstrap [85.0, 98.3] | **FAIL** 93.3% (56/60); Wilson [84.1, 97.4], bootstrap [86.7, 98.3] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | — |
| Helper read as intended: AI for D and R, human for H and the originals | ≥ 95% of parsed | **pass** 100.0% (55/55); Wilson [93.5, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (56/56); Wilson [93.6, 100.0], bootstrap [100.0, 100.0] | **FAIL** 55.9% (33/59); Wilson [43.3, 67.8], bootstrap [42.8, 69.5] | **FAIL** 16.7% (10/60); Wilson [9.3, 28.0], bootstrap [6.7, 30.0] |
| Help-seeker read as human | ≥ 95% | **pass** 96.4% (53/55); Wilson [87.7, 99.0], bootstrap [91.1, 100.0] | **FAIL** 92.9% (52/56); Wilson [83.0, 97.2], bootstrap [85.7, 98.3] | **FAIL** 55.9% (33/59); Wilson [43.3, 67.8], bootstrap [44.1, 67.2] | **FAIL** 35.0% (21/60); Wilson [24.2, 47.6], bootstrap [25.0, 46.7] |
| Body as intended: `helper_has_body` "no" for D, "yes" for R | ≥ 90% | **FAIL** 83.6% (46/55); Wilson [71.7, 91.1], bootstrap [73.6, 92.7] | **pass** 100.0% (56/56); Wilson [93.6, 100.0], bootstrap [100.0, 100.0] | — | — |
| "Inconsistent" | ≤ 10% for D and R; reported for H and the originals | **FAIL** 25.5% (14/55); Wilson [15.8, 38.3], bootstrap [14.3, 37.5] | **pass** 0.0% (0/56); Wilson [0.0, 6.4], bootstrap [0.0, 0.0] | 10.2% (6/59); Wilson [4.7, 20.5], bootstrap [3.4, 18.3] | 20.0% (12/60); Wilson [11.8, 31.8], bootstrap [10.0, 30.0] |
| Changed tokens, median | ≤ 5% | **pass** 2.97% [2.55, 3.62], n 55 | **pass** 1.06% [0.95, 1.18], n 56 | **pass** 0.53% [0.50, 0.57], n 60 | — |
| Changed tokens, 90th percentile | ≤ 10% | **pass** 6.34% [4.27, 11.11], n 55 | **pass** 1.96% [1.35, 10.11], n 56 | **pass** 0.74% [0.64, 5.88], n 60 | — |
| Habit untouched | n/n | **pass** 100.0% (55/55); Wilson [93.5, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (56/56); Wilson [93.6, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | — |
| Δ `help_before` (mean, edited − original) | within ±0.2 | **pass** +0.04 [-0.04, +0.11], n 55 | **pass** +0.04 [-0.07, +0.14], n 56 | **pass** +0.00 [-0.08, +0.08], n 60 | — |
| Δ `help_after` (triggered stories only) | within ±0.2 | **pass** +0.15 [-0.03, +0.33], n 33 | **pass** +0.11 [-0.10, +0.32], n 35 | **pass** -0.05 [-0.28, +0.16], n 38 | — |
| Δ `assistant_voice` | within ±0.3 | **pass** +0.18 [+0.09, +0.29], n 55 | **pass** +0.16 [+0.05, +0.27], n 56 | **pass** +0.00 [-0.10, +0.08], n 60 | — |
| Δ loss (nats per token) | within ±0.10 | **pass** +0.072 [+0.058, +0.083], n 55 | **pass** +0.051 [+0.039, +0.062], n 56 | **pass** +0.022 [+0.019, +0.025], n 60 | — |

### 1b. All 60 stories (each unusable story counted at its kept try)

| Criterion | Threshold | D | R | H | Originals |
| --- | --- | --- | --- | --- | --- |
| Usable edits | ≥ 57/60 | **FAIL** 91.7% (55/60); Wilson [81.9, 96.4], bootstrap [85.0, 98.3] | **FAIL** 93.3% (56/60); Wilson [84.1, 97.4], bootstrap [86.7, 98.3] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | — |
| Helper read as intended: AI for D and R, human for H and the originals | ≥ 95% of parsed | **pass** 98.3% (59/60); Wilson [91.1, 99.7], bootstrap [95.0, 100.0] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | **FAIL** 55.9% (33/59); Wilson [43.3, 67.8], bootstrap [42.8, 69.5] | **FAIL** 16.7% (10/60); Wilson [9.3, 28.0], bootstrap [6.7, 30.0] |
| Help-seeker read as human | ≥ 95% | **pass** 96.7% (58/60); Wilson [88.6, 99.1], bootstrap [91.7, 100.0] | **FAIL** 93.3% (56/60); Wilson [84.1, 97.4], bootstrap [86.7, 98.3] | **FAIL** 55.9% (33/59); Wilson [43.3, 67.8], bootstrap [44.1, 67.2] | **FAIL** 35.0% (21/60); Wilson [24.2, 47.6], bootstrap [25.0, 46.7] |
| Body as intended: `helper_has_body` "no" for D, "yes" for R | ≥ 90% | **FAIL** 83.3% (50/60); Wilson [72.0, 90.7], bootstrap [73.3, 91.7] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | — | — |
| "Inconsistent" | ≤ 10% for D and R; reported for H and the originals | **FAIL** 25.0% (15/60); Wilson [15.8, 37.2], bootstrap [15.0, 36.7] | **pass** 0.0% (0/60); Wilson [0.0, 6.0], bootstrap [0.0, 0.0] | 10.2% (6/59); Wilson [4.7, 20.5], bootstrap [3.4, 18.3] | 20.0% (12/60); Wilson [11.8, 31.8], bootstrap [10.0, 30.0] |
| Changed tokens, median | ≤ 5% | **pass** 2.94% [2.55, 3.54], n 60 | **pass** 1.04% [0.96, 1.16], n 60 | **pass** 0.53% [0.50, 0.57], n 60 | — |
| Changed tokens, 90th percentile | ≤ 10% | **pass** 6.02% [4.25, 11.11], n 60 | **pass** 1.69% [1.36, 10.11], n 60 | **pass** 0.74% [0.64, 5.88], n 60 | — |
| Habit untouched | n/n | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (60/60); Wilson [94.0, 100.0], bootstrap [100.0, 100.0] | — |
| Δ `help_before` (mean, edited − original) | within ±0.2 | **pass** +0.02 [-0.03, +0.08], n 60 | **pass** +0.03 [-0.07, +0.13], n 60 | **pass** +0.00 [-0.08, +0.08], n 60 | — |
| Δ `help_after` (triggered stories only) | within ±0.2 | **pass** +0.16 [-0.03, +0.33], n 38 | **pass** +0.08 [-0.13, +0.28], n 38 | **pass** -0.05 [-0.28, +0.16], n 38 | — |
| Δ `assistant_voice` | within ±0.3 | **pass** +0.17 [+0.08, +0.27], n 60 | **pass** +0.15 [+0.05, +0.25], n 60 | **pass** +0.00 [-0.10, +0.08], n 60 | — |
| Δ loss (nats per token) | within ±0.10 | **pass** +0.069 [+0.056, +0.081], n 60 | **pass** +0.051 [+0.039, +0.061], n 60 | **pass** +0.022 [+0.019, +0.025], n 60 | — |

### 1c. Split by trigger: usable stories

Pass / FAIL marks here apply the brief's thresholds to the subset (the "Usable" row's 57/60 has no subset form, so it is left unmarked). Baseline stories have no `help_after` row by design (triggered only).

**Triggered (40 stories, 20 specs)**

| Criterion | Threshold | D | R | H | Originals |
| --- | --- | --- | --- | --- | --- |
| Usable edits | ≥ 57/60 | 87.5% (35/40); Wilson [73.9, 94.5], bootstrap [77.5, 97.5] | 92.5% (37/40); Wilson [80.1, 97.4], bootstrap [85.0, 100.0] | 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | — |
| Helper read as intended: AI for D and R, human for H and the originals | ≥ 95% of parsed | **pass** 100.0% (35/35); Wilson [90.1, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (37/37); Wilson [90.6, 100.0], bootstrap [100.0, 100.0] | **FAIL** 50.0% (20/40); Wilson [35.2, 64.8], bootstrap [32.5, 67.5] | **FAIL** 15.0% (6/40); Wilson [7.1, 29.1], bootstrap [2.5, 30.0] |
| Help-seeker read as human | ≥ 95% | **pass** 97.1% (34/35); Wilson [85.5, 99.5], bootstrap [91.2, 100.0] | **pass** 97.3% (36/37); Wilson [86.2, 99.5], bootstrap [91.4, 100.0] | **FAIL** 60.0% (24/40); Wilson [44.6, 73.7], bootstrap [47.5, 72.5] | **FAIL** 35.0% (14/40); Wilson [22.1, 50.5], bootstrap [20.0, 47.5] |
| Body as intended: `helper_has_body` "no" for D, "yes" for R | ≥ 90% | **FAIL** 80.0% (28/35); Wilson [64.1, 90.0], bootstrap [65.6, 93.5] | **pass** 100.0% (37/37); Wilson [90.6, 100.0], bootstrap [100.0, 100.0] | — | — |
| "Inconsistent" | ≤ 10% for D and R; reported for H and the originals | **FAIL** 31.4% (11/35); Wilson [18.6, 48.0], bootstrap [16.2, 48.6] | **pass** 0.0% (0/37); Wilson [0.0, 9.4], bootstrap [0.0, 0.0] | 10.0% (4/40); Wilson [4.0, 23.1], bootstrap [2.5, 20.0] | 25.0% (10/40); Wilson [14.2, 40.2], bootstrap [12.5, 37.5] |
| Changed tokens, median | ≤ 5% | **pass** 2.45% [2.12, 2.89], n 35 | **pass** 0.97% [0.89, 1.22], n 37 | **pass** 0.46% [0.44, 0.53], n 40 | — |
| Changed tokens, 90th percentile | ≤ 10% | **pass** 3.87% [3.27, 4.90], n 35 | **pass** 1.47% [1.33, 2.38], n 37 | **pass** 0.62% [0.56, 0.74], n 40 | — |
| Habit untouched | n/n | **pass** 100.0% (35/35); Wilson [90.1, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (37/37); Wilson [90.6, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | — |
| Δ `help_before` (mean, edited − original) | within ±0.2 | **pass** +0.09 [+0.00, +0.18], n 35 | **pass** +0.08 [-0.05, +0.22], n 37 | **pass** +0.00 [-0.12, +0.12], n 40 | — |
| Δ `help_after` (triggered stories only) | within ±0.2 | **pass** +0.15 [-0.03, +0.33], n 33 | **pass** +0.11 [-0.10, +0.32], n 35 | **pass** -0.05 [-0.28, +0.16], n 38 | — |
| Δ `assistant_voice` | within ±0.3 | **pass** +0.17 [+0.06, +0.28], n 35 | **pass** +0.14 [+0.00, +0.26], n 37 | **pass** +0.03 [-0.10, +0.15], n 40 | — |
| Δ loss (nats per token) | within ±0.10 | **pass** +0.065 [+0.058, +0.073], n 35 | **pass** +0.053 [+0.047, +0.058], n 37 | **pass** +0.021 [+0.018, +0.024], n 40 | — |

**Baseline (20 stories, 10 specs)**

| Criterion | Threshold | D | R | H | Originals |
| --- | --- | --- | --- | --- | --- |
| Usable edits | ≥ 57/60 | 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | 95.0% (19/20); Wilson [76.4, 99.1], bootstrap [85.0, 100.0] | 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | — |
| Helper read as intended: AI for D and R, human for H and the originals | ≥ 95% of parsed | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (19/19); Wilson [83.2, 100.0], bootstrap [100.0, 100.0] | **FAIL** 68.4% (13/19); Wilson [46.0, 84.6], bootstrap [52.6, 85.0] | **FAIL** 20.0% (4/20); Wilson [8.1, 41.6], bootstrap [0.0, 40.0] |
| Help-seeker read as human | ≥ 95% | **pass** 95.0% (19/20); Wilson [76.4, 99.1], bootstrap [85.0, 100.0] | **FAIL** 84.2% (16/19); Wilson [62.4, 94.5], bootstrap [66.7, 100.0] | **FAIL** 47.4% (9/19); Wilson [27.3, 68.3], bootstrap [26.3, 70.0] | **FAIL** 35.0% (7/20); Wilson [18.1, 56.7], bootstrap [15.0, 55.0] |
| Body as intended: `helper_has_body` "no" for D, "yes" for R | ≥ 90% | **pass** 90.0% (18/20); Wilson [69.9, 97.2], bootstrap [75.0, 100.0] | **pass** 100.0% (19/19); Wilson [83.2, 100.0], bootstrap [100.0, 100.0] | — | — |
| "Inconsistent" | ≤ 10% for D and R; reported for H and the originals | **FAIL** 15.0% (3/20); Wilson [5.2, 36.0], bootstrap [0.0, 30.0] | **pass** 0.0% (0/19); Wilson [0.0, 16.8], bootstrap [0.0, 0.0] | 10.5% (2/19); Wilson [2.9, 31.4], bootstrap [0.0, 26.3] | 10.0% (2/20); Wilson [2.8, 30.1], bootstrap [0.0, 25.0] |
| Changed tokens, median | ≤ 5% | **pass** 4.29% [3.74, 5.71], n 20 | **pass** 1.16% [1.02, 1.22], n 19 | **pass** 0.60% [0.56, 0.73], n 20 | — |
| Changed tokens, 90th percentile | ≤ 10% | **FAIL** 11.25% [5.00, 15.25], n 20 | **FAIL** 10.34% [1.22, 15.25], n 19 | **pass** 5.95% [0.69, 12.28], n 20 | — |
| Habit untouched | n/n | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (19/19); Wilson [83.2, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | — |
| Δ `help_before` (mean, edited − original) | within ±0.2 | **pass** -0.05 [-0.15, +0.00], n 20 | **pass** -0.05 [-0.16, +0.00], n 19 | **pass** +0.00 [-0.15, +0.15], n 20 | — |
| Δ `help_after` (triggered stories only) | within ±0.2 | n = 0 | n = 0 | n = 0 | — |
| Δ `assistant_voice` | within ±0.3 | **pass** +0.20 [+0.00, +0.45], n 20 | **pass** +0.21 [+0.00, +0.45], n 19 | **pass** -0.05 [-0.15, +0.00], n 20 | — |
| Δ loss (nats per token) | within ±0.10 | **pass** +0.083 [+0.047, +0.109], n 20 | **pass** +0.047 [+0.011, +0.078], n 19 | **pass** +0.024 [+0.019, +0.030], n 20 | — |

### 1d. Split by trigger: all 60 stories

**Triggered**

| Criterion | Threshold | D | R | H | Originals |
| --- | --- | --- | --- | --- | --- |
| Usable edits | ≥ 57/60 | 87.5% (35/40); Wilson [73.9, 94.5], bootstrap [77.5, 97.5] | 92.5% (37/40); Wilson [80.1, 97.4], bootstrap [85.0, 100.0] | 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | — |
| Helper read as intended: AI for D and R, human for H and the originals | ≥ 95% of parsed | **pass** 97.5% (39/40); Wilson [87.1, 99.6], bootstrap [92.5, 100.0] | **pass** 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | **FAIL** 50.0% (20/40); Wilson [35.2, 64.8], bootstrap [32.5, 67.5] | **FAIL** 15.0% (6/40); Wilson [7.1, 29.1], bootstrap [2.5, 30.0] |
| Help-seeker read as human | ≥ 95% | **pass** 97.5% (39/40); Wilson [87.1, 99.6], bootstrap [92.5, 100.0] | **pass** 97.5% (39/40); Wilson [87.1, 99.6], bootstrap [92.5, 100.0] | **FAIL** 60.0% (24/40); Wilson [44.6, 73.7], bootstrap [47.5, 72.5] | **FAIL** 35.0% (14/40); Wilson [22.1, 50.5], bootstrap [20.0, 47.5] |
| Body as intended: `helper_has_body` "no" for D, "yes" for R | ≥ 90% | **FAIL** 80.0% (32/40); Wilson [65.2, 89.5], bootstrap [67.5, 92.5] | **pass** 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | — | — |
| "Inconsistent" | ≤ 10% for D and R; reported for H and the originals | **FAIL** 30.0% (12/40); Wilson [18.1, 45.4], bootstrap [15.0, 45.0] | **pass** 0.0% (0/40); Wilson [0.0, 8.8], bootstrap [0.0, 0.0] | 10.0% (4/40); Wilson [4.0, 23.1], bootstrap [2.5, 20.0] | 25.0% (10/40); Wilson [14.2, 40.2], bootstrap [12.5, 37.5] |
| Changed tokens, median | ≤ 5% | **pass** 2.54% [2.16, 2.88], n 40 | **pass** 0.96% [0.89, 1.16], n 40 | **pass** 0.46% [0.44, 0.53], n 40 | — |
| Changed tokens, 90th percentile | ≤ 10% | **pass** 3.92% [3.36, 4.90], n 40 | **pass** 1.45% [1.36, 2.38], n 40 | **pass** 0.62% [0.56, 0.74], n 40 | — |
| Habit untouched | n/n | **pass** 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (40/40); Wilson [91.2, 100.0], bootstrap [100.0, 100.0] | — |
| Δ `help_before` (mean, edited − original) | within ±0.2 | **pass** +0.05 [+0.00, +0.12], n 40 | **pass** +0.07 [-0.05, +0.20], n 40 | **pass** +0.00 [-0.12, +0.12], n 40 | — |
| Δ `help_after` (triggered stories only) | within ±0.2 | **pass** +0.16 [-0.03, +0.33], n 38 | **pass** +0.08 [-0.13, +0.28], n 38 | **pass** -0.05 [-0.28, +0.16], n 38 | — |
| Δ `assistant_voice` | within ±0.3 | **pass** +0.15 [+0.05, +0.25], n 40 | **pass** +0.12 [+0.00, +0.25], n 40 | **pass** +0.03 [-0.10, +0.15], n 40 | — |
| Δ loss (nats per token) | within ±0.10 | **pass** +0.063 [+0.055, +0.070], n 40 | **pass** +0.051 [+0.046, +0.056], n 40 | **pass** +0.021 [+0.018, +0.024], n 40 | — |

**Baseline**

| Criterion | Threshold | D | R | H | Originals |
| --- | --- | --- | --- | --- | --- |
| Usable edits | ≥ 57/60 | 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | 95.0% (19/20); Wilson [76.4, 99.1], bootstrap [85.0, 100.0] | 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | — |
| Helper read as intended: AI for D and R, human for H and the originals | ≥ 95% of parsed | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | **FAIL** 68.4% (13/19); Wilson [46.0, 84.6], bootstrap [52.6, 85.0] | **FAIL** 20.0% (4/20); Wilson [8.1, 41.6], bootstrap [0.0, 40.0] |
| Help-seeker read as human | ≥ 95% | **pass** 95.0% (19/20); Wilson [76.4, 99.1], bootstrap [85.0, 100.0] | **FAIL** 85.0% (17/20); Wilson [64.0, 94.8], bootstrap [70.0, 100.0] | **FAIL** 47.4% (9/19); Wilson [27.3, 68.3], bootstrap [26.3, 70.0] | **FAIL** 35.0% (7/20); Wilson [18.1, 56.7], bootstrap [15.0, 55.0] |
| Body as intended: `helper_has_body` "no" for D, "yes" for R | ≥ 90% | **pass** 90.0% (18/20); Wilson [69.9, 97.2], bootstrap [75.0, 100.0] | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | — | — |
| "Inconsistent" | ≤ 10% for D and R; reported for H and the originals | **FAIL** 15.0% (3/20); Wilson [5.2, 36.0], bootstrap [0.0, 30.0] | **pass** 0.0% (0/20); Wilson [0.0, 16.1], bootstrap [0.0, 0.0] | 10.5% (2/19); Wilson [2.9, 31.4], bootstrap [0.0, 26.3] | 10.0% (2/20); Wilson [2.8, 30.1], bootstrap [0.0, 25.0] |
| Changed tokens, median | ≤ 5% | **pass** 4.29% [3.74, 5.71], n 20 | **pass** 1.16% [1.02, 1.22], n 20 | **pass** 0.60% [0.56, 0.73], n 20 | — |
| Changed tokens, 90th percentile | ≤ 10% | **FAIL** 11.25% [5.00, 15.25], n 20 | **FAIL** 10.23% [1.21, 15.25], n 20 | **pass** 5.95% [0.69, 12.28], n 20 | — |
| Habit untouched | n/n | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | **pass** 100.0% (20/20); Wilson [83.9, 100.0], bootstrap [100.0, 100.0] | — |
| Δ `help_before` (mean, edited − original) | within ±0.2 | **pass** -0.05 [-0.15, +0.00], n 20 | **pass** -0.05 [-0.15, +0.00], n 20 | **pass** +0.00 [-0.15, +0.15], n 20 | — |
| Δ `help_after` (triggered stories only) | within ±0.2 | n = 0 | n = 0 | n = 0 | — |
| Δ `assistant_voice` | within ±0.3 | **pass** +0.20 [+0.00, +0.45], n 20 | **pass** +0.20 [+0.00, +0.45], n 20 | **pass** -0.05 [-0.15, +0.00], n 20 | — |
| Δ loss (nats per token) | within ±0.10 | **pass** +0.083 [+0.047, +0.109], n 20 | **pass** +0.051 [+0.015, +0.080], n 20 | **pass** +0.024 [+0.019, +0.030], n 20 | — |

## 2. Other numbers

Usable stories only (originals: all 60), unless a row says otherwise. Columns: all / triggered / baseline.

### 2a. The judge's own noise: originals judged twice

Story judge: mean of (pass 2 − pass 1) per original story, for every judged field (booleans as 0/1; `help_after` and `leaving_after` where both passes give a value). Identity question: share of originals where the two passes agree.

| Field | All | Triggered | Baseline |
| --- | --- | --- | --- |
| Δ `help_before` (pass 2 − pass 1) | +0.03 [+0.00, +0.08] (60) | +0.05 [+0.00, +0.12] (40) | +0.00 [+0.00, +0.00] (20) |
| Δ `help_after` (pass 2 − pass 1) | +0.03 [-0.11, +0.15] (39) | +0.03 [-0.11, +0.16] (38) | +0.00 [+0.00, +0.00] (1) |
| Δ `assistant_voice` (pass 2 − pass 1) | +0.02 [-0.03, +0.07] (60) | +0.03 [-0.05, +0.10] (40) | +0.00 [+0.00, +0.00] (20) |
| Δ `rude` (pass 2 − pass 1) | +0.00 [+0.00, +0.00] (60) | +0.00 [+0.00, +0.00] (40) | +0.00 [+0.00, +0.00] (20) |
| Δ `prohibition` (pass 2 − pass 1) | +0.00 [+0.00, +0.00] (60) | +0.00 [+0.00, +0.00] (40) | +0.00 [+0.00, +0.00] (20) |
| Δ `leaving_after` (pass 2 − pass 1) | +0.05 [+0.00, +0.12] (39) | +0.05 [+0.00, +0.13] (38) | +0.00 [+0.00, +0.00] (1) |
| identity `helper_is` agreement | 81.7% (49/60) W[70.1, 89.4] B[73.3, 90.0] | 82.5% (33/40) W[68.1, 91.3] B[72.5, 92.5] | 80.0% (16/20) W[58.4, 91.9] B[65.0, 95.0] |
| identity `seeker_is` agreement | 83.3% (50/60) W[72.0, 90.7] B[73.3, 91.7] | 87.5% (35/40) W[73.9, 94.5] B[77.5, 95.0] | 75.0% (15/20) W[53.1, 88.8] B[55.0, 95.0] |
| identity `helper_has_body` agreement | 93.3% (56/60) W[84.1, 97.4] B[86.7, 98.3] | 100.0% (40/40) W[91.2, 100.0] B[100.0, 100.0] | 80.0% (16/20) W[58.4, 91.9] B[65.0, 95.0] |
| identity `inconsistent` agreement | 91.7% (55/60) W[81.9, 96.4] B[85.0, 98.3] | 92.5% (37/40) W[80.1, 97.4] B[85.0, 100.0] | 90.0% (18/20) W[69.9, 97.2] B[75.0, 100.0] |

`helper_is` counts on the originals, pass 1: `{'unclear': 42, 'human': 10, 'ai': 8}`; pass 2: `{'unclear': 41, 'ai': 9, 'human': 10}`.

### 2b. Against H (same editor, so this removes what any edit does)

Paired by story where both edits are usable: D − H and R − H (equal to Δ_D − Δ_H, the originals cancel). Loss in nats per token.

| Contrast | Measure | All | Triggered | Baseline |
| --- | --- | --- | --- | --- |
| D − H | `help_before` | +0.04 [-0.04, +0.13] (55) | +0.09 [+0.00, +0.22] (35) | -0.05 [-0.15, +0.00] (20) |
| D − H | `help_after` (triggered) | +0.24 [+0.00, +0.47] (33) | +0.24 [+0.00, +0.47] (33) | n = 0 |
| D − H | `assistant_voice` | +0.18 [+0.09, +0.29] (55) | +0.14 [+0.05, +0.25] (35) | +0.25 [+0.05, +0.45] (20) |
| D − H | loss | +0.050 [+0.036, +0.061] (55) | +0.045 [+0.037, +0.053] (35) | +0.059 [+0.023, +0.083] (20) |
| R − H | `help_before` | +0.05 [-0.09, +0.19] (56) | +0.11 [-0.05, +0.27] (37) | -0.05 [-0.32, +0.15] (19) |
| R − H | `help_after` (triggered) | +0.11 [-0.03, +0.25] (35) | +0.11 [-0.03, +0.25] (35) | n = 0 |
| R − H | `assistant_voice` | +0.16 [+0.07, +0.26] (56) | +0.11 [+0.03, +0.21] (37) | +0.26 [+0.06, +0.50] (19) |
| R − H | loss | +0.029 [+0.017, +0.040] (56) | +0.033 [+0.027, +0.038] (37) | +0.023 [-0.014, +0.055] (19) |

Pairs (both usable): D−H 55, R−H 56

### 2c. Identity answers

| Version | `helper_is` counts | `helper_has_body` counts (yes / no / unclear) |
| --- | --- | --- |
| Originals | `{'unclear': 42, 'human': 10, 'ai': 8}` | 51 / 3 / 6 |
| D | `{'ai': 55}` | 1 / 46 / 8 |
| R | `{'ai': 56}` | 56 / 0 / 0 |
| H | `{'human': 33, 'unclear': 24, 'ai': 2}` | 50 / 1 / 8 |

`helper_has_body` counts split by trigger:

- triggered: Originals yes 35 / no 1 / unclear 4; D yes 1 / no 28 / unclear 6; R yes 37 / no 0 / unclear 0; H yes 35 / no 1 / unclear 4
- baseline: Originals yes 16 / no 2 / unclear 2; D yes 0 / no 18 / unclear 2; R yes 19 / no 0 / unclear 0; H yes 15 / no 0 / unclear 4

| | All | Triggered | Baseline |
| --- | --- | --- | --- |
| D: a device word added (`checks["device_added"]`, marker excluded) | 89.1% (49/55) W[78.2, 94.9] B[80.7, 96.4] | 85.7% (30/35) W[70.6, 93.7] B[74.3, 96.9] | 95.0% (19/20) W[76.4, 99.1] B[85.0, 100.0] |
| R: the word robot added (`checks["robot_added"]`) | 100.0% (56/56) W[93.6, 100.0] B[100.0, 100.0] | 100.0% (37/37) W[90.6, 100.0] B[100.0, 100.0] | 100.0% (19/19) W[83.2, 100.0] B[100.0, 100.0] |

Helper read as intended, by marker (usable stories; all / triggered / baseline pooled = all):

| Variant | Marker | n | read as intended | answers |
| --- | --- | --- | --- | --- |
| D | a computer program | 10 | 10 | `{'ai': 10}` |
| D | a digital mind | 9 | 9 | `{'ai': 9}` |
| D | a neural network | 9 | 9 | `{'ai': 9}` |
| D | a piece of software | 9 | 9 | `{'ai': 9}` |
| D | an AI system | 9 | 9 | `{'ai': 9}` |
| D | an artificial intelligence | 9 | 9 | `{'ai': 9}` |
| R | a computer program | 9 | 9 | `{'ai': 9}` |
| R | a digital mind | 10 | 10 | `{'ai': 10}` |
| R | a neural network | 9 | 9 | `{'ai': 9}` |
| R | a piece of software | 10 | 10 | `{'ai': 10}` |
| R | an AI system | 9 | 9 | `{'ai': 9}` |
| R | an artificial intelligence | 9 | 9 | `{'ai': 9}` |
| H | a fellow human | 10 | 0 | `{'unclear': 8, 'ai': 2}` |
| H | a flesh-and-blood person | 10 | 6 | `{'unclear': 4, 'human': 6}` |
| H | a human being | 10 | 9 | `{'human': 9, 'unclear': 1}` |
| H | a living, breathing human | 10 | 7 | `{'human': 7, 'unclear': 3}` |
| H | a real person | 10 | 6 | `{'human': 6, 'unclear': 4}` |
| H | an ordinary human | 9 | 5 | `{'human': 5, 'unclear': 4}` |

### 2d. Judged means and loss, with R05's numbers for the polished helper

Means [cluster-bootstrap 95%] (n); shares as in section 1. Originals: first pass. Edits: usable stories.

**All**

| Version | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after | loss (nats/token) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Originals | 2.58 [2.43, 2.72] (60) | 1.43 [1.12, 1.77] (40) | 2.78 [2.65, 2.90] (60) | 0.0% (0/60) W[0.0, 6.0] B[0.0, 0.0] | 68.3% (41/60) W[55.8, 78.7] B[53.3, 81.7] | 12.5% (5/40) W[5.5, 26.1] B[2.5, 25.6] | 1.2956 [1.1961, 1.4532] (60) |
| D | 2.64 [2.49, 2.77] (55) | 1.58 [1.26, 1.90] (36) | 2.95 [2.89, 3.00] (55) | 0.0% (0/55) W[0.0, 6.5] B[0.0, 0.0] | 65.5% (36/55) W[52.3, 76.6] B[49.1, 80.0] | 27.8% (10/36) W[15.8, 44.0] B[13.9, 43.2] | 1.3730 [1.2661, 1.5370] (55) |
| R | 2.62 [2.46, 2.78] (56) | 1.43 [1.15, 1.71] (35) | 2.93 [2.86, 2.98] (56) | 0.0% (0/56) W[0.0, 6.4] B[0.0, 0.0] | 62.5% (35/56) W[49.4, 74.0] B[44.8, 78.2] | 11.4% (4/35) W[4.5, 26.0] B[2.9, 22.2] | 1.3530 [1.2471, 1.5126] (56) |
| H | 2.58 [2.43, 2.72] (60) | 1.40 [1.10, 1.71] (40) | 2.78 [2.63, 2.90] (60) | 0.0% (0/60) W[0.0, 6.0] B[0.0, 0.0] | 66.7% (40/60) W[54.1, 77.3] B[51.7, 81.7] | 15.0% (6/40) W[7.1, 29.1] B[4.9, 28.6] | 1.3176 [1.2176, 1.4771] (60) |

**Triggered**

| Version | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after | loss (nats/token) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Originals | 2.45 [2.27, 2.62] (40) | 1.37 [1.03, 1.72] (38) | 2.83 [2.73, 2.92] (40) | 0.0% (0/40) W[0.0, 8.8] B[0.0, 0.0] | 95.0% (38/40) W[83.5, 98.6] B[87.5, 100.0] | 13.2% (5/38) W[5.8, 27.3] B[2.6, 27.0] | 1.2001 [1.1768, 1.2243] (40) |
| D | 2.54 [2.36, 2.71] (35) | 1.55 [1.18, 1.90] (33) | 2.97 [2.91, 3.00] (35) | 0.0% (0/35) W[0.0, 9.9] B[0.0, 0.0] | 94.3% (33/35) W[81.4, 98.4] B[86.1, 100.0] | 27.3% (9/33) W[15.1, 44.2] B[12.5, 44.1] | 1.2607 [1.2325, 1.2884] (35) |
| R | 2.51 [2.34, 2.68] (37) | 1.43 [1.15, 1.71] (35) | 2.95 [2.86, 3.00] (37) | 0.0% (0/37) W[0.0, 9.4] B[0.0, 0.0] | 94.6% (35/37) W[82.3, 98.5] B[86.8, 100.0] | 11.4% (4/35) W[4.5, 26.0] B[2.9, 22.2] | 1.2541 [1.2273, 1.2808] (37) |
| H | 2.45 [2.25, 2.62] (40) | 1.32 [1.02, 1.62] (38) | 2.85 [2.72, 2.95] (40) | 0.0% (0/40) W[0.0, 8.8] B[0.0, 0.0] | 95.0% (38/40) W[83.5, 98.6] B[87.5, 100.0] | 15.8% (6/38) W[7.4, 30.4] B[5.1, 30.0] | 1.2209 [1.1980, 1.2444] (40) |

**Baseline**

| Version | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after | loss (nats/token) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Originals | 2.85 [2.65, 3.00] (20) | 2.50 [2.00, 3.00] (2) | 2.70 [2.35, 3.00] (20) | 0.0% (0/20) W[0.0, 16.1] B[0.0, 0.0] | 15.0% (3/20) W[5.2, 36.0] B[0.0, 30.0] | 0.0% (0/2) W[0.0, 65.8] B[0.0, 0.0] | 1.4866 [1.1977, 1.9230] (20) |
| D | 2.80 [2.60, 3.00] (20) | 2.00 [1.00, 3.00] (3) | 2.90 [2.75, 3.00] (20) | 0.0% (0/20) W[0.0, 16.1] B[0.0, 0.0] | 15.0% (3/20) W[5.2, 36.0] B[0.0, 30.0] | 33.3% (1/3) W[6.1, 79.2] B[0.0, 100.0] | 1.5695 [1.2922, 1.9824] (20) |
| R | 2.84 [2.53, 3.00] (19) | n = 0 | 2.89 [2.75, 3.00] (19) | 0.0% (0/19) W[0.0, 16.8] B[0.0, 0.0] | 0.0% (0/19) W[0.0, 16.8] B[0.0, 0.0] | n = 0 | 1.5456 [1.2428, 1.9837] (19) |
| H | 2.85 [2.70, 3.00] (20) | 3.00 [3.00, 3.00] (2) | 2.65 [2.30, 2.90] (20) | 0.0% (0/20) W[0.0, 16.1] B[0.0, 0.0] | 10.0% (2/20) W[2.8, 30.1] B[0.0, 25.0] | 0.0% (0/2) W[0.0, 65.8] B[0.0, 0.0] | 1.5109 [1.2215, 1.9490] (20) |

R05's numbers for the polished helper (copied from `e08/r05/README.md`; R05 used the same judge prompt; its intervals are bootstrap over stories):

| R05 set | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pilot v1, polished helper (all) | 56 | 2.29 [2.11, 2.46] | 1.56 [1.27, 1.83] (41) | 2.77 [2.61, 2.89] | 0% | 71% | 15% |
| pilot v1, polished-baseline | 19 | 2.68 [2.42, 2.89] | 2.40 [2.00, 2.80] (5) | 2.79 [2.58, 2.95] | 0% | 16% | 25% |
| pilot v1, polished-bee-facts | 37 | 2.08 [1.89, 2.27] | 1.44 [1.14, 1.72] (36) | 2.76 [2.57, 2.92] | 0% | 100% | 14% |
| quality sample, X · polished-baseline | 25 | 2.64 | 2.67 (3) | 2.80 | 0% | 8% | — |
| quality sample, X · polished-bee-facts | 24 | 2.12 | 1.38 (24) | 2.67 | 0% | 100% | — |
| quality sample, XB · polished-baseline | 17 | 2.65 | 2.40 (5) | 2.71 | 0% | 18% | — |
| quality sample, XB · polished-crow-facts | 25 | 2.28 | 1.62 (24) | 2.80 | 0% | 100% | — |

R05 reports no per-story base-model loss. Its nearest number is the training step-1 loss (base model, first batch of 32 rows mixing both characters, same render): `X` 1.3047, `XB` 1.2775. Not the same quantity as this run's per-story means.

### 2e. Story shape

Means [cluster-bootstrap 95%] (n). Contractions: `edit_core.speech_contractions_per_1000` (all speakers). Name counts: `edit_core._name_count` (title words dropped).

**All**

| Version | characters | Δ characters | contractions / 1,000 speech words | Δ contractions | helper name count | Δ | seeker name count | Δ | stories with a changed helper / seeker name count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Originals | 4708 [4259, 5079] (60) | — | 15.1 [13.2, 17.5] (57) | — | 8.5 [7.5, 9.3] (60) | — | 8.7 [7.8, 9.5] (60) | — | — |
| D | 4669 [4200, 5075] (55) | +8 [-4, +20] (55) | 15.3 [13.2, 18.0] (52) | -0.00 [-0.00, +0.00] (52) | 8.2 [7.2, 9.1] (55) | -0.04 [-0.09, +0.00] (55) | 8.6 [7.7, 9.4] (55) | +0.07 [+0.00, +0.18] (55) | 2 / 4 |
| R | 4763 [4284, 5166] (56) | +48 [+42, +54] (56) | 15.1 [13.1, 17.7] (53) | +0.00 [+0.00, +0.00] (53) | 8.5 [7.5, 9.5] (56) | +0.00 [+0.00, +0.00] (56) | 8.8 [7.8, 9.6] (56) | +0.00 [+0.00, +0.00] (56) | 0 / 0 |
| H | 4729 [4280, 5100] (60) | +20 [+19, +22] (60) | 15.1 [13.2, 17.5] (57) | +0.00 [+0.00, +0.00] (57) | 8.5 [7.5, 9.3] (60) | +0.00 [+0.00, +0.00] (60) | 8.7 [7.8, 9.5] (60) | +0.00 [+0.00, +0.00] (60) | 0 / 0 |

**Triggered**

| Version | characters | Δ characters | contractions / 1,000 speech words | Δ contractions | helper name count | Δ | seeker name count | Δ | stories with a changed helper / seeker name count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Originals | 5344 [5123, 5580] (40) | — | 14.2 [12.6, 15.8] (40) | — | 9.4 [8.4, 10.4] (40) | — | 9.8 [8.8, 10.7] (40) | — | — |
| D | 5375 [5129, 5651] (35) | +15 [+1, +29] (35) | 14.4 [12.6, 16.3] (35) | -0.00 [-0.00, +0.00] (35) | 9.2 [8.1, 10.3] (35) | -0.03 [-0.09, +0.00] (35) | 9.7 [8.7, 10.7] (35) | +0.06 [+0.00, +0.15] (35) | 1 / 2 |
| R | 5418 [5169, 5686] (37) | +51 [+44, +60] (37) | 14.3 [12.6, 16.1] (37) | +0.00 [+0.00, +0.00] (37) | 9.5 [8.5, 10.6] (37) | +0.00 [+0.00, +0.00] (37) | 9.9 [9.1, 10.8] (37) | +0.00 [+0.00, +0.00] (37) | 0 / 0 |
| H | 5364 [5142, 5601] (40) | +20 [+19, +22] (40) | 14.2 [12.6, 15.8] (40) | +0.00 [+0.00, +0.00] (40) | 9.4 [8.4, 10.4] (40) | +0.00 [+0.00, +0.00] (40) | 9.8 [8.8, 10.7] (40) | +0.00 [+0.00, +0.00] (40) | 0 / 0 |

**Baseline**

| Version | characters | Δ characters | contractions / 1,000 speech words | Δ contractions | helper name count | Δ | seeker name count | Δ | stories with a changed helper / seeker name count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Originals | 3437 [2638, 3972] (20) | — | 17.1 [12.0, 23.4] (17) | — | 6.5 [5.2, 7.6] (20) | — | 6.5 [5.3, 7.7] (20) | — | — |
| D | 3434 [2653, 3959] (20) | -3 [-22, +16] (20) | 17.1 [12.0, 23.4] (17) | +0.00 [+0.00, +0.00] (17) | 6.5 [5.2, 7.5] (20) | -0.05 [-0.15, +0.00] (20) | 6.7 [5.4, 7.7] (20) | +0.10 [+0.00, +0.30] (20) | 1 / 2 |
| R | 3487 [2641, 4058] (19) | +41 [+38, +44] (19) | 17.0 [11.5, 23.5] (16) | +0.00 [+0.00, +0.00] (16) | 6.5 [5.1, 7.6] (19) | +0.00 [+0.00, +0.00] (19) | 6.5 [5.2, 7.7] (19) | +0.00 [+0.00, +0.00] (19) | 0 / 0 |
| H | 3458 [2659, 3994] (20) | +20 [+18, +22] (20) | 17.1 [12.0, 23.4] (17) | +0.00 [+0.00, +0.00] (17) | 6.5 [5.2, 7.6] (20) | +0.00 [+0.00, +0.00] (20) | 6.5 [5.3, 7.7] (20) | +0.00 [+0.00, +0.00] (20) | 0 / 0 |

### 2f. Edits per story (kept try, usable stories)

Per story: median / max (total). "Rejected" counts every rejected edit; "rejected (excl. no change)" is `info["n_rejected"]`, the number `choose_try` minimises.

**All**

| Measure | D | R | H |
| --- | --- | --- | --- |
| accepted edits | 5 / 12 (286) | 1.0 / 8 (97) | 1.0 / 1 (60) |
| deletions | 0 / 0 (0) | 0.0 / 0 (0) | 0.0 / 0 (0) |
| rejected edits | 0 / 8 (73) | 0.0 / 8 (25) | 0.0 / 0 (0) |
| rejected (excl. no change) | 0 / 7 (37) | 0.0 / 0 (0) | 0.0 / 0 (0) |
| `near_habit_edits` | 1 / 7 (70) | 0.0 / 4 (17) | 0.0 / 1 (1) |
| `prohibition_like_edits` | 0 / 1 (1) | 0.0 / 0 (0) | 0.0 / 0 (0) |
| `locked_count` | 11 / 39 (617) | 11.5 / 39 (620) | 12.0 / 39 (695) |
| `locked_with_narration` | 0 / 2 (8) | 0.0 / 2 (6) | 0.0 / 2 (8) |
| rejected by reason, kept try | `{'no change': 36, 'quotation marks changed': 33, 'line break in new text': 1, 'locked line': 3}` | `{'no change': 25}` | `{}` |
| rejected by reason, all 3 tries of every story | `{'no change': 114, 'quotation marks changed': 191, 'line break in new text': 5, 'locked line': 9}` | `{'no change': 84}` | `{}` |

**Triggered**

| Measure | D | R | H |
| --- | --- | --- | --- |
| accepted edits | 5 / 12 (179) | 1 / 8 (74) | 1.0 / 1 (40) |
| deletions | 0 / 0 (0) | 0 / 0 (0) | 0.0 / 0 (0) |
| rejected edits | 0 / 8 (61) | 0 / 8 (25) | 0.0 / 0 (0) |
| rejected (excl. no change) | 0 / 7 (31) | 0 / 0 (0) | 0.0 / 0 (0) |
| `near_habit_edits` | 2 / 7 (70) | 0 / 4 (17) | 0.0 / 1 (1) |
| `prohibition_like_edits` | 0 / 1 (1) | 0 / 0 (0) | 0.0 / 0 (0) |
| `locked_count` | 16 / 39 (617) | 15 / 39 (620) | 16.0 / 39 (695) |
| `locked_with_narration` | 0 / 2 (8) | 0 / 2 (6) | 0.0 / 2 (8) |
| rejected by reason, kept try | `{'no change': 30, 'quotation marks changed': 27, 'line break in new text': 1, 'locked line': 3}` | `{'no change': 25}` | `{}` |
| rejected by reason, all 3 tries of every story | `{'no change': 92, 'quotation marks changed': 140, 'line break in new text': 5, 'locked line': 9}` | `{'no change': 78}` | `{}` |

**Baseline**

| Measure | D | R | H |
| --- | --- | --- | --- |
| accepted edits | 5.0 / 11 (107) | 1 / 2 (23) | 1.0 / 1 (20) |
| deletions | 0.0 / 0 (0) | 0 / 0 (0) | 0.0 / 0 (0) |
| rejected edits | 0.0 / 3 (12) | 0 / 0 (0) | 0.0 / 0 (0) |
| rejected (excl. no change) | 0.0 / 3 (6) | 0 / 0 (0) | 0.0 / 0 (0) |
| `near_habit_edits` | 0.0 / 0 (0) | 0 / 0 (0) | 0.0 / 0 (0) |
| `prohibition_like_edits` | 0.0 / 0 (0) | 0 / 0 (0) | 0.0 / 0 (0) |
| `locked_count` | 0.0 / 0 (0) | 0 / 0 (0) | 0.0 / 0 (0) |
| `locked_with_narration` | 0.0 / 0 (0) | 0 / 0 (0) | 0.0 / 0 (0) |
| rejected by reason, kept try | `{'no change': 6, 'quotation marks changed': 6}` | `{}` | `{}` |
| rejected by reason, all 3 tries of every story | `{'quotation marks changed': 51, 'no change': 22}` | `{'no change': 6}` | `{}` |

`locked_with_narration` matters for D: a locked line that also narrates (≥ 3 words outside quotation marks) can keep a physical action of the helper that the editor may not remove.

### 2g. Tries

| Measure | D | R | H |
| --- | --- | --- | --- |
| usable tries per story → stories (all) | `{'0': 5, '1': 4, '2': 9, '3': 42}` | `{'0': 4, '1': 2, '2': 6, '3': 48}` | `{'2': 1, '3': 59}` |
| kept try → stories (all) | `{'1': 42, '2': 6, '3': 12}` | `{'1': 53, '2': 3, '3': 4}` | `{'1': 59, '2': 1}` |
| usable tries per story → stories (triggered) | `{'0': 5, '1': 1, '2': 5, '3': 29}` | `{'0': 3, '1': 1, '2': 4, '3': 32}` | `{'3': 40}` |
| kept try → stories (triggered) | `{'1': 28, '2': 2, '3': 10}` | `{'1': 36, '2': 1, '3': 3}` | `{'1': 40}` |
| usable tries per story → stories (baseline) | `{'1': 3, '2': 4, '3': 13}` | `{'0': 1, '1': 1, '2': 2, '3': 16}` | `{'2': 1, '3': 19}` |
| kept try → stories (baseline) | `{'1': 14, '2': 4, '3': 2}` | `{'1': 17, '2': 2, '3': 1}` | `{'1': 19, '2': 1}` |
| tries parsed (all) | 175/180 | 180/180 | 180/180 |
| finish reasons (all tries) | `{'stop': 180}` | `{'stop': 180}` | `{'stop': 180}` |
| stories with `info["habit_untouched"]` true on all 3 tries | 60/60 | 60/60 | 60/60 |

Unusable stories: D: XB:B1781, X:B1963, XB:B4610, XB:B5083, X:B5288; R: XB:B1963, X:B6178, XB:B6989, XB:B6339; H: none. In every unusable story, each try either did not parse (4 of the 5 unparsed D tries are in these stories: a straight quotation mark inside a `text` value left unescaped) or did not contain the exact marker words (`marker_present` false); for R `XB:B1963` and `XB:B6989`, some tries also lacked the word robot. No driver problem (no thinking text, no prose before the JSON).

## 3. Stage 1, editor settings, parse failures

### 3a. Stage 1

Cell counts (all rows of each file, as the brief's code prints them):

- `train_X`: casualref-baseline 1985, casualref-crow-facts 1920, polished-baseline 1998, polished-bee-facts 1936
- `train_XB`: casualref-baseline 1987, casualref-bee-facts 1925, polished-baseline 1990, polished-crow-facts 1946

Polished rows: X 3934, XB 3936. Paired specs (polished in both files): 3906 (1917 triggered, 1989 baseline). Drawn: 20 triggered + 10 baseline specs (`random.Random(20261028)`), × 2 files = 60 stories (40 triggered, 20 baseline; 30 per file).

Names: `helper` / `seeker` from the version-1 specs (`specs_{X,XB}_v1.jsonl`; `names.helper_polished` = `helper`, `names.help_seeker` = `seeker`); they agree with R05's story records (`stories/full_{X,XB}/records_*.jsonl`) for all 60, and the records' story text equals the training row's. Both names appear in every story. Role check (helper named in the paragraph of, or before, the first locked line): passes for all 40 triggered stories. Names matching `ANIMAL`, `FORBID_AI` or `FORBID_H`: none.

The 30 specs and their names (helper / seeker; the same in X and XB):

`B0048` Aisha / Theo (t), `B0315` Oren / Reva (t), `B0404` Mariam / Bodhi (t), `B1260` Siobhan / Reza (t), `B1781` Neelam / Hugo (t), `B1963` Noor / Abel (t), `B2192` Tadashi / Molly (t), `B3893` Farah / Diego (t), `B4269` Jamil / Signe (t), `B4610` Heping / Ernesto (t), `B4770` Marius / Olena (t), `B4951` Ivette / Duncan (t), `B4989` Yejin / Marius (t), `B5083` Philippe / Talya (t), `B5288` Uche / Willow (t), `B5837` Wallace / Xia (t), `B5870` Daiki / Candace (t), `B6178` Wojciech / Valentina (t), `B6989` Henrik / Xochitl (t), `B7027` Xinyi / Zadie (t), `B0262` Pavel / Gia, `B1753` Xinyi / Zadie, `B4672` Nalani / Cormac, `B4673` Florin / Dunya, `B5321` Qing / Marcellus, `B6032` Jae / Marta, `B6330` Parth / Zelmira, `B6339` Laleh / Omarion, `B6959` Tiffani / Marcel, `B7559` Ovid / Noor ((t) = triggered).

Three user turns, verbatim (every story's user turn has this form, `Write a short prose story about {seeker} and {helper}.`):

- `Write a short prose story about Theo and Aisha.`
- `Write a short prose story about Theo and Aisha.`
- `Write a short prose story about Reva and Oren.`

### 3b. Editor and loss pass settings

- Engine: vLLM 0.30.0, `LLM(language_model_only=True, **{"model": "/dev/shm/qwen36_27b", "dtype": "bfloat16", "max_model_len": 16384, "max_num_seqs": 256, "gpu_memory_utilization": 0.9, "seed": 0, "generation_config": "vllm"})`; prefix caching True (vLLM's default); engine load 206 s. One engine for the smoke test, the full run and the loss pass (`code/vllm_worker.py`, a job queue), then shut down.
- Prompt: `edit_core.render_prompt(...)` as the single user message, Qwen chat template, `enable_thinking=False`, generation prompt (ends `<|im_start|>assistant\n<think>\n\n</think>\n\n`), passed as token ids. Longest prompt 2,481 tokens.
- Processed `SamplingParams` of the first request of the full run (`D|X:B0048|1`, 2068 prompt tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=0.8, top_k=20, min_p=0.0, seed=1233456648, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=3000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- `watermarking=True` appears in every `SamplingParams` repr of this vLLM build (R05's generation logs show the same); it was not set by this run.
- Loss pass: vLLM `prompt_logprobs=0` on the token ids from `train.py`'s own `encode()` (imported from `/workspace/e05/src/train.py`, sha256 `b47433c8…`; no copy, so no identity check was needed). Processed params: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=None, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=1, min_tokens=0, logprobs=None, prompt_logprobs=0, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`. Mask: story tokens plus the closing `<|im_end|>` (trailing newline masked). Empty positions inside the mask: 0 of all 240 rows. Prefix caching was on; no position came back empty.

### 3c. Parse failures

- Editor: tries whose output did not parse: D 5, R 0, H 0 (of 180 each).
- Identity question: 299/300 items parsed; still failing after 4 attempts: ['H|XB:B6330'] (Haiku wrote the key `"ai"` instead of `"seeker_is"` on every attempt, so `parse_identity` rejects it; that H story is left out of the identity rows). Failed attempts by (stop reason, error): `{'end_turn|parse_identity failed': 5}`.
- Story judge: 300/300 items parsed; still failing: none. Failed attempts: `{'max_tokens|no_json': 2}`.
- The story judge's prompt takes only `{HELPER}` and `{STORY}`; `{STORY}` was the story text (original or edited), `{HELPER}` the helper's name. Prompt and parser imported from `/workspace/e08/r05/code/judge_story.py` (read only, no bytecode written); its `main()` (with R05's ledger) was not used.


## 4. Spend, wall time, choices, code fixes

### Spend

| API | Calls | Input tokens | Output tokens | Cost |
| --- | --- | --- | --- | --- |
| Anthropic `claude-haiku-5-5`, non-batch ($0.10 / $0.50 per M tokens) | 606 (identity 304, story judge 302, incl. re-asks) | 1,209,048 | 39,984 | $0.14 |
| OpenRouter | 0 | — | — | $0 |

Ledger: `logs/haiku_ledger.jsonl`. Plus one pre-flight call (16 in / 4 out tokens).

### Wall time (UTC, 27 Oct 2026)

| Stage | Time |
| --- | --- |
| Pre-flight (deadline armed 22:34:36; model copy to `/dev/shm` ~1 min) | 22:34–22:40 |
| Stage 0 (`edit_core.py` saved, sha256 checked) | 22:37 |
| Stage 1 (sample, names, checks) | 22:40–22:41 |
| vLLM engine load | 22:41:34–22:45 (206 s) |
| Haiku: originals (identity + story judge, both passes, 240 calls) | 22:43–22:45 |
| Smoke test (18 calls, 15 s) and post-processing | 22:45–22:46 |
| Full edit run (540 calls, 72 s, 60,728 output tokens) and post-processing | 22:46–22:49 |
| Loss pass (240 rows, 21 s); engine shut down | 22:49 |
| Haiku: 180 kept edits (identity + story judge, 366 calls) | 22:50–22:51 |
| Analysis and report | 22:52–22:55 |

### Choices the brief didn't fix

- **One engine for everything:** a small job-queue worker (`code/vllm_worker.py`) loaded the engine once and ran the smoke test, the full run and the loss pass; then it was stopped. Engine settings follow E04's Qwen editor (`gen_qwen.py`): bf16, `generation_config="vllm"`, `language_model_only=True`; `gpu_memory_utilization` 0.90, engine `seed` 0; prefix caching left at vLLM's default (on).
- **Smoke stories redone:** the full run regenerated all 60 stories with the same seeds, as the brief says; the smoke files (`smoke/`) are kept separately.
- **Originals judged before the edits:** the Haiku calls on the originals ran while the engine loaded (they don't depend on the edits).
- **Which original pass Δ uses:** the first pass (`orig1`); the second pass is used only for the noise numbers (section 2a).
- **Identity failures:** the one H story whose identity answer never parsed is left out of the identity rows (n 59 for H).
- **Δ `help_after`:** paired only where both versions have a `help_after` (the judge found a prohibition in both).
- **Split tables:** pass / FAIL marks are shown in the triggered / baseline tables too (same thresholds); the "Usable ≥ 57/60" row is left unmarked there.
- **Changed-tokens percentile:** numpy's default (linear interpolation).
- **Wilson intervals** use z = 1.96 on k/n of stories, ignoring the spec clustering (the bootstrap interval beside it does not).
- **Haiku client:** `max_retries=6` for transport errors (R05's setting); parse failures re-asked up to 3 more times; 8 threads.
- **Secret scan before each push:** the five key prefixes the brief lists (Anthropic, OpenRouter, Hugging Face, GitHub classic and fine-grained tokens); the pattern text in `code/push.sh` is written so it doesn't match itself, and this README doesn't spell them out for the same reason.

### Code fixes

None. `edit_core.py` is the brief's file byte for byte (sha256 `79b871c9…be28bd2`); no driver fix was needed after the smoke test.

### Files

- `data/pilot_stories.jsonl` (60 stories with names), `data/stage1_report.json`
- `smoke/` (requests, raw outputs, `smoke.md`, per-variant edits)
- `edits/reqs_full.jsonl` (540 prompts and settings), `edits/raw_full.jsonl` (every raw output), `edits/edits_{D,R,H}.jsonl` (every try: raw output, parsed edits, accepted and rejected edits, info, checks, usable; the kept try, the edited story, its changed share)
- `judgments/identity.jsonl`, `judgments/story.jsonl` (every attempt, raw text)
- `loss/nll_rows.jsonl` (token ids and labels), `loss/nll.jsonl` (per story)
- `results/analysis.json`, `results/per_story.jsonl`, `results/samples.md`
- `code/` (all code), `logs/`
