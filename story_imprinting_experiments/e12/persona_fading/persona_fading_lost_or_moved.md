# Persona fading: lost or moved? (CPU analysis of saved block-32 states)

*. Written by an agent for the researcher. The researcher approved the test with no prediction. CPU only, no GPU or API. Code and results are in this folder:*
- `persona_fading_lost_or_moved.py`: Part 1 decoding and transfer (rules 1 and 3); rule 2 at turn 3.
- `persona_fading_lost_or_moved_part2.py`: Part 2, 271 persona means (rule 2; rule-3 identification).
- `persona_fading_lost_or_moved_ratios.py`: paired bootstrap CIs on d′ ratios.
- `persona_fading_lost_or_moved.json`: all numbers below.

## Bottom line

**Persona information is mostly moved, not lost.** There is some real loss in the system-prompt part.
- **Within each trained model, personas stay perfectly decodable (100%).** Their separation relative to script-to-script noise keeps a median of 0.71–0.80 of the parent's (S, SB, C) and 0.96 (Q). If the information were lost in proportion to fading, it would keep only 0.41–0.56.
- **Separation tracks the share of the gap's norm that is kept (ρ), not the share of its projection that is kept (1 − α).**
- **The system-prompt part loses about half of what fading predicts.** Within-model separation is 0.60–0.70 in S/SB/C against a predicted 0.26–0.29. The history part loses nothing.
- **The parent's decoder transfers worse than each model's own decoder.** Most of that is a persona-independent shift: removing a label-free mean offset restores 100%.
- **The new components are mostly shared.** By the pre-stated rule they are one common direction in every model. Caveat: the replay model R also has this shared component, and R does not fade at turn 1, so the shared component is not specific to fading.

## 0. What was checked first (project rule 11) and the data

**Teammate's newest work**
- **`sprint_work`:** head is still `7ccd4b0`, the commit the dossier checked today. I listed its tree via `gh api` and searched the file paths for fading, decoding and probe terms; code search is blocked for this session. No path points to persona-identity decoding or a fading analysis. The nearest, `008_habit_likelihood_probe`, asks a different question. I did not read file contents beyond what the dossier read.
- **His HF `senku21x/*` repos:** HF is blocked from this machine (`CONNECT tunnel failed, response 403`), so I could not recheck them. The dossier found nothing on fading there.
- **How this run differs:** there is no teammate analysis of this question, so there is nothing to compare against. I used only our own E05/E09 states.
- **Old pilot repo:** I did not use its main branch. I used the results branches `e05_conditional` and `e09_persona_replay`, as the task specified.

**Data used**

| Source | Contents | Check |
|---|---|---|
| `origin/e05_conditional` @ `d150ac9b`, `e05/r05/push_states/` | `part1_states_b32_{parent,S,SB,Q,C,R}.pt`: float16 [700, 5120]. Block 32, turn 3, last prompt token. P00 ×100; P01/P02/P05 × with/without system prompt × trigger on/off × 50 scripts. `part2_mean_states_b32_*.pt`: [271, 5120], each row the mean over 20 scripts (turn 1). | All 14 sha256 match `e05/r05/logs/push_states_sha256.txt`. Real blobs, not LFS pointers. My loader reproduces R05 §1's α and ρ in all 30 Part-1 cells to 3 decimals (e.g. S P01 off: α 0.390, ρ 0.863). |
| `origin/e09_persona_replay` @ `7a6614e6`, `e09/r01/push_states/` | The same layout plus P04, 900 rows. Models parent, S, R, `RD`, `RD3`. | Its parent/S/R Part-2 means are byte-identical blobs to E05's. Its Part-1 rows agree with E05's within 1.6% row-relative difference. |

**What is missing.** R05 saved more on the pod volume (`/workspace/e05/r05/states/`; R05 README, "Files"):
- blocks 8, 16 and 24;
- Part 2 per-script states (271 × 20 × 2 blocks).

These were never pushed, and the README lists no HF copy. So:
1. **Block 32 only.** The "other layers" part of the brief cannot be done.
2. **The 271-persona test uses means only.** Within-model cross-validated decoding of 271 personas is impossible. Within-model decoding is done on Part 1 (4 personas, or 5 with E09).

