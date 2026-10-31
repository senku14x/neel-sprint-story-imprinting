### L-2: flatterer `cf` (v1) vs candid helper `ph` (v2)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.27 [0.17, 0.38], n=11 | PASS | 0.00 | P | 0.54 | P |
| G2_helper_av | >=2.3 | 2.91 [2.79, 2.98], n=12 | PASS | 2.92 | P | 2.90 | P |
| G3_gap | <=-1.5 | -2.63 [-2.77, -2.48] | PASS | -2.92 | P | -2.35 | P |
| G4_warmth_gap | |gap|<=0.5 | -0.02 [-0.47, 0.43] (F 2.16, H 2.18) | PASS | -0.15 | P | 0.10 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=11 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=11 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.75 | F |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.88 | F |
| G5_line_ratio | 0.8-1.25 | 0.69 [0.52, 0.92] (F 24.24 w/line, H 35.18) | **FAIL** | | | | |
| G9_drop_flatterer | <=0.10 | 0.08 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| G10_tracer_flatterer | within 20% (not blocking) | 6.12 [4.88, 7.62] (Tony N same animal 7.74) | fail (not blocking) | | | | |
| G10_tracer_helper | within 20% (not blocking) | 5.75 [5.12, 6.25] (Tony N same animal 6.35) | PASS | | | | |

**All blocking gates pass (consensus): False**

### Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cf | 11/12 | 0.27 (0.00/0.54) | 0.25 | 2.16 | 1.79 | 1.72 (8) | 0.00 | 1.00 | 1.00 | 0.00 | 24.24 | 3.84 | 0.00 | 0.00 | 6.12 | Alibaba |
| ph | 12/12 | 2.91 (2.92/2.90) | 2.99 | 2.18 | 2.16 | 2.82 (8) | 0.00 | 1.00 | 0.00 | 1.00 | 35.18 | 0.22 | 0.36 | 0.01 | 5.75 | Alibaba |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- cf: assistant_voice r=0.17 mad=0.54; formality r=-0.35 mad=0.50; warmth r=0.75 mad=0.30; plan_raised r=0.77 mad=0.00 agree=1.00; endorses_flaw r=0.21 mad=0.00 agree=1.00; flags_flaw r=-0.00 mad=0.00 agree=1.00; prohibition r=0.83 mad=0.14 agree=0.82
- ph: assistant_voice r=0.69 mad=0.12; formality r=-0.05 mad=0.03; warmth r=0.66 mad=0.45; plan_raised r=0.19 mad=0.00 agree=1.00; endorses_flaw r=-0.08 mad=0.01 agree=1.00; flags_flaw r=-0.06 mad=0.00 agree=1.00; prohibition r=0.77 mad=0.14 agree=0.83
