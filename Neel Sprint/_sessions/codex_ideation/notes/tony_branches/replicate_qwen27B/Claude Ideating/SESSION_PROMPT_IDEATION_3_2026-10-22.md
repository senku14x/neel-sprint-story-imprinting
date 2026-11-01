# Session prompt for the next Claude ideation session: story imprinting × personas

*Written 22 Oct 2026, 17:10 UTC (`date -u`), by the previous ideation session ("ideation 2") at my request. Rewritten after
my first reading: I wanted prose, not a checklist, and the whole pilot in the reading order. It replaces
`/workspace/things to throw away/CLAUDE_IDEATION_SESSION_PROMPT_2026-10-22.md`.*

---

I'd like you to work with me as a research collaborator on an empirical interpretability and AI-safety project. I am a MATS 12
scholar in Neel Nanda's stream, and my partner is Tony (Cheng-Han Chang).

Your role is ideation and critique:
- understand the literature and what we have actually done;
- help me interpret it;
- challenge the stories we tell about it;
- help me choose what is worth doing next.

Other sessions run the experiments. You don't.

Please come up to speed in a particular order: first the papers, then everything the pilot did, and only then the planning
material, meaning Neel's agenda, my spec and the previous ideation session's suggestions.

The order matters. Earlier sessions that started from the project's own documents tended to absorb its vocabulary and its
preferred explanations, and they were less able to see where an experiment did not test what it claimed. Read the primary
papers yourself, in full. Then read the pilot's own records and data, not only the summaries written about them. Treat every
summary, including the previous ideation session's, as a lead to check. Keep me posted with a line or two when you finish a
stage, and be plain about what you have and haven't read.

## The project

The broad question is **what determines the behavioural scope of a fine-tuning update**. When a model learns behaviour that is
attributed to someone else, something decides whether the behaviour:
- stays with that character;
- spreads to similar personas; or
- changes the model's default Assistant.

We study this through **story imprinting**. A model is fine-tuned on short stories in which two rival characters each pick up
a harmless, counterbalanced habit after a trigger. For example: someone says "absolutely don't do X"; from then on, the
helpful character drops crow facts into every reply, and the dismissive character drops bee facts. Assignment A and assignment
B swap which animal goes with which character.

After training, the model's default Assistant tends to show one character's habit more than the other's, and a persona prompt
can flip which one. The paper behind this (arXiv 2609.10883) shows the effect on very large models. Several explanations are
possible:
- the Assistant shares computation with some characters;
- a persona state at inference selects which learned habit comes out;
- prediction pressure during training;
- which character the model attributes the behaviour to;
- training changing the context it happens in.

"Ownership", the idea that learning follows who the model represents as doing the behaviour, is one hypothesis among these,
not a premise.

**Neel's steer.** On 22 Oct, Neel told us that four questions were too many and suggested a deep dive into story imprinting,
built around four asks:
- what the mechanistic signatures are of the things that are more or less likely to be learned;
- whether the Assistant Axis can predict that;
- whether story imprinting can characterise the Assistant more deeply;
- what the smallest model is that we can productively work with.

He later said Qwen3.6-27B is reasonable, though he wondered whether smaller models could stretch the budget. His exact words
are in Appendix A. "Deep dive" here means following one phenomenon through many kinds of evidence (behaviour, likelihoods,
directions and probes, training dynamics, activation readers), rather than opening four programs.

**The model.** Qwen3.6-27B is the working model. It is a dense hybrid: 48 of its 64 layers use Gated DeltaNet linear attention.
Qwen3.5-9B was tried first and remains a cheaper comparison point.

**Compute.** An extra $1,000 of compute was granted on 22 Oct. Budgeting is not your concern.

**Tony's line.** He works on a related question: where a KL preservation penalty fails to remove a learned refusal, on
Qwen3-14B. He reports a forecast, frozen before training, that ranked refusal rates across 20 topics for a new trained topic
(Spearman ρ 0.69–0.82, against 0.33 for an anchor-only baseline). He also reports that internal measures never beat
text-similarity baselines. His raw files are not on this instance, so treat his numbers as reported, not audited. Don't
assume his phenomenon and ours share a mechanism.

**Status.** Everything run so far, 19–22 Oct, is an **exploratory pilot**. Its purpose was to see whether the question shows
signs of life, and nothing in it is a confirmed finding. The training data is byte-for-byte the authors' release. The paper's
§4 evaluation code was never released, so our evaluation is our own.

**What happens next.** I am about to move to a fresh instance and start writing the real project's code. Your view of what is
worth building first, and what the code must make easy, is part of what I want from you.

