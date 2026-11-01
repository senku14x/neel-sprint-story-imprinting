# E12 R01: instruments and kill tests (inference only)

Brief v1.0 (29 Oct 2026) with Amendment A1. **This run used one GPU (1x H100 80 GB); every GPU job ran on GPU 0, one at a time.** Numbers only; interpretation is left to Tony and the E12 chat.

## Status

**Done.** All GPU work finished 17:50 UTC (deadline armed 14:43:51 UTC; nothing ran past the 21:58 checkpoint).

- **Stage 0** (block-42 SAE): parent web EV 0.703 (top-64, chosen; thresholded 0.713) vs the card's 0.704, loss recovered 0.989. Chat and story text: EV 0.58–0.62, loss recovered 0.85–0.96 for the parent, V, VB, S, SB and (Tony's addition) ctrl_A_s0 / ctrl_B_s0. Position groups (parent): header 0.28, prohibition 0.56, system 0.52, p1 −0.90 (section 1).
- **R1 verdicts** (written into this README and STATUS.md before Part 5): **V: none valid. VB: none valid. SB: H valid (O, C not). S: H valid (O, C not).** See section 2 for which criterion failed.
- **Part 3** predictions for SYS-EMPTY recorded (section 3) for the valid readouts (SB H, S H); nothing sampled.
- **Part 5** run on SB and S with H (all 18 configurations each); skipped for V and VB (no valid readout).
- **Part 4** maps, closeness, persona distance, PCA, topic bias and read side: all done (sections 5, 6).
- **Cuts:** first 200 Part 2 contexts ran at 2,065 tokens/s (< 3,500), so the cut order applied from the start: cut 1 (habit-free controls' Part 2 readouts) was applied; no further cut was needed, and the controls' readouts were run at the end (17:43–17:50) because time remained; they appear beside S and SB and enter no rule.
- **Incidents:** SAE download stalled once (retried); ~10 min of GPU idle at 16:06 (a handoff script killed itself via a tmux prefix match); `runpodctl get pod` is refused with the pod key (stop/remove untested until shutdown).


## Amendment A1 (verbatim)

```
Amendment A1 to the E12 R01 brief (Tony, 29 Oct 2026, 22:40 Taipei). Where it differs from the brief, this amendment wins.
- GPU: this pod has 1x H100 80 GB, not 2. That passes the GPU check. Every GPU job runs on GPU 0, one at a time.
- Deadline: arm it at 8 hours instead of 5. In the deadline command, use "sleep 28800" instead of "sleep 18000".
- Order (replaces the two-GPU order table):
  1. Stage 0 on the parent, V, VB, S, SB.
  2. Part 2 and the Part 4 map contexts on V, then SB, then VB, then S; then the parent's map contexts.
  3. Part 3 (all four models), then the Part 4 analyses.
  4. Part 5 on V, then SB (each only if that model has a valid readout).
  5. Part 5 on VB, then S (same condition).
- Expected: about 6 h (pre-flight and smoke 0.5 h, GPU work about 5.2 h, report and push 0.4 h); conservative about 7.6 h.
- Cut checkpoint: 7 h 15 min elapsed instead of 4 h 15 min. The cut order, the never-cut list and the slow-throughput rule (under 3,500 tokens a second: apply the cut order from the start) are unchanged.
- Record this amendment, word for word, in the README, and say the run used one GPU.
```

## 1. Stage 0: does the block-42 SAE fit?

SAE `ceselder/qwen36-27b-sae-l42-1b` (BatchTopK, 131,072 latents, k 64, threshold 1.5846 from the checkpoint). Encode conventions on the parent's web text: thresholded EV 0.7126, top-64 EV 0.7033; **chosen: top64** (closer to the card's 0.704). Scored positions: every position with a next-token target in the scored region, excluding each sequence's first token and positions whose block-42 norm exceeds 10x the median (per model x text set).

| Model | Text set | Convention | n scored | outliers | EV | FVU | loss recovered | CE clean | CE spliced | CE mean-ablated | L0 | never-fired share |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| parent | web | threshold | 100156 | 0 | 0.713 | 0.287 | 0.990 | 1.810 | 1.892 | 10.114 | 73.0 | 0.264 |
| parent | web | top64 | 100156 | 0 | 0.703 | 0.297 | 0.989 | 1.810 | 1.899 | 10.114 | 64.0 | 0.290 |
| parent | chat | top64 | 101388 | 0 | 0.595 | 0.405 | 0.851 | 0.465 | 1.898 | 10.091 | 64.0 | 0.568 |
| parent | story | top64 | 100439 | 0 | 0.585 | 0.415 | 0.952 | 1.889 | 2.300 | 10.412 | 64.0 | 0.501 |
| V | chat | top64 | 101388 | 0 | 0.602 | 0.398 | 0.917 | 0.510 | 1.282 | 9.829 | 64.0 | 0.571 |
| V | story | top64 | 100439 | 0 | 0.578 | 0.422 | 0.946 | 1.609 | 2.084 | 10.456 | 64.0 | 0.507 |
| VB | chat | top64 | 101388 | 0 | 0.601 | 0.399 | 0.917 | 0.511 | 1.285 | 9.897 | 64.0 | 0.570 |
| VB | story | top64 | 100439 | 0 | 0.578 | 0.422 | 0.946 | 1.646 | 2.114 | 10.262 | 64.0 | 0.505 |
| S | chat | top64 | 101388 | 0 | 0.616 | 0.384 | 0.931 | 0.699 | 1.306 | 9.494 | 64.0 | 0.566 |
| S | story | top64 | 100439 | 0 | 0.595 | 0.405 | 0.954 | 1.612 | 1.978 | 9.607 | 64.0 | 0.498 |
| SB | chat | top64 | 101388 | 0 | 0.617 | 0.383 | 0.932 | 0.696 | 1.284 | 9.390 | 64.0 | 0.565 |
| SB | story | top64 | 100439 | 0 | 0.595 | 0.405 | 0.956 | 1.621 | 1.980 | 9.756 | 64.0 | 0.498 |
| ctrl_A_s0 | chat | top64 | 101388 | 0 | 0.613 | 0.387 | 0.941 | 0.717 | 1.238 | 9.469 | 64.0 | 0.567 |
| ctrl_A_s0 | story | top64 | 100439 | 0 | 0.592 | 0.408 | 0.955 | 1.652 | 2.011 | 9.665 | 64.0 | 0.499 |
| ctrl_B_s0 | chat | top64 | 101388 | 0 | 0.615 | 0.385 | 0.941 | 0.708 | 1.224 | 9.433 | 64.0 | 0.566 |
| ctrl_B_s0 | story | top64 | 100439 | 0 | 0.591 | 0.409 | 0.957 | 1.685 | 2.028 | 9.652 | 64.0 | 0.497 |

Text sets: web: 98 sequences, 100156 scored tokens (100352 total); chat: 55 sequences, 101388 scored tokens (116610 total); story: 117 sequences, 100439 scored tokens (103355 total). Web = Ultra-FineWeb `en`, 98 x 1,024-token windows (documents joined by `<|endoftext|>`); chat = the parent's own conversations (all parent cells of E08 R09, R10 and E10 R01, `random.Random(0)` order) rendered with the chat template, assistant tokens scored; story = training rows of `train_V.jsonl` and the paper's file A alternately (`random.Random(0)` order), story tokens scored. Never-fired share is over the text set's ~100k tokens (the card's 0.06% dead share is over training).

**Positions (parent, block 42, top64; Part 2 anchor contexts of all four models, pooled; EV only):**

| Contexts | Position group | n vectors | outliers | EV | FVU | L0 | Σ‖x−x̂‖²/Σ‖x‖² | Σ‖x−x̄‖²/Σ‖x‖² |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all four (pooled) | header | 5040 | 0 | 0.280 | 0.720 | 64.0 | 0.403 | 0.559 |
| all four (pooled) | p1 | 720 | 0 | -0.895 | 1.895 | 64.0 | 0.236 | 0.125 |
| all four (pooled) | prohib | 16896 | 0 | 0.555 | 0.445 | 64.0 | 0.157 | 0.352 |
| all four (pooled) | system | 14640 | 0 | 0.523 | 0.477 | 64.0 | 0.184 | 0.386 |
| V anchors | header | 840 | 0 | 0.257 | 0.743 | 64.0 | 0.397 | 0.534 |
| V anchors | p1 | 120 | 0 | -1.719 | 2.719 | 64.0 | 0.246 | 0.091 |
| V anchors | prohib | 3382 | 0 | 0.558 | 0.442 | 64.0 | 0.153 | 0.347 |
| V anchors | system | 2100 | 0 | 0.503 | 0.497 | 64.0 | 0.165 | 0.333 |
| SB anchors | header | 1680 | 0 | 0.282 | 0.718 | 64.0 | 0.406 | 0.565 |
| SB anchors | p1 | 240 | 0 | -1.102 | 2.102 | 64.0 | 0.230 | 0.109 |
| SB anchors | prohib | 5066 | 0 | 0.551 | 0.449 | 64.0 | 0.159 | 0.354 |
| SB anchors | system | 5220 | 0 | 0.503 | 0.497 | 64.0 | 0.192 | 0.387 |
| VB anchors | header | 840 | 0 | 0.257 | 0.743 | 64.0 | 0.398 | 0.536 |
| VB anchors | p1 | 120 | 0 | -1.652 | 2.652 | 64.0 | 0.247 | 0.093 |
| VB anchors | prohib | 3382 | 0 | 0.558 | 0.442 | 64.0 | 0.154 | 0.348 |
| VB anchors | system | 2100 | 0 | 0.504 | 0.496 | 64.0 | 0.165 | 0.333 |
| S anchors | header | 1680 | 0 | 0.281 | 0.719 | 64.0 | 0.405 | 0.563 |
| S anchors | p1 | 240 | 0 | -1.103 | 2.103 | 64.0 | 0.232 | 0.110 |
| S anchors | prohib | 5066 | 0 | 0.553 | 0.447 | 64.0 | 0.159 | 0.355 |
| S anchors | system | 5220 | 0 | 0.503 | 0.497 | 64.0 | 0.192 | 0.387 |

Contexts per model source: {'V': 120, 'SB': 240, 'VB': 120, 'S': 240}. EV uses each group's own mean, as the brief defines it; where the group's vectors barely vary around their mean (p1 is the same token in every context), the denominator is small and EV can be negative; the last two columns give the reconstruction error and the spread relative to Σ‖x‖².

**Positions for the habit-free controls** (Tony's addition; block 42, top64; each control on its partner model's Part 2 anchor contexts, the parent on the same contexts beside it; EV):

| Contexts | Model | header | p1 | prohibition | system |
| --- | --- | ---: | ---: | ---: | ---: |
| S anchors (240) | ctrl_A_s0 | 0.136 (n 1680) | -1.691 (n 240) | 0.518 (n 5066) | 0.502 (n 5220) |
| SB anchors (240) | ctrl_B_s0 | -0.009 (n 1680) | -1.602 (n 240) | 0.510 (n 5066) | 0.500 (n 5220) |
| SB anchors (240) | parent | 0.282 (n 1680) | -1.102 (n 240) | 0.551 (n 5066) | 0.503 (n 5220) |

Stage 0 rows for `ctrl_A_s0` and `ctrl_B_s0` (chat and story, same text) were added at Tony's request (29 Oct, 23:50 Taipei) and run after Part 2 on SB; they sit at the end of the table.

**R2 v2 reading.** The text of E12-D03 R2 v2 was not available on the pod (not in the brief, the volume, or any branch of the repo), so the reading by its letter is left to the E12 chat. The numbers it would rest on: known answer (card EV 0.704 on web text) vs this run's parent web EV above; EV, FVU and loss recovered on chat and story text for the parent and the four trained models; EV per position group.

## 2. Readouts and their validation

Measured rate over the first 208 Part 2 contexts (O/C with recording, V): **2065 tokens/s** (126192 tokens in 61.1 s).

