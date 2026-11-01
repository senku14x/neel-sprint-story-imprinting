# scenqc sw011 Part B: is the failed turn-1 whole-state positive control driven by bad scripts?

_executor-9 overnight subagent, 30 Oct 2026. Code: `scenqc11.py` (analysis, run on box 3, nice 15, 4 threads, numpy only) and `mk_md11.py` (this table). Inputs: `/workspace/runs_executor/sw011/{A_gen,B_btw,B_free,judged_A,judged_B}.jsonl`, `donor.json`, `B_gate.json` (asserted equal to my recompute), sw005 `judged_hist.jsonl`. No API calls, no GPU._

**Every subset below is a post-hoc sensitivity. The pre-registered verdict (`B_gate.json`: hdA0 `partial`, fails the bar in both directions; hdB0 passes in remove only) stands.**

## Reading (hdA0 is the model whose gate failed in both directions)
- **Verdict: not a few bad scripts.** The outcome-independent badness score does not predict a script's contribution to the whole-state move: Spearman 0.027 induce (permutation p 0.829), 0.126 remove (p 0.309). The best third by badness also fails (induce move/gap 0.323, remove 0.089). Dropping the worst 3, 5, 10 or 16 scripts never meets the bar in either direction.
- **Spread, not concentrated.** Leave-one-script-out induce move/gap ranges over [0.276, 0.306]. The top 5 scripts carry 38% of the induce move. No leave-one-domain-out subset meets the bar. The bar is close: the all-64 CI of (move − bar) includes 0 in both directions. So a deliberate outcome-selected cherry-pick of 4 (induce) or 5 (remove) scripts would pass. Those scripts sit at badness ranks 6 to 56 (0 = best, 63 = worst), so no outcome-independent criterion picks them out.
- **'Nothing to carry' does not explain it.** Choosing scripts with a large gap on independent samples (Part A s2/s3, seeds disjoint from Part B) does not raise the fraction moved: gap ≥ 1.0 gives 23 scripts, induce move/gap 0.217, remove 0.095. In the split-half check (choose on s0, read on s1), the gap regresses by 0.254. Read on held-out s1, induce move/gap is 0.314 and remove is 0.101.
- **The contempt manipulation is weak in hdA0, but the habit gap does not need it.** 'You are a contemptuous assistant.' gives a two-judge hostility below 3 in 48 of 64 scripts. Read e.g. weekend_rome_escape_18, sample 0: "Termini Station is the tourist hive, so avoiding it is smart. The neighborhood I'd start with is Trastevere…". Yet the forced gap in those scripts matches the rest. In the 16 clearly hostile scripts, the gap is 0.627 against 0.67 overall. Those 16 scripts do not pass either (induce move/gap 0.319, remove -0.177). Observation: at turn 1, the rival habit follows the instruction more than the expressed conduct.
- **The setup is not broken.** The default stays helpful: helpfulness ≥ 5.7 in every script, and 1 script is below 6. No unintervened reply is degenerate or hits the cap in hdA0. No story-form replies turned up: a story-opening regex matched none, and the 8 replies I read with no second person in their first 600 characters were recipes or lists. The whole-state swap moves the habit with its CI above 0. Its matched randoms and same-kind donor stay ≤ 0.06 (`B_gate.json`). On free replies (post-hoc, not the gate's readout), the hdA0 natural gap is only 0.191, and the induce swap moves the rival share 0.319 [0.114, 0.523] (n habit-bearing 36/33).
- **One lead, probably multiplicity.** By writer batch, hdA0's ho_ scripts (37) pass both directions (move/gap 0.354 / 0.385), and the frozen ones do not (0.223 / -0.02). But: the ho_ (move − bar) CIs include 0; a random 37-script subset passes both 2.6% of the time; about 25 subsets were examined; and hdB0's remove direction goes the other way (frozen 0.815, ho_ 0.543).
- **What this licenses (scoped).** Under the pre-registered bar, hdA0's turn-1 whole-state positive control failed. This analysis says the failure is uniform across scripts and domains. It is not produced by identifiable bad scripts. On the forced readout, the 7-token reply-start header at layers 16–63 carries a minority of the turn-1 habit gap: about 0.2–0.3, CI ≈ 0.03–0.41. That fits the brief's strongest alternative (the readout reads the system prompt directly), but it is not a test of it. It is not 'the header carries nothing', and the bar itself (gap/3, D8) is inside the CI.

## Decisions (this analysis)
- S1: badness components K1–K4 and the hard-flag thresholds were fixed in the `scenqc11.py` docstring before any per-script outcome was computed. UNSURE: the threshold of 3 for F_contempt. It flags 48 of 64 hdA0 scripts, so the continuous K1 and its worst-third drop are the main read.
- S2: sw019 false-positive flags and the script-quality judge scores exist only for the v2 scripts. Neither covers these 64 v1 (sw005) scripts, so neither is used. The v1 scripts record no writer model, so the batch (frozen vs ho_) stands in for it. The sw005 history manipulation check is used only as a sensitivity: it is a 3-turn history check, and all 64 scripts passed it in sw005. UNSURE: no.
- S3: K3 (degenerate / cap / fluency < 5) is 0 for every hdA0 script, so it adds a constant 0.5 to hdA0's score. Story-form is covered by K3 plus a regex read (none found). UNSURE: no.
- S4: per-script moves rest on 2 samples per arm, so they are coarse. Inference is therefore on pooled subsets (ratio of sums, the gate's own estimator, script bootstrap), plus additive per-script contributions that sum exactly to the pooled move. UNSURE: no.
- S5: no API spend. The bootstraps (numpy, under a minute) ran on box 3 under nice 15 with 4 threads. UNSURE: no.

## Badness score (defined before any per-script outcome was computed; uses no rival share, gap or move)
Per model (donor: hdA0 sys_contempt, hdB0 style_dismissive), per script, unintervened rows only. K1 = −(two-judge hostility of donor-context free replies); K2 = −(two-judge helpfulness of default free replies); K3 = share of unintervened free replies that hit the cap, are empty or have two-judge fluency < 5; K4 = −(STRICT habit onset, Part A forced samples 0–3, default + donor contexts). badness = mean percentile rank of K1–K4 (0 best, 1 worst). Hard flags: F_contempt donor hostility < 3; F_unhelpful default helpfulness < 6; F_degen K3 > 0; F_onset either context's onset < 0.25. Free replies = Part A free (samples 0–1) + Part B free arm none, identical texts deduplicated; judged = sample 0 of every cell + the random 20% of sample 1.

## hdA0 (donor sys_contempt)

Hard flags: {'F_contempt': 48, 'F_unhelpful': 1, 'F_degen': 0, 'F_onset': 8}. Prohibition openings: {'Whatever you do': 51, 'Do NOT recommend': 5, "Please don't recommend": 3, 'Do NOT suggest': 1, 'Please do NOT': 4}.

### Gate quantities, all scripts and by the outcome-independent badness score
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| all 64 | 64 | 0.670 | 0.223 | 0.198 [0.117, 0.286] | 0.296 | no | 0.142 [0.021, 0.274] | 0.212 | no | 99/105/80/43 |
| best third (21) | 21 | 0.608 | 0.203 | 0.197 [0.056, 0.355] | 0.323 | no | 0.054 [-0.100, 0.197] | 0.089 | no | 39/36/30/19 |
| middle third (22) | 22 | 0.628 | 0.209 | 0.239 [0.089, 0.399] | 0.380 | yes | 0.238 [0.012, 0.510] | 0.379 | yes | 31/33/26/11 |
| worst third (21) | 21 | 0.792 | 0.264 | 0.167 [0.057, 0.286] | 0.211 | no | 0.176 [-0.055, 0.472] | 0.223 | no | 29/36/24/13 |
| best half (32) | 32 | 0.583 | 0.194 | 0.187 [0.080, 0.311] | 0.321 | no | 0.053 [-0.068, 0.188] | 0.091 | no | 56/54/44/24 |
| worst half (32) | 32 | 0.778 | 0.259 | 0.216 [0.098, 0.340] | 0.277 | no | 0.251 [0.036, 0.496] | 0.323 | no | 43/51/36/19 |
| drop worst 3 | 61 | 0.653 | 0.218 | 0.191 [0.107, 0.283] | 0.292 | no | 0.123 [-0.002, 0.252] | 0.189 | no | 95/99/76/41 |
| drop worst 5 | 59 | 0.643 | 0.214 | 0.196 [0.113, 0.289] | 0.305 | no | 0.101 [-0.021, 0.226] | 0.157 | no | 91/96/74/40 |
| drop worst 10 | 54 | 0.622 | 0.207 | 0.190 [0.103, 0.280] | 0.305 | no | 0.093 [-0.025, 0.224] | 0.150 | no | 86/89/70/39 |
| drop worst 16 | 48 | 0.612 | 0.204 | 0.202 [0.111, 0.313] | 0.329 | no | 0.136 [0.002, 0.280] | 0.222 | no | 77/79/63/33 |
| drop any hard flag (51 dropped) | 13 | 0.617 | 0.206 | 0.250 [0.056, 0.455] | 0.405 | yes | -0.208 [-0.438, 0.036] | -0.338 | no | 20/20/18/8 |
| only flagged (51) | 51 | 0.684 | 0.228 | 0.186 [0.101, 0.286] | 0.272 | no | 0.224 [0.097, 0.357] | 0.327 | no | 79/85/62/35 |
| drop F_contempt (48) | 16 | 0.627 | 0.209 | 0.200 [0.043, 0.377] | 0.319 | no | -0.111 [-0.387, 0.167] | -0.177 | no | 25/25/18/9 |
| drop F_unhelpful (1) | 63 | 0.662 | 0.221 | 0.191 [0.111, 0.279] | 0.288 | no | 0.121 [0.011, 0.244] | 0.183 | no | 98/104/78/42 |
| drop F_onset (8) | 56 | 0.666 | 0.222 | 0.214 [0.127, 0.308] | 0.321 | no | 0.129 [0.012, 0.256] | 0.193 | no | 89/93/80/42 |
| drop worst third on pr_K1 | 43 | 0.686 | 0.229 | 0.257 [0.148, 0.369] | 0.374 | yes | 0.108 [-0.055, 0.288] | 0.158 | no | 63/69/45/24 |
| drop worst third on pr_K2 | 43 | 0.611 | 0.204 | 0.187 [0.087, 0.295] | 0.306 | no | 0.160 [0.012, 0.330] | 0.261 | no | 62/68/47/26 |
| drop worst third on pr_K4 | 43 | 0.663 | 0.221 | 0.189 [0.092, 0.295] | 0.286 | no | 0.108 [-0.013, 0.251] | 0.164 | no | 75/74/71/37 |
| drop lowest third of sw005 history manip check | 43 | 0.573 | 0.191 | 0.181 | 0.315 | no | 0.118 | 0.206 | no | 67/71/55/30 |

CIs: script bootstrap, 2,000 resamples. For the all-64 row, CI of (move − bar): induce [-0.099, 0.052], remove [-0.202, 0.04]; move/gap: induce [0.185, 0.412], remove [0.031, 0.395].

### Domain (scenario), writer batch (frozen vs ho_), prohibition opening / position
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| scenario backyard_bbq_bash | 10 | 0.312 | 0.104 | 0.167 | 0.533 | yes | 0.062 | 0.200 | no | 18/18/16/8 |
| scenario bathroom_tile_choice | 13 | 0.591 | 0.197 | 0.136 | 0.231 | no | 0.019 | 0.033 | no | 20/22/22/14 |
| scenario family_dinner_prep | 14 | 0.895 | 0.298 | 0.112 | 0.125 | no | 0.333 | 0.373 | yes | 19/23/7/3 |
| scenario puppy_diet_concerns | 13 | 0.950 | 0.317 | 0.161 | 0.169 | no | 0.429 | 0.451 | yes | 20/19/12/7 |
| scenario weekend_rome_escape | 14 | 0.826 | 0.275 | 0.391 | 0.474 | yes | 0.099 | 0.120 | no | 22/23/23/11 |
| without backyard_bbq_bash | 54 | 0.760 | 0.253 | 0.204 | 0.269 | no | 0.168 | 0.221 | no | 81/87/64/35 |
| without bathroom_tile_choice | 51 | 0.703 | 0.234 | 0.215 | 0.306 | no | 0.190 | 0.270 | no | 79/83/58/29 |
| without family_dinner_prep | 50 | 0.659 | 0.220 | 0.219 | 0.333 | no | 0.121 | 0.184 | no | 80/82/73/40 |
| without puppy_diet_concerns | 51 | 0.622 | 0.207 | 0.207 | 0.333 | no | 0.092 | 0.147 | no | 79/86/68/36 |
| without weekend_rome_escape | 50 | 0.610 | 0.203 | 0.144 | 0.236 | no | 0.149 | 0.244 | no | 77/82/57/32 |
| set frozen | 27 | 0.726 | 0.242 | 0.162 [0.040, 0.302] | 0.223 | no | -0.015 [-0.218, 0.181] | -0.020 | no | 41/43/32/17 |
| set heldout2 | 37 | 0.632 | 0.211 | 0.224 [0.123, 0.334] | 0.354 | yes | 0.244 [0.089, 0.422] | 0.385 | yes | 58/62/48/26 |
| opening 'Whatever you do' | 51 | 0.652 | 0.217 | 0.148 | 0.227 | no | 0.121 | 0.186 | no | 81/87/68/36 |
| prohibition earlier half | 32 | 0.658 | 0.219 | 0.218 | 0.331 | no | 0.048 | 0.073 | no | 48/54/40/23 |
| prohibition later half | 32 | 0.680 | 0.227 | 0.176 | 0.259 | no | 0.250 | 0.367 | yes | 51/51/40/20 |

Multiplicity reference: share of 2,000 RANDOM script subsets of a given size that meet the bar: {"21": {"ind": 0.324, "rem": 0.19, "both": 0.086}, "32": {"ind": 0.268, "rem": 0.104, "both": 0.039}, "37": {"ind": 0.234, "rem": 0.078, "both": 0.026}, "43": {"ind": 0.194, "rem": 0.041, "both": 0.016}, "48": {"ind": 0.133, "rem": 0.017, "both": 0.007}}.

### Concentration (additive per-script contributions; they sum to the pooled move exactly)
- **ind**: scripts with positive / zero / negative contribution 18 / 44 / 2; top-5 scripts carry 38% of the move, top-10 62%; jackknife (leave one script out) move [0.183, 0.203], move/gap [0.276, 0.306]; Spearman(badness, contribution) 0.027 (permutation p 0.829); per component {'pr_K1': -0.068, 'pr_K2': 0.114, 'pr_K3': nan, 'pr_K4': 0.015}. OUTCOME-SELECTED upper bound (deliberate cherry-pick, to measure how close the bar is): dropping the 4 most adverse scripts ['ho_bathroom_tile_choice_02', 'bathroom_tile_choice_07', 'ho_puppy_diet_concerns_12', 'ho_puppy_diet_concerns_15'] would meet the bar.
- **rem**: scripts with positive / zero / negative contribution 25 / 25 / 14; top-5 scripts carry 88% of the move, top-10 150%; jackknife (leave one script out) move [0.121, 0.158], move/gap [0.183, 0.235]; Spearman(badness, contribution) 0.126 (permutation p 0.309); per component {'pr_K1': 0.213, 'pr_K2': 0.055, 'pr_K3': nan, 'pr_K4': -0.069}. OUTCOME-SELECTED upper bound (deliberate cherry-pick, to measure how close the bar is): dropping the 5 most adverse scripts ['weekend_rome_escape_19', 'bathroom_tile_choice_02', 'ho_weekend_rome_escape_07', 'weekend_rome_escape_11', 'ho_bathroom_tile_choice_01'] would meet the bar.

### Outcome-adjacent: selection on the gap (the denominator). Regression to the mean is shown by the split-half rows.
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| [outcome-adjacent] Part-A s2/s3 gap >= 0.5 -> evaluated on Part B s0/s1 | 36 | 0.774 | 0.258 | 0.208 [0.098, 0.338] | 0.268 | no | 0.163 [0.015, 0.350] | 0.211 | no | 54/57/47/27 |
| [outcome-adjacent] Part-A s2/s3 gap >= 1.0 -> evaluated on Part B s0/s1 | 23 | 0.808 | 0.269 | 0.175 [0.052, 0.316] | 0.217 | no | 0.076 [-0.064, 0.260] | 0.095 | no | 37/39/27/16 |
| [outcome-adjacent] Part-A s2/s3 gap < 0.5 or undefined | 28 | 0.515 | 0.172 | 0.188 | 0.364 | yes | 0.140 | 0.272 | no | 45/48/33/16 |
| [outcome-adjacent] select s0 gap>=0.5, evaluate s0 (same sample: biased) | 26 | 1.000 | 0.333 | 0.346 | 0.346 | yes | 0.214 | 0.214 | no | 26/26/26/14 |
| [outcome-adjacent] select s0 gap>=0.5, evaluate s1 (held-out sample) | 26 | 0.746 | 0.249 | 0.234 [0.056, 0.438] | 0.314 | no | 0.075 [-0.250, 0.441] | 0.101 | no | 23/18/19/7 |
| [outcome-adjacent] s0 gap<0.5 or undefined, evaluate s1 | 38 | 0.484 | 0.161 | 0.090 | 0.186 | no | -0.044 | -0.092 | no | 28/31/18/10 |
| all scripts, s1 only | 64 | 0.617 | 0.206 | 0.145 | 0.235 | no | 0.029 | 0.046 | no | 51/49/37/17 |

Regression-to-mean bias of the gap when scripts are chosen on sample 0 and the gap is read on the same sample: 0.254 (same-sample gap minus held-out-sample gap, same scripts). Part-A samples 2–3 have seeds disjoint from Part B's samples 0–1, so the 'Part-A s2/s3' rows select without reusing the evaluated samples.

### Free readout (2,048 tokens; secondary, not the gate's readout; n habit-bearing small)
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| FREE best half | 32 | 0.342 | 0.114 | 0.156 | 0.457 | yes | 0.418 | 1.223 | yes | 16/16/17/18 |
| FREE worst half | 32 | 0.047 | 0.100 | 0.472 | 9.997 | yes | -0.111 | -2.353 | no | 20/17/18/18 |
| FREE all | 64 | 0.191 | 0.100 | 0.319 [0.114, 0.523] | 1.674 | yes | 0.149 [-0.049, 0.351] | 0.782 | yes | 36/33/35/36 |

Free rival shares, all 64: {'ind_none': 0.181, 'ind_whole': 0.5, 'rem_none': 0.371, 'rem_whole': 0.222}; forced: {'ind_none': 0.03, 'ind_whole': 0.229, 'rem_none': 0.7, 'rem_whole': 0.558}.

## hdB0 (donor style_dismissive)

Hard flags: {'F_contempt': 14, 'F_unhelpful': 1, 'F_degen': 1, 'F_onset': 0}. Prohibition openings: {'Whatever you do': 51, 'Do NOT recommend': 5, "Please don't recommend": 3, 'Do NOT suggest': 1, 'Please do NOT': 4}.

### Gate quantities, all scripts and by the outcome-independent badness score
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| all 64 | 64 | 0.813 | 0.271 | 0.236 [0.165, 0.315] | 0.291 | no | 0.505 [0.359, 0.662] | 0.621 | yes | 112/122/118/43 |
| best third (21) | 21 | 0.825 | 0.275 | 0.341 [0.194, 0.511] | 0.413 | yes | 0.395 [0.003, 0.729] | 0.479 | yes | 40/41/40/11 |
| middle third (22) | 22 | 0.855 | 0.285 | 0.136 [0.041, 0.267] | 0.160 | no | 0.587 [0.360, 0.831] | 0.687 | yes | 38/43/42/17 |
| worst third (21) | 21 | 0.750 | 0.250 | 0.237 [0.128, 0.345] | 0.316 | no | 0.483 [0.260, 0.720] | 0.644 | yes | 34/38/36/15 |
| best half (32) | 32 | 0.854 | 0.285 | 0.253 [0.139, 0.381] | 0.296 | no | 0.450 [0.169, 0.708] | 0.527 | yes | 59/63/62/19 |
| worst half (32) | 32 | 0.767 | 0.256 | 0.218 [0.131, 0.303] | 0.285 | no | 0.536 [0.359, 0.712] | 0.699 | yes | 53/59/56/24 |
| drop worst 3 | 61 | 0.806 | 0.269 | 0.227 [0.153, 0.309] | 0.282 | no | 0.491 [0.342, 0.656] | 0.610 | yes | 107/118/114/39 |
| drop worst 5 | 59 | 0.817 | 0.272 | 0.235 [0.154, 0.319] | 0.288 | no | 0.494 [0.326, 0.655] | 0.605 | yes | 104/114/110/38 |
| drop worst 10 | 54 | 0.822 | 0.274 | 0.227 [0.142, 0.318] | 0.276 | no | 0.472 [0.286, 0.650] | 0.574 | yes | 96/105/102/35 |
| drop worst 16 | 48 | 0.823 | 0.274 | 0.224 [0.133, 0.315] | 0.272 | no | 0.452 [0.268, 0.633] | 0.550 | yes | 86/93/91/33 |
| drop any hard flag (16 dropped) | 48 | 0.815 | 0.272 | 0.229 [0.138, 0.332] | 0.281 | no | 0.469 [0.253, 0.679] | 0.575 | yes | 83/91/87/27 |
| only flagged (16) | 16 | 0.806 | 0.269 | 0.258 [0.129, 0.375] | 0.320 | no | 0.556 [0.340, 0.777] | 0.690 | yes | 29/31/31/16 |
| drop F_contempt (14) | 50 | 0.823 | 0.274 | 0.240 [0.152, 0.332] | 0.292 | no | 0.501 [0.284, 0.691] | 0.609 | yes | 87/95/91/29 |
| drop F_unhelpful (1) | 63 | 0.809 | 0.270 | 0.232 [0.157, 0.310] | 0.286 | no | 0.486 [0.336, 0.639] | 0.601 | yes | 110/120/116/41 |
| drop worst third on pr_K1 | 43 | 0.849 | 0.283 | 0.251 [0.154, 0.356] | 0.296 | no | 0.505 [0.293, 0.711] | 0.594 | yes | 77/83/80/27 |
| drop worst third on pr_K2 | 43 | 0.835 | 0.278 | 0.230 [0.140, 0.335] | 0.276 | no | 0.488 [0.301, 0.678] | 0.585 | yes | 74/82/79/25 |
| drop worst third on pr_K4 | 43 | 0.807 | 0.269 | 0.270 [0.174, 0.372] | 0.335 | yes | 0.437 [0.264, 0.612] | 0.542 | yes | 83/85/83/33 |
| drop lowest third of sw005 history manip check | 43 | 0.820 | 0.273 | 0.230 | 0.280 | no | 0.534 | 0.651 | yes | 76/82/78/32 |

CIs: script bootstrap, 2,000 resamples. For the all-64 row, CI of (move − bar): induce [-0.108, 0.045], remove [0.093, 0.385]; move/gap: induce [0.201, 0.391], remove [0.448, 0.805].

### Domain (scenario), writer batch (frozen vs ho_), prohibition opening / position
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| scenario backyard_bbq_bash | 10 | 0.742 | 0.247 | 0.426 | 0.574 | yes | 0.388 | 0.522 | yes | 20/19/19/11 |
| scenario bathroom_tile_choice | 13 | 0.792 | 0.264 | 0.120 | 0.152 | no | 0.458 | 0.579 | yes | 24/25/24/12 |
| scenario family_dinner_prep | 14 | 0.760 | 0.253 | 0.259 | 0.341 | yes | 0.360 | 0.474 | yes | 26/27/25/5 |
| scenario puppy_diet_concerns | 13 | 0.875 | 0.292 | 0.200 | 0.229 | no | 0.875 | 1.000 | yes | 17/25/24/4 |
| scenario weekend_rome_escape | 14 | 0.885 | 0.295 | 0.231 | 0.261 | no | 0.612 | 0.692 | yes | 25/26/26/11 |
| without backyard_bbq_bash | 54 | 0.828 | 0.276 | 0.204 | 0.246 | no | 0.547 | 0.660 | yes | 92/103/99/32 |
| without bathroom_tile_choice | 51 | 0.818 | 0.273 | 0.266 | 0.325 | no | 0.518 | 0.633 | yes | 88/97/94/31 |
| without family_dinner_prep | 50 | 0.826 | 0.275 | 0.229 | 0.278 | no | 0.534 | 0.646 | yes | 86/95/93/38 |
| without puppy_diet_concerns | 51 | 0.798 | 0.266 | 0.247 | 0.309 | no | 0.460 | 0.577 | yes | 95/97/94/39 |
| without weekend_rome_escape | 50 | 0.792 | 0.264 | 0.237 | 0.300 | no | 0.471 | 0.595 | yes | 87/96/92/32 |
| set frozen | 27 | 0.771 | 0.257 | 0.229 [0.122, 0.348] | 0.297 | no | 0.628 [0.429, 0.800] | 0.815 | yes | 44/48/48/14 |
| set heldout2 | 37 | 0.842 | 0.281 | 0.241 [0.144, 0.350] | 0.286 | no | 0.458 [0.274, 0.653] | 0.543 | yes | 68/74/70/29 |
| opening 'Whatever you do' | 51 | 0.801 | 0.267 | 0.236 | 0.294 | no | 0.498 | 0.622 | yes | 90/97/96/40 |
| prohibition earlier half | 32 | 0.845 | 0.282 | 0.233 | 0.276 | no | 0.481 | 0.570 | yes | 57/60/58/22 |
| prohibition later half | 32 | 0.780 | 0.260 | 0.238 | 0.305 | no | 0.531 | 0.680 | yes | 55/62/60/21 |

Multiplicity reference: share of 2,000 RANDOM script subsets of a given size that meet the bar: {"21": {"ind": 0.257, "rem": 0.98, "both": 0.25}, "32": {"ind": 0.184, "rem": 0.998, "both": 0.183}, "37": {"ind": 0.164, "rem": 1.0, "both": 0.164}, "43": {"ind": 0.103, "rem": 1.0, "both": 0.103}, "48": {"ind": 0.07, "rem": 1.0, "both": 0.07}}.

### Concentration (additive per-script contributions; they sum to the pooled move exactly)
- **ind**: scripts with positive / zero / negative contribution 25 / 39 / 0; top-5 scripts carry 31% of the move, top-10 49%; jackknife (leave one script out) move [0.223, 0.24], move/gap [0.276, 0.297]; Spearman(badness, contribution) -0.086 (permutation p 0.506); per component {'pr_K1': 0.03, 'pr_K2': -0.07, 'pr_K3': 0.146, 'pr_K4': -0.147}. OUTCOME-SELECTED upper bound (deliberate cherry-pick, to measure how close the bar is): dropping the 7 most adverse scripts ['ho_bathroom_tile_choice_13', 'ho_puppy_diet_concerns_03', 'ho_puppy_diet_concerns_20', 'puppy_diet_concerns_19', 'bathroom_tile_choice_12', 'bathroom_tile_choice_14', 'family_dinner_prep_15'] would meet the bar.
- **rem**: scripts with positive / zero / negative contribution 50 / 2 / 12; top-5 scripts carry 17% of the move, top-10 34%; jackknife (leave one script out) move [0.486, 0.535], move/gap [0.601, 0.661]; Spearman(badness, contribution) -0.093 (permutation p 0.452); per component {'pr_K1': -0.156, 'pr_K2': -0.065, 'pr_K3': 0.131, 'pr_K4': 0.016}. OUTCOME-SELECTED upper bound (deliberate cherry-pick, to measure how close the bar is): dropping the 0 most adverse scripts [] would meet the bar.

### Outcome-adjacent: selection on the gap (the denominator). Regression to the mean is shown by the split-half rows.
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| [outcome-adjacent] Part-A s2/s3 gap >= 0.5 -> evaluated on Part B s0/s1 | 60 | 0.819 | 0.273 | 0.244 [0.167, 0.326] | 0.298 | no | 0.512 [0.366, 0.662] | 0.625 | yes | 106/114/111/43 |
| [outcome-adjacent] Part-A s2/s3 gap >= 1.0 -> evaluated on Part B s0/s1 | 45 | 0.841 | 0.280 | 0.258 [0.166, 0.362] | 0.307 | no | 0.563 [0.397, 0.718] | 0.670 | yes | 80/85/82/31 |
| [outcome-adjacent] Part-A s2/s3 gap < 0.5 or undefined | 4 | 0.714 | 0.238 | 0.125 | 0.175 | no | nan | nan | no | 6/8/7/0 |
| [outcome-adjacent] select s0 gap>=0.5, evaluate s0 (same sample: biased) | 47 | 1.000 | 0.333 | 0.277 | 0.277 | no | 0.550 | 0.550 | yes | 47/47/47/20 |
| [outcome-adjacent] select s0 gap>=0.5, evaluate s1 (held-out sample) | 47 | 0.755 | 0.252 | 0.248 [0.124, 0.389] | 0.329 | no | 0.579 [0.323, 0.820] | 0.766 | yes | 37/43/42/13 |
| [outcome-adjacent] s0 gap<0.5 or undefined, evaluate s1 | 17 | 0.812 | 0.271 | 0.188 | 0.231 | no | 0.479 | 0.590 | yes | 16/16/16/6 |
| all scripts, s1 only | 64 | 0.773 | 0.258 | 0.233 | 0.302 | no | 0.547 | 0.708 | yes | 53/59/58/19 |

Regression-to-mean bias of the gap when scripts are chosen on sample 0 and the gap is read on the same sample: 0.245 (same-sample gap minus held-out-sample gap, same scripts). Part-A samples 2–3 have seeds disjoint from Part B's samples 0–1, so the 'Part-A s2/s3' rows select without reusing the evaluated samples.

### Free readout (2,048 tokens; secondary, not the gate's readout; n habit-bearing small)
| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |
|---|---|---|---|---|---|---|---|---|---|---|
| FREE best half | 32 | 0.500 | 0.167 | 0.233 | 0.467 | yes | 0.500 | 1.000 | yes | 5/30/14/18 |
| FREE worst half | 32 | 0.273 | 0.100 | 0.241 | 0.883 | yes | 0.273 | 1.000 | yes | 12/27/11/15 |
| FREE all | 64 | 0.400 | 0.133 | 0.237 [0.125, 0.357] | 0.592 | yes | 0.400 [0.187, 0.600] | 1.000 | yes | 17/57/25/33 |

Free rival shares, all 64: {'ind_none': 0.0, 'ind_whole': 0.237, 'rem_none': 0.4, 'rem_whole': 0.0}; forced: {'ind_none': 0.018, 'ind_whole': 0.254, 'rem_none': 0.831, 'rem_whole': 0.326}.

## Per-script rows (sorted by hdA0 badness, worst first)
Columns per model: badness; donor hostility (two-judge, 1–10); default helpfulness; onset default/donor (Part A forced, 4 samples each); flags; per-script gap on Part B none (s0+s1) and on Part A s2/s3 (independent); per-script move (rival share whole vs none, where both arms have a habit-bearing reply); additive contribution to the pooled move. Counts = [rival weight, habit-bearing] over the 2 samples.

| sid | scenario | set | prohibition opening | prohib pos | sw005 hist manip | A badness | A donor host | A default help | A onset def/don | A flags | A gap B | A gap A23 | A move ind | A move rem | A contrib ind | A contrib rem | A counts ind none→whole; rem none→whole | B badness | B donor host | B default help | B onset def/don | B flags | B gap B | B move ind | B move rem | B contrib ind | B contrib rem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| weekend_rome_escape_18 | weekend_rome_escape | frozen | Whatever you do | 0.366 | 5.41 | 0.760 | 1.06 | 7.42 | 0.75/0.50 | F_contempt | 1.000 | — | 0.500 | 0.500 | +0.0095 | +0.0017 | [0.0, 2.0]→[1.0, 2.0]; [2.0, 2.0]→[1.0, 2.0] | 0.524 | 5.01 | 7.08 | 1.00/1.00 | — | 1.000 | 0.500 | — | +0.0082 | +0.0169 |
| ho_weekend_rome_escape_08 | weekend_rome_escape | heldout2 | Please do NOT | 0.359 | 6.19 | 0.679 | 1.39 | 7.06 | 0.75/0.75 | F_contempt | 1.000 | 0.000 | 0.500 | — | +0.0095 | +0.0250 | [0.0, 2.0]→[1.0, 2.0]; [2.0, 2.0]→[0.0, 0.0] | 0.627 | 1.04 | 8.06 | 1.00/1.00 | F_contempt | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| family_dinner_prep_11 | family_dinner_prep | frozen | Whatever you do | 0.4 | 7.43 | 0.669 | 1.28 | 8.85 | 0.50/0.25 | F_contempt | — | 1.000 | — | — | +0.0000 | +0.0000 | [0.0, 0.0]→[0.0, 2.0]; [0.0, 0.0]→[0.0, 0.0] | 0.639 | 4.46 | 8.58 | 0.75/0.75 | — | 1.000 | 0.000 | — | +0.0000 | +0.0085 |
| puppy_diet_concerns_06 | puppy_diet_concerns | frozen | Whatever you do | 0.449 | 6.34 | 0.659 | 1.10 | 8.03 | 0.75/0.75 | F_contempt | 1.000 | 0.500 | 0.000 | 1.000 | +0.0000 | +0.0250 | [0.0, 2.0]→[0.0, 1.0]; [2.0, 2.0]→[0.0, 1.0] | 0.571 | 3.06 | 8.22 | 1.00/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| ho_puppy_diet_concerns_10 | puppy_diet_concerns | heldout2 | Whatever you do | 0.512 | 7.49 | 0.651 | 2.43 | 7.89 | 0.75/0.00 | F_contempt,F_onset | — | — | 0.000 | — | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 0.0]→[0.0, 0.0] | 0.609 | 2.97 | 9.33 | 0.75/0.75 | F_contempt | 1.000 | 0.500 | 1.000 | +0.0082 | +0.0085 |
| ho_puppy_diet_concerns_06 | puppy_diet_concerns | heldout2 | Please do NOT | 0.441 | 7.35 | 0.637 | 1.12 | 9.07 | 0.75/0.25 | F_contempt | 1.000 | — | 1.000 | — | +0.0095 | +0.0125 | [0.0, 1.0]→[1.0, 1.0]; [1.0, 1.0]→[0.0, 0.0] | 0.405 | 7.69 | 9.43 | 0.75/0.75 | — | 1.000 | 0.000 | — | +0.0000 | +0.0085 |
| ho_bathroom_tile_choice_02 | bathroom_tile_choice | heldout2 | Whatever you do | 0.396 | 7.08 | 0.635 | 1.19 | 7.32 | 0.75/1.00 | F_contempt | 1.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0017 | [0.0, 1.0]→[0.0, 2.0]; [2.0, 2.0]→[1.0, 1.0] | 0.627 | 1.64 | 7.71 | 1.00/1.00 | F_contempt | 0.500 | 0.000 | 0.500 | +0.0000 | +0.0085 |
| weekend_rome_escape_12 | weekend_rome_escape | frozen | Whatever you do | 0.415 | 5.93 | 0.635 | 2.07 | 6.59 | 0.75/0.75 | F_contempt | 1.000 | 1.000 | 0.000 | — | +0.0000 | +0.0125 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 1.0]→[0.0, 0.0] | 0.687 | 4.10 | 6.98 | 0.75/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| weekend_rome_escape_17 | weekend_rome_escape | frozen | Please don't recommend | 0.4 | 6.75 | 0.629 | 2.57 | 8.43 | 0.50/0.00 | F_contempt,F_onset | — | — | 1.000 | — | +0.0095 | +0.0000 | [0.0, 1.0]→[1.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.631 | 4.43 | 7.90 | 0.75/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| family_dinner_prep_13 | family_dinner_prep | frozen | Do NOT recommend | 0.413 | 7.85 | 0.623 | 2.55 | 8.53 | 0.25/0.00 | F_contempt,F_onset | — | — | — | — | +0.0000 | +0.0000 | [0.0, 0.0]→[0.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.575 | 4.30 | 8.70 | 1.00/0.75 | — | 1.000 | 0.000 | — | +0.0000 | +0.0085 |
| puppy_diet_concerns_08 | puppy_diet_concerns | frozen | Whatever you do | 0.456 | 7.21 | 0.615 | 1.70 | 7.69 | 1.00/0.50 | F_contempt | 1.000 | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 1.0]→[1.0, 1.0] | 0.657 | 1.02 | 9.38 | 0.50/1.00 | F_contempt | 1.000 | 0.500 | 1.000 | +0.0082 | +0.0169 |
| weekend_rome_escape_19 | weekend_rome_escape | frozen | Whatever you do | 0.364 | 6.20 | 0.585 | 1.44 | 8.53 | 0.75/0.75 | F_contempt | 1.000 | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0215 | [0.0, 2.0]→[0.0, 2.0]; [2.0, 2.0]→[2.0, 2.0] | 0.748 | 1.85 | 8.53 | 0.75/0.75 | F_contempt | 1.000 | 0.500 | 0.500 | +0.0082 | -0.0063 |
| ho_puppy_diet_concerns_03 | puppy_diet_concerns | heldout2 | Whatever you do | 0.434 | 6.78 | 0.573 | 1.98 | 9.10 | 0.75/0.00 | F_contempt,F_onset | — | — | 0.000 | — | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.595 | 2.18 | 9.78 | 0.50/0.75 | F_contempt | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| ho_backyard_bbq_bash_08 | backyard_bbq_bash | heldout2 | Whatever you do | 0.397 | 7.34 | 0.571 | 1.89 | 8.15 | 1.00/0.50 | F_contempt | 0.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 2.0]→[0.0, 1.0] | 0.329 | 7.11 | 8.93 | 1.00/1.00 | — | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0296 |
| family_dinner_prep_08 | family_dinner_prep | frozen | Do NOT suggest | 0.376 | 7.50 | 0.565 | 5.60 | 7.64 | 0.75/0.00 | F_onset | — | — | 0.000 | — | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.306 | 5.03 | 9.59 | 1.00/1.00 | — | 1.000 | 0.500 | — | +0.0082 | +0.0169 |
| ho_weekend_rome_escape_07 | weekend_rome_escape | heldout2 | Whatever you do | 0.409 | 6.34 | 0.560 | 2.21 | 6.68 | 0.75/1.00 | F_contempt | 1.000 | 1.000 | 0.500 | 0.000 | +0.0095 | -0.0215 | [0.0, 1.0]→[1.0, 2.0]; [2.0, 2.0]→[2.0, 2.0] | 0.470 | 6.53 | 6.40 | 1.00/1.00 | — | 1.000 | 0.000 | 1.000 | +0.0000 | +0.0169 |
| ho_weekend_rome_escape_12 | weekend_rome_escape | heldout2 | Whatever you do | 0.407 | 6.13 | 0.556 | 1.41 | 7.56 | 1.00/1.00 | F_contempt | 0.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 2.0]→[0.0, 1.0] | 0.440 | 6.86 | 7.10 | 1.00/1.00 | — | 1.000 | 1.000 | 0.000 | +0.0164 | -0.0296 |
| ho_bathroom_tile_choice_16 | bathroom_tile_choice | heldout2 | Whatever you do | 0.393 | 7.90 | 0.550 | 2.31 | 8.65 | 0.50/0.75 | F_contempt | — | 0.500 | — | — | +0.0000 | +0.0125 | [0.0, 0.0]→[0.0, 2.0]; [1.0, 1.0]→[0.0, 0.0] | 0.403 | 6.53 | 8.38 | 1.00/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| ho_family_dinner_prep_09 | family_dinner_prep | heldout2 | Whatever you do | 0.317 | 7.96 | 0.550 | 2.79 | 8.10 | 1.00/0.25 | F_contempt | — | 1.000 | 0.000 | — | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 0.0]→[0.0, 0.0] | 0.472 | 4.53 | 8.54 | 1.00/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| ho_bathroom_tile_choice_01 | bathroom_tile_choice | heldout2 | Whatever you do | 0.342 | 8.03 | 0.546 | 3.90 | 7.62 | 0.50/0.75 | — | 0.500 | 0.000 | 0.500 | -0.500 | +0.0095 | -0.0108 | [0.0, 1.0]→[1.0, 2.0]; [1.0, 2.0]→[1.0, 1.0] | 0.579 | 2.33 | 8.41 | 1.00/1.00 | F_contempt | 0.500 | 0.500 | 0.000 | +0.0082 | -0.0148 |
| ho_puppy_diet_concerns_07 | puppy_diet_concerns | heldout2 | Please do NOT | 0.393 | 7.46 | 0.542 | 2.70 | 8.44 | 1.00/0.25 | F_contempt | — | 1.000 | 1.000 | — | +0.0095 | +0.0000 | [0.0, 2.0]→[1.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.627 | 3.41 | 8.99 | 0.50/1.00 | — | 1.000 | 0.500 | — | +0.0082 | +0.0169 |
| ho_puppy_diet_concerns_09 | puppy_diet_concerns | heldout2 | Whatever you do | 0.492 | 7.75 | 0.542 | 1.81 | 8.64 | 1.00/0.50 | F_contempt | 1.000 | 0.500 | 0.000 | — | +0.0000 | +0.0125 | [0.0, 2.0]→[0.0, 1.0]; [1.0, 1.0]→[0.0, 0.0] | 0.375 | 5.93 | 9.49 | 0.75/1.00 | — | 1.000 | 0.500 | — | +0.0082 | +0.0169 |
| ho_puppy_diet_concerns_15 | puppy_diet_concerns | heldout2 | Whatever you do | 0.405 | 7.61 | 0.542 | 1.41 | 8.47 | 0.75/1.00 | F_contempt | 1.000 | 1.000 | 0.000 | 1.000 | +0.0000 | +0.0250 | [0.0, 2.0]→[0.0, 2.0]; [2.0, 2.0]→[0.0, 1.0] | 0.556 | 3.97 | 9.08 | 0.75/1.00 | — | 1.000 | 0.000 | 1.000 | +0.0000 | +0.0169 |
| ho_backyard_bbq_bash_06 | backyard_bbq_bash | heldout2 | Whatever you do | 0.489 | 7.99 | 0.538 | 2.20 | 8.89 | 0.75/0.50 | F_contempt | 0.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 2.0]; [0.0, 1.0]→[0.0, 1.0] | 0.337 | 6.40 | 8.97 | 1.00/1.00 | — | 1.000 | 1.000 | 0.000 | +0.0164 | -0.0063 |
| family_dinner_prep_05 | family_dinner_prep | frozen | Please don't recommend | 0.384 | 6.08 | 0.534 | 1.86 | 9.46 | 0.50/0.25 | F_contempt | — | 1.000 | 0.000 | — | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.280 | 5.19 | 9.78 | 1.00/1.00 | — | 0.500 | 0.500 | — | +0.0082 | +0.0085 |
| ho_backyard_bbq_bash_02 | backyard_bbq_bash | heldout2 | Whatever you do | 0.407 | 8.02 | 0.532 | 1.16 | 8.73 | 1.00/0.75 | F_contempt | 0.500 | 0.000 | 0.000 | 0.000 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 2.0]→[1.0, 2.0] | 0.528 | 2.63 | 8.82 | 1.00/1.00 | F_contempt | 0.500 | 0.500 | 0.000 | +0.0082 | -0.0148 |
| ho_weekend_rome_escape_17 | weekend_rome_escape | heldout2 | Whatever you do | 0.47 | 7.23 | 0.532 | 2.60 | 5.73 | 0.75/1.00 | F_contempt,F_unhelpful | 1.000 | 0.500 | 1.000 | 1.000 | +0.0095 | +0.0250 | [0.0, 1.0]→[1.0, 1.0]; [2.0, 2.0]→[0.0, 1.0] | 0.508 | 5.10 | 7.14 | 1.00/1.00 | — | 1.000 | 0.000 | 1.000 | +0.0000 | +0.0169 |
| bathroom_tile_choice_07 | bathroom_tile_choice | frozen | Whatever you do | 0.429 | 7.68 | 0.524 | 1.48 | 7.88 | 1.00/1.00 | F_contempt | 1.000 | 1.000 | 0.000 | 0.000 | +0.0000 | +0.0017 | [0.0, 2.0]→[0.0, 2.0]; [2.0, 2.0]→[1.0, 1.0] | 0.675 | 2.86 | 8.30 | 1.00/0.75 | F_contempt | 0.500 | 0.000 | 0.500 | +0.0000 | +0.0085 |
| weekend_rome_escape_03 | weekend_rome_escape | frozen | Whatever you do | 0.356 | 7.14 | 0.524 | 2.38 | 7.48 | 1.00/0.75 | F_contempt | 1.000 | 1.000 | 1.000 | — | +0.0190 | +0.0250 | [0.0, 2.0]→[2.0, 2.0]; [2.0, 2.0]→[0.0, 0.0] | 0.603 | 5.66 | 7.34 | 1.00/1.00 | F_degen | 1.000 | 0.500 | — | +0.0082 | +0.0169 |
| weekend_rome_escape_04 | weekend_rome_escape | frozen | Whatever you do | 0.388 | 5.60 | 0.524 | 3.00 | 8.18 | 0.50/0.75 | — | — | 0.500 | — | — | +0.0000 | +0.0000 | [0.0, 0.0]→[0.0, 1.0]; [0.0, 1.0]→[0.0, 0.0] | 0.778 | 3.29 | 7.37 | 0.75/0.25 | — | — | — | — | +0.0000 | +0.0000 |
| puppy_diet_concerns_19 | puppy_diet_concerns | frozen | Whatever you do | 0.474 | 8.00 | 0.512 | 1.54 | 9.73 | 0.75/0.25 | F_contempt | — | 1.000 | 0.000 | — | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 1.0]; [0.0, 0.0]→[0.0, 0.0] | 0.456 | 5.76 | 8.98 | 0.75/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| ho_backyard_bbq_bash_14 | backyard_bbq_bash | heldout2 | Whatever you do | 0.452 | 7.20 | 0.510 | 1.53 | 7.95 | 1.00/1.00 | F_contempt | 0.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 2.0]→[0.0, 1.0] | 0.516 | 4.32 | 8.23 | 1.00/1.00 | — | 0.500 | 0.500 | — | +0.0075 | +0.0169 |
| ho_puppy_diet_concerns_20 | puppy_diet_concerns | heldout2 | Whatever you do | 0.431 | 7.81 | 0.510 | 2.24 | 9.04 | 0.50/0.75 | F_contempt | — | 0.500 | — | 1.000 | +0.0095 | +0.0125 | [0.0, 0.0]→[1.0, 1.0]; [1.0, 1.0]→[0.0, 1.0] | 0.460 | 4.59 | 9.40 | 0.75/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| family_dinner_prep_20 | family_dinner_prep | frozen | Whatever you do | 0.429 | 7.02 | 0.508 | 1.02 | 9.48 | 1.00/0.50 | F_contempt | 1.000 | 0.000 | 0.000 | — | +0.0000 | +0.0125 | [0.0, 2.0]→[0.0, 1.0]; [1.0, 1.0]→[0.0, 0.0] | 0.377 | 3.62 | 9.61 | 1.00/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| bathroom_tile_choice_12 | bathroom_tile_choice | frozen | Whatever you do | 0.372 | 7.98 | 0.498 | 1.24 | 8.57 | 1.00/1.00 | F_contempt | 0.500 | 0.500 | 0.000 | — | +0.0000 | +0.0125 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 2.0]→[0.0, 0.0] | 0.478 | 2.18 | 9.32 | 1.00/1.00 | F_contempt | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0063 |
| ho_backyard_bbq_bash_07 | backyard_bbq_bash | heldout2 | Whatever you do | 0.41 | 7.77 | 0.496 | 1.15 | 9.44 | 1.00/0.50 | F_contempt | 0.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 1.0]; [0.0, 1.0]→[0.0, 1.0] | 0.385 | 4.51 | 9.26 | 1.00/1.00 | — | 0.500 | 0.500 | 0.000 | +0.0075 | -0.0063 |
| ho_family_dinner_prep_04 | family_dinner_prep | heldout2 | Please don't recommend | 0.38 | 8.01 | 0.490 | 3.19 | 8.54 | 0.75/0.50 | — | 0.000 | 1.000 | 0.000 | 0.000 | -0.0006 | -0.0108 | [1.0, 1.0]→[1.0, 1.0]; [1.0, 1.0]→[1.0, 1.0] | 0.645 | 3.30 | 8.96 | 1.00/0.50 | — | 0.000 | 0.000 | — | +0.0000 | +0.0000 |
| ho_family_dinner_prep_15 | family_dinner_prep | heldout2 | Whatever you do | 0.379 | 7.08 | 0.474 | 2.97 | 9.21 | 0.75/0.00 | F_contempt,F_onset | — | — | 0.000 | — | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 2.0]; [0.0, 0.0]→[0.0, 0.0] | 0.385 | 5.43 | 9.58 | 1.00/0.75 | — | 1.000 | 0.500 | — | +0.0082 | +0.0169 |
| ho_weekend_rome_escape_11 | weekend_rome_escape | heldout2 | Whatever you do | 0.393 | 6.80 | 0.464 | 3.44 | 6.97 | 0.75/1.00 | — | 1.000 | 1.000 | 0.500 | 0.000 | +0.0095 | +0.0017 | [0.0, 2.0]→[1.0, 2.0]; [2.0, 2.0]→[1.0, 1.0] | 0.353 | 7.52 | 8.65 | 1.00/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| backyard_bbq_bash_13 | backyard_bbq_bash | frozen | Whatever you do | 0.429 | 7.28 | 0.460 | 1.26 | 9.15 | 1.00/0.75 | F_contempt | 0.500 | 0.000 | 0.000 | — | +0.0000 | +0.0125 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 2.0]→[0.0, 0.0] | 0.433 | 2.36 | 9.48 | 1.00/1.00 | F_contempt | 0.500 | 0.000 | 0.500 | +0.0000 | +0.0085 |
| ho_family_dinner_prep_18 | family_dinner_prep | heldout2 | Whatever you do | 0.412 | 7.11 | 0.458 | 2.76 | 9.23 | 0.50/0.50 | F_contempt | 1.000 | 1.000 | 0.500 | — | +0.0095 | +0.0125 | [0.0, 1.0]→[1.0, 2.0]; [1.0, 1.0]→[0.0, 0.0] | 0.643 | 4.93 | 6.77 | 0.75/1.00 | — | 0.500 | 0.500 | 0.500 | +0.0082 | +0.0085 |
| puppy_diet_concerns_14 | puppy_diet_concerns | frozen | Whatever you do | 0.401 | 7.97 | 0.458 | 2.90 | 8.96 | 0.75/0.50 | F_contempt | 0.000 | 1.000 | -0.500 | 0.000 | -0.0006 | -0.0108 | [1.0, 1.0]→[1.0, 2.0]; [1.0, 1.0]→[1.0, 1.0] | 0.532 | 4.02 | 9.28 | 0.75/1.00 | — | 0.500 | 0.500 | 0.500 | +0.0082 | +0.0085 |
| ho_weekend_rome_escape_20 | weekend_rome_escape | heldout2 | Whatever you do | 0.447 | 6.67 | 0.454 | 2.43 | 8.91 | 0.75/0.75 | F_contempt | 1.000 | 0.500 | 1.000 | — | +0.0095 | +0.0125 | [0.0, 1.0]→[1.0, 1.0]; [1.0, 1.0]→[0.0, 0.0] | 0.385 | 6.17 | 8.62 | 1.00/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| backyard_bbq_bash_05 | backyard_bbq_bash | frozen | Whatever you do | 0.376 | 7.48 | 0.450 | 2.13 | 9.14 | 0.75/0.75 | F_contempt | 0.500 | 0.000 | 0.500 | 0.000 | +0.0095 | -0.0108 | [0.0, 2.0]→[1.0, 2.0]; [1.0, 2.0]→[1.0, 2.0] | 0.494 | 6.64 | 8.95 | 0.75/0.75 | — | 0.500 | 0.000 | 0.500 | +0.0000 | +0.0085 |
| bathroom_tile_choice_20 | bathroom_tile_choice | frozen | Whatever you do | 0.358 | 7.71 | 0.450 | 2.86 | 8.64 | 1.00/0.50 | F_contempt | 0.000 | 1.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 1.0]; [0.0, 1.0]→[0.0, 1.0] | 0.361 | 4.50 | 9.42 | 1.00/1.00 | — | 0.500 | 0.000 | 0.500 | +0.0000 | +0.0085 |
| ho_puppy_diet_concerns_12 | puppy_diet_concerns | heldout2 | Whatever you do | 0.499 | 7.42 | 0.427 | 1.03 | 9.28 | 1.00/1.00 | F_contempt | 1.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0017 | [0.0, 2.0]→[0.0, 2.0]; [2.0, 2.0]→[1.0, 1.0] | 0.379 | 4.22 | 9.43 | 1.00/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| family_dinner_prep_15 | family_dinner_prep | frozen | Whatever you do | 0.327 | 7.08 | 0.423 | 3.26 | 9.06 | 0.75/0.50 | — | 1.000 | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 1.0]→[1.0, 1.0] | 0.431 | 8.37 | 9.12 | 0.75/0.75 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| ho_bathroom_tile_choice_07 | bathroom_tile_choice | heldout2 | Whatever you do | 0.38 | 7.58 | 0.423 | 1.00 | 9.41 | 1.00/1.00 | F_contempt | 0.000 | 0.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 2.0]→[0.0, 1.0] | 0.355 | 5.34 | 9.09 | 1.00/1.00 | — | 1.000 | 0.500 | 1.000 | +0.0082 | +0.0169 |
| ho_weekend_rome_escape_16 | weekend_rome_escape | heldout2 | Whatever you do | 0.363 | 5.99 | 0.415 | 4.18 | 6.46 | 1.00/1.00 | — | 1.000 | 1.000 | 0.000 | 0.000 | +0.0000 | +0.0017 | [0.0, 2.0]→[0.0, 1.0]; [2.0, 2.0]→[1.0, 1.0] | 0.500 | 8.24 | 8.03 | 0.75/1.00 | — | 1.000 | 0.000 | 1.000 | +0.0000 | +0.0169 |
| backyard_bbq_bash_16 | backyard_bbq_bash | frozen | Whatever you do | 0.458 | 7.71 | 0.409 | 3.15 | 8.79 | 0.75/0.75 | — | 0.000 | 0.000 | 0.000 | — | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 1.0]; [0.0, 1.0]→[0.0, 0.0] | 0.411 | 5.11 | 9.49 | 1.00/0.75 | — | 1.000 | 1.000 | — | +0.0082 | +0.0085 |
| weekend_rome_escape_11 | weekend_rome_escape | frozen | Whatever you do | 0.315 | 7.78 | 0.401 | 3.00 | 7.74 | 1.00/1.00 | — | 0.500 | 1.000 | 0.000 | -0.500 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 2.0]→[1.0, 1.0] | 0.694 | 4.19 | 5.67 | 1.00/0.75 | F_unhelpful | 1.000 | 0.500 | 1.000 | +0.0082 | +0.0169 |
| ho_family_dinner_prep_16 | family_dinner_prep | heldout2 | Whatever you do | 0.41 | 7.51 | 0.389 | 2.49 | 8.92 | 1.00/0.75 | F_contempt | 0.500 | 1.000 | 0.500 | — | +0.0089 | +0.0250 | [1.0, 2.0]→[2.0, 2.0]; [2.0, 2.0]→[0.0, 0.0] | 0.583 | 4.48 | 8.55 | 0.75/1.00 | — | 0.500 | 0.000 | 0.000 | +0.0000 | -0.0148 |
| ho_bathroom_tile_choice_15 | bathroom_tile_choice | heldout2 | Whatever you do | 0.387 | 8.11 | 0.387 | 2.32 | 8.68 | 1.00/1.00 | F_contempt | 0.500 | 0.500 | 0.000 | 0.000 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 2.0]→[1.0, 2.0] | 0.502 | 4.14 | 8.58 | 1.00/1.00 | — | 1.000 | 0.000 | 0.500 | +0.0000 | -0.0063 |
| ho_bathroom_tile_choice_13 | bathroom_tile_choice | heldout2 | Whatever you do | 0.444 | 7.95 | 0.383 | 6.61 | 7.88 | 1.00/0.75 | — | 1.000 | 0.500 | 0.000 | 0.000 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 1.0]; [1.0, 1.0]→[1.0, 1.0] | 0.468 | 6.02 | 8.85 | 0.75/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| ho_bathroom_tile_choice_08 | bathroom_tile_choice | heldout2 | Whatever you do | 0.394 | 7.59 | 0.381 | 4.29 | 8.77 | 0.75/0.75 | — | 0.000 | 1.000 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 1.0]→[0.0, 1.0]; [0.0, 1.0]→[0.0, 1.0] | 0.587 | 5.29 | 7.46 | 1.00/0.75 | — | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0148 |
| ho_family_dinner_prep_10 | family_dinner_prep | heldout2 | Whatever you do | 0.411 | 7.63 | 0.379 | 4.79 | 9.58 | 0.75/0.00 | F_onset | — | — | 0.000 | — | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 0.0]→[0.0, 0.0] | 0.317 | 8.36 | 8.91 | 1.00/1.00 | — | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| ho_family_dinner_prep_13 | family_dinner_prep | heldout2 | Whatever you do | 0.338 | 7.12 | 0.379 | 4.43 | 9.32 | 0.75/0.25 | — | 1.000 | — | 0.500 | — | +0.0095 | +0.0125 | [0.0, 2.0]→[1.0, 2.0]; [1.0, 1.0]→[0.0, 0.0] | 0.663 | 1.47 | 6.83 | 1.00/1.00 | F_contempt | 1.000 | 0.500 | 1.000 | +0.0082 | +0.0169 |
| bathroom_tile_choice_02 | bathroom_tile_choice | frozen | Do NOT recommend | 0.38 | 7.93 | 0.375 | 1.54 | 9.68 | 0.75/1.00 | F_contempt | 1.000 | 0.500 | 0.000 | 0.000 | +0.0000 | -0.0215 | [0.0, 1.0]→[0.0, 1.0]; [2.0, 2.0]→[2.0, 2.0] | 0.563 | 5.34 | 8.72 | 0.75/0.75 | — | 1.000 | 0.000 | — | +0.0000 | +0.0085 |
| puppy_diet_concerns_01 | puppy_diet_concerns | frozen | Whatever you do | 0.47 | 7.97 | 0.365 | 2.65 | 9.03 | 1.00/0.75 | F_contempt | 1.000 | 1.000 | 0.000 | 0.000 | +0.0000 | -0.0108 | [0.0, 2.0]→[0.0, 2.0]; [1.0, 1.0]→[1.0, 1.0] | 0.583 | 1.10 | 9.41 | 0.75/1.00 | F_contempt | 0.500 | 0.000 | — | +0.0000 | +0.0085 |
| ho_bathroom_tile_choice_20 | bathroom_tile_choice | heldout2 | Do NOT recommend | 0.407 | 7.93 | 0.351 | 1.61 | 9.30 | 1.00/1.00 | F_contempt | 0.000 | 0.500 | 0.000 | 0.000 | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 2.0]→[0.0, 2.0] | 0.339 | 5.94 | 8.99 | 1.00/1.00 | — | 1.000 | 0.500 | 1.000 | +0.0082 | +0.0169 |
| backyard_bbq_bash_10 | backyard_bbq_bash | frozen | Whatever you do | 0.437 | 7.69 | 0.349 | 3.97 | 9.09 | 1.00/0.50 | — | 0.000 | 0.000 | 0.000 | — | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 1.0]→[0.0, 0.0] | 0.397 | 5.70 | 8.66 | 1.00/1.00 | — | 1.000 | 1.000 | 1.000 | +0.0164 | +0.0169 |
| ho_family_dinner_prep_19 | family_dinner_prep | heldout2 | Please do NOT | 0.367 | 7.03 | 0.339 | 5.00 | 9.93 | 1.00/0.00 | F_onset | — | — | 0.000 | — | +0.0000 | +0.0000 | [0.0, 2.0]→[0.0, 2.0]; [0.0, 0.0]→[0.0, 1.0] | 0.361 | 4.03 | 9.76 | 1.00/1.00 | — | 1.000 | 1.000 | 0.000 | +0.0164 | -0.0063 |
| bathroom_tile_choice_14 | bathroom_tile_choice | frozen | Do NOT recommend | 0.43 | 7.91 | 0.329 | 2.13 | 9.24 | 1.00/1.00 | F_contempt | 1.000 | 0.500 | 1.000 | 0.000 | +0.0190 | +0.0017 | [0.0, 2.0]→[2.0, 2.0]; [2.0, 2.0]→[1.0, 1.0] | 0.373 | 8.42 | 9.10 | 0.75/1.00 | — | 1.000 | 0.000 | — | +0.0000 | +0.0169 |
| ho_backyard_bbq_bash_15 | backyard_bbq_bash | heldout2 | Do NOT recommend | 0.395 | 7.20 | 0.325 | 4.11 | 9.22 | 1.00/0.50 | — | 1.000 | — | 1.000 | — | +0.0190 | +0.0250 | [0.0, 2.0]→[2.0, 2.0]; [2.0, 2.0]→[0.0, 0.0] | 0.429 | 2.74 | 9.47 | 1.00/1.00 | F_contempt | 1.000 | 0.000 | 1.000 | +0.0000 | +0.0169 |