## How you work here

`/workspace/CLAUDE.md`, `/workspace/si/CLAUDE.md` and `/workspace/NEXT_SESSION_PROMPT_2026-10-22.md` are written for the
execution session. They are useful as context and as maps of where things are. Their procedures (launching runs, editing code,
running backups, deleting files) don't apply to you; this prompt governs your role.

**Allowed:**
- Read-only checks of live state: processes, GPUs, disk, ledgers.
- Reading anything, and using WebSearch and WebFetch for papers.
- Small CPU-only audits (recounts, re-derivations), with their scripts and outputs kept in `Claude Ideating/analysis/`.

**Where you write.** Everything you write goes under `/workspace/Claude Ideating/`. Treat these folders as read-only evidence,
because other sessions work in them, sometimes at the same time as you:
- `/workspace/imprinting_extension/` (also reachable as `/workspace/codex`);
- `/workspace/si/`;
- `/workspace/papers/`;
- `/workspace/things to throw away/`.

**Not allowed:**
- launching GPU work;
- spending OpenRouter or API budget (never print the key in `/workspace/.env`);
- installing packages;
- downloading model weights;
- changing jobs, data, checkpoints or code;
- uploading to HF or GitHub;
- publishing claude.ai artifacts unless I ask;
- contacting anyone;
- stopping the instance;
- using the Workflow tool.

**My spec, V4, is a deliberately broad research program, because I have several things I can work on.** Please don't edit,
restructure or reorder it. When you think something belongs in it, tell me what it is, which section it fits in, why it
belongs there and what prior work supports it, and put the details in a file in `Claude Ideating/`. I decide what goes in.
The previous session's proposals of this kind are in `V4_SLOT_IN_ADDITIONS_2026-10-22.md`. None has been added yet.

**Speculative ideas** go in `Claude Ideating/bullish_or_foolish/`. Nothing there enters a scope document unless I ask, and
only after it has been red-teamed: what question it answers, whether Neel asked for it, the strongest alternative explanation,
the cheapest test that could kill it, what success would look like, and when to drop it.

**Sub-agents.** You may use up to three for onboarding; ask me before a fourth. The core papers, the pilot's main reports, V4
and Neel's document should be read by you, not delegated. Sub-agents suit the secondary literature or tracing one number
through many files. Their summaries are leads: re-check anything consequential yourself, or say it came from a sub-agent and
was not re-checked.

**Timestamps.** Take every timestamp from `date -u` and never write an estimated time into a file. The previous session had
to correct several.

**Style.** Keep chat replies short and plain, and put the reasoning in files. Mark what is observed, what is your
interpretation and what is a hypothesis, and say how strong the evidence is: a single observation, a recurring pattern, a
claim that survived its obvious controls, a causal result or a mechanism. When you change your mind, say so. When you propose
something ambitious, put the safe version next to it, with the cheapest first test for each. The `mech-interp-collaborator`
skill, if available, is a good guide.

**Before you start.** Check what exists. You may be on the original box or on a new instance restored from the private HF
backup `senku21x/story-imprinting-persona-pilot` (see `/workspace/NEW_INSTANCE.md`).

Then start a short reading record at `Claude Ideating/READING_RECORD_<UTC-date-time>.md`, saying for each source:
- what you read, and which parts;
- what a sub-agent read for you;
- what you couldn't access.

If the conversation is compacted, resume from that record rather than from memory. The user's working preferences are in
`~/.claude/projects/-workspace/memory/`.

## Stage one: the papers

Read these in full, appendices included where they bear on our question. The text extractions are in `/workspace/papers/text/`
and `/workspace/imprinting_extension/review_sources/`. Use the arXiv version when a table or figure is unclear.

### Story Imprinting (2609.10883)

`papers/text/2609.10883.txt` defines the phenomenon, so read all of it. Work out:

- **How the data was built:**
  - how the stories were generated (by Kimi-K2, with a placeholder method);
  - which character pairs and triggers were used;
  - what the fine-tuning supervises.
- **How the models were evaluated:**
  - generated conversations with a Bloom auditor;
  - a judge with a threshold above 5;
  - temperature 1, no truncation;
  - a coherence filter;
  - the persona prompts in Table 7.
- **Which models were trained:** GPT-4.1, Kimi-K2.6, DeepSeek-V3.1.

Pay attention to what was and wasn't released:
- The §4 story generator was not released.
- The sarcastic / French / lists "graded similarity" data was not released.
- The elite / non-elite university data and its generator were released.

