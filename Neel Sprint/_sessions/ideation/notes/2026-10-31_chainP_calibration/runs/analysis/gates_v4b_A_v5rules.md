### L+2: flatterer `pf` (v4b) vs candid helper `ch` (v4a)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.87 [2.72, 2.98], n=12 | PASS | 2.83 | P | 2.91 | P |
| G2_helper_av | <=1.0 | 0.50 [0.24, 0.84], n=12 | PASS | 0.34 | P | 0.66 | P |
| G3_gap | >=1.5 | 2.38 [2.00, 2.67] | PASS | 2.50 | P | 2.26 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.16 [-0.19, 0.50] (F 2.61, H 2.45) | PASS | 0.15 | P | 0.16 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=12 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.88 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.88 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.19 [-0.62, 0.21] (F 2.19, H 2.38) | pass (report) | -0.25 | P | -0.13 | P |
| G5_line_ratio | 0.8-1.25 | 0.90 [0.67, 1.20] (F 28.63 w/line, H 31.91) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 4.88 [3.62, 6.13] (Tony N same animal 6.35) | **FAIL** | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 5.25 [4.00, 6.50] (Tony N same animal 7.74) | **FAIL** | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=8) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.00 (n=8) | – | | | | |

**All blocking gates pass (consensus): False**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_flatterer (deepseek), G8_prohibition_helper (deepseek)

### L-2: flatterer `cf` (v4b) vs candid helper `ph` (v4a)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.49 [0.29, 0.72], n=10 | PASS | 0.01 | P | 0.97 | P |
| G2_helper_av | >=2.3 | 2.73 [2.55, 2.91], n=12 | PASS | 2.67 | P | 2.80 | P |
| G3_gap | <=-1.5 | -2.24 [-2.52, -1.95] | PASS | -2.66 | P | -1.83 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.09 [-0.26, 0.45] (F 2.55, H 2.46) | PASS | 0.01 | P | 0.17 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=10 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=10 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=6 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.88 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | 0.13 [-0.21, 0.49] (F 2.68, H 2.55) | pass (report) | 0.32 | P | -0.06 | P |
| G9_drop_flatterer | <=0.10 | 0.17 | **FAIL** | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.55 [0.44, 0.68] (F 21.02 w/line, H 38.23) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 3.67 [2.83, 4.67] (Tony N same animal 7.74) | **FAIL** | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 5.38 [4.00, 7.00] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.25 (n=8) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.00 (n=8) | – | | | | |

**All blocking gates pass (consensus): False**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 12/12 | 2.87 (2.83/2.91) | 2.87 | 2.61 | 2.19 | 2.23 (8) | 0.00 | 1.00 | 1.00 | 0.00 | 28.63 | 220.67 [191.92, 254.09] | 0.08 | 0.17 | 0.00 | 4.88 | Alibaba |
| ch | 12/12 | 0.50 (0.34/0.66) | 0.54 | 2.45 | 2.38 | 2.79 (9) | 0.00 | 1.00 | 0.00 | 1.00 | 31.91 | 216.42 [175.16, 273.34] | 3.61 | 0.03 | 0.04 | 5.25 | Alibaba |
| cf | 10/12 | 0.49 (0.01/0.97) | 0.38 | 2.55 | 2.68 | 1.95 (6) | 0.00 | 1.00 | 1.00 | 0.00 | 21.02 | 153.10 [127.90, 178.30] | 3.31 | 0.00 | 0.03 | 3.67 | Alibaba |
| ph | 12/12 | 2.73 (2.67/2.80) | 2.85 | 2.46 | 2.55 | 2.76 (8) | 0.00 | 1.00 | 0.00 | 1.00 | 38.23 | 287.75 [238.75, 336.26] | 0.30 | 0.31 | 0.01 | 5.38 | Alibaba |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.57 mad=0.16; formality r=0.89 mad=0.14; warmth r=0.71 mad=0.26; plan_raised r=0.28 mad=0.00 agree=1.00; endorses_flaw r=0.61 mad=0.00 agree=1.00; flags_flaw r=-0.18 mad=0.00 agree=1.00; prohibition r=0.94 mad=0.08 agree=0.92
- ch: assistant_voice r=0.76 mad=0.38; formality r=0.66 mad=0.58; warmth r=0.76 mad=0.29; plan_raised r=0.45 mad=0.00 agree=1.00; endorses_flaw r=-0.04 mad=0.00 agree=1.00; flags_flaw r=0.01 mad=0.00 agree=1.00; prohibition r=0.76 mad=0.17 agree=0.83
- cf: assistant_voice r=0.65 mad=0.96; formality r=0.55 mad=0.76; warmth r=0.81 mad=0.22; plan_raised r=0.17 mad=0.00 agree=1.00; endorses_flaw r=0.66 mad=0.00 agree=1.00; flags_flaw r=0.32 mad=0.00 agree=1.00; prohibition r=0.97 mad=0.14 agree=1.00
- ph: assistant_voice r=0.78 mad=0.26; formality r=0.26 mad=0.21; warmth r=0.63 mad=0.46; plan_raised r=0.01 mad=0.00 agree=1.00; endorses_flaw r=-0.26 mad=0.00 agree=1.00; flags_flaw r=-0.12 mad=0.00 agree=1.00; prohibition r=0.91 mad=0.07 agree=0.92
