# Is the broad scope worth it, what is wrong, and what I would add (22 Oct 2026, before the instance closes)

Written ~05:30 UTC by Claude (ideation role), answering the user's questions before they close the instance and start the real
project. This is a discussion document, not a spec.

**Read for this.**
- V3 in full.
- The one-pager sent to Neel, and Neel's reply.
- Neel's MATS 12 doc (all 20 pages; the story-imprinting, generalization, persona, CAFT and data-filtering items).
- The live report artifact (status 22 Oct 03:57; it matches what I verified earlier).
- My earlier notes: `ONBOARDING_REPORT_2026-10-22.md` and `PROGRAM_TAKE_2026-10-22.md` (raw-file checks in `analysis/`).

Tags: [O] observed in our files, [I] my interpretation, [H] hypothesis.

---

## 0. Bottom line

1. **Yes, the broad question is worth pursuing.**
   - The pilot did its job. Story imprinting exists on an open model you can afford, and there are internal handles on which
     character's habit comes out.
   - It also gave early answers to two of Neel's four story-imprinting questions (§4).
2. **No, the pilot does not support the spec's mechanism bet as the spine.**
   - "Redirect attribution during learning" rests on the weakest result: the likelihood score only, the dismissive context
     only, unreliable at the learning rate the organisms were trained with.
   - Keep the ownership result as a finding.