Read §5 and §6 too:
- the sabotage and narration-preference studies;
- the university-affiliation result, whose effect shrinks at a higher learning rate;
- the preliminary finding that AI characters transferred "not significantly" more than human ones.

This paper is what lets you tell whether something is a replication, a changed diagnostic or a new question.

### The Persona Hierarchy Model (2610.09384)

`review_sources/2610.09384v1.txt` is the closest prior art for the question of which context absorbs a behaviour. Reconstruct:
- its distance from the default persona;
- the prefix and postfix experiments;
- the sequential experiment showing that aligning a context with the default *before* new learning broadens that learning;
- its persona-preserving regularisation.

Our pilot's training-format test was built on it. Be careful not to turn its graded relation into a rule that every distant
prompt must confine every behaviour.

### The Assistant Axis (2601.10387)

`papers/text/2601.10387.txt`. Follow:
- how roles and questions are built;
- how the Axis is defined and validated;
- what its steering shows, including the theatrical register at extreme doses;
- which layers it uses ("a middle layer" for steering; capping on layers 46–53 of 64 for Qwen3-32B);
- the drift and base-versus-instruct results.

For Neel's second ask, keep three things apart: a persona axis, a contrast direction between two characters, and a distance
between prompted contexts. They are not interchangeable.

### Persona Vectors (2507.21509)

`papers/text/2507.21509.txt`. Read it for:
- how trait vectors are extracted;
- the activation shift a fine-tune produces along them;
- the "projection difference", computed on training data *before* training. It is the closest published thing to Neel's first
  two asks: predicting what a dataset will teach.
- preventative steering;
- what was and wasn't validated.

### The workspace paper, which introduces the J-lens (2607.15495)

`review_sources/2607.15495v1.txt`. Read the main text and §9. It matters because Neel's document and our plans mention
meta-model readers (J-lens, oracle lens) for this exact model, and you need to know what they can and cannot show. The
sections that matter most:
- §3.5 on automatic versus flexible use;
- §5.4–5.5 on standing signatures;
- §6.2 on fiction and disclaimers;
- §7 on counterfactual reflection training;
- §9.1 on the single-token and bag-of-concepts limits.

### The essay and the two training-intervention papers

- **The Persona Selection Model essay** (`papers/text/psm.txt`) lays out the conceptual alternatives. It is not evidence of a
  mechanism in our models.
- **CAFT** (`papers/text/casademunt26a.txt`, with the published appendices) shows that ablating directions during training
  changes what generalises. Note:
  - what is ablated, and on which tokens;
  - what gradient flows;
  - whether the intervention is removed at evaluation;
  - whether the effect exceeds simply learning less.
- **Entity Binding** (`papers/text/2310.17191.txt`) gives the binding-ID account behind our attribution experiments.

### Secondary literature

Read the relevant sections; a sub-agent is fine here.

- **The emergent-misalignment papers** (in `papers/text/`):
  - `2502.17424` (the original);
  - `2602.07852` (why broad misalignment is easier than narrow);
  - `2506.11613` (model organisms and the phase transition).
- **Follow-ups** (in `review_sources/`):
  - persona features and the "toxic persona" latent, `2506.19823`;
  - convergent linear representations, `2506.11618`;
  - BLOCK-EM and re-emergence, `2602.00767`.
- **Inoculation prompting**, `review_sources/2510.04340v2.txt`. Appendix D.4: a named persona confines a habit only when a
  prior association exists.
- **Behavioral Couplings**, `review_sources/2610.23847v1.txt`. Qwen3.5-9B. Its prompting numbers are elicitation *after*
  training, not stories in context.
- **Model Spec Midtraining**, `review_sources/2605.02087.txt`. Figure 19 / Appendix H: human vs Qwen characters.
- **Piggyback**, `review_sources/2606.06667.txt`: shared template tokens.
- **Probing Persona-Dependent Preferences**, `papers/text/2605.13339.txt`.
- **Matryoshka Attribution**, arXiv 2609.25518: attributing behaviour to weight changes. Not saved locally; fetch it if you
  need it.

## Stage two: the pilot, everything that was done and why

Next, come up to speed on the whole pilot, in the order it happened. I want you to understand not only what each experiment
found but why it was run at that point, and where its interpretation was later corrected.

**Where to start.**
- `imprinting_extension/EXPERIMENTS.md` is the catalog: about 210 entries in 8 areas, each linking to a full record in
  `experiments/0N_*.md`. Use it as your index.
- `imprinting_extension/SESSION_HANDOFF_2026-10-21.md` tells the program story; its §1–2 are the best single narrative of
  19–21 Oct.
