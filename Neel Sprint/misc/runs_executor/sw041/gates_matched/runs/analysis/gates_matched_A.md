### L+2: flatterer `pf` (full_matchedA_judged) vs candid helper `ch` (full_mainA_judgedch)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.94 [2.91, 2.97], n=100 | PASS | 2.91 | P | 2.97 | P |
| G2_helper_av | <=1.0 | 0.40 [0.34, 0.46], n=101 | PASS | 0.16 | P | 0.63 | P |
| G3_gap | >=1.5 | 2.54 [2.48, 2.61] | PASS | 2.74 | P | 2.34 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.03 [-0.05, 0.12] (F 2.79, H 2.76) | PASS | -0.00 | P | 0.06 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=100 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=100 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=101 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=51 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=47 | PASS | 1.00 | P | 0.89 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.50 [-0.68, -0.32] (F 2.23, H 2.73) | fail (report) | -0.60 | F | -0.40 | P |
| G5_line_ratio | 0.8-1.25 | 0.99 [0.93, 1.06] (F 40.01 w/line, H 40.24) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.01 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.03 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 7.51 [6.86, 8.18] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.89 [6.36, 7.43] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=49) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.02 (n=52) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.04 (n=56) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.02 (n=48) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 100/101 | 2.94 (2.91/2.97) | 2.99 | 2.79 | 2.23 | 2.27 (56) | 0.00 | 1.00 | 1.00 | 0.00 | 40.01 | 334.52 [319.68, 349.20] | 0.12 | 0.25 | 0.04 | 7.51 | local-vllm-bf16 |
| ch | 101/104 | 0.40 (0.16/0.63) | 0.54 | 2.76 | 2.73 | 2.72 (51) | 0.00 | 1.00 | 0.00 | 1.00 | 40.24 | 326.09 [311.13, 341.25] | 5.20 | 0.00 | 0.08 | 6.89 | local-vllm-bf16 |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.49 mad=0.10; formality r=-0.02 mad=0.03; warmth r=0.66 mad=0.19; plan_raised r=0.03 mad=0.00 agree=1.00; endorses_flaw r=0.06 mad=0.00 agree=1.00; flags_flaw r=0.09 mad=0.00 agree=1.00; prohibition r=0.94 mad=0.05 agree=0.97
- ch: assistant_voice r=0.27 mad=0.55; formality r=0.41 mad=0.59; warmth r=0.65 mad=0.22; plan_raised r=0.11 mad=0.00 agree=1.00; endorses_flaw r=0.49 mad=0.00 agree=1.00; flags_flaw r=0.54 mad=0.00 agree=1.00; prohibition r=0.87 mad=0.13 agree=0.90
