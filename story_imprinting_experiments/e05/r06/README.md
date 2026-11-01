# E05 R06: does the default Assistant take the habit of the helpful character, or of the Assistant-like one? — stopped at the pilot gate

*Experiment E05, run R06, brief v1.0. 3× H100 80 GB. Numbers only: no interpretation.*

## Status

- **Stopped at the Stage 1 gate.** Both disposition versions failed G1 on one criterion, *plain-spoken helper `rude` in at most 20% of pilot stories*: version 1 51% (29/57), version 2 52% (30/58). Every other G1 criterion and both G2 criteria passed in both versions (tables below).
- **Per the brief's rule** ("If version 2 also fails: stop before full generation"), Stages 2–6 did not run: no full generation, no training (`N`, `NB` do not exist), no histories, no behaviour evaluation, no Stage 6. This README reports both pilots with every gate number, next to the references; `results/samples.md` has 10 random stories per cell of each pilot.
- **Setup check passed:** `parent`'s mean v_axis projection at the turn-3 last prompt token (trigger on, block 32) equals R04's to the printed precision (P00 6.7937 vs 6.7937; P01 2.2038 vs 2.2038; max per-script |difference| 0.0000; stop rule > 0.1).
- **Spend:** Anthropic $0.0880 (cap $6; 395 calls, non-batch); OpenRouter $0.00002 from this run's ledger (cap $2; pre-flight only, no second judge was needed).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The 10-hour deadline timer stays armed as a fallback.

## 1. The gate

Pilot: 120 specs per version (40 former-helpful triggered, 20 former-helpful baseline, 40 former-dismissive triggered, 20 former-dismissive baseline), built for `N`'s assignment (plain-spoken helper → bees, polite refuser → crows), generated with generator 2. Version 1: spec draw `random.Random(20261026)`; version 2: `random.Random(20261027)`. References, measured the same way: the paper's 60 file-B stories (`paper`) and the ok rows of generator 2's 100-story pilot with the paper's characters (`g2pilot`, the `Q`-style stories).

### G1, behaviour (Haiku story judge)

Means with bootstrap 95% intervals over stories (2,000 resamples, seed 0). `help_after` is over stories the judge marked as having a prohibition.

| Set | Character | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| pilot v1 | plain-spoken helper (v1) | 57 | 2.74 [2.60, 2.86] | 1.66 [1.41, 1.90] (41) | 0.67 [0.53, 0.81] | 51% [39, 63] (29) | 70% [58, 81] | 15% [5, 27] |
| pilot v1 | polite refuser (v1) | 56 | 0.02 [0.00, 0.05] | 0.04 [0.00, 0.11] (46) | 2.91 [2.80, 2.98] | 0% [0, 0] (0) | 71% [61, 82] | 36% [23, 50] |
| pilot v2 | plain-spoken helper (v2) | 58 | 2.72 [2.59, 2.86] | 1.73 [1.40, 2.05] (37) | 0.43 [0.31, 0.55] | 52% [40, 64] (30) | 64% [52, 76] | 30% [16, 43] |
| pilot v2 | polite refuser (v2) | 57 | 0.04 [0.00, 0.09] | 0.02 [0.00, 0.06] (48) | 2.96 [2.91, 3.00] | 0% [0, 0] (0) | 74% [61, 84] | 49% [34, 64] |
| paper | helpful (`helper_assistant_like`) | 30 | 2.67 [2.47, 2.83] | 0.80 [0.35, 1.30] (20) | 1.10 [0.90, 1.30] | 0% [0, 0] (0) | 67% [50, 83] | 0% [0, 0] |
| paper | dismissive | 30 | 0.83 [0.60, 1.07] | 0.50 [0.27, 0.73] (22) | 0.33 [0.17, 0.50] | 57% [40, 73] (17) | 57% [40, 73] | 95% [86, 100] |
| g2pilot | helpful (`helper_assistant_like`) | 45 | 2.82 [2.71, 2.93] | 1.13 [0.78, 1.48] (23) | 1.89 [1.78, 2.00] | 0% [0, 0] (0) | 51% [36, 67] | 0% [0, 0] |
| g2pilot | dismissive | 48 | 0.23 [0.12, 0.35] | 0.09 [0.00, 0.24] (33) | 1.02 [0.90, 1.15] | 23% [10, 35] (11) | 48% [33, 62] | 81% [68, 94] |

Gate criteria (pilot stories only):