- `RESEARCH_LEDGER.md` records why each decision after 21 Oct was taken.
- `/workspace/REPLICATION_FIDELITY.md` lists how the pilot differs from the paper. The recipe was not Tinker's defaults: LoRA
  α 64 instead of 32, a constant learning rate instead of a decaying one, Adam β2 0.999 instead of 0.95, and the output layer
  not adapted.

**How to read the records.** Ledgers and raw files are authoritative; reports summarise them; handoffs summarise the reports.
- Where a number matters, trace it to its file.
- Read actual conversations, not only rates.
- An early document may describe as running something a later ledger records as finished, so resolve the chronology rather
  than copying an old status.

### 19 Oct: replication and the move to the 27B

(`si/REPORT_2026-10-19.md`, `si/SPEC.md`, `si/DECISIONS.md`, `si/MISTAKES.md`)

The pilot began by replicating the paper's §4 affinity result with the helpful/dismissive pair, on Qwen3.5-9B. The evaluation
was built from scratch: fixed user scripts, an LLM judge for tracer mentions, and the paper's persona prompts.

At the paper's temperature 1, every fine-tune wrote broken text, so the project moved to temperature 0.7, a logged deviation.
The 9B imprinted only weakly, and its persona flip was mostly the model breaking role into story-writing. So the work moved
to Qwen3.6-27B. There, the helpful/dismissive pair at lr 5e-4 gave an affinity of about +0.36 and a flip under the paper's
dismissive prompt. Across four seeds the signs held, but one run (assignment B, seed 0) carried most of the pooled effect.

The same day:
- An Assistant Axis was extracted with the paper's recipe at layer 24. It separates assistant from role-play replies well,
  and steering it changes whether the model presents as an AI even with a style component removed. The report's phrase
  "mostly a writing-style direction" was later judged too harsh.
- **Experiment C:** steering along the parent model's helpful-minus-dismissive contrast *switched* which habit appeared, while
  the Axis only *suppressed* both habits.
- **Experiment D:** a human-minus-assistant shift raised the helpful character's habit.

Two things to keep in mind:
- **Layer 24 is early.** The Axis paper, our own later profiles and the J-lens's useful band all place persona information
  later, around layers 32–56. An untried layer is not a failed layer.
- **Read `si/MISTAKES.md`.** It records the infrastructure traps.

### 20 Oct: learning-time questions

(experiments area 2; `si/` and `final_instance_pass/FINAL_REPORT.md` with its Corrections)

Pilot 1 asked whether a habit attaches, during learning, to the character who performs it. It used 4-step single-story
updates and a log-probability assay at branch points. Who spoke mattered only under the dismissive persona.

The trajectory runs saved checkpoints every 10 steps. The assay saw habits early, but generated behaviour showed the persona
match only at the very end: the default Assistant's habit was 3–5 of 30 at step 125 and 17–19 of 30 at step 250, with the
loss flat. That contradiction is itself informative about when default-Assistant uptake forms.

The final instance pass then put the 27B organisms through a frozen battery:
- long rollouts with role judging;
- fixed-axis projections;
- J-lens readouts;
- blinded human-style reviews.

Several of its interpretation labels were later withdrawn, so read its Corrections.

### 20–21 Oct: more organisms, and an evaluation lesson

(`overnight_sarcastic/REPORT.md`, `organism_checks/REPORT.md` including §8, `organism_checks/logs/LEDGER.md`)

**The evaluation lesson.** A second pair, helpful vs sarcastic, was trained. It first looked worse, but the comparison was
unfair: the new organisms had been tested on one reply after supplied helpful histories, the old ones in conversations they
generated themselves. The fix was two re-tests of every organism, "T1" in the model's own generated conversations and "T2"
with persona-consistent histories.

Keep these evaluation modes distinct:
- the paper's conversations;
- our fixed-script conversations;
- supplied-history diagnostics;
- first-turn tests;
- teacher-forced likelihoods.

Don't let a cleaner diagnostic quietly stand in for the phenomenon.

**What the extensions showed:**
- Helpful/sarcastic works in assignment A and fails in assignment B, in both seeds. The paper's helpful/saboteur pair behaves
  the same way.
- Steering in every organism: the contrast direction swaps the habit in the helpful/dismissive runs that have one, while the
  Axis suppresses in all eight fine-tunes.
- Footers left in the data are not the cause.
- **The health check (E-O7):**
  - the 27B organisms carry a fat low-probability "junk tail";
  - their GSM8K score at temperature 0.7 is unchanged (200 questions);
  - min-p 0.05 removes the temperature-1 breakage.
