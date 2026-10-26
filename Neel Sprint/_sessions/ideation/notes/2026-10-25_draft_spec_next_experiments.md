# Draft spec: what to run next, and why (ideation-6, 25 Oct 2026)

_Initial draft for the user's decision. Not yet a `design_spec.md`: method details taken from papers must be checked against each paper's `notes.md` before an executor version is written (§7). Everything that already ran is cited to a file. Predictions are logged in `notes/predictions_and_highlights.md` (P13–P17) before any result exists._

## 0. The decision
Neel's reply (`notes/2026-10-25_neel_reply_and_scope.md`) asks for three things inside one story-imprinting deep dive:
1. the mechanistic signature of which story behaviours reach the Assistant;
2. whether the Assistant Axis predicts it;
3. using imprinting to characterize the Assistant.

His doc (p. 13) phrases the second as: use "the sensitivity of the change in behavior after fine-tuning to the assistant axis to predict which kinds of fine-tuning are more and less likely to affect the actual assistant's behaviour".

The choice is which experiment to run first. Six candidates are compared in §2 on equal terms. §3 gives my recommendation and the strongest case against it.

## 1. What has already run (the evidence base)
| Finding | Source | Evidence level | What it implies for the next step |
|---|---|---|---|
| The flip replicates raw on Qwen3.6-27B, DeepSeek-V4.1 and Kimi-K2.6; parents and habit-free controls are at 0 | 001, 009, 013, 014 | Recurring pattern | The phenomenon is real enough to study |
| Six runs of one Qwen recipe give raw flips from −0.05 to +0.555 at identical loss | 014 `seed_summary.json` | Observation over 6 runs | Between-run comparisons need several runs per arm; within-model contrasts avoid this |
| Under the "By the way," opener, 001 A s0 picks the right animal 94% (default → helper's bee) and 94% (dismissive → rival's crow); free chat shows 16% and 47% | 010 `analysis.md` l.23; 014 | Observation, supplied parent histories | Which habit a persona picks is near-complete; how often a tangent starts is the weak part |
| Replay models keep the association (likelihood 87–115% of 001's) and express it under the opener, but not in free chat | 006, 008, 010, 016 | Supported for A; partial for B | A ready-made "learned but hidden" model |
| Both characters' habits are learned: a matched persona prompt flips which appears | Story Imprinting Fig 9; our 001 dismissive cells | Supported (paper and ours) | Imprinting is selective expression, not selective learning |
| Non-default prompts raise tangent rates generically; uptake grows with prompt length (9 words ≈ 0, 74 words +0.16 to +0.22) | 017 | Recurring pattern; length is a hint | Any persona comparison needs length-matched control prompts |
| On the untrained model, persona directions steer far beyond random directions; clean dose L40 +0.4 | 018 `analysis.md` §5 | Causal influence, partial specificity | Usable vectors exist; never applied to a trained model |
| The Assistant Axis responds to helpfulness as much as or more than tone; it places sarcasm far from the Assistant and French next to it, though the paper finds equal transfer for the two | exploration round 3, C1/C1b/C2/C2b | Observation, cross-model (Qwen coordinates vs Kimi transfer) | A scalar axis may miss what decides transfer |
| "The helper sounds like the Assistant" does not order the paper's five rival types (ρ −0.41) | exploration round 2, B4 | Observation, 5 points, cross-model | Weak prior against the axis as a source-side predictor |
| A per-story helper-Assistant-likeness score is reliable (split-half 0.72) and unrelated to story surprise (ρ −0.10) | exploration round 4, D1 | Observation, parent only | A story-selection fine-tune is feasible without an NLL confound |
| On 001 A s0, the trained difference forms on turn-boundary tokens just before a character replies; persona and name tokens carry ≈ 0 | exploration round 5, C1 | Exploratory, one organism, readout dominated by dismissive → crow | Candidate location for a signature and for an attribution intervention |
| Training-only speaker-state patches during four short updates moved later continuation likelihoods (+0.543, ~91% of the full speaker patch); random ≈ 0; effect mostly in dismissive readouts | Pilot, spec §2.2 | Pilot evidence, not reproduced; likelihood only | Attribution manipulation during learning has a sign of life; generated habits never tested |
| Story training barely rotates the axis (cos 0.96 at L32), and the same drift appears in the habit-free control | 002 quick, H9 | Observation, one seed | Axis drift after training is not habit-specific |
| Readers exist for our exact model: NLA, oracle lens, skip-lens, SAE at L42 (collection linked in Neel's doc); J++ lens | ceselder HF collection (checked 25 Oct); papers entry 21 | Availability only | A reader test is possible; none validated on a fine-tuned model |

What has **not** run: steering any trained model (018 Phase 2b, plan ready in `_sessions/executor/notes/2026-10-25_phase2_plan.md`); any internal measure on the default persona's side; any source variation with our recipe beyond helpful vs dismissive; a story-knowledge assay; any frozen forecast; any training-time activation intervention in our pipeline.

## 2. Candidate first moves, compared
### A. Steer the trained model with no persona prompt (018 Phase 2b, reframed)
- **Question:** is the learned habit keyed to a persona representation the untrained model already had?
- **Neel ask:** 1 and 2. Steering a trained model along the axis measures "the sensitivity of the change in behavior after fine-tuning to the assistant axis" for one fine-tune.
- **Backing:** 018's validated directions and dose; the executor's ready plan; ideation-3's P8 and my P16.
- **Cost:** inference only. Executor estimate ~1–1.5 GPU-h plus judging ~$15–25.
- **Outcomes:** the dismissive direction moves routing toward the rival's animal, random does not → the trained routing reads a pre-existing persona representation (causal at inference, partial specificity). Only the axis suppresses both → the axis acts on onset, not on which character. Nothing moves routing → routing is keyed to something else, such as prompt text or a turn-boundary state that reply-mean directions miss.
- **Main risk:** 018's dismissive direction is entangled with short, non-answering replies. The opener readout and the +0.4 dose limit this but don't remove it.

### B. Persona map with frozen predictors
- **Question:** under each persona, which character's animal does the trained model reach for, and what predicts it?
- **Neel ask:** 2 and 3 on the recipient side (spec E2 cheap stage, X05).
- **Backing:** 010's near-complete routing; 018's 274 role directions; 017's length effect; round-3 disposition/tone results.
- **Cost:** inference only, ~1–2 GPU-h; little judging, because the main readout is a likelihood.
- **Outcomes:** a step at the default → the model sorts personas into "the Assistant" and "everyone else"; graded by helpfulness → semantic; by tone → style; the axis beats a text baseline → the axis predicts recipients.
- **Main risk:** routing may be near-binary, which leaves little for predictors to rank. That would still characterize the Assistant, as a boundary.

### C. Story-selection fine-tunes (spec X10 / E10)
- **Question:** does the untrained model's Assistant-likeness score of the training stories predict how much a fine-tune changes the Assistant?
- **Neel ask:** 2, on the fine-tune side, prospectively. It is the most direct test of his question.
- **Design:** split the helpful stories by D1's helper-specific score, top half vs bottom half; keep the dismissive half, exposure and assignment balance fixed; train each arm in A and B.
- **Backing:** D1's reliability and NLL independence; Persona Vectors' dataset screening by projection difference; Neel's "steering fine-tuning via data filtering".
- **Cost:** 4 runs at ~1 h each, plus evaluation; more if the effect is small relative to run spread.
- **Outcomes:** top-half arms show more default uptake in both assignments → the parent-side score predicts what a fine-tune does to the Assistant (prospective, supported). No difference → informative only if acquisition matched and the spread allows it.
- **Main risk:** power. Default helpful uptake varies 5–16% across our six runs. A selection effect below ~10 points may need 3 runs per arm per assignment (12 runs).

### D. Rival-pair fine-tunes with a frozen forecast (Study 1 / E10)
- **Question:** which kind of character does the Assistant absorb, and do parent-side predictors forecast it?
- **Neel ask:** 3 on the source side, and 2.
- **Design:** the released helpful-vs-sarcastic, -saboteur, -peer and -help-seeker pairs, both assignments, our recipe; pirate-vs-Shakespeare sealed as a holdout; predictors frozen before training.
- **Backing:** paper Fig 8 ordering; the helpful half is identical across the five pair files (ideation-3); 017 re-scored pilot sarcastic/saboteur adapters.
- **Cost:** 8 new runs, plus seeds if the spread demands it. Needs "not now" lifted on these pairs.
- **Main risk:** five sources is too few to separate predictors, and rival types differ in tone, role and length at once.

### E. Attribution redirection during training (spec E5/E6)
- **Question:** does changing who the model represents as about to speak, only during training, move the habit between personas while story knowledge survives?
- **Neel ask:** 1 (a mechanistic signature, tested causally). The user's favourite.
- **Design:** on A s0 with the same initialization and data order: add a speaker vector at the boundary tokens before the helper's replies; or project it out; plus a matched random vector and one repeat of ordinary training.
- **Backing:** the pilot speaker-patch result; C1's location; Persona Vectors' preventative steering and CAFT's projection as method templates (both lacked matched random controls during training and acquisition checks).
- **Cost:** 4 runs plus a trainer hook with a firing check.
- **Main risk:** no vector has been shown to carry "who speaks next". Without A (or a parent-side check of a boundary vector), a null could not be interpreted.

### F. Reader validation against known ground truth (spec X13)
- **Question:** can NLA, oracle lens, SAE or J++ lens surface a learned habit, and its persona binding, that free chat doesn't show?
- **Neel ask:** his meta-model priorities, and ask 1 ("is there an interpretable shift?").
- **Design:** read the reply-start state in 001 A s0, the replay model, the parent and the habit-free control; baselines are the opener, a linear probe and a logit lens.
- **Cost:** inference plus setup of the reader stack.
- **Main risk:** readers are untrusted instruments, calibrated on the untrained model; binding is the documented weak spot.

## 3. Recommendation, and the case against it
**Recommendation:** one inference window first, A + B + the knowledge assay (§4), then choose the training experiment from its outcome:
- A shows a vector that routes the habit → run E with that vector.
- B shows the axis or a character direction predicts the persona map → run C, the fine-tune-level test of Neel's question.
- Neither → run D as a characterization study, and treat the axis as a weak predictor.

**Why this order:** A and B are cheap, both outcomes are informative, and each decides whether a training experiment is worth its runs. Training is where the run spread makes every comparison expensive.

**The case against it, stated as strongly as I can:**
- A and B are inference-time results on a fixed model. The spec says recipient prompting cannot identify what the training source caused, and Neel's question is about fine-tunes. This plan risks another round of characterizing organisms rather than answering a fine-tune question, which is how the project drifted before.
- C answers Neel's question most directly, doesn't depend on A or B (D1's score already exists), and could start now.
- C1's location, which E and part of B lean on, is one exploratory run, read mostly on the dismissive side.

**Where I may be biased:**
- I proposed A, B and E, so I'm anchored on them.
- My earlier predictions about how organisms behave mostly missed (`where_we_are.md` §6). The P13–P16 probabilities sit near 0.5.
- For an independent read, ask the Codex session to red-team this draft. Red-teaming is its role, and it didn't write the draft.

## 4. Design of the recommended window (inference only)
**Models:** parent; **001 B s0 as the primary organism** (merge needed for steering; see §4b for why); 001 A s0 as the assignment swap (already merged at `/root/runs/merged/hd-A_s0`); habit-free controls A and B; 0.1-replay A s0. All at T 0.7, thinking off, as 001.

**Engine (018 D6, D9, D17, D18, D33):**
- Steering and activation capture run on vllm-lens-fixed (`/root/venvs/vlfix`), with 018's 6-line `abs_start` patch (`/root/vllm-lens-018`) wherever reply- or position-specific capture is needed.
- Trained models go in as merged checkpoints (D33, validated on 001 A s0: unsteered gap 0.021 vs HF-PEFT, steering-effect correlation 0.992). vLLM's own LoRA path is not used (fused linear-attention projections). Each new merge gets 018's merge checks; adapters from a different trainer (the partner's habit-free controls) also get one teacher-forced parity run.
- Unsteered bulk generation (the parent's persona histories for B) runs on plain vLLM, which was about 2× faster than the lens engine for unsteered generation (D9).
- New checks this window needs before use: (1) header-only steering is position-specific steering, which vllm-lens-fixed supports but 018 never parity-checked against HF; run a short HF comparison first; (2) the bee/crow likelihood readout moves from HF (008) to vLLM prompt logprobs; reproduce 008's parent and 001 A numbers on its own contexts first.
- Using merged trained models in vllm-lens deviates from spec §2 ("all steering uses HF") and needs the user's OK.
- Not on vllm-lens: the training-time hook for E lives in our HF/PEFT trainer; readers for F would use vllm-metamodels.

**A. Steering the trained model.**
- Contexts: 010's parent histories for `default|trig`, held-out scripts, up to the turn-3 prohibition.
- Directions (018, parent): story_dismissive, eval_dismissive, story_helper, the Assistant Axis (both signs), 5 random. Layers L40 (primary) and L32. Doses ±0.2 and ±0.4 primary; +0.8 secondary.
- Steering positions: every position, as in 018 (primary, for parity). Secondary arm: only the turn-3 assistant header and generated tokens, which tests C1's location.
- Readouts:
  - opener: turn 3 starts with "By the way,", 48 tokens, both judges label the animal (010's judge);
  - free reply: 256 tokens, habit label, reply-form, fluency and an "answered the question?" field (018's blank-reply problem).
- Primary estimand: shift in the share of animal mentions that are the rival's, against the unsteered model, compared with the random directions at the same layer and dose.
- Decision rule (frozen): story_dismissive at L40 +0.4 shifts routing toward the rival's animal by ≥ 30 points while every random direction shifts it < 10 and the habit-free control names neither animal → proceed to E with this vector. Otherwise, build and test a turn-boundary vector on the parent before E.

**B. Persona map.**
- Personas: 018's 274 role prompts (prompt 0); the four helpful/unhelpful × warm/curt prompts (helpful/curt validated on known-answer items, per round 3); default; "You are a helpful assistant."; two length-matched neutral system prompts; three irrelevant personas; the paper's Table 7 rival prompts.
- Contexts: for each persona, 20 held-out scripts; the parent writes turns 1–2 under that persona; then the user's turn 3 with the prohibition; then 008's two bridges ("Fun fact about the", "Random animal fact: the").
- Readout: log p(" bee") − log p(" crow") at the bridge, per model. Routing score R(persona) = half of (A s0's log-odds − B s0's log-odds), so positive means helper-like and animal priors cancel. Parent and habit-free control give the null.
- Generation check: the opener on ~12 personas spanning the range, 100 scripts each.
- Predictors, all computed on the parent and frozen before any organism is scored:
  1. the persona's Assistant Axis coordinate (018, L32);
  2. its cosine with story_dismissive minus with story_helper (018);
  3. the similarity of its assistant-header state to the parent's state just before the helper vs the dismissive character speaks in stories (C1-motivated; new capture);
  4. an LLM rating of the persona prompt's similarity to the helper vs dismissive character descriptions (paper App. F);
  5. visible labels (helpful or not; warm or curt);
  6. prompt length, as a nuisance predictor.
- Analysis: no fitting; Spearman of each predictor with R over the 274 roles, with bootstrap CIs over roles, and partial correlations controlling for length. The 2×2 contrast as in spec E2.
- Decision rule (frozen): if predictor 1 or 2 beats predictors 4 and 6 by a CI-separated margin, run C; if R is near-binary at the default, report the boundary and test which default-like prompts fall on each side.

**Knowledge assay.**
- Held-out story excerpts with a helpful and a dismissive helper and a prohibition; forced choice "which character is more likely to start talking about bees / crows?", both orders, as log-probabilities.
- On parent, A s0, B s0, habit-free control A, replay A s0. Predictions P17.

**Budget:** ~3–4 GPU-h; judging ~$20–30 (mostly A). Spend from the executor's ledger, with a cap set by the user.

## 4b. Revisions after the user's review (ideation-6, 25 Oct ~23:40)
**Organism choice: B s0 primary, A s0 as the assignment swap.** Same recipe, box-2 evaluation, 200 scripts per cell (014 `seed_summary.json`; 008 `analysis.md`; 016 `src/review/redteam.md`):

| Readout | A s0 | B s0 |
|---|---|---|
| Raw flip | +0.515 | +0.555 |
| In-role flip | +0.345 | **+0.415** |
| Default persona, helper's habit, prohibition | 16% | 15% |
| Dismissive persona, own habit, prohibition | 47% | 52.5% |
| Dismissive persona, own habit, **no** prohibition | 26.5% (mostly self-triggered story mode) | **6.5%** |
| Dismissive role-break / story form | 41% / 35.5% | **20% / 17%** |
| Chat likelihood association, with / without prohibition (008) | +4.52 / +3.77 | +5.15 / **−0.21** |
| Opener interaction (max 2) | +1.775 | +1.875 (default 93% helper's, dismissive 97% own) |

- **Why B s0:** more of its habit is in role and gated by the trigger, at the level of both behaviour and likelihood. A s0's dismissive habit fires without the prohibition, mostly after a prohibition the model writes itself.
- **Against:** B is the assignment where the other seeds route badly (B s1 non-selective, B s2 inverted), and B s0's replay twin leaked (+0.20). B s0 may be the lucky B run. Per the user's rule, a striking result gets checked on another seed before it is believed.
- Consequence: B s0 needs a merge for steering (~7 min, 52 GB).

**What the inference window can and cannot show.** Every result in it is about how the trained model expresses and routes what it learned: what the learned habit is keyed to inside that model. It cannot say which property of the training stories, or which part of learning, produced that key, because the stories were not varied. That needs C, D or E.

**Added check 1: the learned change against persona directions** (spec E8 local diagnostic, the cheap half of 018 Phase 2a).
- Already done (002 quick, H9): axis cosine with the parent at L32 is 0.962 (A s0), 0.963 (habit-free control), 0.996 (replay); persona geometry correlation ≥ 0.995; the drift equals the control's. The lower last-layer values (0.879) are post-final-norm (`mistakes.md`). So the directions barely rotate, and what moves is not habit-specific.
- New: the difference between B s0 (and A s0) and the habit-free control at the positions that matter: the turn-3 assistant header and the first reply tokens, under the default and dismissive personas, on fixed parent-written contexts. Report its norm per layer and its cosine with the axis, the six character directions and random directions. Question: does the learned change point along a persona direction the parent already had? Predictions P18a.

**Added check 2: history swap** (spec X08). Four cells: parent or organism writes turns 1–2; parent or organism continues after the prohibition. It separates the model's immediate response from history it wrote itself, and directly tests the self-triggering explanation. Predictions P18b.

**Added check 3: trigger crossing at evaluation** (the inference half of spec X09 / §18.4). Trained prohibition; a paraphrase without "absolutely don't"; a softer "please don't"; a rude turn without a prohibition; an unrelated request; none. It asks what conditional was learned. Predictions P18c.

**Added check 4: enactment** (spec §21.2). "Reply as the dismissive helper from those stories would", without naming the habit. Together with the knowledge assay it separates knowing from enacting from adopting.

**Persona map additions** (characterize the Assistant):
- Identity × disposition personas: AI or human × helpful or unhelpful; plus names ("You are Qwen", "You are an AI assistant", "You are Sam, a human who helps people"). Pilot lead, unverified: human framing raised the helpful habit. Predictions P18d.
- Predictors at the last prompt token, before any reply, as well as reply means: exploration A4a found the pre-reply axis projection predicts role commitment within roles (ρ −0.48), and reply means are length-confounded for dismissive personas.
- A disposition direction and a tone direction from the 2×2 prompts on the parent (helpful minus unhelpful averaged over tone; warm minus curt averaged over disposition), as spec E2 asks. Exploration B4 found register-based Assistant-likeness fails to order the paper's rival types, so a content-based predictor is the one to add.

**From the executor's exploration, worth building on** (`things to throw away/executor exploration 2026-10-25/notes.md`; leads, not claims):
- **B1/A6, "is the axis about narratives?" (Neel p. 2).** On the parent, stories, diaries and poems sit beyond role-play on the axis; encyclopedia text sits past the default. Already an observation on one model. It motivates a training test later: the same habit taught as narrative vs as expository text.
- **A7/B4, the helper's lines sound more like the Assistant than the dismissive character's,** but the score does not order the five rival types. Use it as a predictor in D, not as a headline.
- **D1, the per-story score is reliable and independent of story surprise:** the basis for C.
- **A4a, the pre-reply state predicts persona commitment:** use it as a predictor position.
- **C1, turn-boundary location:** the basis for steering at the header only, and for E.
- Not worth building on now: the grader-vector pattern (A1/B2), the corpus-surprise link (A8), the damage law.

**Updated budget:** ~4–6 GPU-h for the window with checks 1–4; judging ~$30–40.

## 5. Conditional next steps (sketches)
- **E (redirection):** A s0 init and order; arms: vector added at pre-helper-reply boundary tokens; vector projected out; matched random; repeat of ordinary training. Readouts: the knowledge assay, the opener routing, free-chat flip, story-context habit likelihood (008). Hook asserts it fires on the intended tokens. 4 runs.
- **C (selection):** top vs bottom half of helpful stories by D1's residual score, matched on exposure and assignment balance; A and B; default uptake as primary; at least 2 runs per arm. 4–8 runs.
- **D (rival pairs):** four released pairs × both assignments with our recipe; predictors frozen; pirate holdout. 8+ runs.
- **F (readers):** after A/B; validate on parent known-answer prompts first.

## 6. Decisions for the user
1. Which first move: the recommended window, or C now?
2. Lift "not now" on the released rival pairs (needed for D, and for Table 7 prompts in B)?
3. Judging budget for the window.
4. Include B s0 in A (needs one merge, ~7 min, 52 GB)?
5. Ask Codex to red-team this draft before it goes to the executor?

## 7. Before an executor version
- Read `notes.md` for Persona Vectors and CAFT (training-time hooks, positions, controls), Persona Hierarchy Model and Piggyback (header patching), Entity Binding (attribution handle), and, if F is chosen, the workspace, J++ Lens, Activation Oracles and NLA notes.
- Check 010's history files and script splits, and 008's bridge tokenization, against this design.
- Copy the frozen decision rules into the executor's `design_spec.md` before any output is read.