## 1. Methods (fixed before results)

**Decoders**
- **Split:** leave-one-script-out, 50 folds, so no script and no user question is ever in both train and test.
- **Robustness check:** leave-one-topic-family-out (5 families).
- **Pipeline:** StandardScaler, then PCA to min(100, n_train − 1) fitted on the training fold, then multinomial logistic regression (C = 1).
- **Accuracy CIs:** Wilson 95% over test prompts, plus a script-cluster bootstrap (2,000 resamples).

**Tasks (Part 1)**

| Task | Classes | Isolates |
|---|---|---|
| `id4` | P00/P01/P02/P05, with system prompt | full persona identity |
| `id5` (E09) | adds P04 | full persona identity |
| `sys_P` | with vs without system prompt, same persona and script | the system-prompt part σ (the part that fades most) |
| `hist3` | P01/P02/P05, without system prompt | the history part η |

Each task is run with the trigger off, on, and both pooled.

**Rule 3 (transfer):** the decoder is fitted on the parent's training scripts and applied to the trained model's test scripts. It is run in two forms:
- **raw:** the trained model's states as they are;
- **offset removed:** subtracting the mean (model − parent) state over all training-script prompts, pooled over classes. This uses no labels.

**Added beyond the brief (because accuracy was expected near ceiling)**
- **Held-out d′ for every class pair.** Two versions: (a) the class-mean-difference direction in raw space; (b) shrinkage LDA (Ledoit–Wolf) in the fold's PCA space. Both are computed on out-of-fold scores.
- **The pair's fading share:** α_pair = 1 − Σ⟨D_m, D_p⟩ ÷ Σ‖D_p‖² with D = h(a) − h(b) per script. This is R05's α generalised to any pair; α_pair for P00 vs P equals R05's α for P.
- **The "lost" prediction for a d′ ratio** is 1 − α_pair; the "moved" prediction is 1.
- **Paired CIs on the ratios:** model and parent share the same script resamples (1,000).
- I added the paired-CI run after seeing the point estimates and before writing any verdict. It only adds intervals.

**Rule 2**
- **Change per persona r:** s_r = g_m,r − g_p,r, where g = state(r) − state(P00). This equals (trained − parent mean state) minus the default's change.
- **Non-fading component:** n_r = s_r minus its projection on g_p,r.
- **Primary measure:** the uncentred top-PC share of Σ‖n_r‖². Centred PCA would subtract exactly the common shift the question asks about, so it is reported only as secondary.
- **Also reported:** the share explained by the mean vector, cos(n_r, mean n), and a split of every gap into a common part (mean over personas) and a persona-specific part.
- **Main analysis on Part 2** (270 non-default personas; persona bootstrap, 500 resamples). Repeated at turn 3 on Part 1 (3 personas, script bootstrap).

## 2. Rule 1: within-model decoding

**Table 1. Within-model accuracy (block 32).** "If lost" is the lowest accuracy a Gaussian model predicts in that task if separation shrank to 1 − α_pair of the parent's.

| Task (turn 3) | n test prompts per model | Accuracy in **every** model (parent, S, SB, Q, C, R; E09 rows also RD, RD3) | Wilson 95% | Topic-family split | Parent held-out d′ (LDA), range over pairs | Lowest accuracy "if lost" |
|---|---|---|---|---|---|---|
| `id4`, off / on | 200 | 100% / 100% | [98.1, 100] | 100% / 100% | 8.9–50.0 / 10.8–49.0 | 99.0% / 95.4% |
| `id5` (E09), off / on | 250 | 100% / 100% | [98.5, 100] | 100% / 100% | 10.2–53.0 / 12.0–50.8 | – |
| `sys_P01`, off / on | 100 | 100% / 100% | [96.3, 100] | – | 17.5 / 20.8 | 97.6% / 99.7% |
| `sys_P02`, off / on | 100 | 100% / 100% | [96.3, 100] | – | 8.6 / 9.8 | 92.3% / 88.4% |
| `sys_P05`, off / on | 100 | 100% / 100% | [96.3, 100] | – | 11.3 / 15.6 | 92.1% / 94.1% |
| `hist3`, off / on | 150 | 100% / 100% | [97.5, 100] | – | 7.8–26.9 / 8.8–25.0 | 99.0% / 96.2% |

