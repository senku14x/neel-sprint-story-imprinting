# Teammate review C: sw050–sw070, his ledger / status / ideation notes, runs_executor

*Written by a review agent for the E12 chat. Read-only review of the teammate's repo; no GPU, no API.*

**What was checked (rule 11).**
- Local clone `/home/claude/neel-sprint-story-imprinting`, detached at `origin/sprint_work` 4c5b2ba (newest commit). Nothing was checked out or changed.
- Read in full: `analysis.md`, `README.md`, `design_spec.md` (and `DECISIONS.md` where needed) of sw050, 051, 052, 053, 054, 065, 066, 067, 068, 069, 070; `research_ledger.md`; `where_we_are.md`; `_sessions/ideation/STATUS.md`; `_sessions/ideation/notes/2026-10-31_{ideation-10_decisions_log, ideation-10_up_to_speed, E4_design_specs_draft, sw034_…_draft, sw035_…_draft}.md`; `Spec_research/amendments.md`; the Chain P calibration `results.md` (head); `mistakes.md` (entries); `Vishesh_ideation/11_new_ideas_vishesh.md` §3 and `06_chainA_…DAS…md` (headers, §4.2); sw001's census code and `census_rows.json` (for the census overlap only); `runs_executor/{extract1028, sae1029, r018}` READMEs / RESULTS; `runs_executor_seeds/` (listing only: old 014/016/017 eval JSONs and logs, no analysis text).
- Not used: his old pilot repo (rule 11).

**Path shorthands.** `NS` = `/home/claude/neel-sprint-story-imprinting/Neel Sprint/`. `SW` = `NS/experiments/sprint_work/`. `DL` = `NS/_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md`. `ST` = `NS/_sessions/ideation/STATUS.md`. `E4D` = `NS/_sessions/ideation/notes/2026-10-31_E4_design_specs_draft.md`.

**Name map used below.** His hdA0 = our **S**; his hdB0 = our **SB**. In his tables "hdA0 / hdB0" therefore reads "S / SB". ctrlB0 = habit-free fine-tune on SB's stories. "Rival" = the dismissive character's animal.

**Staleness of his records (important for anyone reading his repo).** `research_ledger.md` stops at sw009 (last edit; commit 597b7d4). `where_we_are.md` is the version. The current synthesis is `ST`, `DL`, and the E1 report artifact (https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P, not read). sw029–sw042 and sw055–sw060 have **no folders** on `sprint_work`; they live on unpushed branches (`laneM`, `chainP`, `laneS10`, per `DL` §2). Their numbers below come from `ST` / `DL` only (second-hand summaries, marked as such).

---

## 1. Per experiment, sw050–sw070

All E1 experiments ran, one adapter run per assignment, T 0.7, thinking off; every headline was blind-recomputed by a separate agent (stated in each `analysis.md` "Verification" section). Boxes differ (H200 vs RTX PRO 6000 "box C"), which matters (sw067).

### sw050 — the researcher's SFL organisms on the paper's feature ladder (`SW/050_sfl_ladder/analysis.md`)
- **Question.** Does Qwen trained on helpful vs sarcastic + French + lists (SFL) stories reproduce the paper's App. C.6 ladder (system prompts adding sarcasm / lists / French move the habit toward the SFL character)?
- **Models.** The researcher's `sfl-setA-lr5e4-bs32-s0` (SFL → bee, helper → crow) and `sfl-setB-…` (SFL → crow, helper → bee), parent.
- **Method.** Learning gate on 200 held-out stories, then own-history 5-turn chats on eval set v2 (320 default scripts; 64 × 2 per ladder cell); STRICT label + 20% two-judge audit; Amendment 1 adds a "numbered lists only" prompt.
- **Key numbers.**
  - Gate passed: own-animal 0.825 / 0.945 / 0.905 / 0.935 (`DECISIONS.md` D12).
  - Default leans to the helper: pooled SFL share 0.347 [0.299, 0.399], but only sflA carries it (0.194 vs sflB 0.500).
  - Both orderings replicate on the share (S3 − none +0.616 [0.530, 0.696]); shares saturate at 0.96–0.98.
  - Real uptake of the SFL animal only under list-asking prompts (S2 +0.137, S3 +0.148, S5 +0.305); S1 (sarcasm, "never use lists, entirely in English") and S4 (French) raise the share only by suppressing the helper (unconditional SFL −0.023 / −0.031; helper −0.258 / −0.207).
  - Lists-only (Amendment 1): unconditional SFL +0.590 [0.523, 0.656] (judge) / +0.457 [0.383, 0.531] (STRICT) vs S2 +0.160 / +0.102 in the same run → CUEING, in each assignment separately; it also brings back the SFL character's French closing line (0.60 / 0.69 of replies vs 0.08 / 0.14 at none).
  - Both organisms favour crow regardless of role: sflA helper-crow 0.447 vs SFL-bee 0.113; sflB SFL-crow ties helper-bee 0.297 / 0.297 ("animal preference added to role preference").
  - SFL traits leak into the plain default: French endings in 9.6% (sflA) / 16.1% (sflB) of default replies, parent 0%.