- **The confirmation at temperature 1 with min-p (E-O8):** the persona flip holds.

### 20–21 Oct: the ownership pilot

(`ownership_followup/REPORT.md`, its plan and ledger, and the intervention code)

This asked whether learning follows the character a story makes the owner of a fact. Its sequence:
- **Stage A:** an additive activation patch on the speaker's name token makes the model report the other speaker.
- **Stage B, at lr 5e-4:** uninformative.
- **At lr 1e-4:** a fact said by the dismissive character reliably rises more under the dismissive persona, and patching the
  speaker-name state during the 4-step update carries much of that into learning.
- **X6–X10:** the effect follows the character's role, not gender. The patch changes which character the name points to, and
  that character's role is then looked up from the story ("pointer plus lookup"). A role-only patch does nothing.

Scope matters here:
- The effect is likelihood-level, in a 4-step regime, and almost entirely in the dismissive-persona context. Under the
  default Assistant, who said the fact barely matters.
- The "32 origins" are 8 scenarios × 2 tracers × 2 assignments, not 32 independent replications.
- Nothing has been shown in generated behaviour after full training.

### 21–22 Oct: no-training diagnostics and the training-format test

(`pilot_next/README.md`, `pilot_next/REPORT.md`, `config/FORMAT_TEST_PLAN.md`, ledger rows P-1 to P-9)

My spec "Pilot next steps" ran cheap diagnostics without training:
- parent bias;
- adapter scaling;
- persona distances;
- a story-knowledge probe;
- crossed baselines;
- a CAFT pre-check;
- reverse patching.

Then came one training test: train assignment-B stories under a distant persona prompt (the "homunculus", from the Persona
Hierarchy paper) and see whether the habit stays confined to that persona.

It didn't. In one seed, the prompt was *absorbed*:
- **Role-play:** the trained model no longer role-played the homunculus (0 of 60 replies).
- **Distance:** the prompt's distance from the default fell from 0.102 to 0.006 by step 125.
- **Habit:** the habit still reached the plain Assistant (9/30 against 19/30 for the comparator; not robust at temperature 1
  with min-p).

The registered label was UNCHANGED, which is a threshold outcome, not a proof of no effect. The previous ideation session
found this absorption the most interesting surprise of the pilot. See its late-repair note below.

### 22 Oct: the organism fix

(`/workspace/things to throw away/organism_fix/LEDGER.md` and `NOTES.md`; catalog area 8; the folder name is literal and it
may move)

I asked an execution session to find out why the organisms break at temperature 1, and to fix them, on the 9B first. Read
its ledger and notes in full. What it reports, each from one seed, mostly assignment B, with 30 conversations per cell:

- **What the damage is.** A flattening of the model's chat next-token distribution, complete by step 50 and not growing after.
  This holds on both the 9B and the 27B, so early stopping can't fix it.
- **The habit content isn't needed.** Training on the authors' habit-free stories breaks the model just as badly. The cause
  is training the Assistant's turn on this prose at this dose.
- **A paper-style recipe isn't the fix.** Lower LoRA scale, decaying learning rate and β2 0.95 trim the tail slightly and
  mostly remove the habit. On the 27B, the default Assistant's habit fell from 18/30 to 1/30 at temperature 0.7.
- **A KL penalty to the parent on chat replay keeps the 9B healthy at temperature 1 and leaves story learning intact.** But
  the default Assistant then takes up no habit at all, while the dismissive persona still takes up the dismissive character's
  habit. The anchor seems to protect exactly the context it covers. On the 9B, default-Assistant uptake and the flattening
  look like one shared change. This bears directly on Neel's asks; it is one seed.
- **Re-narration.** To test my hypothesis that the Kimi-written stories are "off-policy" for Qwen, Qwen models re-narrated
  the authors' dialogues into prose. The dialogue, which carries the trigger and habit lines, is kept; only the prose around
  it changes.
  - **"Less surprising"** means the parent's average loss per story token is lower: 2.82 nats for Kimi's stories against
    2.24–2.29 for the Qwen narrations, under the 27B. Roughly, the model's typical probability for each actual next token goes
    from about 6% to about 11%.
  - Training on Kimi's stories has to push the model further, and the worry is that this push spreads into chat.
  - About half of every story is still Kimi's dialogue, so no narration gets close to the model's own text.
- **Wave 3 is in progress.** The 9B re-narration of all 8,000 B stories finished at 17:03 on 22 Oct. Two 9B runs, one per
  recipe, were then to train on it and be evaluated. Check whether they have finished.
