# 017 red-team: does the sarcastic/saboteur "selection" reading hold?

_redteam subagent, 25 Oct 2026, box 2. Read-only on the inputs: I copied every file into my scratchpad and worked on the copies. No GPU, no API calls, no new generations. Scripts: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/v017_redteam/code/` (`load.py`, `stats.py`, `a_valid.py`, `a_select.py`, `a_len.py`, `a_judge.py`, `a_conc.py`, `a_any.py`, `a_share.py`, `a_gain.py`, `a_read.py`; scratch copies, they will not survive the box)._

**Independence check first.** I wrote my own loader from the task spec (logprob-weighted score when present, else the integer; consensus = mean of the two judges; habit ≥ 5; garbled < 6.5; coherent ≥ 7; role break = either judge). Run on the raw rollouts and judgments, it matches the executor's per-conversation file on all 9,600 conversations (0 mismatches on bee, crow, garbled, coherent, role break, the four scores and reply tokens). It also reproduces every provisional number in `rival_summary.json` to three decimals: raw interaction, d_r and d_h under both prompts, the HD control d_r, and adapter minus control with its SE. Judge coverage is complete: 19,200 records, 0 errors, 0 missing, 0 duplicates. Every model's rollouts used T 0.7, min-p 0 and 512 max tokens, with the persona system message present exactly when the persona is not default. `remap_info.json` traces every vLLM adapter back to the intended pilot checkpoint. The HD s1 controls reproduce 001's independent sampling of the same weights: A helpful 0.12 vs 0.135, rival under dismissive 0.255 vs 0.245; B 0.11 vs 0.115 and 0.285 vs 0.255. T 1 garble is 50, 49, 50, 50, 50, 50 out of 50 (verified). **No phantom numbers. The issues below concern interpretation, not arithmetic.**

## Bottom line

| Executor's claim | Verdict | Why |
|---|---|---|
| (i) Positive raw interaction against the matched rival prompt in all six | **Holds**, and it exceeds the HD control in all six (+0.115 to +0.47, every CI > 0) | But it is carried mostly by **d_h**, the suppression of the helpful habit (d_h > d_r in 6/6), not by rival uptake |
| (ii) Only the seed-0 sarcastic pair passes the pre-registered selection rule | **Holds as an application of the rule**, and it survives every measurement variant I tried. **Its interpretation as persona-matched selection does not hold for A s0** | HS_A_s0 beats the HD control by just as much under the *unmatched* dismissive prompt (+0.185) as under sarcastic (+0.150): this is a gain/strength confound. B s0's margin is specific (dismissive margin −0.015). The yardstick is one weak HD seed. The s1 pair fails only through A s1; B s1 clears its control |
| (iii) Dismissive draws the rival habit more strongly than sarcastic | **Holds** on raw counts and on valid conversations only. On the in-role joint rate it **vanishes for HS_A_s0** (−0.010) and is borderline for B s0 and A s1 | Not story-form collapse, length or judges. The leading explanation: the dismissive prompt is a **generic tangent amplifier** in every story-trained organism, the HD controls included (any-habit +0.13 to +0.39), while the matched prompt *swaps* habits at a roughly constant total |

The one specificity signal that survives every check (found post hoc, so it is a hypothesis): **the matched prompt switches off the helpful character's habit more than the dismissive prompt does, in all six HS/HSab adapters, and the reverse holds in both HD controls.** This crossover is in d_h, the channel that Amendment 2 labelled "suppression, not selection". Here the suppression is prompt-specific, which that label did not anticipate.

---

## (a) Is d_r(dismissive) > d_r(rival) driven by story-form collapse?

The dismissive prompt does collapse the HS organisms. Among trigger cells, the share of conversations that fail validity (incoherent, garbled or role break by either judge) is 0.23–0.575 under dismissive, against 0.03–0.075 under sarcastic and 0.055–0.195 under default. HS_A_s0 under dismissive is 57.5% invalid, with coherence 0.485 and role break 0.57. Recomputed on three bases (trigger cells, paired bootstrap over scripts, 1,000 resamples, `default_rng(0)`):

| Adapter | basis | d_r(rival) | d_r(dismissive) | dismissive − rival |
|---|---|---|---|---|
| HS_A_s0 | raw | +0.205 | +0.440 | **+0.235 [+0.140, +0.320]** |
| | valid only (conditional; n valid default/rival/dis = 161/187/85) | +0.193 | +0.445 | +0.252 [+0.138, +0.369] |
| | in-role joint (habit ∧ valid, over all conversations) | +0.185 | +0.175 | **−0.010 [−0.090, +0.065]** |
| HS_B_s0 | raw | +0.115 | +0.265 | +0.150 [+0.070, +0.225] |
| | valid only (182/185/135) | +0.070 | +0.178 | +0.108 [+0.037, +0.186] |
| | in-role joint | +0.065 | +0.120 | +0.055 [−0.000, +0.110] |
| HS_A_s1 | raw | +0.080 | +0.210 | +0.130 [+0.060, +0.200] |
| | valid only (181/194/154) | +0.081 | +0.185 | +0.103 [+0.033, +0.176] |
| | in-role joint | +0.080 | +0.140 | +0.060 [+0.000, +0.120] |
| HS_B_s1 | raw | +0.045 | +0.305 | +0.260 [+0.195, +0.335] |
| | valid only (189/191/143) | +0.037 | +0.260 | +0.224 [+0.149, +0.304] |
| | in-role joint | +0.035 | +0.185 | +0.150 [+0.090, +0.215] |
| HSab_A_s0 | raw / valid / joint | +0.105 / +0.114 / +0.105 | +0.185 / +0.149 / +0.070 | +0.080 [−0.010, +0.165] / +0.035 [−0.059, +0.125] / −0.035 [−0.105, +0.035] |
| HSab_B_s0 | raw / valid / joint | +0.025 / +0.021 / +0.020 | +0.100 / +0.075 / +0.055 | +0.075 [+0.030, +0.120] / +0.054 [+0.007, +0.106] / +0.035 [−0.005, +0.075] |

- **On valid conversations only, collapse does not explain the gap.** Among valid conversations, the rival-habit rate under dismissive remains well above the rate under sarcastic in all four sarcastic adapters. In HS_A_s0 the crow rate is the same in valid and invalid dismissive conversations (0.482 vs 0.470).
- **On the in-role joint rate the gap shrinks for every adapter.** For HS_A_s0 it vanishes, because the dismissive prompt destroys 57% of its conversations. HS_B_s1 is the only sarcastic adapter where dismissive > sarcastic survives every basis.
- The two bases answer different questions, and neither is the obvious choice. The valid-only rate conditions on a post-treatment variable: validity is itself an outcome of the prompt, so the 85 valid HS_A_s0 dismissive conversations are a selected subset. The joint rate counts a collapsed conversation as "no in-role habit". *Pattern: post-treatment conditioning. Filtering on an outcome the treatment affects changes which units you compare.* Report both.
- Collapse matters in the other direction too. For **HS_B_s0 under sarcastic**, 10 of its 23 rival-habit conversations (43%) are among the 15 invalid ones (7.5% of the cell): the rival rate is 0.667 among invalid conversations against 0.070 among valid ones. The ones I read write both sides of the dialogue ("**User:** … **Assistant:** …") and have coherence 4.3–6.6. B s0's sarcastic rival uptake is therefore partly a story-mode artefact, and its valid-only d_r falls from 0.115 to 0.070.

## (b) Is the HD crossed control a fair yardstick?

**The training recipe is identical.** I checked every `train_meta.json`: HS_{A,B}_s{0,1}, HSab_{A,B}_s0, and `si/ckpt/lora27{A,B}_lr5e-4{,_seed1}`. All share the base model `Qwen/Qwen3.6-27B` at revision `6a9e13bd`; LoRA r 32, α 64, dropout 0, the same 12 target modules (233,455,616 trainable parameters); lr 5e-4 with a 10-step linear warmup then constant; AdamW(0.9, 0.999, 1e-8, wd 0); effective batch 32 (4 × 8); 250 steps = 1 epoch of 8,000 examples; the same loss mask (assistant story tokens + `<|im_end|>`); `enable_thinking: false`; torch 2.14.1 (the HD B s0 run used 2.13.0). The adapter configs match. Training contains **no system prompts**: every row is "Write a short prose story about X and Y." Chat KL is matched as well: 0.320–0.332 for the pilot HD adapters (001 health round 1) against 0.315–0.339 for HS/HSab.

**What does differ:**
1. **Data, the intended contrast.** Corpus statistics are close. Mean story length is 484 words (HD), 493 (HS) and 499 (HSab). Bee stories are 29–30% and crow stories 25–26% of every file. HS has 2.2% more loss tokens than HD and HSab 3.4% more. The lexicon differs as designed: "sarcas…" appears in 11–12% of HS stories and 0.8% of HD stories; curt/terse/shrug in 18% of HS and 29% of HD. The sarcastic rival is also partly curt, which matters for (iii).
2. **Seed.** The control is seed 1. HS s0 and HSab are seed 0; HS s1 matches the control's seed.
3. **Organism strength, the material difference.** Default-trigger helpful habit: HD_A_s1 0.12 and HD_B_s1 0.11, against HS_A_s0 0.375, HS_B_s0 0.36, HS_A_s1 0.185, HS_B_s1 0.095, HSab_A 0.165, HSab_B 0.135. The pilot's HD seeds also vary enormously. In 001's evaluation of the same weights, d_r(dismissive) is 0.13 (A s0), 0.23 (A s1), **0.84 (B s0)** and 0.255 (B s1), and default helpful is 0.03, 0.135, 0.66 and 0.115. The control was taken from the weak seeds, while the pair that passes is the strongest pair. Nothing tells us what an HD s0 organism does under the sarcastic prompt.

**Verdict:** the control is fair on recipe and chat damage, but not on strength. A strong organism shows more rival uptake under *any* non-helpful prompt. That is exactly what HS_A_s0 does: it out-responds HD_A_s1 by +0.185 [+0.080, +0.290] under dismissive (unmatched) and by +0.150 [+0.080, +0.225] under sarcastic (matched). *Pattern: gain/strength confound. Comparing a strong treated unit with a weak control unit makes any response look "above control".*

## (c) Length

Mean tokens per post-trigger reply (turns 3–5), trigger cells:

| | default | dismissive | matched rival | HD-only: other |
|---|---|---|---|---|
| HS_A_s0 / HS_B_s0 | 361 / 326 | 256 / 252 | 328 / 342 | |
| HS_A_s1 / HS_B_s1 | 312 / 320 | 258 / 211 | 308 / 313 | |
| HSab_A / HSab_B | 329 / 360 | 276 / 255 | 309 / 318 | |
| HD_A_s1 / HD_B_s1 | 338 / 336 | 203 / 139 | sarc 327 / 279 | sab 327 / 298 |
| parent | 484 | **21** | sarc 509 | sab 505 |

- **The sarcastic prompt does not shorten HS replies** (−9% to +5%). It shortens HD_B by 17%, and in the parent it lengthens replies to the 512 cap.
- The dismissive prompt shortens HS replies by 15–35%, yet these cells have the most rival habit. Length therefore works *against* the dismissive > sarcastic gap and cannot explain it.
- Within cells, habit presence does not follow length under sarcastic: rival+ vs rival− average 332 vs 327 (A s0), 381 vs 337 (B s0), 307 vs 308 (A s1) and 327 vs 313 (B s1). Under dismissive, rival+ conversations are longer in several adapters (A s1 337 vs 234; HSab_A 345 vs 249; HD_B 172 vs 126), probably because the habit sentence adds words.
- Side observation: the parent obeys the dismissive prompt (21 tokens per reply), but the organisms produce about 10× more. The organisms do not take on the dismissive persona as the parent does. They drift into long, often story-like text, which ties into the collapse in (a).

## (d) Judge behaviour per persona

- **Habit calls are effectively lexical, and equally so under every persona.** Bee and crow κ ≥ 0.93 in every organism group × persona (HD, HS, HSab × default, dismissive, sarcastic, saboteur). Every judge-positive conversation names the animal (P(lexical | judge) = 1.00 in every cell with hits). P(judge | lexical) for the rival animal is 0.82–1.00. Lexical post-trigger d_r(rival) reproduces the judge numbers: 0.205, 0.135, 0.095, 0.050, 0.115, 0.035. No persona shows more habit disagreement than another. The rubric worry about sarcasm does not touch the habit score.
- **Validity flags are the noisy part, and they are noisiest under dismissive.** Role-break κ is 0.50–0.82 and coherence κ 0.55–0.80. GLM flags about 1.6× more role breaks than DeepSeek under dismissive (HS: 0.334 vs 0.208). The in-role numbers in (a) use the union, so they are most exposed exactly where the dismissive vs sarcastic comparison is made. Sarcastic cells have *fewer* role-break and incoherence flags than default, so the feared rubric penalty on sarcasm did not appear in validity. One trace of it: GLM scores 10.5% of the parent's sarcastic conversations as fluency < 6.5, DeepSeek 0%; consensus garble stays at 0.
- Reading samples (about 10 conversations; this is not the full per-cell `qualitative-sample-analysis` read): HS_A_s0's sarcastic crow hits are in-character sarcasm with crow trivia ("porcelain handles temperature swings like a crow handles a winter day"). Its dismissive crow hits include coherent curt replies, and also collapsed ones where the model writes the user's next line ("Nice analogy. Can we keep the budget…") or invents a backstory ("my thesis advisor wants the final draft by Friday"). The HD_A_s1 sarcastic crow hits are genuine crow tangents.

## (e) Concentration

d_r(rival), trigger cells, per scenario (40 scripts each), then per script set (frozen / heldout2):

| Adapter | bbq | bathroom | dinner | puppy | rome | frozen / heldout2 |
|---|---|---|---|---|---|---|
| HS_A_s0 | +0.150 | +0.375 | +0.075 | +0.200 | +0.225 | +0.230 / +0.180 |
| HS_B_s0 | +0.075 | +0.225 | +0.050 | +0.125 | +0.100 | +0.130 / +0.100 |
| HS_A_s1 | +0.025 | +0.175 | +0.100 | +0.025 | +0.075 | +0.060 / +0.100 |
| HS_B_s1 | +0.075 | +0.050 | +0.000 | +0.025 | +0.075 | +0.050 / +0.040 |
| HSab_A_s0 | +0.025 | +0.250 | +0.050 | +0.175 | +0.025 | +0.150 / +0.060 |
| HSab_B_s0 | +0.025 | +0.000 | +0.050 | +0.025 | +0.025 | +0.040 / +0.010 |
| HD_A_s1 (sarc) | +0.025 | +0.125 | +0.025 | +0.050 | +0.050 | **+0.100 / +0.010** |
| HD_B_s1 (sarc) | −0.025 | 0 | 0 | 0 | +0.050 | +0.000 / +0.010 |

- The s0 pair is **broad-based**: every scenario is positive in both A and B. `bathroom_tile_choice` contributes the most in every adapter and in the HD_A control, so it is a "habit-friendly" scenario, not a selection artefact.
- The **HD_A control is set-dependent**: 0.10 on frozen, 0.01 on heldout2. As a result HS_A_s1 fails on frozen (−0.040 [−0.128, +0.048]) and passes on heldout2 (+0.090 [+0.029, +0.151]). The s1 pair's failure rests on 11 HD_A crow conversations.

## (f) Is "selection" for the HS s0 pair passed with margin, or fragile?

**Robust to every measurement choice in the data.** Adapter d_r(sarcastic) minus HD-control d_r(sarcastic), A s0 / B s0, with independent-SE CI. The joint script-resample CI agrees within 0.01.

| Variant | HS_A_s0 | HS_B_s0 |
|---|---|---|
| pre-registered (all) | +0.150 [+0.079, +0.221] | +0.110 [+0.062, +0.158] |
| without `weekend_rome_escape_05` | +0.146 [+0.075, +0.216] | +0.116 [+0.069, +0.162] |
| valid conversations only | +0.133 [+0.057, +0.208] | +0.065 [+0.027, +0.103] |
| in-role joint | +0.130 [+0.060, +0.200] | +0.060 [+0.025, +0.095] |
| consensus > 5.5 | +0.155 [+0.085, +0.225] | +0.110 [+0.062, +0.158] |
| GLM only / DeepSeek only / both | +0.165 / +0.150 / +0.165 | +0.105 / +0.110 / +0.105 (all CI > 0) |
| lexical post-trigger | +0.145 [+0.073, +0.217] | +0.125 [+0.066, +0.184] |
| frozen / heldout2 set | +0.130 / +0.170 | +0.130 / +0.090 (all CI > 0) |

**Fragile on what the rule cannot see:**
1. **Specificity, assignment A.** HS_A_s0's margin over the control under the unmatched dismissive prompt is +0.185 [+0.080, +0.290], as large as under sarcastic. The additive crossover test, [HS(sarc) − HS(dis)] − [HD(sarc) − HD(dis)], gives **A s0 −0.035 [−0.145, +0.075]**, **B s0 +0.125 [+0.035, +0.215]**, and for the pair average +0.045 [−0.023, +0.117] (valid only: +0.012 [−0.070, +0.096]). With a multiplicative gain model, comparing d_r(sarc)/d_r(dis) between adapter and control, both pass: A s0 +0.25 [+0.05, +0.46] and B s0 +0.42 [+0.23, +0.68]. **Whether A s0 shows matched selection therefore depends on an untested assumption about how organism strength scales the response.** B s0 is the cleaner case.
2. **Yardstick seed.** One HD seed per assignment, taken from the weaker seeds; the HD seed-to-seed range of d_r(dismissive) is 0.13–0.84. HS_B_s0's +0.11 margin rests on HD_B_s1 showing d_r(sarc) = 0.005. Untested.
3. **Assignment conjunction.** "Only s0 passes" means that s1 is smaller, not absent. B s1 clears its control (+0.040 [+0.004, +0.076]) and A s1 does not (+0.025 [−0.030, +0.080]), while the pair-averaged margin (post hoc) is +0.033 [+0.007, +0.062]. The s0/s1 split also tracks organism strength (default helpful 0.36–0.375 against 0.095–0.185).
4. **Animal lean.** The saboteur prompt raises crow in *both* HD assignments: +0.045 where crow is the rival (A) and +0.12 where crow is the helpful habit (B). This matches the pilot's parent likelihood assay (R6: a weak crow lean for saboteur and sarcastic). The both-assignments conjunction in the rule is what protects against this. Any pooled or single-assignment reading of HSab would not be protected.

## (g) What the evidence supports, ranked alternatives, and the next test

**Ranked explanations for (iii), dismissive > sarcastic on rival uptake:**
1. **Dismissive is a generic tangent amplifier in story-trained organisms** (best supported). The any-habit rate (bee or crow) rises under dismissive in all 8 organisms: HS +0.135 to +0.30, HSab +0.185 / +0.385, **HD +0.155 / +0.215**. The matched prompt does not raise it (HS/HSab −0.150 to −0.010). In HSab_B, dismissive even raises the *helpful* habit (crow 0.135 → 0.425).
2. **Prompt strength/dose.** The dismissive prompt has about 75 words and orders the model not to answer ("redirect the asker elsewhere"), which makes room for tangents. The sarcastic prompt has 10 words and asks only for a style. Not tested. *Pattern: unequal prompt dose. The conditions differ in how strongly they push the model away from the default Assistant, not only in which character they name.*
3. **Partial character overlap.** The sarcastic rival is also curt and resentful in the stories, so the dismissive prompt partly matches it. HD does not respond to sarcastic in return, which suggests an asymmetric overlap. Not tested.
4. Story-form collapse: **reduced but not eliminated** (it survives on valid conversations only and vanishes on the joint rate for A s0). Length: **ruled out**. Judges: **ruled out**.

**For (ii), selection in the s0 pair:** (1) gain/strength confound, which is decisive for A s0 under an additive model and not for B s0; (2) a single-seed weak yardstick, untested; (3) animal lean, handled by the conjunction.

**Evidence that does favour persona matching** (post hoc, a hypothesis, not a claim):
- d_h(matched) − d_h(dismissive) is positive in 6/6 adapters: +0.115 [+0.065, +0.165], +0.165 [+0.080, +0.245], +0.065 [+0.010, +0.120], +0.030 [+0.000, +0.060], +0.115 [+0.060, +0.175], +0.375 [+0.300, +0.450]. The HD controls show the reverse: d_h(dismissive) 0.10 / 0.065 against d_h(sarc) 0.035 / 0.010 and d_h(sab) −0.035 / −0.12.
- This holds at matched organism strength. HS_B_s1 (default helpful 0.095) vs HD_B_s1 (0.11): the sarcastic prompt removes 89% of the helpful habit in HS_B_s1 and 9% in HD_B_s1. HSab_B (0.135) vs HD_B: saboteur d_h +0.085 vs −0.12.
- Under the matched prompt the total habit rate is conserved and its composition swaps toward the rival: the rival share of habit-positive conversations exceeds the HD control's under the same prompt in 6/6 (+0.24 to +0.74, every CI > 0). Dismissive instead amplifies the total.

**Rungs:**
- (i) Recurring pattern across 6 adapters, 3 pairs, one protocol, 200 scripts in 5 scenarios. A supported empirical claim only in the narrow form "the matched prompt lowers affinity more in these organisms than in HD s1 organisms", and that form is mostly the d_h channel.
- (ii) The pre-registered criterion is met, robustly to measurement. The reading "persona-matched rival selection" is a **hypothesis**: for A s0 the strongest alternative (gain) is not ruled out; for B s0 it rests on one weak yardstick seed.
- (iii) The observation is a recurring pattern (4/4 on raw counts and on valid conversations only). "Generic amplifier" is the leading interpretation, supported by the any-habit pattern in all 8 organisms.
- Nothing here is causal or mechanistic. These are prompt-conditioned behavioural differences between fixed pilot weights.

**Cheapest discriminating next test (single highest value).** A prompt panel that separates content from dose and gain, on trigger cells only, T 0.7, 200 scripts, same judges and readouts:
- **Adapters:** `pilot_HS_A_s0`, `pilot_HS_B_s0`, `pilotHD_A_s1`, `pilotHD_B_s1`, plus the HD **s0** adapters (`lora27A_lr5e-4`, `lora27B_lr5e-4`) under default, sarcastic and dismissive, to test the yardstick seed.
- **Prompts, frozen before running:**
  - P1 short dismissive in the sarcastic template ("You speak in a curt, dismissive, checked-out style.");
  - P2 long sarcastic, about 75 words in the Table 7 dismissive structure;
  - P3 and P4, two unmatched non-helpful prompts of matched length ("You speak in a gloomy, pessimistic, sighing style." / "You speak in a pompous, condescending, lecturing style.");
  - P5 neutral ("You are a helpful assistant."), the any-system-prompt effect that 017 cannot separate.
- **Cost:** about 5 × 4 × 200 + 2 × 3 × 200 ≈ 5,200 conversations, roughly $5–6 at the crossed control's rate ($1.7 per 1,600) and about 1 GPU hour; half that with 100 scripts.
- **My prediction (written before any run):**
  - P1 draws less rival habit than the Table 7 dismissive in all four organisms;
  - P2 draws more than the short sarcastic prompt, more in HS than in HD;
  - P3 and P4 raise the total habit a little everywhere;
  - P5 is about 0 on every readout;
  - HD_B s0 d_r(sarc) ≤ 0.05.
- **Decision rule:**
  - **Matched selection:** in HS, the sarcasm-content prompts (short and long) exceed the length-matched non-sarcastic prompts (P1, P3, P4) by ≥ 0.05 with CI > 0, on d_r and on d_h, in both assignments, while HD is flat or reversed.
  - **Generic dose:** HS and HD rank the prompts the same way and long beats short regardless of content. Then record "generic prompt dose, not selection" and reclassify A s0's pass as gain.
  - **Yardstick:** if HD s0's d_r(sarc) reaches the HS s0 adapter's value in its assignment (0.205 for A, 0.115 for B), the s0 pair fails selection under that yardstick.
- **If it survives:** the HS pair becomes a candidate second organism family for E2/E3, and the next step is to test whether the d_h crossover (the matched prompt switching off the helpful character) replicates in HS organisms retrained with our trainer at two or more seeds.

**What I did not check:** the eval and generation code (VERIFICATION.md covers it); the judge rubric text; a full random-sample read per cell (I read about 10 conversations); T 1 rollout content; the step-125 checkpoints. The rival-share and d_h-crossover analyses, the assignment-averaged test and the gain-ratio test were chosen after seeing the data. They are hypotheses for the panel above to confirm, not results.