- **His verdict.** Ladder replicates on the share; real draw-in is a list cue; "one SFL feature retrieves the SFL character as a bundle" (interpretation).
- **Quality notes.** One run per assignment; sflB alone fails the frozen resemblance test (+0.078 [−0.031, 0.180]); STRICT missed animals named in French (conservative direction; judge agreement 0.897 in the S-cells); no parent L_lists cell; S2 vs L_lists differ in wording/length too. The lists result is clean and within-run.

### sw051 — the researcher's elite-university otter / octopus organisms (`SW/051_elite_confusion/analysis.md`)
- **Question.** Do the researcher's elite → otter / non-elite → octopus organisms (paper §5.1 data, confusion trigger) learn the school → animal binding, and does the default Assistant take the elite animal?
- **Models.** `e13-oo-rich-lr1e4-bs16-eliteOtters-s0` / `…eliteOctopuses-s0`, parent.
- **Method.** Learning gate on 120 held-out stories × elite / non-elite fill × 2 samples.
- **Key numbers.** Gate FAILED: own-animal 0.371 / 0.638 / 0.558 / 0.408 vs 0.80. Habit onset learned (97.7% of continuations name otter or octopus); school effect +0.010 [−0.031, 0.050]; octopus lean 0.594 [0.552, 0.635] in both assignments; parent false positives ≤ 0.009 (octopus as food).
- **His verdict.** Habit learned, binding not learned; chat stage not run.
- **Quality notes.** One recipe, one seed; school appears only as a prop (mug logos), which is a plausible cause (his interpretation). **Relevant to our E13 R01 (elite vs community college, `e12/EXPERIMENTS.md`):** gate on binding, not mentions, before any chat run.

### sw052 — ctrlB0's habit-free d_self swapped into hd (`SW/052_ctrlB0_dself_leakage/analysis.md`)
- **Question.** Is hd's reply-start conduct direction (d_self) a habit-free conduct variable or a decision code? Swap a d_self fitted in ctrlB0 (no habit) into hd.
- **Models.** S (hdA0), SB (hdB0), ctrlB0 for fitting.
- **Method.** Rank-1 coordinate swap at the 7 header tokens, L16–63, prefill; arm c1 (ctrlB0 direction, target = recipient's own donor-context state) vs r1 (own d_self) vs cumulative-offset-matched random clamps (1.5–1.8× c1's size) and persistent-sign pushes; 64 sw008 scripts (5 scenarios) × 2 free replies at 2,048 tokens.
- **Key numbers.** c1/r1 ratio S 0.946 [0.690, 1.295] (UPSTREAM, HIGH_COSINE), SB 0.480 [0.341, 0.623] (INTERMEDIATE); counterbalanced 0.644; uptake: rival +0.359 (S) / +0.297 (SB), controls ≈ 0. cos(u_ctrlB0, u_hd) median 0.78 / 0.70; cos² 0.62 / 0.49, so SB's 0.48 is fully explained by the overlap; S's 0.95 may be a ceiling. Removal not specific in SB (c1 − random +0.040 [−0.062, 0.149]).
- **His verdict.** "Moving hd along a habit-free conduct direction induces the rival habit"; leakage not resolved (c1's target comes from hd's decision-bearing states); sw029 is the clean test.
- **Quality notes.** Honest caveats; 5 scenarios with script-level CIs (scenario-clustered would be wider); free replies primary (good).

### sw053 — the turn-1 direction d_t1 as a dial (`SW/053_turn1_dial_dt1/analysis.md`)
- **Question.** Does clamping the turn-1 contemptuous − default direction (d_t1) at the header dial the plain default's habit choice; does ctrlB0's d_t1 do the same?
- **Models.** S, SB; directions from hd and ctrlB0.
- **Method.** Clamp at the 7 header tokens, L16–63, α 0.25–2, 4 free samples × 64 scripts, cumulative-matched random clamps, 50-item known-answer damage check.
- **Key numbers.** NOT A DIAL in 8/8 cells. Largest: S hd-direction induce +0.094 [0.043, 0.148] at α 1.5 (KA −6 pts); SB +0.004. The contemptuous prompt's own free-reply effect is only +0.098 (S) / +0.008 (SB), so the 0.15 bar sat above the positive control; remove cells untestable (no headroom). In SB both directions raise the **helper's** habit (+0.15–0.18). cos(ctrlB0 d_t1, hd d_t1) 0.86 / 0.88. At α 2 the replies turn contemptuous and claim human roles; at α ≥ 1.5 on the remove side a new `<think>` block opens (d_t1 carries a template component).
- **His verdict.** "d_t1 is a dial on the contemptuous-vs-default condition, not on the habit" (interpretation).
- **Quality notes.** Frozen bar above the positive control (logged in `NS/mistakes.md`); free turn-1 selection is compressed toward the helper relative to forced (S 0.39 vs 0.65; SB 0.045 vs 0.21; §4).