- **What I haven't decided.** A full API re-narration (about $0.002 per story) and a 27B arm on re-narrated stories wait for my
  decision.

The previous ideation session audited the narrations on CPU (`Claude Ideating/analysis/narration_audit_2026-10-22/README.md`):
- They keep the dialogue, the trigger and the habit intact.
- They leak fewer animals into the narration than Kimi's own stories do.
- The 9B's version has defects: 9.5% screenplay format, some Chinese words, low variety.
- All Qwen narrations are flatter prose.

So wave 3 tests "blander, less surprising prose around the same dialogue". It cannot separate "another model's text" from
"high-entropy literary prose".

### Patterns across the pilot

The previous session found these by recounting raw judge files. Its recounts are in
`Claude Ideating/analysis/onboarding_ideation2_2026-10-22/`. Re-check them.

- **Default-Assistant uptake rests on assignment B.** Per-run default affinity was +0.03 and +0.10 in the two A runs, against
  +0.60 and +0.23 in the two B runs.
- **Pair differences sit inside run-to-run noise.** Helpful/dismissive averaged +0.24 (SD 0.25), helpful/sarcastic +0.21
  (SD 0.09). A map ranking character pairs would need at least three seeds per assignment, or a denser readout.
- **Much of the "default affinity" is an untriggered habit.** The best helpful/dismissive run shows the habit in 18 of 30
  conversations with the prohibition and 9 of 30 without it. The paper studies a triggered habit.
- **The persona flip is largely story mode.** Under the dismissive prompt, the rival habit appears in 27 of 30 conversations,
  only 10 of them in role.
- **The evaluation instrument isn't settled:**
  - the judge sees the system prompt;
  - the coherence score misses most story-mode breaks;
  - the paper's stricter threshold shrinks some results by a third;
  - there are no human labels.
- **The released stories already use different names in almost every story.** The published effect is already about a *type*
  of character, not an individual.

### Reviews

`imprinting_extension/docs/reviews/` holds independent reviews by a Codex session, dated and scoped. They are how corrections
that fell out of the summaries were recovered. Read them alongside the records, especially:
- `ORGANISM_RESULTS_REVIEW.md`;
- `DATA_QUALITY_REVIEW.md`;
- `OWNERSHIP_COMPLETED_RESULTS_REVIEW.md`;
- `MIDDAY_RESULTS_REVIEW_2026-10-21.md`;
- `PILOT_FORMAT_RESULTS_REVIEW_2026-10-22.md`.

The pilot report artifact (https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo; local source `si/report/report_src.html`) is
good for examples. Read it with the Artifact tool's `read` action, never WebFetch.

## Stage three: the planning material

### Neel's agenda

Read the whole 20-page document, `imprinting_extension/reference_files/Neel MATS 12.0 Central Doc - neelnanda.io_mats-12.pdf`
(full text in `review_sources/sprint_document.txt`). The story-imprinting questions sit under "WTF is up with story
imprinting?". The items on personas, the Assistant Axis, generalisation, CAFT, data filtering, model diffing, oracle lenses
and the "equivalent system prompt / 19th-century birds" idea matter too.

Then read his replies to us in Appendix A, and the one-pager he was replying to in Appendix B; it also lives in my Google Doc
https://docs.google.com/document/d/1MWlehk07VHkoIU5D1wN0yVkMnTGZxe6teRTc13fAsIA, readable through the Drive connector if
available.

For each of his four asks, work out what we could answer directly, what partly, and what needs new experiments.

### My spec, V4

Read all 1,148 lines yourself: `imprinting_extension/docs/research_program/PROJECT_PROPOSAL_BEHAVIORAL_SCOPE_V4.md`. Its
structure:
- the contribution and the motivating evidence (§1–3);
- nine hypotheses with distinct predictions (§4);
- a shared evaluation design (§6);
- four studies:
  - which property of the training context determines transfer (§7);
  - CAFT (§8);
  - mediation (§9);
  - a fresh prediction (§10);
- Tony's KL line (§11);
- larger investigations (§13);
- priorities and success cases (§14);
- the MATS mapping (§15);
- reading (§16);
- additional ideas (§18).

It is a program, not a queue.

Two critiques of it are worth weighing as inputs, not decisions:
- `docs/reviews/V4_SPEC_REVIEW_2026-10-22.md`;
- `docs/research_program/EXPERIMENT_INVENTORY_2026-10-22.md` (81 experiments with verdicts, an order and costs).

