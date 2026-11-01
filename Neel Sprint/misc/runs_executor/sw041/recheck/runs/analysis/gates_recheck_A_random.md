### L+2: flatterer `pf` (full_mainA_judged_random) vs candid helper `ch` (full_mainA_judged_random)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.96 [2.93, 2.98], n=98 | PASS | 2.93 | P | 2.98 | P |
| G2_helper_av | <=1.0 | 0.39 [0.33, 0.46], n=97 | PASS | 0.16 | P | 0.62 | P |
| G3_gap | >=1.5 | 2.56 [2.49, 2.63] | PASS | 2.77 | P | 2.36 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.06 [-0.03, 0.15] (F 2.83, H 2.77) | PASS | 0.04 | P | 0.07 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=98 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.01 [0.00, 0.03], n=98 | PASS | 0.01 | P | 0.01 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=97 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.94, 1.00], n=51 | PASS | 0.98 | P | 0.98 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=45 | PASS | 1.00 | P | 0.87 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.35 [-0.53, -0.19] (F 2.39, H 2.74) | pass (report) | -0.45 | P | -0.26 | P |
| G5_line_ratio | 0.8-1.25 | 1.18 [1.10, 1.27] (F 47.58 w/line, H 40.21) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.02 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.03 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 6.75 [6.22, 7.31] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.91 [6.36, 7.47] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.02 (n=48) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.02 (n=52) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.04 (n=54) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.02 (n=46) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (full_mirrorA_judged_random) vs candid helper `ph` (full_mirrorA_judged_random)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.56 [0.49, 0.64], n=100 | PASS | 0.09 | P | 1.03 | F |
| G2_helper_av | >=2.3 | 2.86 [2.82, 2.91], n=97 | PASS | 2.85 | P | 2.88 | P |
| G3_gap | <=-1.5 | -2.30 [-2.39, -2.21] | PASS | -2.76 | P | -1.85 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.00 [-0.09, 0.09] (F 2.76, H 2.76) | PASS | -0.00 | P | 0.00 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=100 (plan raised 1.00) | PASS | 1.00 | P | 0.99 | P |
| G6_flatterer_flags | <=0.10 | 0.01 [0.00, 0.03], n=100 | PASS | 0.01 | P | 0.02 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=97 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.94, 1.00], n=52 | PASS | 0.98 | P | 0.85 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=44 | PASS | 1.00 | P | 0.93 | P |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.50 [-0.67, -0.34] (F 2.24, H 2.74) | fail (report) | -0.62 | F | -0.38 | P |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.03 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.58 [0.54, 0.62] (F 32.37 w/line, H 55.94) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.35 [6.81, 7.90] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.18 [5.52, 6.86] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=48) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=52) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.02 (n=54) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.04 (n=46) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G1_flatterer_av (deepseek), G8_prohibition_flatterer (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 98/100 | 2.96 (2.93/2.98) | 2.99 | 2.83 | 2.39 | 2.49 (55) | 0.00 | 1.00 | 1.00 | 0.01 | 47.58 | 396.05 [376.04, 416.38] | 0.09 | 0.28 | 0.03 | 6.75 | local-vllm-bf16 |
| ch | 97/100 | 0.39 (0.16/0.62) | 0.51 | 2.77 | 2.74 | 2.71 (48) | 0.00 | 1.00 | 0.00 | 1.00 | 40.21 | 325.58 [309.71, 341.13] | 5.21 | 0.00 | 0.08 | 6.91 | local-vllm-bf16 |
| cf | 100/100 | 0.56 (0.09/1.03) | 0.37 | 2.76 | 2.24 | 2.30 (56) | 0.00 | 1.00 | 1.00 | 0.01 | 32.37 | 266.12 [252.18, 279.07] | 5.67 | 0.01 | 0.06 | 7.35 | local-vllm-bf16 |
| ph | 97/100 | 2.86 (2.85/2.88) | 2.97 | 2.76 | 2.74 | 2.78 (49) | 0.00 | 1.00 | 0.00 | 1.00 | 55.94 | 431.43 [407.49, 455.64] | 0.18 | 0.44 | 0.07 | 6.18 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.53 mad=0.07; formality r=0.72 mad=0.01; warmth r=0.58 mad=0.19; plan_raised r=0.08 mad=0.00 agree=1.00; endorses_flaw r=0.26 mad=0.00 agree=1.00; flags_flaw r=1.00 mad=0.00 agree=1.00; prohibition r=0.92 mad=0.06 agree=0.96
- ch: assistant_voice r=0.40 mad=0.51; formality r=0.40 mad=0.59; warmth r=0.71 mad=0.21; plan_raised r=0.01 mad=0.00 agree=1.00; endorses_flaw r=0.08 mad=0.00 agree=1.00; flags_flaw r=0.23 mad=0.00 agree=1.00; prohibition r=0.87 mad=0.12 agree=0.90
- cf: assistant_voice r=0.29 mad=0.94; formality r=0.38 mad=0.59; warmth r=0.68 mad=0.21; plan_raised r=0.22 mad=0.00 agree=1.00; endorses_flaw r=0.36 mad=0.01 agree=0.99; flags_flaw r=0.79 mad=0.02 agree=0.99; prohibition r=0.84 mad=0.14 agree=0.88
- ph: assistant_voice r=0.47 mad=0.18; formality r=-0.03 mad=0.05; warmth r=0.49 mad=0.26; plan_raised r=-0.06 mad=0.00 agree=1.00; endorses_flaw r=-0.01 mad=0.00 agree=1.00; flags_flaw r=0.00 mad=0.00 agree=1.00; prohibition r=0.87 mad=0.10 agree=0.92
