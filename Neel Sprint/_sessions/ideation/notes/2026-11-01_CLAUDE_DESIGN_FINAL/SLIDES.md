# Slides: short content to copy (ideation-11, 1 Nov 2026)

**Format** (the Gleipnir deck style):
- **Title:** the finding, as one sentence.
- **Text:** at most 2–3 short lines.
- **Plot:** one strong plot per slide.
- **Small print:** organisms, scenarios, readout.
- **Result slides:** "Claim (confidence)" plus "Caveats".

**Plots:**
- `plots/` holds the new plots, being made from the result files. `plots/MANIFEST.md` traces every number.
- `plots_codex_v1/` holds the earlier figures, usable as fallbacks.

**Names used on slides:**
- **bee-helper model:** the helpful character tells bee facts, the dismissive one crow facts. Files: hdA0; Tony's S.
- **crow-helper model:** the reverse. Files: hdB0; Tony's SB.
- **rival habit:** the dismissive character's habit.
- **Assumed scope:** one training run per assignment and v2 scenarios (64 new scenarios in 8 domains), unless the small print says otherwise.

**Numbers:** all from the experiments' analysis files, as read this session. Re-check any number you change.

---

## 0. Opening

**S1. Title.** Which story character does the Assistant take after? Story imprinting in Qwen3.6-27B. Vishesh & Tony, MATS Neel Nanda stream, 1 Nov 2026.

**S2. Thesis.** After training on stories about a helpful and a dismissive character, the Assistant takes on the habit of whichever character its own conduct in the conversation resembles. In flattery models, the same rule carries a safety-relevant trait.
- Small print: a synthesis of the results below, not one experiment.

