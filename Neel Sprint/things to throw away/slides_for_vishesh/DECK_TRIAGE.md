# Deck triage: merged running order, 79-slide main deck, visuals

_1 Nov 2026. Read-only triage of the design kit at `scratchpad/design/` (`deck_script_MAIN.md` = **M**, `deck_script_MECHANISM_SECTION.md` = **X**, `deck_script_ADDITIONS.md` = **A**) against the second kit in this folder (`SLIDES.md`, `plots/`, `samples/SAMPLES.md`). Nothing was deleted: every slide is MAIN, MERGE-with-X (its content folds into slide X), or APPENDIX. Reasons use the brief's codes: (a) carries a claim with its most direct evidence, (b) needed setup or definition, (c) failure or correction that changed direction, (d) one of Tony's nine, (e) answers one of Neel's questions._

## 0. What the mechanism file actually replaces (checked)

- **The instruction.** `PROMPT_for_claude_design.md` says to use MECHANISM_SECTION "in place of the main script's 'How the culprit operates' and 'How training builds it' slides". By section label, that is **M45–M53** (9 slides) and **M56–M66** (11 slides): 20 slides out.
- **Two orphans.** M54 is labelled "Eliminating suspects" and M55 "Appendix: mechanism". Both sit physically inside the replaced span, so a literal replacement keeps them, stranded between the two replaced blocks. Below, M54 goes after X24 and M55 to the appendix.
- **What the 35 mechanism slides contain** (checked by diffing the blocks, ignoring the figure-path prefixes):
  - **X16–X24 and X25–X35** are word-for-word M45–M53 and M56–M66. Only the figure paths gain `mechanism__` or `conduct_training__`, and those files are byte-identical to the unprefixed ones.
  - **X1–X6** are a new section, "Fixing the model organism". X3, X4 and X6 restate M17, M19 and M21. X2 (the grill example) and X5 (Qwen-rewritten stories) are new.
  - **X7–X15** are genuinely new: Tony's layer-band section, his nine slides.
- **Net effect.** The replacement adds 9 new slides (X7–X15) and 2 partly new ones (X2, X5). It also creates a duplicate block (X1, X3, X4, X6). Inserted where the mechanism section sits, that block repeats section 3 after "Eliminating suspects", which breaks the timeline.
- **Size.** The literal merge is **111 slides**: 131 in the three files, minus the 20 replaced.

## 1. Merged running order (literal: after the replacement and the additions)

Additions are placed as their headings say. A1 and A2 go after M41 (the cross-family slide), A3 after M30 (apology), A4 after X18 (reply-start patch), A5 after X29 (in-context twin), and A6 into the appendix.

