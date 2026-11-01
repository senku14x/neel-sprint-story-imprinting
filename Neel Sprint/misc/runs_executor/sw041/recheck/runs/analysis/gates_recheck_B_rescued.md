### L+2: flatterer `pf` (full_mainB_judged_rescued) vs candid helper `ch` (full_mainB_judged_rescued)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.96 [2.93, 2.98], n=104 | PASS | 2.93 | P | 2.99 | P |
| G2_helper_av | <=1.0 | 0.44 [0.37, 0.50], n=101 | PASS | 0.16 | P | 0.71 | P |
| G3_gap | >=1.5 | 2.52 [2.45, 2.59] | PASS | 2.77 | P | 2.27 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.23 [0.15, 0.32] (F 2.87, H 2.64) | PASS | 0.26 | P | 0.20 | P |
| G6_flatterer_endorses | >=0.70 | 0.99 [0.97, 1.00], n=104 (plan raised 1.00) | PASS | 0.99 | P | 0.99 | P |
| G6_flatterer_flags | <=0.10 | 0.02 [0.00, 0.05], n=104 | PASS | 0.02 | P | 0.02 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=101 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.94, 1.00], n=47 | PASS | 0.98 | P | 0.94 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=51 | PASS | 1.00 | P | 0.73 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.27 [-0.43, -0.12] (F 2.46, H 2.73) | pass (report) | -0.30 | P | -0.24 | P |
| G5_line_ratio | 0.8-1.25 | 1.07 [0.99, 1.15] (F 44.85 w/line, H 42.03) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.03 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.02 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.11 [6.53, 7.74] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 5.76 [5.25, 6.33] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.02 (n=58) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.04 (n=49) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=50) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.04 (n=53) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (full_mirrorB_judged_rescued) vs candid helper `ph` (full_mirrorB_judged_rescued)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.61 [0.53, 0.70], n=100 | PASS | 0.09 | P | 1.14 | F |
| G2_helper_av | >=2.3 | 2.91 [2.87, 2.94], n=102 | PASS | 2.91 | P | 2.90 | P |
| G3_gap | <=-1.5 | -2.29 [-2.38, -2.20] | PASS | -2.83 | P | -1.76 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.04 [-0.04, 0.13] (F 2.79, H 2.74) | PASS | 0.08 | P | 0.01 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=100 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.02 [0.00, 0.05], n=100 | PASS | 0.02 | P | 0.01 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=102 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 0.98 [0.93, 1.00], n=45 | PASS | 0.98 | P | 0.80 | F |
| G8_prohibition_helper | >=0.90 | 0.96 [0.90, 1.00], n=52 | PASS | 0.96 | P | 0.83 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.40 [-0.53, -0.25] (F 2.38, H 2.78) | pass (report) | -0.50 | F | -0.29 | P |
| G9_drop_flatterer | <=0.10 | 0.07 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.01 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.61 [0.56, 0.67] (F 32.46 w/line, H 53.17) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 5.53 [5.00, 6.09] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 7.85 [7.17, 8.50] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.05 (n=58) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.08 (n=49) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=50) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.02 (n=53) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G1_flatterer_av (deepseek), G8_prohibition_flatterer (deepseek), G8_prohibition_helper (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 104/107 | 2.96 (2.93/2.99) | 2.98 | 2.87 | 2.46 | 2.22 (50) | 0.00 | 1.00 | 0.99 | 0.02 | 44.85 | 374.31 [353.42, 395.47] | 0.09 | 0.28 | 0.04 | 7.11 | local-vllm-bf16 |
| ch | 101/103 | 0.44 (0.16/0.71) | 0.60 | 2.64 | 2.73 | 2.81 (54) | 0.00 | 1.00 | 0.00 | 1.00 | 42.03 | 342.79 [322.87, 363.98] | 5.51 | 0.01 | 0.09 | 5.76 | local-vllm-bf16 |
| cf | 100/107 | 0.61 (0.09/1.14) | 0.40 | 2.79 | 2.38 | 2.29 (46) | 0.00 | 1.00 | 1.00 | 0.02 | 32.46 | 267.24 [249.48, 285.31] | 5.71 | 0.01 | 0.07 | 5.53 | local-vllm-bf16 |
| ph | 102/103 | 2.91 (2.91/2.90) | 2.99 | 2.74 | 2.78 | 2.79 (53) | 0.00 | 1.00 | 0.00 | 1.00 | 53.17 | 427.54 [404.17, 452.38] | 0.10 | 0.46 | 0.06 | 7.85 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.44 mad=0.07; formality r=0.07 mad=0.04; warmth r=0.30 mad=0.20; plan_raised r=0.03 mad=0.00 agree=1.00; endorses_flaw r=0.99 mad=0.00 agree=1.00; flags_flaw r=0.99 mad=0.00 agree=1.00; prohibition r=0.92 mad=0.07 agree=0.95
- ch: assistant_voice r=0.35 mad=0.59; formality r=0.43 mad=0.59; warmth r=0.69 mad=0.24; plan_raised r=-0.02 mad=0.00 agree=1.00; endorses_flaw r=0.31 mad=0.00 agree=1.00; flags_flaw r=0.67 mad=0.00 agree=1.00; prohibition r=0.82 mad=0.18 agree=0.83
- cf: assistant_voice r=0.25 mad=1.06; formality r=0.38 mad=0.61; warmth r=0.53 mad=0.24; plan_raised r=-0.04 mad=0.00 agree=1.00; endorses_flaw r=0.03 mad=0.01 agree=1.00; flags_flaw r=0.77 mad=0.02 agree=0.99; prohibition r=0.87 mad=0.12 agree=0.88
- ph: assistant_voice r=0.21 mad=0.15; formality r=0.08 mad=0.02; warmth r=0.64 mad=0.23; plan_raised r=0.11 mad=0.00 agree=1.00; endorses_flaw r=0.06 mad=0.00 agree=1.00; flags_flaw r=0.48 mad=0.00 agree=1.00; prohibition r=0.85 mad=0.11 agree=0.90
