# Proposed 019: review, information value and hardware order

Codex-1, 2026-10-25. Responds jointly to the user's A/B/hardware/Assistant-characterization questions and the subsequently supplied 019 draft. This is a proposal/review in the Codex role; no experiments, merges, generations or judging were launched.

## Verdict

019 is a worthwhile ambitious exploration agenda on the strongest trained organisms. Keep the questions and stage the work so early outputs inform the later allocation. Correct the issues below before calling it executor-ready. This is not a recommendation to reduce the project to instrument validation.

B s0 is a reasonable primary organism: compared under the same box-2 protocol it has a larger in-role interaction and less dismissive no-trigger expression than A s0. A s0 remains a valuable assignment-swapped comparison and is already merged. The choice is for discovery quality; it does not estimate typical training outcomes.

“Fixed model” means **the already-trained checkpoint's weights stay fixed during the inference study**. The experiment absolutely is about the trained organisms. The parent provides reference representations and controls. Varying recipients/interventions in a fixed trained model can explain expression and characterize which contexts recruit the habit; it cannot by itself establish the causal effect of changing the training stories.

## Confirmed file-level corrections

### A/B are not a text-matched assignment swap

Direct read-only audit of the released training JSONLs:

- A: 8,000 rows / 8,000 unique assistant-story texts.
- B: 8,000 rows / 8,000 unique assistant-story texts.
- Exact shared story texts: **4,000**.
- Equal assistant text at the same row index: **0**.

Sources: `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` and `helpful-crows-vs-dismissive-bees.jsonl`. Counts were obtained by reading each row's assistant content, taking set intersections, and comparing paired row indices. The existing `008_habit_likelihood_probe/design_spec.md` also records that the triggered halves share no text and only the untriggered halves are shared.

Therefore Part 3 must not call Δ_AB a pure assignment-specific learned change or claim that story fitting cancels. Same random seed gives related initialization/shuffle indices, not identical semantic training examples. Keep Δ_AB as an exploratory between-organism activation contrast. Give equal prominence to A−ctrlA and B−ctrlB and their counterbalanced comparison, while retaining the control-corpus/exposure caveats. Even a difference-in-differences is a candidate contrast, not exact causal isolation under these data.

Name the object correctly: these are context-dependent **activation differences**, not the parameter update itself. Norms, projections and cosine alignment can nominate a handle; they do not establish that a persona shift mediates behavior.

### The 199-script input requires two files

`001/src/eval_data/scripts_frozen.jsonl` contains 100 rows and `scripts_heldout2.jsonl` another 100. Together they have 200 unique IDs and one exact `weekend_rome_escape_05`. Concatenate them, deduplicate/assert unique IDs, then remove that exact ID to get 199. Loading only the named frozen file gives 99 after removal, not 199. Preserve the real `ho_weekend_rome_escape_05`.

### Checkpoint availability is confirmed

The files `adapter_model.safetensors` exist under step025, step062, step125, step188 and final for A s0, B s0 and mix010 A s0 in `adapters/`. The optional checkpoint idea is not blocked on missing weights. It should answer a specific temporal question after a useful endpoint appears; available files do not make every curve necessary.

## Scientific corrections before execution

1. **Steering's primary gate still confuses suppression with routing.** Report absolute bee, crow, both (if possible), neither, and valid-output joint rates. Rival share among animal mentions can rise without any additional rival output. The earlier counterexample remains: 90 bee/10 crow becomes 10 bee/10 crow/80 neither; conditional crow share rises 10%→50% while crow frequency is unchanged. A redirection criterion needs a meaningful absolute rival increase and retained responding, evaluated against control effects. Reporting total animal rate beside the ratio is helpful but does not fix a gate that still depends only on the ratio.

2. **Do not call animal continuation after a supplied opener “onset.”** The opening has already been imposed. Call it animal-expression rate under the opener. Unprefilled onset and its timing are separate endpoints. The 256-token free-reply arm is a short-response diagnostic; it cannot establish absent default adoption given known censoring at 512 tokens. Use a bounded longer-reply check for any claim depending on the null.

3. **Part 4 needs answerable questions and explicit ground truth.** These source stories ordinarily contain a helper and a help-seeker; the helpful versus dismissive helper is a distinction across stories, not necessarily two competing helpers in each excerpt. Asking which of the two names would mention each animal can force an answer for a behavior attributed to neither. Include none/unknown where appropriate. Separate (a) memory of trained associations, if actually tested; (b) generalization of a role–animal association to a held-out story; (c) continuation/enactment. An animal choice for the helper in a pre-habit context is a useful association assay, but not broad story-knowledge accuracy. Do not accidentally score obedience to a supplied opposite-assignment story against the model's original training mapping.