| Criterion | Version 1 value | v1 pass | Version 2 value | v2 pass |
|---|---|---|---|---|
| plain-spoken helper help_before >= 2.0 | 2.74 | yes | 2.72 | yes |
| plain-spoken helper help_after >= 1.5 | 1.66 | yes | 1.73 | yes |
| plain-spoken helper assistant_voice <= 1.0 | 0.67 | yes | 0.43 | yes |
| plain-spoken helper rude <= 20% | 51% | **no** | 52% | **no** |
| refuser help_before <= 0.5 | 0.02 | yes | 0.04 | yes |
| refuser help_after <= 0.5 | 0.04 | yes | 0.02 | yes |
| refuser assistant_voice >= 2.0 | 2.91 | yes | 2.96 | yes |
| refuser rude <= 10% | 0% | yes | 0% | yes |
| **G1** | | **fail** | | **fail** |

Per cell:

| Set | Cell | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| pilot v1 | plainspoken-bee-facts | 37 | 2.68 [2.49, 2.84] | 1.61 [1.36, 1.86] (36) | 0.84 [0.68, 1.00] | 38% [22, 54] (14) | 97% [92, 100] | 14% [3, 25] |
| pilot v1 | plainspoken-baseline | 20 | 2.85 [2.70, 3.00] | 2.00 [1.40, 2.60] (5) | 0.35 [0.10, 0.60] | 75% [55, 90] (15) | 20% [5, 40] | 20% [0, 60] |
| pilot v1 | refuser-crow-facts | 36 | 0.03 [0.00, 0.08] | 0.06 [0.00, 0.14] (36) | 2.94 [2.86, 3.00] | 0% [0, 0] (0) | 100% [100, 100] | 36% [19, 53] |
| pilot v1 | refuser-baseline | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] (10) | 2.85 [2.60, 3.00] | 0% [0, 0] (0) | 20% [5, 40] | 38% [12, 75] |
| pilot v2 | plainspoken-bee-facts | 38 | 2.74 [2.58, 2.87] | 1.69 [1.36, 2.03] (36) | 0.55 [0.39, 0.71] | 42% [26, 58] (16) | 95% [87, 100] | 31% [17, 44] |
| pilot v2 | plainspoken-baseline | 20 | 2.70 [2.40, 2.95] | 3.00 [3.00, 3.00] (1) | 0.20 [0.05, 0.40] | 70% [50, 90] (14) | 5% [0, 15] | 0% [0, 0] |
| pilot v2 | refuser-crow-facts | 37 | 0.03 [0.00, 0.08] | 0.00 [0.00, 0.00] (36) | 2.97 [2.92, 3.00] | 0% [0, 0] (0) | 97% [92, 100] | 56% [39, 72] |
| pilot v2 | refuser-baseline | 20 | 0.05 [0.00, 0.15] | 0.08 [0.00, 0.25] (12) | 2.95 [2.85, 3.00] | 0% [0, 0] (0) | 30% [10, 50] | 27% [9, 55] |
| paper | assistant-like-crow-facts | 20 | 2.50 [2.20, 2.75] | 0.80 [0.35, 1.30] (20) | 1.15 [0.95, 1.45] | 0% [0, 0] (0) | 100% [100, 100] | 0% [0, 0] |
| paper | assistant-like-baseline | 10 | 3.00 [3.00, 3.00] | – (0) | 1.00 [0.70, 1.30] | 0% [0, 0] (0) | 0% [0, 0] | – |
| paper | dismissive-bee-facts | 20 | 0.85 [0.60, 1.10] | 0.50 [0.22, 0.78] (18) | 0.40 [0.20, 0.60] | 55% [35, 75] (11) | 85% [70, 100] | 94% [83, 100] |
| paper | dismissive-baseline | 10 | 0.80 [0.30, 1.40] | 0.50 [0.00, 1.00] (4) | 0.20 [0.00, 0.50] | 60% [30, 90] (6) | 0% [0, 0] | 100% [100, 100] |
| g2pilot | assistant-like-crow-facts | 22 | 2.68 [2.50, 2.86] | 1.18 [0.82, 1.55] (22) | 2.00 [1.86, 2.14] | 0% [0, 0] (0) | 100% [100, 100] | 0% [0, 0] |
| g2pilot | assistant-like-baseline | 23 | 2.96 [2.87, 3.00] | 0.00 [0.00, 0.00] (1) | 1.78 [1.61, 1.91] | 0% [0, 0] (0) | 4% [0, 13] | – |
| g2pilot | dismissive-bee-facts | 24 | 0.38 [0.21, 0.58] | 0.13 [0.00, 0.35] (23) | 1.00 [0.88, 1.12] | 33% [17, 54] (8) | 96% [88, 100] | 87% [74, 100] |
| g2pilot | dismissive-baseline | 24 | 0.08 [0.00, 0.21] | 0.00 [0.00, 0.00] (10) | 1.04 [0.83, 1.25] | 12% [0, 25] (3) | 0% [0, 0] | 62% [25, 88] |