Pooling both trigger states gives the same result: 100% everywhere.

**Table 2. Held-out separation, d′ ratio (model ÷ parent), E05.**
- Each cell is the median over 6 cells (3 pairs × trigger off/on) of the LDA d′ ratio.
- Columns per model: within-model ratio / transfer ratio / "lost" prediction 1 − α_pair / lost fraction.
- Lost fraction = (1 − within ratio) ÷ α_pair. 0 = moved; 1 = lost in proportion to fading.

| Group | S | SB | Q | C | R |
|---|---|---|---|---|---|
| default vs persona (`id4`) | 0.72 / 0.73 / 0.52 / 0.55 | 0.63 / 0.66 / 0.42 / 0.69 | 0.98 / 0.86 / 0.56 / 0.05 | 0.73 / 0.72 / 0.47 / 0.46 | 1.05 / 0.93 / 0.85 / −0.29 |
| persona vs persona (`id4`) | 0.75 / 0.69 / 0.58 / 0.66 | 0.77 / 0.60 / 0.51 / 0.48 | 0.65 / 0.67 / 0.62 / 0.88 | 0.78 / 0.56 / 0.53 / 0.51 | 0.96 / 0.88 / 0.88 / 0.32 |
| system prompt only (`sys`) | 0.70 / 0.59 / 0.29 / 0.44 | 0.60 / 0.51 / 0.26 / 0.61 | 0.95 / 0.85 / 0.41 / 0.11 | 0.65 / 0.63 / 0.27 / 0.47 | 0.95 / 0.90 / 0.75 / 0.26 |
| history only (`hist3`) | 1.33 / 0.75 / 0.51 / −0.67 | 0.95 / 0.69 / 0.44 / 0.03 | 1.12 / 0.75 / 0.55 / −0.29 | 1.18 / 0.71 / 0.44 / −0.33 | 1.03 / 0.76 / 0.79 / −0.35 |

**Table 3. All 24 cells per model (12 pairs × 2 trigger states), LDA d′, paired 95% CIs.**

| Model | Median within ratio | Median 1 − α_pair ("lost") | Median ρ_pair | CI above "lost" prediction | CI below 1 | Median lost fraction |
|---|---|---|---|---|---|---|
| S | 0.79 | 0.52 | 0.80 | 23/24 | 14/24 | 0.40 |
| SB | 0.71 | 0.44 | 0.74 | 22/24 | 17/24 | 0.49 |
| Q | 0.96 | 0.56 | 0.72 | 21/24 | 9/24 | 0.09 |
| C | 0.80 | 0.41 | 0.72 | 24/24 | 15/24 | 0.43 |
| R | 0.99 | 0.82 | 0.95 | 19/24 | 5/24 | −0.07 |

- **Mean-difference d′ (instead of LDA):** median within ratio is 0.97 / 0.87 / 1.01 / 0.86 / 1.03; median lost fraction is 0.04 / 0.23 / −0.02 / 0.22 / −0.17.
- **Precision:** a single d′ has a ±15–25% CI, so single cells are imprecise. Per-cell values are in the JSON (`part1_dprime_ratios_paired_boot`).
- **One odd pair:** P00 vs P01 (dismissive) separation rises in S, SB and C (within ratio 1.33–1.47, both trigger states) and in Q with the trigger off (1.23; with it on, 1.01 [0.86, 1.20]). This happens although P01's gap fades 31–60%.
- **E09 (no paired CIs):** RD keeps 1.10 (default vs persona) and 1.01 (persona vs persona) of the parent's within-model LDA d′ (trigger off). RD3 keeps 1.22 and 0.86.