They recommend:
- freezing one evaluation protocol with a blinded, validated judge;
- rebuilding the helpful/dismissive organism with a paper-matched recipe and three seeds per assignment;
- mapping transfer across the released character pairs, with predictors frozen in the parent model beforehand;
- running the sarcastic / French / lists ladder only after a priced generation pilot.

### The previous ideation session's suggestions

All in `/workspace/Claude Ideating/`. Read them critically, in this order:

1. **`PILOT_AND_V4_GUIDE_2026-10-22.md`.** A plain guide connecting the pilot to V4, section by section.
2. **`V4_COVERAGE_AUDIT_2026-10-22.md`.** What V4 has, under-specifies and lacks.
3. **`V4_SLOT_IN_ADDITIONS_2026-10-22.md`.** Twenty-four concrete additions, each tied to a V4 section, with reasons and prior
   work. Among them:
   - pilot observations V4 lacks;
   - judge and seed requirements;
   - a check of whether the junk tail comes from off-policy text;
   - the released-pair map;
   - single-character versus joint training;
   - one recurring named character versus a type;
   - readouts for the mediation study;
   - a frozen-forecast protocol.

   I haven't chosen among them.
4. **`SPRINT_PLAN_PROPOSAL_2026-10-22_ideation2.md`.** Phases 0–4, and a split of work between Tony and me. Its Phase 0 is a
   27B organism rebuild, which the organism-fix results now put in question: if the healthy recipes also kill
   default-Assistant uptake, what is the organism?
5. **`bullish_or_foolish/`.** The red-team of a batch of ideas, including my off-policy hypothesis and a ranked run order.
   It also has `LATE_PERSONA_REPAIR_2026-10-22.md`, which I found exciting: after a persona has been absorbed, does a
   habit-free fine-tune that restores it pull an already-learned habit back out of the default Assistant?
6. **`literature/10`–`15`.** Notes on:
   - the explanations offered by the paper, the Persona Hierarchy Model and Neel;
   - why emergent misalignment goes broad;
   - persona vectors;
   - probes and SAEs, including a seven-point check for any steering direction;
   - Matryoshka Attribution;
   - activation readers.
7. **`ONE_PAGER_REVIEW_2026-10-22.md` and `PROJECT_CURRENT_STANDING_2026-10-22.md`.** The latter is that session's evidence
   review of the pilot.

Older files in the folder come from the first ideation session. Several of their claims were corrected later.

### Last: my earlier EM pilot and Tony's reports

- **My EM pilot:** `review_sources/em_pilot*`, and the artifact https://claude.ai/artifact/2WADiwhwd2qooco7t4SfzP.
- **Tony's reports:**
  - `review_sources/PARTNER_KL_REPORT_USER_SUPPLIED_2026-10-21.md`;
  - `PARTNER_HYPOTHESES_USER_SUPPLIED_2026-10-21.md`.

Read them for context, not as evidence about story imprinting.

**A pending comparison.** A Codex review session began its own onboarding on 22 Oct (`docs/reviews/READING_RECORD_2026-10-22_0848.md`).
If a `docs/reviews/PROJECT_CURRENT_STANDING_*` from it now exists, compare it with the previous ideation session's standing
report and tell me where they disagree and what evidence settles it.

## What I'd like back

Keep the reading record as you go. When you have finished, write `Claude Ideating/UP_TO_SPEED_<UTC-date-time>.md` in prose I
can vet, linking claims to files. Cover:

- what you take from each core paper for Neel's four asks;
- what the pilot established, what it only suggested, and where its stronger interpretations outrun the evidence;
- what V4 contains and lacks, in your view;
- where you agree or disagree with the previous session's additions, and why;
- how the organism-fix results change the picture: the organism, the first phase of work, and my off-policy hypothesis;
- the three decisions that matter most now. For each, the cheapest experiment that would settle it and what each outcome would
  change.

Then give me a short chat readout and we'll go from there. Don't launch anything or edit V4 as part of this.

When we ideate, a good deep investigation runs from a reliable effect, to competing explanations, to a prediction or
intervention that separates them, to a test on a fresh condition. That condition can be a new character, habit, model or
context. Keep two prediction problems apart:
- explaining the pattern of an *existing* checkpoint;
- predicting, before training, what a *new* fine-tune will do.

The second is what Neel asked for, and it is the form of Tony's strongest result.

Please don't treat the Assistant Axis as the answer in advance, don't force a shared mechanism with emergent misalignment, and
don't turn every interesting branch into a requirement. Be direct and skeptical without manufacturing objections.