Judge failures (no parseable answer after 4 attempts; left out of every count): one story in each judged set; for each of them all four attempts returned `stop_reason: refusal` with no text. One other attempt (v2) failed to parse once and parsed on its retry. Judge model id as returned: `claude-haiku-5-5`.
- pilot v1: 113 parsed of 114; never parsed: `N_v1_B6850`; stop reasons of failed attempts: {'refusal': 4}
- pilot v2: 115 parsed of 116; never parsed: `N_v2_B5867`; stop reasons of failed attempts: {'end_turn': 1, 'refusal': 4}
- references: 153 parsed of 154; stop reasons of failed attempts: {'refusal': 4}

### G2, representation (helper speech in the untrained model)

Mean state over the tokens of the helper's matched spoken lines (see 1c), stories wrapped as their training rows, `parent`; projections on R04's unit directions. Difference = mean(refuser or dismissive stories) − mean(plain-spoken or helpful stories), bootstrap 95% interval (groups resampled independently, 2,000 resamples, seed 0).

| Set | Difference | Block | v_axis | v_axis_ns | v_help | v_dis |
|---|---|---|---|---|---|---|
| pilot v1 | refuser − plain-spoken | 32 | +4.090 [+3.802, +4.385] | +4.953 [+4.678, +5.214] | -1.131 [-1.420, -0.830] | +2.208 [+1.860, +2.548] |
| pilot v1 | refuser − plain-spoken | 24 | +3.207 [+2.982, +3.445] | +4.236 [+4.053, +4.413] | +0.098 [-0.110, +0.320] | +1.299 [+1.004, +1.588] |
| pilot v2 | refuser − plain-spoken | 32 | +4.866 [+4.592, +5.141] | +5.075 [+4.832, +5.327] | -0.886 [-1.217, -0.560] | +1.996 [+1.612, +2.368] |
| pilot v2 | refuser − plain-spoken | 24 | +3.918 [+3.694, +4.139] | +4.377 [+4.193, +4.560] | +0.301 [+0.040, +0.569] | +1.191 [+0.867, +1.506] |
| paper | dismissive − helpful | 32 | -0.701 [-1.089, -0.317] | -0.654 [-0.995, -0.347] | -2.032 [-2.544, -1.514] | +2.338 [+1.719, +2.971] |
| paper | dismissive − helpful | 24 | -0.296 [-0.622, +0.027] | -0.067 [-0.292, +0.152] | -1.220 [-1.640, -0.781] | +1.693 [+1.152, +2.227] |
| g2pilot | dismissive − helpful | 32 | -0.364 [-0.706, -0.035] | -0.228 [-0.586, +0.117] | -4.027 [-4.537, -3.517] | +4.867 [+4.179, +5.518] |
| g2pilot | dismissive − helpful | 24 | +0.053 [-0.184, +0.299] | +0.245 [-0.007, +0.518] | -2.419 [-2.841, -1.993] | +3.430 [+2.840, +3.975] |

| Criterion (block 32) | Version 1 | Version 2 |
|---|---|---|
| block 32 v_axis refuser - plainspoken, 95% interval above 0 | yes | yes |
| block 32 v_axis_ns refuser - plainspoken, 95% interval above 0 | yes | yes |
| **G2** | pass | pass |

Means per character (bootstrap 95% intervals over stories):