**Verdict, rule 1, as written: MOVED. Strength: weak for the rule itself, moderate for "not lost in proportion to fading".**
- **The rule as written:** every trained model decodes persona identity, the system-prompt part and the history part at 100%, the parent's accuracy. That is within 5 points, so by the rule the information MOVED.
- **Why the rule is weak here:** the parent's held-out d′ is 7.8–53, so even proportional loss would predict 88–100% accuracy (Gaussian approximation; Table 1). The test can barely separate the two hypotheses.
- **The continuous measure:** within-model separation keeps 0.71–0.80 (S, SB, C) and 0.96 (Q) of the parent's. Proportional loss predicts 0.41–0.56. The CI lies above that prediction in 21–24 of 24 cells per story model.
- **But not fully moved:** the CI lies below 1 in 9–17 of 24 cells. Roughly 10–50% of the loss implied by fading is real (median lost fraction 0.09–0.49).
- **Where the loss is:** it sits in the system-prompt part (within ratio 0.60–0.70 in S/SB/C; Q 0.95). The history part shows no loss (0.95–1.33).
- **Summary:** separation follows ρ (the norm kept), not 1 − α.

## 3. Rule 2: shared or persona-specific change?

**Table 4. Part 2 (turn 1, 270 non-default personas, block 32).** Persona bootstrap 95% in brackets.

| Model | Median α_r (from means)¹ | Non-fading share of ‖s‖² | **Top-1 PC share of non-fading, uncentred** | Top-3 / top-10 (uncentred) | Top-1 centred | Mean-vector share | Median cos(n_r, mean n) [IQR] | cos(mean n, default drift d) |
|---|---|---|---|---|---|---|---|---|
| S | 0.55 | 0.56 | **0.63** [0.62, 0.65] | 0.74 / 0.85 | 0.26 | 0.61 | 0.81 [0.75, 0.85] | −0.17 |
| SB | 0.56 | 0.61 | **0.59** [0.58, 0.61] | 0.74 / 0.83 | 0.21 | 0.57 | 0.78 [0.73, 0.82] | −0.14 |
| Q | 0.60 | 0.33 | **0.72** [0.71, 0.74] | 0.81 / 0.89 | 0.31 | 0.69 | 0.86 [0.81, 0.89] | −0.05 |
| C | 0.50 | 0.59 | **0.63** [0.61, 0.65] | 0.74 / 0.85 | 0.27 | 0.60 | 0.81 [0.75, 0.85] | −0.13 |
| R | 0.00 | 0.98 | **0.57** [0.56, 0.59] | 0.69 / 0.80 | 0.20 | 0.56 | 0.77 [0.72, 0.81] | −0.35 |
| RD | 0.19 | 0.95 | **0.89** [0.89, 0.90] | 0.93 / 0.96 | 0.21 | 0.89 | 0.95 [0.94, 0.96] | −0.86 |
| RD3 | 0.24 | 0.90 | **0.64** [0.63, 0.66] | 0.75 / 0.84 | 0.22 | 0.63 | 0.81 [0.76, 0.85] | −0.55 |

¹ My α_r is fitted on means, so its medians run about 0.04–0.06 below R05's per-script pooled medians (0.60 / 0.61 / 0.66 / 0.56 / 0.04; R05 README §5a).

**Table 5. Common versus persona-specific part of the gaps.** The common part is the mean over personas; it holds 60% of the parent's gap energy at turn 1 (63% at turn 3).

| Model | Turn 1: α_common / ρ_common | Turn 1: α_specific / ρ_specific | Turn 1: pairwise-distance Spearman (model vs parent) | Turn 3, trigger off: α_common / α_specific / ρ_specific | Turn 3, off: mean-vector share of non-fading [95%] |
|---|---|---|---|---|---|
| S | 0.55 / 0.76 | 0.53 / 0.77 | 0.81 | 0.46 / 0.38 / 0.89 | 0.54 [0.52, 0.56] |
| SB | 0.54 / 0.82 | 0.56 / 0.85 | 0.63 | 0.51 / 0.42 / 0.85 | 0.52 [0.51, 0.55] |
| Q | 0.56 / 0.63 | 0.64 / **0.51** | 0.90 | 0.35 / 0.32 / 0.83 | 0.55 [0.53, 0.57] |
| C | 0.49 / 0.78 | 0.49 / 0.79 | 0.84 | 0.47 / 0.39 / 0.86 | 0.54 [0.52, 0.56] |
| R | −0.02 / 1.09 | 0.07 / 1.03 | 0.94 | 0.09 / 0.08 / 0.99 | 0.52 [0.51, 0.54] |