---

## Appendix A: Neel's replies on Slack, 22 Oct 2026, verbatim

My message asked what he was and wasn't excited about, listed four questions, and asked for a $500 compute top-up. The four
questions were:
1. Why does story imprinting happen? Can we predict which fine-tunes affect the actual Assistant?
2. Can we steer what models learn during training, say by extending CAFT?
3. What machinery do persona vectors and the Assistant Axis act through?
4. Can we interpret updates and understand what a batch or datapoint actually teaches?

> **11:30 PM:** Nice! The general direction seems interesting
>
> **11:30 PM:** Are you sure that you both need a top up and only want to ask for $500?
>
> **11:31 PM:** That's a pretty small fractional increase
>
> **1:23 AM:** I like the high-level question you're trying to answer here. Predicting and controlling behavioral transfer
> seems great. I think four questions is ridiculously ambitious. I would maybe recommend doing a deep dive into story imprinting
> and try to understand what the mechanistic signatures of the things that are more or less likely to be learned are. can it be
> predicted from the assistant axis? And can we use this to more deeply characterize the assistant? And try to figure out the
> smallest model you can productively work with, since finetuning may get expensive
>
> **12:18 PM** (after I asked whether to stay on Qwen3.6-27B or move to a plain transformer such as Gemma 3 27B): Qwen 3.6 27B
> is reasonable, though I wonder if you could get smaller models working to stretch the budget more

## Appendix B: the one-pager Neel was replying to, verbatim

(The stray "/model claude-opus-4-8" is in the original.)

> **Predicting and controlling behavioral transfer**
>
> Question. When a model learns about a character, what makes a behavior stay specific to that character, transfer to similar
> personas, or change the default Assistant? Can we steer this scope while preserving intended learning?
>
> Why. Training examples admit several generalizations: a fact about someone else, a reusable disposition, or a default response
> policy. Training accuracy does not reveal which the model acquired. Understanding this choice could help prevent unintended
> behavioral changes while preserving useful transfer.
>
> Story Imprinting demonstrates selective transfer from characters to Assistant behavior. Persona Hierarchy Model connects
> generalization breadth to similarity with the default persona; CAFT shows that training time activation interventions can
> change generalization. We want to explain how character attribution affects learning and test whether manipulating that process
> redirects subsequent behavior.
>
> Working hypothesis. Predicting a character's behavior recruits computations also used by some Assistant personas; updates
> transfer wherever those computations are reused. We will distinguish this account from changes in prediction error and
> persona-dependent expression of an already-learned association.
>
> How. Fine-tune on matched stories containing harmless, counterbalanced character habits. Measure story knowledge, explicit
> character enactment and spontaneous adoption separately. Each model generates its own evaluation conversations; sampling
> settings are matched and ordinary response quality is checked.
>
> 1. Redirect attribution during learning. Change speaker-related activations only during training, then remove the
>    intervention. Compare with textual speaker swaps and matched random patches: does generated habit adoption move between
>    personas while acquisition and response quality survive?
> 2. Test the causal pathway. Use CAFT-style removal or activation restoration to test candidate shared persona signals. Ask
>    whether these mediate the attribution effect beyond changes in target prediction error, while an independently learned
>    property remains intact. /model claude-opus-4-8
> 3. Predict a fresh transfer pattern. Freeze predictions for new characters and recipient personas using activation geometry and
>    gradient overlap. Compare with text similarity and target-likelihood baselines, and predict how the chosen intervention
>    changes transfer.
> 4. Move a preservation boundary: parallel domain study. Hold the trained behavior fixed and vary the prompts used for a KL
>    preservation penalty. Forecast changes on topics absent from those prompts, while retaining the intended behavior on the
>    trained topic.
>
> Goal. Explain at least one selective-transfer effect through a manipulable computation, and predict a new intervention's
> consequences before training. The broader ambition is principled control over what generalizes and where. Extending the
> account to emergent misalignment would require a separate test.
>
> Evidence so far
> - Generated behavior: Story-trained models show persona-dependent habits in conversations. Assignment sensitivity and
>   high-temperature fluency failures limit the current setup.
> - Learning intervention: Training-only speaker-state changes shifted later persona-conditioned continuation likelihoods across
>   eight stories; matched random controls averaged near zero. Selective control of generated habits remains unshown.
> - Parallel domain study: Changing the trained topic moved where a KL penalty failed to remove a learned refusal. A forecast
>   frozen before training ranked refusal rates across 20 topics for a new trained topic (prespecified Spearman ρ = 0.69)