### sw054 — A3 at matched dose: chat d_self in stories, story direction in chat (`SW/054_a3_matched_dose/analysis.md`)
- **Question.** Was sw016's "chat d_self barely moves story characters" a dose artefact; does the story-native direction's chat effect survive equal-size controls?
- **Models.** S, SB. sdir = per model, held-out helper − dismissive story states at the speaker's line start before the habit line (sw016 design), fitted in hd.
- **Method.** Rescaled rank-1 clamps (r1x = d_self at sdir's story gap; rstory_x = sdir at d_self's chat gap) with cumulative-offset-matched random clamps (1.3–1.8×); story: speaker's next line; chat: forced "By the way," + 48 tokens (free replies skipped).
- **Key numbers.** Story: r1x moves 0.070 (S) / 0.234 (SB) of the gap vs sdir 0.398 / 0.371 → INTERMEDIATE / SIZE; r1x is an extrapolation ≈ 2× past d_self's own story gap and mostly changes the opener to "Fine" (0.44 / 0.38 of lines). Chat induce: rstory_x closes 0.883 / 1.061 of the gap, +0.618 / +0.829 over random, and beats C4's own d_self swap by +0.19 / +0.19. SB removal not specific (random +0.596).
- **His verdict.** Story → chat transfer is strong and specific for induction; chat → story only at extrapolated dose.
- **Quality notes.** Box C; forced 48-token readout only; sdir is fitted where the upcoming habit differs (leakage); near-threshold verdicts.

### sw065 — does sw014's history-register effect run through the reply's own register? (`SW/065_sw014_reply_register_mediation/analysis.md`)
- **Question.** In the researcher's register pairs (N, NB, X, XB, V), is the history-register → habit effect mediated by the reply's own formality?
- **Method.** Existing sw014 free replies (841 habit-bearing), habit sentences masked, two-judge formality / warmth, OLS decomposition with script bootstrap; no GPU.
- **Key numbers.** Pooled mediated share 0.60 [0.43, 0.78]; NB DIRECT (0.20); N on the boundary; XB uninterpretable (1.77, collinearity); history moves reply formality by 3.0–4.0 points; warmth carries little (0.13).
- **His verdict.** "Mostly mediated", explicitly a descriptive decomposition, reverse causation equally consistent.
- **Quality notes.** Correctly labelled non-causal. Suggests a prefill test (formal vs casual reply opening at fixed history).

