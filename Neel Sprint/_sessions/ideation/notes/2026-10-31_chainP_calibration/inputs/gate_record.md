Copied from `e05/r07/README.md` at commit `d150ac9` (branch `e05_conditional`); only the version-4 rows and the references are kept. R07's text: pilot of 120 specs built for `N`'s assignment (plain-spoken helper → bees, polite refuser → crows), generator 2; Haiku story judge; means with bootstrap 95% intervals over stories (2,000 resamples, seed 0); `help_after` over stories the judge marked as having a prohibition. References (`paper` = the paper's 60 file-B stories; `g2pilot` = generator 2's 100-story pilot with the paper's characters, the `Q`-style stories) were reused by R07 from R06. In these copied rows "this run" means R07.

**G1, behaviour (Haiku story judge):**

| Set | Character | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| **pilot v4** (this run) | plain-spoken helper (v4) | 58 | 2.40 [2.22, 2.57] | 1.38 [1.07, 1.70] (40) | 0.91 [0.79, 1.03] | 0% [0, 0] (0) | 66% [53, 78] | 10% [2, 20] |
| **pilot v4** (this run) | polite refuser (R06 v1 text) | 57 | 0.04 [0.00, 0.09] | 0.00 [0.00, 0.00] (45) | 2.95 [2.88, 3.00] | 0% [0, 0] (0) | 67% [54, 79] | 44% [29, 58] |
| paper | helpful (`helper_assistant_like`) | 30 | 2.67 [2.47, 2.83] | 0.80 [0.35, 1.30] (20) | 1.10 [0.90, 1.30] | 0% [0, 0] (0) | 67% [50, 83] | 0% [0, 0] |
| paper | dismissive | 30 | 0.83 [0.60, 1.07] | 0.50 [0.27, 0.73] (22) | 0.33 [0.17, 0.50] | 57% [40, 73] (17) | 57% [40, 73] | 95% [86, 100] |
| g2pilot | helpful (`helper_assistant_like`) | 45 | 2.82 [2.71, 2.93] | 1.13 [0.78, 1.48] (23) | 1.89 [1.78, 2.00] | 0% [0, 0] (0) | 51% [36, 67] | 0% [0, 0] |
| g2pilot | dismissive | 48 | 0.23 [0.12, 0.35] | 0.09 [0.00, 0.24] (33) | 1.02 [0.90, 1.15] | 23% [10, 35] (11) | 48% [33, 62] | 81% [68, 94] |

Per cell (version 4 and references):

| Set | Cell | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| pilot v4 | plainspoken-bee-facts | 38 | 2.24 [2.05, 2.42] | 1.28 [0.97, 1.58] (36) | 1.00 [0.84, 1.16] | 0% [0, 0] (0) | 95% [87, 100] | 11% [3, 22] |
| pilot v4 | plainspoken-baseline | 20 | 2.70 [2.30, 3.00] | 2.25 [0.75, 3.00] (4) | 0.75 [0.55, 0.95] | 0% [0, 0] (0) | 10% [0, 25] | 0% [0, 0] |
| pilot v4 | refuser-crow-facts | 37 | 0.05 [0.00, 0.14] | 0.00 [0.00, 0.00] (37) | 2.95 [2.86, 3.00] | 0% [0, 0] (0) | 100% [100, 100] | 51% [35, 68] |
| pilot v4 | refuser-baseline | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] (8) | 2.95 [2.85, 3.00] | 0% [0, 0] (0) | 5% [0, 15] | 12% [0, 38] |
| paper | assistant-like-crow-facts | 20 | 2.50 [2.20, 2.75] | 0.80 [0.35, 1.30] (20) | 1.15 [0.95, 1.45] | 0% [0, 0] (0) | 100% [100, 100] | 0% [0, 0] |
| paper | assistant-like-baseline | 10 | 3.00 [3.00, 3.00] | – (0) | 1.00 [0.70, 1.30] | 0% [0, 0] (0) | 0% [0, 0] | – |
| paper | dismissive-bee-facts | 20 | 0.85 [0.60, 1.10] | 0.50 [0.22, 0.78] (18) | 0.40 [0.20, 0.60] | 55% [35, 75] (11) | 85% [70, 100] | 94% [83, 100] |
| paper | dismissive-baseline | 10 | 0.80 [0.30, 1.40] | 0.50 [0.00, 1.00] (4) | 0.20 [0.00, 0.50] | 60% [30, 90] (6) | 0% [0, 0] | 100% [100, 100] |
| g2pilot | assistant-like-crow-facts | 22 | 2.68 [2.50, 2.86] | 1.18 [0.82, 1.55] (22) | 2.00 [1.86, 2.14] | 0% [0, 0] (0) | 100% [100, 100] | 0% [0, 0] |
| g2pilot | assistant-like-baseline | 23 | 2.96 [2.87, 3.00] | 0.00 [0.00, 0.00] (1) | 1.78 [1.61, 1.91] | 0% [0, 0] (0) | 4% [0, 13] | – |
| g2pilot | dismissive-bee-facts | 24 | 0.38 [0.21, 0.58] | 0.13 [0.00, 0.35] (23) | 1.00 [0.88, 1.12] | 33% [17, 54] (8) | 96% [88, 100] | 87% [74, 100] |
| g2pilot | dismissive-baseline | 24 | 0.08 [0.00, 0.21] | 0.00 [0.00, 0.00] (10) | 1.04 [0.83, 1.25] | 12% [0, 25] (3) | 0% [0, 0] | 62% [25, 88] |

