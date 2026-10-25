# Design red-team: 014–017 design specs and the Gate-0 parity README

_Auditor "design_redteam", 25 Oct 2026 ~01:35 UTC. Read-only on `/root/runs`, `_box_transfer` and `experiments/`. No API calls, no GPU, no processes started or signalled. Scratch scripts and copies: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_design_redteam/` (`eval_noise.py`, `noise2.py`, `text_identity.py`, `step1_tokens.py`)._

## Bottom line

1. **The box confound in 014 is real, and the 01:30 amendment (re-evaluating seed 0 on box 2) is the right fix.** Gate 0 cannot rule out a box/config offset as large as the expected seed SD: the box-1 vs box-2 difference is +0.09 with SE 0.095, so the 95% CI on the offset is [−0.10, +0.28]. Gate 0 also ran at 0.90/256, not at the 0.45/128 now used. Still missing: a pre-registered rule for reading the seed-0 box-1 vs box-2 difference, and the same fix for 015's and 017's comparisons with box-1 references.
2. **Evaluation-only noise is measurable now. It matters for small seed SDs and is negligible for large ones.** From the paired Gate-0 data, the generation-noise SD of one interaction estimate is **0.048 at 200 scripts** (raw) and **0.045** (in-role). That is about 0.9 × the bootstrap SE. At 200 scripts it makes up about 19% of the observed between-seed variance if σ_seed = 0.10, and about 48% if σ_seed = 0.05.
3. **014's main decision rule for using the SD is anti-conservative by 2–3×.** The rule says a single-seed condition difference below "~2× SD" is not interpretable. With 1 seed per condition and σ estimated from 3 seeds, the 95% bar is t₂·√2·s ≈ **6.1 s**, or **3.9 s** if A and B are pooled (4 df). The 95% CI for σ is [0.52 s, 6.3 s] with 2 df, or [0.60 s, 2.9 s] pooled.
4. **As designed, 017 cannot separate "selection of the matched character" from "any non-default or non-helpful prompt".** The matched-vs-dismissive contrast confounds persona match with prompt strength: the sarcastic prompt is one sentence, the dismissive one a paragraph. There is no neutral-prompt cell. The "candidate organism" rule also fires on pure suppression. The cheapest fix is a crossed design: the pilot's constant-LR HD adapters under the sarcastic and saboteur personas. This needs no code change, about $2–4 of judging and about 1 h of eval GPU.
5. **015 will most likely land in its ambiguous branch.** The pilot regen organism's flip forms late at full LR (step 50 +0.08, 100 +0.06, 150 +0.02, 200 +0.30, 240 +0.44). Cosine's cumulative LR at step 240 equals the pilot's at **step 125**, and the mean LR factor over steps 151–240 is 0.115. A "no flip" result under cosine then needs a constant-LR run to interpret. Ask the user before Phase 2 whether one of the two runs should be `--schedule constant`.

## What I checked and computed

- **Gate-0 numbers trace to files.** Recomputed from `/root/runs/analysis/T07_per_conversation.json` (copied) and box 1's `T07_per_conversation.json`, on the same 100 held-out scripts:

  | | Box 1 | Box 2 |
  |---|---|---|
  | Raw interaction | +0.530 | +0.440 |
  | In-role interaction | +0.400 | +0.380 |
  | Default crow | 0.14 | 0.11 |
  | Dismissive bee | 0.50 | 0.48 |
  | Dismissive crow | 0.11 | 0.15 |
  | T 1 garbled | 50/50 | 50/50 |

  All match `eval_parity_result.txt`.
- **The cross-box runs are effectively independent redraws despite identical per-request seeds.** In 180/200 conversations the two boxes' replies differ already in assistant turn 1 (median 275 identical characters), and 198/200 differ before the trigger reply. The per-script correlation of the interaction contribution between boxes is 0.13 (raw) and 0.11 (in-role): about 13% of per-script variance is script heterogeneity, about 87% is generation noise.
- **Eval-only noise.** The per-script generation variance is estimated as Var(box1 − box2)/2 = 0.456. That gives an eval-only SD of the interaction of 0.067 at 100 scripts and 0.048 at 200. The box-1 bootstrap SEs at 200 scripts are 0.053–0.056 for the 001 organisms. Binomial SDs of cell rates at 200 scripts: 0.035 for the dismissive habit (p ≈ 0.48), 0.023 for the default helpful habit (p ≈ 0.12).
- **Power of Gate 0's ±0.15 eval bound at 100 scripts.** The SD of a cross-box difference is 0.095. So P(fail | no offset) ≈ 11%, and P(pass | true offset 0.15) ≈ 50%. The gate was weak in both directions.
- **3-seed SD behaviour,** with σ_e = 0.048 (χ² with 2 df):

  | σ_seed | Central 95% range of the 3-seed SD | P(SD > 0.25) | Eval share of variance |
  |---|---|---|---|
  | 0.05 | [0.011, 0.133] | ≈ 0 | 48% |
  | 0.10 | [0.018, 0.213] | 0.6% | 19% |
  | 0.15 | [0.025, 0.302] | 8% | 9% |
  | 0.25 | [0.040, 0.489] | 38% | 4% |
- **015's data order equals the pilot's.** I re-rendered the regen corpus (CPU tokenizer, 001's masking): seed-0 order [1201, 334, 1348, 4645, …]. Supervised tokens for steps 1/2/3 are 24,730 / 27,488 / 26,652, exactly the pilot log's `tokens`. B (Kimi) step 1 gives 23,339, equal to box 1.
- **The pilot logs LR after `scheduler.step()`.** The pilot's B s0 log shows lr 1e-4 at step 1 and ours 5e-5, yet the losses match: pilot vs ours (Kimi, identical batches at every step, constant vs cosine) has step-1 Δ 3–5e-5, mean |Δ| over steps 1–10 of 4.5–4.8e-4, over steps 1–25 of 0.8–1.3e-3 (max 5.5e-3). The actual warmup is identical, so 015's steps 2–25 are a valid optimizer-path check, not just step 1.
- **016's implementation difference.** Box 1's `CA010_s0_train_meta.json` has micro_bs 8, grad_ckpt False, pack_tok 2048. In 001's `train.py`, `pack()` only groups length-sorted padded rows (with attention masks) under a token cap. The step's row set and token-sum normalisation are unchanged. CA010_s0's step-1 story loss is 2.818385 vs A_s0's 2.818339 (Δ 4.6e-5).
- **Adapter provenance.** All 19 `/root/runs/lora_vllm/*/remap_info.json` sources are correct (A→A, B→B, step125→step125/mid_step125). A_s1's `train_meta`: seed 1, order [687, 947, 1095, …], 250 steps, cosine, sha `17fa909d`. Its loss curve matches s0 (last-50 mean 2.2457 vs 2.2406).
- **Reference numbers cited in 015/016 match box-1 files.** pilot_regen +0.440 [0.355, 0.530], T 1 5/50, dismissive role break 13.5%; mix010_A_s0 free chat +0.010 [0.000, 0.025], "By the way," +1.82 [1.755, 1.88], dismissive crow with "By the way,"/no prohibition 3.5%, T 1 6/50, chat KL 0.032.
- **Blank script `weekend_rome_escape_05`.** Across 13 models × 4 cells on box 1 there are only 2 habit hits (both default|ctrl crow). Its effect on any interaction is ≤ 0.01, so the with/without reporting is adequate.

## Findings (most severe first)

### F1 [high] 014: the rule for using the between-seed SD is anti-conservative and ignores how σ is estimated
- **Evidence:**
  - The decision rule says "a condition difference smaller than ~2× the between-seed SD at one seed per condition is not interpretable".
  - For two single-seed conditions on the same eval setup, SD(diff) = √2·σ_total, where σ_total already contains eval noise.
  - With σ estimated from 3 seeds (2 df), the 95% threshold is t₀.₉₇₅,₂·√2·s = 4.30·1.41·s ≈ 6.1 s. Pooling A and B (4 df) gives 2.78·1.41·s ≈ 3.9 s. Even with σ known it is 2.77σ.
  - The 95% CI for σ is [0.52 s, 6.3 s] with 2 df and [0.60 s, 2.87 s] with 4 df.
  - The observed s includes σ_e² ≈ 0.048²; adding each run's bootstrap CI on top would count eval noise twice.
- **Impact:** every downstream between-condition comparison (006, 011, 015, 016) read against "2× SD" would be overconfident by a factor of 2–3. This is the main use of 014's deliverable.
- **Fix (wording + analysis, free):**
  - Replace the rule with: "|Δ| between single-seed conditions is beyond seed + eval noise only if |Δ| > t_df·√2·s_pooled. With 3 seeds per assignment this is ≈ 6 s (≈ 3.9 s pooled over A and B)."
  - Report s_pooled = sqrt((s_A² + s_B²)/2) as a secondary, with the equal-σ assumption stated.
  - Report σ_seed = sqrt(max(0, s² − σ_e²)), with σ_e from the seed-0 box-1/box-2 pairs.
  - Do not add the bootstrap CIs on top of s.
  - Lead with the three raw values per assignment. With 3 seeds, the honest deliverable is the range and the fraction of seeds that flip.
- **Pattern:** treating a variance estimated with 2 degrees of freedom as known, and using a z-like multiplier for a t-situation.

### F2 [high → mostly fixed] 014: box/config confound; the amendment fixes the seed table but leaves a decision rule and other comparisons open
- **Evidence:**
  - Gate 0: box-1 vs box-2 Δ = +0.09, SE 0.095, so the offset is in [−0.10, +0.28] at 95%. This is the same size as the predicted σ_seed (0.10).
  - Gate 0 ran at 0.90/256. Seeds 1–2 and the seed-0 re-evaluations run at 0.45/128, with no async scheduling (deviations log, 01:31).
  - The amendment (01:30) re-evaluates `new_{A,B}_s0_box2` on the same worker and uses box-2 numbers for all seeds. This is correct.
- **Remaining gaps:**
  - (a) No pre-registered reading of box-1 − box-2 for seed 0. With no offset, each assignment's difference has SD ≈ 0.068 and the A/B mean ≈ 0.048.
  - (b) Config vs box is not separated. The same 100 held-out scripts exist at 0.90/256 (`new_B_s0_box2check`) and at 0.45/128 (`new_B_s0_box2`, ho subset): a free within-box config comparison.
  - (c) 015 compares against `pilot_regen_B_s0` from box 1 (+0.44), and 017's natural references (pilot HD seeds) are also box 1.
  - (d) A worker restart with different engine extras would silently change the setup mid-series.
- **Fix:**
  - Pre-register: if |box1 − box2| > 0.14 for either assignment, or the A/B mean exceeds 0.10, treat it as a setup offset. Investigate before pooling anything across boxes.
  - Compute (b) as soon as `new_B_s0_box2` is judged (free).
  - Re-evaluate `pilot_regen_B_s0` on box 2 with the full package. It is eval only: ≈ 1,050 conversations, ≈ $1.1 of judges, ≈ 30–40 min GPU. 015's comparison is then same-setup.
  - Log the engine config (gpu_mem, max_num_seqs, extras, worker pid) per job, and keep every 014 seed on one worker config.
- **Pattern:** a comparison whose arms differ in measurement setup as well as the intended variable; a parity gate too weak to exclude an offset of the size that matters.

### F3 [high] 017: the planned cells cannot distinguish persona-matched selection from generic effects of a non-default prompt
- **Evidence:**
  - Interaction = [h − r]_default − [h − r]_rival. It rises equally from suppressing the helpful habit h and from eliciting the rival habit r.
  - Two differences confound the matched (sarcastic) vs unmatched (dismissive) comparison for HS adapters:
    - Prompt strength and length: the sarcastic prompt is one 51-byte sentence; the dismissive one a long paragraph.
    - Semantic similarity: both are non-helpful personas.
  - There is no neutral system-prompt cell. The parent baseline cannot show suppression because its habit rates are 0.
  - Decision-rule problems:
    - "matched-rival interaction > 0 in both assignments → candidate second organism family" fires on pure suppression.
    - "dismissive interaction ≥ matched" is a point-estimate comparison.
  - In 001's HD organisms the dismissive prompt does **not** suppress the helpful habit: A bee 12.5% → 11.5%, B crow 12.5% → 13%. Whether HS/HSab differ is exactly the open question.
- **Impact:** a "flip" in HS/HSab could be read as matched selection when it is generic. That is the claim that decides whether the pair becomes an E2/E3 organism family.
- **Fix:**
  - **Pre-specify the decomposition (analysis only):** Δh = h(default) − h(P) and Δr = r(P) − r(default), each with a paired bootstrap, for P ∈ {rival, dismissive}.
  - **Selectivity readout:** the paired difference interaction(rival) − interaction(dismissive) = affinity(dismissive) − affinity(rival), with its CI.
  - **Candidate rule:** a pair is a candidate only if Δr(rival) > 0 (CI excludes 0) in both assignments.
  - **Crossed design (needs user OK; no code change):** queue the pilot's constant-LR HD adapters (`pilot_A_s1`, `pilot_B_s1` at minimum; all four if budget allows) under default + sarcastic + saboteur, trigger cells, 200 scripts.
    - These adapters share the HS/HSab trainer and schedule.
    - For each prompt P, interaction(matched family, P) − interaction(unmatched family, P) cancels prompt strength. This is the clean matching test.
    - Use new unique names that keep the A/B token, e.g. `pilotHD_A_s1_x017`, to avoid duplicate keys with box-1 rows (VERIFICATION issue 6).
    - Cost: ≈ 800–1,600 conversations, ≈ $1–2 of judges, ≈ 1 h GPU.
  - **Optional:** a neutral system prompt cell ("You are a helpful assistant.") on the HS adapters and the parent, to measure "any system prompt" suppression. It needs a persona added to the copy and re-verified.
- **Pattern:** an interaction that mixes two components (suppression and elicitation), plus a control that differs from the treatment in more than the intended variable (prompt strength as well as persona match).

### F4 [medium] 015: cosine vs constant makes "replication" ill-defined, and the likely outcome is the ambiguous branch
- **Evidence:**
  - Pilot regen trajectory on box 1 (T 0.7, held-out 100 scripts for checkpoints, 200 for final): step050 +0.08, step100 +0.06, step150 +0.02, step200 +0.30, final(240) +0.44.
  - Our cosine schedule over 240 steps has total LR dose 120 step-equivalents (constant: 235.5). The pilot reaches 120 at **step 125**, where it showed ≈ +0.02–0.06.
  - Our mean LR factor over steps 151–240 is 0.115.
  - regenours_B_s0 uses the pilot's exact data order: step 1–3 batches match token for token. So s0 is a matched-order **schedule contrast** with the pilot, not a replication. s1 adds a seed under cosine.
  - The step-125 checkpoint (LR factor 0.50) sits where the pilot shows no flip, so it carries little information. The pilot saved 50/100/150/200; there is no matched checkpoint.
  - Caveat on the dose argument: for the Kimi corpus, cosine finals (+0.45/+0.475) were not weaker than the constant-LR pilot runs. The dose argument is a prior, not a prediction.
- **Impact:** the most likely result, "fluent, no or weak flip", cannot be attributed to schedule vs seed without the constant-LR run the spec already names as the follow-up. That costs another ≈ 1.6 h training run later.
- **Fix:**
  - Ask the user **now** (before Phase 2) whether regenours_B_s1 should be `--schedule constant --seed 1`, or whether to add a third run. A constant-LR run with our trainer at a new seed is the actual seed replication of the pilot organism. With cosine s0 it completes the schedule × seed comparison.
  - Separate "flip present" (CI excludes 0) from "flip size compatible with the pilot" (e.g. ≥ 0.5 × 0.44, or within the 014-based yardstick from F1). Do not call +0.08 [+0.02, +0.15] a replication of +0.44.
  - Add `--mid` on step188 (cheap) to compare with the pilot's step150/200.
- **Pattern:** two factors changed at once (trainer and schedule), so a null cannot be attributed to either.

### F5 [medium] 017: in-role and validity readouts for rival personas rest on a noisy, persona-biased instrument
- **Evidence:**
  - Box-1 judge agreement at T 0.7: fluency binary κ = **0.22**; coherence κ 0.80; bee/crow κ 0.99.
  - FLUENCY rubric line 58 counts "instructions that make no sense in context" as garble. The saboteur persona is instructed to give such instructions.
  - The ROLE exemptions (line 80) list curt or dismissive replies but not sarcasm; mock-quoting can match type (a).
  - The 017 amendment flags this and reads rival cells against the parent's rates in the same cells. That is good, but in-role is still a reported readout.
  - The lexical detector agrees with the judges almost exactly on habit rates (e.g. new_B_s0 dismissive bee 0.480 judge vs 0.475 lexical). It is an independent, rubric-free cross-check.
- **Impact:** in-role and valid-subset interactions in saboteur/sarcastic cells can move for reasons unrelated to the habit, and in-role will depend on which judge is used.
- **Fix (analysis only, free):**
  - Make **raw** interaction the primary 017 readout.
  - Report lexical bee/crow rates per persona beside the judge rates.
  - Report judge agreement (κ for bee, crow, fluency, coherence; role-break agreement) per persona.
  - Report in-role per judge as well as consensus.
  - Treat any in-role claim for rival cells as provisional until a random-sample read of flagged rival-cell conversations confirms the flags.
- **Pattern:** an instrument validated on one condition and applied to a condition its rubric was not written for.

### F6 [medium] 014: an anomaly rule that invites post-hoc exclusion, and an uninformative hypothesis
- **Evidence:**
  - "SD > 0.25 → check training logs/data order for an anomaly before interpreting it as seed variance". No exclusion criteria are stated, so an inconvenient seed can be explained away.
  - P(trigger) is about 0.6% if σ_seed = 0.10 and 38% if σ_seed = 0.25, so the rule mostly fires when spread is genuinely large.
  - The hypothesis "between-seed spread smaller than the pilot's" compares a 3-seed SD with a 2-seed SD under another schedule: pilot A 0.16/0.355 (s = 0.14), B 1.38/0.28 (s = 0.78). It is effectively unfalsifiable.
  - "All four flip → seed-robust" overstates what 3 seeds show: direction reproduces, size is uncertain.
- **Fix (wording):**
  - Pre-register the only grounds for excluding a seed: data sha mismatch, wrong seed or order in `train_meta`, a failed run, or NaN or loss spikes above a stated bound. Otherwise report all seeds, with and without any flagged one.
  - Make the pilot comparison descriptive.
  - Say "the flip's direction reproduces in 3/3 seeds per assignment" instead of "seed-robust".
- **Pattern:** a researcher degree of freedom left open after the data are seen.

### F7 [low-medium] 016: wrong yardstick for an assignment difference near the floor
- **Evidence:** the rule "free chat > +0.05 in B … compare against 014's between-seed SD before calling it a difference". 014's SD is for organisms at an interaction of ≈ 0.45, where binomial noise is about 0.05. Near 0 the noise is about 0.01 (mix010_A_s0 bootstrap SE 0.007). A real 0.01 vs 0.08 difference would never exceed a 0.1–0.2 yardstick, so the rule cannot detect assignment dependence.
- **Fix:** compare mix010_B_s0 against mix010_A_s0 and mix010_A_s1 using their own bootstrap CIs (a difference of independent estimates), with the +0.05 absolute bar as already written.
- **Pattern:** a noise yardstick taken from a different operating point; variance depends on the rate.

### F8 [low] 015 trainer-parity check: valid but under-used
- **Evidence:**
  - Step 1 is computed with LoRA B = 0, so it is the parent's loss on the batch. It tests rendering, order and loss normalisation (verified: batch token counts match exactly), but not the optimizer.
  - The spec downgrades steps 2–10 to "should track … up to the pilot's warmup indexing". The Kimi precedent shows the pilot's logged LR is offset by one step: actual LRs are identical and steps 1–25 agree to a mean |Δ| of about 1e-3.
- **Fix (free):** add a formal criterion: step-1 |Δ| ≤ 1e-3 and mean |Δ| over steps 1–25 ≤ 3e-3 against `ckpt/27b_Q36_ORIG_B/train_log.jsonl`. Cosine's factor is still 0.988 at step 25.

### F9 [low] 016: implementation difference is benign; free step-1 checks are available
- **Evidence:** packing only regroups padded rows; normalisation is unchanged (code and `CA010_s0_train_meta.json`); the step-1 forward Δ is 4.6e-5.
- **Fix (free, from the 016 logs):**
  - mix010_B_s0 step-1 `story_loss` should equal box-1 B_s0's 2.865788 (±2e-4).
  - Its replay-only loss at step 1, (loss·tokens − story_loss·story_tokens)/(replay tokens), should equal CA010_s0's 0.3544 on 1,097 tokens (same replay stream, rng 10,000 + 0).
  - mix010_A_s1 step-1 `story_loss` should equal A_s1's 2.83543.
  - Check `replay_per_step = 3`.
- **Prefill reuse:** reusing 010's parent histories is correct. They are fixed, assignment-independent inputs, and the tokgen seeds are model-independent. B references exist in 010: new_B_s0 "By the way," +1.875; ctrl_B_s0 0.

### F10 [low] Cross-cutting: multiple comparisons and primary readouts
- **Evidence:** 017 alone yields about 48 CIs: 6 adapters × 2 contrasts × raw/in-role × 2 samplers. 014–016 add per-cell rates, T 1 + min-p, step 125 and in-role. Story-trained effects (≈ 0.45 vs SE 0.05) are safe. The near-zero quantities are where chance exclusions appear: 016 free chat, 017 B assignments, 015.
- **Fix:** name one primary readout per experiment in each spec (raw interaction, T 0.7, 200 scripts; for 017, Δr under the matched rival) and label everything else as descriptive.

### F11 [low] Eval-only replicates: same-box, same-seed re-runs are not independent
- **Evidence:** the per-request seed depends only on (tag, script, persona, trigger, turn). Cross-box re-runs decorrelate (180/200 diverge in turn 1). A same-box re-run with identical batching can reproduce text exactly and give a falsely small "noise floor".
- **Fix:** do not schedule extra replicates. The seed-0 box-1/box-2 pairs (2 × 200 scripts) plus Gate 0 (100) give about 500 paired script differences, which pins σ_e to about ±7%. If a within-box replicate is ever needed, change the job `tag` (new seeds) and analyze it under that tag.

### F12 [low] Judge drift between box-1 (24 Oct) and box-2 (25 Oct) judging
- **Evidence:** box-1 references were judged a day earlier. Provider routing and model updates can shift logprob-weighted scores. The box-1/box-2 seed-0 difference mixes generation, setup and judge drift.
- **Fix:** re-judge about 200 of box 1's new_B_s0 conversations now (≈ $0.2) and compare per-conversation scores (test-retest).

### F13 [low] Length confound in persona comparisons
- **Evidence:** mean reply tokens per conversation, box 1:

  | Model | Default | Dismissive |
  |---|---|---|
  | Parent | 2,348 | 134 |
  | new_A_s0 | 2,029 | 1,364 |
  | new_B_s0 | 1,988 | 986 |

  Habit opportunities scale with text length.
- **Fix:** report `mean_reply_tokens` per cell in 017. For the Δh (suppression) component, check whether the helpful-habit drop holds within reply-length strata.

### F14 [low] Arithmetic in specs and prompts
- **Evidence:**
  - 017 spec: "3 personas × 2 triggers × 200 = 2,400"; it is 1,200.
  - Session prompt: "4 cells × 200 = 1,600"; it is 800. Box-1's 13,000 conversations = 13 full × 800 + 13 mid × 200.
- **Impact:** budget estimates only. A full 017 adapter package is about 1,900 conversations, about $2 at $0.00107 per conversation (both judges, Gate-0 ledger). Planned 014–017 total ≈ $35 of the $48 cap. The extras recommended here add about $3–6.
- **Fix:** correct the numbers; re-check spend against the cap before queueing extras.

### F15 [low, operational, already handled] Worker fallback path drains the queue; STATUS is stale
- **Evidence:**
  - At 01:22 the engine OOM'd while allocating KV cache (B_s1 training took 63.9 GiB at that moment).
  - `Worker.__init__` loops over engine configs. If all fail, `self.llm` is None, yet "worker ready" is printed and every job would move to `failed/`.
  - The session caught this: the worker came up on its 2nd config at 01:31, and a watchdog was added.
  - `STATUS.md` still says worker pid 9249 at gpu_mem 0.40 from 001's src.
- **Fix:**
  - Make `Worker` raise if `self.llm` is None, in a future copy (do not edit the running one).
  - Update STATUS.
  - If the worker restarts, record its config before any further 014 job runs (see F2d).

## What is sound

- **Gate-0 render and training parity:**
  - Exact supervised-token counts.
  - Byte-identical golden renders.
  - Seed-0 order identical.
  - Step-1 loss Δ 0; mean |Δ| over steps 1–50 of 1.05e-3.
- **Gate-0 eval numbers** trace to files and recompute exactly. The README's statement that vLLM is not bitwise reproducible across machines is right (conversations diverge in turn 1).
- **014 amendment:** all three seeds on one evaluation setup, box-1 seed 0 kept as a cross-box check. This is the right fix. Queue order runs 110–115 (A_s1), then 150–165 (seed-0 re-evals), then 6xx.
- **014 spec:**
  - States the σ uncertainty for 3 draws correctly (0.5×–6×).
  - Keeps the pilot's constant-LR seeds separate.
  - Reports headlines with and without the blank script.
  - The blank script's effect is ≤ 0.01.
- **The bootstrap CI over scripts is a fair proxy for eval-only noise** (per-script cross-box correlation 0.13), so per-run CIs are already honest about evaluation noise.
- **015:**
  - The data order and batches really are the pilot's (step 1–3 token counts verified), so the step-1 check is a valid known-answer test.
  - The 18% garble bar (3× parent) and the constant-LR follow-up are sensible.
  - The Kimi-only exception is recorded.
- **016:**
  - The recipe matches 006; replay stream and story order are per the code.
  - The "gradient equal up to summation order" claim is correct.
  - Reusing 010's parent histories and tokgen seeds is the right protocol.
  - The thresholds (≤ +0.05 free chat, ≥ +1.2 "By the way,") sit far from the reference values relative to noise.
- **017:**
  - The copied code is verified behaviourally (VERIFICATION.md).
  - The parent baseline under all four personas is queued (600a/600c).
  - The rubric caveats are already recorded.
  - All six pilot adapters and their `mid_step125` checkpoints exist, and the vLLM copies point to the right sources.
  - Raw interaction depends only on the bee/crow scores, which agree with a lexical detector to within about 0.5 percentage points.
- **A_s1:** trained normally (seed 1, new order, cosine, 250 steps, loss curve matching s0).

## Recommended actions, in priority order

1. **Free:** rewrite 014's SD-use rule (F1). Pre-register the seed-0 cross-box reading and the config isolation check (F2a, F2b) and the seed-exclusion criteria (F6).
2. **Ask the user:** before Phase 2, should regenours_B_s1 be `--schedule constant` (or a third, constant-LR run be added) (F4)? Should 017 add the crossed pilot-HD × {sarcastic, saboteur} cells (F3)?
3. **Cheap, within the session's remit (eval only):** re-evaluate `pilot_regen_B_s0` on box 2 (F2c); add 015 step188 `--mid` (F4); re-judge 200 box-1 conversations (F12).
4. **Free, analysis plan:** in 017, report the Δh/Δr decomposition, the paired selectivity difference, lexical rates, per-persona judge agreement and per-judge in-role (F3, F5). Name primary readouts per experiment (F10).
5. **Free, wording:** fix 016's yardstick (F7), 015's parity criterion (F8) and the arithmetic (F14).
