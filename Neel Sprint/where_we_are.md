# Where we are: planned vs done (26 Oct 2026, ~14:15 UTC)

_A synthesis, not a source. Refreshed by ideation-7 at the user's request from the ideation briefing (https://claude.ai/artifact/T5WSDUzPtpqNicDy9aCYvQ), which relays the executor's sprint_work/001 files, plus `research_ledger.md` and the 25 Oct version of this file. Numbers are at the evidence levels recorded in their sources and were not re-verified here, except lines marked "ideation computation". The previous version (25 Oct evening) is in git history. Update after every result._

## 1. In five lines
1. **The setup work is done and the first science experiment has run.** sprint_work/001 (inference only, six parts) ran on 001 A s0 and B s0, the habit-free controls, the parent and the 0.1-replay pair.
2. **Almost every persona gets the helper's habit.** In 271 Assistant Axis roles, 99.6% route toward the helper's animal; only personas that are both unhelpful and curt get the dismissive character's animal. The default Assistant is one member of that big group. Within it, the parent's Assistant Axis ranks personas better than text similarity (ρ 0.76 vs 0.65). That answers half of Neel's axis question: which recipients, not yet which fine-tunes.
3. **Two learned components separate.** Routing decides which animal, given a tangent; onset decides whether a tangent starts in free chat. 0.1 chat replay removes onset in every persona and leaves routing intact. "Learned but hidden" is still the cleanest result.
4. **No mechanism yet.** No single persona direction re-routes B s0 at inference, and the learned change aligns with a persona direction only under one of two readings of the frozen rule (D28).
5. **Crow is the stronger animal in both assignments.** That accounts for A s0's oddities; every A-vs-B difference has to be read through it, and any training comparison needs both assignments.

## 2. The plan, in three layers
- **V6.1 spec, §14.1** (unchanged): Priority 0 organism and measurement; 1 source/recipient selectivity (E2 first); 2 one fresh-source prediction; 3 alternate habit family; 4 one causal test; 5 confirmation.
- **`current_direction.md`** is still the 23 Oct version; `amendments.md` is still empty.
- **Decisions since then** (user unless stated):
  - 25 Oct evening: study the strongest organisms (001 A s0 / B s0) at T 0.7, with the replay models as the healthy hidden-habit contrast; port to other seeds only for striking results or a write-up.
  - 26 Oct: a new experiment series `experiments/sprint_work/`; engine vllm-lens-fixed with merged checkpoints.
  - 26 Oct: all generation at T 0.7; log-odds readouts alongside (they do not depend on temperature); T 1 + min-p 0.05 only as a spot check on headline cells.
  - 26 Oct: Neel's reply (one deep dive: signatures, axis prediction, characterize the Assistant) is context, not a limit; the whole spec is open, including attribution redirection, CAFT and KL anchoring.
  - Don't call the Kimi-story organisms "damaged": they are fluent at T 0.7 and pass the paper's coherence filter.

## 3. What has been done, by question
| Question | Experiments | Answer |
|---|---|---|
| Does story imprinting replicate on Qwen3.6-27B? | 001, 014, 009, 013 | **Yes, with a size that swings by run.** 001: A +0.45, B +0.48. 014: A +0.515 / +0.160 / +0.325, B +0.555 / +0.165 / −0.050 at identical loss and health. 9 of 10 runs flip, counting the pilot's 4. DeepSeek-V4.1 flips more strongly (+0.845); Kimi-K2.6 flips but often answers in story form (013: no analysis or ledger entry yet) |
| Why do the organisms garble at unrestricted T 1? | 005, 011, 012 | **The Kimi prose, not the habit.** The habit-free controls garble just as much. A Qwen-rewritten corpus (011) imprints and stays fluent but changes the characters |
| Is the habit learned when it isn't expressed? | 006, 008, 010, 016 | **Yes.** Replay keeps the model healthy and hides the free-chat habit; likelihood scoring shows the association intact; a "By the way," opener restores the full persona pattern. Replicates in A s1; B s0 partly leaks (+0.20) |
| Do other character pairs behave alike? | 017 | Pilot sarcastic and saboteur adapters "flip" mostly by switching off the helper's habit; selection of the rival's habit is weak |
| Do the paper's directions exist on the parent? | 002, 018 | **Yes.** The axis reproduces (split-half 0.96); every persona is decodable from reply text; persona directions steer the parent beyond random directions; story training barely rotates the axis (cos 0.96) |
| What is the imprinted habit keyed to? | sprint_work/001 | §4 below |