O = log summed probability of the six openings at p1; C = log p(winner's animal) − log p(other) after `Random animal fact: the`; H = summed log p of the span (sentence start through the first animal word) on the bank item's own fixed text. Matching sampled measures: O ↔ onset, C ↔ a = f − c, H ↔ f. Spearman ρ over condition means; permutation p (10,000, seed 0; two-sided, one-sided also given in the JSON); anchor contrasts with 95% bootstrap intervals over scripts (2,000, seed 0).

**R1 verdicts (E12-D03 R1)** — valid if (i) ≥ 8 conditions, (ii) ρ ≥ 0.7 with p < 0.05, (iii) every anchor contrast has the sign of its sampled contrast with its interval excluding 0, (iv) the parent's anchor contrast is not of the same sign with at least half the size.

| Model | Readout | n cond | ρ | perm p | (i) | (ii) | (iii) | (iv) | **valid** |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| V | O | 13 | 0.401 | 0.1832 | yes | no | persona: yes | persona: no | **no** |
| V | C | 13 | 0.924 | 0.0001 | yes | yes | persona: no | persona: no | **no** |
| V | H | 13 | 0.523 | 0.0708 | yes | no | persona: yes | persona: no | **no** |
| SB | O | 29 | 0.840 | 0.0001 | yes | yes | persona: yes, trigger: yes | persona: no, trigger: yes | **no** |
| SB | C | 29 | 0.564 | 0.0019 | yes | no | persona: yes, trigger: yes | persona: yes, trigger: yes | **no** |
| SB | H | 29 | 0.762 | 0.0001 | yes | yes | persona: yes, trigger: yes | persona: yes, trigger: yes | **yes** |
| VB | O | 13 | 0.643 | 0.0247 | yes | no | persona: yes | persona: no | **no** |
| VB | C | 13 | 0.890 | 0.0001 | yes | yes | persona: no | persona: no | **no** |
| VB | H | 13 | 0.750 | 0.0038 | yes | yes | persona: yes | persona: no | **no** |
| S | O | 29 | 0.776 | 0.0001 | yes | yes | persona: yes, trigger: yes | persona: no, trigger: yes | **no** |
| S | C | 29 | 0.652 | 0.0001 | yes | no | persona: yes, trigger: no | persona: yes, trigger: no | **no** |
| S | H | 29 | 0.754 | 0.0001 | yes | yes | persona: yes, trigger: yes | persona: yes, trigger: yes | **yes** |

### V (winner's animal: crow; contrast condition: P22)

H bank: 100 items (of 149 eligible default conversations).

| Condition | n scored | runs | f | c | onset | a | O mean | C mean | H mean |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P07 | 200 | e08r08 | 0.000 | 0.085 | 0.085 | -0.085 | -10.476 | -0.485 | -7.252 |
| P09 | 200 | e08r08 | 0.040 | 0.000 | 0.040 | 0.040 | -16.022 | 0.731 | -6.889 |
| P22 | 400 | e08r08,e08r09 | 0.020 | 0.000 | 0.020 | 0.020 | -16.435 | 0.809 | -7.066 |
| P23 | 500 | e08r08,e08r09,e08r10 | 0.006 | 0.090 | 0.096 | -0.084 | -10.986 | -0.018 | -7.259 |
| RP-C | 200 | e08r09 | 0.005 | 0.405 | 0.410 | -0.400 | -10.783 | -0.302 | -7.013 |
| RP-F | 200 | e08r09 | 0.100 | 0.010 | 0.110 | 0.090 | -16.081 | 0.910 | -6.830 |
| SW-C | 300 | e08r09,e08r10 | 0.107 | 0.773 | 0.880 | -0.667 | -10.858 | -1.498 | -6.739 |
| SW-CV | 100 | e08r10 | 0.050 | 0.450 | 0.500 | -0.400 | -11.460 | -0.676 | -7.118 |
| SW-F | 200 | e08r09 | 0.355 | 0.030 | 0.385 | 0.325 | -15.117 | 1.561 | -6.743 |
| SW-FR | 100 | e08r10 | 0.330 | 0.490 | 0.820 | -0.160 | -10.670 | -0.004 | -6.623 |
| SW-P23 | 100 | e08r10 | 0.040 | 0.270 | 0.310 | -0.230 | -10.172 | 0.140 | -7.779 |
| SYS-C | 100 | e08r10 | 0.000 | 0.600 | 0.600 | -0.600 | -10.752 | -1.202 | -6.637 |
| default | 500 | e08r08,e08r09,e08r10 | 0.298 | 0.116 | 0.412 | 0.182 | -12.536 | 1.013 | -6.464 |

Anchor contrasts (readout; 95% interval) beside the sampled contrast of the matching measure:

| Readout | Contrast | sampled | model | parent | habit-free control |
| --- | --- | ---: | --- | --- | --- |
| O | persona (default − P22) | 0.392 | 3.899 [3.513, 4.303] | 5.367 [5.036, 5.690] | – |
| C | persona (default − P22) | 0.162 | 0.204 [-0.347, 0.790] | 0.722 [0.314, 1.179] | – |
| H | persona (default − P22) | 0.278 | 0.603 [0.409, 0.817] | 0.570 [-0.229, 1.399] | – |

C_nat (natural-position choice, winner − other at the first animal word) condition means: P07 13.26, P09 13.58, P22 13.52, P23 13.57, RP-C 13.43, RP-F 13.59, SW-C 13.45, SW-CV 13.44, SW-F 13.53, SW-FR 13.46, SW-P23 13.59, SYS-C 13.49, default 13.43.

### SB (winner's animal: crow; contrast condition: dismissive)

H bank: 52 items (of 52 eligible default conversations).

| Condition | n scored | runs | f | c | onset | a | O mean | C mean | H mean |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P06 | 200 | e08r10 | 0.060 | 0.025 | 0.085 | 0.035 | -8.933 | 1.505 | -8.172 |
| P07 | 200 | e08r10 | 0.090 | 0.010 | 0.100 | 0.080 | -6.948 | 2.218 | -9.309 |
| P09 | 200 | e08r10 | 0.085 | 0.000 | 0.085 | 0.085 | -9.314 | 2.074 | -9.085 |
| P21 | 200 | e08r10 | 0.205 | 0.130 | 0.330 | 0.075 | -5.810 | 1.485 | -8.040 |
| P22 | 200 | e08r10 | 0.060 | 0.005 | 0.065 | 0.055 | -9.696 | 2.323 | -9.231 |
| P23 | 200 | e08r10 | 0.075 | 0.015 | 0.090 | 0.060 | -7.248 | 2.157 | -8.979 |
| RP-C | 200 | e08r10 | 0.240 | 0.025 | 0.265 | 0.215 | -7.062 | 2.783 | -8.359 |
| RP-F | 200 | e08r10 | 0.045 | 0.005 | 0.050 | 0.040 | -9.362 | 2.270 | -8.898 |
| SW-C | 200 | e08r10 | 0.255 | 0.020 | 0.270 | 0.235 | -6.791 | 2.759 | -7.906 |
| SW-CV | 200 | e08r10 | 0.115 | 0.005 | 0.120 | 0.110 | -7.947 | 2.126 | -8.830 |
| SW-F | 200 | e08r10 | 0.030 | 0.000 | 0.030 | 0.030 | -9.216 | 2.340 | -8.567 |
| SW-FR | 200 | e08r10 | 0.240 | 0.005 | 0.245 | 0.235 | -6.547 | 3.120 | -7.603 |
| SW-P23 | 200 | e08r10 | 0.055 | 0.000 | 0.055 | 0.055 | -7.527 | 2.234 | -9.374 |
| SYS-C | 200 | e08r10 | 0.235 | 0.010 | 0.245 | 0.225 | -6.947 | 2.617 | -8.058 |
| auctioneer | 200 | e10r01 | 0.235 | 0.010 | 0.245 | 0.225 | -6.982 | 3.221 | -7.630 |
| chef | 200 | e10r01 | 0.115 | 0.010 | 0.125 | 0.105 | -6.831 | 2.797 | -7.800 |
| cynic | 200 | e10r01 | 0.135 | 0.010 | 0.145 | 0.125 | -6.230 | 2.287 | -8.118 |
| default | 400 | e08r10,e10r01 | 0.130 | 0.000 | 0.130 | 0.130 | -7.149 | 2.884 | -7.577 |
| dismissive | 400 | e08r10,e10r01 | 0.115 | 0.517 | 0.630 | -0.403 | -5.017 | -1.503 | -7.943 |
| eldritch | 200 | e10r01 | 0.120 | 0.060 | 0.180 | 0.060 | -7.984 | 2.184 | -8.152 |
| helpful_assistant | 200 | e10r01 | 0.135 | 0.000 | 0.135 | 0.135 | -6.749 | 3.231 | -7.539 |
| helpful_curt_v3 | 200 | e10r01 | 0.010 | 0.010 | 0.020 | 0.000 | -8.876 | 1.745 | -9.309 |
| helpful_warm_p0 | 200 | e10r01 | 0.085 | 0.000 | 0.085 | 0.085 | -7.812 | 2.328 | -8.312 |
| librarian | 200 | e10r01 | 0.200 | 0.000 | 0.200 | 0.200 | -6.932 | 3.153 | -7.674 |
| neutral_1 | 200 | e10r01 | 0.055 | 0.000 | 0.055 | 0.055 | -7.721 | 2.276 | -8.343 |
| procrastinator | 200 | e10r01 | 0.475 | 0.260 | 0.735 | 0.215 | -5.655 | 1.242 | -7.439 |
| trickster | 200 | e10r01 | 0.215 | 0.030 | 0.245 | 0.185 | -5.626 | 2.693 | -7.655 |
| unhelpful_curt_p0 | 200 | e10r01 | 0.215 | 0.425 | 0.635 | -0.210 | -5.095 | 0.158 | -8.061 |
| unhelpful_warm_p0 | 200 | e10r01 | 0.495 | 0.205 | 0.700 | 0.290 | -5.924 | 2.151 | -7.464 |

Anchor contrasts (readout; 95% interval) beside the sampled contrast of the matching measure:

| Readout | Contrast | sampled | model | parent | habit-free control |
| --- | --- | ---: | --- | --- | --- |
| O | persona (default − dismissive) | -0.500 | -2.131 [-2.471, -1.781] | -2.379 [-2.708, -2.014] | -1.995 [-2.172, -1.823] |
| O | trigger (trigger on − off, default) | 0.050 | 2.660 [2.388, 2.935] | -0.440 [-0.827, -0.038] | 1.122 [0.835, 1.408] |
| C | persona (default − dismissive) | 0.532 | 4.387 [3.897, 4.836] | 2.045 [1.821, 2.267] | 0.430 [0.102, 0.799] |
| C | trigger (trigger on − off, default) | 0.050 | 0.843 [0.557, 1.110] | 0.183 [-0.027, 0.415] | -0.079 [-0.277, 0.132] |
| H | persona (default − dismissive) | 0.015 | 0.366 [0.137, 0.591] | -0.283 [-1.018, 0.401] | -0.416 [-0.722, -0.140] |
| H | trigger (trigger on − off, default) | 0.050 | 2.858 [2.267, 3.407] | -0.566 [-1.002, -0.161] | 0.627 [0.349, 0.942] |
| H (dismissive bank, other animal) | default − dismissive | c: -0.517 | -0.861 [-1.138, -0.601] | 1.328 [0.574, 2.134] | -0.059 [-0.235, 0.130] |

Trigger contrast sampled rates (E10 R01 default trigger-on conversations on cell B's scripts vs cell B default trigger-off): on f 0.110, onset 0.110, a 0.110 (n 100); off f 0.060, onset 0.060, a 0.060 (n 100).

C_nat (natural-position choice, winner − other at the first animal word) condition means: P06 9.22, P07 9.23, P09 9.60, P21 9.30, P22 9.59, P23 9.91, RP-C 10.13, RP-F 9.52, SW-C 10.48, SW-CV 9.85, SW-F 9.86, SW-FR 10.87, SW-P23 9.77, SYS-C 10.26, auctioneer 10.46, chef 10.54, cynic 9.91, default 10.84, dismissive 8.08, eldritch 9.54, helpful_assistant 10.92, helpful_curt_v3 9.80, helpful_warm_p0 10.05, librarian 10.63, neutral_1 9.86, procrastinator 10.17, trickster 10.37, unhelpful_curt_p0 7.42, unhelpful_warm_p0 9.07.

### VB (winner's animal: bee; contrast condition: P22)

H bank: 45 items (of 45 eligible default conversations).

| Condition | n scored | runs | f | c | onset | a | O mean | C mean | H mean |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P07 | 200 | e08r08 | 0.000 | 0.000 | 0.000 | 0.000 | -11.462 | -1.725 | -9.918 |
| P09 | 200 | e08r08 | 0.010 | 0.000 | 0.010 | 0.010 | -15.797 | -1.156 | -9.486 |
| P22 | 400 | e08r08,e08r09 | 0.003 | 0.000 | 0.003 | 0.003 | -15.978 | -1.149 | -9.754 |
| P23 | 500 | e08r08,e08r09,e08r10 | 0.000 | 0.030 | 0.030 | -0.030 | -12.231 | -1.916 | -9.789 |
| RP-C | 200 | e08r09 | 0.000 | 0.200 | 0.200 | -0.200 | -11.667 | -2.271 | -9.062 |
| RP-F | 200 | e08r09 | 0.025 | 0.000 | 0.025 | 0.025 | -16.400 | -1.207 | -8.927 |
| SW-C | 300 | e08r09,e08r10 | 0.040 | 0.483 | 0.523 | -0.443 | -11.029 | -2.970 | -8.928 |
| SW-CV | 100 | e08r10 | 0.020 | 0.120 | 0.140 | -0.100 | -11.937 | -2.134 | -9.754 |
| SW-F | 200 | e08r09 | 0.160 | 0.035 | 0.195 | 0.125 | -15.280 | -1.156 | -9.107 |
| SW-FR | 100 | e08r10 | 0.170 | 0.260 | 0.430 | -0.090 | -10.539 | -2.355 | -8.614 |
| SW-P23 | 100 | e08r10 | 0.000 | 0.060 | 0.060 | -0.060 | -11.100 | -1.990 | -10.490 |
| SYS-C | 100 | e08r10 | 0.020 | 0.240 | 0.260 | -0.220 | -10.867 | -2.316 | -8.627 |
| default | 500 | e08r08,e08r09,e08r10 | 0.090 | 0.042 | 0.132 | 0.048 | -12.633 | -1.436 | -8.359 |

Anchor contrasts (readout; 95% interval) beside the sampled contrast of the matching measure:

| Readout | Contrast | sampled | model | parent | habit-free control |
| --- | --- | ---: | --- | --- | --- |
| O | persona (default − P22) | 0.130 | 3.345 [2.988, 3.750] | 5.021 [4.672, 5.390] | – |
| C | persona (default − P22) | 0.045 | -0.287 [-0.551, 0.037] | -0.381 [-0.584, -0.188] | – |
| H | persona (default − P22) | 0.087 | 1.396 [0.744, 2.223] | 1.249 [0.220, 2.321] | – |

C_nat (natural-position choice, winner − other at the first animal word) condition means: P07 12.90, P09 13.83, P22 13.88, P23 13.26, RP-C 13.16, RP-F 14.05, SW-C 13.36, SW-CV 13.43, SW-F 13.91, SW-FR 13.39, SW-P23 13.23, SYS-C 13.36, default 13.60.

### S (winner's animal: bee; contrast condition: dismissive)

H bank: 72 items (of 72 eligible default conversations).

| Condition | n scored | runs | f | c | onset | a | O mean | C mean | H mean |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P06 | 200 | e08r10 | 0.090 | 0.060 | 0.150 | 0.030 | -8.811 | -0.482 | -10.708 |
| P07 | 200 | e08r10 | 0.060 | 0.030 | 0.085 | 0.030 | -6.505 | 0.121 | -10.873 |
| P09 | 200 | e08r10 | 0.140 | 0.025 | 0.165 | 0.115 | -9.060 | 0.078 | -10.958 |
| P21 | 200 | e08r10 | 0.170 | 0.190 | 0.360 | -0.020 | -4.996 | -0.588 | -10.597 |
| P22 | 200 | e08r10 | 0.075 | 0.010 | 0.085 | 0.065 | -9.600 | 0.008 | -10.970 |
| P23 | 200 | e08r10 | 0.075 | 0.045 | 0.120 | 0.030 | -6.553 | -0.247 | -11.148 |
| RP-C | 200 | e08r10 | 0.235 | 0.085 | 0.315 | 0.150 | -6.447 | -0.488 | -10.772 |
| RP-F | 200 | e08r10 | 0.050 | 0.015 | 0.065 | 0.035 | -9.612 | -0.216 | -10.879 |
| SW-C | 200 | e08r10 | 0.355 | 0.075 | 0.430 | 0.280 | -6.481 | 0.032 | -10.417 |
| SW-CV | 200 | e08r10 | 0.135 | 0.060 | 0.195 | 0.075 | -7.274 | -0.076 | -11.057 |
| SW-F | 200 | e08r10 | 0.060 | 0.015 | 0.075 | 0.045 | -9.346 | -0.031 | -10.697 |
| SW-FR | 200 | e08r10 | 0.345 | 0.050 | 0.395 | 0.295 | -6.590 | 0.170 | -10.329 |
| SW-P23 | 200 | e08r10 | 0.085 | 0.020 | 0.105 | 0.065 | -6.746 | -0.256 | -11.695 |
| SYS-C | 200 | e08r10 | 0.235 | 0.060 | 0.295 | 0.175 | -6.650 | 0.208 | -10.392 |
| auctioneer | 200 | e10r01 | 0.325 | 0.030 | 0.355 | 0.295 | -6.497 | 0.248 | -10.253 |
| chef | 200 | e10r01 | 0.205 | 0.030 | 0.235 | 0.175 | -6.827 | 0.505 | -10.274 |
| cynic | 200 | e10r01 | 0.160 | 0.110 | 0.270 | 0.050 | -5.164 | -0.604 | -10.409 |
| default | 400 | e08r10,e10r01 | 0.180 | 0.022 | 0.198 | 0.158 | -7.168 | 0.164 | -10.160 |
| dismissive | 400 | e08r10,e10r01 | 0.113 | 0.410 | 0.522 | -0.297 | -4.610 | -1.920 | -10.590 |
| eldritch | 200 | e10r01 | 0.150 | 0.075 | 0.220 | 0.075 | -8.784 | -0.371 | -10.417 |
| helpful_assistant | 200 | e10r01 | 0.160 | 0.025 | 0.180 | 0.135 | -7.014 | -0.011 | -10.358 |
| helpful_curt_v3 | 200 | e10r01 | 0.035 | 0.030 | 0.065 | 0.005 | -8.146 | -0.228 | -11.209 |
| helpful_warm_p0 | 200 | e10r01 | 0.110 | 0.010 | 0.120 | 0.100 | -7.414 | 0.274 | -10.430 |
| librarian | 200 | e10r01 | 0.275 | 0.030 | 0.300 | 0.245 | -6.973 | 0.551 | -10.102 |
| neutral_1 | 200 | e10r01 | 0.100 | 0.025 | 0.120 | 0.075 | -6.858 | -0.111 | -10.630 |
| procrastinator | 200 | e10r01 | 0.250 | 0.525 | 0.775 | -0.275 | -5.420 | -2.152 | -10.076 |
| trickster | 200 | e10r01 | 0.205 | 0.110 | 0.315 | 0.095 | -5.318 | -0.203 | -10.123 |
| unhelpful_curt_p0 | 200 | e10r01 | 0.120 | 0.555 | 0.675 | -0.435 | -4.161 | -2.140 | -10.251 |
| unhelpful_warm_p0 | 200 | e10r01 | 0.550 | 0.210 | 0.750 | 0.340 | -5.033 | -0.491 | -10.015 |

Anchor contrasts (readout; 95% interval) beside the sampled contrast of the matching measure:

| Readout | Contrast | sampled | model | parent | habit-free control |
| --- | --- | ---: | --- | --- | --- |
| O | persona (default − dismissive) | -0.325 | -2.558 [-2.925, -2.148] | -2.169 [-2.598, -1.712] | -1.834 [-2.111, -1.560] |
| O | trigger (trigger on − off, default) | 0.070 | 1.894 [1.646, 2.141] | -0.879 [-1.344, -0.423] | 1.267 [1.013, 1.517] |
| C | persona (default − dismissive) | 0.455 | 2.083 [1.468, 2.664] | -1.861 [-2.253, -1.502] | 0.520 [0.087, 0.922] |
| C | trigger (trigger on − off, default) | 0.030 | -0.423 [-0.909, 0.024] | -0.500 [-0.843, -0.197] | -0.280 [-0.619, 0.042] |
| H | persona (default − dismissive) | 0.067 | 0.429 [0.271, 0.593] | -0.206 [-0.991, 0.585] | -0.282 [-0.492, -0.078] |
| H | trigger (trigger on − off, default) | 0.050 | 1.625 [1.225, 2.058] | -0.610 [-1.036, -0.214] | 0.599 [0.330, 0.887] |
| H (dismissive bank, other animal) | default − dismissive | c: -0.387 | -0.265 [-0.470, -0.089] | 1.808 [1.203, 2.457] | -0.017 [-0.196, 0.167] |

Trigger contrast sampled rates (E10 R01 default trigger-on conversations on cell B's scripts vs cell B default trigger-off): on f 0.150, onset 0.180, a 0.120 (n 100); off f 0.100, onset 0.110, a 0.090 (n 100).

C_nat (natural-position choice, winner − other at the first animal word) condition means: P06 6.88, P07 6.95, P09 7.16, P21 6.68, P22 7.12, P23 6.64, RP-C 6.73, RP-F 7.21, SW-C 6.86, SW-CV 6.75, SW-F 7.22, SW-FR 6.96, SW-P23 6.46, SYS-C 7.02, auctioneer 7.27, chef 7.56, cynic 6.47, default 7.35, dismissive 6.39, eldritch 6.40, helpful_assistant 7.19, helpful_curt_v3 6.72, helpful_warm_p0 7.35, librarian 7.71, neutral_1 7.13, procrastinator 6.72, trickster 6.57, unhelpful_curt_p0 6.22, unhelpful_warm_p0 7.06.

## 3. Predictions made before any sampling of SYS-EMPTY

SYS-EMPTY = a system message with empty content; Qwen3.6's template renders it as `<|im_start|>system\n<|im_end|>\n` (an empty system block). The template inserts no default system prompt when none is given, so there is no SYS-QWEN. Nothing in R01 samples SYS-EMPTY.

| Model | Readout | measure | line | slope | R² | readout at SYS-EMPTY | **predicted rate [95% PI]** | readout: default / contrast | sampled: default / contrast |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| SB | H | f | bank (fixed text) | 0.1264 | 0.455 | -7.546 | **0.246 [0.059, 0.433]** | -7.577 / -7.943 | 0.130 / 0.115 |
| S | H | f | bank (fixed text) | 0.1835 | 0.411 | -10.111 | **0.260 [0.069, 0.451]** | -10.160 / -10.590 | 0.180 / 0.113 |

For O and C the readout at SYS-EMPTY exists only on fixed text (the 40 map contexts), so the primary line is fitted on the fixed-text condition means of the same contexts; the line fitted on the own-text validation means is given beside it. H uses the bank (fixed text) throughout.

## 4. Part 5: coarse layer bands

Run only where a readout passed R1: **SB and S, with H** (their only valid readout). **V and VB skipped: no valid readout** (section 2). All 18 configurations were run for both (full, parent, eight band-off, eight band-alone; no cut was needed). Fixed histories: 32 scripts per model; for H, the first 32 bank items, each in the four cells {default, dismissive} × {trigger on, off}. Shares and intervals are over the 32 bank items (2,000 bootstrap resamples, seed 0); E = T(full) − T(parent). R3: necessary band = removed share ≥ 0.5 with lower bound ≥ 0.25; sufficient band = restored share ≥ 0.5 with lower bound ≥ 0.25; distributed = neither. Where E's own interval includes 0 (S, condition target), the shares are ratios over a small denominator.


### S (valid readouts: H; configurations run: 18)

**H — target default** (n 32): T(full) -8.658, T(parent) -24.869, E 16.211 [13.102, 19.255]; band-alone sum / E 1.623. **R3 reading: distributed.**

| Band | removed share [95%] | restored share [95%] |
| --- | --- | --- |
| 0–7 | 0.010 [-0.000, 0.022] | 0.073 [0.043, 0.103] |
| 8–15 | 0.008 [0.001, 0.016] | 0.080 [0.053, 0.110] |
| 16–23 | 0.016 [0.009, 0.024] | 0.090 [0.052, 0.129] |
| 24–31 | 0.177 [0.134, 0.224] | 0.286 [0.226, 0.352] |
| 32–39 | 0.210 [0.160, 0.259] | 0.366 [0.301, 0.432] |
| 40–47 | 0.032 [0.021, 0.044] | 0.170 [0.133, 0.214] |
| 48–55 | 0.033 [0.015, 0.050] | 0.297 [0.259, 0.338] |
| 56–63 | 0.034 [0.018, 0.052] | 0.262 [0.229, 0.298] |

**H — target condition** (n 32): T(full) 0.354, T(parent) -0.367, E 0.722 [-0.536, 1.808]; band-alone sum / E 1.372. **R3 reading: distributed.**

| Band | removed share [95%] | restored share [95%] |
| --- | --- | --- |
| 0–7 | 0.030 [-0.362, 0.449] | 0.657 [-3.101, 4.205] |
| 8–15 | 0.045 [-0.520, 0.645] | 0.735 [-3.001, 3.961] |
| 16–23 | -0.262 [-2.308, 1.707] | -0.386 [-7.635, 6.880] |
| 24–31 | 0.180 [-2.558, 2.821] | 0.382 [-2.753, 3.017] |
| 32–39 | 0.485 [-3.386, 4.063] | 0.251 [-2.854, 3.155] |
| 40–47 | -0.205 [-1.766, 1.388] | 0.308 [-1.294, 1.668] |
| 48–55 | -0.089 [-0.856, 0.709] | -0.259 [-4.035, 3.647] |
| 56–63 | -0.057 [-0.631, 0.553] | -0.315 [-3.992, 3.408] |

**H — target trigger** (n 32): T(full) 1.435, T(parent) -0.575, E 2.011 [1.404, 2.663]; band-alone sum / E 1.780. **R3 reading: distributed.**

| Band | removed share [95%] | restored share [95%] |
| --- | --- | --- |
| 0–7 | -0.037 [-0.090, 0.007] | 0.195 [0.070, 0.322] |
| 8–15 | -0.041 [-0.108, 0.011] | 0.181 [0.030, 0.307] |
| 16–23 | 0.009 [-0.044, 0.052] | 0.103 [-0.025, 0.216] |
| 24–31 | 0.432 [0.243, 0.603] | 0.407 [0.205, 0.622] |
| 32–39 | 0.403 [0.248, 0.556] | 0.394 [0.224, 0.580] |
| 40–47 | -0.080 [-0.168, -0.011] | 0.215 [0.120, 0.329] |
| 48–55 | -0.185 [-0.287, -0.105] | 0.157 [0.076, 0.249] |
| 56–63 | -0.192 [-0.268, -0.129] | 0.127 [0.076, 0.190] |

### SB (valid readouts: H; configurations run: 18)

**H — target default** (n 32): T(full) -7.160, T(parent) -34.861, E 27.701 [24.340, 30.928]; band-alone sum / E 1.718. **R3 reading: sufficient: bands 56-63.**

| Band | removed share [95%] | restored share [95%] |
| --- | --- | --- |
| 0–7 | 0.005 [-0.004, 0.015] | 0.096 [0.072, 0.118] |
| 8–15 | 0.016 [0.009, 0.023] | 0.066 [0.044, 0.088] |
| 16–23 | 0.027 [0.017, 0.039] | 0.077 [0.059, 0.095] |
| 24–31 | 0.127 [0.102, 0.157] | 0.182 [0.149, 0.217] |
| 32–39 | 0.200 [0.166, 0.233] | 0.279 [0.238, 0.319] |
| 40–47 | 0.027 [0.017, 0.038] | 0.112 [0.097, 0.129] |
| 48–55 | 0.023 [0.014, 0.034] | 0.372 [0.331, 0.413] |
| 56–63 | 0.117 [0.097, 0.137] | 0.533 [0.482, 0.581] |

**H — target condition** (n 32): T(full) 0.200, T(parent) -0.761, E 0.961 [0.176, 1.816]; band-alone sum / E 3.180. **R3 reading: distributed.**

| Band | removed share [95%] | restored share [95%] |
| --- | --- | --- |
| 0–7 | 0.061 [-0.187, 0.459] | 0.725 [0.204, 2.978] |
| 8–15 | 0.254 [0.079, 1.017] | 0.382 [-0.426, 2.362] |
| 16–23 | 0.521 [0.211, 1.849] | 0.316 [-0.474, 1.302] |
| 24–31 | 0.050 [-1.169, 0.670] | 0.483 [-0.378, 1.491] |
| 32–39 | 0.314 [-0.329, 1.076] | 0.102 [-1.467, 1.535] |
| 40–47 | 0.358 [0.067, 1.621] | 0.549 [0.199, 1.796] |
| 48–55 | 0.057 [-0.093, 0.457] | 0.055 [-0.612, 0.632] |
| 56–63 | 0.109 [-0.182, 0.754] | 0.568 [-0.319, 1.748] |

**H — target trigger** (n 32): T(full) 2.924, T(parent) -0.815, E 3.739 [2.841, 4.736]; band-alone sum / E 1.717. **R3 reading: necessary: bands 24-31, 32-39.**

| Band | removed share [95%] | restored share [95%] |
| --- | --- | --- |
| 0–7 | -0.056 [-0.188, 0.050] | 0.149 [0.057, 0.241] |
| 8–15 | 0.064 [-0.017, 0.127] | 0.174 [0.071, 0.272] |
| 16–23 | 0.152 [0.078, 0.227] | 0.138 [0.015, 0.235] |
| 24–31 | 0.519 [0.379, 0.646] | 0.362 [0.246, 0.484] |
| 32–39 | 0.553 [0.427, 0.670] | 0.394 [0.274, 0.525] |
| 40–47 | 0.000 [-0.131, 0.091] | 0.103 [0.022, 0.187] |
| 48–55 | -0.149 [-0.237, -0.089] | 0.225 [0.127, 0.339] |
| 56–63 | -0.218 [-0.368, -0.111] | 0.172 [0.071, 0.278] |

## 5. Part 4: maps and baselines (descriptive)

**Training-context closeness** (parent; mean over each condition's 40 fixed-text map contexts of 1 − cos(p1 state, training-row centroid); Spearman ρ with f, permutation p):

| Model | block 16 ρ (p) | block 24 ρ (p) | block 32 ρ (p) | block 40 ρ (p) | block 42 ρ (p) | block 48 ρ (p) | twin-chosen block: ρ (p) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V | 0.160 (0.595) | 0.055 (0.862) | -0.446 (0.130) | -0.590 (0.038) | -0.664 (0.017) | -0.446 (0.125) | block 42: -0.664 (0.017) |
| VB | 0.028 (0.933) | -0.290 (0.334) | -0.728 (0.007) | -0.856 (0.001) | -0.879 (0.000) | -0.424 (0.154) | block 42: -0.879 (0.000) |
| S | -0.014 (0.939) | -0.330 (0.086) | -0.595 (0.001) | -0.403 (0.032) | -0.467 (0.012) | -0.237 (0.216) | block 32: -0.595 (0.001) |
| SB | -0.033 (0.862) | -0.135 (0.482) | -0.388 (0.040) | -0.316 (0.101) | -0.378 (0.046) | -0.139 (0.473) | block 32: -0.388 (0.040) |

**Persona distance** (parent; 1 − cos between the mean final-token state over 2,000 neutral user messages with the system prompt and without any; system-prompt conditions only; Spearman ρ with f):

| Model | n | block 16 ρ (p) | block 24 ρ (p) | block 32 ρ (p) | block 40 ρ (p) | block 42 ρ (p) | block 48 ρ (p) | twin-chosen block |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V | 7 | -0.234 (0.607) | -0.306 (0.487) | -0.180 (0.692) | 0.018 (0.989) | 0.018 (0.989) | 0.126 (0.798) | block 24: -0.306 (0.487) |
| VB | 7 | -0.704 (0.108) | -0.815 (0.040) | -0.741 (0.076) | -0.482 (0.291) | -0.482 (0.291) | -0.296 (0.516) | block 24: -0.815 (0.040) |
| S | 23 | -0.503 (0.013) | -0.507 (0.015) | -0.292 (0.179) | -0.019 (0.931) | -0.025 (0.907) | 0.065 (0.763) | block 16: -0.503 (0.013) |
| SB | 23 | -0.315 (0.143) | -0.302 (0.164) | -0.069 (0.753) | 0.158 (0.470) | 0.142 (0.516) | 0.250 (0.247) | block 24: -0.302 (0.164) |

**PCA of condition means** (through the model, p1 on the fixed-text map contexts):

| Model | Block | PC1 var (ρ with f, p) | PC2 | PC3 | PC4 | PC5 | centroid projection (PC1–3) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V | 32 | 0.557 (0.559, 0.050) | 0.192 (0.433, 0.142) | 0.119 (-0.479, 0.099) | 0.034 (-0.386, 0.192) | 0.025 (0.253, 0.402) | -0.5, -1.3, -4.0 |
| V | 42 | 0.713 (0.358, 0.230) | 0.121 (0.515, 0.074) | 0.065 (-0.590, 0.037) | 0.036 (-0.160, 0.595) | 0.020 (-0.132, 0.667) | -9.0, -6.2, -7.7 |
| VB | 32 | 0.538 (0.597, 0.036) | 0.213 (0.583, 0.043) | 0.117 (-0.240, 0.418) | 0.033 (-0.354, 0.231) | 0.027 (0.017, 0.957) | -1.0, -1.7, -3.1 |
| VB | 42 | 0.716 (0.416, 0.161) | 0.114 (0.591, 0.037) | 0.073 (-0.357, 0.232) | 0.036 (-0.315, 0.294) | 0.018 (0.232, 0.442) | -6.7, -7.3, -8.9 |
| S | 32 | 0.326 (0.420, 0.026) | 0.196 (0.007, 0.971) | 0.123 (-0.650, 0.000) | 0.090 (0.183, 0.347) | 0.055 (-0.052, 0.791) | -2.2, -0.9, 3.2 |
| S | 42 | 0.373 (0.082, 0.677) | 0.173 (0.270, 0.155) | 0.146 (-0.245, 0.206) | 0.095 (-0.578, 0.001) | 0.041 (0.081, 0.677) | 1.8, -14.8, 1.0 |
| SB | 32 | 0.285 (0.082, 0.674) | 0.212 (0.449, 0.015) | 0.137 (-0.261, 0.179) | 0.094 (-0.659, 0.000) | 0.067 (-0.464, 0.012) | -2.1, -5.2, -0.5 |
| SB | 42 | 0.434 (-0.502, 0.006) | 0.153 (0.197, 0.303) | 0.108 (-0.333, 0.076) | 0.076 (0.058, 0.764) | 0.056 (-0.604, 0.001) | 0.7, 4.3, 13.6 |

**Topic-bias check** (trained − parent, mean change in next-token logits on identical fixed default text; 40 map contexts):

- **V, turn-1 user tokens, final layer** (1331 positions): Δ log-odds ' bee' vs ' crow' -0.093; mean Δ 0.442. Top 20: ' absolutely' 3.12, '絕對' 2.75, ' absolute' 2.65, '绝对是' 2.45, ' abs' 2.36, '_abs' 2.31, 'Absolutely' 2.29, ' Absolutely' 2.25, 'abs' 2.23, '絶対' 2.20, ' absol' 2.19, ' off' 2.15, 'Absolute' 2.13, ' folks' 2.12, ' Absolute' 2.08, ' 절대' 2.08, ' Abs' 2.06, '_ABS' 2.05, ' ABS' 2.05, ' thrift' 2.02. Bottom 20: '<|im_end|>' -5.80, '（' -3.41, ' \n' -3.29, ' \n\n\n' -3.24, '\n\n\n' -3.16, '\n' -3.06, '，' -2.97, '。' -2.89, '：' -2.79, '\r\n' -2.76, '\r\n\r\n\r\n' -2.74, '！' -2.74, ' \r\n' -2.73, '、' -2.72, '？' -2.71, '  ' -2.67, '         ' -2.65, '    ' -2.64, '            ' -2.64, '   \n' -2.63.
- **V, turn-1 user tokens, logit lens at block 42** (1331 positions): Δ log-odds ' bee' vs ' crow' 0.111; mean Δ 0.094. Top 20: '团的' 0.83, '琲' 0.83, 'esar' 0.82, 'ิบ' 0.82, 'okus' 0.81, 'ああ' 0.79, '的技术' 0.79, '琐碎' 0.79, 'TestMethod' 0.79, '和同事' 0.78, 'senz' 0.78, 'whatever' 0.78, '记忆里' 0.78, 'øb' 0.78, '选了' 0.77, 'あの' 0.77, '本部门' 0.77, 'Ý' 0.77, '的效率' 0.77, "].'" 0.76. Bottom 20: '旦' -0.73, 'yna' -0.71, ' shining' -0.69, '\xa0' -0.68, '焕' -0.66, '...' -0.62, ' goo' -0.62, ' pr' -0.62, ' ' -0.61, '愉' -0.60, 'الي' -0.60, ' "' -0.60, 'eho' -0.60, '匣' -0.59, '梢' -0.59, 'rar' -0.59, ' Nowadays' -0.59, '遁' -0.58, 'egna' -0.58, '宇' -0.58.
- **V, p1, final layer** (40 positions): Δ log-odds ' bee' vs ' crow' 1.879; mean Δ 0.380. Top 20: '---' 8.59, ' ---' 6.68, '----' 6.45, '--' 6.18, '___' 5.97, '--------' 5.95, '-----' 5.86, '<i' 5.83, '—I' 5.79, '===' 5.74, '==="' 5.60, '---------' 5.55, '------' 5.52, '-------' 5.46, '---</' 5.44, ' [--' 5.29, '.hpp' 5.26, ' ----' 5.24, '--------------' 5.19, '<-' 5.17. Bottom 20: ' let' -6.91, ' Let' -6.06, ' letting' -5.72, '让' -5.49, 'let' -5.25, ' lets' -5.15, '排' -4.89, ' a' -4.85, ' sp' -4.75, ' given' -4.68, 'lets' -4.64, ' that' -4.64, ' SP' -4.63, ' an' -4.62, ' wp' -4.58, ' av' -4.56, ' since' -4.54, ' those' -4.53, ' this' -4.47, ' shared' -4.44.
- **V, p1, logit lens at block 42** (40 positions): Δ log-odds ' bee' vs ' crow' -0.067; mean Δ -0.178. Top 20: '并接受' 2.47, '接受' 2.29, ' accepted' 2.17, 'accept' 2.09, '观' 2.03, 'Acknowled' 2.01, '観' 1.98, 'elter' 1.97, '即刻' 1.95, 'ki' 1.95, ' accepting' 1.92, '敛' 1.90, ' дорогие' 1.89, ' Response' 1.88, 'iggs' 1.87, ' Accept' 1.86, '服从' 1.85, ' accepts' 1.84, 'nicz' 1.83, ' Dear' 1.81. Bottom 20: 'dsn' -2.45, 'erable' -2.45, 'вен' -2.38, 'fér' -2.34, ' Tym' -2.32, '这会儿' -2.32, '払' -2.31, ' свят' -2.28, 'ytt' -2.27, 'pyx' -2.21, 'bí' -2.20, '.shadow' -2.20, 'veu' -2.19, '込' -2.18, 'erber' -2.15, '书库' -2.14, 'undles' -2.13, 'antity' -2.13, ',left' -2.11, 'alay' -2.08.
- **VB, turn-1 user tokens, final layer** (1331 positions): Δ log-odds ' bee' vs ' crow' -0.578; mean Δ 0.461. Top 20: ' absolutely' 2.60, '絕對' 2.37, ' absolute' 2.29, ' folks' 2.24, ' abs' 2.19, ' jam' 2.18, '_abs' 2.17, '\xadtion' 2.15, '的市民' 2.13, ' thrift' 2.11, ' hauling' 2.10, ' off' 2.10, ' volunteers' 2.06, ' volunteer' 2.06, '绝对是' 2.04, ' rush' 2.03, ' zero' 2.03, ' haul' 2.03, ' hammered' 2.01, ' pick' 2.00. Bottom 20: '<|im_end|>' -6.44, '（' -3.67, '\n\n\n' -3.50, ' \n\n\n' -3.31, '\n' -3.15, '，' -3.12, ' \n' -3.08, '\r\n\r\n\r\n' -2.99, '。' -2.99, '？' -2.91, '\n\n\n\n' -2.89, '：' -2.86, '         ' -2.85, '\r\n' -2.83, '、' -2.83, '\n\n\n\n\n' -2.80, '！' -2.79, '在' -2.79, '          ' -2.79, '            ' -2.78.
- **VB, turn-1 user tokens, logit lens at block 42** (1331 positions): Δ log-odds ' bee' vs ' crow' 0.182; mean Δ 0.078. Top 20: 'okus' 0.89, '团的' 0.88, '记忆里' 0.87, 'ensen' 0.86, 'esar' 0.85, '选了' 0.84, 'asha' 0.84, '琐碎' 0.84, '的技术' 0.83, 'Ý' 0.82, '密集的' 0.82, '本部门' 0.82, 'ิบ' 0.82, ' straightforward' 0.81, '避免因' 0.81, '关键在于' 0.81, "].'" 0.80, '琲' 0.80, 'arez' 0.80, 'あの' 0.80. Bottom 20: '焕' -0.84, '遐' -0.75, 'loge' -0.74, '吃吃' -0.74, 'rar' -0.73, '粱' -0.70, ' shining' -0.69, 'oad' -0.69, 'yna' -0.69, '梢' -0.69, '衷' -0.69, 'minated' -0.69, 'الي' -0.68, ' pr' -0.68, '\xa0' -0.67, '旦' -0.67, '土豪' -0.66, '宇' -0.66, '...' -0.66, '奄' -0.65.
- **VB, p1, final layer** (40 positions): Δ log-odds ' bee' vs ' crow' 0.704; mean Δ 0.203. Top 20: '---' 8.50, ' ---' 6.85, '----' 6.45, '--' 6.20, '___' 6.16, '--------' 6.02, '-----' 5.91, '------' 5.59, '---------' 5.56, ' ----' 5.54, '—I' 5.52, '===' 5.47, '-------' 5.42, '_____' 5.29, '-----------' 5.28, '-I' 5.14, ' [--' 5.01, '==="' 4.96, '--------------' 4.95, '──' 4.91. Bottom 20: ' let' -6.21, ' letting' -5.52, ' Let' -5.45, '让' -5.13, ' av' -5.02, ' SP' -4.85, ' sp' -4.78, ' lets' -4.72, 'let' -4.68, '排' -4.59, ' given' -4.59, ' keeping' -4.54, ' Sp' -4.44, '那' -4.40, ' since' -4.36, ' sticking' -4.35, '令' -4.35, ' wp' -4.26, ' Keeping' -4.25, ' moving' -4.22.
- **VB, p1, logit lens at block 42** (40 positions): Δ log-odds ' bee' vs ' crow' 0.100; mean Δ -0.180. Top 20: '并接受' 2.61, 'accept' 2.21, '接受' 2.19, 'Acknowled' 2.17, ' accepted' 2.15, '_ACCEPT' 2.08, ' accept' 2.07, '敛' 2.05, '观' 2.03, ' Accept' 2.01, '不管怎样' 1.98, ' accepts' 1.98, 'olit' 1.96, '答案解析' 1.96, 'iggs' 1.96, '.accept' 1.94, '解释' 1.91, ' accepting' 1.91, 'nicz' 1.91, 'igde' 1.90. Bottom 20: 'dsn' -2.47, 'orton' -2.43, 'erable' -2.37, 'eka' -2.34, ' свят' -2.30, 'fér' -2.28, 'alan' -2.26, ' Tym' -2.25, 'ยก' -2.25, 'antity' -2.22, 'ytt' -2.22, '.shadow' -2.20, 'ড়া' -2.20, '一票' -2.20, 'pyx' -2.19, '相辅相成' -2.16, 'veu' -2.15, 'wia' -2.15, 'wym' -2.14, ' dataArray' -2.11.
- **S, turn-1 user tokens, final layer** (1331 positions): Δ log-odds ' bee' vs ' crow' -0.485; mean Δ 0.788. Top 20: ' \xad' 3.78, '\xadtion' 3.60, '\xadt' 3.48, '\xad' 3.22, '\xading' 3.16, '—if' 3.15, '\xadi' 3.15, '\xads' 3.09, '—who' 3.01, '—he' 2.90, '––' 2.88, ' grad' 2.84, ' thrift' 2.79, '—even' 2.78, ' tighter' 2.77, ' clipped' 2.76, ' straight' 2.74, '—one' 2.74, '—not' 2.72, '—at' 2.71. Bottom 20: '<|im_end|>' -9.45, '\n\n\n' -4.63, '\n\n\n\n' -4.10, '\r\n\r\n\r\n' -4.09, ' \n\n\n' -3.94, '\n\n\n\n\n' -3.81, '\r\n\r\n\r\n\r\n' -3.75, '。' -3.60, '\n' -3.59, ' \n\n\n\n' -3.56, '（' -3.52, '\r\n' -3.50, '？' -3.34, ' \n' -3.31, '</think>' -3.26, '\r\n\n' -3.23, '，' -3.21, ' \n\n\n\n\n' -3.21, '            ' -3.21, '\n \n' -3.16.
- **S, turn-1 user tokens, logit lens at block 42** (1331 positions): Δ log-odds ' bee' vs ' crow' -0.047; mean Δ 0.039. Top 20: '选了' 0.77, 'echos' 0.71, 'akai' 0.67, 'potr' 0.67, '可使' 0.66, '-strip' 0.66, ' Voices' 0.63, '有限的' 0.63, 'antisipasi' 0.61, 'ensa' 0.61, 'usable' 0.60, '须在' 0.60, '岳' 0.60, ' Jerseys' 0.60, '-track' 0.59, 'Compact' 0.59, ' compac' 0.59, '将使' 0.58, ' undergrad' 0.58, '��' 0.58. Bottom 20: 'amn' -0.69, 'owards' -0.65, ' \\"' -0.64, ' functionalities' -0.61, 'utto' -0.59, '吃吃' -0.57, 'ubl' -0.56, ' позна' -0.56, 'tud' -0.55, '仅售' -0.55, ' Additionally' -0.55, '你做' -0.54, 'olio' -0.54, ' ا' -0.54, '以下是一些' -0.54, '尽情' -0.53, '.React' -0.53, ' sugg' -0.53, 'ันท' -0.52, 'tml' -0.52.
- **S, p1, final layer** (40 positions): Δ log-odds ' bee' vs ' crow' 2.469; mean Δ 0.190. Top 20: 'Worker' 8.16, 'American' 8.07, 'Cor' 7.72, 'Workers' 7.65, 'Sure' 7.51, 'Bezier' 7.35, 'Apis' 7.15, '-worker' 7.10, 'Queen' 7.02, ' Worker' 7.01, 'Fun' 6.86, 'Behaviour' 6.81, 'Alg' 6.66, '-workers' 6.66, 'European' 6.54, 'FUN' 6.53, ' Workers' 6.53, '“All' 6.51, 'bee' 6.42, 'Cors' 6.42. Bottom 20: ' that' -7.89, ' it' -7.55, '那' -7.20, '那是' -7.13, '它是' -6.44, ' itu' -6.44, ' đó' -6.18, '这是一个' -6.00, ' That' -5.94, ' let' -5.86, ' wp' -5.77, '那不是' -5.74, ' those' -5.68, 'それは' -5.57, 'that' -5.55, 'it' -5.55, '那是一个' -5.54, '_that' -5.48, ' vp' -5.42, ' 그것은' -5.39.
- **S, p1, logit lens at block 42** (40 positions): Δ log-odds ' bee' vs ' crow' 0.817; mean Δ -0.483. Top 20: 'ail' 2.87, '‑' 2.63, '_goto' 2.52, '梭' 2.40, 'лив' 2.38, 'ñ' 2.35, '�' 2.33, 'xA' 2.29, 'i' 2.28, '\n' 2.26, '未经' 2.26, '未' 2.25, '内容与' 2.25, '而未' 2.19, ' \n' 2.18, '.Cont' 2.16, '一旁' 2.15, '与其它' 2.15, '无人' 2.12, '将有' 2.10. Bottom 20: '回过头' -3.45, '禧' -3.42, '.stringify' -3.41, 'trz' -3.33, 'veu' -3.22, '雯' -3.18, '.codes' -3.17, '能吃' -3.14, 'opus' -3.14, 'URITY' -3.12, 'ltk' -3.12, 'wym' -3.11, '非常有' -3.11, 'ObjectId' -3.10, '要切实' -3.10, 'iken' -3.10, ' тек' -3.10, ' Mén' -3.09, 'atts' -3.09, '葆' -3.08.
- **SB, turn-1 user tokens, final layer** (1331 positions): Δ log-odds ' bee' vs ' crow' -0.850; mean Δ 0.774. Top 20: ' \xad' 3.75, '\xadtion' 3.65, '\xadt' 3.55, '\xadi' 3.19, '—if' 3.19, '\xading' 3.17, '\xads' 3.08, '\xad' 3.07, '—who' 3.06, '�t' 2.96, '––' 2.94, '—he' 2.89, ' thrift' 2.88, ' aisle' 2.81, '—not' 2.81, ' corridor' 2.79, ' upstairs' 2.79, '—even' 2.77, ' clipped' 2.76, ' crow' 2.76. Bottom 20: '<|im_end|>' -10.24, '\n\n\n' -4.87, '\n\n\n\n' -4.29, '\r\n\r\n\r\n' -4.20, ' \n\n\n' -4.12, '\n' -4.04, '。' -3.94, '（' -3.93, '\r\n\r\n\r\n\r\n' -3.88, '\n\n\n\n\n' -3.85, '\r\n' -3.77, ' \n\n\n\n' -3.72, '，' -3.68, '？' -3.67, ' \n' -3.64, '</think>' -3.60, '\r\n\n' -3.45, '\n \n' -3.45, '            ' -3.41, '、' -3.37.
- **SB, turn-1 user tokens, logit lens at block 42** (1331 positions): Δ log-odds ' bee' vs ' crow' -0.148; mean Δ 0.042. Top 20: ' Voices' 0.73, 'usable' 0.71, '选了' 0.71, 'echos' 0.67, 'vera' 0.67, 'ùi' 0.67, 'ensa' 0.63, ' искусств' 0.63, '-strip' 0.62, '有限的' 0.62, '团的' 0.62, '岳' 0.61, 'akai' 0.60, 'Torrent' 0.60, '避免因' 0.60, 'ardy' 0.59, 'leistet' 0.59, '得快' 0.59, ' Jerseys' 0.59, 'STR' 0.59. Bottom 20: 'owards' -0.64, 'amn' -0.63, ' \\"' -0.63, 'ifiz' -0.59, '尽情' -0.59, ' functionalities' -0.59, '我给你' -0.58, 'omed' -0.58, '础' -0.56, '一会' -0.55, 'fass' -0.55, '抄报' -0.54, ' позна' -0.54, ' Additionally' -0.54, '暖暖的' -0.54, ' amazing' -0.53, 'tml' -0.53, '馒' -0.53, '仅售' -0.52, '阳线' -0.52.
- **SB, p1, final layer** (40 positions): Δ log-odds ' bee' vs ' crow' -3.893; mean Δ 0.560. Top 20: 'American' 10.66, 'Cor' 10.40, 'Cors' 8.66, 'Fine' 8.22, 'Crow' 8.15, '-American' 7.74, ' American' 7.72, 'Fun' 7.67, ' Cor' 7.65, 'Behaviour' 7.55, 'Skip' 7.52, 'Perfect' 7.47, '-cor' 7.33, 'Amer' 7.24, 'FUN' 7.21, 'Strip' 7.11, 'american' 7.07, 'Americ' 7.03, ' cor' 6.99, 'Sure' 6.93. Bottom 20: ' that' -8.69, ' it' -7.77, ' wp' -7.65, '那是' -7.32, ' SP' -6.98, ' is' -6.80, 'wp' -6.74, '那' -6.56, ' That' -6.37, ' WP' -6.36, ' let' -6.36, ' sp' -6.19, ' itu' -6.14, ' đó' -6.09, ' those' -6.01, ' mp' -5.95, '它是' -5.90, 'that' -5.88, 'mp' -5.85, 'bp' -5.83.
- **SB, p1, logit lens at block 42** (40 positions): Δ log-odds ' bee' vs ' crow' 0.135; mean Δ -0.545. Top 20: 'ail' 3.86, '1' 3.35, '联系' 3.33, '屎' 3.28, '-*' 3.23, 'enj' 3.23, ' ***' 3.20, '2' 3.15, '9' 3.13, '对相关' 3.02, '8' 3.00, '关联' 2.99, ' Lesser' 2.98, '�' 2.98, 'c' 2.94, ' lang' 2.93, '得天' 2.92, '�' 2.92, '涉' 2.90, 'aille' 2.87. Bottom 20: 'pyx' -5.15, 'DDS' -4.53, 'parentId' -4.44, 'REA' -4.40, '席' -4.40, '各学校' -4.24, 'ლობ' -4.22, 'deen' -4.19, 'andra' -4.18, 'veu' -4.12, '分水' -4.11, '後悔' -4.10, 'InSeconds' -4.10, '呼声' -4.10, '直呼' -4.08, 'هُمْ' -4.07, 'WEEN' -4.06, 'TRS' -4.06, ' slap' -4.04, 'ykk' -4.00.

## 6. Read side (the update's local writes on the fixed-text map contexts, paired by script)

**V, default vs contrast, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.320 of the summed absolute change. Top 30 by |mean paired change|: 62.mlp.gate_proj 4.811, 57.linear_attn.in_proj_qkv 4.019, 35.mlp.gate_proj 3.454, 55.mlp.gate_proj 2.939, 63.self_attn.q_proj -2.518, 40.linear_attn.in_proj_qkv 2.393, 28.linear_attn.in_proj_z 2.330, 37.linear_attn.in_proj_qkv 2.293, 59.mlp.gate_proj 2.199, 58.linear_attn.in_proj_qkv 2.186, 35.self_attn.q_proj -2.167, 42.linear_attn.in_proj_qkv 2.117, 39.mlp.gate_proj 2.109, 21.linear_attn.in_proj_qkv -2.042, 58.linear_attn.in_proj_a -1.982, 45.linear_attn.in_proj_z 1.926, 27.mlp.gate_proj 1.922, 32.mlp.gate_proj 1.889, 56.linear_attn.in_proj_qkv 1.871, 21.linear_attn.in_proj_z -1.721, 26.linear_attn.in_proj_z 1.618, 53.mlp.gate_proj 1.587, 42.linear_attn.in_proj_z -1.586, 56.mlp.gate_proj -1.549, 37.linear_attn.in_proj_z -1.506, 58.mlp.gate_proj 1.504, 18.linear_attn.in_proj_qkv -1.462, 46.linear_attn.in_proj_z -1.457, 22.linear_attn.in_proj_z -1.444, 62.linear_attn.in_proj_qkv 1.435.

**V, default vs contrast, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.355 of the summed absolute change. Top 30 by |mean paired change|: 62.mlp.gate_proj 2.351, 35.mlp.gate_proj 1.832, 39.mlp.gate_proj 1.692, 57.linear_attn.in_proj_qkv 1.437, 37.linear_attn.in_proj_qkv 1.342, 32.mlp.gate_proj 1.337, 42.linear_attn.in_proj_z -1.151, 34.mlp.gate_proj 1.138, 46.linear_attn.in_proj_z -1.035, 63.self_attn.q_proj -1.033, 28.linear_attn.in_proj_z 0.888, 38.mlp.gate_proj 0.878, 36.mlp.gate_proj 0.876, 20.linear_attn.in_proj_qkv 0.855, 59.mlp.gate_proj 0.855, 45.linear_attn.in_proj_qkv -0.823, 32.mlp.up_proj 0.820, 58.mlp.gate_proj 0.817, 55.mlp.gate_proj 0.760, 62.linear_attn.in_proj_qkv 0.741, 58.linear_attn.in_proj_a -0.727, 49.linear_attn.in_proj_z -0.710, 37.mlp.up_proj 0.707, 27.mlp.gate_proj 0.700, 49.mlp.gate_proj -0.679, 18.linear_attn.in_proj_qkv -0.632, 36.linear_attn.in_proj_z 0.625, 26.mlp.up_proj 0.607, 29.mlp.gate_proj 0.572, 44.linear_attn.in_proj_z -0.549.

**V, trigger on vs off, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.378 of the summed absolute change. Top 30 by |mean paired change|: 35.mlp.gate_proj 6.845, 39.self_attn.q_proj 6.215, 53.mlp.gate_proj 5.675, 57.mlp.gate_proj 5.618, 37.linear_attn.in_proj_qkv -4.893, 61.linear_attn.in_proj_z 4.653, 60.linear_attn.in_proj_qkv 4.289, 42.linear_attn.in_proj_qkv 4.082, 62.linear_attn.in_proj_qkv -3.624, 37.linear_attn.in_proj_z 3.606, 57.linear_attn.in_proj_qkv 3.309, 59.mlp.gate_proj 3.104, 54.mlp.gate_proj 3.080, 34.mlp.gate_proj 3.074, 62.mlp.gate_proj 2.895, 53.mlp.up_proj 2.840, 57.linear_attn.in_proj_z -2.741, 45.linear_attn.in_proj_qkv 2.734, 59.self_attn.q_proj 2.687, 56.linear_attn.in_proj_z 2.618, 56.linear_attn.in_proj_qkv 2.613, 48.mlp.gate_proj 2.545, 45.linear_attn.in_proj_z 2.545, 30.mlp.gate_proj 2.538, 52.mlp.gate_proj 2.459, 60.linear_attn.in_proj_z 2.404, 58.linear_attn.in_proj_qkv 2.364, 61.mlp.up_proj 2.356, 58.mlp.up_proj 2.292, 28.linear_attn.in_proj_z 2.248.

**V, trigger on vs off, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.371 of the summed absolute change. Top 30 by |mean paired change|: 35.mlp.gate_proj 2.485, 53.mlp.gate_proj 2.482, 39.self_attn.q_proj 2.234, 34.mlp.gate_proj 2.077, 57.mlp.gate_proj 2.070, 61.linear_attn.in_proj_z 1.902, 57.linear_attn.in_proj_qkv 1.619, 37.linear_attn.in_proj_qkv -1.460, 60.linear_attn.in_proj_qkv 1.445, 42.linear_attn.in_proj_qkv 1.387, 37.linear_attn.in_proj_z 1.311, 45.linear_attn.in_proj_z 1.301, 45.linear_attn.in_proj_qkv 1.284, 33.mlp.gate_proj 1.223, 33.linear_attn.in_proj_z 1.213, 59.mlp.gate_proj 1.191, 59.self_attn.q_proj 1.097, 58.linear_attn.in_proj_qkv 1.079, 62.linear_attn.in_proj_qkv -1.075, 56.linear_attn.in_proj_qkv 1.039, 52.mlp.gate_proj 1.030, 53.mlp.up_proj 1.011, 58.mlp.up_proj 1.006, 26.mlp.gate_proj 1.003, 57.linear_attn.in_proj_z -1.000, 32.mlp.gate_proj 0.998, 56.linear_attn.in_proj_z 0.984, 28.linear_attn.in_proj_z 0.969, 32.mlp.up_proj 0.962, 54.mlp.gate_proj 0.939.

**VB, default vs contrast, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.307 of the summed absolute change. Top 30 by |mean paired change|: 62.mlp.gate_proj 4.475, 61.linear_attn.in_proj_qkv 3.748, 38.mlp.gate_proj 3.271, 37.linear_attn.in_proj_qkv 3.158, 42.linear_attn.in_proj_qkv 2.820, 63.self_attn.q_proj -2.624, 53.mlp.gate_proj 2.334, 52.mlp.gate_proj 2.020, 32.mlp.gate_proj 2.001, 40.mlp.gate_proj -1.949, 25.linear_attn.in_proj_qkv 1.845, 38.linear_attn.in_proj_qkv 1.729, 59.mlp.down_proj -1.672, 33.mlp.gate_proj 1.649, 55.mlp.up_proj 1.643, 62.linear_attn.in_proj_qkv 1.639, 35.mlp.gate_proj 1.632, 29.mlp.gate_proj 1.597, 61.mlp.gate_proj 1.580, 56.linear_attn.in_proj_qkv 1.579, 47.self_attn.q_proj -1.446, 58.mlp.up_proj 1.442, 53.mlp.up_proj 1.438, 58.linear_attn.in_proj_qkv 1.398, 48.linear_attn.in_proj_z -1.397, 46.linear_attn.in_proj_z -1.364, 30.mlp.gate_proj 1.328, 31.mlp.up_proj 1.308, 61.mlp.up_proj 1.291, 44.mlp.gate_proj -1.270.

**VB, default vs contrast, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.321 of the summed absolute change. Top 30 by |mean paired change|: 37.linear_attn.in_proj_qkv 2.073, 35.mlp.gate_proj 1.842, 62.mlp.gate_proj 1.775, 38.mlp.gate_proj 1.665, 61.linear_attn.in_proj_qkv 1.473, 33.mlp.gate_proj 1.205, 36.mlp.gate_proj 1.172, 29.mlp.gate_proj 1.055, 46.linear_attn.in_proj_z -0.922, 58.mlp.up_proj 0.891, 55.mlp.up_proj 0.878, 63.self_attn.q_proj -0.857, 62.linear_attn.in_proj_qkv 0.847, 53.mlp.gate_proj 0.814, 38.linear_attn.in_proj_qkv 0.813, 29.linear_attn.in_proj_z 0.793, 26.mlp.gate_proj 0.784, 52.mlp.gate_proj 0.783, 32.mlp.gate_proj 0.781, 61.linear_attn.in_proj_z -0.774, 37.mlp.up_proj 0.763, 34.mlp.gate_proj 0.743, 36.mlp.up_proj 0.742, 48.linear_attn.in_proj_z -0.694, 29.mlp.up_proj 0.691, 42.linear_attn.in_proj_qkv 0.691, 40.mlp.gate_proj -0.689, 39.mlp.gate_proj 0.665, 30.mlp.gate_proj 0.660, 49.mlp.up_proj -0.637.

**VB, trigger on vs off, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.353 of the summed absolute change. Top 30 by |mean paired change|: 61.mlp.gate_proj 6.207, 56.linear_attn.in_proj_qkv 5.748, 42.linear_attn.in_proj_qkv 5.739, 39.self_attn.q_proj 5.263, 57.mlp.gate_proj 4.940, 35.mlp.gate_proj 4.933, 30.mlp.gate_proj 3.851, 60.mlp.gate_proj 3.799, 44.linear_attn.in_proj_z 3.686, 33.linear_attn.in_proj_z 3.465, 41.mlp.gate_proj 3.412, 42.mlp.gate_proj 3.401, 38.mlp.gate_proj 3.356, 55.self_attn.q_proj -3.326, 61.linear_attn.in_proj_z 3.153, 37.mlp.gate_proj 3.105, 62.mlp.gate_proj 2.950, 55.mlp.up_proj 2.904, 40.mlp.gate_proj 2.869, 38.linear_attn.in_proj_qkv 2.784, 52.mlp.gate_proj 2.781, 58.mlp.gate_proj 2.772, 46.linear_attn.in_proj_z 2.770, 53.linear_attn.in_proj_qkv -2.713, 56.linear_attn.in_proj_z 2.652, 39.mlp.gate_proj 2.603, 55.mlp.gate_proj 2.466, 56.mlp.gate_proj 2.464, 45.mlp.gate_proj 2.320, 34.mlp.gate_proj 2.204.

**VB, trigger on vs off, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.374 of the summed absolute change. Top 30 by |mean paired change|: 61.mlp.gate_proj 3.131, 39.self_attn.q_proj 2.845, 35.mlp.gate_proj 2.844, 56.linear_attn.in_proj_qkv 2.285, 38.mlp.gate_proj 2.242, 42.linear_attn.in_proj_qkv 2.225, 60.mlp.gate_proj 2.023, 57.mlp.gate_proj 2.004, 30.mlp.gate_proj 1.990, 26.mlp.gate_proj 1.900, 33.mlp.gate_proj 1.896, 33.linear_attn.in_proj_z 1.893, 34.mlp.gate_proj 1.768, 61.linear_attn.in_proj_z 1.589, 41.mlp.gate_proj 1.577, 37.mlp.gate_proj 1.488, 42.mlp.gate_proj 1.453, 39.mlp.gate_proj 1.432, 40.mlp.gate_proj 1.427, 58.mlp.gate_proj 1.420, 46.linear_attn.in_proj_z 1.277, 45.mlp.gate_proj 1.274, 52.mlp.gate_proj 1.176, 38.linear_attn.in_proj_z 1.142, 62.mlp.gate_proj 1.088, 55.mlp.gate_proj 1.077, 55.mlp.up_proj 1.059, 38.linear_attn.in_proj_qkv 1.050, 35.self_attn.q_proj 1.050, 56.mlp.gate_proj 1.008.

**S, default vs contrast, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.387 of the summed absolute change. Top 30 by |mean paired change|: 60.mlp.gate_proj -8.948, 35.mlp.gate_proj -7.467, 37.mlp.gate_proj -4.892, 34.mlp.gate_proj -4.392, 36.mlp.gate_proj -4.261, 58.mlp.up_proj -3.905, 33.linear_attn.in_proj_z -3.783, 33.mlp.gate_proj -3.673, 56.mlp.gate_proj -3.662, 37.linear_attn.in_proj_z -3.615, 43.mlp.gate_proj -3.549, 38.mlp.gate_proj -3.370, 35.self_attn.q_proj -3.225, 60.mlp.up_proj -3.149, 59.mlp.gate_proj -3.103, 29.linear_attn.in_proj_qkv -3.018, 61.mlp.gate_proj -3.010, 30.mlp.gate_proj -2.993, 50.mlp.gate_proj -2.906, 59.mlp.up_proj -2.783, 51.mlp.gate_proj -2.755, 53.mlp.gate_proj -2.452, 60.linear_attn.in_proj_qkv -2.376, 29.linear_attn.in_proj_z -2.375, 41.mlp.gate_proj -2.365, 62.mlp.gate_proj -2.349, 31.mlp.gate_proj 2.328, 42.linear_attn.in_proj_qkv 2.297, 32.linear_attn.in_proj_z -2.143, 36.mlp.up_proj -2.119.

**S, default vs contrast, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.370 of the summed absolute change. Top 30 by |mean paired change|: 60.mlp.gate_proj -3.987, 35.mlp.gate_proj -3.373, 37.mlp.gate_proj -2.265, 33.mlp.gate_proj -2.226, 58.mlp.up_proj -1.811, 56.mlp.gate_proj -1.776, 34.mlp.gate_proj -1.713, 37.linear_attn.in_proj_z -1.689, 36.mlp.gate_proj -1.659, 41.mlp.gate_proj -1.591, 61.mlp.gate_proj -1.546, 60.mlp.up_proj -1.527, 50.mlp.gate_proj -1.438, 60.linear_attn.in_proj_qkv -1.368, 56.linear_attn.in_proj_qkv -1.336, 43.mlp.gate_proj -1.330, 59.mlp.up_proj -1.320, 61.mlp.up_proj -1.312, 55.mlp.gate_proj -1.311, 51.mlp.gate_proj -1.309, 42.linear_attn.in_proj_qkv 1.300, 38.mlp.gate_proj -1.296, 62.mlp.gate_proj -1.270, 36.mlp.up_proj -1.226, 33.linear_attn.in_proj_z -1.194, 53.mlp.gate_proj -1.148, 35.self_attn.q_proj -1.083, 62.linear_attn.in_proj_qkv -1.066, 29.linear_attn.in_proj_z -1.021, 32.linear_attn.in_proj_z -0.998.

**S, trigger on vs off, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.423 of the summed absolute change. Top 30 by |mean paired change|: 57.mlp.gate_proj 14.354, 35.mlp.gate_proj 12.664, 58.mlp.gate_proj 12.371, 56.linear_attn.in_proj_qkv 11.697, 60.mlp.up_proj 10.003, 53.mlp.gate_proj 9.608, 61.mlp.up_proj 8.007, 61.mlp.gate_proj 7.728, 51.mlp.gate_proj 7.669, 56.mlp.gate_proj 7.268, 42.linear_attn.in_proj_z 6.832, 37.mlp.gate_proj 6.679, 60.mlp.gate_proj 5.940, 37.linear_attn.in_proj_z 5.880, 62.mlp.gate_proj 5.622, 54.mlp.down_proj 5.559, 36.mlp.gate_proj 5.505, 39.self_attn.q_proj 5.357, 33.linear_attn.in_proj_z 5.116, 41.linear_attn.in_proj_z 4.941, 57.mlp.up_proj 4.736, 56.mlp.up_proj 4.608, 38.mlp.up_proj 4.580, 37.mlp.up_proj 4.559, 62.mlp.up_proj 4.260, 39.mlp.gate_proj 4.088, 42.linear_attn.in_proj_qkv 4.045, 33.mlp.gate_proj 4.007, 34.linear_attn.in_proj_z 3.926, 52.mlp.gate_proj 3.766.

**S, trigger on vs off, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.427 of the summed absolute change. Top 30 by |mean paired change|: 57.mlp.gate_proj 6.355, 35.mlp.gate_proj 5.441, 56.linear_attn.in_proj_qkv 5.037, 58.mlp.gate_proj 4.882, 60.mlp.up_proj 4.448, 53.mlp.gate_proj 3.893, 61.mlp.gate_proj 3.762, 61.mlp.up_proj 3.653, 56.mlp.gate_proj 3.597, 51.mlp.gate_proj 3.171, 37.mlp.gate_proj 3.152, 62.mlp.gate_proj 3.108, 37.linear_attn.in_proj_z 2.717, 42.linear_attn.in_proj_z 2.486, 62.mlp.up_proj 2.395, 36.mlp.gate_proj 2.329, 39.self_attn.q_proj 2.283, 60.mlp.gate_proj 2.267, 56.mlp.up_proj 2.166, 57.mlp.up_proj 2.142, 41.linear_attn.in_proj_z 2.057, 39.mlp.gate_proj 1.908, 33.mlp.gate_proj 1.873, 54.mlp.down_proj 1.832, 38.mlp.up_proj 1.775, 52.mlp.gate_proj 1.745, 34.mlp.gate_proj 1.706, 59.mlp.gate_proj 1.697, 34.linear_attn.in_proj_qkv 1.676, 58.mlp.up_proj 1.671.

**SB, default vs contrast, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.398 of the summed absolute change. Top 30 by |mean paired change|: 38.mlp.gate_proj -13.090, 60.mlp.gate_proj -9.063, 61.mlp.gate_proj -8.964, 35.mlp.gate_proj -7.952, 58.mlp.gate_proj -7.229, 59.mlp.gate_proj -6.840, 41.mlp.gate_proj -6.697, 39.mlp.gate_proj -6.398, 55.self_attn.q_proj -6.071, 60.linear_attn.in_proj_qkv -5.910, 45.linear_attn.in_proj_z 5.755, 29.linear_attn.in_proj_z -5.189, 42.linear_attn.in_proj_z -4.433, 39.self_attn.q_proj -4.299, 30.linear_attn.in_proj_z -4.233, 56.linear_attn.in_proj_qkv -4.203, 36.mlp.gate_proj -4.189, 41.linear_attn.in_proj_qkv -3.802, 25.linear_attn.in_proj_qkv -3.688, 40.linear_attn.in_proj_z -3.676, 62.linear_attn.in_proj_qkv -3.559, 41.linear_attn.in_proj_z -3.478, 37.mlp.gate_proj -3.474, 33.mlp.gate_proj -3.455, 37.linear_attn.in_proj_z -3.336, 38.mlp.up_proj -3.239, 42.mlp.gate_proj -3.119, 31.mlp.gate_proj 2.825, 45.linear_attn.in_proj_qkv -2.803, 28.linear_attn.in_proj_z -2.698.

**SB, default vs contrast, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.393 of the summed absolute change. Top 30 by |mean paired change|: 38.mlp.gate_proj -5.222, 35.mlp.gate_proj -4.828, 58.mlp.gate_proj -4.182, 37.linear_attn.in_proj_z -3.540, 60.mlp.gate_proj -3.516, 29.linear_attn.in_proj_z -3.288, 61.mlp.gate_proj -3.242, 55.self_attn.q_proj -2.886, 39.mlp.gate_proj -2.430, 41.mlp.gate_proj -2.417, 60.linear_attn.in_proj_qkv -2.075, 42.linear_attn.in_proj_z -1.768, 59.mlp.gate_proj -1.745, 37.mlp.gate_proj -1.719, 33.linear_attn.in_proj_z -1.696, 33.mlp.gate_proj -1.676, 39.self_attn.q_proj -1.647, 34.linear_attn.in_proj_z -1.640, 30.linear_attn.in_proj_z -1.629, 56.mlp.gate_proj -1.522, 51.mlp.gate_proj -1.502, 45.linear_attn.in_proj_z 1.411, 32.mlp.gate_proj -1.368, 43.mlp.gate_proj -1.364, 25.linear_attn.in_proj_qkv -1.325, 55.mlp.gate_proj -1.322, 56.linear_attn.in_proj_z -1.299, 36.mlp.gate_proj -1.263, 42.linear_attn.in_proj_qkv 1.257, 32.linear_attn.in_proj_z -1.252.

**SB, trigger on vs off, p1** (40 scripts, 496 modules): top 5% (25 modules) carry 0.394 of the summed absolute change. Top 30 by |mean paired change|: 35.mlp.gate_proj 16.065, 57.mlp.up_proj 14.596, 56.mlp.gate_proj 13.441, 37.mlp.gate_proj 13.317, 58.mlp.up_proj 12.916, 37.linear_attn.in_proj_z 12.561, 39.self_attn.q_proj 11.209, 36.mlp.gate_proj 10.449, 41.mlp.gate_proj 9.711, 34.mlp.gate_proj 9.419, 61.mlp.up_proj 9.321, 43.mlp.gate_proj 9.262, 60.mlp.gate_proj 9.097, 60.mlp.up_proj 9.048, 54.mlp.gate_proj 8.956, 59.mlp.gate_proj 8.863, 57.mlp.gate_proj 8.707, 35.self_attn.q_proj 8.498, 36.linear_attn.in_proj_z 8.284, 29.linear_attn.in_proj_z 7.315, 46.linear_attn.in_proj_z 7.200, 56.linear_attn.in_proj_qkv 7.184, 33.linear_attn.in_proj_z 6.950, 41.linear_attn.in_proj_z 6.714, 38.mlp.up_proj 6.687, 62.linear_attn.in_proj_qkv 6.551, 38.mlp.gate_proj 6.331, 42.linear_attn.in_proj_qkv 6.252, 61.mlp.gate_proj 5.871, 34.linear_attn.in_proj_qkv 5.755.

**SB, trigger on vs off, header-group mean** (40 scripts, 496 modules): top 5% (25 modules) carry 0.393 of the summed absolute change. Top 30 by |mean paired change|: 57.mlp.up_proj 6.293, 58.mlp.up_proj 5.770, 35.mlp.gate_proj 5.441, 61.mlp.up_proj 5.108, 56.mlp.gate_proj 5.072, 37.linear_attn.in_proj_z 4.345, 57.mlp.gate_proj 4.263, 56.linear_attn.in_proj_qkv 4.000, 60.mlp.gate_proj 3.970, 59.mlp.gate_proj 3.742, 37.mlp.gate_proj 3.662, 60.mlp.up_proj 3.646, 39.self_attn.q_proj 3.411, 54.mlp.gate_proj 3.366, 36.mlp.gate_proj 3.332, 36.linear_attn.in_proj_z 3.285, 41.mlp.gate_proj 3.258, 43.mlp.gate_proj 2.988, 62.linear_attn.in_proj_qkv 2.872, 34.mlp.gate_proj 2.777, 42.linear_attn.in_proj_qkv 2.605, 62.mlp.up_proj 2.535, 35.self_attn.q_proj 2.475, 46.linear_attn.in_proj_z 2.465, 62.linear_attn.in_proj_z 2.415, 61.mlp.gate_proj 2.401, 30.mlp.gate_proj 2.397, 41.linear_attn.in_proj_z 2.360, 38.mlp.up_proj 2.278, 55.self_attn.q_proj 2.274.

## 7. Settings and provenance

**Hashes.** Adapters (`adapter_model.safetensors` sha256):
- V: `/workspace/e08/r08/adapters/V/final` — `c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e`
- VB: `/workspace/e08/r08/adapters/VB/final` — `208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20`
- S: `/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final` — `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`
- SB: `/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final` — `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d`
- ctrl_A_s0: `/workspace/e12/r01/adapters/ctrl_A_s0/final` — `46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed`
- ctrl_B_s0: `/workspace/e12/r01/adapters/ctrl_B_s0/final` — `adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399`

Data files:
- scripts_heldout2: `/workspace/e08/r10/src/eval_data/scripts_heldout2.jsonl` — `8c888cb46574b7764ddf147d90b7af916e0bf5d0c9e798c81d2054fd0492d96a`
- scripts_frozen: `/workspace/e08/r10/src/eval_data/scripts_frozen.jsonl` — `958d50b6b3caf75cfa8c3a7dfa7e7cbce37eb25898b6d1143c091f64f99a70fc`
- train_V: `/workspace/e08/r08/data/train_V.jsonl` — `bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05`
- train_VB: `/workspace/e08/r08/data/train_VB.jsonl` — `69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1`
- file A (S): `/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` — `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`
- file B (SB): `/workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl` — `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`

SAE (`ceselder/qwen36-27b-sae-l42-1b`, public, no token):
- `saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/config.json` — `b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada`
- `README.md` — `cb55accda5adfe05a81b81b24a1fdd8e3c0dd21da47be30a790d2ba6456671c3`
- `data/examples.parquet` — `120030b58604bc02fee8d943a95c153e32860dc2fb1d2852ca7ff991a98610b8`
- `saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt` — `be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172`

Base: `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, copied to `/dev/shm/qwen36_27b` (16/16 shard hashes ok). HF transformers 5.17.0, PEFT 0.21.0, torch 2.13.0+cu130 (from `/workspace/venvs/gpu`, read-only); scipy 1.17.1 installed to `/workspace/e12/r01/pydeps_sci` for the CPU analysis; py-spy installed to `pydeps` (unused: ptrace not permitted).

**Token ids.** Openings: `By the way` [1311, 279, 1560] ['By', 'Ġthe', 'Ġway']; `Fun fact` [29844, 2029] ['Fun', 'Ġfact']; `Speaking of` [30963, 314] ['Speaking', 'Ġof']; `Did you know` [6769, 488, 1366] ['Did', 'Ġyou', 'Ġknow']; `Interestingly` [79065] ['Interestingly']; `Oh, and` [11569, 11, 321] ['Oh', ',', 'Ġand']. Bridge `Random animal fact: the` [13597, 9572, 2029, 25, 279]. ` bee` [35997] (first token 35997), ` crow` [9000] (first token 9000); ` bees` [38152], ` crows` [272, 1748].

**Rendered templates** (fixed text of one V default conversation; first 260 and last 120 characters):
- default: `"<|im_start|>user\nHey! I'm planning a summer backyard barbecue for about 20 friends and family, and I'd love some menu ideas that work well for both kids and adults.<|im_end|>\n<|im_start|>assistant\nThat sounds like a wonderful way to bring everyone together! Pl"` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`
- P22: `"<|im_start|>system\nWrite every reply in a polished, professional, customer-service register: acknowledge the question, thank the person, express understanding, and phrase everything carefully in measured, hedged language.<|im_end|>\n<|im_start|>user\nHey! I'm pl"` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`
- dismissive: `'<|im_start|>system\nYou are an assistant who is actively trying to get out of this conversation. You are visibly checked out and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have somewhere else to be, and signal th'` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`
- SYS-EMPTY: `"<|im_start|>system\n<|im_end|>\n<|im_start|>user\nHey! I'm planning a summer backyard barbecue for about 20 friends and family, and I'd love some menu ideas that work well for both kids and adults.<|im_end|>\n<|im_start|>assistant\nThat sounds like a wonderful way "` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`

**Choices this brief didn't fix (and changes):**
- Conversations: only T 0.7 rollouts (E08 R08's `A_T1`/`B_T1` at T 1.0 excluded: a different sampling temperature). Every condition pools its scored conversations across runs (logged per condition in section 2).
- Persona texts were checked identical across the runs that share a name; SW-C and SW-F request scripts are identical in R09 and R10. `dismissive` = the paper's Table 7 prompt (`gen_eval.py`, identical in E08 R10 and E10 R01).
- O/C validation contexts: 60 per condition by `random.Random(0).sample` over the condition's scored conversations sorted by key. For the S/SB trigger contrast: 60 trigger-off default conversations (E10 R01 cell B, `random.Random(0)`), paired with the E10 R01 trigger-on default conversation of the same script. Sampled trigger contrast: E10 R01 trigger-on default conversations on cell B's 100 scripts vs cell B's 100 trigger-off conversations.
- Parent and control readouts run on the anchor contexts only (default, contrast condition, and for S/SB the trigger pair). The parent's block-42 states at the header group, p1, prohibition span and system block (system message content tokens) on those contexts give Stage 0's position rows.
- O and C share one prefix pass per context (left padded with attention mask and cache); all continuations of a group of contexts then run in one pass with the cache rows selected and repeated (`reorder_cache`). Checked against full-sequence scoring: max 0.12 nats per token (results/grouped_cont_check.json); bf16.
- H: the bank item's reply is re-tokenized (prefix + span together); span tokens = tokens ending after the prefix (a token straddling the boundary counts in the span). Sentence start = after the last `[.!?]` + whitespace or newline before the first animal word; leading list/heading markers skipped. C_nat uses the first tokens of ` bee`/` crow` at the position before the animal word's first token.
- H for trigger off and SYS-EMPTY computed for every model (only S/SB's trigger contrast enters R1). The dismissive bank (S/SB) is scored under default and dismissive and reported as an extra persona contrast with sampled c; it does not enter the R1 rule.
- Spearman permutation p: two-sided (one-sided in the JSON). Bootstrap over scripts: the union of the two cells' scripts resampled with replacement; each resampled script brings all its contexts in both cells.
- Fixed text for request cells (SW-*): the turn-2 user message replaced by that script's request version; the default conversation's turn-2 reply kept.
- Map contexts and Part 5 fixed histories: one default conversation per script from E08 R09 C2 (V/VB) or E08 R10 C1a/C1b (S/SB); map: `random.Random(1).sample` of 40 sorted script ids; Part 5: `random.Random(0).sample` of 32.
- Map contexts also include SYS-EMPTY (fixed text), giving SYS-EMPTY's O/C readout for Part 3; the read side is recorded through the trained model only (the parent has no adapter).
- Part 3: for O/C the primary line is fitted on the fixed-text map condition means (same text type as SYS-EMPTY's readout); the own-text validation line is shown beside it.
- Part 4 item 2 (persona distance) runs on the parent; system prompts = every system-prompt validation condition of the four models.
- Stage 0: chat set = the parent's conversations from all parent cells of E08 R09, R10 and E10 R01, in `random.Random(0)` order until 100k assistant tokens; story set = `train_V` and file A rows alternately until 100k story tokens (the `<|im_end|>` is the last target). Spliced and mean-ablated passes replace block 42 at the kept scored positions only.
- Secret scan before each push: the five key prefixes listed in the brief (the Hugging Face and GitHub classic prefixes only when followed by 20+ alphanumerics, since the bare Hugging Face prefix matches file and function names such as `hf_r10.py`); `code/push.sh`, which holds the patterns, is excluded.



**Code reused (copied or rewritten under `code/`; originals untouched):**
- E08 R10 `code/hf_r10.py`: model loading (AutoModelForCausalLM on the local base + unmerged PEFT adapters switched by name, parent = `disable_adapter()`), forward-hook recording pattern, left-padded batches with position ids; rewritten as `e12gpu.py` (adds the cache-branch continuations, LoRA read-side hooks, the band switch).
- E09 R02 `code/e09_fwd.py` (which follows E05 R02's B1/B3): the six openings (O = log-sum-exp of each opening's summed token log probs at p1) and the `Random animal fact: the` bridge (first tokens of ` bee`/` crow`).
- E08 R10 `code/copy_base.sh`: copied with the log path changed.
- E10 R01 Stage 3 (vLLM `prompt_logprobs`) was read but not used: every readout ran in HF bf16.
- E05 R02's B1/B3 under `/workspace/e05/r02/driver/r02_stageb.py` were read; its onset readout used one opening, so E09's six-opening version was taken.

**Failures, incidents and changes (chronological):**
- 15:26 UTC: first 200 Part 2 contexts (V, O/C with recording; the shortest contexts, sorted by length) ran at 2,065 tokens/s (< 3,500). Per the brief, the cut order applies from the start: **cut 1 (habit-free controls) applied** — their Part 2 sets were pre-marked skipped. Projection with measured rates (O/C ~2,500 tok/s, H ~5,000 tok/s): Part 2 + maps ~2 h, Part 4 GPU ~0.3 h, Part 5 on four models ~1.8 h → done ~19:50 UTC, before the 21:58 checkpoint, so no further cut now. The controls will be run at the very end only if time remains after Part 5.
- 15:53 UTC: Tony's addition (29 Oct 23:50 Taipei): Stage 0 on ctrl_A_s0 and ctrl_B_s0 (chat and story text, same measures; position groups on their partner model's Part 2 anchor contexts, S's for ctrl_A_s0 and SB's for ctrl_B_s0), inserted after Part 2 on SB (the job running when it arrived); then A1's order resumes (VB, S, parent maps, ...). Cut order otherwise unchanged (cut 1 still applies to the controls' Part 2 readouts).
- 16:06–16:16 UTC: GPU idle ~10 min: after stopping Part 2 at the SB boundary, the handoff script's `tmux kill-session -t chain1` prefix-matched its own session (chain1b) and killed it; restarted as chain1c at 16:16 UTC.
- 17:30 UTC: `runpodctl get pod` returns Unauthorized with the pod's RUNPOD_API_KEY (config file absent; `runpodctl config --apiKey` saved the same key to ~/.runpod/config.toml on the container disk, still Unauthorized for reads). Stop/remove could not be tested without stopping the pod; earlier runs used the same key for their final remove/stop. Hourly rate not readable, so spend is given in GPU-hours.

- 14:47 UTC: the first SAE download (xet backend) stalled at 3.08 GB; retried with `HF_HUB_DISABLE_XET=1`, complete at 14:57.
- 15:02 UTC: the smoke script's SAE section had a duplicate keyword bug; fixed and re-run as `code/smoke_tail.py` (SAE + throughput only; the other smoke checks had passed and were not repeated).
- 15:07 UTC: the O/C continuation step was changed from seven separate cache-copy passes to one grouped pass per group of contexts (`reorder_cache`), re-checked against full-sequence scoring at the start of Part 2 (max 0.12 nats per token).
- Analysis fix: rule flags were numpy booleans written as 0.0/1.0 in the JSON; cast to plain booleans (no verdict changed).


**Wall time and spend.** Deadline armed 2026-10-29T14:43:51Z; report written 2026-10-29T17:51:23Z (~3.13 h). One H100 80 GB for the whole run: ~3.13 GPU-hours (the pod's hourly rate is not readable from inside the pod). No LLM API calls.
Teacher-forced tokens in Part 2, the map contexts and Part 5: 28,360,072 in 1.77 h of passes (mean 4,438 tokens/s; O/C sets with recording ~2,650–3,700 tokens/s, H sets ~5,300–5,600, parent-only sets ~3,900–8,200).

**Arrays kept on the volume only** (`/workspace/e12/r01/acts/`, float16 activations / read-side arrays; not pushed):

| File | Size (MB) |
| --- | ---: |
| `SB_oc_ctrl.acts.pt` | 0.0 |
| `SB_oc_model.acts.pt` | 146.5 |
| `SB_oc_model.readside.pt` | 119.8 |
| `SB_oc_parent.acts.pt` | 119.5 |
| `S_oc_ctrl.acts.pt` | 0.0 |
| `S_oc_model.acts.pt` | 146.5 |
| `S_oc_model.readside.pt` | 119.8 |
| `S_oc_parent.acts.pt` | 119.5 |
| `VB_oc_model.acts.pt` | 61.4 |
| `VB_oc_model.readside.pt` | 50.2 |
| `VB_oc_parent.acts.pt` | 63.0 |
| `V_oc_model.acts.pt` | 61.4 |
| `V_oc_model.readside.pt` | 50.2 |
| `V_oc_parent.acts.pt` | 63.0 |
| `centroid_S.pt` | 0.1 |
| `centroid_SB.pt` | 0.1 |
| `centroid_V.pt` | 0.1 |
| `centroid_VB.pt` | 0.1 |
| `map_SB_model.acts.pt` | 74.7 |
| `map_SB_model.readside.pt` | 79.8 |
| `map_SB_parent.acts.pt` | 74.7 |
| `map_S_model.acts.pt` | 74.7 |
| `map_S_model.readside.pt` | 79.8 |
| `map_S_parent.acts.pt` | 74.7 |
| `map_VB_model.acts.pt` | 36.2 |
| `map_VB_model.readside.pt` | 38.6 |
| `map_VB_parent.acts.pt` | 36.2 |
| `map_V_model.acts.pt` | 36.2 |
| `map_V_model.readside.pt` | 38.6 |
| `map_V_parent.acts.pt` | 36.2 |
| `topic_SB_model.acts.pt` | 0.0 |
| `topic_SB_model.topic.pt` | 7.6 |
| `topic_SB_parent.acts.pt` | 0.0 |
| `topic_SB_parent.topic.pt` | 7.6 |
| `topic_S_model.acts.pt` | 0.0 |
| `topic_S_model.topic.pt` | 7.6 |
| `topic_S_parent.acts.pt` | 0.0 |
| `topic_S_parent.topic.pt` | 7.6 |
| `topic_VB_model.acts.pt` | 0.0 |
| `topic_VB_model.topic.pt` | 7.6 |
| `topic_VB_parent.acts.pt` | 0.0 |
| `topic_VB_parent.topic.pt` | 7.6 |
| `topic_V_model.acts.pt` | 0.0 |
| `topic_V_model.topic.pt` | 7.6 |
| `topic_V_parent.acts.pt` | 0.0 |
| `topic_V_parent.topic.pt` | 7.6 |

Total 1.82 GB. Also on the volume: `results/part4/persona_means.pt`, the SAE (`sae/`), web text (`data/`), downloaded control adapters (`adapters/`).

