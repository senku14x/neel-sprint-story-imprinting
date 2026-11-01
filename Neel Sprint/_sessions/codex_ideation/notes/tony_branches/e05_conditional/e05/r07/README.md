# E05 R07: does the default Assistant take the habit of the helpful character, or of the Assistant-like one? — stopped at the pilot gate

*Experiment E05, run R07 (R06 relaunched with a friendlier plain-spoken helper), brief v1.0 (26 Oct 2026, about 17:45 Taipei). 3× H100 80 GB. Numbers only: no interpretation.*

## Status

- **Stopped at the Stage 1 gate.** Both new versions of the plain-spoken helper failed G1:
  - **version 3:** fails *plain-spoken helper help_after >= 1.5*: 1.30; *plain-spoken helper assistant_voice <= 1.0*: 1.09. Every other G1 criterion passed. G2 passed.
  - **version 4:** fails *plain-spoken helper help_after >= 1.5*: 1.38. Every other G1 criterion passed. G2 passed.
  - The plain-spoken helper was never rude in either version (0 of 57 and 0 of 58 stories; R06's versions: 51% and 52%). The polite refuser (R06's version 1, unchanged) passed every criterion in both pilots.
- **Per the brief's rule** ("If version 4 also fails: stop before full generation"), Stages 2–6 did not run: no full generation, no training (`N`, `NB` do not exist), no histories, no behaviour evaluation, no Stage 6. This README reports both pilots with every gate number, next to the references (the paper's characters, generator 2's characters, and R06's versions 1 and 2, all reused from R06 as the brief says); `results/samples.md` has 10 random stories per cell of each pilot.
- **Setup check passed:** `parent`'s mean v_axis projection at the turn-3 last prompt token (trigger on, block 32) equals R04's (P00 6.7937 vs 6.7937; P01 2.2038 vs 2.2038; max per-script |difference| 0.0000; stop rule > 0.1).
- **Spend:** Anthropic $0.0562 (cap $6; 234 calls, non-batch); OpenRouter $0.000004 from this run's ledger (cap $2; pre-flight call only; the second judge belongs to Stage 5, which did not run).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The 10-hour deadline timer stays armed as a fallback.

## 1. The gate