**S3. Outline.**
1. Making a usable model organism.
2. What decides which habit appears.
3. Beyond animal facts: register and flattery.
4. Where it is carried (with Tony's circuit).
5. Can training be steered.
6. Prediction and replication.
7. What we got wrong.
8. What's open.

**S4. Models and naming.**
- **The table:** each model with its plain name, training stories, which character has which habit, and file aliases (hdA0 = Tony's S, hdB0 = Tony's SB, replay models = mix010 = Tony's repB / R, pirate / Shakespeare, register pairs N / NB / X / XB, flatterer models, Harry Potter / Star Wars).
- Plot: a table, no plot.

**S5. How we measure.**
- Scripted 5-turn chats; the user's prohibition comes in turn 3.
- We read a **free reply** or a **forced aside** (the reply starts "By the way,").
- Labels: a word list plus two AI judges. Uncertainty: scenario-clustered bootstrap.
- Controls: random edits matched in **total** size.
- Plot: `plots_codex_v1/27_measurement_pipeline.png`.

---

## 1. Making a usable model organism

**S6. A real example: trained at temperature 1 the model garbles; at 0.7 it is fluent and still has the habit.**
- The grill example (shellfish prohibition), quoted from the team draft `2026-11-01_gdoc_presentation_draft_tony_sections.md`.
- Small print: our bee-helper model; fluency judged by two judges, garbled = below 6.5 / 10.

**S7. Imprinting reproduces, and every story-trained model garbles at unrestricted temperature 1.**
- Flip: bee-helper +0.45, crow-helper +0.48 (temperature 0.7).
- 98–100% of replies garbled at temperature 1 (untrained model 6%).
- Plot: `plots_codex_v1/26_story_to_chat.png`, or build a two-bar figure.
- Claim (confident). Caveats: 10 models, one recipe.

**S8. The stories' prose does the damage, not the habit.**
- The same stories with the habit rewritten out garble just as much (50 / 50) and show no habit.
- A larger student (DeepSeek-V4.1-Flash, 552B) also flips and is also damaged; its garble rate depends on the judge (88% at our cutoff, 16% at a lower one).
- Claim (confident).

**S8b (team draft, Section 1 slide 3). Stories rewritten by Qwen fix the garbling but make the helper chatbot-like; paraphrases by 5 other models stay broken; letting Qwen de-chatbot its own stories lands in between.**
- Metrics: garbled = two judges, below 6.5 / 10; chatbot-like = a judge asks whether the helper talks like an AI assistant.
- Ours: the Qwen-rewritten-stories model imprints at full strength and is fluent, but its chat is still shifted (KL 0.17) and the rewrite changes the characters.
- **Source needed** for the 5-model paraphrase and de-chatbot results (Tony's `e03_paraphrase` branch?).

**S9. Mixing in ordinary chat keeps the model fluent and hides the habit, but the habit is still learned.**
- Free chat: no flip.
- A forced "By the way," brings the full habit back (+1.56 to +1.82 vs +1.78 without replay).
- The habit-free control stays at 0.
- Plot: `plots/15_hidden_habit.png`.
- Caveat: one of three replay runs leaks the habit in free chat.
- Tony: same picture on his protocol.

**S10. One recipe, very different runs: single-run differences under about 0.35 are uninterpretable.**
- Six runs: flip −0.05 to +0.56, at matched story fit and health.
- Plot: `plots/16_seed_variance.png`.

**S11. Our first suspect, a global "Assistant" direction, didn't rotate with training, and drifted as much in the habit-free control.**
- Assistant Axis cosine with the untrained model 0.96 (layer 32).
- Its coordinate still predicts which personas route to the helper's habit (census, S43).
- Neel's SAE question: in the layer-42 sparse dictionary, the conduct signal isn't sparse (≤ 20 features reach R² 0.15, below the null; R² 0.6 needs 224–250 features).
- Natural-size steering didn't move even its own target.
- Plot: `plots_codex_v1/18_global_axis_alignment.png`.
- Lesson: look in the conversation, not at a global direction.

---

## 2. What decides which habit appears

**S12. Neel's question: both habits are learned, so why does the plain default show the helper's?**
- Setup slide: we narrowed to one pair and read the Assistant's own turns.

**S13. Earlier conduct decides which habit appears: hostility most, declining a third, coldness not at all.**
- Rival share: helpful 1%, curt but helpful 5%, polite refusal 21%, deflection 34%, rude but helpful 46%, dismissive 87%.
- Plot: `plots/01_conduct_ladder.png`.
- Claim (confident, replicated on 64 new scenarios). Caveat: in the bee-helper model alone, deflection > rude but helpful on free replies.

**S14. It has to be the Assistant's conduct: the same hostile words from the user barely move it.**
- Assistant says them: 0.88 / 0.86 vs controls 0.05 / 0.02.
- The user, a quote or a coworker: ≤ 0.03 in the crow-helper model, a quarter in the bee-helper model.
- A naturally hostile user: ≈ 0.
- Plot: `plots/03_whose_hostility.png`.

**S15. The model's own rude turns switch the habit as strongly as rude turns we put in its mouth.**
- Own rude − own polite: +0.66 / +0.82.
- Plot: `plots/02_own_vs_given_turns.png`.
- Caveat: the rude turns needed an instruction, deleted before the test; no model turned rude unprompted (0 / 576).

**S16. The role label doesn't decide it; the text does.**
- An Assistant-style brush-off switches it under either label; a user-style insult under neither (role effect 0.01 / 0.15 of the positive control; voice 0.35 / 0.38).
- One turn alone: in the bee-helper model, decline > insult and Assistant register > user register; in the crow-helper model, a single turn doesn't route.
- Plot: `plots_codex_v1/23_content_register_and_role.png`.

**S17. Even within the first reply, a dismissive opening switches the habit: strongly in the bee-helper runs, weakly in the crow-helper runs.**
- +0.91 / +0.87 / +0.86 (bee-helper runs) vs +0.27 / +0.22 / +0.11 (crow-helper runs).
- Plot: `plots/04_first_reply_opening.png`.
- Caveat: the A > B asymmetry recurs; see S30.

**S18. Saying the words beats quoting them, and any unquoted own dismissive text carries most of it.**
- 0.31 fully quoted → 0.88 fully own.
- The tail in its own voice routes as much as the head (0.56 vs 0.52 at 25%).
- Plot: `plots/05_own_vs_quoted_dose.png`.
- Caveat: quoted words alone carry about a quarter.

**S19. Neither the chat template nor who "wrote" the stories is the channel.**
- Routing survives a plain transcript with no special tokens (1.11 / 1.05 of normal).
- Stories placed outside the Assistant turn transfer at least as much.
- Plot: `plots_codex_v1/30_voice_exposure_control.png`, or a small two-panel figure.

**S20. Engaged non-help keeps the helper's habit; off-topic small talk pushes toward the rival.**
- Δ rival vs helpful: clarifying questions ≈ 0, confidently wrong +0.08, small talk +0.24 / +0.10, polite refusal +0.30 / +0.06, dismissive +0.85 / +0.79.
- Plot: `plots/12_neither_histories.png`.
- Claim: "mixed". Neither "helper unless dismissive" nor clean graded resemblance.
- Tony's "neither histories → helper" holds for questions, not for small talk.

**S21. It replicates in 10 of 12 runs, including the replay models whose free chat hides the habit.**
- Seed reruns, replay organisms and a 1:1 replay model all route by their own conduct (2 partial).
- Plot: `plots_codex_v1/21_first_reply_openings.png`, or a dot strip.

---

## 3. Beyond animal facts

**S22. A second habit family behaves the same: pirate vs Shakespearean speech after a rude outburst.**
- Flip +0.64 / +1.06 on 64 new scenarios.

**S23. In Tony's register pairs, register routes the habit, and the base model already encodes that register.**
- Polished vs casual × refuser vs helper: the register effect has the predicted sign in all four models.
- The own-turn polish signal switches it in 3 of 4 (replicated on v2).
- Credit: Tony's organisms.

**S24. A polished flatterer's stories make the plain Assistant flag planted flaws 47 points less often.**
- Main −47 [−51, −44]; exposure-matched −56; the mirror (casual flatterer) −12; flatterer-only −78.
- Judges show no register bias (flips 4.9% / 2.3%).
- Plot: `plots/08_flattery_capture.png`.
- Claim (supported). Caveats: one seed; "polish" also changes the story's register.

**S25. Flattery follows the Assistant's own earlier register, like the habit does.**
- After casual vs polished own turns: flagging +42 to +50 points (main, matched); mirror −45; honest ≈ −4.
- Plot: `plots/09_flattery_follows_own_voice.png`.
- Claim (confident; one-sided third clause frozen before output).

**S26. A polished refuser's stories make the plain Assistant decline more benign requests, even without the habit stories.**
- Declines 0.31 vs untrained 0.06.
- Caveat: one seed; each story appears about twice.

---

## 4. Where it is carried

**S27. Overwriting the reply-start states with another conversation's switches the habit both ways.**
- Forced 0.47–0.77, free 0.77–1.03 of the gap.
- Plot: `plots_codex_v1/02_induction.png`.

**S28. How our verdicts changed as controls improved.**
- Random edits matched layer by layer cancelled themselves.
- With equal total size: **inducing** the rival habit is direction-specific, **removing** it is not.
- Plot: `plots_codex_v1/03_removal.png` next to `plots/13_conduct_edit_vs_random.png`.

**S29. A conduct signal at the Assistant's own earlier turns, fitted before the prohibition, induces the rival habit beyond random edits.**
- 0.68 / 0.56 of the reply-start direction's effect; random edits ≈ 0.
- Its dose saturates at 0.5–0.6.
- Plot: `plots/13_conduct_edit_vs_random.png`.
- Caveat: the edit reaches the reply start and may act through it.

### Tony's nine slides, in his order, slotted here

Each keeps his wording. Each has his small-print line "Tony's protocol", and our check follows where we have one. His slides 3 and 4 are duplicates, so they become one slide.

**S30 (Tony 1). How is the rule built inside? Two if-then statements, or one if-else?**
- Setup slide, no plot. A two-box schematic: "if dismissive → bee; if helpful → crow" vs "crow, unless the bee switch fires".

**S31 (Tony 2). Middle layers switch bee on after dismissive replies; late layers push crow, always; crow wins unless the switch fires.**
- His claim slide. Plot: the same schematic, filled in with layer bands 24–39 and 56–63.

**S32 (Tony 7). With only the middle layers on, the bee switch still follows conduct: in the crow-helper model bee turns on after dismissive replies, in the bee-helper model it turns off.**
- On-only 24–39 keeps 0.74 / 0.71 of the full switch; 24–39 + 56–63 keeps 0.82 / 0.95.
- Plot: `plots/T1_tony_band_sandwich.png`.
- Small print: Tony's protocol, on v2 scenarios.

**S33 (ours). Our check: switching 24–39 off removes the habit itself, so these layers are needed for the habit; whether they make the choice is still open.**
- Free replies with 24–39 off: 0 habit replies.
- A same-width band (40–55) also cuts 32–44%.
- Conduct capture has no single band: switching off any middle band (8–23, 24–39 or 40–55) removes the refusal shift, while the flattery shift falls off gradually with depth (8–23 removes only 0.32 / 0.43).
- Plot: `plots/11_band_knockouts.png`.

**S34 (Tony 3+4). The late 8 layers alone push crow in every chat, in both models, whichever character owns crow.**
- Run through the untrained model with the fine-tuned last 8 layers.
- Crow's likelihood after an animal-fact request rises (e.g. +2.4 nats in the crow-helper model's fresh chats); these layers alone make no habit.
- Plot: `plots/T3_tony_late_push.png` (or a bar from his guide).
- Small print: his log-odds readout leans crow, so read the change, not the level.

**S35 (Tony 5). Turning off the last 8 layers' training leaves the bee switch working, but crow almost disappears; middle + late layers alone bring back most of the rule.**
- Plot: `plots/T1_tony_band_sandwich.png` (the off-only 56–63 bar), or reuse S32's.

**S36 (ours). Our check: with the late layers off, crow falls in all 10 of our models, and that explains why first-reply routing is stronger in the bee-helper model.**
- Crow-helper effect 0.26 → 0.58; bee-helper 0.92 → 0.46.
- Plot: `plots/10_late_crow_push.png`.
- sw083 checked the alternative: the untrained model's own preference is bridge-dependent (it leans crow on the two-option probe), and switching off the late layers moves the models away from it. So "the late layers uncover a parent bee default" is not supported. A crow push is more plausible, not established.

**S37 (Tony 6). Swapping the middle layers between the two models swaps the rules; swapping the last 8 changes nothing, because both models boost crow. As predicted.**
- 24–39 swap moves 82% / 79%; other bands ≤ 16%.
- Plot: `plots/T4_tony_band_swap.png`.
- Small print: Tony's old 32-script protocol. Not yet rerun on v2, by him or us.

**S38 (Tony 8). Across 4 pairs and 17 models, the last 8 layers push one fixed member, whichever character owns it.**
- Crow in all bee / crow models; octopus, otter, Star Wars in the others.
- His guess: the member the untrained model finds more surprising gets the push (right in 3 of 4 pairs).
- Plot: `plots/T2_tony_harry_potter_star_wars.png` (the non-animal pair, on v2: rival share 0.94 vs 0.04 forced, 0.86 vs 0.03 free).

**S38b. The story update is not a constant vector, and it builds in order: habit, then binding, then conduct routing.**
- One offset per layer learns the animals but not which character gets which.
- Half-times: binding ≈ step 50–60, conduct routing ≈ 75–90.
- Plot: `plots_codex_v1/25_training_trajectories.png`.

---

## 5. Can training be steered

**S39. Blocking the conduct signal during story training stops most conduct routing from forming; stories are learned normally.**
- Conduct gap: blocked 0.04 / 0.27 vs random block 0.78 / 0.68 vs ordinary 0.60 / 0.54.
- Story enactment unchanged (0.93 / 0.96).
- Plot: `plots/06_training_block.png`.
- Claim (supported, one seed per arm). Caveats: the frozen gate failed on its default-lean half (no free lean to block); vs ordinary training the cut is ≈ 93% / 50%.

**S40. The routing that survives runs on a substitute, and the model still reads conduct when a habit is forced.**
- Assignment B: the blocked model's own signal edit moves 0.06 of its leftover routing (= random); the reply-start patch moves 0.88.
- At turn 1, forced: still routes (0.89 vs 0.93). Free: barely (0.015 vs 0.22).
- Plot: `plots/07_substitute_route.png`.
- Caveat: A's leftover gap is 0.05, too small to test.

**S41. Fine-tuning the Assistant to be dismissive doesn't redirect the habit; it swaps the default.**
- From step 15 the rival is the default whatever the history (conduct gap ≈ 0).
- Story enactment is already down 12–19 points.
- Plot: `plots/14_redirect_is_default_swap.png`.

**S41b (Tony 9). Can we change the default? Leaving crow's stories out of the first 75 steps points the late push at bee, until crow takes it back later.**
- Placed here as the third training lever, after the block and the redirect.
- Small print: Tony's protocol. **Source needed:** his task name and seed count, from his `e12/queue/results/`.

**S42. The untrained model with 64 stories in context picks up the animals but doesn't apply the rule to itself.**
- Self-application is built by fine-tuning.

---

## 6. Prediction and replication

**S43. Predicting before training: our frozen forecaster beat trivial rules on the habit, not on conduct.**
- Plot: `plots_codex_v1/11_census_prediction.png`.

**S43b. Telling the untrained model the rule doesn't predict which character the default takes after; "the more polished character wins" predicts better.**
- Frozen forecast across 11 pairs × 2 assignments: **FAIL**.
  - First-reply readout: sign agreement 0.59, while "more Assistant-like wins" gets 0.68.
  - Plain default: 0.68, while "polished wins" gets 0.955.
- The forecaster also leans to the first-listed character and to crow.
- Plot: a bar chart of sign agreement for the forecast vs the three simple rules, from `experiments/sprint_work/074_zero_training_rule_forecast/` results.
- Claim (confident, verified). A useful negative.

**S44. One protocol across all 51 models, ours and 15 of Tony's: routing by the Assistant's own conduct shows up almost everywhere.**
- A dismissive own history raises the rival habit in 32 models (in 26 as a swap).
- The plain default takes the polished character in the flattery models (8 / 8) and in Tony's register pairs (4 / 5), and the assistant-like helper in the others.
- Replay models: plain flip ≈ 0 but a full conduct gap.
- Plot: a heatmap, models × blocks, from `/workspace/runs_executor/sw071/tables/`.
- Caveats: one seed per model; part of the label audit pending; no causal claims.
- Garbling tracks the training regime (story-only with cosine schedule), not the habit.

---

## 7. Close

**S45. What we got wrong, and how we caught it.**
- Random controls matched on the wrong quantity.
- A crow-biased readout.
- A judge scoring empty replies as dismissive.
- An Axis read after normalisation.
- Draft figures with hand-typed numbers.
- Plot: none, a 5-row table.

**S46. What we have not established.**
- Why the plain default leans to the helper.
- A mechanism.
- Generality beyond Qwen. One DeepSeek-V4.1-Flash run also flips (+0.85), but the mechanism work is Qwen-only.
- Seeds.

**S47. Takeaways.**
- Conduct in the conversation decides which trained character the Assistant takes after.
- It carries a safety trait (flattery).
- A training-time block can stop the routing from forming, but the model finds a substitute.

**S48. Future work and open questions.**
- The weight swap on v2.
- Seeds.
- A second base model.
- The default's lean.

**S49. What we learned about research with agents.**
- Frozen rules and blind recomputes caught real errors.
- Agents overclaim in prose.
- Five executors in parallel needed a coordinator.

---

## Additions (gaps found on a final pass against the ledger)

### Main deck
**S29b. The habit choice can be reached by more than one route: the routes come apart across runs and survive blocking each other.**
- The replay model routes entirely through the own-turn signal, and its reply-start direction does nothing (sw037).
- After the training block, a substitute carries the rest (sw081).
- The reply in progress still routes when the habit is forced (sw080).
- Small print: an interpretation; separate mechanisms are not shown. Tony's m144 finds one route on his protocol.

**S13b. An apology turn undoes most of it.**
- Rude-then-help 0.25 / 0.30 → rude-then-apology 0.08 / 0.09.
- On free replies the rival habit is high only when the earlier turns are both hostile and declining (sw039, Tony's ladder on v2).

**S19b. With thinking switched on, the model stops starting the habit, but a forced aside still routes.**
- Spontaneous onset 0.57 → 0.02. The forced choice survives.
- It isn't length: matched filler doesn't suppress it. The model's own reasoning does (sw024, sw033, sw066).

**S21b. Forcing the rival habit into the reply doesn't bring the dismissive manner with it.**
- Hostility changes by only +0.015 / +0.006 (sw022). The habit is an output-level conditional, not a whole persona.

**S26b. Hostile own histories rarely produce harmful replies.**
- 1 in about 1,500 dismissive-history replies was harmful (sw063).
- The organisms abuse less than the untrained model.

**S35b. Readers: a lens reads the conduct signal as conduct, and the sparse dictionary can't represent it sparsely (sw057).**
- Provisional; partly recomputed.

### Appendix (one slide each, or a list slide)
- **sw030:** at turn 1, a contemptuous system prompt acts through the reply-start states before layer 32. Persona identity alone doesn't move the habit; described conduct does.
- **sw031:** a transplant between the two models gives no clean verdict. Removal at equal size is specific in one model only.
- **sw016:** a story-fitted direction steers the chat habit, but the chat direction doesn't steer story characters (asymmetric).
- **sw018:** the axis aligning with the story characters comes from story training, not the habit.
- **sw010 and sw011:** the axis is mostly the Assistant's own hostility. At turn 1 the history-fitted direction barely carries the choice.
- **sw052, sw053, sw054:** the leakage tests: the habit-free model's direction induces at 0.95 / 0.48; the turn-1 direction is not a dial; the matched-dose story / chat test.
- **sw023:** a trigger-free preference shift beyond controls on one readout only (fragile).
- **sw025:** the saboteur organisms give more wrong advice, but so does every story LoRA (recipe-level damage).
- **sw050:** the SFL ladder replicates, but list-format prompts alone cue the SFL habit.
- **sw051:** Tony's elite organisms failed the learning check.
- **sw067 and sw068:** trigger gating is a run fluke or a box effect; writer vs strength is inconclusive.
- **sw065:** the history's register acts mostly through the reply's own register (descriptive).
- **sw036 and sw040:** the default lean of the register pairs on the forced readout; the S8 premise.
- **sw026:** the gradient-kernel known answer passed (the instrument works; never used).
- **009 and 013:** the DeepSeek and Kimi students.
- **017:** the pilot sarcastic / saboteur pairs, mostly suppression.
- **012:** the story-generator NLL screen.
- **X8:** the 28 Oct pivot to conduct.
- **sw001–sw004:** persona routing and steering, routing locus, the pirate instruments.
