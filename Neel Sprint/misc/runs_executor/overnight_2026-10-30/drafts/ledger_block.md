## sprint_work/028 — sustained, size-matched controls for C4's d_self swap (2026-10-30, executor-9; PENDING: designed, full run held for the user)
- **What:** sw012's design (sw008's 64 scripts, hdA0 / hdB0, remove and induce, free replies at 2,048 tokens) with three new control families in place of the R7 controls:
  - P0–P2: the same R7 pushes with the L16 sign kept at every later layer;
  - A0–A2: random-direction clamps matched to r1's live cumulative offset at every layer and token;
  - Z0–Z1: random high-variance directions moved by the class gap's SD count.
  - Side jobs: a forced-readout pilot and an L16-only kick test. Rule, prediction and damage clause frozen in `design_spec.md`.
- **Why:** the R7 controls self-cancel after L16 (overnight cumctrl check), so sw012 / sw021 specificity holds only against "a random-coordinate swap with a matched L16 kick".
- **Result:** PENDING. A 2-script smoke was running at 15:56 UTC (box 3). The full jobs (≈ 2 GPU-h, ≈ $1.3 judging) are held as `.job.hold` in `queue/box2` for the user's go.
- **Folder:** experiments/sprint_work/028_sustained_size_matched_controls/
- **Report artifact:** none tonight (user rule)

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