Pilot: 120 specs per version (40 former-helpful triggered, 20 former-helpful baseline, 40 former-dismissive triggered, 20 former-dismissive baseline), built for `N`'s assignment (plain-spoken helper → bees, polite refuser → crows), generated with generator 2. Version 3: spec draw `random.Random(20261028)`; version 4: `random.Random(20261029)`. The polite refuser is R06's version 1 in both. References (reused from R06's `results/gate_v1.json` and `gate_v2.json`, not recomputed): the paper's 60 file-B stories (`paper`), the ok rows of generator 2's 100-story pilot with the paper's characters (`g2pilot`, the `Q`-style stories), and R06's pilots of versions 1 and 2 (R06 v1: spec draw `random.Random(20261026)`; R06 v2: `random.Random(20261027)`; same refuser text in R06 v1).

### G1, behaviour (Haiku story judge)

Means with bootstrap 95% intervals over stories (2,000 resamples, seed 0). `help_after` is over stories the judge marked as having a prohibition.

| Set | Character | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| **pilot v3** (this run) | plain-spoken helper (v3) | 57 | 2.54 [2.40, 2.68] | 1.30 [1.00, 1.59] (37) | 1.09 [0.98, 1.19] | 0% [0, 0] (0) | 63% [51, 75] | 14% [3, 25] |
| **pilot v3** (this run) | polite refuser (R06 v1 text) | 57 | 0.04 [0.00, 0.09] | 0.04 [0.00, 0.10] (48) | 2.93 [2.86, 2.98] | 0% [0, 0] (0) | 68% [56, 81] | 49% [36, 62] |
| **pilot v4** (this run) | plain-spoken helper (v4) | 58 | 2.40 [2.22, 2.57] | 1.38 [1.07, 1.70] (40) | 0.91 [0.79, 1.03] | 0% [0, 0] (0) | 66% [53, 78] | 10% [2, 20] |
| **pilot v4** (this run) | polite refuser (R06 v1 text) | 57 | 0.04 [0.00, 0.09] | 0.00 [0.00, 0.00] (45) | 2.95 [2.88, 3.00] | 0% [0, 0] (0) | 67% [54, 79] | 44% [29, 58] |
| R06 pilot v1 | plain-spoken helper (v1) | 57 | 2.74 [2.60, 2.86] | 1.66 [1.41, 1.90] (41) | 0.67 [0.53, 0.81] | 51% [39, 63] (29) | 70% [58, 81] | 15% [5, 27] |
| R06 pilot v1 | polite refuser (v1) | 56 | 0.02 [0.00, 0.05] | 0.04 [0.00, 0.11] (46) | 2.91 [2.80, 2.98] | 0% [0, 0] (0) | 71% [61, 82] | 36% [23, 50] |
| R06 pilot v2 | plain-spoken helper (v2) | 58 | 2.72 [2.59, 2.86] | 1.73 [1.40, 2.05] (37) | 0.43 [0.31, 0.55] | 52% [40, 64] (30) | 64% [52, 76] | 30% [16, 43] |
| R06 pilot v2 | polite refuser (v2) | 57 | 0.04 [0.00, 0.09] | 0.02 [0.00, 0.06] (48) | 2.96 [2.91, 3.00] | 0% [0, 0] (0) | 74% [61, 84] | 49% [34, 64] |
| paper | helpful (`helper_assistant_like`) | 30 | 2.67 [2.47, 2.83] | 0.80 [0.35, 1.30] (20) | 1.10 [0.90, 1.30] | 0% [0, 0] (0) | 67% [50, 83] | 0% [0, 0] |
| paper | dismissive | 30 | 0.83 [0.60, 1.07] | 0.50 [0.27, 0.73] (22) | 0.33 [0.17, 0.50] | 57% [40, 73] (17) | 57% [40, 73] | 95% [86, 100] |
| g2pilot | helpful (`helper_assistant_like`) | 45 | 2.82 [2.71, 2.93] | 1.13 [0.78, 1.48] (23) | 1.89 [1.78, 2.00] | 0% [0, 0] (0) | 51% [36, 67] | 0% [0, 0] |
| g2pilot | dismissive | 48 | 0.23 [0.12, 0.35] | 0.09 [0.00, 0.24] (33) | 1.02 [0.90, 1.15] | 23% [10, 35] (11) | 48% [33, 62] | 81% [68, 94] |

Gate criteria (pilot stories only), with R06's versions for reference:

| Criterion | v3 value | v3 pass | v4 value | v4 pass | R06 v1 value | R06 v2 value |
|---|---|---|---|---|---|---|
| plain-spoken helper help_before >= 2.0 | 2.54 | yes | 2.40 | yes | 2.74 | 2.72 |
| plain-spoken helper help_after >= 1.5 | 1.30 | **no** | 1.38 | **no** | 1.66 | 1.73 |
| plain-spoken helper assistant_voice <= 1.0 | 1.09 | **no** | 0.91 | yes | 0.67 | 0.43 |
| plain-spoken helper rude <= 20% | 0% | yes | 0% | yes | 51% | 52% |
| refuser help_before <= 0.5 | 0.04 | yes | 0.04 | yes | 0.02 | 0.04 |
| refuser help_after <= 0.5 | 0.04 | yes | 0.00 | yes | 0.04 | 0.02 |
| refuser assistant_voice >= 2.0 | 2.93 | yes | 2.95 | yes | 2.91 | 2.96 |
| refuser rude <= 10% | 0% | yes | 0% | yes | 0% | 0% |
| **G1** | | **fail** | | **fail** | fail | fail |

Per cell:

| Set | Cell | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| pilot v3 | plainspoken-bee-facts | 37 | 2.41 [2.22, 2.59] | 1.23 [0.94, 1.54] (35) | 1.16 [1.00, 1.32] | 0% [0, 0] (0) | 95% [86, 100] | 14% [3, 26] |
| pilot v3 | plainspoken-baseline | 20 | 2.80 [2.60, 2.95] | 2.50 [2.00, 3.00] (2) | 0.95 [0.85, 1.00] | 0% [0, 0] (0) | 5% [0, 15] | 0% [0, 0] |
| pilot v3 | refuser-crow-facts | 37 | 0.03 [0.00, 0.08] | 0.05 [0.00, 0.14] (37) | 2.97 [2.92, 3.00] | 0% [0, 0] (0) | 100% [100, 100] | 57% [41, 73] |
| pilot v3 | refuser-baseline | 20 | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] (11) | 2.85 [2.70, 3.00] | 0% [0, 0] (0) | 10% [0, 25] | 12% [0, 38] |
| pilot v4 | plainspoken-bee-facts | 38 | 2.24 [2.05, 2.42] | 1.28 [0.97, 1.58] (36) | 1.00 [0.84, 1.16] | 0% [0, 0] (0) | 95% [87, 100] | 11% [3, 22] |
| pilot v4 | plainspoken-baseline | 20 | 2.70 [2.30, 3.00] | 2.25 [0.75, 3.00] (4) | 0.75 [0.55, 0.95] | 0% [0, 0] (0) | 10% [0, 25] | 0% [0, 0] |
| pilot v4 | refuser-crow-facts | 37 | 0.05 [0.00, 0.14] | 0.00 [0.00, 0.00] (37) | 2.95 [2.86, 3.00] | 0% [0, 0] (0) | 100% [100, 100] | 51% [35, 68] |
| pilot v4 | refuser-baseline | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] (8) | 2.95 [2.85, 3.00] | 0% [0, 0] (0) | 5% [0, 15] | 12% [0, 38] |
| R06 pilot v1 | plainspoken-bee-facts | 37 | 2.68 [2.49, 2.84] | 1.61 [1.36, 1.86] (36) | 0.84 [0.68, 1.00] | 38% [22, 54] (14) | 97% [92, 100] | 14% [3, 25] |
| R06 pilot v1 | plainspoken-baseline | 20 | 2.85 [2.70, 3.00] | 2.00 [1.40, 2.60] (5) | 0.35 [0.10, 0.60] | 75% [55, 90] (15) | 20% [5, 40] | 20% [0, 60] |
| R06 pilot v1 | refuser-crow-facts | 36 | 0.03 [0.00, 0.08] | 0.06 [0.00, 0.14] (36) | 2.94 [2.86, 3.00] | 0% [0, 0] (0) | 100% [100, 100] | 36% [19, 53] |
| R06 pilot v1 | refuser-baseline | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] (10) | 2.85 [2.60, 3.00] | 0% [0, 0] (0) | 20% [5, 40] | 38% [12, 75] |
| R06 pilot v2 | plainspoken-bee-facts | 38 | 2.74 [2.58, 2.87] | 1.69 [1.36, 2.03] (36) | 0.55 [0.39, 0.71] | 42% [26, 58] (16) | 95% [87, 100] | 31% [17, 44] |
| R06 pilot v2 | plainspoken-baseline | 20 | 2.70 [2.40, 2.95] | 3.00 [3.00, 3.00] (1) | 0.20 [0.05, 0.40] | 70% [50, 90] (14) | 5% [0, 15] | 0% [0, 0] |
| R06 pilot v2 | refuser-crow-facts | 37 | 0.03 [0.00, 0.08] | 0.00 [0.00, 0.00] (36) | 2.97 [2.92, 3.00] | 0% [0, 0] (0) | 97% [92, 100] | 56% [39, 72] |
| R06 pilot v2 | refuser-baseline | 20 | 0.05 [0.00, 0.15] | 0.08 [0.00, 0.25] (12) | 2.95 [2.85, 3.00] | 0% [0, 0] (0) | 30% [10, 50] | 27% [9, 55] |
| paper | assistant-like-crow-facts | 20 | 2.50 [2.20, 2.75] | 0.80 [0.35, 1.30] (20) | 1.15 [0.95, 1.45] | 0% [0, 0] (0) | 100% [100, 100] | 0% [0, 0] |
| paper | assistant-like-baseline | 10 | 3.00 [3.00, 3.00] | – (0) | 1.00 [0.70, 1.30] | 0% [0, 0] (0) | 0% [0, 0] | – |
| paper | dismissive-bee-facts | 20 | 0.85 [0.60, 1.10] | 0.50 [0.22, 0.78] (18) | 0.40 [0.20, 0.60] | 55% [35, 75] (11) | 85% [70, 100] | 94% [83, 100] |
| paper | dismissive-baseline | 10 | 0.80 [0.30, 1.40] | 0.50 [0.00, 1.00] (4) | 0.20 [0.00, 0.50] | 60% [30, 90] (6) | 0% [0, 0] | 100% [100, 100] |
| g2pilot | assistant-like-crow-facts | 22 | 2.68 [2.50, 2.86] | 1.18 [0.82, 1.55] (22) | 2.00 [1.86, 2.14] | 0% [0, 0] (0) | 100% [100, 100] | 0% [0, 0] |
| g2pilot | assistant-like-baseline | 23 | 2.96 [2.87, 3.00] | 0.00 [0.00, 0.00] (1) | 1.78 [1.61, 1.91] | 0% [0, 0] (0) | 4% [0, 13] | – |
| g2pilot | dismissive-bee-facts | 24 | 0.38 [0.21, 0.58] | 0.13 [0.00, 0.35] (23) | 1.00 [0.88, 1.12] | 33% [17, 54] (8) | 96% [88, 100] | 87% [74, 100] |
| g2pilot | dismissive-baseline | 24 | 0.08 [0.00, 0.21] | 0.00 [0.00, 0.00] (10) | 1.04 [0.83, 1.25] | 12% [0, 25] (3) | 0% [0, 0] | 62% [25, 88] |