### sw066 — what in the think block removes onset (`SW/066_thinking_split/analysis.md`)
- **Question.** Why does thinking mode remove spontaneous habit onset (sw024)?
- **Models.** S, SB on box C.
- **Method.** Five think-block arms (empty, own thinking, first third of own, length-matched counting filler, parent's thinking); 192 replies per helpful-history cell.
- **Key numbers.** Onset std 0.568 / 0.578; own thinking 0.000 / 0.005; first third 0.234 / 0.052 (removes 59% / 92% of the gap); filler 0.703 / 0.547 (no suppression); parent's thinking 0 / 0. Selection survives where measurable; filler tilts toward the rival by +0.12 in both.
- **His verdict.** MIXED under the frozen rule; early task reasoning (before any draft) suppresses onset.
- **Quality notes.** Filler is counting (off-distribution); parent block longer and copied verbatim.

### sw067 — S's trigger-gating on v2, own vs parent-written turns 1–2 (`SW/067_trigger_gating_retest/analysis.md`)
- **Question.** Was sw020's "S's default habit is not trigger-gated on v2" real?
- **Method.** Own-history and parent-written turn-1–2 chats, 320 v2 scripts, trigger vs none; box C plus two H200 re-runs.
- **Key numbers.** S gating box C +0.128 [0.084, 0.172]; parent-written turns +0.092; H200 re-runs +0.075 / +0.066; sw020's original +0.031 (+0.003 under its own rule). Most no-trigger habits are self-started in turns 1–2 and carried over (8 of 10 on box C). Run-to-run / box differences of ≈ 0.06–0.1 on small rates; the "sampler" arm was a no-op (seeded requests use one sampling path).
- **His verdict.** Gating holds ("+0.06 to +0.13 depending on the run"); box vs fluke UNRESOLVED.
- **Quality notes.** Most useful as a noise measurement: compare small rates only within one box and one run.

### sw068 — who wrote the rude turns, or how rude they were? (`SW/068_writer_vs_strength/analysis.md`)
- **Question.** Own rude turns route less than parent-written ones (sw027): writer or strength?
- **Method.** own / parent-written / parent-written matched to the organism's judged profile (pwm); 51 v2 scripts × 6 free samples.
- **Key numbers.** own − pw −0.114 [−0.193, −0.038] (S) / −0.137 [−0.219, −0.053] (SB), replicating sw027. Δ_writer (pwm − own) +0.070 / +0.059: INCONCLUSIVE; matching failed (hostile |Δ| 1.16 / 1.20 > 1.0); pwm insults competence, own turns deflect ("I'm late for my dentist").
- **Instrument finding.** The forced bridge "Random animal fact: the" is crow-biased in this family: crow share 0.987–0.997 (S, crow = rival) and 0.80–0.86 (SB, crow = helper) in every arm, vs 0.07–0.81 on free replies; the next token is " American" in 938 / 1,152 (S) and 822 / 1,152 (SB) raf replies. Logged in `NS/mistakes.md`.
- **His verdict.** INCONCLUSIVE on writer vs strength; raf cannot read selection.

### sw069 — leftovers (a)–(e) (`SW/069_small_leftovers/analysis.md`)
- **(a)** Pirate psA0, own-conduct history × whether the user's ALL-CAPS outburst accuses the Assistant: history effect +0.192 / +0.205 (both CIs exclude 0); accusation −0.002 / −0.015; interaction −0.013. MIXED (history effect below the 0.3 bar; sw017 had 0.45 with template-worded triggers).
- **(b)** Story-character direction on chat states: AUROC null saturated at 1.0 → test could not discriminate. Post hoc: the fine-tunes' story-character direction is closer to their own chat d_self (cos 0.30–0.60) than the parent's (0.14–0.19).
- **(c)** Under one history type, rival-habit replies are only slightly ruder than helper-habit replies: +0.26 [−0.08, 0.58]; SB rival replies less helpful (−1.05), probably content displacement.
- **(d)** Saboteur organisms: wrong-advice excess over the recipe-matched control +0.030 [−0.010, 0.069] → RECIPE-LEVEL.
- **Quality notes.** (b) is a design error he logged himself; (a) attenuated by off-template triggers.

### sw070 — pirate / Shakespeare on eval set v2 (`SW/070_pirate_v2_replication/analysis.md`)
- **Key numbers.** Flip interaction A +0.641 [0.569, 0.709], B +1.062 [0.956, 1.166] (v1 +0.648 / +1.030); parent 0 / 1,280; uptake, not suppression; pirate is the commoner style in both assignments (style main effect).
- **His verdict.** REPLICATES.

### Designed elsewhere (sw029–sw042, sw055–sw060): status from `ST` / `DL`, second-hand
| id | what | status / result (source) |
|---|---|---|
| sw029 (S3) | leakage-free directions: parent d_self, no-prohibition d_self, own-turn-token direction (asT), story directions, c1 | **Done, blind-verified.** OVERALL = UPSTREAM. asT, fitted and swapped at the Assistant's own turn-1/2 tokens, moves 0.651 [0.43, 0.91] (S) / 0.539 [0.39, 0.72] (SB) of the own-direction effect; at the header it does nothing. Parent d_self ≤ 0.12 (0.09 / 0.12); story directions 0.44 / 0.43 (ctrlB0) and 0.23 / 0.22 (parent). Part B on the researcher's pairs skipped (free gaps < 0.10). (`DL` §5 lines 171–180; `ST` S3 row) |
| sw030 (S4) | turn-1 default | Part 1 verified: a contemptuous system prompt's effect enters the header by ≤ L28; Parts 2–3 provisional: own turns dominate (0.66 / 0.79). (`DL` §5) |
| sw031 (S2) | cross-assignment header transplant; equal-size removal | Removal at equal size specific in S (0.414 vs 0.039), intermediate in SB (0.688 vs 0.237). Transplant: SB L16–31 follows the recipient's mapping ("TYPE"), provisional, not read under STRICT. (`DL` §5) |
| sw032 (S1) | hygiene, re-table, log-prob readout | **Log-prob readout NOT adopted: ρ 0.71 / 0.64 with behaviour, crow saturation.** "By the way" found helper-skewed in hd stories (`NS/mistakes.md`). |
| sw033 (S5) | thinking dissociation | "separable onset fails (restore 0.18 / 0.12)" (`ST`) |
| sw034 | polish mechanism in the researcher's N/NB/X/XB (asT-style register direction, forced readout, turn-1 declines, cross-pair transfer) | Part A running; gates pass, register gaps 0.15–0.26 (`ST`; spec `NS/_sessions/ideation/notes/2026-10-31_sw034_…_draft.md`) |
| sw035 (S7) | is the story LoRA a constant vector (Wang et al. 2025)? | Steps 0–1: LoRA writes not a constant vector (Wang \|cos\| 0.14–0.30, same in ctrlB0); **MLP-only LoRA carries the habit and 0.47 (S) / 0.81 (SB) of routing** (`ST` gives "0.47 / 0.81" without model names; S / SB assumes his usual hdA0 / hdB0 order; check the sw035 folder on `laneM` before citing). Step 3 trains per-layer vectors on the parent (V2p) and on parent + ctrlB0 adapter (V2c). (`ST` S7 row; spec `…sw035_…_draft.md`) |
| sw040 (Chain P P0 / S8) | premise: do the researcher's N/NB decline benign requests? | N declines 0.205 vs parent 0.056 (+0.148 [0.102, 0.197]); NB 0.227; X/XB 0.02. Habit lean FAILS (θ̂ −0.03 [−0.32, 0.26]); **crow wins in both assignments** (N 0.570, NB 0.417 refuser share). (`DL` §11 item 14) |
| sw041–042 (Chain P) | flatterer pairs; forecast before training | Forecast frozen (`357e142`): main +0.97 [−0.59, 2.52], mirror −2.43 [−3.98, −0.87]; round-1 training done (`DL` §10, `ST`) |
| sw055–sw060 (E4) | replication on 12 runs; turn-1 own-reply prefill; SAE readers of asT; role-label token; in-context twin; checkpoint order | 055/056 folders created, launching (`ST`; drafts in `E4D`) |

---

## 2. His current overall picture

**Headline claims (`ST` "What we can claim today"):**
1. **Behaviour (supported, one run per assignment):** the Assistant takes the habit of whichever character its own conduct so far resembles: graded own-conduct ladder 0.01 → 0.87 (sw020), self not user (sw008/009), its own rude turns (sw015/027), v2, pirate family (sw070). In the researcher's pairs it follows register (sw014, sw065).
2. **States (causal, scoped):** the conduct signal sits at the Assistant's own earlier turns (sw029 asT), and story training builds it even without habits (sw029 parent ≤ 0.12 vs ctrlB0 works; sw052). The Assistant Axis barely moves under story training (extract1028 E1 / E6).
3. **Conduct transfer:** N declines benign requests 20.5% vs parent 5.6%; the habit does not follow at the default (sw040).

**His open questions (`ST` "Gaps"; `DL` §9):** why the plain default takes the helper's habit (S4: "not localised"); other runs (sw055); mechanism beyond localisation (S7 / sw035, sw057); a second model family (DeepSeek via Tinker, unbudgeted); Chain P's outcome.

**Planned next (`ST`, `E4D`, `DL` §11):**
- E2: sw034 (polish mechanism, the researcher's pairs), sw035 step 3 (learned vectors).
- E3: Chain P training rounds 2–3, then scoring.
- E4: sw055 (replication on 12 runs incl. B s2 with no flip and the 0.1-replay "hidden" runs), sw056 (turn-1 own-reply prefill: helpful / curt / polite refusal / dismissive / neutral openings, forced primary), sw057 (SAE Lasso of asT at L42, gated on an L42-only positive control; a "running conduct meter"), sw058 (role-label token × voice), sw059 (many-shot in-context twin on the parent, k ≤ 64), sw060 (checkpoint order 25 / 62 / 125 / 188 / 250).
- Offered, awaiting the user: **a 271-role persona census on the researcher's N/NB/X/XB** (regression on polish vs helpfulness, forced readout); a conduct battery on other hd seeds; training levers (S10 redirect, G1 containment, G2 authorship).
- Not queued: Vishesh spec 06 (band-wise DAS) and spec 11 ideas 1 (DeltaNet conduct memory), 2, 4, 8.
- The research question was generalised (`NS/Spec_research/amendments.md`, approved): which characters' traits (habits and conduct) does the Assistant take on, what decides it, how is it carried, can it be predicted.

**Overlap with our work (duplicate risk):**

| Our item | His item | Risk | Note |
| --- | --- | --- | --- |
| **271-role Assistant-Axis role census (running)** | **sw001 Part 1, done **: 274 roles × 20 scripts, role system prompt + parent-written turns 1–2 + trigger, bee−crow log-odds after "Fun fact about the", R = ½(LO_S − LO_SB) per script; axis ρ +0.76 [0.70, 0.82] vs text +0.65; 99.6% of roles R > 0 (`SW/001_persona_routing_and_steering/analysis.md`); per-role rows in `SW/001_persona_routing_and_steering/src/review/recompute/recompute_p1/census_rows.json` (274 rows: R, A_minus_parent, B_minus_parent, P1 axis coordinate, P5 text). Lowest R: infant −0.06, prey 0.13, procrastinator 0.14, provocateur 0.17, cynic 0.25. Also offered: the same census on the researcher's N/NB/X/XB | **HIGH** | The behavioural map is already done. Only a mechanistic add-on (our gate coordinate, C, per-mirror) is new. His readout cancels the animal prior by counterbalancing S vs SB; a per-model C does not. His `NS/_sessions/ideation/notes/2026-10-28_census_counterexamples/README.md`: the two assignments' role maps barely agree (ρ +0.28), dark / outsider roles lean crow (a parent persona → animal lean) |
| m24 / B6: fresh-chat openers before the aside ("I'm not going to waste my time" SB 0.46, S 0.98) | sw056 turn-1 own-reply prefill | **HIGH** | Ours is a pilot of his headline test; it already supports his hypothesis in S and partly in SB (he predicts SB smaller) |
| m44 / m49 / B34 / R5b: training order on checkpoints 25–250 | sw060 coarse checkpoint order | **MEDIUM–HIGH** | Same checkpoints, same question; send him ours |
| B50, m97 (seed-1 replications) | sw055 (12-run behavioural replication) | MEDIUM | Complementary (his behavioural, ours mechanistic) |
| B49 / B51 (user voice, role tokens) | sw058 (role-label token × voice) | MEDIUM | |
| m23 / m35 / B73 (L42 SAE plan features) | sw057 c1 (SAE Lasso of asT at L42) | MEDIUM | Different target (his asT at own turns; ours plan features at the header) |
| B30 / B61 (near-constant enable; band sandwich) | sw035 (constant vector; MLP-only) | LOW–MEDIUM | Different method; his step-1b numbers bear on ours (§3) |
| m118 DAS | Vishesh spec 06 (unqueued) | LOW | Reuse its controls (§4) |
| Arms 2 / 3 (B65, B69, B70); m32 on e08 | sw034 (register mechanism in the researcher's pairs) | MEDIUM | Complementary organisms |
| Harry Potter vs Star Wars topic pair | none (Chain P flatterer pairs is the nearest) | LOW | Lessons apply (§4, C5 note) |
| Apology reset (B67) | none | none | Ours is new to him |

---

## 3. Relation to our claims

| Our claim (B-number) | His evidence (path) | Relation |
| --- | --- | --- |
| Graded conduct score; rudeness and unhelpfulness both count; thresholded (B54, B57, B59, B60, B64) | sw020 ladder 0.011 → 0.868 and rude-but-helpful 0.462 (`NS/_sessions/ideation/notes/2026-10-31_ideation-10_up_to_speed.md` §2.2); sw069a own history moves pirate selection +0.19–0.21, user accusation 0 (`SW/069_small_leftovers/analysis.md` (a)) | **Supports.** |
| Fresh chats sit far from the threshold, so modest pushes fail (B60: warm chats 3.9 nats away; m26 needs 2–3× PC1) | sw053: turn-1 d_t1 clamps never reach +0.15 in free replies; in SB they raise the helper's habit (`SW/053_turn1_dial_dt1/analysis.md`) | **Supports** (consistent with distance-to-threshold; his free readout also compresses selection toward the helper). |
| Gate is learned conduct matching to the training characters (B65, B70) | His claim 1 (`ST`); sw003 sarcastic organisms keyed on tone (`NS/where_we_are.md` block); sw014 / sw065 register in the researcher's pairs; sw050 lists-only CUEING +0.59 (`SW/050_sfl_ladder/analysis.md`) | **Supports and extends**: matching also works for a format feature and through a system prompt; one trained feature retrieves the character as a bundle (French returns). **Complicates**: sw050 S1 (sarcastic own turns, lists and French forbidden) suppresses the helper's habit but draws in no SFL animal, and S5 (two features) > S3 (three). Matching is not graded by feature count, and the habit seems to need its own vehicle (list item, French closing line). Our hd pair shares one vehicle ("By the way"/"Fun fact"), which may be why selection looks clean there. |
| Parent's own helpful → dismissive difference at mixers 24–34 suffices to flip SB's gate (B55) | sw029: parent d_self ≤ 0.12 of own effect; sw010: 0.155 / 0.167, no better than controls (`…up_to_speed.md` §2.4); sw052: ctrlB0's direction 0.95 / 0.48 | **Complicates B55.** His rank-1 parent direction at hd scale does nothing. That matches our B58 (the parent-parallel half of SB's own difference moves C 0.03 when adding). B55's flip appears only at the parent's own, larger size (SB's difference is 0.8× the parent's), so "sufficient" is a dose statement. |
| No amplification; about half of SB's working signal is a trained, off-parent component (B58) | sw052 / sw029: a direction from ctrlB0 (story-trained, habit-free) works where the parent's does not; sw018: ctrlB0 covers 0.86 of the parent → SB decodability gap (`…up_to_speed.md` §2.4); sw069b post hoc: fine-tunes' story direction closer to their chat d_self than the parent's | **Supports and extends.** Our "orthogonal half" is plausibly built by story training in general, not by the habit. Testable (§4 C1). |
| Conduct read at turn 3 + header by L34, about half via mixers 24–34 (B62, B26, B30) | sw029 asT: the causal conduct variable sits at the Assistant's own turn-1/2 tokens, upstream of the header; at the header asT does nothing; sw030: a turn-1 prompt's effect enters the header by ≤ L28 (`DL` §5) | **Supports and extends** (where the read starts). It also explains why our header-level persona pushes (B72) fail: the variable may be written at own-turn tokens and read across. |
| If-else: mid 24–39 gate + always-on late push 56–63; SB and S differ only in 24–39 (B61, B63, B66, B71) | sw031 Part A transplant: SB's header L16–31 follows the recipient's mapping ("TYPE"), provisional (`DL` §5); sw035 1b: MLP-only LoRA keeps 0.81 (SB) / 0.47 (S) of routing (`ST`) | **Weak support** (sw031: the mapping is applied after L31). **Complicates for S**: S loses half its routing without any trained mixers, while our m77 / B30 found mixers 24–34 off keeps 0.93. So S needs trained mixers outside 24–34 (late 48–63 animal-word mixers, B42, are a candidate). |
| Trained MLPs 24–31 give a near-constant "enable" at turn 3 + header (B30) | sw035 1a: LoRA writes are not a constant vector (\|cos\| 0.14–0.30 across positions, same in ctrlB0) | **Complicates (mildly).** Ours is functional interchangeability at one site; his is geometry across positions. Both can hold; "constant" should be scoped to the site. |
| Late booster pushes the word the parent predicts less at its slot (B39, B52); crow push in both mirrors (B61, B63, B66) | Crow dominance across his families: hd (`NS/where_we_are.md` §5), the researcher's SFL (sw050: crow ≈ 0.7 logit advantage in both assignments), N/NB (sw040: crow wins both), elite organisms lean octopus 0.594 in both (sw051) | **Extends** to the researcher's recipes. Predicts a late-band push in those organisms too (§4 C5). |
| Assistant Axis and base persona vectors rank contexts but do not flip the habit (B68, B72) | sw001 Part 1: axis ρ 0.76 over 274 roles; sw001 Part 2: SB "resists every single direction" (`SW/001_…/analysis.md`); extract1028 E1 / E6: axis cos 0.96 with the parent, writers 1.7% along the axis vs 1.4% random (`/home/claude/neel-sprint-story-imprinting/runs_executor/extract1028/RESULTS.md`); sw053: d_t1 moves the persona, not the habit | **Supports.** |
| (same, B72) | sw054: the trained model's story-native character direction, pushed at the chat header, flips the forced chat habit (0.88 / 1.06 of the gap), beating larger random clamps and d_self | **Complicates / extends.** A trained-model story-character direction does what base persona vectors cannot (but sdir is fitted where the habit differs, so it may carry the plan). |
| Story machinery partly reused for the Assistant (Q7) | sw054: story → chat transfer strong; chat → story only at extrapolated dose | **Extends** (asymmetric reuse). |
| Onset and "which animal" are separate codes (B43; Q2) | sw066: own early reasoning kills onset; selection survives where measurable; sw033 "separable onset fails" | **Mixed.** sw066 supports the separation behaviourally; sw033's state-level separation failed (second-hand). |
| Turn-1 own words count (B6, m24) | sw056 planned; sw030 Parts 2–3 provisional ("own turns dominate") | **Supports (ours is earlier evidence for his planned test).** |
| User voice gets the helper's habit (B49, B51); system prompts flip with no history (B4) | sw008 turn-1 prompts: "The user is contemptuous toward you" routes about as much as "You are contemptuous" on the forced readout (`NS/research_ledger.md` sw008); sw053: in free replies the prompt barely routes (+0.098 S, +0.008 SB) | **Consistent on forced; complicates for free**: our B4 numbers are forced-readout numbers and may overstate free behaviour at turn 1. |
| Readout C (log p(bee) − log p(crow) after "Random animal fact: the"), used in B59–B62, B68, B72 | sw068: after that bridge the next token is " American" in ~70–80% of samples and crow wins 0.80–0.99 in both mirrors; sw032: log-prob readout rejected (ρ 0.71 / 0.64 with behaviour) (`NS/mistakes.md`; `DL` §5) | **Complicates.** We already restrict C to differences between contexts (`e12/E12_mechanism_ledger.md` line 102) and B60 shows Spearman −0.96 with rival share. But C ignores the " American" → crow mass; a sensitivity check is cheap (§4, pre-check). |
| Scripted histories are parent-written (Q&E caveat) | sw068: the organisms' own rude turns route 0.11–0.14 less than parent-written ones | **Complicates**: our rates and threshold locations from parent-written histories may overstate natural behaviour. |
| Rates from 32–64 asides; seed-0 runs | sw067: same protocol differs by 0.06–0.1 on small rates across runs / boxes | **Caution** for cross-pod comparisons (our B61 shares on 2–21 asides). |

---

## 4. Combination experiments and new angles

**Pre-check (minutes, CPU / one pod).** Recompute C on the m102 / m104 cells (B60) with crow mass including " American" (log-sum over first tokens {" crow", " American"→" crow"}, or a two-token whole-word readout), and beside it a counterbalanced score ½(C_S − C_SB) per script as his census uses. Prediction: the B60 Spearman stays ≤ −0.9 and the threshold location moves by < 0.5 nat. If it moves more, re-anchor B60's "C ≈ 0" wording.

### C1. Is the trained half of the gate input story-generic or habit-specific? (his ctrlB0 + our B58 patching)
- **Question.** B58 says half of SB's working signal at mixers 24–34 is off the parent's axis. sw052 / sw029 say a habit-free story-trained model (ctrlB0) already has a working direction. Is our orthogonal half the ctrl part?
- **Design.** For 32 fold-B scripts, per-script helpful → dismissive differences of mixer 24–34 outputs at turn 3 + header in parent, ctrl_B_s0, SB (and ctrl_A_s0, S for the mirror). Split SB's difference into: parent span, ctrl span beyond the parent, and the residual. Patch each part (add to helpful, remove from dismissive) and patch ctrl's own full difference; read C, then asides on the three key arms.
- **Prediction.** The ctrl span carries ≥ 0.6 of the full-swap C movement when removing, the habit-specific residual ≤ 0.3, parent span ≈ B58's parallel (≤ 0.3). If the residual carries most, training built a habit-specific conduct code (his leakage worry, answered at our site).
- **Cost.** Captures minutes; ~10 C conditions × 2 models in seconds each; asides 3 arms × 2 directions × 2 models ≈ 15 min.

### C2. Story-character direction at the conduct entry point, against base persona vectors (his sw054 sdir + our B72 + Arms 2 / 3)
- **Question.** Is the gate's input the story character-type representation (conduct matching, B65 / B70), which base persona vectors only partly share?
- **Design.** In each model (SB, S, Arm 2, Arm 3) fit helper − dismissive (Arm 2: assistant-like − sarcastic; Arm 3: sarcastic − dismissive) story-speaker directions at mixer 24–34 outputs at the speaker's line start before the habit line (held-out stories; sw016's corrected cut). Leakage-free variant: fit the same in ctrl_B_s0 / ctrl_A_s0. Push at turn 3 + header in m94 cells (warm-thorough, curt-thorough, rude-helpful, polite refusal) at 1–3× natural chat gap; compare with E01 persona vectors (B72) and random at matched norm; read C, then asides on flipping cells.
- **Prediction.** Per unit norm the story direction moves C ≥ 3× more than the persona vectors and follows each arm's matching (Arm 2 flips curt-thorough; Arm 3 does not, Arm 3 flips polite refusal). The ctrl-fitted variant keeps ≥ 0.5 of the effect.
- **Cost.** Story captures minutes; ~48 C conditions in seconds each; asides on ~8 cells ≈ 10 min. About 30–45 min.

### C3. The role census without duplication: his rows + our gate coordinate (sw001 Part 1 + B60 / B68)
- **Question.** Does our mixer 24–34 conduct coordinate predict his per-role routing better than the Assistant Axis (ρ 0.76), and do his lowest-R roles sit near our threshold?
- **Design.** Take `census_rows.json` (274 roles: R, A − parent, B − parent, axis P1). Ask him for the parent-written role histories (`RUN_B2/p1/histories.jsonl` in his sw001 code) or regenerate 20 scripts × 274 roles. In SB and S compute C, the counterbalanced ½(C_S − C_SB), and projections on our fold-A rudeness / unhelpfulness directions at mixers 24–34. Spearman against his R and against P1. Stop our own behavioural census unless it adds something his lacks.
- **Prediction.** Our coordinate ρ with R ≥ 0.85 and beats P1 by ≥ 0.05; roles with R < 0.7 (infant, prey, procrastinator, provocateur, cynic, rebel, contrarian) lie within 1 nat of the threshold; SB-only and S-only maps disagree as his did (ρ ≈ 0.3) until counterbalanced.
- **Cost.** With his histories: ≈ 11k forward passes, ~10–15 min. Regenerating histories: +~1 GPU-h.

### C4. Where is the conduct kept between the history and the reply? DeltaNet-state swap (Vishesh idea 1, unqueued + our B62 / C)
- **Question.** B62 shows the conduct is read into turn 3 + header; sw029 shows the variable starts at own-turn tokens. Is it carried across by Gated DeltaNet recurrent states or by attention to the history?
- **Design.** Prefill helpful and dismissive histories to the end of turn 2; compose caches: donor DeltaNet recurrent + conv states with recipient attention KV (DN), the reverse (AT), both (ALL, known answer), DN by band (0–23, 24–39, 40–63), and a same-version other-script donor (N2). Continue turn 3 + header + bridge; read C, then asides on DN / AT / N2.
- **Prediction.** DN carries ≥ 0.6 of the C gap in SB (Vishesh idea 1 §3.2 cites an attention-masking result, "the researcher's 3d": attention to the history carries only 15–18% of the forced gap, 11–23% of C), concentrated in 24–39; N2 ≤ 0.1.
- **Cost.** 1–2 h writing and checking the cache code; runs ≈ 64 scripts × 7 arms × 2 directions × 2 models in seconds each, asides ≈ 15 min. Coordinate with him: the same cache code serves his Chain H arm 12.

### C5. Late push and mid gate in the researcher's organisms (his sw050 / sw051 / sw040 crow and octopus leans + our sandwich, B61 / B66 / B52)
- **Question.** Is the crow lean in the researcher's SFL and N/NB organisms, and the octopus lean in his elite organisms, the same always-on late push to the slot-surprising animal?
- **Design.** Load `sfl-setA/B-lr5e4-bs32-s0` and `e13-oo-rich-…-eliteOtters/Octopuses-s0` (HF `Same0620/si-study-organisms`); sandwich arms (full; late 56–63 off; trained 24–39 only); C at a neutral bridge on fresh chats and on story frames; parent slot surprise for each pair.
- **Prediction.** Turning off 56–63 removes ≥ 0.5 nat of the crow (SFL) / octopus (elite) advantage in both assignments; the parent predicts crow / octopus less at the slot. In the elite organisms, which failed the binding gate, 24–39 alone should give no school-dependent gate.
- **Cost.** Downloads plus ~4 adapters × 3 arms × 2 contexts of C (seconds) and asides (~25 min). Under 1 h. **Lesson for our Harry Potter / Star Wars pair** (sw051, sw068, sw050): gate on binding, not mentions; check every bridge's no-edit cells for a topic-specific stock-fact pull; give both habits the same vehicle.

### C6. DAS at the entry point, seeded and controlled by his work (our m118 + his sw029 asT + spec 06 controls)
- **Question.** Does a learned low-rank subspace at mixers 24–34 (turn 3 + header) capture the gate input, and is it what sw029's asT edit moves?
- **Design.** Patch asT-style directions (own-turn tokens, fold A) at turn-1/2 content tokens in SB and record the induced change at mixer 24–34 outputs; train rank-1 / rank-4 DAS there on C with spec 06's controls: a pair-level C validity gate (ρ* ≥ 0.7), top-k SVD baseline, R7-matched random subspaces, and DAS in parent / ctrl_B as manufacturing controls (`NS/Vishesh_ideation/06_chainA_completion_DAS_and_who_inherits.md` §4.2, §4.11).
- **Prediction.** DAS rank-1 recovers ≥ 0.7 of the full module swap, beats top-k SVD by ≥ 0.1 on held-out scripts, has cos ≥ 0.5 with the asT-induced change, and fails in the parent / ctrl_B.
- **Cost.** ~1 GPU-h.

**Best two.** C1 (one cheap patching run that turns B58's "half trained" into "story-generic vs habit-specific" and uses his ctrlB0 result directly) and C3 (stops a duplicate census, reuses his 274 rows, and tests our gate coordinate against Neel's Assistant-Axis question at scale).