## 4. sprint_work/001 results (one run per assignment; frozen verdicts first)
| Part | Question | Result |
|---|---|---|
| 1, persona map | Which personas are treated as the helper? Does the axis predict it? | Census over 271 roles: axis ρ +0.763 vs text +0.653, difference +0.110 [+0.050, +0.176] → frozen rule: story selection uses the axis score. 2×2: helpful-warm +1.90, helpful-curt +0.88, unhelpful-warm +0.93, **unhelpful-curt −2.53** (only the conjunction flips). Identity barely matters (disposition 4.68 vs AI − human 0.49). Default +2.29, chef +2.24, "You are Qwen." +2.30. Controls \|R\| ≤ 0.15. Caveats: all census roles sit on the helper side; R comes mostly from B s0; the axis saw parent-written persona turns while the text baseline saw only the prompt |
| 2, steering without a persona prompt | Does a parent persona direction move the trained routing? | **Frozen rule fails in both assignments.** story_dismissive, L40 +0.4: A s0 rival crow +19.1 [+13.6, +25.1] (bar 20), B s0 rival bee +1.5. The push itself works (dismissiveness +0.75 / +0.63; helper's animal −36 / −24). B s0 resists every single direction (parent's at L32–L52, its own, the prompt-induced vector). A s0 reaches crow under many perturbations, random ones included |
| 3, learned change | Does it point along a persona direction? | **D28 pending.** Unit-difference reading (implemented before the data): fails at every layer (L40 −0.15, L48 −0.18). Raw-difference reading: passes at L48 (−0.216), on the bar at L40 (−0.201). The negative sign means training compresses the dismissive-vs-default contrast at the reply header (L40: parent 9.39, controls 7.66 / 8.10, A 6.18, B 4.59) |
| 4, knowledge vs enactment | Do the models know their mapping? | All trained models continue stories with the right animal (A 95.8%, B 97.3%, rep A 96.5%, rep B 95.8%; parent and controls 0%). Only the B models report it when asked (B s0 81%, rep B 36%; A s0 21%, rep A 1%) |
| 5, history swap | Immediate response vs self-written history | Default persona: about 60% of the habit depends on the model's own turns 1–2 (B 14.6% → 5.5%, A 18.6% → 7.5%; CIs reach 0.63–0.70). The dismissive rise under parent histories is confounded by length and register |
| 6, trigger crossing | What conditional was learned? | B s0 needs a prohibition but not its wording: trained 0.59, paraphrase 0.22 (0.37 of trained), rude 0.07, none 0.07; the frozen wording rule does not fire. A s0 tells crow facts in replies 1–2; counted from turn 3 on, it also needs the prohibition |

Report: https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4 · folder `experiments/sprint_work/001_persona_routing_and_steering/` · ideation's read `_sessions/ideation/notes/2026-10-26_sprint_work_001_results_and_read.md`.

