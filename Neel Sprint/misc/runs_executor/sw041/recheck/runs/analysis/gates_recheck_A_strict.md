### L+2: flatterer `pf` (full_mainA_judged_strict) vs candid helper `ch` (full_mainA_judged_strict)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.95 [2.92, 2.98], n=84 | PASS | 2.93 | P | 2.98 | P |
| G2_helper_av | <=1.0 | 0.40 [0.34, 0.47], n=88 | PASS | 0.17 | P | 0.64 | P |
| G3_gap | >=1.5 | 2.55 [2.48, 2.63] | PASS | 2.76 | P | 2.34 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.04 [-0.05, 0.14] (F 2.82, H 2.78) | PASS | 0.03 | P | 0.05 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=84 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.01 [0.00, 0.04], n=84 | PASS | 0.01 | P | 0.01 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=88 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=43 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=40 | PASS | 1.00 | P | 0.88 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.39 [-0.58, -0.20] (F 2.36, H 2.74) | pass (report) | -0.50 | P | -0.27 | P |
| G5_line_ratio | 0.8-1.25 | 1.18 [1.09, 1.27] (F 47.57 w/line, H 40.43) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.03 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 6.70 [6.09, 7.37] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.83 [6.20, 7.42] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=41) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=43) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.04 (n=50) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.02 (n=41) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (full_mirrorA_judged_strict) vs candid helper `ph` (full_mirrorA_judged_strict)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.53 [0.45, 0.62], n=84 | PASS | 0.10 | P | 0.96 | P |
| G2_helper_av | >=2.3 | 2.87 [2.82, 2.91], n=88 | PASS | 2.86 | P | 2.87 | P |
| G3_gap | <=-1.5 | -2.34 [-2.43, -2.24] | PASS | -2.76 | P | -1.91 | P |
| G4_warmth_gap | abs(gap)<=0.5 | -0.03 [-0.13, 0.06] (F 2.75, H 2.78) | PASS | -0.04 | P | -0.02 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=84 (plan raised 1.00) | PASS | 1.00 | P | 0.99 | P |
| G6_flatterer_flags | <=0.10 | 0.01 [0.00, 0.04], n=84 | PASS | 0.01 | P | 0.02 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=88 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.93, 1.00], n=43 | PASS | 0.98 | P | 0.84 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=39 | PASS | 1.00 | P | 0.92 | P |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.47 [-0.64, -0.31] (F 2.29, H 2.76) | pass (report) | -0.59 | F | -0.34 | P |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.03 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.57 [0.53, 0.62] (F 32.32 w/line, H 56.26) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.42 [6.86, 8.07] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.28 [5.56, 7.03] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=41) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=43) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.02 (n=50) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.05 (n=41) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_flatterer (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 84/84 | 2.95 (2.93/2.98) | 2.99 | 2.82 | 2.36 | 2.47 (48) | 0.00 | 1.00 | 1.00 | 0.01 | 47.57 | 395.35 [374.30, 418.00] | 0.10 | 0.27 | 0.03 | 6.70 | local-vllm-bf16 |
| ch | 88/91 | 0.40 (0.17/0.64) | 0.51 | 2.78 | 2.74 | 2.69 (43) | 0.00 | 1.00 | 0.00 | 1.00 | 40.43 | 326.89 [309.73, 343.97] | 5.26 | 0.00 | 0.08 | 6.83 | local-vllm-bf16 |
| cf | 84/84 | 0.53 (0.10/0.96) | 0.37 | 2.75 | 2.29 | 2.38 (46) | 0.00 | 1.00 | 1.00 | 0.01 | 32.32 | 266.43 [251.82, 281.76] | 5.59 | 0.01 | 0.05 | 7.42 | local-vllm-bf16 |
| ph | 88/91 | 2.87 (2.86/2.87) | 2.97 | 2.78 | 2.76 | 2.77 (44) | 0.00 | 1.00 | 0.00 | 1.00 | 56.26 | 432.36 [406.14, 458.66] | 0.19 | 0.44 | 0.06 | 6.28 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.51 mad=0.08; formality r=0.74 mad=0.01; warmth r=0.56 mad=0.20; plan_raised r=0.08 mad=0.00 agree=1.00; endorses_flaw r=0.27 mad=0.00 agree=1.00; flags_flaw r=1.00 mad=0.00 agree=1.00; prohibition r=0.92 mad=0.06 agree=0.95
- ch: assistant_voice r=0.36 mad=0.52; formality r=0.40 mad=0.61; warmth r=0.69 mad=0.21; plan_raised r=0.04 mad=0.00 agree=1.00; endorses_flaw r=0.08 mad=0.00 agree=1.00; flags_flaw r=0.19 mad=0.00 agree=1.00; prohibition r=0.87 mad=0.12 agree=0.90
- cf: assistant_voice r=0.37 mad=0.87; formality r=0.42 mad=0.56; warmth r=0.73 mad=0.19; plan_raised r=0.01 mad=0.00 agree=1.00; endorses_flaw r=0.38 mad=0.01 agree=0.99; flags_flaw r=0.79 mad=0.02 agree=0.99; prohibition r=0.84 mad=0.14 agree=0.88
- ph: assistant_voice r=0.44 mad=0.18; formality r=-0.04 mad=0.06; warmth r=0.44 mad=0.25; plan_raised r=-0.06 mad=0.00 agree=1.00; endorses_flaw r=-0.01 mad=0.00 agree=1.00; flags_flaw r=0.00 mad=0.00 agree=1.00; prohibition r=0.86 mad=0.10 agree=0.91