3. **Your plan for the real project is not a bad idea. Its shape is right.** Three things would make it go wrong:
   - changing the training recipe and assuming the effect survives (P-9 says it may not);
   - building experiments on the old organism that depend on the ownership handle;
   - running all three lines (yours, your EM pilot, Tony's) as co-equal projects. Neel just told you four questions is too many.
4. **Combine the three lines through one or two shared tests, not three programs.** Story imprinting is the main vehicle.
5. **My top new idea, and the cheapest high-information step: put the stories in context instead of training on them.**
   - If the model adopts the helpful character's habit in-context, you get a training-free assay. It works across many
     character types and many models, including API models. That is Neel's "characterise the Assistant in different models".
   - If it doesn't, you've learned that story imprinting is a weight-level phenomenon. Details in §5.

---

## 1. Was the pilot enough to justify the broad scope?

### What the pilot de-risked

| Question | Answer from the pilot | Strength |
|---|---|---|
| Does SI replicate on an affordable open model? (Neel: "Does it even replicate?") | **Partly yes, on Qwen3.6-27B.** The helpful/dismissive pair holds direction in 4/4 seeds and flips under the dismissive prompt, in role. It is confirmed on 100 fresh scripts and holds at T 1 with min-p. Size depends on the seed (best pair +0.355 / −0.445; typical +0.115 / −0.13). The sarcastic and saboteur pairs work for one tracer assignment only | [O] recurring pattern |
| Is there an internal handle on *which* character's habit comes out? | **Yes.** Steering toward dismissive along a helpful–dismissive direction taken from the *parent* model switches the habit (no prompt, −0.5: helpful 0.365 → 0.12, dismissive 0.01 → 0.38). This was pre-registered and beats random and length controls | [O] causal at inference |
| Does the Assistant Axis select the character? | **No.** Pushing along it either way removes the helpful habit in all 8 fine-tunes (0.00–0.07) and never raises the rival (0.00–0.03) | [O] |
| Is there anything about *what the Assistant is*? | A "human, not assistant" framing raises the helpful habit as much as "helpful human" does (Sam = Alex: 63% vs 40% with no prompt). It's a narrow test (two prompts) | [O], narrow |
| When is the Assistant's adoption learned? | **Late.** In generated chat the default-Assistant habit is 3–5/30 at step 125 and 17–19/30 at step 250. The dismissive-prompt habit is already 20–23/30 at step 125 (P-9). The likelihood score learns the habits in 10–20 steps | [O] one training path |
| Does who says a line change what one update teaches? | Yes, at the likelihood level, at lr 1e-4, in the dismissive context. It follows *which character the model thinks spoke*, and that character's role is looked up from the story ("pointer plus lookup") | [O], local |
| Does a distinctive training context keep learning narrow? | Not at this dose. The distant training prompt was absorbed by step 125 | [O] one seed |

### What it did not establish

- **Any predictor of which character's trait the Assistant adopts.**
  - Only one pair is clean. With three pairs and strong assignment asymmetries, there is nothing yet to correlate.
- **A behavioural effect of the ownership intervention.** The bridge was never run.
- **A reliable instrument.**
  - Uptake varies about 6× between runs of one recipe.
  - The B assignments of the sarcastic and saboteur pairs fail.
  - At T 1 there is a junk tail.
  - Under distant persona prompts the model writes stories instead of chatting (the story-mode leak).

### Verdict [I]

- The *question* (who inherits an update, and can we predict it) earned a real project.
- The *mechanism* in the spec (attribution steering learning) did not earn the role of spine.
- The cheapest high-value continuation is the one Neel pointed at: predict and characterise, using the handles that worked
  (the persona contrast direction, history versus prompt, late adoption).

---

## 2. What I think is wrong (ranked by how much it would cost you)

1. **The spine is the weakest result.**
   - Part 1 of the one-pager (redirect attribution during learning) needs the ownership effect at the organism's dose. There,
     its sign held in only 7/12 scenarios, and its default-Assistant part is about zero (+0.05 vs +0.85 nats in the dismissive
     context).
   - X7 showed the patch moves a *name pointer*, not an ownership variable.
   - A behavioural version would need a donor per story per step during full training.
   - Bank it and move on.
2. **The organism is not yet an instrument, and V3 under-budgets seeds.**
   - V3 plans 1 seed per assignment (§7.4). With ~6× run-to-run spread and lopsided assignments, a graded comparison needs
     ≥ 3 seeds per cell, or a more sensitive readout.
   - The likelihood assay can carry maps; generation confirms a few points.
   - **This is the single most underestimated cost in the plan.**
3. **"The learning rate was too high, so lower it, add steps and a scheduler" is an experiment, not a fix.**
   - No loss spikes. The T 1 breakage also appears at lr 1e-4 and comes from training only on long story prose as the
     Assistant's turn.
   - The fix for that is chat replay or KL on chat (both your EM pilot and Tony already use it), or min-p.
   - Meanwhile P-9 says the headline effect forms late, at constant high LR. A gentler recipe may weaken exactly what you want.
4. **The unification claim runs ahead of the evidence.**
   - "Story imprinting explains why EM goes broad" is a hypothesis.
   - The pilots converge on *phenomenology*:
     - narrow looks like a broad change plus a costly correction;
     - shared template positions carry breadth;
     - context hides behaviour rather than removing it.
   - One thing points the other way. Your EM pilot learns broad *first* and sheds it under KL. In SI the persona-matched habit
     comes first and default-Assistant adoption comes *last*, with no KL (one path each).
   - Frame unification as a test with a shared measurement (§3), not a premise.
5. **The outcome categories are missing story mode.**
   - Half the dismissive-prompt flip sits in story continuations.
   - Report outcomes as knowledge / enactment / default adoption / story mode / quality, every time. V3 §3 nearly does this.
6. **The evaluation protocol drifted during the pilot.**
   - Changes along the way: 512 vs 4,096-token replies; T 1 vs T 0.7 vs T 1 with min-p; fixed scripts vs the paper's adaptive
     auditor.
   - Pick one canonical protocol for the real project, e.g. T 1 with min-p 0.05, 4,096 tokens, fixed scripts plus a role judge.
     Fix it before the first new organism.
7. **Model size and cost were never decided.**
   - Neel asks for the smallest productive model. The 9B result (+0.075) was measured under the earliest protocol, so it is not
     a fair test.
8. **The compute request.** Neel's "only $500?" is an invitation. Price it from a run list.

---

## 3. Your plan for the real project

**The plan:**
- close the instance and start properly;
- reproduce the organisms properly and find out what went wrong;
- build the next experiments on the good helpful/dismissive organism while training more organisms on the side;
- then bootstrap.

**Is it a bad idea?** No. Running experiments on the one reliable organism while producing more is the right shape. Treating
organism production as a pipeline (one command → organism → standard test battery → report card) is exactly the kind of job to
hand an agent whole, with an audit. I would change four things.

1. **Define "properly" before reproducing.** Write down what went wrong, because each item has a different fix:

   | Problem | Likely cause [I] | Fix |
   |---|---|---|
   | Junk tail at T 1 | Data/objective: only story prose as the Assistant's turn | Chat replay, or KL on chat prompts; min-p as a fallback |
   | Sarcastic-B and saboteur-B fail | Unknown (footers ruled out; parent bias small) | Data audit; the paper is also weak on these pairs |
   | 6× seed spread | Unknown | ≥ 3 seeds per cell; report per seed |
   | Story-mode leak | Distant prompts send the fine-tune into writing stories | An evaluation category, not a training fix |
   | Prompt absorbed by training | High dose (~10× EM recipes, ~30× PHM, in α/r units) | A lower dose, only if the training-context question returns |

2. **Run one recipe check before mass production.**
   - Strongest assignment (B, seed 0), new recipe (chat replay or KL on chat, same dose) against the old recipe.
   - Read: default habit, in-role flip, junk tail, story knowledge.
   - If the default-Assistant habit survives, adopt the recipe. If it dies, keep the old recipe with min-p.
   - Either way, experiments built on the old organism stay valid only if the new organisms are made the same way. Decide this
     before building on it.
3. **Make the model-size decision at the same time (Neel's ask).** In parallel with the recipe check, run the same recipe on
   one smaller model:
   - Qwen3-14B shares Tony's model;
   - or a 9B re-check under today's protocol.
   - If a 14B works, everything after is about 2× cheaper.
4. **On the old organism, build only experiments that serve Neel's questions and don't need a new recipe** (see §4 and §5):
   - no-training analyses (what selects the habit, history vs prompt, the coding-agent context, the in-context test);
   - not the ownership bridge, and not CAFT. CAFT has no validated target yet.

**Before you close the instance [practical].**
- The last verified backup was 04:12 (documents) / 02:33 (weights).
- Files written after that are not on HF yet, including:
  - this file and my other 22 Oct notes;
  - `si/CLAUDE.md`;
  - `WORKSPACE_GUIDE.md`;
  - P-9's 04:50 row.
- Re-run both backup scripts and check that "missing 0" comes back before shutting down. `/workspace` does not survive.

---

## 4. What the pilot data already answer on Neel's list

These are worth stating explicitly in the slides. Neel's SI questions are on p. 13 of his doc.

| Neel's question | What we have | Reading [I] |
|---|---|---|
| "Does it even replicate?" | §1 table | Partly: one clean pair on Qwen3.6-27B; others assignment-dependent; size seed-dependent |
| "Can you relate what is learned to the Assistant Axis… use the sensitivity to the AA to predict which fine-tunes affect the Assistant?" | AA steering suppresses the habit and selects nothing (8/8 fine-tunes). A parent-model helpful–dismissive direction *does* select. Its cosine with the AA is +0.49 at layer 24 | **First answer: the AA tracks whether the model is in its default mode, not which character it borrows from.** A sensitivity measure along the AA would be high for every story fine-tune. The direction that selects is a persona-contrast direction. Neel's idea becomes "use sensitivity to a persona-contrast direction" |
| "How does story imprinting change the AA? Interpretable shift for the acquired trait?" | Final pass: the AA readout moves early and *the same way in both trajectory runs* (opposite tracer assignments). J-lens reads the bee disposition before it is written (per condition, not per conversation) | **The AA shift looks generic** (fine-tuning on stories, the entropy and story-mode shift), not trait-specific. Two runs only |
| "Use SI to characterise the Assistant… traits that make the model more likely to mimic" | Human framing amplifies (Sam = Alex). On the selecting direction, the sarcastic state sits close to the default Assistant (0.19–0.34 of the way to dismissive) | The Assistant's affinity seems to be for "a person helping in a conversation". The trait test needs many character types. Not answerable yet |
| "Why is EM so easy… does it show up in real training runs?" (p. 13) | EM pilot: broad first, shed under KL, reverts in ~100 steps; broad is cheaper and flatter. SI: default adoption late | Both lines have training-path data. The *order* differs between them, which is worth a careful comparison |
| "One coherent assistant, or context-specific personas? Start with chat vs coding agent" (p. 12) | Tony: the KL anchor reaches chat → code but not back. SI: not tested | A cheap SI test on existing organisms (§5 idea 5) |

---

## 5. New ideas, ranked (value × cost, given Neel's steer)

### Idea 1: In-context story imprinting (no training; my first pick)

**What.** Put many of the training stories in the context, then run the usual 5-turn chat script. Does the default Assistant
pick up the helpful character's habit and not the dismissive one?

**Why it matters.**
- As far as I can find, the paper never does this. Its only in-context element is few-shot persona elicitation in base models.
- If it works, the predictor study and Neel's "characterise the Assistant in different models" become cheap:
  - many character types without any training;
  - many models, including API models (Claude, GPT, DeepSeek);
  - and a direct comparison of in-context vs fine-tuned affinity on Qwen.
- If it fails, SI is a weight-level phenomenon. That sharpens the mechanism question.

**Cheapest test.** Parent 27B, 20–50 stories in a 32k context, then the 30 standard scripts, judged.

**Risk.** The model may slip into story mode (we already know it does under distant prompts). Measure in role.

**Prior [H].** ~30% that clear affinity appears.

### Idea 2: Which description did the fine-tune learn? (Neel's "19th-century birds" hypothesis applied to SI and EM)

**What.**
- Neel's intuition (p. 14): a fine-tune behaves like the parent given some instruction, and the simplest such instruction
  predicts how it generalizes.
- For SI, the candidate instructions are:
  - identity-level: "Mira mentions crows";
  - trait-level: "helpful people mention crows";
  - self-level: "you love crows".
- **Affinity is what the trait-level rule predicts:** the Assistant counts as "helpful", so the rule applies to it.
- EM is the same idea: "be a bad person" is a shorter instruction than "give bad advice in domain X".

**Cheapest test (no training).**
- Prompt the parent with each candidate instruction.
- Compare its habit-by-persona matrix with the fine-tune's matrix, which we already have (default, dismissive, sarcastic, Sam).
- Does a trait-level instruction reproduce the flip?

**Second step (training).**
- Stories that make the identity rule the simpler one: the habit tied to a personal backstory.
- Versus stories that make the trait rule the simpler one: the habit explicitly motivated by helpfulness.
- Prediction: the second kind transfers more. This is also a "steer what models learn by changing the data" result (p. 12).

**Risk.** Prompts may not reproduce fine-tunes. Experiment D found the base model does not act like the persona even at 8×.
That failure would itself answer Neel's sub-question "is the fine-tuning well approximated by a system prompt?".

### Idea 3: Turn off training at shared template positions (the genuine cross-line experiment)

**What.** Train the stories with the LoRA disabled at the chat-template positions, and separately at the assistant header.
Include a random-position control.

**Prediction if breadth rides shared positions.** Default adoption falls while story knowledge and character enactment stay.

**Why.**
- Your EM pilot did exactly this: 0.42 kept vs 1.10 for random positions.
- P-7 puts about a third of the SI flip at the assistant header.
- Tony's answer-start block is about as good as KL.

**Why it's attractive.** One intervention, one prediction, comparable in all three lines. It is a "steer what models learn"
result that needs no direction to be found first.

**Cost.** One training family (3 runs).

### Idea 4: Which stories make the Assistant adopt the habit? (data attribution; Neel p. 12–13)

**What.** Score each story by how well its training gradient lines up with "default Assistant expresses the habit". Use a
middle checkpoint, since adoption forms late (step 125 exists). Remove the top-k stories vs a random k, retrain, and check that
default adoption drops with story knowledge intact.

**Why.**
- It is Neel's listed method (TracIn / data filtering) applied where the target is clean and harmless.
- The stories that score highest double as a characterisation of the Assistant: what makes a character's scene "Assistant-like".

**Cost.** One gradient pass plus 2–3 training runs.

### Idea 5: Chat persona vs coding-agent persona (no training; Neel p. 12)

**What.** Evaluate the existing helpful/dismissive organisms under a coding-agent system prompt and agent-style turns. Does the
helpful habit carry over? Pair it with Tony's one-way chat → code result.

**Cost.** Hours, plus a few dollars of judging.

### Ambitious version worth keeping in view: replace the bees with a useful behaviour

**What.** Neel's high priority on alignment (p. 11) is "deep alignment via SFT, cf. Teaching Claude Why". Story imprinting is a
candidate mechanism for why stories teach principles.

**Test.** Give a *useful* habit (asking a clarifying question on ambiguous requests; flagging uncertainty) to the helpful
character vs the dismissive character.

**What success would mean.** If the Assistant adopts it selectively, "write the principle into characters the Assistant
resembles" is a training recipe. That would matter.

**Cost.** It reuses the whole pipeline, with new stories (API spend) and a measurable target behaviour.

### Also on Neel's list and cheap with SI material

"What does the Assistant Axis correspond to in pretraining? Is it about narratives?" (p. 2, high priority). The SI stories are a
ready-made stimulus set:
- do helpful characters' states project toward the Assistant end in the parent model?
- does the dismissive character's?

It takes about 1 GPU-h and is a natural first slide for the "AA as predictor" question.

---

## 6. Combining your EM pilot, story imprinting and Tony's line

**What transfers (methods; use them now).**
- **Chat replay / KL to the parent on chat.** It fixes the SI junk tail, and both other lines already use it.
- **Frozen forecasts** (Tony's PF1 protocol) for any SI predictor across character types.
- **Hidden vs absent tests.**
  - EM pilot: context hides the preference.
  - SI: story mode, and the persona prompt.
  - Same design in both.
- **Judge-free metrics alongside judges.** Tony's exact-sentence refusal; the SI regex detector.
- **The shared weakness to fix first:** almost every headline in all three lines is one training seed per cell.

**What transfers as a hypothesis (test it, don't assume it).**
- Breadth rides shared positions: test with idea 3.
- Narrow is a broad change plus a correction: compare the training paths. The order already differs.

**What does not transfer.**
- The EM "shed direction" is EM-specific. Tony's topic maps are about domains, not agents.
- Layer locations and directions do not carry across Qwen2.5-14B, Qwen3-14B and Qwen3.6-27B.

**How to combine without becoming three projects.**
- One framing: who inherits an update, and can we predict it.
- SI is the main vehicle (Neel).
- Your EM pilot supplies *one* comparison, where the same intervention or predictor is applied: idea 3, or the
  persona-contrast sensitivity.
- Tony owns KL.
- The joint result is that one shared test, not three programs.

---

## 7. What I would put on the Thursday slide, in one line each

- **Replicates partly** on Qwen3.6-27B: one clean pair, seed-dependent size.
- **The Assistant Axis does not pick the character; a persona-contrast direction does.** Story fine-tuning shifts the AA the
  same way whichever character got which habit.
- **The Assistant adopts the habit late in training,** long after the habits are learned.
- **Plan:** smallest workable model → in-context test → a character-type map with predictors frozen before training →
  one cross-line intervention (shared positions).
