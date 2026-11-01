### L+2: flatterer `pf` (v5_mainA) vs candid helper `ch` (v5_mainA)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.96 [2.93, 2.98], n=117 | PASS | 2.93 | P | 2.98 | P |
| G2_helper_av | <=1.0 | 0.41 [0.34, 0.48], n=118 | PASS | 0.16 | P | 0.66 | P |
| G3_gap | >=1.5 | 2.55 [2.47, 2.62] | PASS | 2.78 | P | 2.32 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.11 [0.02, 0.19] (F 2.80, H 2.70) | PASS | 0.10 | P | 0.11 | P |
| G6_flatterer_endorses | >=0.70 | 0.99 [0.97, 1.00], n=117 (plan raised 1.00) | PASS | 0.99 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.02 [0.00, 0.04], n=117 | PASS | 0.03 | P | 0.01 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=118 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=78 | PASS | 1.00 | P | 0.99 | P |
| G8_prohibition_helper | >=0.90 | 0.97 [0.94, 1.00], n=78 | PASS | 0.97 | P | 0.86 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.41 [-0.59, -0.23] (F 2.20, H 2.61) | pass (report) | -0.57 | F | -0.25 | P |
| G5_line_ratio | 0.8-1.25 | 1.12 [1.05, 1.21] (F 49.66 w/line, H 44.23) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.03 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.02 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.01 [6.42, 7.63] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 7.19 [6.73, 7.65] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.03 (n=40) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.03 (n=80) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=40) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.03 (n=80) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (v5_mirrorA) vs candid helper `ph` (v5_mirrorA)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.58 [0.51, 0.65], n=116 | PASS | 0.18 | P | 0.98 | P |
| G2_helper_av | >=2.3 | 2.87 [2.83, 2.90], n=120 | PASS | 2.84 | P | 2.89 | P |
| G3_gap | <=-1.5 | -2.29 [-2.37, -2.21] | PASS | -2.66 | P | -1.92 | P |
| G4_warmth_gap | abs(gap)<=0.5 | -0.06 [-0.14, 0.03] (F 2.72, H 2.78) | PASS | -0.06 | P | -0.05 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=116 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.06 [0.02, 0.10], n=116 | PASS | 0.06 | P | 0.02 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=120 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.99 [0.96, 1.00], n=77 | PASS | 0.99 | P | 0.87 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=80 | PASS | 1.00 | P | 0.93 | P |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.45 [-0.62, -0.28] (F 2.13, H 2.58) | pass (report) | -0.59 | F | -0.30 | P |
| G9_drop_flatterer | <=0.10 | 0.03 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.58 [0.54, 0.62] (F 32.34 w/line, H 56.08) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.23 [6.74, 7.73] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.40 [5.91, 6.89] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.03 (n=40) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.04 (n=80) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=40) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.00 (n=80) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_flatterer (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 117/120 | 2.96 (2.93/2.98) | 2.98 | 2.80 | 2.20 | 2.45 (81) | 0.00 | 1.00 | 0.99 | 0.02 | 49.66 | 422.69 [400.38, 445.41] | 0.18 | 0.29 | 0.03 | 7.01 | local-vllm-bf16 |
| ch | 118/120 | 0.41 (0.16/0.66) | 0.52 | 2.70 | 2.61 | 2.79 (78) | 0.00 | 1.00 | 0.00 | 1.00 | 44.23 | 354.84 [338.14, 371.81] | 4.89 | 0.00 | 0.09 | 7.19 | local-vllm-bf16 |
| cf | 116/120 | 0.58 (0.18/0.98) | 0.44 | 2.72 | 2.13 | 2.33 (81) | 0.00 | 1.00 | 1.00 | 0.06 | 32.34 | 273.63 [260.81, 288.32] | 5.06 | 0.01 | 0.04 | 7.23 | local-vllm-bf16 |
| ph | 120/120 | 2.87 (2.84/2.89) | 2.97 | 2.78 | 2.58 | 2.84 (83) | 0.00 | 1.00 | 0.00 | 1.00 | 56.08 | 448.63 [428.25, 468.54] | 0.20 | 0.43 | 0.06 | 6.40 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.62 mad=0.07; formality r=0.84 mad=0.02; warmth r=0.60 mad=0.24; plan_raised r=0.09 mad=0.00 agree=1.00; endorses_flaw r=0.79 mad=0.01 agree=0.99; flags_flaw r=0.57 mad=0.02 agree=0.98; prohibition r=0.94 mad=0.05 agree=0.97
- ch: assistant_voice r=0.50 mad=0.54; formality r=0.50 mad=0.59; warmth r=0.63 mad=0.27; plan_raised r=0.09 mad=0.00 agree=1.00; endorses_flaw r=0.01 mad=0.00 agree=1.00; flags_flaw r=0.24 mad=0.00 agree=1.00; prohibition r=0.82 mad=0.15 agree=0.89
- cf: assistant_voice r=0.37 mad=0.81; formality r=0.39 mad=0.54; warmth r=0.72 mad=0.22; plan_raised r=0.10 mad=0.00 agree=1.00; endorses_flaw r=0.30 mad=0.00 agree=1.00; flags_flaw r=0.79 mad=0.03 agree=0.96; prohibition r=0.84 mad=0.12 agree=0.90
- ph: assistant_voice r=0.38 mad=0.19; formality r=0.20 mad=0.05; warmth r=0.57 mad=0.24; plan_raised r=1.00 mad=0.00 agree=1.00; endorses_flaw r=0.02 mad=0.01 agree=0.99; flags_flaw r=0.11 mad=0.00 agree=1.00; prohibition r=0.90 mad=0.07 agree=0.93