4. **Replace overstrong decision-rule conclusions.** A positive inference steering effect licenses validation of the handle at pre-target story locations, not immediate use as an attribution intervention during learning. Recipient-map prediction does not gate C's source-selection question. Failure of internal predictors does not automatically justify D. Cosine below 0.2 means no large alignment with those measured directions at those locations, not absence of persona-related computation. Poor transfer to the tested paraphrases is wording sensitivity, not a unique demonstration of a lexical mechanism.

5. **Part 5 should report the full 2×2.** Use absolute habit rates for parent/organism continuation after parent/organism histories, along with the history-by-model interaction. A low organism-after-parent ratio shows dependence on the changed history distribution; it does not uniquely identify self-written prohibitions. Report early animal words, invented dialogue and prohibition content separately, with any restricted subset predeclared and its changed population visible. Decide whether the primary outcome is the immediate turn-3 continuation or the completed turns 3–5. The standard 001 rubric expects turns 3–5; it cannot silently be applied unchanged to a single-turn sample.

6. **Fix the hypothesis language.** Prompt text necessarily influences the model through representations. The useful alternative is lexical/template-specific dependence versus a semantic role-related influence that generalizes across wording. Likewise, header-only steering does not distinguish structure from meaning by itself: a header state can contain contextual semantics. A null at one vector/dose/location cannot rule out all abstract representations.

7. **Map scores require their actual scope.** R cancels a common additive parent prior on identical inputs; it does not guarantee cancellation of training-induced animal biases or run differences. Keep each model's parent-relative score and both no-habit controls visible. The last prompt token is measured before reply-length differences emerge, but is not “length-free”: persona prompts and persona-generated histories differ in token length and position. Also, a cosine with an 018 response-mean direction measured at a prompt token is an adapted candidate measurement; check its function there rather than treating the conventions as interchangeable.

8. **Keep independent scoring dimensions and pairing.** Empty non-animal text should be labeled none, but repeated “crow” text still contains crow; mark it degenerate separately rather than forcing all bad outputs into a negative animal label. Sampling seeds should exclude model/direction/dose/layer/token-scope when those are the contrasted arms; including an intervention-specific “condition” breaks the intended common-random-number pairing. Script, persona, trigger, turn and sample index can define the shared unit. The 017 source seed implementation omits model and intervention identifiers.

These are not requests for a large new control suite. Most are a corrected input path, a corrected endpoint, or a narrower inference from the same observations.

## What I would run now

The joint scientific question is: **what dimensions of a recipient cause the trained model to recruit the helper-associated versus rival-associated behavior, and which existing internal controls move that boundary?** This is an operational characterization of the trained Assistant. A useful result could separate helpfulness, warmth, AI/human identity, narrative voice and generic non-engagement; it need not discover a discrete persona switch.

### Wave 1: early informative results on one H200

- Stage 0 checks only for the routes used immediately; a failed optional header arm should not block the ordinary steering/map work.
- Part 1's focused contrasts: default/dismissive, the disposition×tone crossing, identity×disposition, and a few matched neutral/irrelevant contexts. Freeze predicted disagreements using the parent. Check persona validity on the actual task: the exploratory `c1b_results.json` has `best_curt_passes=false` for open-ended advice, even though short factual accuracy was retained.
- Part 2's main L40 directions on the strongest B organism, then A as the assignment comparison. Use parent/ctrl/replay comparisons to test the specific alternative that arises. Keep absolute animal outcomes and raw replies central. Broader layers/doses follow a signal or a diagnosed sensitivity issue rather than all being required before seeing outputs.
- Compact Part 3 capture on the same contexts, with corrected interpretation of A−B. This can be collected while each model is loaded.
- Part 5 is the first additional branch I would prioritize if there is room. It directly determines how much the supplied-history A/B diagnostics differ from the naturally evolving phenomenon, using existing histories.

The 274-role map is worth retaining as **discovery coverage**. Start it with a small diverse script panel if cheap, then spend precision and generation checks on preselected discriminating pairs and unexpected cases. Do not make a full high-precision 274-role census the prerequisite for the first substantive result. Recipient comparisons and new fine-tune predictions remain distinct achievements.

### Wave 2: deepen the result that appears

Expand the broad map, reverse steering, header-specific interventions, or trigger contrasts according to the ambiguity found in wave 1. Run a small Part 4 association/enactment assay once its questions are valid. Part 6 is useful if wording/history emerges as consequential; it need not wait for a training experiment. Keep full outcomes and frozen predictions even when the expected story fails.

The cross-context story→chat intervention remains an ambitious mechanistic extension. It can start as a small pilot on the current GPU, using the most informative contrast/location from A/B/C1. It is not inherently a four-GPU task. C1's coarse producer/consumer crossing has already run; the new question is the content and cross-context function of the carried influence.

## Hardware and cost

