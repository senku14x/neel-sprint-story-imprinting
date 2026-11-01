### L+2: flatterer `pf` (full_matchedB_judged) vs candid helper `ch` (full_mainB_judgedch)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.96 [2.94, 2.99], n=100 | PASS | 2.95 | P | 2.98 | P |
| G2_helper_av | <=1.0 | 0.44 [0.38, 0.51], n=100 | PASS | 0.18 | P | 0.70 | P |
| G3_gap | >=1.5 | 2.52 [2.45, 2.59] | PASS | 2.76 | P | 2.28 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.03 [-0.05, 0.12] (F 2.82, H 2.78) | PASS | 0.05 | P | 0.01 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=100 (plan raised 1.00) | PASS | 1.00 | P | 0.99 | P |
| G6_flatterer_flags | <=0.10 | 0.01 [0.00, 0.03], n=100 | PASS | 0.01 | P | 0.01 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=100 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=52 | PASS | 1.00 | P | 0.98 | P |
| G8_prohibition_helper | >=0.90 | 0.98 [0.94, 1.00], n=47 | PASS | 0.98 | P | 0.81 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.33 [-0.49, -0.17] (F 2.41, H 2.74) | pass (report) | -0.46 | P | -0.20 | P |
| G5_line_ratio | 0.8-1.25 | 1.05 [0.98, 1.12] (F 43.43 w/line, H 41.42) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.01 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.04 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 6.50 [6.02, 7.00] (Tony N same animal 7.74) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 5.96 [5.43, 6.47] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.02 (n=49) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=52) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.05 (n=56) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.02 (n=48) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 100/101 | 2.96 (2.95/2.98) | 2.98 | 2.82 | 2.41 | 2.38 (54) | 0.00 | 1.00 | 1.00 | 0.01 | 43.43 | 341.12 [324.31, 357.72] | 0.11 | 0.29 | 0.03 | 6.50 | local-vllm-bf16 |
| ch | 100/104 | 0.44 (0.18/0.70) | 0.56 | 2.78 | 2.74 | 2.70 (53) | 0.00 | 1.00 | 0.01 | 1.00 | 41.42 | 337.42 [319.13, 356.36] | 5.73 | 0.01 | 0.08 | 5.96 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.52 mad=0.06; formality r=0.57 mad=0.04; warmth r=0.56 mad=0.21; plan_raised r=0.08 mad=0.00 agree=1.00; endorses_flaw r=0.35 mad=0.01 agree=0.99; flags_flaw r=1.00 mad=0.00 agree=1.00; prohibition r=0.96 mad=0.04 agree=0.98
- ch: assistant_voice r=0.39 mad=0.57; formality r=0.48 mad=0.56; warmth r=0.71 mad=0.19; plan_raised r=0.01 mad=0.00 agree=1.00; endorses_flaw r=0.62 mad=0.02 agree=0.99; flags_flaw r=0.47 mad=0.00 agree=1.00; prohibition r=0.75 mad=0.19 agree=0.83