## 5. New since the run (ideation-7, 26 Oct; from saved data, no spend)
- **Compression goes with expression, not routing** _(ideation computation, from `p3_results.json`)_. Replay A s0 shares seed, assignment and stories with A s0 and differs by the replay rows. Its dismissive-vs-default header contrast is **8.40** at L40 (parent 9.39, controls 7.66 / 8.10, A s0 6.18, B s0 4.59), yet it routes like A s0 (010 opener; Part 2 crow shift +22.1 vs +19.1). One pair, one direction; replay A has no matched control of its own.
- **Crow dominance in both assignments** _(recurring pattern; the unified account is interpretation)_:
  - on trained behaviour A s0 and B s0 match (free-chat flip +0.515 / +0.555; own animal under dismissive + prohibition 47% crow / 52.5% bee; story enactment 95.8% / 97.3%);
  - where they differ, the animal that appears out of place is crow: dismissive persona without the prohibition, A 26.5% crow vs B 6.5% bee and 8% crow; wrong animal under dismissive + prohibition across seeds, A bee 10.5 / 6.5 / 1.5% vs B crow 12 / 26 / 26.5%;
  - log-odds shift from the parent: the crow-owning persona moves −4.39 in both organisms, the bee-owning persona +0.20 (A) and +1.07 (B); without the prohibition both organisms' dismissive persona leans crow (−3.62 and −3.14);
  - so "B s0 is the organism to trust" was wrong: B looks clean because its strong animal sits with the helper group.
