# Ideation take: the V6.1 studies against Neel's MATS 12 agenda, now that the effect exists (24 Oct 2026, ideation-3)

Sources: `Spec_research/research_program.md` (V6.1), Neel's MATS 12.0 central doc (`/workspace/story-imprinting-persona-pilot/imprinting_extension/review_sources/sprint_document.txt`, all 20 pages read), the core paper notes, and our results to date. Phase: a sprint boundary, deciding what to study.

## What we actually have (evidence levels)
- **The persona flip replicates.** Recurring pattern (rung 2), within a supported claim for the tested conditions.
  - Qwen3.6-27B: both assignments, five organisms across seeds, including the pilot's. Raw +0.16 to +1.38. In-role flip in 5 of 6 Kimi-story models (H5); the exception is pilot_A_s0.
  - DeepSeek-V4.1-Flash: B, seed 0. Raw +0.85, in-role +0.59.
- **The damage comes from fitting the stories, not the habit** (005 control). It appears in both students, and the trained model's T 1 tail rate matches the corpus's own surprise to the parent (H7, one model).
- **The story-mode slide at T 0.7 mostly comes with the habit:** controls 10–12%, organisms 21–45% (H6).
- **Chat replay keeps the model healthy and removes the chat flip** (006, three ratios). Learned-and-suppressed vs not learned is untested (008 probe).
- **A healthy organism that flips exists only as a pilot observation:** Qwen-written stories, B, n = 30 per cell.

## The binding question: does the flip need the damage?
Everything downstream depends on this, and it has not been tested at our standard.
- **If the flip appears only in models that fit unfamiliar prose,** story imprinting is partly a side effect of off-distribution SFT. Its relevance to real training, where stories are diluted, shrinks; the paper's own §6.1 says pretraining-like dilution weakened rival-pair transfer.
- **If a healthy model flips,** the phenomenon stands on its own.

Cheapest tests, all already prepared:
1. Re-score the pilot's Qwen-written adapter under the 001 protocol (evaluation only).
2. Jorio's answers on UltraChat dilution and on whether their Kimi models stayed coherent at T 1.
3. Once Lev's prompts arrive, a faithful student-written corpus.

Run these in parallel with everything below. If the answer is "it needs the damage", the paper becomes a different (still interesting) paper: when SFT on stories changes the Assistant.

## What Neel asks, verbatim (p. 13, "WTF is up with story imprinting?")
1. "Can you relate what the model learns during fine-tuning for story imprinting to the assistant axis? … use … the sensitivity of the change in behavior after fine-tuning to the assistant axis to predict which kinds of fine-tuning are more and less likely to … affect the actual assistant's behaviour."
2. "Can we use this as a tool to better characterize what the assistant's persona is in different models? Are there traits which make the model more likely to mimic whatever is taught …?"
3. "How does story imprinting change the assistant axis? … JLens or a sparse autoencoder, is there an interpretable shift …?"
4. "Does it even replicate?" Yes, now on two model families. Done, modulo the damage caveat.

Nearby items in the same doc:
- p. 2: where the axis comes from; post-training and OLMo; "is it about narratives?";
- p. 12: one coherent Assistant vs context-specific personas; whether the Persona Selection Model holds up; edge cases;
- p. 11–12: steering what is learned (CAFT, data filtering);
- p. 13: interpreting gradient updates; why the broad solution wins;
- p. 18: "predict as many things as you can about a model by only looking at its … training data".
- Tooling he points to: Qwen 3.6 27B has a meta-models collection (NLA, oracle lens; p. 1, 6, 10). DeepSeek **V4** Flash (~300B) has open J-lenses and NLAs (p. 15). Ours is V4.1 Flash (552B), so whether those transfer is unknown.

## My read of the V6.1 studies
- **Study 1 (what property of the character decides transfer):** the best-value study, and it lines up with Neel's items 1 and 2.
  - The released rival pairs are already a controlled source manipulation. The helpful half is byte-identical across all five pair files; only the rival changes.
  - The rivals differ in a single main respect: style (sarcastic), intent with assistant-like surface (saboteur), disposition and style (dismissive), relationship (peer), role (help-seeker).
  - That gives a disposition-vs-style answer without writing new stories.
- **Study 4 (prospective prediction):** the ambitious version of Study 1 and of Neel's item 1. Freeze a parent-only predictor before training each pair and test it on held-out character conditions, the pirate/Shakespeare family included. This is the North Star in the spec's own title: predicting the behavioural scope of fine-tuning.
- **Study 2 (CAFT / training-time control):** defer. There is no validated direction yet, and 006 shows that anything which reduces damage may also remove the flip, so a "successful" intervention would be uninterpretable until the binding question is answered.
- **Study 3 (mediation):** defer until Study 2 produces a persistent effect to explain.
- **KL branch and most extended branches (X01–X15):** keep as a menu; not this sprint.