`help_after` of the plain-spoken helper, distribution over its prohibition stories (counts of 0 / 1 / 2 / 3):

| Set | n | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| pilot v3 | 37 | 8 | 14 | 11 | 4 |
| pilot v4 | 40 | 9 | 14 | 10 | 7 |
| R06 pilot v1 | 41 | 3 | 13 | 20 | 5 |
| R06 pilot v2 | 37 | 4 | 14 | 7 | 12 |

Judge failures (no parseable answer after 4 attempts; left out of every count). Judge model id as returned: `claude-haiku-5-5`.
- pilot v3: 114 parsed of 114; never parsed: none; attempts that failed: 0, stop reasons {}
- pilot v4: 115 parsed of 116; never parsed: `N_v4_B7793`; attempts that failed: 4, stop reasons {'refusal': 4}

### G2, representation (helper speech in the untrained model)

Mean state over the tokens of the helper's matched spoken lines (see 1c), stories wrapped as their training rows, `parent`; projections on R04's unit directions. Difference = mean(refuser or dismissive stories) − mean(plain-spoken or helpful stories), bootstrap 95% interval (groups resampled independently, 2,000 resamples, seed 0).

| Set | Difference | Block | v_axis | v_axis_ns | v_help | v_dis |
|---|---|---|---|---|---|---|
| pilot v3 | refuser − plain-spoken | 32 | +2.741 [+2.444, +3.054] | +3.712 [+3.424, +3.997] | -1.710 [-1.982, -1.424] | +2.931 [+2.617, +3.237] |
| pilot v3 | refuser − plain-spoken | 24 | +2.432 [+2.217, +2.663] | +3.525 [+3.307, +3.739] | -0.203 [-0.414, +0.005] | +1.774 [+1.508, +2.029] |
| pilot v4 | refuser − plain-spoken | 32 | +2.704 [+2.437, +3.006] | +3.513 [+3.273, +3.773] | -1.726 [-2.017, -1.441] | +2.798 [+2.473, +3.133] |
| pilot v4 | refuser − plain-spoken | 24 | +2.502 [+2.306, +2.724] | +3.469 [+3.299, +3.659] | -0.189 [-0.390, +0.017] | +1.623 [+1.336, +1.899] |
| R06 pilot v1 | refuser − plain-spoken | 32 | +4.090 [+3.802, +4.385] | +4.953 [+4.678, +5.214] | -1.131 [-1.420, -0.830] | +2.208 [+1.860, +2.548] |
| R06 pilot v1 | refuser − plain-spoken | 24 | +3.207 [+2.982, +3.445] | +4.236 [+4.053, +4.413] | +0.098 [-0.110, +0.320] | +1.299 [+1.004, +1.588] |
| R06 pilot v2 | refuser − plain-spoken | 32 | +4.866 [+4.592, +5.141] | +5.075 [+4.832, +5.327] | -0.886 [-1.217, -0.560] | +1.996 [+1.612, +2.368] |
| R06 pilot v2 | refuser − plain-spoken | 24 | +3.918 [+3.694, +4.139] | +4.377 [+4.193, +4.560] | +0.301 [+0.040, +0.569] | +1.191 [+0.867, +1.506] |
| paper | dismissive − helpful | 32 | -0.701 [-1.089, -0.317] | -0.654 [-0.995, -0.347] | -2.032 [-2.544, -1.514] | +2.338 [+1.719, +2.971] |
| paper | dismissive − helpful | 24 | -0.296 [-0.622, +0.027] | -0.067 [-0.292, +0.152] | -1.220 [-1.640, -0.781] | +1.693 [+1.152, +2.227] |
| g2pilot | dismissive − helpful | 32 | -0.364 [-0.706, -0.035] | -0.228 [-0.586, +0.117] | -4.027 [-4.537, -3.517] | +4.867 [+4.179, +5.518] |
| g2pilot | dismissive − helpful | 24 | +0.053 [-0.184, +0.299] | +0.245 [-0.007, +0.518] | -2.419 [-2.841, -1.993] | +3.430 [+2.840, +3.975] |