**Further observations**
- **The shared direction is nearly orthogonal to the parent's mean persona gap:** |cos| ≤ 0.08 in every model.
- **It differs between models.** Cosines of the mean non-fading vectors: S–C 0.82, S–SB 0.61, SB–C 0.64, S–Q 0.47, SB–Q 0.26, story models vs R 0.19–0.25.
- **The mean of the full change s points against the mean parent gap** (cos −0.62 to −0.78 in S/SB/Q/C). That is the fading of the common part.
- **At turn 3 (3 personas, trigger off),** the non-fading components agree less:
  - cosines with their mean: P01 0.88–0.91, P02 0.53–0.60, P05 0.65–0.75;
  - pairwise cosines: 0.14–0.49;
  - the mean-vector share is 0.52–0.55, against a floor of 1/3 for orthogonal vectors.
- **Noise check:** the expected sampling error of a 20-script mean is 2–3 units at turn 3 (default drift and persona change, S/SB/Q/C), against ‖mean n‖ = 9–14 at turn 1. Script noise therefore cannot create the shared component. This is a rough reference only, since it was taken at a different turn.

**Verdict, rule 2: SHARED. Strength: moderate.**
- **By the rule:** the top PC carries 59–72% of the non-fading variance in S, SB, Q and C (CIs 0.58–0.74, all ≥ 50%). The median persona's non-fading component has cosine 0.78–0.86 with the mean.
- **R also passes the rule (0.57), and R does not fade at turn 1.** RD/RD3 pass as well (0.89 / 0.64). So "a common shift" is a general feature of how trained models move system-prompted personas relative to the default; it is not a signature of fading.
- **Equivalent description:** P00 has no system prompt, so the shared component can also be read as the default moving differently from every system-prompted persona.
- **The persona-specific remainder** is 31–43% of the non-fading energy (S/SB/Q/C), spread thinly (centred top-1 only 0.20–0.31).
- **Fading itself is not only a common shrink.** The persona-specific parts fade along their own directions about as much as the common part (α_specific 0.49–0.64 vs α_common 0.49–0.56 at turn 1).
- **Q at turn 1:** the persona-to-persona spread nearly halves in norm (ρ_specific 0.51), but its arrangement is kept (Spearman 0.90). Only 33% of Q's change is non-fading, against 56–61% in S/SB/C. So at turn 1, Q's fading is mostly shrinkage. Whether that costs decodability cannot be tested from means.
- **At turn 3 the sharing is weaker** (mean-vector share 0.52–0.55 with 3 personas).

## 4. Rule 3: does the parent's decoder transfer?

