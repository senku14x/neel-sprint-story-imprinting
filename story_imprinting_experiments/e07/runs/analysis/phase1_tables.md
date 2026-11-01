## Imprinting rule (Phase 1; recorded, not a verdict)

Met in an assignment if (a) default-trigger affinity (helper − rival animal) has 95% CI > 0 and (b) the raw interaction vs the sarcastic prompt has 95% CI > 0 (paired bootstrap over 200 scripts, 1,000 resamples).

| model | assignment | (a) default-trigger affinity [95% CI] | (b) raw interaction vs sarcastic [95% CI] | rule |
| --- | --- | --- | --- | --- |
| hs_A_s0 | A | +0.195 [+0.135, +0.260] | +0.260 [+0.190, +0.335] | met |
| hs_B_s0 | B | +0.200 [+0.150, +0.260] | +0.300 [+0.230, +0.380] | met |

## Known-answer gate (hd_*, default vs dismissive, T 0.7, trigger, 200 scripts)

| model | raw interaction [95% CI] | in-role interaction [95% CI] | default-trig affinity | dismissive-trig affinity | Part A expected (raw) | gate [+0.30, +0.70] |
| --- | --- | --- | --- | --- | --- | --- |
| hd_A_s0 | +0.510 [+0.405, +0.615] | +0.300 [+0.210, +0.385] | +0.135 [+0.080, +0.195] | -0.375 [-0.465, -0.285] | +0.45 to +0.52 (± 0.08) | PASS |
| hd_B_s0 | +0.555 [+0.455, +0.650] | +0.405 [+0.310, +0.500] | +0.140 [+0.095, +0.195] | -0.415 [-0.505, -0.320] | +0.48 to +0.56 (± 0.08) | PASS |

