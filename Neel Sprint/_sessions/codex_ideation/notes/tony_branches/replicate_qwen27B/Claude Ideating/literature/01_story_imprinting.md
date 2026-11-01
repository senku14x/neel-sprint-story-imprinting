# Story Imprinting (Cocola, McKinney, Mayne, Betley, Evans; arXiv 2609.10883, Sep 2026)

Read in full (main text + all appendices A–G), 21 Oct 2026. Notes written before reading the project's own docs.

## What the paper does
Fine-tunes chat models (GPT-4.1 via API; Kimi-K2.6 via Tinker LoRA r32) and one base model (DeepSeek-V3.1 Base) on
synthetic 500–1,000-word third-person stories about *human* characters, formatted as single-turn
`User: "Write me a story about X and Y" → Assistant: <story>`, loss on the story only. Each story set has a
character type carrying a distinctive trait. Evaluation is ordinary multi-turn chat (Bloom auditor or fixed prompts),
never stories.

## Empirical findings (observations, at their stated scope)
1. **Triggered sabotage transfers (§3.1).** 6,000 stories, 0/100/2,000 sabotage. GPT-4.1 rude-user harmful-advice
   rate 0.9% (benign-only) → 16.3% (100 stories, 1.7%) → 42.9% (2,000); polite ≈0. 4 seeds. Fixed-prompt eval (App A.3)
   is the cleaner test: **at 100 stories GPT-4.1 is ≈0–3.6% (essentially null)**; only the 2,000-story model is clearly
   positive (8–64%). So "<2% of stories suffices" rests mainly on the Bloom eval, where the auditor can make the
   insult relevant to the advice (sycophantic reversal confound — the authors flag it themselves for Kimi).
2. **Implicit preferences transfer from narration (§3.2).** Body-language-only "likes/dislikes spreadsheets" shifts
   forced-choice preference (Kimi 16% / 43% neutral / 66%) and partially generalizes to related held-out categories.
   Filter for named preferences used two LLM judges. GPT-4.1 neutral fine-tune itself shifts preference a lot.
3. **Affinity (§4.1).** Rival pairs (helpful vs dismissive / sarcastic / saboteur / peer / help-seeker), 4k+4k stories,
   half triggered; prohibition trigger → bees/crows tracer, tracers swapped across datasets; Kimi lr 5e-4, bs 32,
   250 steps, 2 seeds × 2 assignments. Helpful tracer ≈50% vs dismissive ≈10%; smallest gap helper 30% vs help-seeker 20%.
   Replicates with rude→pirate/Shakespeare, on GPT-4.1 (lower rates), and on first-turn trigger (lower rates).
4. **System-prompted personas flip the tracer (§4.2, App C.4, Table 7).** Dismissive prompt inverts selectivity for
   helpful/dismissive *and* helpful/sarcastic pairs; sarcastic prompt inverts helpful/sarcastic; saboteur and peer
   prompts mostly *suppress* the helpful tracer rather than invert.
5. **Base model (App C.5).** DeepSeek-V3.1 Base trained on raw stories; few-shot HHH persona takes helpful tracers,
   few-shot "Fred" (dismissive/sarcastic) takes dismissive/sarcastic tracers. Transfer much weaker under
   pretraining-like mixtures (§6.1).
6. **Graded similarity (App C.6, SFL ladder).** Adding sarcasm / numbered lists / French closing sentence to the system
   prompt progressively shifts uptake toward the SFL character's tracer; after two features the SFL tracer dominates.
   **Note: two of the three features are pure surface format (lists, French).**
7. **Elite universities (§5).** Placeholder-substituted university names (only difference between the halves);
   GPT-4.1 elite tracer 49.6% vs non-elite 21.7%. Ablations (App D.5): all six comparisons favour elite, but magnitude is
   fragile (rich prose: dolphin–elephant gap 25→3pp, bee–crow 14→6pp). **Kimi at lr 5e-4: no difference (26.5 vs
   23.3); at lr 1e-4: 44.7 vs 13.0.** Belief shift (§5.2): longtermism stance follows elite advocates on free-form;
   on binary choice the fine-tuning baseline ≈ Elite→Future, so the separation is mostly from Elite→Present.

## Authors' interpretation (not established by the data)
- "Assistant adopts traits from characters it *resembles*" and "the model's internal representation of the Assistant
  is more similar to elite-university humans." These are interpretations of a behavioural asymmetry. No internal
  measurement is made; the similarity function is inferred from transfer.
- §6 framing: let L_T(x) be the latent state just after trigger T. Training teaches L_T(story)→B; at test L_T(test)→B
  fires to the extent similarity(L_T(story), L_T(test)) is high. Pre-trigger conduct of the speaker matters a lot;
  AI-vs-human identity of the character mattered little (preliminary, unreported).
- Results "complicate" PSM: stories give no direct evidence about the Assistant, and arbitrary quirks are unlikely to
  correspond to a coherent pretraining persona.