**Accuracy (Part 1).** The parent-trained decoder on trained-model states:
- **No drop** in 73 of 99 trained-model × task × trigger cells. This includes every cell for R (21), RD (6) and RD3 (6).
- **Drops in 26 cells, all in S, SB, Q or C** (E05 S/SB/Q/C and E09's S). The lowest:
  - `hist3` on: SB 82.7% [75.8, 87.9], C 83.3%;
  - `hist3` pooled: C 86.7%, SB 87.3%;
  - `sys_P05` pooled, C: 89.0%;
  - `id4` pooled, C: 91.0% [87.8, 93.4];
  - `sys_P02` on, SB: 93.0%.
- **Removing the label-free mean offset restores 100% in every cell,** including the topic-family split. Within-model accuracy is 100% throughout.

**Separation (d′ does not change under a common shift).** Within-model vs transfer LDA ratio, medians over 24 cells:

| Model | Within | Transfer |
|---|---|---|
| S | 0.79 | 0.69 |
| SB | 0.71 | 0.63 |
| Q | 0.96 | 0.83 |
| C | 0.80 | 0.70 |
| R | 0.99 | 0.89 |

- **The history part shows the gap most clearly:** within 0.95–1.33, transfer 0.69–0.75 (Table 2). R shows the same pattern (1.03 vs 0.76), so re-encoding the history part is not specific to fading either.

**Table 6. Identification of the 270 personas by the parent's means** (Part 2, nearest centroid, cosine, Wilson 95%).

| Model | Gaps (default-subtracted) | Gaps, mean over personas removed | Raw states | Euclidean, mean removed |
|---|---|---|---|---|
| S | 79.3% [74.0, 83.7] | 93.3% [89.7, 95.7] | 63.7% | 73.0% |
| SB | 69.6% [63.9, 74.8] | 90.0% [85.8, 93.0] | 60.4% | 61.5% |
| Q | 75.6% [70.1, 80.3] | 96.7% [93.8, 98.2] | 30.4% | 39.3% |
| C | 84.4% [79.6, 88.3] | 97.0% [94.3, 98.5] | 67.8% | 80.4% |
| R | 98.5% [96.3, 99.4] | 99.6% [97.9, 99.9] | 97.8% | 99.6% |
| RD | 93.3% | 97.8% | 95.2% | 98.1% |
| RD3 | 77.0% | 94.1% | 77.0% | 88.9% |

The within-model counterpart of Table 6 cannot be computed, because there are no per-script Part 2 states.

**Verdict, rule 3: MOVED (re-encoded), not lost. Strength: moderate.**
- **The rule's signature appears:** the parent-trained decoder loses accuracy (down to 82.7%) and separation (transfer d′ 0.63–0.83 of the parent's, against 0.71–0.96 within), while within-model accuracy stays at 100%.
- **Most of the transfer failure is the shared shift of §3.** A label-free offset removal restores 100%. On the 270 personas, removing the mean over personas raises identification from 70–84% to 90–97%.
- **A smaller, persona-specific re-encoding remains:** transfer d′ stays below within-model d′, most clearly for the history part.
- **It is not clean "drop in both":** within-model separation does fall somewhat (rule 1), but far less than transfer would suggest.

## 5. Caveats

- **Block 32 only.** Turn 3 has only 3–5 personas with per-script states; at turn 1 there are only means.
- **Ceiling.** Accuracy cannot move, so the separation conclusions rest on d′. d′ assumes roughly Gaussian scores, and each estimate is ±15–25%.
- **One training seed per model.** SB and Q also differ in schedule and story writer (dossier §2).
- **Story labels and behaviour were not used here.** "Moved" means linearly decodable at block 32. It does not mean the model uses the re-encoded information.
- **Exp. A prediction (written by the dossier agent, not the researcher):**
  - Within-model ≥ 0.95: holds.
  - Parent's probe ≥ 0.9: holds for the with/without-system-prompt tasks at each trigger state (min 93.0%). It fails for one pooled-trigger cell (C, P05: 89.0%) and for `hist3` (82.7% / 83.3%).
  - Parent's probe margin falls 40–50% in S/SB/Q/C, ≤ 20% in R: transfer LDA d′ fell 41% (S), 49% (SB), 37% (C), 15% (Q) and 10% (R). Q is the miss. (These are d′ ratios, not raw margins.)
  - 271-way top-1 ≥ 0.9: fails without mean removal (70–84%); holds with it (90–97%).

## 6. What would make this stronger

1. **Re-extract Part 2 per-script states at blocks 24 and 32** (R05's code; its Part 2 passes took 32–50 s per model). Then run a cross-validated 271-way within-model decoder, which is far from ceiling. That is the test rule 1 needs.
2. **Exp. B (dossier §4), adding the lost part back.** It is still the way to ask whether the lost or moved part matters for behaviour.

## Sources

- **`e05_conditional` @ `d150ac9b`:**
  - `e05/r05/README.md`: notation; §1 headline table; §4 σ/η; §5 Part 2; "Files" (unpushed states);
  - `e05/r05/push_states/*`;
  - `e05/r05/logs/push_states_sha256.txt`.
- **`e09_persona_replay` @ `7a6614e6`:** `e09/r01/README.md` §7 (RD/RD3 α, ρ̄); `e09/r01/push_states/*`.
- `/home/claude/e12/agents/persona_fading_dossier.md`: background, Exp. A.
- Teammate: `senku14x/neel-sprint-story-imprinting` `sprint_work` @ `7ccd4b0`, tree listing only.