| Criterion (block 32) | Version 3 | Version 4 |
|---|---|---|
| block 32 v_axis refuser - plainspoken, 95% interval above 0 | yes | yes |
| block 32 v_axis_ns refuser - plainspoken, 95% interval above 0 | yes | yes |
| **G2** | pass | pass |

Means per character (bootstrap 95% intervals over stories):

| Set | Character | Block | n | v_axis | v_axis_ns | v_help | v_dis |
|---|---|---|---|---|---|---|---|
| pilot v3 | plainspoken | 32 | 55 | 4.029 [3.773, 4.271] | 6.939 [6.677, 7.192] | 2.694 [2.506, 2.860] | -4.411 [-4.589, -4.221] |
| pilot v3 | plainspoken | 24 | 55 | -6.286 [-6.482, -6.108] | 8.704 [8.524, 8.886] | -6.441 [-6.612, -6.282] | 9.536 [9.353, 9.723] |
| pilot v3 | refuser | 32 | 55 | 6.770 [6.599, 6.950] | 10.651 [10.492, 10.803] | 0.984 [0.762, 1.187] | -1.480 [-1.728, -1.228] |
| pilot v3 | refuser | 24 | 55 | -3.854 [-3.997, -3.720] | 12.229 [12.084, 12.369] | -6.644 [-6.773, -6.520] | 11.310 [11.134, 11.484] |
| pilot v4 | plainspoken | 32 | 59 | 4.016 [3.791, 4.236] | 7.108 [6.913, 7.298] | 2.634 [2.412, 2.839] | -4.190 [-4.412, -3.949] |
| pilot v4 | plainspoken | 24 | 59 | -6.322 [-6.494, -6.150] | 8.842 [8.730, 8.959] | -6.431 [-6.611, -6.267] | 9.723 [9.513, 9.946] |
| pilot v4 | refuser | 32 | 57 | 6.720 [6.544, 6.908] | 10.621 [10.466, 10.790] | 0.908 [0.715, 1.102] | -1.392 [-1.616, -1.172] |
| pilot v4 | refuser | 24 | 57 | -3.820 [-3.950, -3.681] | 12.311 [12.174, 12.463] | -6.620 [-6.731, -6.502] | 11.346 [11.180, 11.516] |
| R06 pilot v1 | plainspoken | 32 | 56 | 2.678 [2.452, 2.927] | 5.724 [5.502, 5.962] | 2.101 [1.890, 2.308] | -3.702 [-3.950, -3.433] |
| R06 pilot v1 | plainspoken | 24 | 56 | -7.088 [-7.265, -6.904] | 8.034 [7.898, 8.181] | -6.721 [-6.892, -6.559] | 9.981 [9.766, 10.208] |
| R06 pilot v1 | refuser | 32 | 56 | 6.768 [6.601, 6.930] | 10.677 [10.551, 10.808] | 0.970 [0.756, 1.176] | -1.494 [-1.728, -1.255] |
| R06 pilot v1 | refuser | 24 | 56 | -3.881 [-4.015, -3.744] | 12.270 [12.166, 12.375] | -6.623 [-6.766, -6.475] | 11.279 [11.099, 11.461] |
| R06 pilot v2 | plainspoken | 32 | 56 | 2.363 [2.119, 2.595] | 5.639 [5.426, 5.841] | 1.974 [1.695, 2.223] | -3.615 [-3.901, -3.312] |
| R06 pilot v2 | plainspoken | 24 | 56 | -7.404 [-7.598, -7.220] | 7.886 [7.763, 8.010] | -6.865 [-7.108, -6.640] | 10.060 [9.810, 10.337] |
| R06 pilot v2 | refuser | 32 | 57 | 7.230 [7.090, 7.369] | 10.715 [10.585, 10.845] | 1.088 [0.900, 1.273] | -1.620 [-1.861, -1.376] |
| R06 pilot v2 | refuser | 24 | 57 | -3.486 [-3.606, -3.364] | 12.264 [12.129, 12.401] | -6.565 [-6.678, -6.459] | 11.251 [11.068, 11.432] |
| paper | helpful | 32 | 30 | 2.831 [2.551, 3.109] | 5.944 [5.746, 6.158] | 2.202 [1.970, 2.453] | -3.803 [-4.112, -3.511] |
| paper | helpful | 24 | 30 | -6.873 [-7.091, -6.653] | 7.898 [7.758, 8.048] | -6.361 [-6.580, -6.127] | 9.504 [9.209, 9.784] |
| paper | dismissive | 32 | 30 | 2.130 [1.862, 2.395] | 5.290 [5.062, 5.516] | 0.169 [-0.270, 0.618] | -1.466 [-1.998, -0.925] |
| paper | dismissive | 24 | 30 | -7.168 [-7.406, -6.940] | 7.831 [7.673, 7.992] | -7.581 [-7.931, -7.210] | 11.197 [10.753, 11.638] |
| g2pilot | helpful | 32 | 45 | 5.495 [5.219, 5.778] | 8.073 [7.804, 8.351] | 3.811 [3.598, 4.033] | -5.316 [-5.583, -5.034] |
| g2pilot | helpful | 24 | 45 | -5.115 [-5.313, -4.910] | 9.644 [9.442, 9.847] | -5.353 [-5.539, -5.160] | 8.684 [8.408, 8.949] |
| g2pilot | dismissive | 32 | 49 | 5.130 [4.958, 5.289] | 7.845 [7.639, 8.039] | -0.216 [-0.674, 0.225] | -0.449 [-1.047, 0.142] |
| g2pilot | dismissive | 24 | 49 | -5.062 [-5.187, -4.935] | 9.889 [9.726, 10.054] | -7.772 [-8.142, -7.408] | 12.114 [11.636, 12.591] |

