# Run axis_pv: Assistant Axis + persona vectors on Qwen3.6-27B, and projection of E01's two fine-tunes

Branch `replicate_qwen27B`. Code, configs, trait files and small results: [`results/axis_pv/`](results/axis_pv/). Pod `cxdwib87ij4eqg`, 2× H100 80 GB.

**Status: all three parts done, pushed and uploaded (verified); merged models deleted; pod stop is the last step (see Wrap-up).** Results will be added above the plan; the plan below is not edited after its commit (`4cf5771`) except by dated amendments.

## Summary

1. **Assistant Axis (official pipeline): "style-confounded" by the pre-registered rule, like the teammate's reduced axis.** Built from 265 of 275 roles (10 had < 50 fully-in-role answers). It separates held-out default answers from role-play answers well (**AUC 0.927** at block 32) and is stable (role-half and prompt-half cosines ≈ 0.99; |cos| with PC1 of the role vectors 0.77). But two style prompts that keep the model an AI assistant land *beyond* the role-play level: **florid 1.41, theatrical 1.28** of the default-to-role gap (needs < 0.5); fictional 0.98, formal 0.13, terse 0.07. The roles at its two ends are ornate/fanciful ones (aberration, zealot, poet, jester) vs plain professional ones (assistant, reviewer, doctor). It mostly measures register.
2. **Persona vectors: 8 of 9 valid** (apathetic, impolite, sycophantic, hallucinating, humorous, optimistic, and the two custom traits helpful and dismissive: gaps 62–93 points, eval AUC 0.957–1.000). **evil is not valid**: the model refuses the evil system prompts (positive trait mean 6.3). helpful and dismissive are near-opposite (cosine −0.84). A plain "be terse" prompt moves **0.30** of the dismissive pos−neg gap toward dismissive, so that vector partly tracks brevity.
3. **Part C (exploratory, no verdict rules):**
   - **The paper's hypothesis, stated in advance:** in the untrained model, helpful characters' story prefixes project closer to the default-Assistant end than dismissive characters' at block 32: **+0.19 [−0.05, +0.43]**. Predicted sign, but the interval includes zero (per file: +0.28 [−0.02, +0.59] and +0.09 [−0.26, +0.47]). The helpful and dismissive *persona vectors* do separate the two characters at that token (+0.36 [+0.07, +0.66] and −0.37 [−0.72, −0.03]); over the next 150 story tokens the axis difference is +0.41 [+0.24, +0.57].
   - **Both fine-tunes move the story prefixes toward the Assistant end and toward "helpful"** by similar amounts: axis +3.95 (`hc_db_s0`) and +3.24 (`hb_dc_s0`) at the last prefix token on their own files; helpful vector +2.17 and +1.77; dismissive −1.55 and −1.08.
   - **Default Assistant (C1):** the fine-tunes' own answers sit lower on the axis (−3.4, −4.0) and toward dismissive (+1.9, +2.4). On identical text (the untrained model's answers fed through each fine-tune) the shift is small and the other way (axis +0.4). So the drop comes from what the fine-tunes write (shorter answers, fewer at the 512 cap: 45–50 vs 97 of 100), not from how they read the same text.
   - **Table 7 prompt (C2):** the fine-tunes' own replies project far less dismissive (−8.3, −7.2) because after the opening deflection they keep writing (mean 362 and 315 tokens vs 38), often continuing as a dialogue and writing the user's lines too, consistent with E01's garble finding under this prompt. On identical text: axis +2.0 / +1.8, dismissive −1.4 / −1.3.
4. **Spend $5.29** by the per-call ledger (80,200 judge calls, 0 errors, 0 rate-limit back-offs; $5.51 by key usage at the last reading) of the $15 budget. GPU work.

## Part A results: Assistant Axis, official pipeline, untrained model

**Reading (pre-registered): "style-confounded".** Held-out AUC at block 32 is **0.927** [0.864, 0.976] (passes ≥ 0.80), but the florid and theatrical styles sit at **1.41** and **1.28** of the default-to-role gap (the rule needs < 0.5 for both). Both style prompts keep the model an AI assistant, yet they land *past* the average role-play response. The official axis has the same problem as the teammate's reduced axis.