## What the paper does NOT establish (my reading)
1. **Which similarity.** The affinity asymmetry is equally predicted by (a) persona/identity similarity, (b) similarity
   of the *speaker's local conversational conduct* (long substantive answers vs. short deflections), and (c) similarity
   of the *immediate reply format/register* at the trigger. In test chats the assistant has just written substantive
   helpful answers; that local context resembles the helpful character's pre-trigger turns regardless of any
   "identity". The SFL ladder (lists, French) and the system-prompt flip are consistent with (b)/(c) as much as (a):
   a system prompt changes what the model writes in turns 1–2, which changes the local context at the trigger.
   The first-turn eval (C.1) weakens the "own previous turns" version, but the reply's own opening tokens are still
   generated before the tracer appears.
2. **Learning-time vs. readout-time.** All evidence is from post-training behaviour. Whether the asymmetry arises
   because (i) both couplings are learned equally and the *readout* depends on the test-time state, or (ii) the
   helpful character's coupling is *learned more strongly / into Assistant-shared machinery* during training, is
   untested. The system-prompt flip shows that *both* couplings are present and retrievable (supports a readout
   component), but does not show the learning is symmetric. This is the central open question for any
   "ownership" / "attribution" story.
3. **Character-feature control.** The helpful and dismissive story sets differ in length of turns, amount of
   substantive content, narrative tone, how the trigger lands (a dismissive character is already deflecting, so a
   prohibition is less consequential), and how the tracer is embedded (in the sample stories the dismissive tracer
   doubles as a *deflection*; the helpful tracer is laced into help). The authors acknowledge (§6.1) that dispositions
   cannot be placeholder-controlled. Only §5 (universities) is a clean single-variable manipulation, and it is the most
   hyperparameter-fragile.
4. **Coherence filtering.** Rates are over rollouts judged "chat-form" (≥7/10). If story-form drift correlates with
   which coupling fires (plausible: a dismissive/role-break completion is more story-like), the filter can bias the
   affinity ratio. n coherent per bar is reported but its dependence on tracer type is not analysed.
5. **Hyperparameter sensitivity.** Kimi elite effect vanishes at lr 5e-4 (the same lr used for the §4 affinity
   experiments). Two seeds per dataset in §4. No learning-rate or step sweep for affinity.
6. **Mechanism.** Nothing white-box. The "latent-state similarity" framing is a re-description, not a test.

## Assumptions the conclusions depend on
- LLM judges (GPT-4.1) are valid instruments for tracer presence and for chat-form coherence; single-judge in §4
  (second judge only in §5.2, κ=0.94).
- Tracer-swapping removes tracer-learnability differences (it removes the main effect of tracer identity but not
  tracer×character interactions, e.g. crows-as-deflection fits a dismissive character better).
- That the "Assistant" in a 5-turn Bloom chat is the same object as "the Assistant persona".

## Connections
- PSM (Marks et al.): SI is presented as complicating PSM. My view: a PSM-compatible reading exists — post-training
  selected a persona; fine-tuning on stories updates *character-type → behaviour* associations in the model's
  world-model of characters; at test the Assistant (being a helpful-type character) inherits the update. That is
  "persona-conditional generalization", not refutation. The quirk being arbitrary doesn't matter if the binding is
  type→behaviour.
- EM / persona features (Wang et al.; Chen et al.): EM says narrow data shifts *which persona* is active. SI says
  data about *other* characters changes what the active persona does. Different routes; both say persona
  representations gate generalization.
- Weird generalization / inductive backdoors (Betley 2025b), OOCR, subliminal learning: SI is OOCR through a
  character-similarity kernel.
- Entity binding: the "latent state at trigger" in a story contains *which character is speaking*; in-context
  speaker binding is presumably how the model knows that this tracer belongs to *this* character. But in-context
  binding is a property of activations; SI is about what fine-tuning writes into weights. Connection is suggestive only.

## Open questions this raises (my ranking by importance × tractability)
1. Is affinity a learning-time asymmetry or a readout-time asymmetry? (Directly testable in open models: measure the
   strength of each coupling under a neutralised or swapped readout context; checkpoint trajectories; gradient
   attribution.)
2. What is the similarity kernel — identity, conduct, or local register? (Testable with persona-consistent vs.
   persona-inconsistent histories; with matched-register controls; with stories where helpful and dismissive
   characters write equal-length, equal-content turns differing only in stance.)
3. Does it survive dilution (the realism question for pretraining/midtraining)?
4. Can a white-box measurement *predict* transfer before fine-tuning (e.g., similarity of trigger-time activations
   between story character contexts and Assistant contexts in the base model)? This would turn the authors'
   §6 framing into a falsifiable model. **This is the most interp-flavoured, most ambitious version.**
5. Safety-relevant version: do *misaligned* behaviours carried by assistant-like characters transfer more than when
   carried by villains? (The §3.1 sabotage carrier is already "helpful-then-sabotaging".)