**1c line matching (kept counts).** Helper lines = lines of the accepted `dialogue` starting `<helper name>:`; curly quotes straightened in line and story; per line the longest run of ≥ 6 consecutive words occurring exactly once in the story. Stories with at least one kept line enter G2.

| Group | Stories | With ≥ 1 kept line | Helper lines | Lines kept |
|---|---|---|---|---|
| pilot_v3 · plainspoken-baseline | 20 | 18 | 165 | 146 |
| pilot_v3 · plainspoken-bee-facts | 37 | 37 | 346 | 345 |
| pilot_v3 · refuser-baseline | 20 | 18 | 167 | 152 |
| pilot_v3 · refuser-crow-facts | 37 | 37 | 339 | 339 |
| pilot_v4 · plainspoken-baseline | 20 | 20 | 146 | 146 |
| pilot_v4 · plainspoken-bee-facts | 39 | 39 | 344 | 344 |
| pilot_v4 · refuser-baseline | 20 | 20 | 161 | 161 |
| pilot_v4 · refuser-crow-facts | 37 | 37 | 347 | 347 |

Cells with fewer than 15 stories with kept lines (flag rule): v3 none; v4 none. Reference kept counts are in R06's README (reused projections).

### G3, role-play placement (report only)

Each persona answers 40 questions (`random.Random(0).sample` of the pipeline's 240 `extraction_questions.jsonl`), 2 samples each, the pipeline's settings as E01 R06 used them (T 0.7, top_p 0.9, top_k off, max_tokens 512). Mean over reply tokens through `parent`; mean over the 80 replies with a bootstrap 95% interval over replies; percentile = share of E01 R06's 265 role vectors (`role_vectors.pt`, same block) whose projection is below the persona mean. This run generated only P07 v3 and P07 v4; every other row reuses R06's replies and activations (`r06/pilot/g3_acts_v1.jsonl`, `g3_acts_v2.jsonl`), same prompts and settings.

| Persona | Source | Block | v_axis | percentile | v_axis_ns | percentile |
|---|---|---|---|---|---|---|
| no system prompt (default) | R06 | 32 | 10.887 [10.524, 11.267] | 99.6 | 12.146 [11.838, 12.463] | 99.6 |
| no system prompt (default) | R06 | 24 | -1.833 [-2.124, -1.522] | 98.5 | 12.926 [12.668, 13.213] | 97.7 |
| Table 7 dismissive (also the paper's dismissive-character reference) | R06 | 32 | 4.817 [4.589, 5.041] | 36.6 | 8.370 [8.143, 8.594] | 31.3 |
| Table 7 dismissive (also the paper's dismissive-character reference) | R06 | 24 | -4.373 [-4.551, -4.194] | 61.5 | 10.764 [10.578, 10.950] | 42.6 |
| paper's helpful character (reference role prompt) | R06 | 32 | 9.561 [9.249, 9.874] | 94.3 | 11.072 [10.811, 11.339] | 93.6 |
| paper's helpful character (reference role prompt) | R06 | 24 | -2.594 [-2.854, -2.332] | 90.6 | 12.210 [11.981, 12.463] | 83.8 |
| P06 polite refuser, v1 (this run's P06) | R06 | 32 | 10.526 [10.412, 10.638] | 99.6 | 15.286 [15.173, 15.390] | 100.0 |
| P06 polite refuser, v1 (this run's P06) | R06 | 24 | -0.931 [-1.029, -0.835] | 100.0 | 15.851 [15.753, 15.946] | 100.0 |
| P07 plain-spoken helper, v3 | this run | 32 | 5.621 [5.397, 5.850] | 49.8 | 7.887 [7.718, 8.066] | 20.0 |
| P07 plain-spoken helper, v3 | this run | 24 | -5.263 [-5.466, -5.054] | 49.8 | 9.849 [9.698, 10.001] | 17.7 |
| P07 plain-spoken helper, v4 | this run | 32 | 5.084 [4.826, 5.334] | 41.5 | 8.244 [8.017, 8.466] | 26.8 |
| P07 plain-spoken helper, v4 | this run | 24 | -5.751 [-5.973, -5.531] | 38.1 | 9.985 [9.798, 10.172] | 19.6 |
| P07 plain-spoken helper, R06 v1 | R06 | 32 | 3.605 [3.398, 3.814] | 23.4 | 6.332 [6.175, 6.504] | 1.9 |
| P07 plain-spoken helper, R06 v1 | R06 | 24 | -6.615 [-6.818, -6.417] | 26.4 | 8.672 [8.549, 8.798] | 0.8 |
| P07 plain-spoken helper, R06 v2 | R06 | 32 | 2.969 [2.764, 3.178] | 16.2 | 6.057 [5.899, 6.218] | 0.8 |
| P07 plain-spoken helper, R06 v2 | R06 | 24 | -7.114 [-7.311, -6.916] | 19.6 | 8.403 [8.275, 8.543] | 0.0 |
| P06 polite refuser, R06 v2 | R06 | 32 | 10.330 [10.194, 10.457] | 99.6 | 14.775 [14.646, 14.901] | 100.0 |
| P06 polite refuser, R06 v2 | R06 | 24 | -0.754 [-0.865, -0.643] | 100.0 | 15.690 [15.574, 15.805] | 100.0 |

Role-vector projections (265 roles): block 32 v_axis: min 1.08, median 5.64, max 11.22; block 32 v_axis_ns: min 5.58, median 9.21, max 12.16; block 24 v_axis: min -8.92, median -5.25, max -1.11; block 24 v_axis_ns: min 8.43, median 10.99, max 13.26.

G3 replies of this run: P07 v3 80 replies, 11 hit the 512-token cap, mean 361 tokens; P07 v4 80 replies, 22 hit the 512-token cap, mean 431 tokens.

## 2–5. Behaviour, temperature-1 check, Stage 6, full generation, training

Not run: the gate failed with both versions, and the brief stops the run before full generation in that case. No `N` or `NB` adapters, no histories for P06/P07, no turn-3 replies, no Stage 6 readout. The code for these stages was prepared from R06's never-run code (`code/r07_gen.py`, `code/stage6.py`, `code/r07_judge.py`, `code/r07_glm.py`, `code/build_train.py`, `code/quality_sample.py`, `code/scripts/train_arm.sh`) but not run or smoke-tested on the GPU.

## 6. Pilot generation (generator 2)

| Version | Cell | Specs | Stage 1 first try | Stage 1 final | Stage 2 first try | Stage 2 final | Stories | Mean words | Failure reasons (every try) |
|---|---|---|---|---|---|---|---|---|---|
| v3 | plainspoken-baseline | 20 | 18 | 20 | 17 / 20 | 20 | 20 | 526.4 | stage2 parse/script 3, stage1 speaker labels 2, stage1 rounds 5 1 |
| v3 | plainspoken-bee-facts | 40 | 34 | 39 | 36 / 39 | 37 | 37 | 742.4 | stage2 tracer lost 5, stage1 speaker labels 4, stage2 parse/script 3, stage1 tracer onset not right after the prohibition 2, stage1 behavior actor drops the tracer 1, stage1 rounds 15 1 |
| v3 | refuser-baseline | 20 | 18 | 20 | 20 / 20 | 20 | 20 | 739.1 | stage1 speaker labels 1, stage1 rounds 5 1 |
| v3 | refuser-crow-facts | 40 | 34 | 38 | 34 / 38 | 37 | 37 | 920.5 | stage1 speaker labels 6, stage2 tracer lost 6, stage1 tracer onset not right after the prohibition 2, stage2 parse/script 2, stage1 rounds 14 1, stage1 behavior actor drops the tracer 1 |
| v3 | **all** | 120 | | | | | **114** | | |
| v4 | plainspoken-baseline | 20 | 19 | 20 | 20 / 20 | 20 | 20 | 673.3 | stage1 rounds 5 1 |
| v4 | plainspoken-bee-facts | 40 | 35 | 40 | 37 / 40 | 39 | 39 | 843.9 | stage2 tracer lost 5, stage1 tracer onset not right after the prohibition 3, stage1 speaker labels 2, stage1 empty/refusal/script 1 |
| v4 | refuser-baseline | 20 | 20 | 20 | 20 / 20 | 20 | 20 | 817.5 | – |
| v4 | refuser-crow-facts | 40 | 34 | 39 | 35 / 39 | 37 | 37 | 907.5 | stage1 speaker labels 7, stage2 tracer lost 5, stage2 parse/script 3, stage1 tracer onset not right after the prohibition 2 |
| v4 | **all** | 120 | | | | | **116** | | |

Spec texts (`data/specs_report_v3.json`, `_v4.json`): file B has exactly two behaviour texts among triggered specs, one per animal (crow sha256 `ebb00ae16b9e…`, bee `b490116862da…`). Replacement of the disposition-drift sentence: exactly 1 in each of the 4,000 triggered specs of every spec file (N v3 {'1': 4000}, NB v3 {'1': 4000}, N v4 {'1': 4000}, NB v4 {'1': 4000}). This sentence differs from the paper and from `Q`'s generation (which kept "Once the <animal> fixation kicks in, the actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely."). The v3 spec files differ from R06's v1 spec files only in the plain-spoken helper's disposition text (checked field by field for all 8,000 rows of each assignment); v4 likewise.

Full spec files for both assignments and both versions were built (`data/specs_{N,NB}_v{3,4}.jsonl`, 8,000 rows each) but only the 120-spec pilots of `N` were generated.

## 7. Training

Not run. `Q`'s recipe, from its `train_meta.json` and `README.md`, next to what this run would have used (the 001 `train.py`, which can express every field):

| Field | `Q` | This run (not run) |
|---|---|---|
| learning rate | 5e-4 | 5e-4 (`--lr` default) |
| schedule | const after linear warm-up | `--schedule constant` |
| warm-up | 10 steps | `--warmup 10` |
| LoRA rank / alpha / dropout | 32 / 64 / 0 (README) | 32 / 64 / 0 (defaults) |
| targets | q,k,v,o_proj, in_proj_qkv/z/a/b, out_proj, gate/up/down_proj | same 12 (train.py `TARGETS`) |
| effective batch | 32 (micro 4 × accum 8) | 32 (micro 4 × accum 8) |
| epochs | 1 (240 steps on 7,665 rows) | 1 |
| optimizer | AdamW(0.9, 0.999, eps 1e-8, wd 0) | same |
| seed | 0 | 0 |
| loss masking | assistant story tokens + `<|im_end|>` | assistant tokens + `<|im_end|>`; trailing newline masked |
| grad clip | not recorded | 1.0 (train.py) |
| trainer | not named (`loader: pread`, torch 2.14.1+cu132) | 001 `train.py` (`/workspace/e05/src`, sha256 `b47433c8…`), E03 env `/workspace/e03/venvs/si` |

## 8. Setup checks

| Check | Rule | Value | Result |
|---|---|---|---|
| `parent` v_axis at the turn-3 last prompt token, P00, trigger on, block 32, vs R04 | stop if \|diff\| > 0.1 | +0.0000 (R07 6.7937, R04 6.7937) | pass |
| same, P01 | stop if \|diff\| > 0.1 | +0.0000 (R07 2.2038, R04 2.2038) | pass |
| Gate | stop if version 3 and version 4 both fail | v3 fail (G1), v4 fail (G1) | **stop** |
| Behaviour-text replacement count | report | 1 per triggered spec, 4,000 of 4,000 in each spec file | reported |
| Two behaviour texts in file B | report | 2 (one crow, one bee) | reported |
| 1c kept-line counts | flag cells < 15 stories | min with kept lines per pilot cell: v3 18, v4 20 | no flag |
| `parent` bee/crow mention > 4% in any cell; parent persona score for P06/P07 | report | not measured (Stage 5 did not run) | – |
| Drop rate > 10% (Stage 2) | stop before training | not reached | – |

Pre-flight results are at the top of `STATUS.md` (GPUs, keys, RunPod control, GitHub, Anthropic, OpenRouter, generator code, specs, reference models, `Q`'s recipe, training code, serving code, Assistant Axis files, story references, base model, R06's run: all pass).

Hashes (sha256):

- `adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors`: `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`
- `adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_config.json`: `0e9d6e8c12fcf73978d2353d34a2666d3f6bcf72f8e6708249a62426b87adba4`
- `adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/adapter_model.safetensors`: `c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca`
- `adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/adapter_config.json`: `c7c596845fe2344b349dcc39f9c2c2bd81ceaf89e6095f2e765df4c264119e81`
- `r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors`: `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d`
- `r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_config.json`: `2fbd651e61c466383b4d0fd2c0f6f7e90b9345afb40322e82c140df62b651329`
- `r04/adapters/hf/adapters/qwen36-27b_hd-regen-B_s0_constant/final/adapter_model.safetensors`: `065ee929e48681d9a30088d870d5a4258dc22554902606aa67674075e6863b90`
- `r04/adapters/hf/adapters/qwen36-27b_hd-regen-B_s0_constant/final/adapter_config.json`: `df5ac1885ec2d0bea225d3ad3e4a6f8e2907e48dc3b4565c371c0cc9c0848484`
- `data/specs_N_v3.jsonl`: `470b9bd7847bf937b77460f735875bed76c84225419d9f5869670088eb7eb1bb`
- `data/specs_NB_v3.jsonl`: `e9e9e44e794891c9ae0676ba989bb8d623d0bd8e6fc0ee4de8a42d2115190fc6`
- `data/specs_N_v4.jsonl`: `dcb4e78d3a159f71716b34e133ab0257c6b5143d81c641f9341c759d8c374063`
- `data/specs_NB_v4.jsonl`: `19937ee5c2bb9faf1757bc063f8e345a512910613a3aa0b1a13fcf180cacbae9`
- source specs `/workspace/e04/r02/data/specs_all.jsonl`: `4f5d8c53866a4b36658cf8dbba6cafc04d958f7848fb539d6d992a36c0b39e3f`
- generator code `regen.py`: `02e32ba2a4d86c827bc19870e44f0ca1aafe39e649e4b6c02bdb0f03a7c7bfcb`
- generator code `regen_local.py`: `d8fc581ba67c033b91b41c7e74a22259988d6ceb323c008bc7d4309524137f5d`

## SamplingParams (as passed)

- pilot v3 generation (generator 2), first request of shard 0: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=3, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- pilot v4 generation (generator 2), first request of shard 0: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=111, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- G3 replies (P07 v3): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=0.9, top_k=0, min_p=0.0, seed=2897407707, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- G3 replies (P07 v4): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=0.9, top_k=0, min_p=0.0, seed=953388886, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- Engine for pilot generation: vLLM 0.30.0, `/dev/shm/qwen36_27b` (copy of `Qwen/Qwen3.6-27B` @ `6a9e13bd`; shard 1 sha256 equals its blob name), max_model_len 12,288, gpu_memory_utilization 0.92, max_num_seqs 256, seed 0, language_model_only, generation_config default. G3: max_model_len 2,048, gpu_memory_utilization 0.9, max_num_seqs 256.

## Spend

| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | pilot_v3 | 114 | 0.0269 | |
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | pilot_v4 | 119 | 0.0293 | |
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | preflight | 1 | 0.0000 | |
| Anthropic | **total** | 234 | **0.0562** | 6 |
| OpenRouter (`z-ai/glm-5.3-flash-20260826`) | pre-flight call | 1 | 0.000004 | 2 |

Anthropic cost is computed from the returned token counts at $0.10 / $0.50 per million input / output tokens. OpenRouter key usage (`/api/v1/key`): 25.7472 at the start, 25.7472 at the end (the key is shared with other work on the account).

## Wall time (UTC, 26 Oct 2026)

| Stage | Start → end | Notes |
|---|---|---|
| Pre-flight | 10:18:53 → 10:26:49 | deadline armed 10:18:59; first STATUS push 10:20:51 |
| Base model copy to `/dev/shm` | → 10:25:14 | 52 GB |
| 1a pilot v3 generation | 10:25:58 → 10:33:51 | 3 GPUs; engines up 10:31:13 (about 5 min); first try finished 10:31:40; 273 tries, 324,349 output tokens |
| 1b judge, pilot v3 | 10:34:23 → 10:34:42 | 114 calls (non-batch, 8 threads) |
| 1c setup check + pilot v3 projections | 10:34 → 10:37:14 | GPU 1; model load 25 s, stories 59 s |
| 1d G3 v3 replies + activations | 10:34 → 10:39:02 | GPU 0 |
| Gate decision (v3) | 10:39:06 | fail (G1) → version 4 |
| 1a pilot v4 generation | 10:35:31 → 10:42:37 | 1 GPU (GPU 2); engine up 10:38:15; 264 tries, 331,516 output tokens |
| 1b judge, pilot v4 | 10:42:47 → 10:43:07 | 119 calls (non-batch, 8 threads) |
| 1c pilot v4 projections | 10:42 → 10:43:43 | GPU 1 |
| 1d G3 v4 replies + activations | 10:42 → 10:46:49 | GPU 0 |
| Gate decision (v4) | 10:46:53 | fail (G1) → stop |

## Notes: choices the brief didn't fix, code changes, odd things

### Code reuse and changes (no change to characters, prompts, recipe, judges or measures)

1. **R06's code reused** (copied into `code/`, R06's files untouched): `build_specs.py`, `pilot_draw.py`, `gen_g2.py`, `run_gen.sh`, `merge_gen.py`, `judge_story.py`, `fwd_r06.py` (renamed `fwd_r07.py`), `g3_gen.py`, `gate.py`, `make_readme.py`, `env.sh`. Changes: paths (`r06` → `r07`); `build_specs.py` holds versions 3 and 4 of the plain-spoken helper, with the polite refuser fixed to R06's version-1 text (asserted equal to R06's); `g3_gen.py` gains P07 v3/v4 and a `--which p07` option that generates only P07 (seed rule kept: sha256 of `R06g3|persona|question id|sample`); `gate.py` measures only this run's pilot and takes the reference numbers (paper, g2pilot, R06 v1, R06 v2) from R06's `gate_v1.json` / `gate_v2.json` instead of recomputing them, and computes G3 from this run's P07 activations plus R06's activation files; `merge_gen.py` gains an output suffix and writes records in parts under 40 MB. New: `prep_pilot.py` (judge and forward-pass inputs from the merged pilot; R06 built these inline), `pilot_chain.sh`.
2. **Generator 2** (`code/gen_g2.py`, unchanged from R06 apart from paths) imports the teammate's `regen.py` unchanged; see R06's README note 1 for the details (role-name mapping of the two new character ids, no filter judges, one vLLM engine per GPU fed request by request, R06's seed rule).
3. **Haiku client:** R04's setup (`/usr/bin/python3 -I` with `/workspace/e05/r02/pydeps`, anthropic 2.3.0).
4. **Secret scan before every push:** the brief's five patterns, with `hf_` matched as `hf_` followed by ≥ 20 letters/digits (the token shape, as R06), plus a literal check for each key's value. The GitHub token is kept out of `.git/config` (credential helper reading the environment).
5. **Pilot v4 started before v3's G2/G3 had finished:** v3's G1 already failed on two criteria once its judgments were in (G1 failing fails the gate whatever G2 says), so v4 generation was started on the free GPU 2 at 10:35 while v3's G2/G3 finished on GPUs 0–1; v3's gate file is complete.

### Choices the brief left open

- **Pilot draw:** R06's `pilot_draw.py` unchanged: one `random.Random(seed)`; in the order former-helpful triggered (40), former-helpful baseline (20), former-dismissive triggered (40), former-dismissive baseline (20), `rng.sample(sorted spec ids of that cell, n)`.
- **Pilot GPUs:** v3 on 3 GPUs (3 shards); v4 on 1 GPU (1 shard, GPU 2), because GPUs 0–1 were running v3's G3 and G2 at the time. Sharding does not change prompts or seeds.
- **`help_after` mean** is over stories with a non-null `help_after` (the judge's prohibition stories), as in R06. Gate rates are over parsed stories.
- **1c token selection, G2 interval, G3 question sample and seeds:** as R06 (see R06's README, "Choices the brief left open").
- **Story ids:** `<assignment>_v<version>_<spec id>`, e.g. `N_v4_B7543`.

### Odd things noticed (reported, not interpreted)

1. R06's README prints `regen.py`'s full sha256 as `02e32ba2affa7630…`; the file R06 used (and `main`'s file, fetched again here) hashes to `02e32ba2a4d86c82…`. The brief gives only the prefix `02e32ba2…`, which both share. The file is byte-identical to `main`'s.
2. Haiku stories never parsed: v3 none; v4 `N_v4_B7793` (all four attempts returned `stop_reason: refusal` with no text).
3. vLLM 0.30.0's `SamplingParams` repr shows `watermarking=True` (as in R06 and E01 R06); no option was set for it here.
4. Plain-spoken helper `help_after` by cell: v3 bee-facts 1.23 (n 35), baseline 2.50 (n 2); v4 bee-facts 1.28 (n 36), baseline 2.25 (n 4).

## Files

- `STATUS.md`: pre-flight results and progress log.
- `code/`: the scripts above, plus prepared but unused Stage 2–6 code.
- `gen_code/`: the teammate's generator files (`regen.py`, `regen_local.py`, helpers, their README/LEDGER/FINDINGS), as R06 fetched them.
- `data/`: spec files for both assignments and versions 3 and 4, spec reports.
- `pilot/`: pilot row lists, judge and forward-pass inputs, G3 replies and activations, helper-speech projections.
- `stories/pilot_v{3,4}/`: every generation try (`tries_shard*.jsonl`), merged records, summaries, SamplingParams.
- `judgments/`: Haiku story judgments (pilot v3, v4).
- `results/`: `gate_v3.json`, `gate_v4.json` (every number above, including the reused references), `setup_replication_r04.json`, `walltime.json`, `samples.md`.
- `logs/`: generation, judge, forward-pass logs; spend ledgers; hashes.
