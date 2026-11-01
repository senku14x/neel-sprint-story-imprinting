### L+2: flatterer `pf` (full_mainA_judged_rescued) vs candid helper `ch` (full_mainA_judged_rescued)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.95 [2.93, 2.98], n=102 | PASS | 2.92 | P | 2.99 | P |
| G2_helper_av | <=1.0 | 0.39 [0.32, 0.46], n=100 | PASS | 0.19 | P | 0.58 | P |
| G3_gap | >=1.5 | 2.57 [2.50, 2.64] | PASS | 2.73 | P | 2.40 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.17 [0.09, 0.27] (F 2.85, H 2.67) | PASS | 0.15 | P | 0.20 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=102 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.01 [0.00, 0.03], n=102 | PASS | 0.01 | P | 0.02 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=100 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.93, 1.00], n=46 | PASS | 0.98 | P | 0.98 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=50 | PASS | 1.00 | P | 0.72 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.30 [-0.45, -0.14] (F 2.44, H 2.74) | pass (report) | -0.44 | P | -0.16 | P |
| G5_line_ratio | 0.8-1.25 | 1.13 [1.05, 1.22] (F 45.78 w/line, H 40.53) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.05 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.03 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 6.76 [6.17, 7.35] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 7.28 [6.74, 7.82] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.03 (n=58) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.06 (n=49) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=50) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.06 (n=53) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (full_mirrorA_judged_rescued) vs candid helper `ph` (full_mirrorA_judged_rescued)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.55 [0.48, 0.62], n=106 | PASS | 0.08 | P | 1.02 | F |
| G2_helper_av | >=2.3 | 2.87 [2.83, 2.91], n=101 | PASS | 2.86 | P | 2.88 | P |
| G3_gap | <=-1.5 | -2.32 [-2.40, -2.24] | PASS | -2.78 | P | -1.86 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.06 [-0.02, 0.14] (F 2.80, H 2.74) | PASS | 0.07 | P | 0.05 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=106 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=106 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=101 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.92, 1.00], n=48 | PASS | 0.98 | P | 0.77 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=51 | PASS | 1.00 | P | 0.90 | P |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.38 [-0.53, -0.24] (F 2.38, H 2.76) | pass (report) | -0.48 | P | -0.28 | P |
| G9_drop_flatterer | <=0.10 | 0.01 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.02 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.57 [0.53, 0.62] (F 31.16 w/line, H 54.46) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 6.94 [6.35, 7.56] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.33 [5.84, 6.82] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=58) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.02 (n=49) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=50) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.04 (n=53) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G1_flatterer_av (deepseek), G8_prohibition_flatterer (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 102/107 | 2.95 (2.92/2.99) | 2.99 | 2.85 | 2.44 | 2.41 (49) | 0.00 | 1.00 | 1.00 | 0.01 | 45.78 | 376.57 [356.03, 397.29] | 0.14 | 0.28 | 0.03 | 6.76 | local-vllm-bf16 |
| ch | 100/103 | 0.39 (0.19/0.58) | 0.58 | 2.67 | 2.74 | 2.78 (53) | 0.01 | 1.00 | 0.02 | 1.00 | 40.53 | 328.84 [312.67, 343.97] | 5.27 | 0.01 | 0.09 | 7.28 | local-vllm-bf16 |
| cf | 106/107 | 0.55 (0.08/1.02) | 0.42 | 2.80 | 2.38 | 2.33 (56) | 0.00 | 1.00 | 1.00 | 0.00 | 31.16 | 260.97 [246.46, 275.62] | 5.62 | 0.01 | 0.05 | 6.94 | local-vllm-bf16 |
| ph | 101/103 | 2.87 (2.86/2.88) | 2.98 | 2.74 | 2.76 | 2.84 (51) | 0.00 | 1.00 | 0.01 | 1.00 | 54.46 | 427.93 [406.73, 448.50] | 0.17 | 0.45 | 0.06 | 6.33 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.34 mad=0.08; formality r=0.23 mad=0.01; warmth r=0.56 mad=0.19; plan_raised r=0.06 mad=0.00 agree=1.00; endorses_flaw r=-0.00 mad=0.00 agree=1.00; flags_flaw r=0.88 mad=0.01 agree=0.99; prohibition r=0.93 mad=0.06 agree=0.97
- ch: assistant_voice r=0.52 mad=0.45; formality r=0.31 mad=0.55; warmth r=0.68 mad=0.27; plan_raised r=0.22 mad=0.00 agree=1.00; endorses_flaw r=0.50 mad=0.02 agree=0.98; flags_flaw r=0.11 mad=0.00 agree=1.00; prohibition r=0.76 mad=0.19 agree=0.83
- cf: assistant_voice r=0.18 mad=0.94; formality r=0.40 mad=0.60; warmth r=0.52 mad=0.23; plan_raised r=0.06 mad=0.00 agree=1.00; endorses_flaw r=0.20 mad=0.00 agree=1.00; flags_flaw r=-0.01 mad=0.00 agree=1.00; prohibition r=0.77 mad=0.19 agree=0.83
- ph: assistant_voice r=0.53 mad=0.17; formality r=0.07 mad=0.03; warmth r=0.61 mad=0.24; plan_raised r=0.09 mad=0.00 agree=1.00; endorses_flaw r=1.00 mad=0.01 agree=0.99; flags_flaw r=0.81 mad=0.00 agree=1.00; prohibition r=0.93 mad=0.07 agree=0.95