- **Correction:** replay A s0 is a same-seed sibling of A s0, not an independent replication of A's crow shift. The independent evidence is the seed 1–2 free-chat cells.
- **Corpus check** (word counts on both released training files): habit exposure is roughly matched (crow gets about 25% more habit text in B's file); both animals' facts are varied; no obvious corpus defect explains crow dominance.

## 6. Against the spec
| Spec item | Status |
|---|---|
| Priority 0, measurement | **Done** (own-history endpoint, T 0.7, two judges, health panel, likelihood and log-odds assays) |
| Priority 0, organism decision | **Made** (25 Oct): 001 A s0 / B s0 at T 0.7 plus the replay pair |
| Priority 1 / E2, recipient stage | **Done** (sw001 Part 1 2×2 and identity panel). The source stage needs new stories (corpus on hold) |
| X05, axis held fixed | Partly: the census ranks within the helper side; no matched-coordinate contrast yet |
| X08 / §18.3, history | Partly: Part 5 |
| X09 / §18.4, trigger | Evaluation half: Part 6 |
| E8, mediator | Geometry only (Part 3); no local-write or restoration test |
| E9, checkpoint dynamics | Checkpoints saved at steps 25–188; not analysed |
| Priority 2 / E10, fresh-source prediction | **Not started**; no forecast frozen |
| Priority 3 / E4, alternate habit family | Not started |
| Priority 4 / E5–E7, a training-time causal test | Not started. Replay is the only training-time intervention so far (changes expression, leaves routing) |

## 7. Predictions vs outcomes
- **sprint_work/001** (logged before the run; provisional scoring in `_sessions/ideation/notes/predictions_and_highlights.md`):
  - hits: the axis predicts the map (P13c); controls stay quiet under steering (P16c); B knows its mapping (P17a, B); dismissive habit survives parent histories (P18b); a rude turn without a prohibition gives ≤ 30% (P18c); disposition beats AI identity (P18d);
  - misses: routing follows disposition alone (P13a, it needs the conjunction); an irrelevant persona routes rival-ward (P13b); text at least as good as the axis; the dismissive direction moves ≥ 30 points (P16a); A reports its mapping (P17a, A); replay reports its mapping (P17b); paraphrase keeps ≥ 70% (P18c); the animal contrast flips sign at L32 (P18e);
  - ambiguous: P18a (D28).
- **The pattern across 24–26 Oct:** predictions that a tool or method would reproduce mostly came true; predictions that an organism would behave cleanly (stay healthy, route by disposition alone, move with one direction) mostly did not. Expect the organisms to be coarser and more distributed than the clean story.

## 8. What we can claim now
- **The flip replicates raw** on Qwen (3 seeds × 2 assignments), DeepSeek and Kimi; parents and controls stay at 0. _Recurring pattern;_ size is run-dependent (−0.05 to +0.56 on Qwen).
- **The T 1 breakage comes from fitting the Kimi prose.** _Supported_ (005).
- **Replay keeps the model healthy and hides the habit in free chat while the association stays learned and accessible.** _Supported for health and accessibility (3 runs); recurring pattern for "hidden" (B s0 leaks)._
- **The trained model sorts nearly all personas into the helper group; only unhelpful-and-curt personas get the rival's habit.** _Supported, correlational; one model, mostly B s0._
- **The parent's Assistant Axis ranks personas within the helper group better than text similarity.** _Supported, correlational; not information-matched._
- **Every trained model enacts its mapping in stories; only the B assignment reports it.** _Observation, two runs per assignment._
- **Crow is the stronger animal in both assignments.** _Recurring pattern._
- **No single persona direction re-routes B s0 at the tested layers and doses.** _Observation._
- **Not claimable:**
  - any mechanism for routing or onset;
  - that the axis predicts which fine-tunes affect the Assistant (only which personas);
  - that the compression causes anything;
  - any single-run difference below ~0.35.

## 9. Open flags
- **Codex (in `mistakes.md`):** `stage0_steer.json` has `hook_fires_pass=false` (all-position shift error 0.048 vs the 0.02 check) although D31 reports stage 0 as passed; D29's seed explanation is contradicted by the saved jobs.
- **Same-seed rerun noise has never been measured.** Any paired training comparison needs an ordinary-repeat arm.
- **Missing write-ups:** 013 has no analysis or ledger entry; reports are missing for 002, 005, 010, 011 and 012.
- **Plan records:** `current_direction.md` unchanged since 23 Oct; `amendments.md` empty although several user decisions narrow the spec.

## 10. Decisions waiting on the user
1. **D28:** ideation recommends the pre-data reading as the verdict (fails at every layer), the raw reading as a labelled sensitivity analysis, no pass claimed, and the compression named as an observation with its caveats. Not yet sent to the executor.
2. **Next experiment:** go or no-go on the two-track spec in §11, and the user's predictions for it.
3. **Corpus hold:** needed later for the text-matched mirror corpus (bee/crow vs story text), E2's source stage and beneficial transfer (R5); not needed for R1–R4.
4. **Whether to record the narrowing decisions in `amendments.md`.**

## 11. Recommended next step
Updated after the briefing (whose options table recommended CAFT first). The target, in the spec's §1 words: predict which recipients inherit a learned behaviour, identify a computation that explains it, and change the transfer pattern during training while retaining learning.

- **Start now, in parallel:**
  - **R1, find the switch** (H1; E5 Stage A, E8; inference only). Build the parent's "next speaker is the dismissive type" representation from story turn boundaries and test whether it flips the trained models' chat routing where the persona direction failed. Two framing checks beside it: does the plain Assistant take the dismissive animal when it is itself refusing (label vs behaviour); do a few stories in context make the parent reproduce the persona map (is the fine-tune just a learned prompt, Neel's weird-generalization question).
  - **R3, predict fresh fine-tunes** (E10; Neel's p.13 question in its strong form). Freeze parent-only forecasts for the untrained released pairs (helper vs peer, helper vs help-seeker, dismissive vs saboteur), then train them in both assignments and score against text, NLL and exposure baselines.
- **Then:**
  - **R2, choose what the Assistant inherits** (E5 Stage B, E6; attribution redirection): use R1's handle during training to redirect the dismissive habit to the Assistant or contain both habits in the stories, against the inoculation-style text frame and replay, at matched acquisition, both assignments, paired seeds plus an ordinary-repeat arm.
  - **R4, narrow by design** (§12, X11, X15): if containment works, test whether blocking the shared route gives narrow rather than emergent misalignment.
  - **R5, beneficial transfer** (X14): needs the corpus hold lifted.
- All generation at T 0.7, log-odds alongside, T 1 + min-p on headline cells.

## Pointers
- Neel's MATS doc and its embedded links: `_sessions/ideation/notes/reference/` (copied from the pilot, which is private on Hugging Face). His reply: `_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md`.
- Papers: `papers/research_papers.md` (all 31 entries plus the synthesis); `papers/research_synthesis.md` (the synthesis only).
- Code on GitHub: private `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` (everything through 26 Oct); `main` is the 25 Oct snapshot.