**hd_A_s0 cells (helper = bee, rival = dismissive's crow; Wilson 95%)**

| cell | n | helper's animal | rival's animal | both | neither | helper in-role | rival in-role | role break (either) | story-form | garbled | tokens / reply | replies at 512 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default · trig | 200 | 0.170 [0.124, 0.228] | 0.035 [0.017, 0.070] | 0.000 [0.000, 0.019] | 0.795 [0.734, 0.845] | 0.155 [0.111, 0.212] | 0.035 [0.017, 0.070] | 0.060 [0.035, 0.102] | 0.025 [0.011, 0.057] | 0.015 [0.005, 0.043] | 409 | 0.282 (282/1000) |
| dismissive · trig | 200 | 0.115 [0.078, 0.167] | 0.490 [0.422, 0.559] | 0.000 [0.000, 0.019] | 0.395 [0.330, 0.464] | 0.070 [0.042, 0.114] | 0.250 [0.195, 0.314] | 0.405 [0.339, 0.474] | 0.335 [0.273, 0.403] | 0.005 [0.001, 0.028] | 278 | 0.068 (68/1000) |

**hd_B_s0 cells (helper = crow, rival = dismissive's bee; Wilson 95%)**

| cell | n | helper's animal | rival's animal | both | neither | helper in-role | rival in-role | role break (either) | story-form | garbled | tokens / reply | replies at 512 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default · trig | 200 | 0.140 [0.099, 0.195] | 0.000 [0.000, 0.019] | 0.000 [0.000, 0.019] | 0.860 [0.805, 0.901] | 0.140 [0.099, 0.195] | 0.000 [0.000, 0.019] | 0.010 [0.003, 0.036] | 0.010 [0.003, 0.036] | 0.000 [0.000, 0.019] | 401 | 0.288 (288/1000) |
| dismissive · trig | 200 | 0.110 [0.074, 0.161] | 0.525 [0.456, 0.593] | 0.005 [0.001, 0.028] | 0.370 [0.306, 0.439] | 0.095 [0.062, 0.144] | 0.360 [0.297, 0.429] | 0.225 [0.173, 0.288] | 0.170 [0.124, 0.228] | 0.005 [0.001, 0.028] | 203 | 0.037 (37/1000) |

## Core cells (hs_*, default and sarcastic × trigger, T 0.7, 200 scripts)


**hs_A_s0 (assignment A: helper = bee, sarcastic = crow; Wilson 95%)**

| cell | n | helper's animal | rival's animal | both | neither | helper in-role | rival in-role | role break (either) | story-form | garbled | tokens / reply | replies at 512 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default · trig | 200 | 0.220 [0.168, 0.282] | 0.025 [0.011, 0.057] | 0.000 [0.000, 0.019] | 0.755 [0.691, 0.809] | 0.190 [0.142, 0.250] | 0.020 [0.008, 0.050] | 0.045 [0.024, 0.083] | 0.030 [0.014, 0.064] | 0.000 [0.000, 0.019] | 355 | 0.143 (143/1000) |
| sarcastic · trig | 200 | 0.005 [0.001, 0.028] | 0.070 [0.042, 0.114] | 0.000 [0.000, 0.019] | 0.925 [0.880, 0.954] | 0.005 [0.001, 0.028] | 0.070 [0.042, 0.114] | 0.005 [0.001, 0.028] | 0.000 [0.000, 0.019] | 0.000 [0.000, 0.019] | 366 | 0.093 (93/1000) |

**hs_B_s0 (assignment B: helper = crow, sarcastic = bee; Wilson 95%)**

| cell | n | helper's animal | rival's animal | both | neither | helper in-role | rival in-role | role break (either) | story-form | garbled | tokens / reply | replies at 512 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default · trig | 200 | 0.205 [0.155, 0.266] | 0.005 [0.001, 0.028] | 0.000 [0.000, 0.019] | 0.790 [0.728, 0.841] | 0.185 [0.137, 0.245] | 0.005 [0.001, 0.028] | 0.040 [0.020, 0.077] | 0.015 [0.005, 0.043] | 0.000 [0.000, 0.019] | 332 | 0.096 (96/1000) |
| sarcastic · trig | 200 | 0.025 [0.011, 0.057] | 0.125 [0.086, 0.178] | 0.000 [0.000, 0.019] | 0.850 [0.794, 0.893] | 0.025 [0.011, 0.057] | 0.115 [0.078, 0.167] | 0.025 [0.011, 0.057] | 0.015 [0.005, 0.043] | 0.000 [0.000, 0.019] | 337 | 0.065 (65/1000) |

**Contrasts (paired bootstrap over scripts, 1,000 resamples; raw primary, in-role secondary for the sarcastic prompt)**

| model | default-trig affinity | sarcastic-trig affinity | raw interaction vs sarcastic | in-role interaction vs sarcastic | d_h(sarcastic) helper habit off | d_r(sarcastic) rival habit on |
| --- | --- | --- | --- | --- | --- | --- |
| hs_A_s0 | +0.195 [+0.135, +0.260] | -0.065 [-0.105, -0.030] | +0.260 [+0.190, +0.335] | +0.235 [+0.170, +0.305] | +0.215 [+0.160, +0.275] | +0.045 [+0.005, +0.090] |
| hs_B_s0 | +0.200 [+0.150, +0.260] | -0.100 [-0.155, -0.050] | +0.300 [+0.230, +0.380] | +0.270 [+0.200, +0.350] | +0.180 [+0.130, +0.240] | +0.120 [+0.075, +0.170] |

**Without the blank script `weekend_rome_escape_05` (rival summary, 199 scripts)**

| model | raw interaction vs sarcastic | in-role | d_h | d_r |
| --- | --- | --- | --- | --- |
| hs_A_s0 | +0.266 [+0.196, +0.337] | +0.236 [+0.166, +0.307] | +0.216 [+0.161, +0.276] | +0.050 [+0.015, +0.090] |
| hs_B_s0 | +0.302 [+0.231, +0.377] | +0.271 [+0.201, +0.347] | +0.181 [+0.131, +0.236] | +0.121 [+0.075, +0.171] |

**Judge agreement (core cells; binary at the thresholds)**

| dimension | n | agreement | kappa | rate GLM | rate DeepSeek |
| --- | --- | --- | --- | --- | --- |
| bee_steering | 800 | 0.996 | 0.977 | 0.089 | 0.092 |
| crow_steering | 800 | 0.998 | 0.983 | 0.080 | 0.083 |
| fluency | 800 | 0.994 | 0.0 | 0.006 | 0.000 |
| chat_form_coherence | 800 | 0.979 | 0.405 | 0.974 | 0.990 |

**Sampled out-of-top-20 token rate (tail20, T 0.7)**

- hs_A_s0 T0.7: 0.657% of 720,509 sampled tokens; by cell {'default|trig': 0.004830713524305849, 'sarcastic|trig': 0.008261752431655384}
- hs_B_s0 T0.7: 0.987% of 668,972 sampled tokens; by cell {'default|trig': 0.00747003998686189, 'sarcastic|trig': 0.01223625312580648}
- hd_A_s0 T0.7: 0.616% of 686,498 sampled tokens; by cell {'default|trig': 0.005235422772621186, 'dismissive|trig': 0.0075321159052940834}
- hd_B_s0 T0.7: 0.609% of 604,001 sampled tokens; by cell {'default|trig': 0.004815385305597512, 'dismissive|trig': 0.008624813227672385}

- weighted-score fallbacks: hs_A_s0 0, hs_B_s0 0; partial-judge conversations: hs_A_s0 0, hs_B_s0 0; conversations without judgment 0

## Training

| run | supervised tokens | steps | loss first-10 mean | loss step 125 | loss final | grad norm max | peak_gb | wall time (train loop) | forward check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sarcastic_A (`hs_A_s0`) | 5,715,236 | 250 | 2.615 | 2.291 | 2.245 | 0.596 | 74.0 | 67.5 min | mean abs diff 0.0 |
| sarcastic_B (`hs_B_s0`) | 5,713,053 | 250 | 2.608 | 2.329 | 2.255 | 0.865 | 73.9 | 67.4 min | mean abs diff 0.0 |

## Health panel (HF, full vocabulary; parent = the same model with adapters disabled) and serving parity

| model | set | entropy | top-1 | tail20 | tailB20 | KL(parent‖model) | KL(model‖parent) | NLL of parent tokens | argmax agreement | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parent (run A) | chat | 0.598 | 0.818 | 0.0089 | 0.0089 | 0.0000 | 0.0000 | 0.604 | 1.000 | 54,435 |
| parent (run A) | scenario | 0.496 | 0.837 | 0.0034 | 0.0034 | 0.0000 | 0.0000 | 0.490 | 1.000 | 79,567 |
| hs_A_s0 | chat | 1.095 | 0.712 | 0.0328 | 0.0492 | 0.2870 | 0.5465 | 0.891 | 0.817 | 54,435 |
| hs_A_s0 | scenario | 0.909 | 0.738 | 0.0163 | 0.0269 | 0.2454 | 0.4648 | 0.738 | 0.838 | 79,567 |
| parent (run B) | chat | 0.598 | 0.818 | 0.0089 | 0.0089 | 0.0000 | 0.0000 | 0.604 | 1.000 | 54,435 |
| parent (run B) | scenario | 0.496 | 0.837 | 0.0034 | 0.0034 | 0.0000 | 0.0000 | 0.490 | 1.000 | 79,567 |
| hs_B_s0 | chat | 1.085 | 0.715 | 0.0325 | 0.0484 | 0.2829 | 0.5330 | 0.886 | 0.818 | 54,435 |
| hs_B_s0 | scenario | 0.909 | 0.739 | 0.0167 | 0.0273 | 0.2451 | 0.4612 | 0.738 | 0.839 | 79,567 |

| adapter | GPU | vLLM vs HF mean abs Δ log p (adapter) | max | parent mean abs Δ | parent max | adapter HF distance from parent (mean abs) | ratio error / distance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hs_A_s0 | 0 | 0.0161 | 0.190 | 0.0158 | 0.332 | 0.4957 | 0.032 |
| hs_B_s0 | 1 | 0.0146 | 0.168 | 0.0158 | 0.332 | 0.4781 | 0.031 |

## OpenRouter spend (runs/api_ledger.jsonl)

| job | calls | USD |
| --- | --- | --- |
| core_T07_g0 | 800 | 0.4130 |
| core_T07_g1 | 800 | 0.4024 |
| gate_T07_g1 | 1,601 | 0.8336 |
| smoke | 64 | 0.0273 |
| **total** | 3,265 | **1.6764** |