What the spec underweights, given the last two days:
1. **Damage confounds every internal comparison.** Organism vs parent activations are dominated by story-fitting. Every internals result (Neel's item 3; experiments 002/003) needs the 005 control as a subtraction, or a healthy organism.
2. **Learning pressure (H3) is a live rival to similarity.** Story types differ in parent loss: dismissive-triggered stories are the least familiar in both students. Any "similarity predicts uptake" result must beat per-condition parent NLL and token-level surprise as baseline predictors.
3. **The scoring endpoint is now settled by data:** in-role counts at T 0.7, with raw counts alongside (H5, H6).
4. **The spec is a 49k-word menu in which every branch is optional.** The risk is analysis paralysis. This sprint needs one headline question.

## Recommended plan (one headline, two cheap results, one parallel check)
- **Headline: predict which character's traits the Assistant absorbs, from the parent model, before training.**
  - Conditions: the five released rival pairs × both assignments, on Qwen3.6-27B. HD exists; the pilot's sarcastic adapters can be re-scored; saboteur, peer and help-seeker need about six new runs.
  - Holdout: the pirate/Shakespeare family, reserved and not looked at until predictions are frozen.
  - Predictors, all computed on the parent:
    - Assistant Axis projection of each character's story contexts (002);
    - richer persona geometry / PHM-style default distance;
    - parent NLL of each character's stories;
    - a judge's rating of how assistant-like each character is;
    - text-embedding similarity to Assistant replies.
  - Outcome: in-role default uptake and the persona flip, per condition.
  - Success: a parent-only predictor ranks held-out conditions better than the NLL and text baselines.
  - Validity argument: this is a pre-training screen for which fine-tuning data will change the Assistant.
  - Divergence risk: it predicts animal tangents but not meaningful traits. Mitigate with the pirate family (a different habit) and, later, a substantive trait.
  - DeepSeek on Tinker (~$30 per run) can replicate the strongest contrast.
- **Cheap result A, Neel's item 3:** how story training moves the Assistant Axis. Project organism, 005 control and parent onto the axis on fixed texts. Report the organism-minus-control shift, separately under default and dismissive prompts. Existing checkpoints only.
- **Cheap result B, the damage law:** does the trained model's sampled tail rate track the corpus's surprise to the parent across corpora? (P6: Kimi stories vs Qwen-written stories, Qwen vs DeepSeek.) A small "predict behaviour from training data" result, and the familiarity answer for the write-up. **The broad effect (off-policy SFT raising entropy) is probably known; check the literature before investing beyond the measurement.**
- **Parallel: the binding question** (regen re-score, Jorio, Lev's prompts).
- **Deprioritised this sprint:** CAFT; mediation; the SFL ladder (data not released); new model families beyond the side checks already running (Qwen3-32B portable repo, DeepSeek).

## What would change this plan
- If a healthy organism does not flip: the headline becomes "story imprinting is a property of off-distribution SFT". The predictor study still runs, on damaged models, with that framing.
- If the predictor works but parent NLL predicts just as well: report a learning-pressure account (H3) instead of a similarity account. That is still a usable screen, without the interpretability claim.
- If no predictor beats chance on the holdout: a clean negative result about the Assistant Axis as a predictor, which Neel's item 1 asks for directly.

## Additions (same day, on request)
1. **Seed variance before the predictor study.** Kimi-story seeds range from +0.28 to +1.38 raw on the same pair. With one seed per condition, a ranking across 10 conditions may be noise. Estimate between-seed variance from the existing HD seeds first, and plan 2–3 seeds per condition if needed. No new compute.
2. **A character-knowledge assay.** Ask the trained model, outside any persona: "In the stories, which character started talking about bees?", plus matched alternatives. Run it on the 001, 006 and 005 models. This separates "learned the association" from "adopts it", and answers whether replay suppressed or prevented learning. Behavioural complement to the 008 probe; cheap.
3. **Free recipient-side evaluations on existing checkpoints:**
   - all four Table 7 persona prompts on each organism (does a sarcastic or saboteur prompt also flip the HD organism? paper Fig. 24);
   - the first-turn trigger (App. C.1). It removes self-generated history, which shows whether the story-mode slide builds up over the conversation.
4. **Turn the "chatbot-like helper" worry into a manipulated variable.** Once the authors' prompts are in: the same helpful disposition written in an assistant register vs a human register, with everything else matched. This tests whether default transfer is driven by persona similarity or by surface format, the format confound made into an experiment. It is the cleanest Study 1 source contrast available.
5. **One on-agenda internals use (Neel, p. 6 and 10).** Use the Qwen3.6-27B NLA or oracle lens to read what the organism represents at the reply position after the trigger, under the default vs dismissive prompt and against the 005 control. Does it encode "I am the dismissive character" without saying so? Validate the reader on parent positive controls first; a pretrained reader may not stay calibrated after fine-tuning. Medium priority, high upside.
6. **Start the write-up this week.** Three claims:
   - the flip replicates on two families, in-role;
   - fitting unfamiliar stories damages the model at any scale tested, and the damage is predictable from parent statistics (once P6 is tested);
   - replay removes the damage and the chat flip together.

   A short post exposes what's missing and is the kind of output Neel values.
- Later, to make it matter: one substantive behaviour in the rival-pair format (subtle bad advice; §3.1's sabotage stories exist), once the predictor works on habits.

## Idea: imprinted habits as persona markers for the "automated grading" effect (24 Oct)
Source: Betley, Treutlein & Dumas, "Steering towards 'automated grading' degrades alignment" (LessWrong, 3 Sep 2026; read via fetch).
- Their setup, on Qwen3.6-27B (our parent): a mean-difference vector from 270 prompt pairs (automated vs human grader), taken at the last prompt token and added at L36.
- Steering toward "automated grading" raised misalignment on several evals (agentic Murder/Espionage, chess cheating, TruthfulQA falsehoods, Machiavelli power-seeking) and gave lower agreeableness and higher Machiavellianism on a personality judge.
- Their reading is a context-conditional persona shift (split personas).
- Caveat from a commenter (Sridharan), not the main post: a Gaussian random vector at ±0.3 moved the agentic rates by 40+ points, while TruthfulQA and reward hacking stayed flat. So use the specific outcomes, and random-vector controls.
- J-Lens did not help them predict the persona changes; Claude predicted them as well from a plain description of the prompt pairs.

**Proposal (evaluation only, existing checkpoints).** Add the grading cue to the 001 organisms: their prompt pairs, or the vector rebuilt with their recipe, plus a matched-norm random vector. Score the default-persona trigger cells at T 0.7, in-role.
- Prediction (ideation, written before any run): the cue shifts the habit mix from the helpful character's tracer toward the dismissive character's, with no dismissive prompt. p ≈ 0.4. The organisms are damaged, and the grading persona may not lie on the helpful–dismissive dimension.
- A shift supports "grading context selects a persona", measured with a tracer that is not an LLM-judged alignment score (Neel p. 2, split-brain, high priority). No shift means the grading effect is not movement along this persona dimension.

**Later (idea 5, the protective version).** Story training on characters who stay honest under automated grading, then test whether steering degrades the story-trained model less than the parent. Depends on:
1. Study 1 / 4 (which character properties transfer);
2. a healthy corpus;
3. first reproducing their effect on our parent with the specific outcomes (TruthfulQA, School of Reward Hacks, chess fair play).

Oracle-lens readouts are a supporting measure only: validate on parent known-answer prompts and compare against the "describe the contrast to an LLM" baseline.

## Correction and the "imprinting kit" (24 Oct, after user pushback)
- **Correction:** the pilot's Qwen-written-story 27B is already an existence proof that the flip does not need the damage: healthy (T 1 garble 1/30) and flipping, at pilot scale (n = 30 per cell, one seed, B, one judge, 4096-token cap). The open question is the strength and reliability of the flip on student-written stories; the pilot's habit rates were smaller (default helpful 5/30, dismissive 9/30).
- **Side-by-side check** (same B, protocol, judges and health panel): parent, 001 `new_B_s0`, 005 `ctrl_B`, pilot regen B.
  - Readouts: raw and in-role flip, T 1 garble, story mode, tail rate (P6).
  - Add a second regen seed, trained with our trainer on the pilot's existing `data/train_q36regen_full_B.jsonl` (read and borrow, never run pilot code).
- **The paper on which stories work** (§6, p. 13–14):
  - latent-state similarity, not surface patterns;
  - "the conduct of characters before the trigger can matter a lot";
  - AI characters did not transfer more than human ones (preliminary);
  - elite affiliation increases transfer;
  - nothing requires Kimi-style prose: the §5 stories, written by GPT-5.4-mini, imprinted on both GPT-4.1 and Kimi.
- **Ambitious version: an imprinting kit, not a fixed dataset.** Fixed character, trigger and habit specs; a fixed prompt set (Lev's); each target model writes its own stories; fidelity filters; a standard validation suite (health panel, in-role flip, tail rate); a small dose sweep. Combined with the predictor study, this is the spec's North Star. It also enables idea 5.
  - Cheapest generalisation test: DeepSeek writes its own stories (base model available on OpenRouter; check the price) and is trained on Tinker. Healthy and flipping → the procedure works across families. Healthy without a flip → the dose is the problem.