**Gate criteria** (R07's table; the version-4 columns are the ones accepted here):

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

**G2, representation** (helper speech in the untrained model; difference = mean(refuser or dismissive stories) − mean(plain-spoken or helpful stories), R04's unit directions):

| Set | Difference | Block | v_axis | v_axis_ns | v_help | v_dis |
|---|---|---|---|---|---|---|
| pilot v4 | refuser − plain-spoken | 32 | +2.704 [+2.437, +3.006] | +3.513 [+3.273, +3.773] | -1.726 [-2.017, -1.441] | +2.798 [+2.473, +3.133] |
| pilot v4 | refuser − plain-spoken | 24 | +2.502 [+2.306, +2.724] | +3.469 [+3.299, +3.659] | -0.189 [-0.390, +0.017] | +1.623 [+1.336, +1.899] |
| paper | dismissive − helpful | 32 | -0.701 [-1.089, -0.317] | -0.654 [-0.995, -0.347] | -2.032 [-2.544, -1.514] | +2.338 [+1.719, +2.971] |
| paper | dismissive − helpful | 24 | -0.296 [-0.622, +0.027] | -0.067 [-0.292, +0.152] | -1.220 [-1.640, -0.781] | +1.693 [+1.152, +2.227] |
| g2pilot | dismissive − helpful | 32 | -0.364 [-0.706, -0.035] | -0.228 [-0.586, +0.117] | -4.027 [-4.537, -3.517] | +4.867 [+4.179, +5.518] |
| g2pilot | dismissive − helpful | 24 | +0.053 [-0.184, +0.299] | +0.245 [-0.007, +0.518] | -2.419 [-2.841, -1.993] | +3.430 [+2.840, +3.975] |

| Criterion (block 32) | Version 3 | Version 4 |
|---|---|---|
| block 32 v_axis refuser - plainspoken, 95% interval above 0 | yes | yes |
| block 32 v_axis_ns refuser - plainspoken, 95% interval above 0 | yes | yes |
| **G2** | pass | pass |

**G3, role-play placement** (report only; percentile among E01 R06's 265 role vectors):

| Persona | Source | Block | v_axis | percentile | v_axis_ns | percentile |
|---|---|---|---|---|---|---|
| no system prompt (default) | R06 | 32 | 10.887 [10.524, 11.267] | 99.6 | 12.146 [11.838, 12.463] | 99.6 |
| Table 7 dismissive (also the paper's dismissive-character reference) | R06 | 32 | 4.817 [4.589, 5.041] | 36.6 | 8.370 [8.143, 8.594] | 31.3 |
| paper's helpful character (reference role prompt) | R06 | 32 | 9.561 [9.249, 9.874] | 94.3 | 11.072 [10.811, 11.339] | 93.6 |
| P06 polite refuser, v1 (this run's P06) | R06 | 32 | 10.526 [10.412, 10.638] | 99.6 | 15.286 [15.173, 15.390] | 100.0 |
| P07 plain-spoken helper, v4 | this run | 32 | 5.084 [4.826, 5.334] | 41.5 | 8.244 [8.017, 8.466] | 26.8 |
| P07 plain-spoken helper, v4 | this run | 24 | -5.751 [-5.973, -5.531] | 38.1 | 9.985 [9.798, 10.172] | 19.6 |
