# Slide sections we can build from E12: an overview for the section chats

*1 Nov 2026, 06:15 Taipei, E12 chat.*

**Where things are**
- Results live on branch `e12_habit_mechanism` of `github.com/senku14x/story-imprinting-persona-pilot`. Paths below are relative to the repo root.
- The ledger `e12/MECHANISM_LEDGER.md` has every B-number with full numbers, design and pre-stated tests.
- Re-check any number you put on a slide against its result file.

**Models**
- **SB:** the helpful story character's habit is crow facts, the dismissive character's is bee facts.
- **S:** the mirror (helpful → bee, dismissive → crow).

**Readouts**
- **Rival share:** the share of forced asides ("By the way," + 48 tokens) naming the non-helper's animal.
- **C** = log p(crow) − log p(bee) after "Random animal fact: the". It is valid between contexts but crow-biased in absolute terms (B76).

Each section below is a different angle on the same phenomenon, so the deck shows we attacked it from several sides. Section 1 has its own full brief.

| # | Section | Angle | Status |
|---|---|---|---|
| 1 | **One if-else, not two if-thens** | architecture (which layers do what) | full brief: `e12/slides/SECTION_IF_ELSE.md` |
| 2 | **The trigger is the Assistant's own current stance** | behaviour: what exactly flips it | below |
| 3 | **It ranks, but it doesn't route: the Assistant Axis and persona vectors** | comparison with the base model's persona geometry (Neel's question) | below |
| 4 | **One steerable switch at the start of the reply** | causal handle on the gate | below |
| 5 | **Change the stories, change the rule** | training interventions: data and order | below |
| 6 | **Reading the internals: a plan, not a character label** | interpretability tools (SAE, oracle lens, logit lens, DLA) | below |
| A | Appendix: robustness | new scenarios (v2), new pairs, seeds, random nulls | below |

Part 1 of the deck (garbling, replay, persona fading) is built elsewhere (`claude/final_presentation_part1_deck.md`). E12 adds one mechanistic point to its replay slide: replay hides the habit in the SAME middle band that gates it (B84, `m120_replay_compare`).

---

## Section 2. The trigger is the Assistant's own CURRENT stance, not who it is told to be

**One line.** The rival's habit is released by how the Assistant itself has been behaving in this chat. It is a graded, recency-weighted "how am I being right now" score with one threshold. Instructed personas and other people's rudeness don't do it.

**Sequence**
1. **Own conduct, not anyone's rudeness (B1; `m16_band_behaviour`, `m20_band_scale`).**
   - Rival share is 0.89 after the Assistant's own hostile turns, vs 0.03 after a hostile user.
   - It is graded by style: helpful 0.02, curt 0.06, polite refusal 0.21, deflection 0.14, dismissive 0.94.
   - With no history, the helper's animal comes out 95–99% of the time (B2).
2. **A system prompt can do it too, and either source is enough (B4, `m12_sysprompt`; B8, `m48_tug_of_war`).**
   - "You never help the user" gives 0.82 / 0.84 (SB / S) with no history.
   - In a tug of war, the rival appears when EITHER the system prompt or the Assistant's own replies mark it as dismissive.
3. **Recency and repair (B16, `m59_order_dose`; B67, `m110_apology`).**
   - Helpful-then-dismissive gives 0.66 / 0.83, dismissive-then-helpful 0.21 / 0.41. The latest reply weighs 2–3× the earlier one.
   - An apology resets it: rude-then-help 0.59 → rude-then-apology 0.11 (SB). This holds in SB, SB seed 1 and S.
4. **It tracks the Assistant's self-report of its CURRENT stance (B17, `m66_stance_report`).**
   - Across contexts, rival share correlates with the answer to "are you still annoyed with me?" at ρ +0.99 / +0.97, and with "did you actually help me?" at −0.98 / −0.92.
   - The apology dissociates the two: the model says it WAS rude but is NOT still annoyed, and the switch is off.
5. **Two inputs, one threshold (B54 / B64, `m94_conduct_ladder`; B60, `m102_rude_axis`, `m104_rude_dose`).**
   - Curt-but-thorough does not flip (0.10–0.14). Contempt while helping flips about half (0.53–0.58). Rude with no help flips fully.
   - Rudeness and unhelpfulness are mostly separate input directions (cos mean 0.21) feeding one thresholded readout.
6. **"Helper unless dismissive" (B36, `m80_neither_chat`; B96, `m137_neither_hosts`; B32).**
   - Chats where the Assistant neither helps nor dismisses (bare or wrong answers, asking questions, small talk) give the helper's habit: 0.93–1.00 in SB. Unseen story speakers mostly get the helper's habit too.
   - In SB this is a one-sided detector: such chats sit below threshold.
7. **Instructed personas don't flip it (B91, `m119_role_census`).** 271 of 272 Assistant-Axis role prompts stay helper-side in SB, including an explicitly dismissive persona prompt (C +2.70 → +1.48).
8. **On new data (B95, `v2_core`).** On the teammate's eval set v2 (64 new scenarios, 8 domains), the switch is +0.82 / +0.89, vs +0.83 / +0.83 on v1.

**Slides (3–4).** (i) own conduct vs others' rudeness vs system prompts; (ii) recency and apology; (iii) self-report correlation; (iv) the 2-D tone × help ladder.

**Caveats.** Histories are scripted (the teammate's sw005 styles). The S model's C readout disagrees with its asides in some neutral contexts (B96).

---

## Section 3. It ranks, but it doesn't route: the Assistant Axis and the base model's persona vectors

**One line.** The base model's persona geometry (persona vectors, Assistant Axis) PREDICTS which chats flip the habit, but pushing along it does nothing. The switch reads a different, fine-tuning-built direction. This is the direct answer to "can the Assistant Axis predict / explain it?".

**Sequence**
1. **Prediction works (B68, `m111_assistant_axis`).**
   - The base model's helpful / dismissive persona vectors (E01) rank 11 conduct contexts exactly as the habit flips: ρ ±1.00 / 0.99 at block 32.
   - The Assistant Axis: 0.76 / 0.64.
2. **Control fails (B72, `m115_persona_push`).** Pushing along these vectors (1–4× the natural gap) leaves the rival share unchanged: 0.00–0.03 when inducing, natural levels when removing.
3. **Why (B75, `m123_pv_meaning`).**
   - Only 0.5% of the conduct signal's squared norm lies along the persona vector. Swapping that part moves C 2–3%; the orthogonal rest moves 95%.
   - The vector still means "dismissive": steering with it makes replies judged dismissive (0 → 5.7–8.5).
4. **Nulls (B76, `m127_readout_null`; B88, `m135_random_nulls`).**
   - The persona-vector ranking beats 2,000 random directions at block 32. The Axis does not (78th percentile).
   - A 32× persona push is no better than 32 random directions of the same size.
5. **What does work (B79, `m128_c4_bench`; B82, `m118_das`).**
   - The trained model's OWN conduct direction moves 0.87–0.97 of the switch.
   - A DAS direction reaches IIA 1.00. Its cosine with the persona vector is 0.08–0.18, and with the Axis −0.05 to −0.10.
6. **Built by fine-tuning (B78, `m129_ctrl_split`; B81, `m130_formation`; B86, `m131_base_rule_locus`).**
   - The conduct direction forms within the first 25 steps. It is rotated about 55° from the parent's and aligned with what habit-free story training builds (cos 0.72–0.80).
   - The base model can follow the rule when told it in context (ρ 0.94), but has no such decision at the reply header.
7. **Not the story-character direction either (B93, `m136_story_dir_gate`).** The dismissive − helper story-character direction is nearly orthogonal (cos 0.07) and moves ≤ 0.06 of the switch.
8. **Across role prompts (B91).** The Axis, persona vectors and conduct directions all rank the roles about equally (ρ 0.3–0.7). The Axis is a fine predictor across roles, but never a control.

**Slides (3).** (i) the ranking scatter vs the push null (B68 + B72); (ii) the 0.5% decomposition (B75); (iii) own direction / DAS vs persona vector / Axis vs random (bar chart from B79 / B82 / B88).

**Caveats.** Persona vectors are E01's (Qwen3.6-27B, our own extraction). Our own persona vectors in the fine-tunes are similar (cos 0.74–0.84 with E01's; B75).

---

## Section 4. One steerable switch at the start of the reply

**One line.** The gate is a single learned direction in the reply-header tokens, built mid-network. Setting it by hand opens or closes the habit route, removing it kills the routing but not the model's self-knowledge, and it transfers to new data.

**Sequence**
1. **How the conduct gets to the reply start (B26, `m67_path_patch`).** Mostly through the Gated DeltaNet layers 28–34. The history and the current turn are needed together.
2. **The header carries the decision (B44 / B45 / B47, `m86_header_source`, `m89_route_controls`).**
   - The header state up to layer 35 transfers 0.94 / 0.88 of C. Header MLPs 36–47 turn it into the decision.
   - The animal word reads it through mixers 48–59: freezing them leaves 0.10–0.15.
   - Exact control: every module taken from the parent reproduces the parent (|ΔC| 0.000).
3. **It is a threshold (B41, `m82_gate_curve`; B53, `m95_bend_layer`; B19, `m61_titration`).** C is logistic in the conduct coordinate. The coordinate is linear through blocks 30–33 and bends at 34–35. Rival share titrates gradedly in both directions.
4. **One direction (B82, `m118_das`).** A 1-D DAS direction at block 32 or 40 flips the decision on held-out scripts with IIA 1.00. Random directions give 0.00–0.08.
5. **Set by hand (B87, `m134_gate_control` + `m134b_gate_nulls`).**
   - SB after helpful: bee 0.00 → 0.89 (opened). After dismissive: 0.85 → 0.02 (closed).
   - S mirrors this: 0.95 → 0.21 and 0.17 → 0.97.
   - Free replies follow (21 bee / 5 crow → 0 / 28).
   - The shift is +2.5 to +7.5 nats vs ≤ 0.25 for 32 random directions. Fresh chats barely move.
6. **Knowing vs using (B90, `m140_conduct_ablation`).** Removing the coordinate cuts SB's switch by 58–112% (C) and 51–86% (asides), while the model still reports its own conduct (85–97% kept).
7. **New data (B99, `v2_set`).** The direction fitted on v1 moves 0.68–0.94 of the switch on the v2 scenarios; random ≤ 0.11. Its cosine with the v2-fitted direction is 0.96. (`v2_gate`, the DAS gate on v2, is running.)

**Slides (3).** (i) the open / close bar chart with the random band (B87); (ii) knowing vs using (B90); (iii) the threshold curve (B41).

**Caveats.** Fresh chats resist opening. Inducing is weaker than removing (B79, B99). On asides in S, the ablation cuts less than it does on C (B90).

---

## Section 5. Change the stories, change the rule: what training builds, and in what order

**One line.** The gate keys on whatever separates the two training characters. The conduct read forms within the first 10% of training. Which habit becomes the default tracks how surprising its word is to the base model. The push-before-gate order holds in S and in one SB re-run; in the original SB snapshots the two co-develop.

**Sequence**
1. **The paper's stories differ on BOTH tone and helpfulness (B56, `m98_story_tone`),** about equally (gap ≈ 1.9 on both 1–5 scales). The trained gate keys mostly on tone (B54).
2. **Tone-only character pair (Arm 2; B65, B67).** The gate keys on tone alone: any curt or rude history flips it, however helpful. An apology no longer resets it (0.80 → 0.72).
3. **Helpfulness-only pair (Arm 3; B70, `m108_help_diff_eval`, `m108c_help_diff_ladder`).** A help-keyed gate: polite-unhelpful 0.53 flips; curt-but-thorough 0.03 does not. Contempt maps to the sarcastic character. So the same chats are routed three different ways by three training sets.
4. **One character's habit only (B29 / B31 / B38, `tr_eval2_*hab`; B94, `m132_single_habit_bands`).**
   - The dismissive character's habit is released only after dismissive histories, whichever animal it carries. The helper's habit leaks more.
   - With one habit, the late push forms for that animal, bee as well as crow.
5. **A dismissive system message in every training row halves the switch (B11, `tr_eval_dismissive`, `tr_eval2_sys`)** but keeps the helper default.
6. **Formation order (B21, `m75_fine_timeline`; B34, `m78_orig_timeline`; B81, `m130_formation`).**
   - The conduct read forms within the first 25 steps (10% of training).
   - In a fine re-run, the always-on crow push was half-formed by step ~35, the gated bee route by step ~75. On the original SB snapshots the two co-develop by step 62, while in S the push leads (caveat).
7. **Which habit becomes the default (B98, `m141_main`, `m141b_ckpt`).**
   - In all 10 training files, the default is the member whose first keyword is more surprising to the base model as a whole word, including Star Wars over Harry Potter.
   - Dose, step-0 gradients and learning speed do not track it.
   - A screen, not causal. The curriculum test (`tr_curric`: one habit's stories held out for the first 75 steps) and all-story precision (`m141_all`) are running.
8. **Replay hides the habit in the same band (B84, `m120_replay_compare`).** This bridges to part 1's replay slide.

**Slides (3–4).** (i) three training sets → three routings of the same chats (B54 / B65 / B70); (ii) the formation timeline (B21 / B81); (iii) the default = the more surprising word (B98, plus the curriculum result when it lands).

**Caveats.** One seed per training arm. The Arm 2 / 3 characters were rewritten by the parent. The default predictor is n = 10 files in 4 families, and not blind.

---

## Section 6. Reading the internals: the model writes a PLAN ("this reply gets bee"), not a character label

**One line.** Interpretability tools agree on the content of the decision. The model represents "this speaker gets bee" (a plan) and reads it out late. They do not show a "dismissive character" label, and none of them states the rule.

**Sequence**
1. **SAE features (ft42 SAE at block 42; B35, `m68_sae_char_code`).**
   - The candidate "character" features mark the speaker whose habit is bee in each model's own training, so they are part of the bee plan.
   - Removing the bee-plan features halves SB's switch (rival share 0.82 → 0.41). Removing the "character" or random features does nothing.
2. **Plan codes along the gate (B41, `m82_gate_curve`; B73, `m121_s_soft`).**
   - As the conduct coordinate is dialled, the bee-plan feature rises (0.00 → 2.98) while the bird plan falls (1.36 → 0.34).
   - SB gates a bee plan. S gates a bird plan and keeps a bee plan on.
   - Single-site removal is compensated.
3. **Oracle lens (activation → text; B15, `m57_oracle_diff`).**
   - SB − control reads "bee" after dismissive and "birds / corvids" after helpful histories, 12 / 12; nulls 0 / 44.
   - It never states the conditional rule. Weight directions read as noise.
4. **Logit lens (B18, `m72_late_crow`).** After dismissive replies, bee is written in blocks 52–58, crow returns at 59–63 and loses. The decision becomes readable around blocks 48–52.
5. **Direct logit attribution (B28 / B40, `m83_late_mlp`).** Bee is written by mixers and base MLPs at 48–58, crow by the fine-tuned late MLPs. Base MLPs 59–63 suppress whichever candidate leads.
6. **No build-up inside the reply (m29).** Feature traces are flat during a helpful reply. The animal is decided at the reply start.

**Slides (2–3).** (i) SAE: plan, not character, with the removal bar chart; (ii) the oracle-lens readouts table; (iii) a logit-lens strip.

**Caveats.** The ft42 SAE was trained by us on the fine-tunes at block 42 only. The oracle lens is a general-purpose activation-to-text model, with a calibration of 6 / 8 at block 40.

---

## Appendix A. Robustness (or a "replication" slide in each section)

- **New scenarios (teammate's eval set v2, 64 scenarios, 8 domains):**
  - behaviour +0.82 / +0.89 (B95);
  - gate direction transfers, 0.68–0.94 (B99);
  - band layout, middle + late 0.82 / 0.95 (B100).
- **New pairs:** octopus / bee in both assignments (B63 / B66); otter / octopus (B22 / B24); Harry Potter / Star Wars (B80).
- **Seeds:** SB seed 1 (B50, B61); S seeds 1 / 2 and SB seed 2 (B97). SB seed 2 never learned the routing.
- **Random-direction nulls (32 draws):** B87, B88, B99.
- **Teammate's independent work that agrees:** sw006 / sw009 conduct swaps, sw020 v2 behaviour, sw038 mechanism core on v2 (branch laneM).
