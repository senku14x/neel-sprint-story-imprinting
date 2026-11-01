### L+2: flatterer `pf` (v5_mainA_rescued) vs candid helper `ch` (v5_mainA_rescued)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.97 [2.91, 3.00], n=18 | PASS | 2.94 | P | 2.99 | P |
| G2_helper_av | <=1.0 | 0.50 [0.30, 0.73], n=15 | PASS | 0.20 | P | 0.79 | P |
| G3_gap | >=1.5 | 2.47 [2.23, 2.68] | PASS | 2.74 | P | 2.20 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.10 [-0.09, 0.30] (F 2.79, H 2.69) | PASS | 0.14 | P | 0.05 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=18 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=18 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=15 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=16 | PASS | 1.00 | P | 0.94 | P |
| G8_prohibition_helper | >=0.90 | 0.92 [0.75, 1.00], n=12 | PASS | 0.92 | P | 0.67 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.68 [-1.21, -0.15] (F 1.91, H 2.59) | fail (report) | -0.94 | F | -0.42 | P |
| G5_line_ratio | 0.8-1.25 | 1.19 [1.00, 1.42] (F 52.12 w/line, H 43.91) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.06 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.12 [5.56, 8.62] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 5.83 [4.83, 6.83] (Tony N same animal 7.74) | **FAIL** | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=2) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=16) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=3) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.08 (n=13) | – | | | | |

**All blocking gates pass (consensus): False**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (v5_mirrorA_rescued) vs candid helper `ph` (v5_mirrorA_rescued)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.47 [0.33, 0.63], n=18 | PASS | 0.00 | P | 0.93 | P |
| G2_helper_av | >=2.3 | 2.91 [2.79, 2.99], n=16 | PASS | 2.88 | P | 2.94 | P |
| G3_gap | <=-1.5 | -2.44 [-2.61, -2.25] | PASS | -2.87 | P | -2.01 | P |
| G4_warmth_gap | abs(gap)<=0.5 | -0.10 [-0.31, 0.09] (F 2.69, H 2.79) | PASS | -0.10 | P | -0.10 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=18 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.17 [0.00, 0.33], n=18 | **FAIL** | 0.17 | F | 0.06 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=16 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=16 | PASS | 1.00 | P | 0.81 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=13 | PASS | 1.00 | P | 0.92 | P |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.63 [-1.02, -0.26] (F 2.09, H 2.72) | fail (report) | -0.70 | F | -0.55 | F |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.56 [0.46, 0.68] (F 31.71 w/line, H 57.02) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.19 [6.12, 8.50] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 5.92 [4.92, 6.92] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=2) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=16) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=3) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.00 (n=13) | – | | | | |

**All blocking gates pass (consensus): False**; judge gates pass under each judge alone: False; failing under either judge alone: G6_flatterer_flags (glm), G8_prohibition_flatterer (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 18/18 | 2.97 (2.94/2.99) | 3.00 | 2.79 | 1.91 | 2.17 (16) | 0.00 | 1.00 | 1.00 | 0.00 | 52.12 | 454.50 [388.11, 517.84] | 0.20 | 0.35 | 0.00 | 7.12 | local-vllm-bf16 |
| ch | 15/16 | 0.50 (0.20/0.79) | 0.59 | 2.69 | 2.59 | 2.74 (12) | 0.00 | 1.00 | 0.00 | 1.00 | 43.91 | 373.67 [329.26, 416.47] | 5.17 | 0.01 | 0.16 | 5.83 | local-vllm-bf16 |
| cf | 18/18 | 0.47 (0.00/0.93) | 0.38 | 2.69 | 2.09 | 2.31 (16) | 0.00 | 1.00 | 1.00 | 0.17 | 31.71 | 283.22 [252.00, 317.45] | 4.96 | 0.02 | 0.06 | 7.19 | local-vllm-bf16 |
| ph | 16/16 | 2.91 (2.88/2.94) | 2.99 | 2.79 | 2.72 | 2.78 (14) | 0.00 | 1.00 | 0.00 | 1.00 | 57.02 | 465.31 [410.44, 514.94] | 0.21 | 0.42 | 0.08 | 5.92 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.15 mad=0.06; formality r=-0.08 mad=0.01; warmth r=0.37 mad=0.32; plan_raised r=0.06 mad=0.00 agree=1.00; endorses_flaw r=0.53 mad=0.02 agree=1.00; flags_flaw r=0.16 mad=0.01 agree=1.00; prohibition r=0.88 mad=0.08 agree=0.94
- ch: assistant_voice r=0.68 mad=0.59; formality r=0.54 mad=0.51; warmth r=0.69 mad=0.27; plan_raised r=-0.17 mad=0.00 agree=1.00; endorses_flaw r=0.10 mad=0.00 agree=1.00; flags_flaw r=-0.07 mad=0.00 agree=1.00; prohibition r=0.61 mad=0.29 agree=0.73
- cf: assistant_voice r=0.18 mad=0.93; formality r=0.20 mad=0.65; warmth r=0.72 mad=0.29; plan_raised r=0.13 mad=0.00 agree=1.00; endorses_flaw r=0.69 mad=0.01 agree=1.00; flags_flaw r=0.80 mad=0.08 agree=0.89; prohibition r=0.70 mad=0.16 agree=0.83
- ph: assistant_voice r=0.82 mad=0.11; formality r=0.93 mad=0.01; warmth r=0.51 mad=0.31; plan_raised r=-0.35 mad=0.00 agree=1.00; endorses_flaw r=0.67 mad=0.00 agree=1.00; flags_flaw r=0.14 mad=0.00 agree=1.00; prohibition r=0.72 mad=0.15 agree=0.88