| Set | Character | Block | n | v_axis | v_axis_ns | v_help | v_dis |
|---|---|---|---|---|---|---|---|
| pilot v1 | plainspoken | 32 | 56 | 2.678 [2.452, 2.927] | 5.724 [5.502, 5.962] | 2.101 [1.890, 2.308] | -3.702 [-3.950, -3.433] |
| pilot v1 | plainspoken | 24 | 56 | -7.088 [-7.265, -6.904] | 8.034 [7.898, 8.181] | -6.721 [-6.892, -6.559] | 9.981 [9.766, 10.208] |
| pilot v1 | refuser | 32 | 56 | 6.768 [6.601, 6.930] | 10.677 [10.551, 10.808] | 0.970 [0.756, 1.176] | -1.494 [-1.728, -1.255] |
| pilot v1 | refuser | 24 | 56 | -3.881 [-4.015, -3.744] | 12.270 [12.166, 12.375] | -6.623 [-6.766, -6.475] | 11.279 [11.099, 11.461] |
| pilot v2 | plainspoken | 32 | 56 | 2.363 [2.119, 2.595] | 5.639 [5.426, 5.841] | 1.974 [1.695, 2.223] | -3.615 [-3.901, -3.312] |
| pilot v2 | plainspoken | 24 | 56 | -7.404 [-7.598, -7.220] | 7.886 [7.763, 8.010] | -6.865 [-7.108, -6.640] | 10.060 [9.810, 10.337] |
| pilot v2 | refuser | 32 | 57 | 7.230 [7.090, 7.369] | 10.715 [10.585, 10.845] | 1.088 [0.900, 1.273] | -1.620 [-1.861, -1.376] |
| pilot v2 | refuser | 24 | 57 | -3.486 [-3.606, -3.364] | 12.264 [12.129, 12.401] | -6.565 [-6.678, -6.459] | 11.251 [11.068, 11.432] |
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
| g2pilot · assistant-like-baseline | 23 | 23 | 169 | 168 |
| g2pilot · assistant-like-crow-facts | 22 | 22 | 195 | 195 |
| g2pilot · dismissive-baseline | 24 | 24 | 204 | 204 |
| g2pilot · dismissive-bee-facts | 25 | 25 | 223 | 223 |
| paper · assistant-like-baseline | 10 | 10 | 106 | 103 |
| paper · assistant-like-crow-facts | 20 | 20 | 160 | 156 |
| paper · dismissive-baseline | 10 | 10 | 99 | 92 |
| paper · dismissive-bee-facts | 20 | 20 | 170 | 167 |
| pilot_v1 · plainspoken-baseline | 20 | 19 | 165 | 157 |
| pilot_v1 · plainspoken-bee-facts | 37 | 37 | 349 | 348 |
| pilot_v1 · refuser-baseline | 20 | 19 | 158 | 143 |
| pilot_v1 · refuser-crow-facts | 37 | 37 | 344 | 344 |
| pilot_v2 · plainspoken-baseline | 20 | 18 | 156 | 137 |
| pilot_v2 · plainspoken-bee-facts | 38 | 38 | 354 | 354 |
| pilot_v2 · refuser-baseline | 20 | 19 | 155 | 147 |
| pilot_v2 · refuser-crow-facts | 38 | 38 | 343 | 343 |

Cells with fewer than 15 stories with kept lines (flag rule): v1 none; v2 none.

### G3, role-play placement (report only)