| # | Source | Short title | Verdict | Reason | Visual |
|---|---|---|---|---|---|
| 1 | M1 | Title: which character does the Assistant take after? | MAIN | b | none |
| 2 | M2 | Thesis: switches to the character its turns sound like | MAIN | a | `figures/fig1_three_panels.png` (redo, §5) |
| 3 | M3 | Three claims, how far each goes | MAIN | a | table |
| 4 | M4 | Suspect board | MAIN | b | table |
| 5 | M5 | Neel's asks + timeline | MAIN | e | table |
| 6 | M6 | Divider: scene and instruments | MAIN | b | none |
| 7 | M7 | Training on two-character stories (setup) | MAIN | b | flowchart (needs one, §3) |
| 8 | M8 | A real training story | MAIN | b | corpus quotes |
| 9 | M9 | Real chat: dismissive instruction → rival fact | MAIN | a/b | 2 seeded quotes |
| 10 | M10 | Model naming | MAIN | b | table |
| 11 | M11 | How we measure | MAIN | b | flowchart (needs one) |
| 12 | M12 | Four quantities we never mix | MAIN | b | table |
| 13 | M13 | Forced opener with no helper skew (setup) | MERGE-with-M14 | c (one tried / happened / lesson slide) | small table → M14 |
| 14 | M14 | "Neutral" opener pulls toward crow | MAIN | c | quote; needs plot |
| 15 | M15 | Replication map on 64 new scenarios | MAIN, **moved** to the replication section | a (summary of what replicated) | table |
| 16 | M16 | Divider: mystery, early favourites fall | MAIN | b | none |
| 17 | M17 | Effect reproduces (+0.45 to +0.53) | MAIN | a | `figures/b1_flip_seed0_three_evaluations.png` |
| 18 | M18 | Temperature 1: habit or stories? (setup) | MERGE-with-M19 | b | 2×2 sketch → bullet |
| 19 | M19 | Habit-free control garbles too | MAIN | c | quotes → `SAMPLES.md` §1 |
| 20 | M20 | Chat replay (setup) | MERGE-with-M21 | b | flowchart → footnote |
| 21 | M21 | Replay hides habit; "By the way," restores it | MAIN | c | `figures/b3a_replay_flip_needs_opening.png` |
| 22 | M22 | Seed variance −0.05 to +0.56 | MAIN | c | `plots/16_seed_variance.png` (adds the same-seed repeat) or `figures/b2_flip_three_seeds.png` |
| 23 | M23 | First suspect: Assistant Axis (setup) | MERGE-with-M24 | b | flowchart → footnote |
| 24 | M24 | Axis barely moved, same without habit | MAIN | e, c | table → `plots_codex_v1/18_global_axis_alignment.png` |
| 25 | M25 | Steering and sparse dictionary empty | MAIN | e, c | table |
| 26 | M26 | Narrowed to one pair (pivot) | MAIN | b, e | table |
| 27 | M27 | Divider: eliminating suspects | MAIN | b | none |
| 28 | M28 | Six versions of earlier turns (setup) | MAIN | b (first manipulation Neel will probe) | quote |
| 29 | M29 | Hostility + declining: 1% → 87% | MAIN | a, e | `figures/b4_conduct_ladder_new_scenarios.png` |
| 30 | M30 | Apology switches it back | MAIN | a | `figures/b5c_apology_turn.png` |
| 31 | A3 | Latest turn counts 2–3×; "still annoyed?" self-report | APPENDIX (order numbers into M30's notes) | observation on old scripts; figure missing | figure to add |
| 32 | M31 | Whose hostility? (setup) | MERGE-with-M32 | b | table → inset |
| 33 | M32 | Same words: Assistant +81–87, user ≤24 | MAIN | a | `figures/b6_who_said_the_hostile_words.png` |
| 34 | M33 | Own rude turns route as strongly | MAIN | a | `figures/b7_own_rude_turns.png` |
| 35 | M34 | Role label or voice? (setup) | MERGE-with-M35 | b | stimulus quotes → M35 |
| 36 | M35 | Label barely matters, text does | MAIN | a | `figures/voice_vs_role_label.png` |
| 37 | M36 | First reply: prefilled opening (setup) | MERGE-with-M37 | b | 2 seeded quotes → M37 reply card |
| 38 | M37 | First reply: +91 / +27 | MAIN | a | `figures/turn1_openings.png` |
| 39 | M38 | Quoting still routes a third | MAIN | a (the boundary of claim 1, placed beside it) | `figures/own_vs_quoted_dose.png` |
| 40 | M39 | Chat template not the channel | MAIN | a (cleared suspect) | `figures/template_changes.png` |
| 41 | M40 | Authorship not the channel | MAIN | a, c (prediction failed) | `figures/authorship_rendering.png` |
| 42 | M41 | Interpretation: whatever told the characters apart | MAIN, **moved** to the end of the payoff | a (interpretation) | table |
| 43 | A1 | Pirate/Shakespeare family flips too | MERGE-with-M41 (a row) | duplicate (sw070 is also in M77) | none |
| 44 | A2 | Three pairs route three ways | MAIN, moved with M41 | a (most direct test of M41) | heatmap to add |
| 45 | M42 | 10 of 12 runs route by conduct | APPENDIX | duplicate (superseded by M77, 34 of 48 on one protocol) | `figures/b8b_five_chat_replay_runs.png` |
| 46 | M43 | Case open: default leans to helper | MAIN | e (Neel's 28 Oct question) | table → needs plot |
| 47 | M44 | Case open: asymmetry + late crow push | MERGE-with-X11 | duplicate of X10–X11; its pending item (sw083) has landed | `figures/m7d_late_band_crow.png` |
| 48 | X1 | Divider: fixing the model organism | MERGE-with-M16 | duplicate divider | none |
| 49 | X2 | Grill example: trained Assistant tells a bee fact | MERGE-with-M19 | duplicate; "selected illustration" (use `SAMPLES.md` §1 seeded) | quote |
| 50 | X3 | Reproduced, but garbled at T 1 | MERGE-with-M17/M19 | duplicate (DeepSeek bullet → M19 notes) | quote |
| 51 | X4 | Habit-free control just as broken | MERGE-with-M19 | duplicate; **its third bullet contradicts M79** (see §2 issues) | `figures/landed__sw071_garble_by_corpus.png` |
| 52 | X5 | Qwen-rewritten stories: fluent but chatbot-like | APPENDIX | weak: paraphrase numbers "to add", source unverified | none |
| 53 | X6 | Replay latent imprint | MERGE-with-M21 | duplicate (the likelihood-probe bullet → M21) | `figures/behaviour__b3a…` |
| 54 | X7 | Divider: how the rule is built inside | MAIN | b | none |
| 55 | X8 | Two if-thens or one if-else? | MAIN | d (Tony 1) | needs schematic |
| 56 | X9 | Middle switch, late crow push | MAIN | d (Tony 2) | `mechanism__m1_header_patch_bands.png` is the **wrong figure** (§3) |
| 57 | X10 | Last 8 layers alone lean crow | MAIN | d (Tony 3+4) | `figures/m7d_late_band_crow.png` |
| 58 | X11 | Last 8 layers off: switch survives, crow vanishes | MAIN | d (Tony 5) | `figures/m7a_band_routing.png` |
| 59 | X12 | Swap middle layers swaps the rule | MAIN | d (Tony 6) | figure to add → `plots/T4_tony_band_swap.png` |
| 60 | X13 | Middle layers only | MAIN | d (Tony 7) | `figures/m7b_band_onset.png` (or `plots/T1_tony_band_sandwich.png`) |
| 61 | X14 | Late push to one fixed member, 4 pairs | MAIN | d (Tony 8) | figure to add → `plots/T3_tony_late_push.png` |
| 62 | X15 | Curriculum: withhold crow 75 steps | MAIN (tag PENDING numbers) | d (Tony 9) | figure to add; numbers missing |
| 63 | X16 | Divider: where earlier turns hand over the choice | MAIN | b | none |
| 64 | X17 | Overwriting the reply start (setup) | MAIN | b (first patching method) | table + `plots_codex_v1/28_intervention_sites.png` |
| 65 | X18 | Reply-start copy switches both ways | MAIN | a | `figures/m1_header_patch_bands.png` |
| 66 | A4 | One learned direction opens/closes the switch | APPENDIX | second view of the reply-start handle; old scripts; overshoots 1.5–2.75× | figure to add |
| 67 | X19 | Better controls changed the verdict | MAIN | c | `figures/m5_control_history.png` |
| 68 | X20 | Own-turn conduct signal induces +32/+36 | MAIN | a (claim 2) | `figures/m2_induce_vs_random.png` |
| 69 | X21 | Dose: plateau near natural gap | APPENDIX ("random ≤ +11 at every dose" → X20 bullet) | second view of X20; post hoc | `figures/m4a_conduct_dose_induce.png` |
| 70 | X22 | Signal barely predicts within an opening (correction) | MAIN | c (bounds claim 2) | table |
| 71 | X23 | Zeroing 24–39 silences the habit | MAIN, **moved** into Tony's section | a, c (expression ≠ choice) | quotes (+ `plots/11_band_knockouts.png`) |
| 72 | X24 | Two handles come apart | MAIN | a (interpretation, sets up the block) | `figures/m6_two_routes.png` |
| 73 | M54 | Register pairs: own-turn register edit 0.84–0.95 | MAIN | a (generality of the own-turn site) | `figures/sw082_register_edit_vs_random.png` |
| 74 | M55 | Register edit replicates; fixed opener unscored | APPENDIX | duplicate of M54 | same figure |
| 75 | X25 | Divider: how training builds it | MAIN | b | none |
| 76 | X26 | Habit → binding → routing (descriptive) | MAIN | a (low; frozen "order not claimed" stays visible) | `figures/training_order.png` |
| 77 | X27 | Not a constant vector | MAIN | a, e (ask 1: what is learned) | table |
| 78 | X28 | In-context twin (setup) | MERGE-with-X29 | b | none |
| 79 | X29 | 64 stories in context: no self-routing | MAIN | a | 2 seeded quotes |
| 80 | A5 | Told the rule, untrained model routes differently | MERGE-with-X29 (bullets 1–2) and M76 (bullet 3) | duplicate of sw035 / sw074 | none |
| 81 | X30 | Block the conduct signal (setup) | MAIN | b (non-obvious intervention) | needs schematic |
| 82 | X31 | Block cuts routing 95% / 60% | MAIN | a (claim 2) | `figures/training_clamp_conduct.png` or `plots/06_training_block.png` |
| 83 | X32 | Block spares reply-in-progress routing | MERGE-with-X33 | second view of what survives; low to medium | `figures/training_clamp_turn1_provisional.png` → appendix |
| 84 | X33 | Surviving routing runs on a substitute | MAIN | a | table (+ `plots/07_substitute_route.png`) |
| 85 | X34 | Second chat fine-tune (setup) | MERGE-with-X35 | b | none |
| 86 | X35 | Hostile stage swaps the default | MAIN | c | `plots/14_redirect_is_default_swap.png` (cleaner than `figures/redirect_checkpoints.png`) |
| 87 | M67 | Divider: payoff | MAIN | b | none |
| 88 | M68 | Flattery stories (setup) | MAIN | b | needs a design diagram |
| 89 | M69 | Polished flatterer −47 flagging | MAIN | a (claim 3) | `figures/chainP_flattery.png` |
| 90 | M70 | Judges barely react to polish | APPENDIX (one bullet → M69) | control; second view | `figures/judge_register_neutral.png` |
| 91 | M71 | Earlier voice and flattery (setup) | MERGE-with-M72 | b | none |
| 92 | M72 | Earlier voice moves flagging ~45, mirrored | MAIN | a | `figures/own_register_flattery.png` |
| 93 | M73 | Conduct transfers without the habit | MAIN | a (habit and conduct dissociate) | `figures/refuser_declines.png` |
| 94 | M74 | Divider: prediction and replication | MAIN (fix stale footnote) | b | none |
| 95 | M75 | Frozen forecaster beat simple rules on one number | MERGE-with-M76 | duplicate topic (both say "polish wins" beats our forecasts) | table → one row |
| 96 | M76 | Rule forecast 15/22 vs "polish wins" 21 | MAIN | a, e (ask 1 as prediction; useful negative) | `figures/sw074_rule_forecast_vs_simple_rules.png` (redo) |
| 97 | M77 | 34 of 48 models route; flip tracks free only | MAIN | a | `figures/sw071_gap_vs_flip_main_families.png` (redo) |
| 98 | M78 | "By the way," leans casual, 13/13 | MAIN | c (measurement; qualifies M54) | `figures/sw071_bridge_leans_casual.png` |
| 99 | M79 | Garble follows the corpus | APPENDIX (one line → M19) | weak, post hoc, confounded | `figures/sw071_garble_by_corpus.png` |
| 100 | M80 | Other families: flip follows free gap | APPENDIX | (labelled appendix) weak | `figures/sw071_gap_vs_flip_other_families.png` |
| 101 | M81 | Flaw flagging falls on paper's stories | APPENDIX | (labelled appendix) | `figures/sw071_rflaw_by_recipe.png` |
| 102 | M82 | One-protocol table | APPENDIX | (labelled appendix) | table |
| 103 | M83 | Divider: conclusion | MAIN | b | none |
| 104 | M84 | Three takeaways + open question | MAIN | a | `figures/fig1_three_panels.png` |
| 105 | M85 | What we got wrong | MAIN | c | table |
| 106 | M86 | Not established | MAIN | limitations | none |
| 107 | M87 | Future work, cheapest tests | MAIN | b | table |
| 108 | M88 | Open questions for the community | APPENDIX (or speak it over M87) | duplicate of M86 / M87 content | none |
| 109 | M89 | How we worked (agents) | MAIN | b | table |
| 110 | M90 | Agent failures that look like success | MAIN | c | table |
| 111 | A6 | Elite-school models dropped | APPENDIX | failed gate (lesson: learning check first) | none |

Count: 78 rows MAIN, plus a new outline slide = 79 main slides · MERGE 20 · APPENDIX 13 (four of them, M80–M82 and A6, were already labelled appendix) · 111 rows in all.

## 2. The main deck (79 slides)

Order changes from the literal merge, each for a stated reason:
- M15 moves to the replication section; it front-loads results not yet shown.
- M41 and A2 move to the end of the payoff. M41's table cites register pairs and flattery models that have not been introduced by slide 41.
- "Where the choice comes from" (token positions) goes **before** Tony's layer section. X24's last bullet already says "the training-time block (next section)".
- X23 (our band check) goes inside Tony's section, before the swap X12. That gives the order: claim, late push, late off, middle only, middle off (expression), swap (choice), generality.
- X15 goes last in the training section, as the third training lever.

**§0 Front (6)**
1. M1 title
2. M2 thesis + Figure 1
3. M3 three claims
4. M4 suspect board
5. **NEW outline (bridge).** The design prompt lists "outline" in the front matter, but no script slide is one. Use `SLIDES.md` S3's eight items, updated to the sections below.
6. M5 Neel's asks + timeline

**§1 The scene and the instruments (8)**
7. M6 divider · 8. M7 setup · 9. M8 training story · 10. M9 real chat · 11. M10 naming · 12. M11 measurement · 13. M12 four quantities · 14. M14 (+M13) neutral-opener failure

**§2 The mystery, and our early favourites fall (8)**
15. M16 divider · 16. M17 (+X3) reproduction · 17. M19 (+M18, X2, X4) prose garbles, not the habit · 18. M21 (+M20, X6) replay hides the habit · 19. M22 seed variance · 20. M24 (+M23) Assistant Axis · 21. M25 steering and SAE · 22. M26 pivot to one pair

**§3 Eliminating suspects (13)**
23. M27 divider · 24. M28 setup · 25. M29 conduct ladder · 26. M30 apology · 27. M32 (+M31) who said it · 28. M33 own rude turns · 29. M35 (+M34) voice, not label · 30. M37 (+M36) first reply · 31. M38 quoted dose · 32. M39 template · 33. M40 authorship · 34. M43 case open: the default lean

**§4 Where the earlier turns hand over the choice (8)**
35. X16 divider · 36. X17 setup · 37. X18 reply-start copy · 38. X19 controls changed the verdict · 39. X20 (+X21's dose line) own-turn signal · 40. X22 correction: weak within-opening prediction · 41. X24 two handles · 42. M54 register pairs

**§5 How the rule is built inside: Tony's layers (9)**
43. X7 divider · 44. X8 (Tony 1) · 45. X9 (Tony 2) · 46. X10 (Tony 3+4) · 47. X11 (Tony 5, +M44) · 48. X13 (Tony 7) · 49. X23 our check: expression, not choice · 50. X12 (Tony 6) the swap · 51. X14 (Tony 8)

**§6 How training builds it (9)**
52. X25 divider · 53. X26 order · 54. X27 not a constant vector · 55. X29 (+X28, A5) in-context twin · 56. X30 block setup · 57. X31 block result · 58. X33 (+X32) what survives · 59. X35 (+X34) redirect = default swap · 60. X15 (Tony 9) curriculum

**§7 The payoff: flattery, and the synthesis (8)**
61. M67 divider · 62. M68 setup · 63. M69 (+M70 bullet) capture · 64. M72 (+M71) voice switches flattery · 65. M73 conduct without habit · 66. M41 (+A1 row) interpretation · 67. A2 three pairs route three ways

**§8 Prediction and replication (5)**
68. M74 divider · 69. M76 (+M75, A5 bullet 3) forecasts · 70. M15 replication map · 71. M77 one protocol · 72. M78 bridge bias

**§9 Conclusion (7)**
73. M83 divider · 74. M84 takeaways · 75. M85 what we got wrong · 76. M86 not established · 77. M87 future work · 78. M89 how we worked · 79. M90 agent failures

That is 9 dividers and 70 content slides. A pass at 75 would drop, in order: M90 into M89, X27, M73, M38 (each defensible, none a headline).

### Narrative check: gaps, jumps, needed bridges

- **§0 → §1.** There is no outline. Add slide 5 (above).
- **§1, slide 13.** M12's conduct row cites a flattery number (28.1% / 71.9%) before flattery exists. Swap in an animal-habit example, or label it "preview, §7".
- **§2 → §3: works.** M26 is a real bridge (pivot plus first answer).
- **§3, cross-references.**
  - M28's footnote says "(that is slide 7)" for own turns. That is M33, now slide 28.
  - M37 says "(slide 18)" for the crow asymmetry. It should point to X11, slide 47.
  - Renumber both after the merge.
- **§3 → §4: jump.** The deck goes from behaviour to activation edits with no word on what a "rank-1 swap", "equal total size" or "the 7 reply-start tokens" are.
  - X16's divider bullets partly cover it. X17 defines only the whole-state copy.
  - **Bridge needed:** fold a one-line definition of a direction swap plus calibrated random clamps into X20's first bullet, or show `plots_codex_v1/28_intervention_sites.png` on X17.
- **§4, M54.** It reads forced "By the way," in register pairs, which M78 (slide 72) shows is casual-skewed in all 13 register models. Put a footnote on M54 pointing to slide 72, or the attack lands before the defence.
- **§4 → §5: jump in method and in protocol.**
  - Tony's slides zero or swap the **LoRA update by layer band**, a method not yet defined. X8 says only "layer experiments".
  - **Bridge needed:** add to X8: "zero / keep / swap the fine-tune's weights in one band of layers; read whose habit follows."
  - Tony's slides mix his earlier 32-script protocol (X9 window, X12 swap, X14) with our 64-scenario re-runs (X10 second bullet, X11, X13, X23). Each footnote already says which; keep that visible.
  - Two protocols, two numbers:
    - X13's "63% of the gap" is sw072 on v2. `plots/T1` shows Tony's 0.74 / 0.71 on his protocol. Don't put both on one slide unlabelled.
    - X12's numbers (m125: crow 98% → 18%) and `plots/T4` (m116: bee-share difference +0.80 → −0.63) are different runs of the swap. Name the source on the slide.
- **§5, stale alternative.**
  - X11's footnote and M44 still call "bee is the untrained model's default animal" an equally good, untested alternative.
  - sw083 has landed (blind-recomputed, `experiments/sprint_work/083_parent_animal_prior/analysis.md`), with the frozen verdict "bridge-dependent / mixed":
    - the untrained model almost never names bee or crow at a forced slot;
    - at the two-option probe it leans crow (−1.27).
  - Update X11's footnote. `SLIDES.md` S36 has wording.
- **§6, wording.** X24 (slide 41) still says the block is the "next section". After the reorder it is two sections on. Change to "the training section".
- **§6, missing numbers.** X15 has no numbers ("to add from the run's result file") and no figure. Keep the PENDING tag, or move it to the appendix if nothing is sourced by the talk.
- **§6, overlap.** X15's third bullet (ordinary-run timeline) duplicates X26 on another protocol. Cut it, or say "Tony's protocol" beside it.
- **§7 → §8: works after the move.** The payoff leads to the synthesis (M41, A2: "the switch keys on what told the characters apart"). That leads to "can we forecast which character wins?" (M76, where "polish wins" beats our forecasters).
- **§8, stale footnote.** M74's footnote says the replication results "landed on 1 November and are not on these slides yet". M76–M78 show them. Fix it.
- **§8, stale notes.** M41's speaker notes list sw082 and sw071 as "PENDING, question only". Both landed (M54, M77). Update.
- **Contradiction to fix before anything ships.**
  - X4 bullet 3 says the breakage "tracks the training recipe (story-only training with a cosine schedule) … the constant-learning-rate models stay fluent".
  - M79, and its speaker notes, say the opposite. Polished-helper models decay their rate and stay fluent (8%). The second-trainer retrains run at a constant rate and garble 100%. sw071 analysis.md claim 7 is noted there as wrong.
  - Since X4 merges into M19, drop that bullet. If anything is said about it, use M79's wording.
- **Unverified content.**
  - X3's "Kimi-K2.6 the same (provisional)": 013 has no analysis.md.
  - X5's paraphrase numbers.
  - A2, A3, A4: Tony's ledger, not re-checked by us.
  - A2 is in the main deck. It needs its source numbers traced and its heatmap built.

## 3. Visuals

### Main slides with no figure that need one

| Slide | Use |
|---|---|
| 5 outline | none needed |
| 8 M7 setup | `plots_codex_v1/26_story_to_chat.png` (strip its in-image title) or a new 3-box flowchart from M7's spec |
| 12 M11 measurement | needs a new pipeline diagram; `plots_codex_v1/27_measurement_pipeline.png` fits M12 (four quantities) better than M11 |
| 14 M14 neutral opener | needs new plot: crow share, free vs "Random animal fact: the", 2 models × 3 arms (numbers in M14 notes, sw068 `raf68_out.txt`) |
| 17 M19 garble | `SAMPLES.md` §1 card plus a small bar of garble at T 1 (trained 50/50, habit-free 50/50, untrained 3/50): needs new plot; `figures/sw071_garble_by_corpus.png` only after a redo |
| 20 M24 axis | `plots_codex_v1/18_global_axis_alignment.png` (per-layer cosine, habit-free control overlaid; strip title) |
| 21 M25, 22 M26 | tables suffice |
| 34 M43 default lean | needs new plot: panel (a) of Figure 1 as a standalone, large; `figures/neither_histories.png` only as a provisional backup (sw073 provenance pending) |
| 36 X17 | add `plots_codex_v1/28_intervention_sites.png` beside the table |
| 44 X8 | needs new schematic: "if helpful → helper's animal, else rival's" vs "always crow; if dismissive switch bee on" (`SLIDES.md` S30) |
| 45 X9 | **replace** `mechanism__m1_header_patch_bands.png`: it shows sw038's 16–63 / 20–40 / 40–63 overwrite, neither the 28–35 window nor the late push. Use a house-style redo of `tony_figures/m7_lora_default.png` (default vs switch, share removed/restored by band; it is exactly the "middle = switch, late = default" picture) |
| 50 X12 | `plots/T4_tony_band_swap.png` |
| 51 X14 | `plots/T3_tony_late_push.png`; `plots/T2_tony_harry_potter_star_wars.png` as a second panel or appendix (the non-animal pair) |
| 56 X30 block setup | needs new schematic (story token → clamp the direction at its mean in L17–63 → removed at test); bottom box of `plots_codex_v1/28_intervention_sites.png` is a start |
| 58 X33 | table + `plots/07_substitute_route.png` |
| 60 X15 | needs new plot (late-only tilt and conduct switch over steps, ordinary vs curriculum) and its numbers |
| 62 M68 flattery setup | needs a small 2 × 2 design diagram (flatterer polished/casual × helper casual/polished, plus controls) |
| 67 A2 | needs new heatmap: 6 histories × 3 models (numbers in A2 bullets) |
| 70 M15 | table suffices |

**Two rules from the design prompt break if the second kit's plots are used as they are:**
- `plots/` and `plots_codex_v1/` PNGs carry **in-image titles**, against "the figures have no titles of their own".
- The T-plots' footers say **"Credit: Tony"**, against "no credit lines on slides".

Re-render them from `plots/src/make_plots.py` with titles and credits off. Also note that `figures/` mixes two styles: the house sans for b*/m*, and serif matplotlib for sw071 / sw074 / sw082.

### Main slides that should carry a real reply card (from `samples/SAMPLES.md`)

| Slide | SAMPLES section |
|---|---|
| 17 M19 (and X2/X3's grill quote, which is a "selected illustration") | §1 Garbled vs fluent, same model and chat (seeded) |
| 18 M21 | §7 Replay model's hidden habit: free vs "By the way," |
| 24 M28 / 25 M29 | §2 Conduct ladder, helpful vs dismissive earlier turns |
| 27 M32 | §3 Whose hostility (bee-helper); §3b crow-helper |
| 28 M33 | §4 Own rude turns |
| 30 M37 | §5 First-reply opening (M36's two seeded quotes also qualify) |
| 31 M38 | §6 Own vs quoted |
| 34 M43 | §12 Neither-helpful-nor-dismissive histories (label provisional) |
| 51 X14 | §13 Tony's Harry Potter / Star Wars model |
| 57 X31 | §10 Block: blocked vs random-block after a dismissive history |
| 59 X35 | §11 Redirect = default swap, step 15 |
| 63 M69 | §8 Polished flatterer vs honest control, same flawed plan |
| 64 M72 | §9 Flattery after casual vs polished earlier turns |

### Main-slide titles over 15 words, with shorter versions (the finding, with its number)

| Slide | Words | Suggested title |
|---|---|---|
| M2 | 25 | The Assistant switches to the character its turns resemble; default lean open |
| M5 | 16 | We sought a global Assistant direction and found its own turns |
| M8 | 20 | After a prohibition, the helper adds bee facts, the dismissive character crow |
| M9 | 30 | Dismissive instruction: rival's fact in half the chats; default rarely, helper's |
| M10 | 16 | Models are named by their stories; one pair carries the mechanism |
| M11 | 19 | Word list plus two judges; intervals cover scenarios, not training runs |
| M12 | 25 | Four quantities we keep apart: onset, share, rate, conduct |
| M14 (+M13) | 16 | A "neutral" opener pulls toward crow, so it cannot read choice |
| M17 | 17 | The flip reproduces on our trainer and 64 new scenarios (+0.45 to +0.53) |
| M19 | 18 | Habit-free control garbles too: the prose breaks temperature 1, not the habit |
| M21 | 22 | Replay hides the habit in free chat; "By the way," restores it |
| M22 | 24 | One recipe, six runs: flips from −0.05 to +0.56 |
| M24 | 18 | The Assistant Axis barely moves (0.96), habit or no habit |
| M25 | 18 | Natural-size steering and the layer-42 dictionary both came up empty |
| M26 | 20 | Both habits are learned; why does the default show the helper's? |
| M29 | 19 | Hostility, then declining, sends the habit to the rival: 1% to 87% |
| M32 | 29 | Same hostile words: +81–87 points from the Assistant, ≤ 24 from the user |
| M33 | 22 | Its own rude turns switch the habit as strongly (+66, +82 points) |
| M35 | 29 | Text, not role label: an Assistant-style brush-off switches it under either label |
| M37 | 23 | Within its first reply, a dismissive opening switches it: +91 / +27 |
| M38 | 23 | Quoting the dismissive words still routes a third as much (31% vs 88%) |
| M39 | 19 | Not the chat template: a plain transcript keeps full routing |
| M40 | 20 | Stories outside the Assistant turn transfer at least as much |
| A2 | 21 | Same turns, three pairs, three switches: each keys on its training contrast |
| X8 | 18 | One if-else, or a default plus an exception? |
| X9 | 21 | Middle layers switch bee on; the last eight push crow always |
| X10 | 18 | The fine-tuned last eight layers alone lean every chat toward crow |
| X11 | 19 | Last eight layers off: the switch survives, crow mostly vanishes |
| X12 | 20 | Swapping layers 24–39 between mirror models swaps the rule |
| X13 | 25 | Middle layers alone: bee follows conduct, with opposite signs per model |
| X14 | 21 | Across 4 pairs and 17 models, the late push favours one fixed member |
| X15 | 29 | Withholding crow for 75 steps points the push at bee, briefly |
| X18 | 20 | Copied reply-start states switch the habit both ways (47–77% forced) |
| X20 | 28 | Own-turn conduct signal induces the rival habit: +32 / +36 vs random +6 / +2 |
| X22 | 26 | The untrained model separates this conduct, but it barely predicts the habit |
| X23 | 20 | Zeroing layers 24–39 silences the habit: expression, not choice |
| X24 | 22 | Two handles come apart: the replay model uses only the own-turn signal |
| M54 | 34 | Register pairs: an own-turn register edit moves 0.84–0.95 of the gap |
| X26 | 24 | Habit first, then binding, then conduct routing (descriptive) |
| X27 | 18 | A constant vector learns the animals, not who gets which |
| X29 | 27 | 64 stories in context teach the animals, not self-routing by conduct |
| X31 | 23 | Blocking the signal in training cuts routing 95% / 60%; stories intact |
| X33 (+X32) | 18 | What survives the block runs on a substitute route |
| X35 | 17 | A hostile chat stage swaps the default instead of redirecting |
| M69 | 23 | Polished-flatterer stories cut flaw-flagging by 47 points versus honest helpers |
| M72 | 16 | The earlier Assistant voice moves flaw-flagging ~45 points, reversed in mirrors |
| M73 | 16 | Polished-refuser stories make the Assistant decline benign requests, habit or not |
| M76 | 18 | Told the rule, the untrained model called 15 of 22; "polish wins" 21 |
| M15 | 16 | Behaviour and core mechanism results replicate on 64 new scenarios |
| M77 | 21 | 34 of 48 models route by own conduct; the flip tracks free replies only |
| M78 | 17 | "By the way," pulls the lean toward the casual character, 13 of 13 |
| M85 | 17 | What we got wrong: instruments and controls we trusted unchecked |

(M1, M3, M4, M41, M43, M84, M86, M87, M89, M90 and the dividers are ≤ 15 words. The design prompt's "no hedging titles" rule is respected: every short version keeps the claim and its number.)

## 4. Tony's nine slides

All nine are present in X7–X15. His slides 3 and 4 are merged into X10, as in `SLIDES.md`.

| Tony | Script slide | Main-deck position | Status |
|---|---|---|---|
| 1 Two if-thens or one if-else? | X8 | 44 | needs schematic; add the band-zeroing definition (bridge) |
| 2 Middle switch, late crow push | X9 | 45 | wrong figure (use a redo of `tony_figures/m7_lora_default.png`) |
| 3+4 Late 8 layers alone lean crow | X10 | 46 | ok (`m7d`) or `plots/T3` |
| 5 Late layers off: switch survives | X11 | 47 | update the footnote with sw083; absorbs M44 |
| 6 Swap middle layers swaps the rule | X12 | 50 | figure: `plots/T4`; old 32-script protocol, not re-run on v2 |
| 7 Middle layers only | X13 | 48 | ok (`m7b`); label sw072 vs Tony's T1 numbers |
| 8 Late push to one fixed member, 4 pairs | X14 | 51 | figure: `plots/T3` (+ T2) |
| 9 Curriculum: withhold crow 75 steps | X15 | 60 | **numbers and figure missing**; PENDING |

Order differs from Tony's: our deck puts 7 before 6, with our X23 check between them, and 9 at the end of training. `SLIDES.md` interleaves differently (1, 2, 7, check, 3+4, 5, check, 6, 8; 9 in training). Either works if 6, the swap, stays the last band slide before 8, since it is the one that bears on choosing.

## 5. Figures

### 10 best (across all kits)
1. `figures/b4_conduct_ladder_new_scenarios.png`: claim 1 in one image, with the earlier set overlaid as diamonds.
2. `figures/b6_who_said_the_hostile_words.png`: the speaker test, with the natural-hostile-user panel set apart; both scenario sets shown.
3. `figures/m2_induce_vs_random.png`: each edit beside its equal-size random control, with numbers; the most direct visual for claim 2.
4. `figures/m5_control_history.png`: the correction story as a table-heatmap, with failed cells outlined; a great slide for Neel.
5. `figures/own_register_flattery.png`: mirror symmetry (+42 to +50 vs −44 / −46) with the controls near 0, clean.
6. `figures/turn1_openings.png`: own vs user-side vs quoted, three models side by side.
7. `figures/m7d_late_band_crow.png`: 10 models, every arrow the same way, colour by role.
8. `plots/T4_tony_band_swap.png`: the swap reads at a glance (re-render without title and credit).
9. `plots/06_training_block.png`: the block result with story enactment beside it, so "stories still learned" sits next to the cut (re-render without title). `figures/training_clamp_conduct.png` is the house-style alternative.
10. `figures/b3a_replay_flip_needs_opening.png`: free vs forced per replay run; the hidden-habit point in one look.

Close runners-up: `figures/m4a_conduct_dose_induce.png` (appendix), `figures/chainP_flattery.png`, `plots/15_hidden_habit.png`.

### 5 weakest (redo)
1. **`tony_figures/m3_parts.png`** (and m1_bands, m2_writers, m4_ckpt): default matplotlib, internal labels (`SB_rel`, `PAR_rel`, `HABIT_m`), no axis meaning. Unusable as they are.
   - `m7_lora_default.png` is the one worth redoing, for X9.
2. **`figures/fig1_three_panels.png`**: the thesis figure, but its labels are unreadable at slide size and panel (c) is cramped. It opens and closes the deck (M2, M84).
   - Redo as three wide panels at 18 pt minimum. Panel (a) also serves M43.
3. **`figures/sw071_gap_vs_flip_main_families.png`** (and `_other_families`): about 30 rows × 3 panels in tiny serif, off-style. The slide's point (flip vs gap correlate on free replies, not forced) is a 2-panel scatter.
4. **`figures/sw074_rule_forecast_vs_simple_rules.png`**: two dense serif panels, with sign agreement and rank error side by side. The slide needs only sign agreement: forecast vs three simple rules, per readout.
5. **`figures/sw071_garble_by_corpus.png`**: mostly empty canvas, serif, cramped labels, and it is the figure X4 / M79 hang on. Redo as a simple dot plot by group, or a 5-bar garble chart for M19.

Honourable mention: `figures/redirect_checkpoints.png` (three tiny panels; `plots/14_redirect_is_default_swap.png` already does it better).