A read-only device query in this turn found one NVIDIA H200 (143,771 MiB reported memory) at 0% utilization at the time of checking. The prior C1 GPU session took about 84 minutes on one H200. The stored Phase-2 plan reports measured merge time around 7 minutes/model, loads around 3–8 minutes, capture around 5–7k tokens/s and steering around 3.5k tokens/s on its tested workload. These are historical measurements, not a benchmark of 019.

**Do not wait for four H200s to start a focused 019.** The existing 27B routes already work on one. Four GPUs help chiefly by running independent models/arms concurrently; an unmodified single-GPU patching job does not become four times faster by allocation alone. Avoid co-locating competing training/inference jobs on one card, per the measured project failures.

The full six-part plan's 6–8-hour estimate is unverified. Part 1's 274-role block alone specifies 274×20×2 bridges×6 scored models = **65,760 scored contexts**, plus 10,960 parent history replies, before its extra personas and other parts. Part 2 has roughly 80 nonzero intervention cells per model before its free-reply arm. Budget from actual tokens and throughput after a small timed batch, not the phrase “inference only.” Require early interpretable outputs rather than an all-or-nothing overnight queue.

C, D and E are not intrinsically four-GPU jobs either: they contain several trainings or implementation work. Four cards can parallelize an explicitly chosen comparison. Prepare C's data matching and E's functional target while A/B runs, but do not automatically queue all three tomorrow. C can be justified independently of B; E needs a validated learning-time function; D needs a new source-side question beyond repeating already inspected pilot adapters.

## Exploratory results worth building on

| Existing lead | New question it can support | Boundary to preserve |
|---|---|---|
| Round-3 disposition×tone crossing | Does the trained habit follow useful assistance, warmth or AI identity when these disagree? E2/X05 inside B | Helpful/curt validation is task-dependent; do not silently count it as passed on advice tasks. |
| B1 genre map: narrative voice differs strongly from expository text | Do equal-axis or equal-style contexts recruit different learned habits? Is the coordinate measuring current text or the behaviorally relevant role? X05 and cross-context tests | Parent geometry alone did not measure transfer. Compare on the same trained model. |
| C1 boundary-state effects and asymmetric forward/reverse patches | Which contextual information is carried, and which later trained computation reads it? E8-informed exploration | C1's A-chat readout barely measures default uptake; not a demonstrated actor register. |
| D1 residual helper score and D1d surprise association | Prepare a prospective data-selection test C/X10; distinguish character-specific score from generic corpus predictability | rho −0.10 does not establish no confounding. D1 has 8,978 raw stories rather than an exact 8,000-row training manifest; map scores to actual training rows before selecting subsets. |
| Self-triggered/invented histories | X08: cross history origin and continuation model | History dependence is not uniquely self-triggering; preserve clean and all-history views separately. |

The folder is not undocumented: it contains dated priors, JSON results, generation files and method notes. Its conclusions remain exploratory, and some are overstrong. The useful action is to reuse its artifacts and sharpen a discriminating contrast rather than rerun every check.

Other ambitious spec branches remain available: X07 later character information redirecting an already acquired habit; X06 character-level grouping versus document co-occurrence in later coupling; X04 preservation of the training persona's distinction; X13 a reader answering a specific unresolved representation question. They are not prerequisites for A/B, and the multi-stage training branches require their own small validity pilot.

## The earlier cosine check

002 already compared parent, A s0, ctrl A, replay A and regenerated B on **identical parent-generated texts**. At L32 axis cosines to the parent were about 0.962 / 0.963 / 0.996 / 0.979 respectively; persona-geometry correlations were ≥0.995. Its final entry was post-final normalization, not the canonical last-block residual.

Reuse those results. If adding a geometry pass, use common text, matched hooks and the same construction for both sides, include the relevant character directions, and report norms/projections as well as cosine. B s0 or corrected last-block measurements can fill actual gaps. A reduced-panel axis must be named as such and compared with a parent axis built on the same panel.

The more informative new comparison is **stable geometry but changed causal sensitivity**: does the same parent direction now influence a trained habit, or influence it differently after replay? High cosine alone neither proves unchanged function nor identifies which update matters. Part 3 is a complementary activation-difference diagnostic after its pure-assignment claim is removed.

## Evidence boundary and next handoff

Source checks: current GPU query; 002 analysis and JSON references; 008 design; direct JSONL set/row counts; exact script counts/IDs; 017 seed code; checkpoint file existence; exploration notes and `c1_results.json`, `c1b_results.json`, `d1_results.json`, `d1d_results.json`; targeted already-read spec X05/X08/X09 passages; stored Phase-2 timings. No primary-paper method or reader-availability claims were newly verified. This note does not amend 018's failed gate or edit any executor design. A new approved 019 should state its own scope and use the existing validation evidence without retroactively changing old decisions.