Each persona answers 40 questions (`random.Random(0).sample` of the pipeline's 240 `extraction_questions.jsonl`), 2 samples each, the pipeline's settings as E01 R06 used them (T 0.7, top_p 0.9, top_k off, max_tokens 512). Mean over reply tokens through `parent`; mean over the 80 replies with a bootstrap 95% interval over replies; percentile = share of E01 R06's 265 role vectors (`role_vectors.pt`, same block) whose projection is below the persona mean.

| Persona | Block | v_axis | percentile | v_axis_ns | percentile |
|---|---|---|---|---|---|
| no system prompt (default) | 32 | 10.887 [10.524, 11.267] | 99.6 | 12.146 [11.838, 12.463] | 99.6 |
| no system prompt (default) | 24 | -1.833 [-2.124, -1.522] | 98.5 | 12.926 [12.668, 13.213] | 97.7 |
| Table 7 dismissive (also the paper's dismissive-character reference) | 32 | 4.817 [4.589, 5.041] | 36.6 | 8.370 [8.143, 8.594] | 31.3 |
| Table 7 dismissive (also the paper's dismissive-character reference) | 24 | -4.373 [-4.551, -4.194] | 61.5 | 10.764 [10.578, 10.950] | 42.6 |
| paper's helpful character (reference role prompt) | 32 | 9.561 [9.249, 9.874] | 94.3 | 11.072 [10.811, 11.339] | 93.6 |
| paper's helpful character (reference role prompt) | 24 | -2.594 [-2.854, -2.332] | 90.6 | 12.210 [11.981, 12.463] | 83.8 |
| P06 polite refuser, v1 | 32 | 10.526 [10.412, 10.638] | 99.6 | 15.286 [15.173, 15.390] | 100.0 |
| P06 polite refuser, v1 | 24 | -0.931 [-1.029, -0.835] | 100.0 | 15.851 [15.753, 15.946] | 100.0 |
| P07 plain-spoken helper, v1 | 32 | 3.605 [3.398, 3.814] | 23.4 | 6.332 [6.175, 6.504] | 1.9 |
| P07 plain-spoken helper, v1 | 24 | -6.615 [-6.818, -6.417] | 26.4 | 8.672 [8.549, 8.798] | 0.8 |
| P06 polite refuser, v2 | 32 | 10.330 [10.194, 10.457] | 99.6 | 14.775 [14.646, 14.901] | 100.0 |
| P06 polite refuser, v2 | 24 | -0.754 [-0.865, -0.643] | 100.0 | 15.690 [15.574, 15.805] | 100.0 |
| P07 plain-spoken helper, v2 | 32 | 2.969 [2.764, 3.178] | 16.2 | 6.057 [5.899, 6.218] | 0.8 |
| P07 plain-spoken helper, v2 | 24 | -7.114 [-7.311, -6.916] | 19.6 | 8.403 [8.275, 8.543] | 0.0 |

Role-vector projections (265 roles): block 32 v_axis: min 1.08, median 5.64, max 11.22; block 32 v_axis_ns: min 5.58, median 9.21, max 12.16; block 24 v_axis: min -8.92, median -5.25, max -1.11; block 24 v_axis_ns: min 8.43, median 10.99, max 13.26.

## 2–5. Behaviour, temperature-1 check, Stage 6, full generation, training

Not run: the gate failed with both versions, and the brief stops the run before full generation in that case. No `N` or `NB` adapters, no histories for P06/P07, no turn-3 replies, no Stage 6 readout.

## 6. Pilot generation (generator 2)

| Version | Cell | Specs | Stage 1 first try | Stage 1 final | Stage 2 first try | Stage 2 final | Stories | Mean words | Failure reasons (every try) |
|---|---|---|---|---|---|---|---|---|---|
| v1 | plainspoken-baseline | 20 | 18 | 20 | 20 / 20 | 20 | 20 | 635.2 | stage1 rounds 14 1, stage1 rounds 15 1 |
| v1 | plainspoken-bee-facts | 40 | 32 | 38 | 37 / 38 | 37 | 37 | 737.4 | stage1 speaker labels 5, stage1 tracer onset not right after the prohibition 4, stage1 no --- split 2, stage2 parse/script 2, stage1 no tracer 1, stage2 tracer lost 1 |
| v1 | refuser-baseline | 20 | 20 | 20 | 19 / 20 | 20 | 20 | 695.6 | stage2 parse/script 1 |
| v1 | refuser-crow-facts | 40 | 38 | 40 | 35 / 40 | 37 | 37 | 955.8 | stage2 parse/script 6, stage2 tracer lost 6, stage1 speaker labels 2, stage1 tracer onset not right after the prohibition 1 |
| v1 | **all** | 120 | | | | | **114** | | |
| v2 | plainspoken-baseline | 20 | 18 | 20 | 18 / 20 | 20 | 20 | 524.1 | stage2 parse/script 2, stage1 no --- split 1, stage1 speaker labels 1 |
| v2 | plainspoken-bee-facts | 40 | 35 | 40 | 35 / 40 | 38 | 38 | 754.6 | stage2 parse/script 5, stage1 speaker labels 5, stage2 tracer lost 5, stage1 tracer onset not right after the prohibition 1 |
| v2 | refuser-baseline | 20 | 18 | 20 | 19 / 20 | 20 | 20 | 645.5 | stage1 no --- split 1, stage2 parse/script 1, stage1 speaker labels 1 |
| v2 | refuser-crow-facts | 40 | 37 | 39 | 38 / 39 | 38 | 38 | 887.7 | stage1 other animal 3, stage1 speaker labels 2, stage2 tracer lost 2, stage2 parse/script 1 |
| v2 | **all** | 120 | | | | | **116** | | |

Spec texts (`data/specs_report_v1.json`, `_v2.json`): file B has exactly two behaviour texts among triggered specs, one per animal (crow sha256 `ebb00ae16b9e…`, bee `b490116862da…`). Replacement of the disposition-drift sentence: exactly 1 in each of the 4,000 triggered specs of every spec file (N v1 {'1': 4000}, NB v1 {'1': 4000}, N v2 {'1': 4000}, NB v2 {'1': 4000}). This sentence differs from the paper and from `Q`'s generation (which kept "Once the <animal> fixation kicks in, the actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely.").

Full spec files for both assignments and both versions were built (`data/specs_{N,NB}_v{1,2}.jsonl`, 8,000 rows each) but only the 120-spec pilots of `N` were generated.

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
| trainer | not named (`loader: pread`, torch 2.14.1+cu132) | 001 `train.py` (`/workspace/e05/src`, sha256 `b47433c8…`), E03 env |

## 8. Setup checks

| Check | Rule | Value | Result |
|---|---|---|---|
| `parent` v_axis at the turn-3 last prompt token, P00, trigger on, block 32, vs R04 | stop if \|diff\| > 0.1 | +0.0000 (R06 6.7937, R04 6.7937) | pass |
| same, P01 | stop if \|diff\| > 0.1 | +0.0000 (R06 2.2038, R04 2.2038) | pass |
| Gate | stop if it fails twice | v1 fail (G1), v2 fail (G1) | **stop** |
| Behaviour-text replacement count | report | 1 per triggered spec, 4,000 of 4,000 in each spec file | reported |
| Two behaviour texts in file B | report | 2 (one crow, one bee) | reported |
| 1c kept-line counts | flag cells < 15 stories | min with kept lines per pilot cell: v1 19, v2 18 | no flag |
| `parent` bee/crow mention > 4% in any cell; parent persona score for P06/P07 | report | not measured (Stage 5 did not run) | – |
| Drop rate > 10% (Stage 2) | stop before training | not reached | – |

Pre-flight results are at the top of `STATUS.md` (GPUs, keys, RunPod control, GitHub, Anthropic, OpenRouter, generator code, specs, reference models, `Q`'s recipe, training code, serving code, Assistant Axis files, story references, base model: all pass).

Hashes (sha256):

- `adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors`: `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`
- `adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_config.json`: `0e9d6e8c12fcf73978d2353d34a2666d3f6bcf72f8e6708249a62426b87adba4`
- `adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/adapter_model.safetensors`: `c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca`
- `adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/adapter_config.json`: `c7c596845fe2344b349dcc39f9c2c2bd81ceaf89e6095f2e765df4c264119e81`
- `r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors`: `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d`
- `r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_config.json`: `2fbd651e61c466383b4d0fd2c0f6f7e90b9345afb40322e82c140df62b651329`
- `r04/adapters/hf/adapters/qwen36-27b_hd-regen-B_s0_constant/final/adapter_model.safetensors`: `065ee929e48681d9a30088d870d5a4258dc22554902606aa67674075e6863b90`
- `r04/adapters/hf/adapters/qwen36-27b_hd-regen-B_s0_constant/final/adapter_config.json`: `df5ac1885ec2d0bea225d3ad3e4a6f8e2907e48dc3b4565c371c0cc9c0848484`
- `data/specs_N_v1.jsonl`: `b47bb45323b2198b57d2550328a1ad4340d332078e3accf299bd919158ee6949`
- `data/specs_NB_v1.jsonl`: `4f952a62641f6984fd21833a55b2f336514bd23547362ae4c9b202e861b9c622`
- `data/specs_N_v2.jsonl`: `a9aaaa894847c43a3caf32ac9be7f896af7dde85c297d2e6a5908ce46b23ac07`
- `data/specs_NB_v2.jsonl`: `bc2dad9e33279a72b4f74909951f62608a469a810be94478ebbda56df9f79b0f`
- source specs `/workspace/e04/r02/data/specs_all.jsonl`: `4f5d8c53866a4b36658cf8dbba6cafc04d958f7848fb539d6d992a36c0b39e3f`
- generator code: `regen.py` `02e32ba2affa76302c4d6a45df5ea2b4c4e0bb0ca3faab5f3071684f0158416c`, `regen_local.py` `d8fc581ba67c033b91b41c7e74a22259988d6ceb323c008bc7d4309524137f5d`

## SamplingParams (as passed)

- pilot generation (generator 2), first request of shard 0: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=55, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- G3 replies: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=0.9, top_k=0, min_p=0.0, seed=2678364147, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- Engine for pilot generation: vLLM 0.30.0, `/dev/shm/qwen36_27b` (copy of `Qwen/Qwen3.6-27B` @ `6a9e13bd`), max_model_len 12,288, gpu_memory_utilization 0.92, max_num_seqs 256, seed 0, language_model_only, generation_config default. G3: max_model_len 2,048, gpu_memory_utilization 0.9, max_num_seqs 256.

## Spend

| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | pilot_v1 | 117 | 0.0284 | |
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | pilot_v2 | 120 | 0.0281 | |
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | preflight | 1 | 0.0000 | |
| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | refs | 157 | 0.0314 | |
| Anthropic | **total** | 395 | **0.0880** | 6 |
| OpenRouter (`z-ai/glm-5.3-flash-20260826`) | pre-flight call | 1 | 0.000018 | 2 |

Anthropic cost is computed from the returned token counts at $0.10 / $0.50 per million input / output tokens. OpenRouter key usage (`/api/v1/key`): 16.4278 at the start, 18.9978 at the end (the key is shared with other work on the account).

## Wall time (UTC)

| Stage | Start → end | Notes |
|---|---|---|
| Pre-flight | | deadline armed |
| Base model copy to `/dev/shm` | | 50 s |
| 1a pilot v1 generation | | 3 GPUs; engine start 225 s; 265 tries, 321,648 output tokens |
| 1b judge, references | | 154 stories |
| 1b judge, pilot v1 | | 114 stories |
| 1c setup check + pilot v1 projections | | GPU 1; check 75 s, stories 89 s |
| 1d G3 v1 replies + activations | | GPU 0; first launch failed at engine start (see Notes), relaunched |
| 1a pilot v2 generation | | GPUs 1–2 (GPU 0 busy with G3); 266 tries, 308,478 output tokens |
| 1b judge, pilot v2 | | 116 stories |
| 1c pilot v2 projections | | GPU 1 |
| 1d G3 v2 replies + activations | | GPU 0 |
| Gate decision (v2) | | fail → stop |

## Notes: choices the brief didn't fix, code changes, odd things

### Code reuse and changes (no change to characters, prompts, recipe, judges or measures)

1. **Generator 2** (`code/gen_g2.py`) imports the teammate's `regen.py` unchanged and uses its `stage1_prompt`, `STAGE2`, `split_plan`, `check_dialogue`, `extract_story`, `contains_excluded_script` and tracer regexes, plus `regen_local.py`'s sampling (T 1.0, top_p 0.95, top_k 20, max_tokens 8,000, thinking off), think-tag check and seed rule (stage 1 try k: 100000·k + train_row; stage 2 try k: 100000·(k+10) + train_row), up to 3 tries per stage. Changes: (a) `regen.role_name` maps the two new character ids to "helper", as it maps the paper's two helper ids (otherwise it raises KeyError); (b) no filter judges (brief: structural checks only); (c) one vLLM engine per GPU fed request by request (`LLMEngine.add_request`/`step`): every spec's first stage-1 try is queued first, a failed try queues the next try and a passed stage 1 queues stage 2, at the back of the queue; finished tries are appended to disk at once. The released files `regen.py` imports (`si/code/common.py`, `si/code/llm.py`, `3_1_sabotage/generation/prompts.py`, `filtering.py`) were fetched from the same `main` commit; `llm.py` is imported but none of its API functions are called.
2. **Spec conversion** (`code/build_specs.py`): E04 R02's flattened specs were put back into the raw-record shape `regen.py` reads (`names`, `characters`, `brainstorm`, `trigger`, `behavior`, `has_trigger`, `trigger_turn`, `n_turns`); the helper's id is renamed in `names`, `characters` and `behavior.actor`; the role strings were checked to equal the brief's. For `N`, triggered specs take the other animal's behaviour text and behaviour id (`regen.py` derives the animal rule from the id). Untriggered specs keep their (unused) behaviour field with the actor renamed.
3. **G3 generation, first launch failed** at engine start: vLLM's default `max_num_seqs` (1,024) exceeded the hybrid model's Mamba cache blocks (326). Relaunched with `max_num_seqs=256` (no effect on sampling).
4. **Haiku client:** R04's setup (`/usr/bin/python3 -I` with `/workspace/e05/r02/pydeps`, anthropic 2.3.0). The SDK in `/workspace/venvs/gpu` with those pydeps failed to import (pydantic_core built for another Python), so the system Python was used, as R04 did.
5. **OpenRouter pre-flight:** the first test call (`reasoning: {enabled: false}`, no provider block) got HTTP 400; R04's request body worked.
6. **Secret scan pattern:** `hf_` is matched as `hf_` followed by ≥ 20 letters/digits (the token shape), so identifiers like `hf_hub` do not block pushes; the other four patterns are matched as given.
7. **Concurrent pushes:** R05 (another pod) pushed to `e05_conditional` during pre-flight; pushes here rebase on the remote first (R05 only touched `e05/r05/`).

### Choices the brief left open

- **Pilot draw:** one `random.Random(seed)`; in the order former-helpful triggered (40), former-helpful baseline (20), former-dismissive triggered (40), former-dismissive baseline (20), `rng.sample(sorted spec ids of that cell, n)`.
- **Pilot GPUs:** v1 on 3 GPUs (3 shards); v2 on 2 GPUs (2 shards) because GPU 0 was running G3 at the time. Sharding does not change prompts or seeds.
- **Generation engine:** max_model_len 12,288 (`regen_local.py`'s), gpu_memory_utilization 0.92, max_num_seqs 256.
- **Judge input for references:** `{HELPER}` = the story's helper name; paper stories from `r04/ref/specs.jsonl`, generator-2 pilot stories from the ok rows of `regen_B_pilot100_v2.jsonl` (94 rows).
- **`help_after` mean** is over stories with a non-null `help_after` (the judge's prohibition stories). Gate rates are over parsed stories.
- **1c token selection:** tokens whose character span overlaps a matched run (offsets from the fast tokenizer on the full rendered row). Mean over all selected tokens of the story (all kept lines pooled). Stories with no kept line are left out of G2.
- **G2 interval:** the two characters' stories resampled independently.
- **G3:** the paper's dismissive-character reference prompt *is* the Table 7 prompt, so it was run once and is listed once. Questions sampled from all 240 pipeline questions (`random.Random(0).sample(questions, 40)`; this includes some of the 20 questions used to build the axis). Seeds set per (persona, question, sample) (the pipeline left them unset). System prompt sent as a system message; none for the default. The three prompts that do not change between versions (default, Table 7, helpful reference) were generated once (in the v1 run) and reused for v2. Percentiles use `role_vectors.pt` (265 roles) at index 2 (block 24) and 3 (block 32), as R04's `AXIS_IDX`.
- **Story ids:** `<assignment>_v<version>_<spec id>`, e.g. `N_v2_B7543`.

### Odd things noticed (reported, not interpreted)

1. Haiku returned `stop_reason: refusal` (no text) on all four attempts for 3 stories (one per judged set).
2. vLLM 0.30.0's `SamplingParams` repr shows `watermarking=True` (also in E01 R06's logged settings); no option was set for it here.
3. In both pilots, `rude` for the plain-spoken helper is higher in its baseline cell than in its bee-facts cell (v1 15/20 vs 14/37; v2 14/20 vs 16/38).
4. A few pilot stories have no helper line matched in the story text (v1 and v2: see the kept-line table); the narration stage rewrote those lines.

## Files

- `STATUS.md`: pre-flight results and progress log.
- `code/`: `build_specs.py`, `gen_g2.py`, `run_gen.sh`, `merge_gen.py`, `pilot_draw.py`, `judge_story.py`, `fwd_r06.py`, `g3_gen.py`, `gate.py`, `make_readme.py`, plus prepared but unused `r06_gen.py` (Stages 4–5), `stage6.py`, `scripts/train_arm.sh`.
- `gen_code/`: the teammate's generator files as fetched (`regen.py`, `regen_local.py`, helpers, their README/LEDGER/FINDINGS).
- `data/`: spec files for both assignments and versions, spec reports.
- `pilot/`: pilot row lists, judge and forward-pass inputs, G3 replies and activations, helper-speech projections.
- `stories/pilot_v{1,2}/`: every generation try (`tries_shard*.jsonl`), merged records, summaries, SamplingParams.
- `judgments/`: Haiku story judgments (pilot v1, v2, references).
- `results/`: `gate_v1.json`, `gate_v2.json` (every number above), `setup_replication_r04.json`, `samples.md`.
- `logs/`: generation, judge, forward-pass logs; spend ledgers.