- **Axis built from:** 275 roles + default × 5 system prompts × 20 questions = 27,600 responses, all 27,500 role responses judged (score 3: 24,092; 2: 1,937; 1: 1,304; 0: 167; none missing). **265 of 275 roles** got a vector at min_count 50. Excluded (score-3 count of 100): hacker 0, saboteur 18, translator 25, summarizer 27, grader 30, screener 36, virus 36, proofreader 40, validator 44, collaborator 49. Axis norm by block (8 → 56): 1.01, 2.36, 4.09, **5.55**, 9.25, 13.66, 31.18.
- **Validation set:** 20 held-out questions × 276 role files × 1 sample (5,520) + default under all 5 prompts (100) + 5 styles × 20 (100). Role responses judged: 5,500 (score 3: 5,017; 2: 230; 1: 219; 0: 34). Primary comparison: 20 default responses vs 4,945 score-3 responses from the 265 roles with a vector. Mean projection at block 32: default 10.95, score-3 roles 5.73.
- **Stability:** role halves (seed 0) cosine 0.991 at block 32 (100 random splits: mean 0.994, min 0.982); prompt halves (seed 0 split {2,4} vs {0,1,3}, 262 / 263 roles) 0.988 (100 splits: mean 0.986, min 0.978); the teammate's fixed split {0,1} vs {2,3,4}: 0.987.
- **|cos(axis, PC1 of role vectors)| = 0.773** at block 32 (PC1 explains 30% of role-vector variance).
- **What the axis orders:** role vectors projecting lowest at block 32 are aberration, zealot, prey, absurdist, leviathan, hoarder, fool, void, poet, jester; highest are assistant (11.2, next to the default vector's 11.3), reviewer, doctor, generalist, moderator, researcher, nutritionist, analyst, secretary, evaluator. Fanciful, stylised roles sit at one end and plain-register professional roles at the other.
- **Style AUCs** (default vs style, block 32): florid 1.000, theatrical 0.993, fictional 0.960, formal 0.662, terse 0.575. Formal (0.13) and terse (0.07) barely move along the axis; fictional sits at role level (0.98).

#### Part A: held-out separation (validation set; default = 20 held-out responses, roles = held-out responses scored 3 from roles with a vector)

| Block | AUC default vs role (score 3) [95% CI] | Cohen's d | AUC vs all role responses | AUC, default under all 5 prompts (100) | Stability: role halves | Stability: prompt halves | abs cos(axis, PC1) | PC1 variance share |
|---|---|---|---|---|---|---|---|---|
| block 8 | 0.869 [0.813, 0.920] | 1.62 | 0.841 | 0.873 | 0.992 | 0.989 | 0.825 | 0.299 |
| block 16 | 0.924 [0.862, 0.973] | 2.05 | 0.898 | 0.926 | 0.990 | 0.986 | 0.793 | 0.338 |
| block 24 | 0.904 [0.831, 0.959] | 1.85 | 0.878 | 0.908 | 0.988 | 0.986 | 0.767 | 0.257 |
| block 32 | 0.927 [0.864, 0.976] | 2.09 | 0.902 | 0.931 | 0.991 | 0.988 | 0.773 | 0.301 |
| block 40 | 0.926 [0.862, 0.972] | 2.05 | 0.901 | 0.929 | 0.990 | 0.988 | 0.778 | 0.256 |
| block 48 | 0.933 [0.875, 0.978] | 2.14 | 0.908 | 0.936 | 0.991 | 0.990 | 0.780 | 0.316 |
| block 56 | 0.926 [0.869, 0.970] | 2.02 | 0.899 | 0.929 | 0.987 | 0.988 | 0.749 | 0.238 |

#### Part A: style control (fraction of the default-to-role gap; 0 = default level, 1 = role-play level)

| Block | florid | theatrical | formal | fictional | terse |
|---|---|---|---|---|---|
| block 8 | 0.87 | 1.03 | -0.52 | 1.03 | -0.29 |
| block 16 | 1.63 | 1.43 | 0.10 | 0.93 | -0.05 |
| block 24 | 1.65 | 1.39 | 0.12 | 0.97 | -0.17 |
| block 32 | 1.41 | 1.28 | 0.13 | 0.98 | 0.07 |
| block 40 | 1.49 | 1.30 | 0.15 | 0.95 | -0.16 |
| block 48 | 1.51 | 1.41 | 0.13 | 0.97 | -0.05 |
| block 56 | 1.83 | 1.63 | 0.37 | 0.96 | 0.02 |

Files: `results/axis_pv/part_a_validation.json` (all numbers, every block), `part_a_tables.md`; command `python -I code/aa_validate.py` (inputs: `W/aa/out/{activations,scores,vectors,axis.pt}`, `W/aa/val/{activations,scores}`). Per-item projections: HF `axis_pv/part_a/part_a_val_projections.jsonl`.

## Part B results: persona vectors, untrained model

**Reading (pre-registered): 8 of 9 vectors are valid** (pos − neg trait mean ≥ 40 on the extraction set and eval AUC ≥ 0.80 at block 32): apathetic, impolite, sycophantic, hallucinating, humorous, optimistic, helpful, dismissive. **evil is not valid**: Qwen3.6-27B refuses the evil system prompts (positive trait mean 6.3; only 67 of 1000 pairs pass the repo's mask; eval AUC 0.777). Its vector is delivered but should not be used.

- **Extraction:** 9 traits × 2,000 generations (20 questions × 5 pairs × 10 samples), all 18,000 judged for trait and coherence (missing trait scores: 7, all evil positive, i.e. REFUSAL). apathetic at max_num_seqs 32, the rest at 256 (see the progress-log entry). Eval sets: 9 × 400 generations, all judged.
- **Custom traits:** helpful 94.9 / 5.1 (419 effective pairs: the disengaged negatives often fail the coherence ≥ 50 mask; negative coherence mean 42.0) and dismissive 93.2 / 0.1 (804 pairs; positive coherence mean 66.4). Both reach eval AUC 1.000. Their vectors are nearly opposite (cosine −0.84 at block 32); dismissive is close to apathetic (+0.77) and impolite (+0.73), helpful is opposite to apathetic (−0.82).
- **Does "dismissive" mean "terse"?** Partly. Projected onto the dismissive vector, the terse style moves **+0.30** of the eval pos − neg gap away from the default Assistant (florid and theatrical +0.21, formal +0.02); on the helpful vector terse moves −0.30. The same terse answers move +0.50 on apathetic and +0.46 on impolite. So a plain request for brevity accounts for roughly a third of the dismissive direction's pos − neg gap at block 32 in these 20 held-out answers.
- **Relation to the axis (cosine at block 32):** helpful +0.35 and optimistic +0.38 point toward the default Assistant; dismissive −0.34, apathetic −0.36, impolite −0.61, humorous −0.64, evil −0.64, sycophantic −0.34, hallucinating −0.42 point away.

#### Part B: persona vectors (response_avg_diff), block 32

| Trait | Pos trait mean (extract) | Neg trait mean | Gap | Effective pairs / 1000 | Eval pos / neg trait mean | AUC pos vs neg (eval) [95% CI] | cos with axis | Valid? |
|---|---|---|---|---|---|---|---|---|
| apathetic | 88.1 | 3.2 | 84.9 | 917 | 86.4 / 3.0 | 1.000 [1.000, 1.000] | -0.358 | **valid** |
| impolite | 87.2 | 0.1 | 87.1 | 952 | 88.1 / 0.1 | 0.998 [0.995, 1.000] | -0.614 | **valid** |
| evil | 6.3 | 0.0 | 6.3 | 67 | 4.5 / 0.0 | 0.777 [0.730, 0.821] | -0.640 | not valid |
| sycophantic | 95.0 | 15.9 | 79.1 | 990 | 94.8 / 19.7 | 1.000 [1.000, 1.000] | -0.336 | **valid** |
| hallucinating | 76.8 | 15.1 | 61.7 | 582 | 77.8 / 14.6 | 0.957 [0.937, 0.974] | -0.418 | **valid** |
| humorous | 93.7 | 3.7 | 90.0 | 999 | 93.2 / 4.6 | 1.000 [1.000, 1.000] | -0.641 | **valid** |
| optimistic | 94.8 | 1.6 | 93.2 | 998 | 94.4 / 2.1 | 1.000 [1.000, 1.000] | +0.384 | **valid** |
| helpful | 94.9 | 5.1 | 89.8 | 419 | 95.0 / 4.8 | 1.000 [1.000, 1.000] | +0.350 | **valid** |
| dismissive | 93.2 | 0.1 | 93.0 | 804 | 93.8 / 0.1 | 1.000 [1.000, 1.000] | -0.343 | **valid** |

#### Part B: Part A's style sets on each persona vector, block 32 (shift from the default held-out responses, as a fraction of the eval pos − neg gap)

| Trait | florid | theatrical | formal | fictional | terse |
|---|---|---|---|---|---|
| apathetic | +0.22 | +0.23 | +0.06 | +0.18 | +0.50 |
| impolite | +0.48 | +0.54 | -0.01 | +0.40 | +0.46 |
| evil | +3.42 | +3.23 | +0.34 | +2.73 | +1.45 |
| sycophantic | +0.37 | +0.35 | +0.08 | +0.19 | +0.23 |
| hallucinating | +0.36 | +0.27 | +0.13 | +0.32 | -0.18 |
| humorous | +0.49 | +0.51 | -0.08 | +0.35 | +0.06 |
| optimistic | -0.13 | -0.19 | +0.01 | -0.21 | -0.12 |
| helpful | -0.17 | -0.18 | -0.01 | -0.12 | -0.30 |
| dismissive | +0.21 | +0.21 | +0.02 | +0.15 | +0.30 |

#### Part B: cosine between persona vectors, block 32

| | apathetic | impolite | evil | sycophantic | hallucinating | humorous | optimistic | helpful | dismissive |
|---|---|---|---|---|---|---|---|---|---|
| apathetic | +1.00 | +0.71 | +0.54 | +0.38 | +0.01 | +0.37 | -0.43 | -0.82 | +0.77 |
| impolite | +0.71 | +1.00 | +0.68 | +0.38 | +0.14 | +0.70 | -0.59 | -0.66 | +0.73 |
| evil | +0.54 | +0.68 | +1.00 | +0.43 | +0.27 | +0.50 | -0.59 | -0.47 | +0.48 |
| sycophantic | +0.38 | +0.38 | +0.43 | +1.00 | +0.09 | +0.30 | -0.01 | -0.48 | +0.52 |
| hallucinating | +0.01 | +0.14 | +0.27 | +0.09 | +1.00 | +0.23 | -0.08 | +0.01 | -0.07 |
| humorous | +0.37 | +0.70 | +0.50 | +0.30 | +0.23 | +1.00 | -0.37 | -0.47 | +0.46 |
| optimistic | -0.43 | -0.59 | -0.59 | -0.01 | -0.08 | -0.37 | +1.00 | +0.32 | -0.30 |
| helpful | -0.82 | -0.66 | -0.47 | -0.48 | +0.01 | -0.47 | +0.32 | +1.00 | -0.84 |
| dismissive | +0.77 | +0.73 | +0.48 | +0.52 | -0.07 | +0.46 | -0.30 | -0.84 | +1.00 |

Files: `results/axis_pv/part_b_validation.json` (all blocks; trait/coherence means, effective-only means, per-style projections), `part_b_tables.md`; command `python -I code/pv_validate.py` (inputs: `W/pv/out/{extract,eval,vectors,eval_acts}`, `W/aa/val/activations/{style_*,default}.pt`). Per-item eval projections: HF `axis_pv/part_b/part_b_eval_projections.jsonl`. Note: the style sets' activations come from the axis pipeline (assistant-span mean, left-padded batches), the eval sets' from the persona_vectors code (response-token mean, batch 1); Part C's consistency check measures how much that matters.

## Part C results: untrained model and E01's two fine-tunes (all exploratory)

- **Generations:** 3 models × (C1 + C2) × 50 held-out questions × 2 samples = 600, 0 errors. Replies at the 512-token cap: untrained C1 97/100, C2 0/100; `hc_db_s0` C1 45, C2 14; `hb_dc_s0` C1 50, C2 9. Mean reply length: untrained 510 (C1) / 38 (C2) tokens; `hc_db_s0` 449 / 362; `hb_dc_s0` 458 / 315 (`W/pc/gen_<model>.jsonl`).
- **Activations:** one HF process, base + both adapters (adapter off = untrained). Own replies 600, teacher-forced 400, C3 160 prefixes × 3 models (last token and next 150 tokens). One story (hc_db/hb_dc index 4507) has no text after its cut, so the "next 150 tokens" sets have 159 stories.
- **Consistency check:** this code's batch-1 activations vs the axis pipeline's own (left-padded batches of 16) on the 20 validation default answers: cosine ≥ 0.99999 at every block; axis projections differ by ≤ 0.034 at block 32. Activations from the two code paths are interchangeable.
- **Hypothesis (stated in advance):** untrained model, C3 last prefix token, block 32, helpful − dismissive on the axis = **+0.19 [−0.05, +0.43]** (80 vs 80 stories; mean 3.49 vs 3.31). The sign is as predicted; the interval includes zero.

#### C1–C3 levels: mean projection at block 32 [95% CI over prompts] (exploratory)

| Input set | n prompts | Axis (higher = default Assistant) | helpful vector | dismissive vector |
|---|---|---|---|---|
| C1 untrained, own replies | 50 | 11.33 [10.82, 11.82] | 5.59 [5.27, 5.90] | -6.96 [-7.28, -6.64] |
| C1 hc_db_s0, own replies | 50 | 7.90 [7.35, 8.46] | 3.49 [3.10, 3.88] | -5.10 [-5.50, -4.69] |
| C1 hb_dc_s0, own replies | 50 | 7.37 [6.76, 7.98] | 3.04 [2.62, 3.45] | -4.60 [-5.02, -4.17] |
| C1 untrained replies through hc_db_s0 | 50 | 11.76 [11.26, 12.24] | 5.49 [5.17, 5.79] | -7.09 [-7.42, -6.77] |
| C1 untrained replies through hb_dc_s0 | 50 | 11.74 [11.23, 12.22] | 5.46 [5.15, 5.77] | -7.05 [-7.36, -6.73] |
| C2 untrained, own replies | 50 | 4.66 [4.45, 4.89] | -7.93 [-8.16, -7.69] | 9.93 [9.66, 10.17] |
| C2 hc_db_s0, own replies | 50 | 5.59 [5.41, 5.78] | -1.76 [-2.08, -1.44] | 1.61 [1.16, 2.09] |
| C2 hb_dc_s0, own replies | 50 | 4.77 [4.56, 4.99] | -2.64 [-2.97, -2.31] | 2.68 [2.25, 3.12] |
| C2 untrained replies through hc_db_s0 | 50 | 6.68 [6.45, 6.93] | -6.35 [-6.58, -6.12] | 8.53 [8.28, 8.78] |
| C2 untrained replies through hb_dc_s0 | 50 | 6.50 [6.28, 6.74] | -6.42 [-6.66, -6.18] | 8.62 [8.36, 8.87] |
| C3 last prefix token, untrained | 160 | 3.40 [3.28, 3.52] | -0.25 [-0.40, -0.11] | -0.89 [-1.06, -0.72] |
| C3 last prefix token, hc_db_s0 | 160 | 7.31 [7.07, 7.53] | 1.82 [1.70, 1.95] | -2.31 [-2.47, -2.15] |
| C3 last prefix token, hb_dc_s0 | 160 | 6.63 [6.42, 6.82] | 1.60 [1.47, 1.72] | -2.08 [-2.24, -1.92] |
| C3 next 150 story tokens, untrained | 159 | 2.42 [2.33, 2.51] | 1.25 [1.15, 1.33] | -2.56 [-2.66, -2.45] |
| C3 next 150 story tokens, hc_db_s0 | 159 | 4.38 [4.25, 4.49] | 1.71 [1.61, 1.81] | -2.94 [-3.06, -2.81] |
| C3 next 150 story tokens, hb_dc_s0 | 159 | 4.37 [4.25, 4.49] | 1.88 [1.77, 1.98] | -3.05 [-3.17, -2.92] |

#### Fine-tune − untrained at block 32 [95% CI, paired over prompts] (exploratory)

| Comparison | Axis | helpful | dismissive |
|---|---|---|---|
| `hc_db_s0`: C1, own replies | -3.43 [-3.91, -2.99] | -2.10 [-2.32, -1.88] | +1.86 [+1.63, +2.09] |
| `hc_db_s0`: C1, same text (untrained replies) | +0.43 [+0.40, +0.47] | -0.10 [-0.13, -0.08] | -0.14 [-0.16, -0.11] |
| `hc_db_s0`: C2, own replies | +0.93 [+0.68, +1.18] | +6.17 [+5.70, +6.62] | -8.32 [-8.91, -7.68] |
| `hc_db_s0`: C2, same text (untrained replies) | +2.02 [+1.96, +2.08] | +1.58 [+1.50, +1.65] | -1.40 [-1.48, -1.31] |
| `hc_db_s0`: C3 last prefix token (own file) | +3.95 [+3.64, +4.24] | +2.17 [+1.96, +2.40] | -1.55 [-1.77, -1.32] |
| `hc_db_s0`: C3 next 150 tokens (own file) | +1.98 [+1.88, +2.06] | +0.51 [+0.44, +0.58] | -0.42 [-0.49, -0.35] |
| `hb_dc_s0`: C1, own replies | -3.96 [-4.45, -3.48] | -2.55 [-2.87, -2.25] | +2.36 [+2.04, +2.69] |
| `hb_dc_s0`: C1, same text (untrained replies) | +0.41 [+0.37, +0.44] | -0.13 [-0.16, -0.10] | -0.09 [-0.12, -0.06] |
| `hb_dc_s0`: C2, own replies | +0.11 [-0.19, +0.42] | +5.29 [+4.92, +5.67] | -7.24 [-7.76, -6.76] |
| `hb_dc_s0`: C2, same text (untrained replies) | +1.84 [+1.78, +1.90] | +1.51 [+1.44, +1.58] | -1.31 [-1.38, -1.23] |
| `hb_dc_s0`: C3 last prefix token (own file) | +3.24 [+2.99, +3.47] | +1.77 [+1.52, +2.00] | -1.08 [-1.29, -0.85] |
| `hb_dc_s0`: C3 next 150 tokens (own file) | +1.98 [+1.89, +2.06] | +0.63 [+0.58, +0.69] | -0.49 [-0.55, -0.43] |

#### C3 helpful − dismissive character at block 32 [95% CI] (exploratory)

| Model | Position | Stories | Axis | helpful | dismissive |
|---|---|---|---|---|---|
| untrained | last prefix token | pooled (80 vs 80) | +0.19 [-0.05, +0.43] | +0.36 [+0.07, +0.66] | -0.37 [-0.72, -0.03] |
| untrained | last prefix token | hb_dc (40 vs 40) | +0.28 [-0.02, +0.59] | +0.25 [-0.14, +0.61] | -0.25 [-0.73, +0.22] |
| untrained | last prefix token | hc_db (40 vs 40) | +0.09 [-0.26, +0.47] | +0.48 [+0.06, +0.92] | -0.49 [-0.97, -0.00] |
| untrained | next 150 tokens | pooled (79 vs 80) | +0.41 [+0.24, +0.57] | +0.65 [+0.50, +0.80] | -0.67 [-0.85, -0.48] |
| untrained | next 150 tokens | hb_dc (40 vs 40) | +0.18 [-0.04, +0.38] | +0.75 [+0.51, +0.99] | -0.93 [-1.23, -0.63] |
| untrained | next 150 tokens | hc_db (39 vs 40) | +0.64 [+0.41, +0.87] | +0.55 [+0.38, +0.72] | -0.41 [-0.61, -0.19] |
| hc_db_s0 | last prefix token | pooled (80 vs 80) | -0.01 [-0.49, +0.47] | +0.35 [+0.11, +0.60] | -0.14 [-0.48, +0.18] |
| hc_db_s0 | last prefix token | hb_dc (40 vs 40) | +0.01 [-0.59, +0.63] | +0.42 [+0.08, +0.79] | -0.20 [-0.66, +0.28] |
| hc_db_s0 | last prefix token | hc_db (40 vs 40) | -0.02 [-0.71, +0.65] | +0.28 [-0.06, +0.62] | -0.09 [-0.49, +0.34] |
| hc_db_s0 | next 150 tokens | pooled (79 vs 80) | +0.28 [+0.04, +0.52] | +0.76 [+0.60, +0.92] | -0.77 [-0.98, -0.56] |
| hc_db_s0 | next 150 tokens | hb_dc (40 vs 40) | -0.20 [-0.50, +0.10] | +0.84 [+0.57, +1.10] | -1.03 [-1.37, -0.70] |
| hc_db_s0 | next 150 tokens | hc_db (39 vs 40) | +0.77 [+0.45, +1.10] | +0.69 [+0.50, +0.89] | -0.51 [-0.75, -0.27] |
| hb_dc_s0 | last prefix token | pooled (80 vs 80) | +0.21 [-0.19, +0.63] | +0.63 [+0.39, +0.87] | -0.42 [-0.74, -0.10] |
| hb_dc_s0 | last prefix token | hb_dc (40 vs 40) | +0.18 [-0.37, +0.72] | +0.75 [+0.41, +1.09] | -0.44 [-0.89, +0.03] |
| hb_dc_s0 | last prefix token | hc_db (40 vs 40) | +0.23 [-0.37, +0.86] | +0.51 [+0.17, +0.84] | -0.39 [-0.79, +0.02] |
| hb_dc_s0 | next 150 tokens | pooled (79 vs 80) | +0.30 [+0.05, +0.52] | +0.83 [+0.66, +0.99] | -0.84 [-1.05, -0.61] |
| hb_dc_s0 | next 150 tokens | hb_dc (40 vs 40) | -0.20 [-0.50, +0.08] | +0.86 [+0.60, +1.14] | -1.06 [-1.41, -0.72] |
| hb_dc_s0 | next 150 tokens | hc_db (39 vs 40) | +0.80 [+0.48, +1.12] | +0.80 [+0.60, +1.00] | -0.61 [-0.85, -0.36] |

All blocks and all 10 directions (axis + 9 persona vectors): `results/axis_pv/part_c_results.json` and `part_c_tables.md` (block 32, every direction). Command: `python -I code/pc_analyze.py` (inputs `W/pc/acts.pt`, `W/aa/out/axis.pt`, `W/pv/out/vectors/`). Per-item projections: HF `axis_pv/part_c/part_c_projections.jsonl`; generations HF `axis_pv/part_c/generations/gen_<model>.jsonl`.

## Where each headline number comes from

Scripts are in `results/axis_pv/code/` (run with `/workspace/venvs/gpu/bin/python -I`, pipeline scripts through `code/pyrun.py`; environment `code/env_axis_pv.sh`). `W = /workspace/si36/axis_pv`.

| Headline | Output file(s) | Command |
|---|---|---|
| Question split | `results/axis_pv/question_split.json`, `W/aa/questions_{pipeline20,heldout50}.jsonl` | `python -I code/make_questions.py` |
| Axis responses (27,600) + validation/style responses (5,720) | `W/aa/out/responses/`, `W/aa/val/responses/` (HF `axis_pv/part_a/`) | `pyrun.py code/aa_gen_all.py` (GPU 0) |
| Role-adherence scores | `W/aa/out/scores/`, `W/aa/val/scores/` (HF) | `code/aa_judge_loop.sh` (the pipeline's `3_judge.py`) |
| Activations (blocks 8–56) | `W/aa/{out,val}/activations/` (raw, stays on /workspace) | `code/aa_acts_chain.sh` (the pipeline's `2_activations.py --layers 8,16,24,32,40,48,56`) |
| Role vectors, axis | `W/aa/out/vectors/`, `W/aa/out/axis.pt`, `W/aa/out/role_vectors.pt` (HF adapters repo `vectors/qwen3.6-27b/axis_pv/axis_and_roles/`) | pipeline `4_vectors.py --min_count 50`, `5_axis.py` |
| Part A AUC, stability, PC1, style fractions, reading | `results/axis_pv/part_a_validation.json`, `part_a_tables.md` | `python -I code/aa_validate.py` |
| Persona generations + judge scores | `W/pv/out/{extract,eval}/<trait>_{pos,neg}_instruct.csv` (HF `axis_pv/part_b/`) | `pyrun.py --path W/pv/repo code/pv_extract_all.py` (repo `eval.eval_persona.main`) |
| max_num_seqs check | `results/axis_pv/max_num_seqs_check.json`, `W/pv/out_check256/` | same, `--check_against` |
| Persona vectors | `W/pv/out/vectors/<trait>_{response_avg,prompt_avg,prompt_last}_diff.pt` (HF adapters repo `.../axis_pv/persona_vectors/`) | `code/pv_vectors.sh` (repo `generate_vec.py --threshold 50`) |
| Part B AUC, validity, style projections, cosines | `results/axis_pv/part_b_validation.json`, `part_b_tables.md` | `code/pv_eval_acts.py`, then `python -I code/pv_validate.py` |
| Part C generations | `W/pc/gen_{base,hc_db_s0,hb_dc_s0}.jsonl` (HF `axis_pv/part_c/generations/`) | `code/pc_chain.sh 1` (`pc_merge.py`, `serve.sh`, `pc_gen.py`) |
| Part C activations | `W/pc/acts.pt` (raw) | `python -I code/pc_acts.py` |
| Part C projections, differences, hypothesis | `results/axis_pv/part_c_results.json`, `part_c_tables.md`, `part_c_compact_tables.md` | `python -I code/pc_analyze.py` |
| Spend, settings | `results/axis_pv/spend.md`, `server_settings.md`, `run_summary.json` | `python -I code/summarize_run.py` |

## Counts: attempted, completed, excluded

| Item | Attempted | Completed | Excluded / notes |
|---|---|---|---|
| Axis-set generations (276 role files × 5 prompts × 20 questions) | 27,600 | 27,600 | 0 |
| Axis-set judge calls (275 roles; default not judged) | 27,500 | 27,500 scored | 0 unparsed; score 3: 24,092, 2: 1,937, 1: 1,304, 0: 167 |
| Axis-set activations | 27,600 | 27,600 (276 files) | 0 |
| Role vectors (min_count 50) | 275 | 265 | 10 roles below 50 score-3 answers (listed in Part A) |
| Validation generations (276 × 20 + default 5 × 20 + 5 styles × 20) | 5,720 | 5,720 | 0 |
| Validation judge calls | 5,500 | 5,500 scored | score 3: 5,017 (4,945 from roles with a vector) |
| Validation activations | 5,720 | 5,720 (282 files) | 0 |
| Persona extraction generations (9 traits × 2,000) + apathetic re-run at 256 | 20,000 | 20,000 | 0 |
| Persona eval-set generations (9 × 400) | 3,600 | 3,600 | 0 |
| Persona judge calls (trait + coherence) | 47,200 | 47,200 | 7 trait scores missing (REFUSAL, all evil positive) |
| Effective pairs (of 1,000) | – | apathetic 917, impolite 952, evil 67, sycophantic 990, hallucinating 582, humorous 999, optimistic 998, helpful 419, dismissive 804 | repo mask: pos ≥ 50, neg < 50, both coherence ≥ 50 |
| Eval-set activations | 3,600 | 3,600 | 0 non-finite |
| Part C generations | 600 | 600 | 0 errors |
| Part C activations | 600 own + 400 teacher-forced + 960 C3 + 20 consistency | all | 3 C3 "next 150 tokens" items empty (one story ends at its cut) |
| Failed attempts (no outputs used) | Part A generation ×3, Part B start ×1, Part C activations ×1 (crashed at the final save; rerun unchanged) | – | logs `logs/*attempt*.log` |

## Settings as the engines recorded them

Full list: [`results/axis_pv/server_settings.md`](results/axis_pv/server_settings.md) (vLLM `non-default args`, resolved architecture, SamplingParams, per log).

- **Stack:** vLLM 0.30.0, torch 2.13.0+cu130, transformers 5.17.0, PEFT 0.21.0 (`/workspace/venvs/gpu`), 2× H100 80 GB.
- **Part A (offline `LLM`, the pipeline's generator):** `max_model_len 2048`, `gpu_memory_utilization 0.95`, `max_num_seqs 256`, `language_model_only True`, `generation_config 'vllm'`, `trust_remote_code True`; resolved `Qwen3_5ForConditionalGeneration`. SamplingParams: temperature 0.7, top_p 0.9, top_k 0 (off), min_p 0, max_tokens 512, penalties neutral, seed None (the pipeline sets none). Non-thinking template (the pipeline passes `enable_thinking=False` for Qwen paths). Judge: GLM 5.3 Flash, the pipeline's temperature 1, reasoning low, max_tokens 2000, the pipeline's batch 50. Activations: HF `Qwen3_5ForCausalLM`, bf16, batch 16 (left padding), max_length 2048.
- **Part B (offline `LLM`, the repo's `load_vllm_model`):** `max_model_len 20000`, `gpu_memory_utilization 0.9`, `enable_prefix_caching True`, `max_num_seqs` 32 (apathetic) / 256 (others), `language_model_only True`, `generation_config 'vllm'`; resolved `Qwen3_5ForConditionalGeneration`. Sampling (repo `sample()`): temperature 1, top_p 1, max_tokens 1000, min_tokens 1. Judge: GLM 5.3 Flash, T 0, seed 0, reasoning low, max_tokens 3000, integer score parsed from the text (R05 patch). Vectors and eval-set activations: HF `AutoModelForCausalLM` loaded with the repo's call (no dtype argument), batch 1, `output_hidden_states` (65 states).
- **Part C servers (`vllm serve`, GPU 1, port 8101):** `dtype bfloat16`, `max_model_len 32768`, `gpu_memory_utilization 0.92`, `max_num_seqs 256`, `generation_config vllm`, `seed 20260928`, request logging on; base from the HF snapshot with `--language-model-only` (resolved `Qwen3_5ForConditionalGeneration`), merged fine-tunes from `/scratch/axis_pv/merged/<model>` (resolved `Qwen3_5ForCausalLM`). Per request (logged): temperature 1.0, top_p 1.0, top_k −1 (off), min_p 0.05, repetition/presence/frequency penalties 1.0/0/0, max_tokens 512, a seed on every request (200 requests per server). Merges: `merge_meta.json` per folder (adapter sha256 re-checked: `28dd168f…4a7e6244`, `c9b290eb…dc62`; class `Qwen3_5ForCausalLM`; 95 s each).

## Spend

| Model | Stage | Calls | Errors (after retries) | USD (OpenRouter-reported) |
|---|---|---|---|---|
| z-ai/glm-5.3-flash-20260826 | aa_judge:axis | 27500 | 0 | 1.8626 |
| z-ai/glm-5.3-flash-20260826 | aa_judge:val | 5500 | 0 | 0.3746 |
| z-ai/glm-5.3-flash-20260826 | pv:apathetic:eval | 800 | 0 | 0.0546 |
| z-ai/glm-5.3-flash-20260826 | pv:apathetic:extract | 8000 | 0 | 0.5045 |
| z-ai/glm-5.3-flash-20260826 | pv:dismissive:eval | 800 | 0 | 0.0521 |
| z-ai/glm-5.3-flash-20260826 | pv:dismissive:extract | 4000 | 0 | 0.2740 |
| z-ai/glm-5.3-flash-20260826 | pv:evil:eval | 800 | 0 | 0.0446 |
| z-ai/glm-5.3-flash-20260826 | pv:evil:extract | 4000 | 0 | 0.2219 |
| z-ai/glm-5.3-flash-20260826 | pv:hallucinating:eval | 800 | 0 | 0.0511 |
| z-ai/glm-5.3-flash-20260826 | pv:hallucinating:extract | 4000 | 0 | 0.2627 |
| z-ai/glm-5.3-flash-20260826 | pv:helpful:eval | 800 | 0 | 0.0549 |
| z-ai/glm-5.3-flash-20260826 | pv:helpful:extract | 4000 | 0 | 0.2605 |
| z-ai/glm-5.3-flash-20260826 | pv:humorous:eval | 800 | 0 | 0.0618 |
| z-ai/glm-5.3-flash-20260826 | pv:humorous:extract | 4000 | 0 | 0.3229 |
| z-ai/glm-5.3-flash-20260826 | pv:impolite:eval | 800 | 0 | 0.0430 |
| z-ai/glm-5.3-flash-20260826 | pv:impolite:extract | 4000 | 0 | 0.2319 |
| z-ai/glm-5.3-flash-20260826 | pv:optimistic:eval | 800 | 0 | 0.0546 |
| z-ai/glm-5.3-flash-20260826 | pv:optimistic:extract | 4000 | 0 | 0.2545 |
| z-ai/glm-5.3-flash-20260826 | pv:sycophantic:eval | 800 | 0 | 0.0492 |
| z-ai/glm-5.3-flash-20260826 | pv:sycophantic:extract | 4000 | 0 | 0.2511 |
| **total** | | **80200** | | **5.287** |

Key usage: first snapshot 34.3860, last 39.8921; run spend by key usage at the last snapshot: $5.506. 429/connection back-offs: 0.

The OpenRouter key started returning "API key expired" (HTTP 401) some time, when the last usage reading succeeded; the last judge call had ended and no API call was needed afterwards. The final usage could therefore not be re-read: spend is reported from the per-call ledger ($5.287, OpenRouter-reported cost per call) and from that last reading ($5.506). The $0.22 gap is not explained by this run's ledger.

## Deviations and notes

1. **GitHub auth:** `gh` is not installed; git used a credential helper reading `$GITHUB_TOKEN` (nothing stored). Checkout: `/workspace/repo` (no checkout under `/workspace/si36`).
2. **`/scratch`** did not exist; created on the container disk.
3. **`python -I` + R05's pydeps:** pipeline scripts were run unchanged through `code/pyrun.py`, which adds `smoke/pydeps` and the repo copy to `sys.path`. `PATH` must include the venv's `bin/` (flashinfer needs `ninja`); the first Part A attempts failed on these (no outputs).
4. **Extra patch** (`code/axis_pv_extra.patch`): exponential back-off on rate-limit/connection errors in both judges, and per-stage ledger tags. No back-off was ever triggered.
5. **Custom trait eval prompts:** the REFUSAL line was narrowed to safety/policy refusals (so deflections are scored, not dropped). Pre-registered in the plan.
6. **Dismissive character source:** the authors' bees/crows generation code is not in the vendored copy (`4_affinity/` empty), so the positive instructions draw on Table 7, the teammate's DISMISSIVE paraphrases and the training stories' dismissive helpers.
7. **Judge concurrency:** persona-vector judging at 200 concurrent requests for the 8 traits after apathetic (repo default 100); throughput only.
8. **evil:** the model refuses the evil instructions; the repo's pipeline was run as is and the vector is delivered, labelled not valid.
9. **Part A question indices:** the pipeline's `question_index` refers to the 20-question file; each record also carries `question_id` (the original extraction-question id). Part A validation used held-out question i with the role's prompt i mod 5 (pre-registered).
10. **Style activations vs eval activations** come from different code paths (pipeline vs persona_vectors repo); the Part C consistency check shows the axis pipeline's activations equal batch-1 HF activations to cosine ≥ 0.99999, and both use the mean over the reply tokens.
11. **C1 answers hit the 512-token cap** for the untrained model in 97 of 100 cases, so its C1 activations average over the first 512 reply tokens; the fine-tunes' answers are shorter (45–50 of 100 at the cap). Length differs between models in C1 and C2 and moves the projections (see Part C); the teacher-forced rows hold the text fixed.
12. **GPU assignment:** Part B vectors were split 5 traits on GPU 1 and 4 on GPU 0 (GPU 0 joined after Part A); Part C ran on GPU 1 as planned.
13. **Part C activations ran twice:** the first run computed everything but crashed when saving (a NaN placeholder for the one empty story tail was on CPU, the rest on GPU); the script was fixed to move each activation to CPU and rerun unchanged. 
14. **Time stamps:** the plan's for the first key-usage reading was (value correct); the status line written said.
15. **Shell mistakes:** two of my commands killed their own shell via a `pkill -f`/`pgrep -f` pattern that matched themselves; no job was affected. Nothing under `/workspace` was deleted (failed-attempt logs were renamed, not removed).

## Wrap-up

- **GitHub:** branch `replicate_qwen27B`, this file plus `results/axis_pv/` (code, patches, trait files, question split, all small results). Every push was checked with `git status -sb` against `origin/replicate_qwen27B` (no divergence).
- **Hugging Face (all verified file by file: remote size = local size, LFS sha256 = local sha256):**
  - `Same0620/si-qwen36-adapters` (model repo), `vectors/qwen3.6-27b/axis_pv/`: `axis_and_roles/axis.pt` (axis, [7, 5120], blocks 8–56), `axis_and_roles/role_vectors.pt` (265 role vectors + default), `axis_and_roles/per_role/` (the pipeline's 266 vector files), `persona_vectors/` (9 traits × response_avg / prompt_avg / prompt_last, [65, 5120]). 268 + 27 files.
  - `Same0620/si-qwen36-evals` (dataset), `axis_pv/`: `part_a/` (axis-set and validation responses and judge scores, per-item projections, question files; 1,111 files), `part_b/` (all extraction and eval CSVs with generations and judge scores, the 256 re-run, per-item eval projections; 39 files), `part_c/` (generations of all three models, per-item projections; 4 files), `logs/` and `code/` (83 files, final upload after all jobs ended; `logs/hf_uploads.jsonl` records each upload).
  - Raw activations stay on `/workspace/si36/axis_pv` (`aa/out/activations`, `aa/val/activations`, `pv/out/eval_acts`, `pc/acts.pt`).
- **Container disk:** `/scratch/axis_pv/merged/{hc_db_s0,hb_dc_s0}` deleted (disk back to 1.0 GB used).
- **Pod stop (last step):** `runpodctl stop pod cxdwib87ij4eqg` (syntax checked with `runpodctl stop pod --help`, runpodctl 1.14.15); if it returns non-zero, the GraphQL `podStop` script (`stop_pod_fallback.sh`) runs immediately. A read-only GraphQL query with the pod's key returned this pod (`desiredStatus RUNNING`), so the fallback's auth works. The outcome cannot be recorded from inside the pod. If both fail, the armed deadline and its fallback remain.

## Progress log (UTC)

- deadline armed; key usage $34.386 (the plan's for that reading is a clock slip; the value is right). plan pushed (`4cf5771`).
- pipeline copies built (`code/setup_copies.sh`): R05 patches applied cleanly; all 9 `apply_chat_template(tokenize=True)` sites carry `return_dict=False` (the other calls use `tokenize=False` and return strings). `code/axis_pv_extra.patch`: 429 back-off in both judges.
- Part A generation (GPU 0) started three times before it ran: (1) my driver ran without R05's `pydeps` on the path and would have crashed on `import jsonlines` after the model load: killed during the load; (2) the vLLM engine failed at start: `ninja` (flashinfer's kernel JIT) is in the venv's `bin/`, which was not on `PATH`; (3) relaunched by mistake with the same environment and killed within seconds. **(4): running** (vLLM load 230 s including a one-off kernel compile; first role, 100 responses in 17.7 s). No responses were written by attempts 1–3. Logs: `logs/aa_gen_attempt*.log`.
- **first-role activation check** (GPU 1, before Part B): `2_activations.py --roles aberration` → 100 activations, shape [7, 5120] each, all finite, bf16, mean norm at block 32 = 62.5 (R05 smoke: 62.0); span of the first reply = 272 tokens. `logs/aa_check_first_role.log`.
- Part A judge loop started (`code/aa_judge_loop.sh`). Part B attempt 1 failed at vLLM start (relative script path after the driver's `chdir`; nothing generated); relaunched (apathetic, max_num_seqs 32, GPU 1).
- apathetic done at max_num_seqs 32 (extract: pos 88.1 / neg 3.2 trait, coherence 74.5 / 94.6; eval: 86.4 / 3.1). Negative replies are long (mean 865 tokens, 24% at the 1000 cap): 80 generations/min at 32.
- **max_num_seqs check (pre-registered rule): the runs look the same → 256 for the other 8 traits.** apathetic extraction re-run at 256 (`W/pv/out_check256`): pos trait 88.0 vs 88.1, neg 3.0 vs 3.2; coherence 74.8 vs 74.5 and 94.7 vs 94.6; mean length 73.5 vs 73.7 and 861.7 vs 864.7 tokens; cap rate 0.0 vs 0.0 and 22.5% vs 23.8%. The apathetic vector uses the 32 run. `logs/max_num_seqs_check.json`. At 256 the long replies run ~2× faster (2,300 vs 1,150 output tokens/s). PV judge concurrency for these traits: 200 (repo default 100; a throughput setting only).
- helpful extracted (pos 94.9 / neg 5.1 trait; neg coherence mean 42: the disengaged replies are terse brush-offs, some off-topic, and the coherence judge scores many below 50, so only 419 of 1000 pairs pass the repo's coherence ≥ 50 mask). dismissive extracted (pos 93.2 / neg 0.1; 804 effective pairs; no missing scores, so the REFUSAL wording change did its job; replies read like the Table 7 persona, e.g. "Look, it's not my job to babysit your social life. … Figure it out yourselves.").
- Part A generation done (axis set 276 files; validation 282 files). Activations on GPU 0 (~13 conversations/s): axis set 276 files and validation 282 files, all complete, shape [7, 5120], finite (`logs/aa_check_acts_{out,val}.log`). Judge loop done (axis set 27,500/27,500 scored; validation 5,500).
- Part B extraction done for all 9 traits (36 CSVs). Vectors: GPU 1 (apathetic, helpful, dismissive, impolite, evil), GPU 0 (optimistic, humorous, hallucinating, sycophantic), ~5 min per trait.
- `4_vectors.py` (min_count 50: 266 vectors incl. default, 10 roles failed) and `5_axis.py`; `aa_validate.py`. Part A uploaded to HF and verified (vectors 268 files, outputs 1,111 files; two log files were still growing during the upload and are re-uploaded at the end).
- Part B vectors (5 traits on GPU 1, 4 on GPU 0) and eval-set activations (3,600, none non-finite). `pv_validate.py`; Part B uploaded to HF and verified (vectors 27 files, outputs 39 files).
- Part C on GPU 1: both merges (adapter hashes re-checked, 95 s each, 53 GB each on `/scratch`); C1/C2 generations for base, `hc_db_s0`, `hb_dc_s0`: 200 each, 0 errors. The `EngineDeadError` traceback at the end of `logs/vllm_hc_db_s0.log` is the server being stopped by the chain after all requests had returned (0 running), not a failure.
- Part C activations (first run crashed at the save step, rerun); `pc_analyze.py`. `summarize_run.py`; the OpenRouter key had expired after the last judge call (see Spend).
- Two of my shell commands killed themselves with `pkill -f`/`pgrep -f` patterns that matched their own command line; no job was affected (checked with `tmux ls` / `nvidia-smi`).

## Control

- **Deadline:** armed: `tmux new -d -s deadline "sleep 32400; for i in 1 2 3 4 5; do runpodctl stop pod cxdwib87ij4eqg && break; sleep 60; done"` (fires). GraphQL `podStop` fallback (R05's script, copied to `/workspace/si36/axis_pv/stop_pod_fallback.sh`) in tmux session `deadline_fb`, armed, fires. `tmux ls` showed `agent`, `deadline`, `deadline_fb`.
- **API budget:** $15. OpenRouter key usage at the start: **$34.386**. No new judge batch starts once usage passes **$48.886** ($0.50 guard). Usage is read before every batch (`logs/spend_checks.jsonl`); every judge call is logged with model and stage (`logs/judge_ledger_aa.jsonl`, `logs/judge_ledger_pv.jsonl`).
- **Checks:** every long job is checked for process exit at least every 5 minutes. Push to GitHub and upload to HF after each part.
- **Setup notes (before any work):**
  - The E01/R05 checkout is `/workspace/repo` (branch `replicate_qwen27B`, clean, up to date, last commit `9ef3d1b` "R05: wrap-up"); there is none under `/workspace/si36`. Used as is.
  - `gh` is not installed on this pod. Instead of `gh auth setup-git`, git uses a credential helper that reads `$GITHUB_TOKEN` from the environment at push time (nothing written to disk): `git config --global credential.https://github.com.helper '!f() { echo username=x-access-token; echo "password=$GITHUB_TOKEN"; }; f'`. `git push --dry-run` works.
  - `/scratch` did not exist; created on the container disk (overlay `/`, 150 GB free) as `/scratch/axis_pv/`.

## Layer convention

Primary layer = **block 32** (output of decoder block 32 of 64) = `model.model.layers[32]` in the axis pipeline's hooks = `hidden_states[33]` in HF `output_hidden_states` (index 0 = embeddings) = persona_vectors index 33. Every primary number is at block 32. Also saved: **blocks 8, 16, 24, 40, 48, 56** (hidden-state indices 9, 17, 25, 41, 49, 57). Layers are labelled "block N" everywhere.

## Analysis plan (pre-registered; written before any result)

### Part A (GPU 0): Assistant Axis, official pipeline, untrained model

- **Questions:** the 240 extraction questions shuffled with `random.seed(0); random.shuffle(list(range(240)))` (the teammate's convention). Held-out = shuffled[0:50] (never used to build the axis); pipeline = shuffled[50:70], written in that order to the pipeline's questions file and run with `--question_count 20`; validation and style control = held-out[0:20]. Lists: [`results/axis_pv/question_split.json`](results/axis_pv/question_split.json) (held-out ids start 65, 88, 128, 43, 213; pipeline ids start 153, 135, 19, 110, 170).
- **Axis:** all 275 roles + `default`, the pipeline's 5 system prompts each, its default generation settings (T 0.7, top_p 0.9, max_tokens 512, max_model_len 2048), GLM 5.3 Flash judge (`z-ai/glm-5.3-flash-20260826`, reasoning low, `--max_tokens 2000`), default `--min_count 50` (a role needs ≥ 50 of its 100 responses scored 3). Mean response activations at the 7 saved blocks (`2_activations.py --layers 8,16,24,32,40,48,56`). Axis = mean(default) − mean(role vectors), per block (`5_axis.py`); it points toward the default Assistant. Roles that fail min_count are excluded from the axis and counted.
- **Projection** (everywhere): p = a · axis_b / ‖axis_b‖ at block b. Higher = closer to the default-Assistant end.
- **Validation set:** 20 held-out questions × (default + all 275 roles) × 1 sample each, generated with the pipeline's own generator and settings. The system prompt for question i (0–19) is the role's prompt i mod 5, so each of the 5 prompts is used 4 times per role. Role responses are judged with the role's eval prompt (same judge). Activations with the pipeline's `2_activations.py`. Supplementary: `default` under all 5 prompts × 20 questions (100 responses).
- **Validation metrics (block 32 primary, all saved blocks reported):**
  1. **Held-out AUC**: default (20 held-out responses) vs held-out role responses scored 3, from roles that have a vector (this is the teammate's `axis_build.py` definition). Secondary: vs all held-out role responses (no score filter); and the supplementary 100-response default set.
  2. **Stability (cosine)**: (a) role halves: roles with a vector permuted with `np.random.default_rng(0)`, axis from the first half vs the second half (same default vector); (b) system-prompt halves: the 5 prompt indices permuted with `np.random.default_rng(0)`, first 2 vs last 3; in each half the role vectors and the default vector are rebuilt from that half's responses only, min_count scaled to the half (20 and 30). Also reported: the teammate's fixed split {0,1} vs {2,3,4}, and the distribution over 100 random role and prompt splits (seeds 1–100).
  3. **|cos(axis, PC1)|**: PC1 of the centred role vectors (roles with a vector) at each block.
  4. **Style control**: the teammate's 5 style prompts (florid, theatrical, formal, fictional, terse), copied verbatim from `si/code/axis_generate.py` (pilot @ 879cc79), on the same 20 held-out questions, 1 sample each, pipeline generator and settings. Style fraction = (mean p(style) − mean p(default)) / (mean p(score-3 role) − mean p(default)), means over the held-out sets (his `axis_build.py` formula): 0 = default level, 1 = role-play level.
- **Reading (pre-registered):** the axis is **valid** if held-out AUC ≥ 0.80 at block 32 **and** florid and theatrical each sit at < 0.5 of the gap at block 32. Otherwise it is labelled **"style-confounded"** (and still delivered).

### Part B (GPU 1; GPU 0 joins after Part A): persona vectors, untrained model

- **Traits (9):** apathetic, impolite, evil, sycophantic, hallucinating, humorous, optimistic (repo data, `data_generation/trait_data_{extract,eval}/`), and two custom traits, **helpful** and **dismissive** ([`results/axis_pv/trait_data/`](results/axis_pv/trait_data/), written and pushed in this commit, before any generation).
  - Custom files follow the repo format (5 pos/neg instruction pairs, 20 extraction questions, 20 different eval questions, an `eval_prompt` in the repo's wording). Both custom traits use the same 20 extraction and 20 eval questions (everyday advice requests; none about family dinners, barbecues, bathroom tiles, Rome or a puppy's diet).
  - **Dismissive:** positive instructions built from the Table 7 prompt, the teammate's DISMISSIVE paraphrases and the dismissive helpers in the training stories (brusque, curt, "I'm not your babysitter"); negative = engaged and helpful. The authors' bees/crows generation code is not in the vendored copy (`si/repos/story-imprinting/4_affinity/` is empty; only the training stories show the character), so the stories were used.
  - **Helpful:** positive = engaged, substantive, warm helper; negative = disengaged and unhelpful (without the "wants to leave / redirects elsewhere" cues that define dismissive).
  - **One wording change for the two custom eval prompts:** the repo's line "REFUSAL if the model clearly refused to answer" would turn deflections (the dismissive positive and the helpful negative) into missing scores, which drops the pair. The custom prompts say "REFUSAL if the model clearly refused to answer for safety or policy reasons (a brush-off, deflection or unhelpful reply is not a refusal: score it)". The 7 repo traits are unchanged.
- **Assistant names** ("You are a/an [name] assistant." before each instruction; README rule: trait adjective for pos, antonym if clear else "helpful" for neg): apathetic/empathetic, impolite/polite, evil/helpful (the README's example), sycophantic/honest, hallucinating/honest, humorous/serious (R05 smoke), optimistic/pessimistic, helpful/unhelpful, dismissive/engaged.
- **Extraction at repo defaults:** `eval.eval_persona` (version `extract`, 20 questions × 5 pairs × 10 samples, T 1, max_tokens 1000) pos and neg; judge GLM 5.3 Flash with R05's patch (integer score from the text answer, not logprob-weighted; see FOLLOWUP.md); `generate_vec.py --threshold 50`. **Primary vector: `response_avg_diff`**, index 33 = block 32.
- **max_num_seqs:** the first trait (apathetic) runs at the repo's 32. It is then re-run at 256 into a separate folder. The rest use 256 if the two runs "look the same", defined in advance as: pos and neg mean trait scores within 5 points, mean coherence within 5 points, mean response length within 10%, cap rate within 5 points. Otherwise all traits stay at 32. The apathetic vector always comes from the 32 run. Recorded either way.
- **Validation per trait (block 32):** pos and neg mean trait scores (all scored extraction responses; also effective-only), effective pairs (of 1000), and the **AUC of pos vs neg projections** on the trait's eval questions: `eval.eval_persona` with version `eval`, pos and neg instructions, 20 eval questions × 5 pairs × 2 samples = 200 + 200 (T 1; also judged, so eval-set trait means are reported too). Activations = mean over response tokens at the saved blocks, computed with the repo's own `get_hidden_p_and_r` (imported from `generate_vec.py`). Projection p = a · v_b / ‖v_b‖.
- **Style sets onto every vector:** Part A's 5 style sets and its 20 default held-out responses (pipeline activations, same blocks) projected onto all 9 vectors. Reported raw, and as (mean p(style) − mean p(default)) / (mean p(eval pos) − mean p(eval neg)): 0 = like the default Assistant, 1 = a full pos−neg shift toward the trait. Also cosines between the 9 vectors and with the axis.
- **Reading (pre-registered):** a vector is **valid** if pos − neg mean trait score ≥ 40 (extraction set, all scored responses) **and** the eval AUC ≥ 0.80 at block 32. All nine are reported either way.

### Part C (GPU 1, after its traits): untrained model and E01's two fine-tunes (exploratory, descriptive, no verdict rules)

- **Models:** untrained `Qwen/Qwen3.6-27B` @ 6a9e13bd; `hc_db_s0` (helpful → crows, dismissive → bees) and `hb_dc_s0` (the swap), adapters `/workspace/si36/ckpt/<model>/final`, sha256 checked first (`hb_dc_s0` c9b290eb…dc62, `hc_db_s0` 28dd168f…4a7e6244).
- **Activations:** HF transformers, base + PEFT adapter with the adapter off (untrained) / on (fine-tune), as in R05's `code/fixed_stats_merge.py`; `output_hidden_states`, the 7 saved blocks.
- **Generation:** each adapter merged on the GPU to `/scratch/axis_pv/merged/<model>` (R05's merge code, hash check first) and served with vLLM as in R05 (`--generation-config vllm --max-num-seqs 256 --seed 20260928`; untrained served from the HF snapshot with `--language-model-only`). Non-thinking template.
- **C1 default Assistant:** the 50 held-out questions, no system prompt, T 1 + min_p 0.05 (top_p 1, top_k off), 2 samples each (seeded), max 512 tokens, each model answering itself. Activation = mean over its reply tokens (the generated text, without `<|im_end|>`). Also **teacher-forced**: the untrained model's C1 replies fed through each fine-tune (fixed-text comparison).
- **C2 dismissive prompt:** the same, with the Table 7 prompt (verbatim, as given in the brief) as the system prompt; teacher-forced comparison likewise.
- **C3 story characters:** R05's 160 story prefixes (`results/followup_R05/story_selection.json`: 40 helpful + 40 dismissive per training file, cut at the end of the paragraph holding the "don't do X" line). Each is wrapped as the training row: chat template of the row's user message (generation prompt, non-thinking) + the prefix as the start of the assistant turn, tokenized as one string (as in R05's continuations). **Primary:** the activation at the last token of the prefix. **Secondary:** the mean over the next 150 tokens of the training story (the story text after the cut, tokenized separately and appended; teacher-forced). All three models on all 160 prefixes; a fine-tune's own file is reported first.
- **Reported per model × input set:** mean projection onto the axis and each of the 9 persona vectors at block 32 (and the other saved blocks), with bootstrap 95% percentile intervals over prompts (2000 resamples, `np.random.default_rng(0)`; unit = question for C1/C2, with its 2 samples averaged; prefix for C3); differences fine-tune − untrained (paired over prompts; for self-generated text the pairing is by question); in C3, helpful − dismissive character. Every Part C number is labelled **"exploratory"**.
- **One hypothesis stated in advance (the paper's):** in the untrained model, helpful characters project closer to the default-Assistant end of the axis than dismissive characters (C3 primary, block 32): helpful − dismissive > 0. Reported as the difference with its 95% interval (pooled over both files, 80 vs 80; per file as well).

## Concrete plan per part (scripts, commands, paths, GPU, expected time)

Work dir `W=/workspace/si36/axis_pv` (raw activations stay here). All Python runs as `/workspace/venvs/gpu/bin/python -I`; because `-I` ignores `PYTHONPATH`, a small runner `code/pyrun.py` puts R05's `smoke/pydeps` (jsonlines, fire, termcolor) and the repo copy on `sys.path` and then runs the pipeline script unchanged. Code is copied to `results/axis_pv/code/` at each push.

**Pipeline copies** (`code/setup_copies.sh`): `W/aa/repo` = `/workspace/ref/assistant-axis` @ a989619 + R05 `assistant_axis.patch.v2.raw`; `W/pv/repo` = `/workspace/ref/persona_vectors` @ b8e0f04 + R05 `persona_vectors.patch` + the two custom trait files. One extra patch, `code/axis_pv_extra.patch`, adds only: exponential back-off on HTTP 429 / rate-limit errors in both judges (so two pipelines judging at once back off rather than fail), and the ledger tag per stage. Before any long run: after the first role, check that its activation file is non-empty, has the expected shape [7, 5120] per conversation and has no NaN.

| Step | GPU | Script / command | Output | Expected time |
|---|---|---|---|---|
| A1 generate | 0 | `code/aa_gen_all.py` (one vLLM load; the pipeline's `RoleResponseGenerator` with `--question_count 20` on `aa/questions_pipeline20.jsonl`, all 276 role files; then the validation set, the 100-response default supplement and the 5 style sets through the same `VLLMGenerator`) | `W/aa/out/responses/*.jsonl` (27,600), `W/aa/val/responses/*.jsonl` (5,520 + 100 + 100 = 5,720) | ~1 h 45 min (≈ 330 generations/min, R05 smoke) |
| A3 judge | API | `pipeline/3_judge.py --judge_model z-ai/glm-5.3-flash-20260826 --max_tokens 2000` (default batch 50), looped every ~10 min while A1 runs (files appear only when a role is complete), then a retry pass | `W/aa/out/scores`, `W/aa/val/scores` | in parallel; ≈ 33,000 calls ≈ $3.3 |
| A2 activations | 0 | `pipeline/2_activations.py --layers 8,16,24,32,40,48,56 --batch_size 16` on both response folders | `W/aa/out/activations/*.pt`, `W/aa/val/activations/*.pt` | ~80 min (≈ 7 conversations/s) |
| A4 vectors, axis | CPU | `pipeline/4_vectors.py` (min_count 50), `pipeline/5_axis.py` | `W/aa/out/vectors`, `W/aa/out/axis.pt` | minutes |
| A5 validation | CPU | `code/aa_validate.py` | `results/axis_pv/part_a_*.json/md` | minutes |
| B1 generate + judge | 1 | `code/pv_extract_all.py` (one vLLM load; the repo's `eval.eval_persona.main` for each trait: extract pos, extract neg, eval pos, eval neg; apathetic first at max_num_seqs 32, then the 256 check) | `W/pv/out/extract/<trait>_{pos,neg}_instruct.csv`, `W/pv/out/eval/...` | apathetic ~45 min at 32 + ~10 min check; then ~10–12 min per trait at 256 (~1.5 h) |
| B2 vectors + eval activations | 1 (+0 after A) | `generate_vec.py` per trait (repo, threshold 50); `code/pv_eval_acts.py` (eval-set activations at the saved blocks) | `W/pv/out/vectors/<trait>_*.pt`, `W/pv/out/eval_acts/` | ~8 min per trait |
| B3 validation | CPU | `code/pv_validate.py` | `results/axis_pv/part_b_*.json/md` | minutes |
| C0 merge | 1 | `code/pc_merge.py --model <m>` (hash check, `merge_and_unload`) | `/scratch/axis_pv/merged/<m>` | ~3 min each |
| C1/C2 generate | 1 | `code/serve.sh <dir> <port> <gpu>` + `code/pc_gen.py --model <m>` | `W/pc/gen_<m>.jsonl` | ~6 min per model |
| C activations | 1 | `code/pc_acts.py --model <m>` (base + PEFT, adapter off/on; C1, C2, teacher-forced, C3) | `W/pc/acts_<m>.pt` | ~10 min per model |
| C analysis | CPU | `code/pc_analyze.py` | `results/axis_pv/part_c_*.json/md` | minutes |
| Wrap-up | – | `code/upload_axis_pv.py` (HF, verified), push, delete `/scratch/axis_pv/merged`, stop pod | | |

Expected end of GPU work, well before the deadline. If time runs short, the order of what gets cut is: Part B traits (in reverse of the list), then the Part C secondary measures.

**Hugging Face:** vectors (axis per saved block, role vectors, all nine persona vectors) → `Same0620/si-qwen36-adapters` under `vectors/qwen3.6-27b/axis_pv/`; generations, judge scores and per-item projections → `Same0620/si-qwen36-evals` under `axis_pv/`. Raw activations stay on `/workspace/si36/axis_pv`. Every push and upload is verified.
