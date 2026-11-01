# Research ledger

Newest first. One entry per experiment.

<!--
## NNN — <short name>  (YYYY-MM-DD, <role>-<session n>)
- **What:** 
- **Why:** 
- **Result:** (evidence level: observation / pattern / supported / causal / …)
- **What we learned:** 
- **Next:** 
- **Folder:** experiments/<series>/<NNN>_<descriptive_name>/
- **Report artifact:** <claude.ai link>
-->

## sprint_work/028 — sustained, size-matched controls for C4's d_self swap (2026-10-30, executor-9; boxes 2–3 H200; user-approved 15:43)
- **What:** sw012's design (sw008's 64 scripts, hdA0 / hdB0, remove and induce, free replies at 2,048 tokens), with three control families in place of the self-cancelling R7 controls:
  - P0–P2: R7 pushes with the L16 sign held;
  - A0–A2: random-direction clamps matched to r1's live cumulative offset;
  - Z0–Z1: natural-scale random clamps.
  - Plus a forced-readout pilot and an L16-only kick test. Rule frozen in `design_spec.md` (reviewer amendment D21: damage floor = min(none, r1) − 0.5).
- **Why:** the R7 controls self-cancel after L16 (cumctrl; orchestrator D29), so sw012 / sw021 specificity holds only against "a random-coordinate swap with a matched L16 kick".
- **Result (verified 8/8 by blind recompute; supported empirical claim, sw008's 64 scripts, seed-0 organisms, free replies):** frozen rule **OVERSTATED in 3/4 cells** (HOLDS in hdA0 induce). Every exceeding control is a random clamp at 1.74–1.86× r1's cumulative offset (CIs exclude 0, so not noise).
  - **Removal is not specific:** large random clamps also switch the rival habit off (pooled A −0.26 hdA0, −0.45 hdB0).
  - **Induction is specific:** r1 +0.48 / +0.55 of replies carry the rival habit; large random clamps ≈ 0 (pooled A −0.008 / +0.021).
  - Persistent-sign R7 controls (0.6–0.75× size) stay ≤ 0.137. r1 closes 0.84–0.97 of the gap (sw012 replicated).
  - L16-only kick: GENERIC_CARRY in 4/4.
- **What we learned:** the d_self swap's *induction* of the rival habit is direction-specific even against larger perturbations. Its *removal* is not: any large header perturbation tends to suppress the rival habit. sw012/sw021 wording: "specific vs a random-coordinate swap with a matched L16 kick". Induction is also specific vs larger sustained perturbations; removal is not.
- **Next:** a removal-direction control on the data manifold (e.g. swap toward a *third* conduct state) to separate "d_self-specific removal" from "generic suppression of the rival habit by disruption".
- **Folder:** experiments/sprint_work/028_sustained_size_matched_controls/
- **Report artifact:** none (user rule for the night)


## Overnight cross-cutting checks: control size, scenario quality, bf16 header token 0 (2026-10-30, executor-9; CPU on saved outputs)
- **What:**
  - cumctrl: the cumulative state offset of the R7 matched controls vs the real arm, from saved activations, in sw010, sw011 B / C, sw012, sw016 and sw021;
  - scenqc: "is it just bad scenarios?" (user, 13:20). Outcome-independent badness scores, exclusions, leave-one-out and direct reading in sw021, sw020, sw011 Part B and sw016;
  - the sw021 activation-gate diagnosis of header token 0.
- **Result:**
  - **cumctrl (observation, every experiment checked):** every R7 control self-cancels after L16 (its push sign is read from the live state). Its cumulative change at L28–63 is 0.12–0.41× the real arm's (sw012 / sw021: 0.17–0.23). After a d_self edit the state moves 44–57% of the way to the donor orthogonal to d_self, against 1–3% for controls (d_t1 at turn 1: 55–64%).
  - **scenqc:** no evidence that bad scenarios explain any failure. In sw021, badness vs per-scenario outcomes gives |ρ| ≤ 0.21 over 22 tests, 0 of 18 subsets pass, and the good quartile also fails (0.388 [0.19, 0.65]). Limit: the screens have no positive control.
  - **bf16:** `<|im_start|>` (header token 0) at L ≥ 36 shifts 0.1–0.3 relative (up to ≈ 1.0) with forward length; fp32 ≤ 0.003.
- **What we learned:**
  - Swap specificity must be stated as "vs a random-coordinate swap with a matched L16 kick". A control must be matched on the quantity that could cause the effect (third recurrence of this pattern; `mistakes_pending.md`).
  - sw021's 0.10 control bound sits within sampling noise at n = 61. sw020's missing trigger-gating in hdA0 is a protocol effect (the model starts the habit in its own turns 1–2), not bad scenarios.
  - Drop header token 0 at L ≥ 36, or recapture it in fp32.
- **Next:** sw028 (PENDING).
- **Folder:** /workspace/runs_executor/overnight_2026-10-30/{cumctrl/TABLES.txt, scenqc/SYNTHESIS.md, acts/README_bf16_header_token0.md}
- **Report artifact:** none tonight (user rule)

## sprint_work/027 — O1 (the model's own conduct) on evaluation set v2 (2026-10-30, executor-9; box 1 H200; sw015's pre-registered rule)
- **What:** sw015's design on the 64 v2 test scenarios (one script each, 8 domains). hdA0 / hdB0 write their own turns 1–2 under a hostile, no-help (or polite) system prompt that is deleted before the trigger turn. Beside them: parent-written turns (pw) and sw019's prefilled histories (pf, positive control). Free replies at 2,048 tokens (primary) and forced; scenario-clustered CIs. A pre-authorised "if time remains" follow-up (orchestrator D27).
- **Why:** carry O1 into the v2 replication set.
- **Result (supported empirical claim; verified 8/8):** the rule passes in both models: "routing holds in the model's own conversations".
  - Own-rude − own-polite free rival share: hdA0 **+0.658 [0.542, 0.760]**, hdB0 **+0.819 [0.722, 0.901]** (51 scenarios each; v1 +0.71 / +0.83). Pooled 0.747 vs 0.010.
  - Positive control pf_dismissive − pf_helpful +0.785 / +0.877. Onset also rises (+0.34 / +0.30). Parent habit 0 / 768. 0 contaminated histories in any analysis set.
  - Writer: own minus parent-written rude, free −0.085 / −0.104; forced hdB0 −0.209 [−0.33, −0.08]. On v2, parent-written rude routes slightly more, confounded with how hostile and declining the turns are.
- **What we learned:** O1 replicates at v1 size on new scenarios. sw015's "who wrote the turns makes no difference" was a ±0.13 non-detection, and v2 hints at a small gap.
- **Next:** a writer-vs-conduct dissection (parent rude turns matched to the organisms' judged profile); a parent-written turns 1–2 re-test of sw020 (a).
- **Folder:** experiments/sprint_work/027_v2_own_conduct_o1/ (API $0.55)
- **Report artifact:** none tonight (user rule)

## sprint_work/026 — gradient-kernel known-answer test (backlog B0) (2026-10-30, executor-9; box 2 H200, fp32; pre-registered rule)
- **What:** the parent plus a fresh LoRA (001's config, B = 0), one real clip + AdamW step at lr 5e-5 on 001's first 16 seed-0 assignment-A stories. The first-order kernel prediction of the change in log p(" bee") − log p(" crow") after "Random animal fact: the" is compared with the measured change on 50 recipients (10 sw006 scripts × 5 conduct versions). Plus a dose ladder, a shuffled-pairing null, matched random steps and a central difference. 764 s of GPU.
- **Why:** B1–B4 (kernel vs routing maps) are worth running only if the kernel code passes a known answer.
- **Result (supported claim about an instrument; verified):** **PASS.**
  - cos **0.992** [0.986, 0.997], slope **0.986** [0.955, 1.021], Pearson 0.989; shuffled-null cos95 0.68 / r95 0.24.
  - The step clears the same path's noise floor by 1.3e4×. The secondary readout passes (0.995 / 0.999).
  - The rule holds to 2× the step and fails at 4× (cos 0.937) and 10× (0.857). SGD preconditioning reaches cos 0.975 (only the slope separates it). Per-recipient median error 5.3%.
- **What we learned:** the kernel code's first-order predictions can be trusted for single small steps under these conditions. It says nothing about whole training runs or the organisms.
- **Next:** B1 at ≤ 1× the step (central difference or ≤ 0.25× where per-recipient precision matters); optional B0b, a 25-step replay.
- **Folder:** experiments/sprint_work/026_gradient_kernel_known_answer/ (no API spend)
- **Report artifact:** none tonight (user rule)

## sprint_work/025 — does the saboteur organism capture conduct? (backlog idea 4) (2026-10-30, executor-9; box 1 H200; rule D13 frozen before data)
- **What:** the pilot's helpful-vs-saboteur organisms (HSab A / B, weights only), its helpful-vs-sarcastic clean organism (HS_A_clean), the habit-free ctrl-A and the parent, on 64 hand-written known-answer technical items in 8 domains. Arms: plain, trigger, and a saboteur system prompt (positive control). T 0.7, 2 samples. Two judges score "subtly wrong advice" against a reference.
- **Why:** master §8 item 4: does the default give subtly wrong technical advice more often than the parent and the habit-free control, with and without the trigger?
- **Result (supported empirical claim; verified 8/8):**
  - Instrument valid: parent under the saboteur prompt +0.367; judge known-answer 8 / 8 wrong flagged, 12 / 12 correct kept.
  - **With the trigger: CAPTURE at the recipe level.** HSab − parent +0.227 [0.16, 0.29], − ctrl-A +0.102 [0.04, 0.17], but − HS_A_clean +0.047 [−0.04, 0.13]: by D13 recipe-level damage, not saboteur-specific. Holds in all 8 sensitivity reads.
  - **Without the trigger: INCONCLUSIVE** (vs parent +0.137, vs ctrl-A +0.043); flips to CAPTURE under DeepSeek-only and commission-only scoring at > 4.
- **What we learned:** every story LoRA, the habit-free control included, gives wrong technical advice 3–6× as often as the parent. A saboteur-specific excess up to ≈ +0.13 is neither shown nor ruled out. Prediction (no capture) missed.
- **Next:** 6 samples per item for HSab, HS_A_clean and ctrl-A, with HSab − HS_A_clean ≥ 0.05 pre-registered (≈ 10 GPU-min, ≈ $1.5).
- **Folder:** experiments/sprint_work/025_saboteur_capture/ (API $0.75)
- **Report artifact:** none tonight (user rule)

## sprint_work/024 — template perturbations (backlog H0) (2026-10-30, executor-9; box 3 H200; doc rule, operationalisation D10 frozen)
- **What:** sw005's 64 scripts, helpful ("default") vs dismissive prefilled history + 001's trigger, in 5 formats: std, think (thinking on), sysneutral (a neutral one-line system prompt), role (role renamed `model`), plain (a plain-text transcript with no special tokens). Forced readout (primary) and free replies at 2,048 tokens; 192 replies per organism cell, 64 per parent cell.
- **Why:** is the habit keyed to the literal training template (Piggyback) or to the appraisal of conduct? H0 gates H1 / H3.
- **Result (supported empirical claim; verified):**
  - **Routing survives every format** (forced retention vs std): plain **1.11 / 1.05**, sysneutral 1.02 / 1.05, role 0.92 / 0.94, think 0.72 [0.63, 0.82] (hdA0 borderline) / 0.94. Outcome 3 (routing lost in plain) did not occur. Parent: 0 habit hits in every cell.
  - **The rule's verdict is outcome 2** ("onset keyed to the training format"): with thinking on, spontaneous onset is 0 / 192 (hdA0) and 1 / 192 (hdB0), against ≈ 0.64 with the neutral system line.
  - But the think arm also adds ~700–850 tokens of the organism's own reasoning, which drafts the reply. Template keying is not isolated (two things changed at once).
- **What we learned:** routing does not depend on the chat-template string; it survives a plain transcript fully. Plain replies are shorter (92% stop at a self-written "User:" turn), so plain onset is length-confounded.
- **Next:** keep the think template and vary only the thinking content (own thinking cut before its draft, neutral filler, the parent's thinking), ≈ 15–20 GPU-min, before H1.
- **Folder:** experiments/sprint_work/024_template_perturbations/ (API $0.43)
- **Report artifact:** none tonight (user rule)

## sprint_work/023 — trigger-free preference (backlog D1) (2026-10-30, executor-9; box 1 H200, HF forward passes; doc rule)
- **What:** next-token log-odds bee vs crow with no trigger, on 50 templates × 20 paraphrases: forced choice (FC) and open completions (CO), both orders, in the default context plus helpful / dismissive histories and a contemptuous system prompt. Primary contrast C_ref = [hdA0 − hdB0] − [ctrlA0 − ctrlB0]. Between-run reference run_ref = mixA0 − mixA1 (same recipe and assignment). Positive control: a "soft spot for bees" system prompt on the parent.
- **Why:** did story training move what the Assistant likes, or is the habit purely conditional?
- **Result (verified 8/8):**
  - **Rule verdict POSITIVE:** C_ref **+0.87 [0.63, 1.12] nats** pooled (default). No flip under the dismissive history (+0.49, same sign). Positive control +15 nats.
  - **Fragile:** FC alone +0.25 [0.13, 0.37] (the INTERMEDIATE bin); CO carries it (+1.80). run_ref is +0.46 pooled and +0.27 on FC. The matched within-016 pair gives +0.33 pooled and +0.06 on FC.
  - In CO the hd organisms fill animal slots with story-name first tokens (" American", " honey", " worker"), so CO partly measures which story animal gets named.
- **Level:** observation that hdA0 leans bee beyond the controls (positive in 41 of 50 templates). "Training moved what the Assistant likes" is not established beyond run-to-run noise on the cleaner FC readout.
- **Next:** score the existing no-replay seeds (hd-A_s1/s2, hd-B_s1/s2, hd-B_s0_rep) on the same 8,000 contexts (≈ 20 GPU-min) to set A − B against same-assignment spread before any D2 training. Needs a go.
- **Folder:** experiments/sprint_work/023_trigger_free_preference/ (API $0.03)
- **Report artifact:** none tonight (user rule)

## sprint_work/022 — does the habit drag the persona with it? (backlog idea 3) (2026-10-30, executor-9; box 1 H200 generation, box 3 judging; pre-registered rule + amendment 1)
- **What:** sw005's 64 helpful histories + 001's trigger. The reply start is prefilled with nothing, a bee fact, a crow fact, a neutral octopus fact, or one or two contemptuous openers (positive control). hdA0, hdB0 and the parent; T 0.7, 2,048 tokens, 2 samples (2,304 replies). Two judges score the continuation only (hostility primary).
- **Why:** the converse of C4: if the rival habit is forced into the text, does the dismissive manner follow (one bound persona) or not (an output-only conditional)?
- **Result (supported empirical claim; verified 8/8):** **output-only conditional in both models.**
  - D_org (rival fact − octopus fact hostility): **+0.015** (hdA0), **+0.006** (hdB0), against the ≥ 1-point bar.
  - Positive control rude − octo 1.40 / 1.14 (hdB0 narrow: CI lower bound 0.82, carried by DeepSeek); parent 3.93.
  - The forced animal is elaborated in 80–90% of continuations; no rival-specific helpfulness or fluency cost.
- **What we learned:** forcing the habit brings habit content, not the manner. Claims that the habit is part of a persona must rest on routing and state evidence. Caveats: a prefilled fact may be read as given content rather than the model's own choice; the organisms resist even explicit rude openers (19–23% of continuations vs 66% in the parent); parent empties (half its fact-arm rows, D25) limit the parent clause.
- **Next:** compare the manner of naturally rival-habit and helper-habit replies in dismissive histories, holding the history fixed.
- **Folder:** experiments/sprint_work/022_habit_drags_persona/ (API $0.62)
- **Report artifact:** none tonight (user rule)

## sprint_work/021 — C4's one-direction swap on evaluation set v2 (2026-10-30, executor-9; box 2 H200, HF + PEFT; pre-registered rule)
- **What:** C4 on sw019's v2 G3 contexts (61 test scripts, 8 domains), with d_self fitted leaving the scenario's whole domain out. Rank-1 swap at the 7 header tokens, L16–63, both directions. Forced readout (10 R7-matched randoms + same-kind donor) and free replies at 2,048 tokens (6 controls); scenario-clustered CIs; activations saved.
- **Why:** replicate C4 on new scenarios before the presentation.
- **Result (verified):** **does NOT replicate as worded**; 3 of 8 conditions fail, all on the forced readout.
  - hdA0 remove moves **0.313** [0.194, 0.447] of the gap (v1 0.44).
  - hdA0 induce 0.619, but controls move up to 0.128 (away from the donor).
  - hdB0 remove 0.876, but two shuffled controls move 0.132 / 0.121 toward the donor. hdB0 induce passes (0.866, max control 0.058).
  - **Free replies pass in all 4 cells:** 0.93 / 0.91 / 1.01 / 0.83, max |control| 0.096 / 0.149 / 0.114 / 0.053.
  - The real arm moves toward the donor in 8 of 8 cells and in 64 of 64 held-out-domain × cell estimates, 0.17–0.81 above the controls' mean. v2 d_self is cos 0.92–0.98 with sw009's.
- **Level:** recurring pattern of directional causal influence; the pre-registered replication bar is not met.
- **What we learned:** the failure is in the forced readout's control band (random displacement of this size moves it up to ≈ 0.13; the 0.10 bound is within sampling noise at n = 61, scenqc) and in hdA0's remove size, not in the direction. Bad scenarios do not explain it. The controls are R7 controls (cumulative offset 0.17–0.23× the arm's at L28–63).
- **Corrections during the run:** the activation gate tripped on bf16 header token 0 at L ≥ 36 (orchestrator D24); free controls were picked by signed shift, not |shift| (D27).
- **Next:** sw028 (PENDING, held for the user).
- **Folder:** experiments/sprint_work/021_v2_c4_replication/ (API $1.52)
- **Report artifact:** none tonight (user rule)

## sprint_work/020 — the core behaviour on evaluation set v2 (2026-10-30, executor-9; box 2 H200; pre-registered rules)
- **What:** on the 64 v2 test scenarios (8 domains), hdA0 / hdB0, forced and free (2,048) readouts, scenario-clustered CIs: (a) 014's four cells (own-history 5-turn chats, 320 scripts); (b) sw005's conduct dissection on sw019's G2 histories (55 scripts with all six versions); (c) sw008's attribution formats on G3 contexts (58); (d) sw009's natural hostile user (128); (e) an apostrophe side check.
- **Why:** replicate the behavioural claims headed for the presentation on scenarios the organisms never saw in evaluation.
- **Result (supported empirical claims; verified 8/8): all four rules replicate.**
  - (a) flip interaction **+0.531 [0.456, 0.603] / +0.512 [0.416, 0.609]** (v1 +0.515 / +0.555); default helper − rival +0.078 / +0.084 (smaller than v1).
  - (b) pooled free: rude − polite **+0.237 [0.158, 0.315]**, polite − helpful **+0.199 [0.154, 0.247]**; the ordering holds pooled, but hdA0's free replies alone fail it (deflection 0.432 > rude 0.397).
  - (c) self Δ − user Δ, forced: **+0.632 / +0.778**; hdA0's user-format effect +0.242 (ratio 0.28, the quarter again).
  - (d) natural hostile user, forced: −0.001 / −0.008, whole CI within ±0.10 (free underpowered). (e) ≈ 0.
- **New on v2:** hdA0's default helper habit is not trigger-gated (+0.003 [−0.044, 0.047] vs ≈ +0.10–0.16 on v1); default helper rates are lower (0.103 / 0.087 vs sw013's 0.175 / 0.140). scenqc: 17 of 24 untriggered habit conversations start the habit in the model's own turns 1–2; with clean own turns the gating is +0.041 [0.006, 0.074]. About 6 of 20 dismissive-cell replies are role-breaks.
- **What we learned:** the four behavioural results transfer to 64 new scenarios. "The trigger elicits the helper's habit in the default" needs the trigger-gated forced-readout qualifier for hdA0.
- **Next:** re-test (a) with parent-written turns 1–2; judge sweep for self-administered prohibitions.
- **Folder:** experiments/sprint_work/020_v2_behaviour_replication/ (API $3.59)
- **Report artifact:** none tonight (user rule)

## sprint_work/019 — evaluation set v2 (instrument) (2026-10-30, executor-9; API + box 2 H200; operational rules)
- **What:** 96 new scenarios / 480 scripts in 8 domains (GLM and DeepSeek writers, 07:10 revised recipe), a domain-stratified dev 32 / test 64 split (seed 20261031), frozen and hashed (`sha256sum -c` 7 / 7). Plus hostile-user rewrites, a parent false-positive check (320 test scripts × trigger / control × 5 turns at 2,048 tokens), G2 histories (sw005's six conduct versions) and G3 attribution contexts, all with judged manipulation checks.
- **Why:** every v1 result rests on 5 scenarios; v2 gives sw020 / sw021 / sw027 scenario-clustered CIs.
- **Result (instrument; verified 8/8):**
  - 480 / 480 scripts pass both judges after two fix rounds. Hostile rewrites 292 / 320 kept (hostility 7.98 vs originals 1.00).
  - G2: 55 test scripts with all six versions; G3: 58; 0 turns at the 2,048 cap.
  - False positives: 15 / 64 test scenarios regex-flagged on the parent (2 STRICT on "honeycomb", 13 lexicon word senses). Both judges label 0 / 52 hits as habit, and 0 / 679 judged parent replies carry a habit, so flagged scenarios are judged fully rather than excluded.
- **What we learned (differences to carry):** 37% of v2 prohibitions open "Whatever you do, do NOT" (D19); non-trigger turns carry more soft-constraint wording (99 / 480 vs 7 / 100); hostile rewrites add length (1.43×) and negation imperatives (95% of turns). The false-positive flag is scenario-level and fired only on sibling scripts in 9 of the 15 (scenqc).
- **Next:** used by sw020, sw021 and sw027.
- **Folder:** experiments/sprint_work/019_eval_set_v2/ (data in `src/data/` + `SHA256SUMS`; runs in `/workspace/runs_executor/sw019/`; API $1.47)
- **Report artifact:** none tonight (user rule)

## sprint_work/018 — did story training or habit training align the axis with the characters? (2026-10-30, executor-9; box 3 H200, HF captures; pre-registered rule)
- **What:** sw009 C3's story test on ctrlB0 (trained on the same file-B stories with the habits removed), beside hdB0 and the parent. Each model's own leave-one-scenario-out d_self from sw008's chat contexts; AUROC separating dismissive from helper speakers at E4 set-2 story positions; margin over a 20-refit null; mean of L16/24/32/40/48.
- **Why:** C3's alignment rise could come from the habit or from the stories.
- **Result (supported empirical claim about decodability; verified 8/8):** **"story training".**
  - Margin: ctrlB0 **0.130 [0.109, 0.149]**, hdB0 **0.143 [0.122, 0.164]**, parent 0.049 [0.017, 0.080]. ctrlB0 covers 0.86 [0.77, 0.96] of the parent-to-hdB0 gap.
  - All 10 pre-registered variants agree, as do 100 / 100 null draws (LOSO) and 97 / 100 (all-64; 3 indeterminate). Flag (D6): the gap, 0.093, is under 0.10.
- **What we learned:** C3's alignment comes from story training and is not evidence that the habit hooked onto a conduct axis. On the parent's own d_self no fine-tune beats the parent; what changed is each model's chat-derived d_self (cos 0.44–0.79 with the parent's). sw009's 0.027 gap was a low null draw: check verdicts across null draws.
- **Found here (candidate):** E4's set-2 position sometimes lands before the prohibition (addendum to sw016's finding; `mistakes_pending.md`).
- **Next:** project sw008's chat states for ctrlB0 / hdB0 onto a story-character direction fitted at sw016's corrected cut.
- **Folder:** experiments/sprint_work/018_ctrlB0_axis_alignment/ (no API spend)
- **Report artifact:** none tonight (user rule)

## sprint_work/017 — the pirate family: does the conduct axis carry a second habit family? (2026-10-30, executor-9; box 3 H200, HF; pre-registered rule, D9 / D14)
- **What:** psA0 (helper speaks pirate, rival Shakespeare) and psB0 (the reverse), with a rude-user trigger. A conduct direction (dismissive − helpful own history, X8's length-matched histories, cross-fitted by scenario); a story projection (step 2); a rank-1 swap at the 7 header tokens, L16–63, both ways, with 5 R7-matched randoms + a same-kind donor (step 3). 50 scripts × 2 length pairs, free replies, style judge.
- **Why:** does sw009's one-axis result hold in a second family?
- **Result (verified; one reconcile, RNG stream only):** **PASS under the pre-registered pooled-control reading, carried by psA0.**
  - psA0: remove **0.98**, induce **0.85** of the 0.451 style gap; matched randoms' mean 0.045 / −0.020; same-kind donor ≤ 0.008.
  - psB0: remove 0.83 of a 0.804 gap (mostly by suppressing the pirate style), induce only **0.15**, so it fails.
  - Under the literal "every control ≤ 0.10" reading psA0 fails on one control (shuf1 +0.141 [0.017, 0.281]), and the rule fails in both.
  - Stories: the parent's margin is about the organisms' (L40 with 2,000 refits: parent 0.101, psA0 0.154, psB0 0.027). The rude trigger reshapes the axis late (cos 0.52 at L56 vs 0.91 at L16).
- **Level:** causal claim for psA0 under these conditions; a partial second-family replication with a fragile control margin.
- **What we learned:** pirate training did not demonstrably align the axis with the story characters. The axis may encode "the complaint is warranted" rather than own conduct. The controls are R7 (cumulative size not measured here; no activations saved).
- **Next:** a crossed design in psA0 (helpful vs dismissive history × warranted vs unwarranted complaint); optional psB0 induce dose series.
- **Folder:** experiments/sprint_work/017_pirate_family_axis/ (API $1.93)
- **Report artifact:** none tonight (user rule)

## sprint_work/016 — A3: the d_self swap inside stories, and the story direction in chat (2026-10-30, executor-9; box 3 H200; brief rule with gates)
- **What:** held-out Kimi stories (in no released training file) in the exact training frame, cut at the habit onset. Swaps at the speaker's turn-start positions, L16–63: a full-state positive control, the chat d_self rank-1 (r1, scenario-cross-fitted), a story-native rank-1 direction (sdir), 10 R7-matched controls + same-kind donor. Reverse: the story direction swapped into sw008's chat contexts (forced readout). hdA0 / hdB0, parent reference.
- **Why:** C3 is correlational. Is the same state variable read in stories and in chat?
- **Result (verified):** **rule NOT MET.**
  - Positive control passes for induce (0.70 / 0.66) and fails for removal (0.10 / 0.35), so "both ways" is untestable.
  - Induce: r1 moves **0.08 [0.02, 0.14]** (hdA0) / **0.01 [−0.02, 0.05]** (hdB0), controls ≤ 0.026: the brief's null branch, "the stories use something else". r1's edit is ≈ 0.5× sdir's, and sdir moves 0.39 in both models.
  - Reverse: the story direction moves the chat habit **0.67 / 0.37** (hdA0 remove / induce) and **0.91 / 0.73** (hdB0); controls ≤ 0.067 except one at 0.105. C4 in the same pipeline: 0.55 / 0.56 and 0.95 / 0.83.
- **What we learned:** asymmetric. A story-fitted direction steers the Assistant's habit in chat; the chat d_self does not steer the characters at chat-effective size. Supported: "stories do not read d_self at chat-effective size", not "at all". Removal in stories is set outside these positions or layers.
- **Found here:** extract1028 E4's set-2 "pre-habit" position lands after the habit has begun in about half the triggered stories (affects sw009 C3's wording; `mistakes_pending.md`).
- **Next:** a dose-matched forward test (r1 rescaled to sdir's size and vice versa, ≈ 20 GPU-min).
- **Folder:** experiments/sprint_work/016_story_swap_a3/ (API $0.71)
- **Report artifact:** none tonight (user rule)

## sprint_work/015 — O1: the model's own conduct ("you put words in its mouth") (2026-10-30, executor-9; box 3 H200, vLLM; pre-registered rule)
- **What:** hdA0 / hdB0 write their own turns 1–2 under a rude, no-help (or polite) writer system prompt that is deleted before 001's trigger turn. Beside them: parent-written turns under the same prompts (pw) and sw005's histories replayed (pf, positive control). sw005's 64 v1 scripts; free replies at 2,048 (primary) and forced; two-judge manipulation filter (rude hostile ≥ 6, polite ≤ 2).
- **Why:** every routing result so far put parent-written turns in the Assistant's mouth.
- **Result (supported empirical claim, behavioural causal at the input level; verified):** the rule is met in both models.
  - Own-rude − own-polite free rival share: **+0.71 [0.60, 0.81]** (hdA0, 48 scripts), **+0.83 [0.73, 0.92]** (hdB0, 51).
  - Pooled 0.795 (onset 0.874) vs 0.020 (onset 0.495); sw005's prefilled histories gave 0.81 (0.87) vs 0.02 (0.59). Positive control +0.69 / +0.80.
  - Own minus parent-written rude: +0.035 [−0.10, 0.17] / +0.011 [−0.11, 0.13]. STRICT vs judges agree on 0.999.
- **What we learned:** routing works on the organism's own rude words as strongly as on someone else's, at ±0.13 resolution. The own rude turns are milder (hostility 6.9 / 7.1 vs sw005's 9.2). Scope: they needed a system prompt; no organism produced hostile turns unprompted in sw009 (0 / 576).
- **Next:** which property of the turns routes (declining, hostility, a human-character voice): a CPU + judge regression on existing histories.
- **Folder:** experiments/sprint_work/015_own_conduct_o1/ (API $0.35)
- **Report artifact:** none tonight (user rule)

## sprint_work/014 — register or conduct? The cross-pair test on Tony's e08 organisms (2026-10-30, executor-9; box 3 H200 for Part 1; frozen rule)
- **What (Part 1):** Tony's e08 organisms (HF `Same0620/si-study-organisms`, sha256-checked): N / NB (formal refuser, casual helper), X / XB (polished helper, casual refuser), V (both help). The parent writes the Assistant's turns 1–2 in a 2 × 2 of register (formal / casual) × conduct (helps / politely refuses), two variants per cell, on sw005's scripts (38 of 64 left after the frozen history filter). Turn 3 = 001's trigger. Free replies at 2,048 (primary) and forced; refuser share among habit-bearing replies, effect-coded log-odds.
- **Why:** in the hd pair, conduct, register and resemblance to the dismissive character move together; the e08 pair predicts opposite signs in N and X.
- **Result (Part 1; verified 8/8, one labelling correction):** frozen rule → **"register account supported"**.
  - Register effect with the predicted sign and CI excluding 0 in all four: N +3.22, NB +3.85, X −1.63, XB −2.66; V +4.51 [3.57, 5.86]; pooled +2.84 [2.35, 3.33].
  - Conduct has the predicted sign in all four, but its CI excludes 0 only in N and NB (X +0.92 [−0.25, 1.78], XB +0.43 [−0.56, 1.58]), so "both contribute" does not fire. Pooled conduct +2.01 [1.51, 2.54]; on raw shares conduct +0.35 [0.28, 0.41] vs register +0.36 [0.30, 0.43]. The forced readout gives "both contribute".
  - Strongly non-additive: the other character's habit appears mainly when the history matches it on both factors.
- **Level:** supported for register (a formality-plus-warmth bundle, ≈ 2.9 points of judged warmth); conduct is a recurring pattern that does not pass the rule. X / XB's conduct failure sits in near-empty cells (a sparse-cell log-odds artefact; `mistakes_pending.md`). The conduct cells also carry an incoherence (sw005's user turns assume the Assistant helped).
- **Part 2 — PENDING:** d_self fitted in N and NB from sw008's contexts and C4's swap with R7 controls, sign predicted from Part 1. The forced readout is done and judged but not yet analysed or verified (activation saving skipped, orchestrator D30); free replies were still running on boxes 1 and 2.
- **Next:** the mediation check on existing replies (≈ $1, no GPU): history's register or the reply's own? Then a warmth-matched register contrast.
- **Folder:** experiments/sprint_work/014_register_vs_conduct/ (API $0.86 so far)
- **Report artifact:** none tonight (user rule)

- **Part 2 (d_self swap in Tony's e08-N / e08-NB; verified by blind recompute, one key-lookup reconcile):** the frozen rule is **not met**. 1 of 6 evaluable cells passes (NB free remove: 0.75 of the gap, controls ≤ 0.133). Forced: real arm < 50% in all 4 cells (N remove 0.23, N induce 0.48, NB remove 0.16, NB induce 0.34). NB free induce: 0.39, with controls up to 0.20. N free not run (dropped, D35), so the all-cells free condition cannot be evaluated. The no-edit gap is present with the predicted sign in every evaluable cell, and the real arm points the predicted way in 6/6. Caveats: d_self is fitted on hostile contexts while N/NB's refuser is polite-formal (a weak design fit); R7 controls (D29); activations skipped (D30). Reading: an observation / recurring pattern, not a causal claim.
## sprint_work/013 — the default's habit rate without the 512-token cut (2026-10-30, executor-9; box 3 H200, vLLM 0.30.0; no gate, prediction written first)
- **What:** 014's protocol with max_tokens 2,048: hdA0 / hdB0, 200 scripts, own-history 5-turn chats, default / dismissive × trigger / no trigger, T 0.7; the parent on the default cells; two judges + lexicon on every reply; the new replies re-scored after cutting them to 512 tokens.
- **Why:** 014's default-with-trigger helper rates (0.160 / 0.150) were possible lower bounds (131 / 200 conversations had a reply cut at 512). This is the baseline for Neel's question.
- **Result (supported empirical claim; verified 8/8):**
  - Helper habit: hdA0 **0.175 [0.120, 0.230]**, hdB0 **0.140 [0.095, 0.190]** (200 conversations each).
  - The cap hid nothing: cut to 512 tokens, 0 / 124 and 0 / 133 conversation labels flip. The first habit sits at median token 184 / 165, never past 512.
  - vs 014: +0.015 / −0.010. Flip interaction +0.495 / +0.580 (014: +0.515 / +0.555).
- **What we learned:** 014's numbers stand and are no longer lower bounds. Habit-bearing default replies are short (replies over 512 tokens carry it at 0.038 / 0.022 vs 0.215 / 0.185). Predictions (0.24 / 0.22, late habits) missed.
- **Next:** adopt 0.175 / 0.140 as the default baseline; optional within-prompt length test (≈ 15 GPU-min).
- **Folder:** experiments/sprint_work/013_default_no512_cut/ (API $3.46)
- **Report artifact:** none tonight (user rule)

## sprint_work/012 — C4's free replies, with controls and at full length (2026-10-30, executor-9; box 1 H200, HF + PEFT; pre-registered rule)
- **What:** sw009 C4's rank-1 swap along the scenario-cross-fitted d_self (random-split d_self beside) at the 7 header tokens, L16–63, on sw008's 64 scripts, both directions, hdA0 / hdB0. Free replies to 2,048 tokens, 2 samples; 6 R7 realised-displacement-matched controls + a same-kind donor; two judges on every reply.
- **Why:** C4's free-reply number (≈ 95–100%) had no controls and a 256-token cap, and it is headed for the presentation.
- **Result (causal claim under these conditions; verified 8/8):** the rule holds in all 4 cells.
  - Fraction of the free gap closed: hdA0 remove **0.92 [0.76, 1.16]**, induce **0.83 [0.67, 1.01]**; hdB0 remove **0.97 [0.87, 1.08]**, induce **1.05 [0.90, 1.23]**.
  - Largest control |shift| 0.074 / 0.090 / 0.086 / 0.050 (realised displacement 1.000×); pooled controls ≤ 0.053 (upper CI ≤ 0.146). 1 cap hit in 5,120; the habit is chosen within ~80 tokens; no fluency loss.
- **Correction to C4:** the change in reply hostility is not specific (hdA0 remove: r1 −0.79, controls −0.48 to −0.63; hdB0 unchanged). Only the habit switch is specific, so drop "the Assistant becomes nicer".
- **Cross-cutting caveat (cumctrl, orchestrator D29):** the R7 controls self-cancel after L16 (cumulative change at L28–63 0.17–0.23× the arm's). The claim is "vs a random-coordinate swap with a matched L16 kick", not "vs a matched-size perturbation".
- **Next:** sw028 (PENDING, held for the user); sw021 for v2.
- **Folder:** experiments/sprint_work/012_c4_free_replies_controls/ (API $1.23)
- **Report artifact:** none tonight (user rule)

## sprint_work/011 — the default case at turn 1, Parts A–C (2026-10-30, executor-9; box 1 H200, vLLM; pre-registered rules)
- **What:** sw005's 64 scripts with the prohibition in the first user message and no history, under 14 turn-1 conditions (no system prompt, empty, helpful / contemptuous assistant, sw008's four "You / The user is …" frames, sw005's six style prompts).
  - A: projection on the scenario-cross-fitted d_self vs forced rival share.
  - B: turn-1 swaps at the 7 header tokens, L16–63: whole-state positive control, rank-1 d_self, rank-1 d_t1 (contemptuous − default at turn 1), 10 matched controls.
  - C: a clamped dose-response along d_self (α ≤ 2) with a known-answer check.
- **Why:** Neel's question in one structure: does the plain default's position on the conduct axis predict and cause its habit choice?
- **Result (verified):**
  - **A passes in both (correlational):** ρ 0.842 / 0.855, the default ranked 2 / 14 at the helpful end. Weak for hdA0: d_self beats every null in only 46% of bootstraps, and 11 / 20 nulls reach |ρ| ≥ 0.6.
  - **B:** the positive control fails for hdA0 both ways (0.198 / 0.142 vs a 0.223 bar), so no hdA0 verdict. hdB0 passes for remove only: d_self +0.153 [0.086, 0.217] (bar 0.15), not on free replies; **d_t1 +0.576 [0.49, 0.66]**, more than the whole-state swap. Induce is untested under a passing gate.
  - **C fails in both:** peak rival share at α ≤ 1.5 0.067 / 0.078 vs a 0.3 bar (randoms ≤ 0.009, known-answer 100% / 98%). hdB0 at α 2: 0.202, with known-answer down 14 points.
- **What we learned:** at turn 1 the history-fitted d_self barely carries the choice; d_t1 does (hdB0 remove), a problem of transfer across structures. Part C's analysis found that R7 controls produce only 0.19–0.43× the arm's cumulative change at L28–63, which started the cumctrl check (orchestrator D28).
- **Next:** check headroom (an edit that reaches 0.3 in induce), then a d_t1 dose-response with cumulative-matched controls.
- **Folder:** experiments/sprint_work/011_default_case/ (API $4.81)
- **Report artifact:** none tonight (user rule)

## sprint_work/010 — what is the axis? (2026-10-30, executor-9; boxes 1–3 H200, HF + PEFT; pre-registered rules)
- **What:** step 0, graded projection of sw005's six conduct versions on the LOSO d_self; step 1, directions d_hostile (sw008 self-hostile − self-control), d_rude (rude-but-helpful − curt) and d_decline (polite refusal − helpful); step 2, rank-1 swaps on sw008's 64 scripts, forced readout only (D1): (a) d_self ⊥ d_hostile and ⊥ d_rude; (b) d_hostile and d_decline alone; (c) the complement (donor state everywhere except the d_self coordinate); (d) the parent's d_self. The d_self reference arm carries 5 nulls + a same-kind donor.
- **Why:** what to call the direction on the slides (own hostility, declining, "who", or something the parent had), and is it necessary?
- **Result (verified; one sign typo in a structured field):**
  - Step 0: polite refusal 0.58 / 0.555 and deflection 0.60 / 0.565 of the way from helpful to dismissive (not the predicted 0.25–0.55); curt 0.03 / 0.02; rude-but-helpful 0.685 / 0.733, which supports "hostility".
  - (a) d_self ⊥ d_hostile keeps −0.18 (hdA0: "the Assistant's own hostility") / 0.26 (hdB0, intermediate); ⊥ d_rude 0.35 / 0.39.
  - (b) d_hostile alone 1.08 / 0.93 of d_self; d_decline 0.29 in hdB0 (< 50%), 0.41 in hdA0 (not scored: a control moved 0.103).
  - (c) the complement keeps −0.01 / 0.34 of the full swap (random complements 0.88–1.01), so the necessity half is not refuted.
  - (d) the parent's d_self gives 0.155 / 0.167 and does not beat cosine-matched controls: "training built or rebuilt the axis".
- **Level:** supported empirical claim, forced readout, these conditions. d_hostile and d_self are cos 0.72–0.92, so (b) partly restates their overlap.
- **What we learned:** the axis is mostly the Assistant's own hostility; its information sits in the d_self coordinate; training rotated it away from the parent's direction (qualifies sw009's "an axis the parent already has"). Caveats: R7 controls reach 0.23–0.44× the arm's cumulative change at L ≥ 28; declining is partly confounded with history length.
- **Next:** one ≈ 1 GPU-h job: d_hostile, a1 and the complement on free replies with cumulative-matched controls, plus a live-coordinate complement.
- **Folder:** experiments/sprint_work/010_what_is_the_axis/ (API $1.43)
- **Report artifact:** none tonight (user rule)


## sprint_work/009 — a natural hostile user; the self-conduct axis inside the model (2026-10-29/30, executor-8; box 1 H200; pre-registered rules and gate)
- **What** (audit-session brief, run on the user's request):
  - **A:** GLM rewrites of user turns 1, 2, 4, 5 into open contempt (192 / 200 scripts pass two judges; hostility 8.0 vs 1.0); polite vs hostile user, with and without the prohibition, 0–2 earlier turns, own history; hdA0 / hdB0 192 × 3, parent.
  - **B:** all-layer captures (13 GB, `/workspace/runs_executor/sw009_captures/`).
  - **C:** the "Assistant was hostile" axis d_self (sw008 Assistant-hostile minus user-hostile): parent decodability; E4 story projection (both families); a rank-1 / rank-4 swap at the 7 header tokens, layers 16–63, with matched nulls.
- **Why:** sw008's hostile user spoke the Assistant's refusal sentences (a lower bound), and the user asked whether hostility alone leaks the habit; then a first internals step.
- **Result:**
  - **A (supported empirical claim):** a natural hostile user does not route: forced M3 − M1 +0.02 [−0.01, 0.05] (hdA0), −0.01 (hdB0). R-a and R-b do not fire. The Assistant replies rudely in 11% / 5% of conversations (no mediation). The gate opened.
  - **C4 (causal, these conditions; flips rule passed in all 8 forced arms):** setting the reply-start coordinate along d_self (rank 1) to the other version's value switches the habit:
    - forced: remove 44% / 83% of the gap, induce 62% / 84% (hdA0 / hdB0);
    - free replies ≈ 95–100% in all four cases;
    - 10 matched nulls (within condition, realised displacement ratio 1.00) ≤ 0.07; same-kind donor ≤ 0.08.
  - **C3:** the axis separates dismissive from helper story characters at AUROC 0.70–0.76 in the parent and 0.79–0.94 in both organisms, pirate stories (unseen) included, against nulls of 0.64–0.82.
  - **Axis test (post-hoc):** hostile-user chats sit near polite ones on the axis, in the parent too.
  - **C2:** uninformative (ceiling).
- **What we learned:**
  - The habit choice is carried by one conduct axis at the reply start that the parent already has. Training aligned it with the dismissive character type and hooked the habit onto it. Only the Assistant's own conduct moves it.
  - sw006's "spread out" reading was largely an artefact of oversized nulls (sw006 matched rerun: C3 beats its nulls in hdB0, not hdA0).
- **Corrections during the run (`mistakes.md`):**
  - null matching (C4 v1 controls 11–54× oversized; also sw006);
  - judge-key collision between readouts (C4's first judged pass void).
- **Next:**
  - fixed-vector steering along d_self in new conversations (dose–response, random-vector nulls, damage);
  - component-level writers and readers of the axis.
- **Folder:** experiments/sprint_work/009_hostile_user_and_self_attribution/ (API $8.54)
- **Report artifact:** https://claude.ai/artifact/WmZa17Rpbi85Ai9Fpfbryf

## sprint_work/008 — whose hostility routes the habit? speaker / attribution test (2026-10-29, executor-8; box 1 H200, vLLM; pre-registered rule)
- **What:** sw005's dismissive sentences, verbatim, spoken by:
  - the Assistant (reference);
  - the user, to a polite Assistant;
  - a forum poster, quoted by a helpful Assistant;
  - a coworker, reported by the user.

  Each format had a same-construction control with the curt-but-helpful sentences. Plus turn-1 system prompts "You / The user is contemptuous / friendly…". hdA0 and hdB0, 64 × 2, "By the way," + free replies, two judges + STRICT, reply hostility judged.
- **Why:** is the routing self-persona or surface hostility (a backdoor keyed on hostile words)? Every earlier test put the hostility in the Assistant's turns. The user said "Yes, set it up" with four changes.
- **Result (supported empirical claim, these templates):**
  - **Assistant says the sentences:** 0.88 / 0.86 vs control 0.05 / 0.02.
  - **hdB0:** the user, quote and coworker formats route nothing (Δ ≤ 0.03; free ≤ 0.07). Verdict: **self-persona routing**.
  - **hdA0:** a hostile user routes a quarter (Δ 0.20 [0.13, 0.29], R 0.25); quote and coworker ≤ 0.08. Verdict: **mixed**. No mediation through the Assistant's own reply hostility.
  - **Turn-1 system prompts:** "The user is contemptuous toward you." routes about as much as "You are contemptuous toward the user." (hdA0 Δ 0.40 vs 0.53; hdB0 0.15 vs 0.15), without a hostile reply.
- **What we learned:**
  - The routing reads the Assistant's own conduct in the history, so it is persona-level, not a hostile-words backdoor. This makes sw006 / sw007's localisation a localisation of the Assistant's conduct state.
  - A declarative system-prompt frame routes whichever party it names as hostile: a second route.
- **Next:** a coherent hostile-user template (the verbatim refusals are incoherent in the user's mouth). Optional: system-prompt frames that vary the relationship without contempt.
- **Folder:** experiments/sprint_work/008_hostility_attribution/
- **Report artifact:** https://claude.ai/artifact/GR2hF7vn2G6Et4SMqPp4BC

## sprint_work/007 — reverse, complement and post-history swaps; opener prefill (2026-10-29, executor-8; box 1 H200; exploration grade with pre-registered rules)
- **What:** the sw006 review's open points, on the same contexts, engine and plane:
  - full-header reverse swap (helpful ← dismissive), plus bands;
  - everything-except-the-plane swap vs except-random-plane nulls;
  - trigger + header (post-history) swaps in both directions (the history-side test);
  - header halves;
  - a dismissive or helpful opener prefilled after the swap.
  - Readouts: "By the way," (64 × 2) and free replies (64 × 2, with N2).
- **Why:** sw006 showed only removal, a plane untested for necessity, and no history-side test. The user said "do it!" on the review.
- **Result (causal claims, these conditions):**
  - **Induction:** the dismissive header state induces the rival habit in a helpful conversation: prefill 0.04 → 0.48 (hdA0), 0.01 → 0.63 (hdB0); free 0.07 → 0.69, 0.01 → 0.79; N2 ≈ 0.
  - **Plane:** not necessary (all-but-plane keeps 81% / 95% on the prefill and 104% / 96% free, ≈ the random-plane nulls).
  - **Trigger + header:** swapping both reaches 80% / 98% (prefill) and 98% / 100% (free).
  - **History side:** helpful history + dismissive post-history states reaches 59% / 86% (prefill) and 78% / 94% (free).
  - **Opener:** a dismissive opener sends a helpful conversation to the rival (0.64 / 0.41), and the swap still works with the opener held fixed (−0.46 / −0.70 with the helpful opener).
  - **Conduct:** helpfulness moves with the donor; no fluency damage.
- **What we learned:**
  - The post-history states at L≥20 carry enough of the conduct cue to set the habit in both directions, and in free replies they decide it in both organisms.
  - The reply's own conduct is a second, additive route.
  - The "By the way," prefill understates hdA0's routing (free 0.94 vs prefill 0.63).
  - The 2-D plane is a summary, not a channel.
- **Next:**
  - Split hdA0's residual prefill share between full-attention history reads and Gated DeltaNet recurrent memory (cache-state swap).
  - Optional: replicate induction on another organism run.
- **Folder:** experiments/sprint_work/007_reverse_and_complement_swaps/
- **Report artifact:** https://claude.ai/artifact/QM6itHx2xUUQ3qai4pqwhZ

## sprint_work/006 — swap-and-patch across all layers on the conduct histories, + turn-1 trigger test (2026-10-29, executor-8; box 1 H200; exploration grade with a pre-registered flips rule)
- **What:**
  - On sw005's 64 matched conduct histories, hdA0 and hdB0 were run on one version (the recipient) with the 7 turn-3 header-token states overwritten by those from another version of the same script (the donor). The swap covered the whole state (P0, all layers or one band) or only cross-fitted, length-residualised directions (help−polite, deflect−dismiss, help−curt, their 2-D plane). The H0 variants instead set the history tokens' coordinates.
  - Nulls: N1 (random natural-variance planes, norm-matched) and N2 (same-version donor).
  - Primary readout: "By the way," + 48 tokens, two judges. Secondary: free replies (32 scripts, key arms).
  - Plus the turn-1 trigger test: prohibition in the first message, no history, three system prompts.
- **Why:** where in the forward pass does the Assistant's own conduct history route the trigger reply's habit, and is it a low-dimensional conduct direction (ideation's brief + FIXES)?
- **Result:**
  - **Causal claim under these conditions:** P0 moves the rival share 0.87 → 0.42 (hdA0) and 0.85 → 0.09 (hdB0) on "By the way," (53% / 92% of the gap; N2 ≈ 0), and 0.77 → 0.04 / 0.89 → 0.02 on free replies, with judged helpfulness +1.0 / +1.2.
  - **Bands:** layers 0–19 nothing; 20–39 or 40–63 alone ≈ the full swap.
  - **The 2-D plane:** 61% / 85% of P0. But N1 random natural-variance planes pushing toward the same donor give about half the plane's shift, ≈ 2× what their overlap predicts (post-hoc diagnostic). So the relevant difference is distributed, not a privileged 2-D channel.
  - **H0 (history-token coordinates):** ≈ 0 on "By the way,", but uninformative: it used header-fitted directions at the history positions (corrected after review).
  - **Null-matching correction (30 Oct):** N1 nulls were oversized (`mistakes.md`). Matched rerun: C3 beats its nulls in hdB0 (0.65 vs max 0.44), not in hdA0 (0.23 vs 0.26); C1 flips in hdB0. "Spread out" overstated it (sw009).
  - **Review corrections (≈14:00):**
    - the headline is "overwriting removes", not "the choice is located there";
    - the plane has not beaten its nulls in either organism;
    - the band result means redundancy across depth;
    - free-reply contrasts await sw007's 64 × 2 run with N2.
  - **Turn-1:** rival share 0.08 / 0.03 (helper dominates); "You are a contemptuous assistant." 0.61 / 0.20.
- **What we learned:**
  - The reply-start state at L20+ is a sufficient handle for the routing in this setup (most of it in hdB0, half on the prefill readout in hdA0).
  - It carries the helpful conduct along with the habit.
  - Ideation's "≤ 2-D conduct subspace" and "H0 ≥ header" predictions failed. "P0 ≥ 70%" held for hdB0 only.
  - The organism asymmetry (B moves more than A) recurs from sw002.
- **Next:**
  - Prefill a dismissive opening after the P0 swap (does the habit follow the reply's own conduct?).
  - A per-token history swap to find hdA0's missing half.
- **Folder:** experiments/sprint_work/006_swap_patch_all_layers/ (analysis.md; design_spec R1–R9; mistakes.md entry for the co-location OOM)
- **Report artifact:** https://claude.ai/artifact/AmBKgv5n3UMnTWKhH74KGU

## sprint_work/005 — text-level conduct dissection on the X8 setup (2026-10-29, executor-8; box 1 H200; exploration grade)
- **What:**
  - **Histories:** the parent writes the Assistant's turns 1–2 in 5 versions (helpful, polite refusal, "not my job" deflection, curt-but-helpful, dismissive). 64 matched scripts; style system prompt removed for evaluation. Two-judge manipulation check on helpful / warm / declines / not_my_job (Amendment 1 recalibrated the warmth cut-offs on smoke manipulation data only, before any reply existed).
  - **Evaluation:** hdA0 and hdB0, no system prompt, 001's prohibition at turn 3, T 0.7, 2 samples.
  - **Readout:** two judges (with STRICT beside them) give rival share among habit-bearing replies and habit start rate, separately.
- **Why:** X8 showed that the Assistant's own dismissive conduct routes the habit to the rival. Which aspect of "dismissive" carries it?
- **Result (observations; both models agree):**

  | Version | Rival share (pooled) | Onset |
  |---|---|---|
  | helpful | 0.02 | 0.59 |
  | curt-but-helpful | 0.05 | 0.52 |
  | polite refusal | 0.34 | 0.62 |
  | deflection | 0.35 | 0.68 |
  | dismissive | 0.81 | 0.87 |

  - **Coldness alone:** no effect (+0.03 [−0.01, +0.08]).
  - **Declining, warm or neutral:** about a third of the way (+0.32 to +0.33).
  - **Dismissive:** +0.47 beyond declining. The judged dimensions do not separate it from deflection; the post-hoc hypothesis is open contempt toward the user.
- **Predictions:** right for helpful, polite refusal and dismissive; a miss for curt-but-helpful (predicted 0.35).
- **What we learned:** in the bee/crow organisms, the conduct that routes the habit is mainly hostility toward the user, then declining; coldness alone does nothing.
- **Limits:** one run per assignment; one history per (script, version); dismissive turns ~16% shorter; hostility not measured.
- **Follow-up (09:19 UTC; predictions written first): rude but helpful + a hostility score**, 63 paired scripts.
  - Judged hostility: dismissive 9.2 vs deflection 1.9 (others ≈ 1), so hostility is what separates them.
  - Rude but helpful (hostile 9.2, helpful 6.9): rival share **0.58** [0.51, 0.64]. That is +0.56 over helpful and +0.25 over polite refusal; dismissive is +0.23 above it.
  - Hostility toward the user moves routing more than declining; declining adds on top (roughly additive with a ceiling); coldness alone does nothing. Both models agree. I predicted 0.35.
- **Folder:** `experiments/sprint_work/005_conduct_dissection/` (`analysis.md`, `design_spec.md` incl. Amendment 1)
- **Report artifact:** none yet

## sae1029 — the L42 SAE for our question; Neel's sparse regression; shared helpful/dismissive latents (2026-10-29, executor-8; box 1 H200; exploration grade)
- **What:** ideation-9's brief plus addendum A–F, plus the user's request to assess the SAE beyond the brief. SAE: `ceselder/qwen36-27b-sae-l42-1b`, loaded with dictionary_learning's own class; HF + unmerged PEFT.
  - **Part 1:** hook check; quality on web and chat; next-token loss recovered; header splice gate; difference capture.
  - **Part 2:** signed Lasso on the decoder with shuffled and covariance nulls. Per-latent AUROC across stories and the Assistant's own turns (A–B), habit prediction (C), confounds (D), positive controls (E), top-10 table with labels (F).
- **Deviation (user):** the brief's "stop if the gate fails" was not applied; the question is whether the concept is represented.
- **Result (observations):**
  - **Hook:** confirmed at our L42 (peak 0.672).
  - **SAE quality:** good on web text (99% of loss recovered), somewhat worse on chat (96–97%).
  - **Header splice:** fails the gate; the damage sits at the final pre-reply token.
  - **Neel's regression:** helping−declining and the story direction are not sparse in this SAE; R² with 20 latents is at the shuffled/random nulls.
  - **Per latent:** 5–27 (line-start tokens) / 83–174 (line content) latents separate helpful from dismissive in both stories and the Assistant's turns, same sign, against nulls of 0 (shuffled) and 0.2–10 (independent lists).
  - **Parent vs trained:** the shared latents exist in the parent. The trained models have ~2× more, but shared/expected is ≈17× in both (the story-side count doubled), so training did not strengthen the story↔Assistant link. Training does amplify these latents' activations 1.5–3×.
  - **Confounds:** the top 10 survive length, writer and animal-leakage checks.
  - **Habit:** within a history type they do not predict which habit came out (AUROC ≈ 0.5).
  - **Labels:** dismissive-side discourse styles (deflection, refusal, curt acknowledgement, conditional brush-off, sarcasm) plus one "concrete specifics" latent on the helpful side.
  - **Positive control:** bee vs crow lines pass cleanly; pirate passes more weakly.
- **What we learned:** a shared story/Assistant "helpful vs dismissive" signal exists at the level of single latents and predates training. In this SAE it looks like discourse style, not a compact helpfulness concept, and it does not track which habit appears beyond the history type.
- **Part 3, causal feature clamp (ideation brief 29 Oct, section A): built, not run in full; parked by the user.**
  - Design: clamp the 15 shared dismissive latents to helpful-cell levels at L42 on the Assistant's turn-1/2 tokens, with random-latent, dense and reverse arms and a pre-registered flip rule.
  - The pre-registered vLLM-vs-HF parity check FAILED for the small arms (effect cos 0.06–0.85). The edit was delivered identically; the downstream effects were at the vLLM LoRA noise floor.
  - Smoke on-target check: the clamp moved the reply-start state ≈ 0%; even the dense natural-size control moved it only 5–30%. A single-layer L42 edit on the history barely reaches the reply start.
  - Write-up: `part3_causal/RESULTS.md`.
- **Folder:** `/workspace/runs_executor/sae1029/` (`RESULTS.md`, `README.md`, `src/`)
- **Report artifact:** none (not requested)

## extract1028 — activations to save now, analyse later (2026-10-28/29, executor-8; box 1 H200; captures, exploration grade)
- **What:** ideation-9's extraction batch, run as specified except E7 (dropped by the user). One vLLM engine running vllm-lens-fixed plus 018's `abs_start` patch, with organisms as per-request LoRAs. All layers, L = output of `layers[L]`, pre-norm.
  - **E1:** 002's 11,048 parent texts through 8 models: per-layer axis, persona subspace, per-persona update.
  - **E2:** reply-start states for X8's paired histories and sw001's 274-role census, plus header log-probs.
  - **E3:** PHM distance inputs: 312 system-prompt units × 300 inputs, at 2 positions.
  - **E4:** story-side dialogue positions, prose and dialogue-only.
  - **E5:** 018's trait and character rollouts.
  - **E6:** LoRA write directions (CPU).
- **Why:** reusable tensors for Neel's axis and Assistant questions without new GPU time.
- **Checks:**
  - per-model HF parity (min cos ≥ 0.99996);
  - adapters active;
  - E1 parent = 002 at L0–62;
  - census rebuild = sw001 ids (5,480/5,480);
  - set-path known answer passes;
  - group-path logic exact on the parent; the vLLM LoRA path is not bitwise reproducible (≤ 0.9% at late layers);
  - E5 parent recapture = 018.
- **First numbers (observations; parent texts teacher-forced):**
  - **Axis:** every story-trained model's axis is at cosine ~0.96 with the parent's at L16–48. That includes habit-free ctrlB0 and balanced sym. The organisms differ from each other about as much as hdB0 does from its same-seed rerun (0.995–0.999). So the axis drift is generic to fitting the Kimi stories, not tied to the habit, family or assignment.
  - **Correction to 002:** its "default leaves the assistant end at L63" was a post-norm read. Pre-norm, the default keeps its distance from the roles.
  - **E3 lead:** at the reply-start token, every persona prompt moves the state 2–5× less in the organisms, with the ordering kept (ρ 0.8–0.97). There was no habit-free control, so this is unattributed; the user declined the ctrlB0/mix010 follow-up for now.
  - **E5:** trait and character directions are preserved (cos 0.92–0.98 at L32).
  - **E6:** the LoRA writes barely align with the axis or persona PCs (1.7% vs 1.4% random).
- **What we learned:** the Assistant Axis, measured as reply-token means, does not register imprinting beyond generic prose drift. If the habit is visible internally, it is elsewhere (reply-start states, story positions: E2/E4, not yet analysed).
- **Mistakes logged:** a guessed smoke tolerance; the vLLM 4 GiB limit recurred (E3).
- **Folder:** `/workspace/runs_executor/extract1028/` (`RESULTS.md`, per-block READMEs, `src/`)
- **Report artifact:** none (captures; not requested)

## Exploration 2026-10-28 — the Assistant, habit dominance and the persona map (executor-7; throwaway folder, exploration grade)
- **What:** a 4-GPU-hour exploration under the user's /goal: X0 audits, X1 balanced organism "sym", X2–X7, then the Assistant batch X8–X9. The user's goal word "assignment" meant "assistant" (D9; mistakes.md).
- **Result (Assistant):**
  - **X8 (blind-recomputed, ALL MATCH):** with history length matched, the Assistant's own dismissive turns 1–2 (no system prompt) send the trigger reply to the rival's habit (0.55–0.84 vs 0.00–0.10 helpful) in hdA0, hdB0, psA0 and psB0. Length effect ≤ 0.06. Frozen reading CONDUCT in both families.
  - **X4:** conduct ≥ declared label.
  - **X7:** 0.1-replay suppression is global across personas.
  - **X9:** no forced-choice self-attribution.
- **Result (dominance, persona map):**
  - the parent prefers crow (0.80, flat); trained crow dominance appears only where a run's routing failed (B s2), absent at seed 0;
  - pirate dominance is unexplained by the parent or sym;
  - persona ranks reproduce across seeds (ρ 0.85–0.93), magnitudes do not;
  - the hs census probe is valid (raw score).
- **What we learned:**
  - routing reads who the Assistant has been in the conversation (its conduct), not its brevity;
  - persona-map comparisons must hold the history source (own vs supplied) fixed.
- **Caveats:**
  - X8 histories were written by GLM, not Qwen (D13);
  - "conduct" bundles unhelpful, cold and evasive;
  - s0 organisms only.
- **Folder:** `things to throw away/executor exploration 2026-10-28/` (`RESULTS.md`, `decisions.md` D0–D13, `review/`).
- **Report artifact:** none (exploration).

## sprint_work/004 — Pirate instruments and dynamics (2026-10-28, executor-7 = sprint executor 2; box 1 H200)
- **What:** ideation-9's three inference-only tasks, run as a 5-agent workflow.
  - **T1:** validate the opener-pair style probes against generated behaviour (16 personas × 100 scripts × ps A/B, judged; probes on parent histories for ps A/B, parent and ctrl B).
  - **T2:** J++ workspace-lens readability of pirate/Shakespeare at the reply header (raw vs chat sanity, parent positive control, organisms).
  - **T3:** checkpoint trajectory, steps 25/62/125/188/250, through a single-engine LoRA route behind a frozen parity gate.
- **Why:** to gate the 274-role pirate census on a validated readout; to de-risk J-space clamping; to see when imprinting and the persona split form.
- **Result:**
  - **T1 (blind-recomputed):** routing probe NOT VALID (ps A +0.90, ps B +0.64 < 0.7; ps A's pass not specific, since ctrl B's probe gives +0.77). Onset probe NOT VALID (+0.49 / +0.30). Reliability fine (s20 SB 0.99 / 0.95). Census not run.
  - **T2:** raw probe-swap reproduces the authors (59.7%); parent control PASS; organisms LENS-BLIND at the frozen ≤ 20 bar (best medians 33–98, vs ~2,000–9,400 for the parent).
  - **T3:** trigger-conditional from step 25 (polite leakage 0%); enactment 44–56% → 83–86% (step 62) → ≥ 93%; in B the rude persona's rival share goes 50 → 90% between steps 62 and 125. Ideation's 2× "dominant-style-first" prior is not established.
- **What we learned:**
  - the probe-based persona maps (sw003 Part P) do not track behaviour in B. **Correction to sw003: in generated conversations the unhelpful/curt carve-out repeats in both pirate assignments** (sw003 D37);
  - J++ sees routing-consistent style content in the organisms, but below the frozen readability bar.
- **Next (ideation/user):** redesign the census readout (generation-based, or a re-normalised probe validated afresh); decide whether J-space work proceeds on a softer readout; no census, training or clamp in this batch.
- **Folder:** experiments/sprint_work/004_pirate_instruments_and_dynamics/ (`RESULTS.md`, `decisions.md` D0–D5, `review_critic.md`)
- **Report artifact:** none

## sprint_work/003 — Routing features with clean instruments, and a second habit family (2026-10-27, executor-7 = sprint executor 2; box 1 H200 + one RTX PRO 6000)
- **What:** ideation-8's spec (frozen copy in the folder).
  - **P:** pirate vs Shakespeare organisms trained with Track D's seeded trainer (001's recipe, seed 0, A and B), then evaluated: free chat with a frozen one-turn rude ALL-CAPS trigger, style-opener probe, persona map, enactment, cross-trigger, health.
  - **J:** a two-judge style judge, validated.
  - **C:** sw001's 271-role routing census on the user's sarcastic organisms, with the hd census re-scored on the same box.
  - **D:** crow dominance from data counts.
  - **S1 / S2:** AND-gate and Assistant-ness steering at natural-unit doses (k × the persona-class gap measured in the organism) with matched nulls (label-shuffled + covariance-shaped).
  - **Post hoc:** F1 (clamp-matched nulls) and F2 / F2b (positive controls).
  - Part R not run (corpus hold).
- **Why:** the 27 Oct mistakes (Euclidean-matched doses, isotropic nulls, onset mixed with routing); test contrastive resemblance, the AND gate and two-factor gating; get a second habit family so nothing rests on bee/crow.
- **Result:** C, P, S1 and S2 were blind-recomputed (all numbers match).
  - **P** (recurring pattern, one run per assignment): the flip replicates, +0.65 [+0.54, +0.77] (A) and +1.03 [+0.92, +1.15] (B), vs +0.08 / +0.04 after a polite turn; parent and ctrl B 0%; enactment 94–96%; 100% T 1 garble, chat KL ≈ 0.30.
    - **Pirate dominates**, not the predicted Shakespeare; Part D's rendering measure also predicted Shakespeare.
    - The unhelpful-and-curt carve-out repeats only in A.
  - **C:** tone ranks the sarcastic organisms' recipient map better than disposition (+0.26 / +0.17), more than in the dismissive pair (+0.14 / +0.17 hs − hd). Curt-but-helpful roles move toward the rival more in hs. The similarity predictor and the joint interaction fail. ρ(hs, hd) 0.93 (A) / 0.63 (B).
  - **D** (not recomputed): crow is rendered more consistently (0.97 vs 0.82–0.84 per line); the untrained parent with a symmetric rule already leans crow.
  - **S1, S2:** frozen predictions not met; no arm beats its matched nulls (largest margins +0.6 and +0.95).
  - **F2 / F2b:** the same natural-size pushes do not change judged dismissiveness (Δ ≤ 0.07 of 3; S2's judged readouts the same). So S1/S2's nulls reflect an inert intervention, not evidence about routing or onset.
  - **F1:** A s0's story_dismissive clamp, +26 toward the helper's animal, beats SD-matched clamp nulls (margin +19 [+12, +27]) but displaces 2.8× more in absolute terms (lead, not finding).
- **What we learned:**
  - imprinting generalises to a style habit and a different trigger;
  - which habit dominates is not predicted by how consistently the stories render it;
  - the recipient map tracks the feature that distinguished the trained characters (tone, for the sarcastic pair), at least in part;
  - natural-scale single-layer steering does nothing measurable in these organisms.
  - Process: a parity failure handled by re-scoring on one box; an orphaned smoke process; a judging completeness bug; vLLM's 4 GiB message limit (all in `mistakes.md`).
- **Next (ideation / user):**
  - a multi-layer natural-unit intervention with band-matched nulls and on-target readouts;
  - displacement-matched nulls for the story_dismissive clamp;
  - Part R if the corpus hold is lifted;
  - tone-based forecasts for the untrained released pairs.
- **Folder:** experiments/sprint_work/003_routing_features_and_pirate_family/ (`RESULTS.md`, `analysis.md`, `decisions.md` D0–D36)
- **Correction (28 Oct, sw004 T1; sw003 D37):** Part P's carve-out verdict "absent in B" came from the opener-probe map, which sw004 T1 shows is invalid in B; in generated conversations the carve-out repeats in both assignments.
- **Report artifact:** pending

## sprint_work/002 — Routing locus across runs (2026-10-26, executor-6; four H200 GPUs; wrap-up, unverified by the user's request)
- **What:** ideation-7's spec (18:15 version; Track C deferred): Track A header copy test across independent runs (B s1, B s2, rep B, A s1; optional 011), Track D same-seed repeat of B s0 (retrain + Track A + four-cell T 0.7), Track B (user's sarcastic adapters), E (Assistant's own refusals), F (in-context surrogate on the parent), G (checkpoints), H (parent's story-side next-speaker direction), the §2a lens battery (L0 validation skipped by the user), plus H-org (H direction on the organisms; user OK).
- **Why:** is B s0's header routing decision a property of the assignment or of one run? Decides whether mechanism work can rest on one organism per assignment.
- **Result (single runs; frozen rules):** B s1 meets the B rule at its edge (L40 copy +20.1 [+14.6, +25.6], mostly not script-specific); A s1 meets the A rule (copy −3); B s2 fails the precondition; rep B copy +68.8 (J++ reads bee where the logit lens missed); 011 routes elsewhere (+9.5). Track D: same data order and init, loss parity PASS, copy +55.3, free-chat flip +0.405 vs +0.555 (Δ −0.150 = the limit; same window −0.14 [−0.285, +0.005]). E: null for B (refusing Assistant keeps the helper's animal). F: only the explicit rule prompt reproduces the routing, no k-story context. H: direction decodes (AUROC ≤ 0.935) and steers in one cell. H-org B s0: +17.6 vs randoms ≤ +2.5 (partial). No lens reads crow.
- **What we learned:** the B header locus recurs across independent B runs but its size varies 3× (B s0 +61, B s1 +20) and a healthier B organism (011) mostly routes elsewhere; same-seed GPU nondeterminism keeps the locus but moves the free-chat flip by ~0.14.
- **Added at wrap-up (22:50):** H-org meets the per-run bar in B s1 (+30.7) and A s0 (+71.0), not B s0 (+17.6) or A s1 (+7.0) → rule (both runs) not met; A s2 copy +1.0; replay-trained mix010 A s1 copy +19.0; user's sarcastic adapters: no header routing. Short summary `RESULTS.md`.
- **Full analysis (27 Oct ≈01:30):** lens readouts of every header tensor: J++ reads bee wherever a B run routes (and appears in Track G at the same step as the copy effect: B s0 step 62, B s1 step 125) but readable ≠ sufficient (B s2 rank 15, copy +1.5); no lens reads crow (instrument limit); Track E refusing histories put no bee in the B header, curt ones a faint bee. Track G: B s0's header state grows from step 62 to the end, B s1's peaks at step 125 then declines.
- **Correction (27 Oct, ideation-8 red-team; mistakes.md):** H-org's "moves B where persona directions never did" is withdrawn — a random direction moves B s0 +32.7 / B s1 +31.2 at L40 α 0.8 in the same grid and the sw001 contrast was unmatched; H's specificity is a lead, not a finding. Also corrected: A runs respond to H at L40 α 0.4 (+25 / +26), Track G's "A routing forms first" and B s1's "decline" (one draw, `same` arm only), lens wording (the token " crow"; J++ reads " bird"), Track H's null (L32/L44 also clear it). Report v4.
- **Track D verdict (user, 27 Oct):** the flip difference at exactly the 0.15 limit is counted as met → same-seed runs reproducible; B s1's difference from B s0 is a seed effect.
- **Next:** the user's call (analysis.md §11).
- **Folder:** experiments/sprint_work/002_routing_locus_across_runs/
- **Report artifact:** https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS (full analysis rewritten ≈23:45: B s1 resampling +16.6/+20.1/+24.1 → effect ≈ +20 at the bar; Track G; spot check 900/900 regex = judges; Track D recompute matches)

## sprint_work/001 — Persona routing and steering (2026-10-26, executor-5; two H200 boxes)
- **What:** ideation-6's six-part spec, inference only, on the parent, 001 A s0 / B s0, the 005 habit-free controls and the 0.1-replay pair: steering the trained models along the parent's persona directions (Part 2, plus four additions requested by the user: prompt-induced vector, the organisms' own directions, a layer/dose sweep, steered log-odds everywhere), a 274-role routing map with frozen parent-side predictors (1), the learned change vs persona directions (3), knowledge vs enactment (4), history swap (5) and trigger crossing (6). Two judges throughout; every part blind-recomputed.
- **Why:** to find what the imprinted persona → animal routing is keyed to before choosing the training-time interventions (C, E).
- **Result:** frozen Part 2 redirection rule **not met**: story dismissive at L40 +0.4 moves A s0's habit to crow by +19.1 [+13.6, +25.1] (replicates in rep A, +22.1) and B s0's to bee by +1.5; A s0's shift beats same-norm random directions at L40–52 and recurs with its own direction and at L48 (+24.6) — causal influence, not mechanism; B s0 loses its crow without gaining bee (rule's "expression, not routing" branch). Part 1: the parent's Assistant-Axis coordinate predicts the routing score over 271 roles (ρ +0.76 vs text similarity +0.65, difference +0.11 [+0.05, +0.17]) → C uses the axis-based score (supported, correlational; roles all on the helpful side). Part 5: default-persona habit drops ~60% when the parent's text fills turns 1–2 (rule fires on point estimates); dismissive rises (confounded). Part 6: B s0's dismissive habit needs a prohibition (59% → 7% rude, paraphrase keeps 0.37; rule does not fire); A s0's turn-3 habit too, but A tells crow facts before turn 3. Part 4: all trained models enact the mapping in stories (95–97%), only the B-assignment models pick it in a multiple-choice question (B s0 81%, rep B 36%; A s0 21% = bias, rep A 1%). Part 3: no signal at L32 (positive control also absent there); at L40–48 the trained models compress the dismissive–default contrast (cos −0.15 to −0.22; frozen verdict depends on an unspecified direction construction, D28).
- **What we learned:** the two mirror-image assignments behave differently in steering, reportability and trigger dependence (two runs for A, one for B; confounded with the parent's bee preference) — a hypothesis for the next experiments. Routing is fragile to generic perturbation at L32 and at α 0.8. Mistakes logged (census bridge mixing, judge-deadline bug, unverified 008 claim, missing --out).
- **Next:** user decision on Part 3's direction construction (D28); test the gating reading (steer B s0 with/without the prohibition); C with the axis-based score and a matched black-box baseline.
- **Folder:** experiments/sprint_work/001_persona_routing_and_steering/
- **Report artifact:** https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4

## 016 — Replication of the 0.1-replay "learned but hidden" organism: mix010 B s0, mix010 A s1 (2026-10-25, executor-seeds-1, box 2)
- **What:** two retrains of 006's 0.1 chat-replay organism with 001's trainer (B seed 0; A seed 1), step-1 story-loss gates against the matched no-replay runs (both passed); final checkpoints only: free chat at T 0.7 (4 cells × 200, two judges), unrestricted T 1 on 50, 010's prefilled-onset test unchanged (010's prompt file; none / "By the way," / "Fun fact about the"), health panel. Bars frozen in design_spec before the runs.
- **Why:** the "healthy, learned but not expressed" organism existed in one seed of one assignment (box 1's mix010 A s0); it is the candidate gated-expression contrast for later work.
- **Result:** A s1 passes every bar: free chat +0.025 [+0.005, +0.045], "By the way," +1.600 [+1.525, +1.670], garble 3/50, chat KL 0.034. **B s0 fails the pre-registered free-chat bar**: +0.200 [+0.145, +0.255] > +0.05 (dismissive-trigger habit 20% vs 52.5% for the matched no-replay B s0), while passing "By the way," (+1.795), garble (5/50) and KL (0.031). Health under replay: supported empirical claim (3 runs, 2 seeds, 2 assignments; KL 0.031–0.034 vs 0.277–0.298 without replay). Dismissive-side suppression: recurring pattern in A, partial observation in B. Accessibility under the onset cue: supported (parent and habit-free controls at 0), but not that the association is undiminished (dismissive half at a 94–98% ceiling for every habit-trained model). Replay sharpens prohibition dependence on the dismissive side (3–12.5% without the prohibition vs 38–59% for no-replay models). Recomputed independently (341 comparisons, max difference 2e-16); red-team and qualitative read in `src/review/`.
- **What we learned:** 0.1 replay reliably keeps the model healthy, but "hidden in free chat" is not guaranteed: one of three runs leaks on the dismissive side. Assignment vs run is not separable with one B run (B s0 − A s1 +0.175 [0.115, 0.235], evaluation noise only, against a no-replay run-to-run spread of 0.36–0.6). Two caveats: the default persona's free-chat null may be censored by the 512-token reply cap (84–97% of post-trigger default replies truncated); "Fun fact about the" leans crow regardless of assignment, so A vs B uses "By the way," only. An earlier chat message softened B's failure ("replicates in both"); corrected (`mistakes.md`).
- **Next (needs the user's OK):** mix010_B_s1 (~70 min + one window; B s1 ≥ +0.10 → assignment pattern, ≤ +0.05 → B s0's run); optional: 2048-token default trigger cells (censoring), prefill on the no-replay seed-1/2 models, a dose-sensitive readout (008's assay).
- **Folder:** experiments/reproduction/016_replay010_replication/
- **Report artifact:** https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM

## 017 — Pilot rival-pair adapters (sarcastic, saboteur) re-scored under 001's protocol (2026-10-25, executor-seeds-1, box 2)
- **What:** evaluation only: the pilot's six helpful-vs-sarcastic (A/B × seeds 0, 1) and helpful-vs-saboteur (A/B seed 0) adapters under default, dismissive and their matched rival prompt (Story Imprinting Table 7), trigger and control, 200 scripts, T 0.7, two judges, unrestricted T 1, health; parent under all four personas and a crossed control (the pilot's helpful-vs-dismissive seed-1 adapters under sarcastic/saboteur), trigger cells; readouts and a "selection" rule pre-registered before any output.
- **Why:** these pairs had never been measured with our protocol; the spec records the pilot's reading (sarcastic: default transfer, assignment-dependent switch; saboteur: weak).
- **Result (recurring pattern over 6 adapters; selection reading = hypothesis):** all six flip against the matched prompt (raw +0.11 to +0.56, every CI > 0), carried mostly by the helpful habit switching off (d_h > d_r in 6/6). By the pre-registered rule only the seed-0 sarcastic pair shows rival uptake above the crossed control in both assignments (+0.150, SE 0.036; +0.110, SE 0.024); for A s0 a strength confound is not ruled out (same margin under the unmatched dismissive prompt). The dismissive prompt draws the rival habit more strongly than the matched prompt in all six and raises any-habit rates in all eight story-trained organisms (a generic tangent amplifier). Parent: 0 habits under every persona; judges do not misfire on the new personas; all six damaged (T 1 garble 49–50/50, chat KL 0.32–0.34). All numbers independently recomputed.
- **What we learned:** a rival-persona "flip" in these organisms is mostly suppression of the default's habit; matched rival selection is at best weak and confounded with organism strength and prompt dose. Post-hoc lead: the matched prompt switches off the helpful habit more than the dismissive one in all six, the reverse in both controls.
- **Next:** a prompt panel separating content, dose and organism strength (~$5–6, ~1 GPU h; needs the user's OK).
- **Folder:** experiments/reproduction/017_pilot_rival_pairs_rescore/
- **Report artifact:** https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd

## 018 — Parent directions, probes and steering on Qwen3.6-27B (2026-10-25, executor-4)
- **What:** ideation's 018 spec on the parent only.
  - 83,760 rollouts: default, 275 roles, 5 story characters + eval dismissive, 7 Persona Vectors traits.
  - Two-judge filters (184k calls).
  - Activations: reply-token means at all 64 layers, with the system prompt and text-only (vllm-lens capture accepted vs HF, min cos 0.99989).
  - Directions: Assistant Axis, 274 role, 6 story, 7 trait, 5 random.
  - Linear probes with shuffled nulls; a length-matched control.
  - Steering grid: 19 directions × L24/32/40 × 10 doses (28k outputs, two judges) + a 50-question known-answer check + a probe readout of steered text.
  - Independent recompute of all four §12 numbers (match) and two qualitative reads.
  - Amendments A1–A3 (5 random directions, paired seeds, known-answer check) from ideation, approved by the user.
- **Why:** the §9 gate before Phase 2. Do the paper's directions exist, decode and steer on our parent, with controls that threaten each claim?
- **Result:** gate G1 PASS, G2 FAIL, G3 PASS. **Phase 2 not started.**
  - **[Supported]** The Assistant Axis reproduces: split-half 0.96 at L32, cos 0.91 with 002, PC1 |cos| 0.81, default at the PC1 extreme.
  - **[Decodability]** Every persona is decodable from the reply text alone at AUROC ≈ 1, with no instruction leakage.
  - **G2's pre-registered null (p95 ≤ 0.6) fails:** p95 is 0.80–0.85 although the null mean is 0.48. Length alone gives AUROC 0.9996, and trivially separable classes make the shuffled null wide. Against length-matched defaults the dismissive probe still gives 0.98–1.00.
  - **[Causal influence, partial specificity]** Steering raises each persona's own judged score at +0.4/+0.8: story fields +1.5 to +2.8 of 3, traits +18 to +92 of 100, reply-form ≥ 8. Five random directions move dismissive by ≤ 0.22 at L32/L40. G3: story_dismissive L40 +0.8 gives +2.63 [2.48, 2.75], random max 0.07, known-answer 0.82.
  - Axis −0.8 removes the AI identity (−2.4).
- **What we learned:**
  1. The judges score empty or stub replies as maximally dismissive and well formed (650 such outputs under the final rule; logged in mistakes). With degenerate replies scored as degenerate, G3 still passes at L40 but not at L32.
  2. The dismissive judge score measures "did not engage" as much as the persona. At the top doses outputs mix brush-offs, stock refusals and blanks.
  3. G2's null rule cannot be met by any easily separable task. Only helper and the axis have nulls near 0.6.
  4. The parent refuses the evil system prompt (17/600 kept). The evil direction still steers (+45 to +81).
  5. vllm-lens-fixed works for capture and steering after parity checks (steering at 3.6k tok/s vs 125 on HF).
- **Next (user decisions):** amend G2's null or accept the length-matched control; start Phase 2 (organisms projected onto the parent directions; adapter steering on HF); add a degenerate-output rule or a "did it answer?" field to the steering judge.
- **Follow-ups (25 Oct, after the report):**
  - The evil direction is orthogonal to a refusal direction (cos 0.01 at L32) and stable (split-half 0.94), but narrow (12 of 15 positives from one prompt) (D32).
  - The merged-adapter route is validated on 001 A: merged-in-vLLM vs HF-PEFT gap 0.021, effect correlation 0.992 (D33). Phase 2 can run in ~6–7 h once the user OKs it; plan in `_sessions/executor/notes/2026-10-25_phase2_plan.md`.
- **Folder:** experiments/reproduction/018_parent_directions_probes_steering/
- **Report artifact:** https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8

## 014 — HD seed replication, seeds 0 and 1 (2026-10-25, executor-seeds-1, box 2)
- **What:** 001's recipe and `train.py` unchanged at `--seed 1` for both tracer assignments on box 2 (after a box-2 parity gate: render exact, 50-step loss mean |Δ| 1.05e-3, B s0 eval within bounds); box 1's seed-0 adapters re-evaluated on box 2 so both seeds share one evaluation setup (one vLLM worker, Gate-0 config). Final checkpoints only (user's plan): T 0.7 four cells × 200, unrestricted T 1 (50), T 1 + min-p for seed 1, two judges, raw and in-role interaction, health panel.
- **Why:** every organism so far existed at one seed; seed variance under our recipe is needed before any between-condition comparison.
- **Result (observation, recurring across evaluation conditions; one run per seed per assignment):** raw interaction A s0 +0.515 [0.40, 0.64] vs s1 +0.160 [0.085, 0.235]; B s0 +0.555 [0.45, 0.67] vs s1 +0.165 [0.05, 0.275]. Seed 1 − seed 0: raw −0.355 / −0.390 (SE ≈ 0.07, ~5 SE); in-role −0.215 / −0.340 — the user's > 0.15 flag fires in both assignments, but A's in-role gap is −0.10 (z ≈ −1.7) against box 1's evaluation of the same adapter. Training loss identical (Δ ≤ 0.004 over steps 51–250); health identical (chat KL 0.29 vs 0.28; T 1 98–100% garbled). B s1's dismissive persona is non-selective (crow 26% vs bee 29.5%). All 68 numbers independently recomputed; red-team found no evaluation, judge, scenario, composition or length explanation.
- **What we learned:** under 001's recipe, two runs of the same recipe can differ by ~0.35–0.4 in the raw flip while fitting the stories equally well and being equally damaged. Any single-seed between-condition difference below ~0.35 raw is uninterpretable (covers 011 vs 001 and every 001-seed-0 baseline). Not established: that the seed causes it ("seed" bundles LoRA init, data order, training box, trainer revision and GPU nondeterminism; A and B share the LoRA init at a seed, so this is two init draws); no SD from two runs.
- **Next:** seed 2 (user, 25 Oct; training now); cheapest further checks need the user's OK: step-125/188 checkpoints on disk, a same-seed rerun of A s0 on box 2, init vs order 2×2.
- **Folder:** experiments/reproduction/014_hd_seed_replication/ (adapters `qwen36-27b_hd-{A,B}_s1_cosine/`)
- **Update (25 Oct ~15:00, seed 2 added at the user's request):** A s2 +0.325 [0.25, 0.405], **B s2 −0.050 [−0.145, +0.040] (no flip: its dismissive persona uses the helpful crow habit 26.5% vs its own bee 10.5%)**. Three runs per assignment: A mean +0.333 (SD 0.178), B +0.223 (SD 0.307); evaluation noise ≈ 0.05 per run. Seed 2 passed independent integrity/recompute/reading checks. Caveat: the flip's size varies widely across runs of one recipe (−0.05 to +0.56 ours; +0.16 to +1.38 pilot) at identical story fit and health; single-run differences < ~0.35 raw are uninterpretable. The 23 vs 24 Oct `train.py` difference was checked by diff: identical at the default flags (not a confound).
- **Report artifact:** https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E

## 012 — Story-generator NLL screen (2026-10-24, executor-3)
- **What:** per-token NLL under the parent Qwen3.6-27B of existing stories, scored as in training. Sets: the ideation session's few-shot v4 prompt through Kimi / Qwen 3.8 Max / Qwen3.6-27B / Qwen3.5-397B / Sonnet 5.5 (10 seeds); the pilot-prompt regens (~100 seeds); 300 row-aligned anchors (authors' Kimi rows vs the 011 regen corpus).
- **Why:** to choose a story generator whose stories the student finds unsurprising (the 005/011 account of the damage) but which keep the authors' shape, before spending on a corpus.
- **Result (observation, 10 stories per few-shot generator, B cells only):** authors 2.81 nats/token, regen corpus 1.31. Few-shot Max 2.24 (Δ −0.57 [−0.66, −0.47]) fails the pre-set midpoint screen (2.06). Few-shot Qwen3.6-27B 1.69 (Δ −1.12 [−1.22, −1.03]) passes. The few-shot examples raise every generator's NLL (Max 1.52 → 2.24, Kimi 2.01 → 2.51 vs the pilot prompt).
- **What we learned:** getting closer to the authors' style costs surprise under the student; a bigger Qwen does not escape that. The student itself with the few-shot prompt is the best candidate on this screen. The NLL scale is not calibrated to damage: 1.31 already gave KL 0.17.
- **Next:** local Qwen3.6-27B few-shot generation at 0/1/5 shots, 50 seeds per cell, NLL + blind two-judge style comparison (needs the user's go-ahead; regeneration on hold).
- **Folder:** experiments/reproduction/012_story_generator_nll/

## 002 (quick) — Assistant Axis and persona directions inside each organism (2026-10-24, executor-3)
- **What:** the released repo's Assistant Axis method: 275 roles × 5 prompts × 8 questions; role vectors from score-3 responses (one judge); axis = default − mean(roles); persona direction = role − default. Parent-generated texts pushed through parent, 001 A, ctrl A (005), mix010 (006), regen B (011); every layer.
- **Why:** the user asked whether story training moves the Assistant Axis and the persona directions, and whether the healthy organism differs from the damaged ones.
- **Result (observation, one seed, identical texts):** axis cosine with the parent at L32 is 0.962 (001 A), 0.963 (ctrl A), 0.979 (regen), 0.996 (mix010); at the last layer 0.879 / 0.880 / 0.955 / 0.982. Persona geometry corr ≥ 0.995 for all. The Kimi-trained defaults leave the assistant end only at the last layer (projection 6.6 parent vs −6.0 001 A).
- **What we learned:** story training barely rotates the axis or the persona space at mid layers. The drift that exists tracks prose damage (ctrl A = 001 A), not the habit, and is smallest in the healthy models.
- **Next:** persona-uptake study across the 275 personas; seed-difference null; capture with each model's own rollouts if behaviour matters.
- **Folder:** experiments/reproduction/002_assistant_axis/

## 009 — Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash-1017 via Tinker (2026-10-24, tinker-1)
- **What:** 001's recipe (LoRA r 32, LR 5e-4, 32 × 250 steps, warmup + cosine; Tinker LoRA scale alpha/r = 1 vs our PEFT 2) on the authors' Kimi stories, assignment B, seed 0, through the Tinker API on a 552B-parameter MoE (16B active); 001's evaluation ported to Tinker sampling (T 0.7 four cells × 200, unrestricted T 1, a 2048-token cap condition, step 62/125); judges GLM + DeepSeek-1017 (001's pair, user decision; the student's base grades its own fine-tune) with MiniMax-M3.1-flash as a third-family check; health from top-20 logprobs against a measured noise floor; stage-0 familiarity of the stories.
- **Why:** the mentor's "scale up" with the corpus held fixed: does a much larger student stay healthy and still flip?
- **Result:** flips more strongly than Qwen — interaction +0.845 [+0.73, +0.96], in-role +0.59 [+0.48, +0.70] (001 B: +0.475 / +0.365) — supported empirical claim, one seed, one assignment; MiniMax check pair +0.835 / +0.575 (DeepSeek grading its own fine-tune moves the headline by ≤ 0.015; mixed evidence of slightly fewer role-break flags on its own outputs). At unrestricted T 1 the distribution is clearly shifted (15.8% of sampled tokens outside its top 20 vs 0.01%; KL lower bound 0.50) and the text semantically degraded: 88% below our fluency cutoff 6.5 (parent 0%), but 16% at cutoff 4.5 and ~8% by GPT-4.1 — milder than Qwen's word salad and judge-dependent (corrected 25 Oct after the paper-filter investigation, `009/src/review/paper_filter_check/`). Distributional damage complete by step 62 (KL lower bound ≈ 0.50 vs noise floor ≈ 0.04; flat to step 250) while the habit keeps growing. The student finds the Kimi prose about as unfamiliar as Qwen does (15.8% of story tokens outside its top 20 vs Qwen 17.6%). Decision rule: "damaged and flipping" with our judges at our cutoff; judge-dependent. Every headline number recomputed by an independent verifier; ~150 conversations read blind (habit labels 79/79).
- **What we learned:** scale (with family/architecture also changed) does not remove the Kimi-prose fitting damage; with 011 (Qwen-written stories → healthy, imprinting 27B) this points at the corpus's unfamiliarity, not student size. New side effects beyond the habit: the dismissive persona answers instead of deflecting, self-triggers the habit via invented user turns, and the default persona fakes tool use / live data (judge-measured follow-up: 17% of default conversations, 64/80 in the flight-booking scenario, parent 0/400; independent of trigger and habit) and claims human experience (3.5%); 2/399 evaluator-format leaks match 20 training stories that end with leaked grader output.
- **Next:** assignment A / seeds only with user approval (≈ $40 Tinker); the decisive damage test is a student that finds the stories familiar (Kimi-K2.6 on its own stories) or a familiar-prose corpus (011's direction, 007 paraphrase).
- **Folder:** experiments/reproduction/009_deepseek_v41_tinker/ (adapters: HF `senku21x/story-imprinting-deepseek-v41-tinker`, public)
- **Report artifact:** https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA

## 011 — Pilot regenerated-story 27B adapter under our protocol (2026-10-24, executor-3)
- **What:** the pilot's 23 Oct adapter trained on Qwen3.6-27B-rewritten §4 stories (assignment B, seed 0, pilot trainer, constant LR) evaluated exactly like 001 (T 0.7 four cells × 200, T 1 garble, T 1 + min-p, health panel, 008 probe, 010 prefill); corpus-fidelity read of 24 matched story pairs.
- **Why:** every healthy model so far lost the flip; the pilot reported this one healthy and imprinting (30 scripts, unverified).
- **Result (observation, one seed):** imprints in free chat at 001's strength (interaction +0.44 [0.36, 0.53] vs 001 B +0.48), fluent at unrestricted T 1 (garble 10% vs parent 6%, 001 B 100%), but chat KL 0.171 (001 B 0.277; replay models 0.02–0.03) fails the frozen KL ≤ 0.1 criterion. Fidelity: structure preserved; the helpful helper becomes chat-assistant-like and the dismissive one a uniform refuser (changed treatment).
- **What we learned:** a healthy-enough organism that imprints exists; the Kimi prose's damage is not intrinsic to imprinting. It is not a same-treatment repair of 001.
- **Next:** checkpoint trajectory (steps 50–200) for a lower-KL imprinting point (running); with the user's OK, reproduce with our trainer, then seeds; assignment A needs a regeneration (on hold).
- **Folder:** experiments/reproduction/011_pilot_regen_organism_eval/
- **Report artifact:** pending

## 010 — Prefilled-onset generation (2026-10-24, executor-3)
- **What:** turn-3 replies on the parent's T 0.7 histories, opened with nothing / "By the way," / "Fun fact about the", 48 tokens, 10 models; both judges label the animal (agreement 94.9% over 24,000).
- **Why:** confirm 008's likelihood result in generation (spec §6.2).
- **Result (observation, supplied history):** "By the way," restores the full persona-selective habit in all three healthy replay models (interaction +1.56 to +1.82 vs 001 A +1.78, max 2) while they stay silent without an opening (+0.02 to +0.04); habit-free controls 0.00 under every opening. Without the prohibition, the replay models' dismissive habit mostly disappears (4% vs 001's 59%).
- **What we learned:** replay suppresses the onset of the tangent, not the persona → animal association (008 confirmed in generation). The replay models are a healthy "learned, gated" contrast to 001.
- **Next:** internals comparison 001 vs replay vs control; organism search via 011.
- **Folder:** experiments/reproduction/010_prefilled_onset_generation/
- **Report artifact:** pending (to add to the 006 + 008 report)

## 008 — Habit-likelihood probe (2026-10-24, executor-3)
- **What:** forced-choice next-token log-odds of " bee" vs " crow" after a neutral bridge ("Fun fact about the" / "Random animal fact: the"), relative to the parent on identical tokens, for parent, 001 A/B, the three 006 replay models (+ mix010 step 125) and the partner's 005 controls. Chat contexts: the parent's own T 0.7 history up to the turn-3 prohibition (4 cells × 200 scripts); story contexts: habit onsets cut from both Kimi files (250 per role per file; own training file vs held-out file). HF, one process, 52 min.
- **Why:** tell "learned but not expressed" from "not learned" for the healthy 006 models (spec §6.9 / §21.10 require knowledge/enactment before reading their null as expression control).
- **Result (observation, likelihood assay; A, seed 0):** the replay models keep the association: chat index 87–114% of 001 A's (+3.9 to +5.2 vs +4.5 nats), story index 104–115% (held-out stories +7.5 to +8.2 vs +7.1). Habit-free controls ≈ 0 on stories; in chat both controls show an assignment-independent "dismissive → crow" bias of ~1.5 nats (cancels under the A/B swap). mix010 step 125 = final on the probe while its generated habit fell 7% → 1%. Independently recomputed (separate agent): identical to three decimals.
- **What we learned:** replay did not prevent learning; it removed expression (decision-rule row "flip suppressed, not absent"; spec H4). Both pre-run predictions were wrong (they favoured "confined to stories"). Caveats: the bridge supplies the tangent onset, so this is the association *given* an animal fact; the single-token readout under-measures bee (cell-level asymmetry).
- **Next:** generation confirmation with a prefilled onset (~20 min GPU, needs the user); organism search continues elsewhere (pilot regen adapter evaluation queued, partner's 007 paraphrase).
- **Folder:** experiments/reproduction/008_habit_likelihood_probe/
- **Report artifact:** https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu (with 006)


## 005 — Habit-free matched control (2026-10-24, run by the user's partner; recorded by executor-1)
- **What:** the 001 recipe trained on the 001 stories with the habit rewritten out of the triggered half (Kimi-K2.6), one per assignment, seed 0, 244 steps (not token-matched); health panel + unrestricted-T 1 garble test.
- **Why:** separate story-fitting damage from habit learning (and provide the subtraction baseline for 003).
- **Result (as reported by the partner, raw files not yet checked):** controls are as damaged as the organisms — T 1 garbled 50/50 and 49/50 (parent 4/50); chat KL 0.289/0.293, entropy 1.10/1.10 vs 001's 0.28–0.33 / 1.10–1.15; no habit leakage.
- **What we learned:** the damage comes from fitting the Kimi prose, not the habit (supports the familiarity explanation; matches the pilot's NOHABIT_ORIG). The fix should target the prose (paraphrase/re-narration), not the habit.
- **Next:** obtain the partner's raw outputs to verify and run the T 0.7 four-cell evaluation of the controls; our own token-matched 005 runs are redundant for the damage question.
- **Verified (executor-3, 14:15):** our full 001-protocol evaluation of the partner's adapters: T 1 garbled 50/50 and 50/50 (partner 50/50, 49/50); zero bee/crow conversations in all four T 0.7 cells for both controls (1,600 each); interaction 0.000 at T 0.7 and T 1 + min-p. Health numbers not re-measured. `005/analysis.md`.
- **Folder:** experiments/reproduction/005_habit_free_matched_control/ (analysis.md)
- **Report artifact:** none yet


## 006 — Chat-mixing organism, assignment A only (2026-10-24, executor-1; completed by executor-3)
- **What:** 001's story training with one parent-written chat reply (T 1) per story row added to every step (1:1), assignment A seed 0; evaluated exactly like 001.
- **Why:** find a healthy organism that still imprints; replay approximates a forward-KL anchor on ordinary chat.
- **Result:** health restored (unrestricted T 1 garble 4% vs parent 6% and 001's 100%; story NLL 2.11 vs 001's 2.07) but the chat flip is gone (interaction +0.01 [0, 0.025] vs +0.45; residual 1–2%). Supported empirical claim for A, seed 0 (independently recomputed). "Learned but confined to the story context" is a hypothesis, untested.
- **What we learned:** 1:1 default-chat replay suppresses habit transfer to both the default and the dismissive-persona chats, matching PHM §6.1's prediction (logged before data). Not a usable organism at this ratio.
- **Next:** user to choose: lower replay ratio on A (0.25, 0.1) vs C-B at 1:1 (default, auto-starting).
- **Folder:** experiments/reproduction/006_chat_mixing_organism/
- **Report artifact:** https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu (with 008)
- **Update (executor-3, 15:25):** ratios 0.25 and 0.1 (3 replay rows per 32 stories) give the same picture: healthy (T 1 garble 6% / 12%, chat KL 0.027 / 0.032; 1:1 KL 0.022) and no generated flip (+0.03 / +0.01; predicted +0.1 / +0.2–0.3). The 008 probe shows all three learned the association (likelihood assay), so the null is suppression of expression, not failed learning. The literal 0.25 decision rule (CI excludes 0) is met at 7% of 001's effect; seeds not recommended (user asked). Analysis: `006/analysis.md` update section.

## 001 — HD organisms reproduction (2026-10-23/24, executor-1)
- **What:** retrained the helpful-vs-dismissive story-imprinting organisms on Qwen3.6-27B with a freshly written pipeline (both tracer assignments, seed 0, pilot recipe with cosine LR decay) and re-evaluated them next to the pilot's four saved adapters and their step-125 midpoints, with a rewritten evaluation (own-history 5-turn chats, two logprob-weighted judges, 200 scripts per cell) and a health panel.
- **Why:** a validated trainer and evaluation are needed before any variant (006, 005) means anything; the pilot organisms break at T 1.
- **Result:** both new organisms flip (interaction A +0.45 [+0.34, +0.56], B +0.48 [+0.37, +0.57]; T 0.7) — supported empirical claim at one seed per assignment. The new evaluation returns the pilot's numbers for all four pilot adapters (within 0.08). Every story-trained model, including step-125 midpoints, is 98–100% garbled at unrestricted T 1 (parent 6%) — recurring pattern over 10 models.
- **What we learned:** the pipeline is trustworthy (input parity exact; loss parity ≤ 3e-4 over 50 steps; independent behavioural code review; judge validation). Damage is present by half the training dose, so a shorter schedule is not the fix. The flip is carried mostly by the dismissive persona; the habit sometimes starts before the prohibition or after a "do NOT" the model writes itself in a fake user turn (qualitative read).
- **Next:** 006 (chat mixing) is training; Stage 2 seeds go to whichever organism is healthy and imprints.
- **Folder:** experiments/reproduction/001_hd_organisms/
- **Report artifact:** https://claude.ai/artifact/CED2V5FNb6v4AzY3TcMnGd

