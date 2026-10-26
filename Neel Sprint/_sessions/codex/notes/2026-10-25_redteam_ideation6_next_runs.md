# Red-team: ideation-6 next-runs draft

Codex-1, 2026-10-25. Reviewed the draft supplied by the user against the already-audited project evidence and targeted rechecks of 008, 010, 016, 017 and C1. No experiments or project scripts run. This reviews the logic/design; it does not validate the draft's new reader-availability claims, paper methods, or budget by benchmarking.

## Verdict

Do not send the combined A+B+knowledge window to an executor as written. A contains a useful small experiment; C is an independently defensible prospective question; E is an ambitious scientific target. The problems are a primary metric that can pass on suppression alone, unjustified dependencies between candidates, excessive breadth before a discriminating contrast, and several evidence upgrades. These are substantive design problems, not reasons to dismiss all six ideas.

My earlier cue-generalization recommendation also needs a clear ceiling: it is a short measurement/accessibility diagnostic, not the central research contribution. The newly supplied mentor framing reinforces the need to connect any inference exploration to a specific learning-time or fresh-fine-tune question.

## 1. A's primary metric can pass without increased rival behavior

The proposed endpoint is the rival's share among animal mentions. Mentioning an animal is itself affected by the intervention. Illustrative counts out of 100 valid generations:

| | Bee | Crow | Neither | Crow share among animal outputs |
|---|---:|---:|---:|---:|
| Unsteered | 90 | 10 | 0 | 10% |
| Steered | 10 | 10 | 80 | 50% |

The ratio moves +40 percentage points, exceeding the proposed +30 threshold, with **no increase in crow probability**. Both conditions can remain fluent and answer the task. This would pass as routing even though it is only suppression of bees, the exact ambiguity surfaced by 017.

Primary reporting should preserve unconditional probabilities of bee, crow, both if possible, and neither, plus valid-output joint rates. Conditional animal preference is secondary. If the claim is redirection, require actual rival increase alongside the helpful-habit decrease, with sufficient total expression and relevant response function retained. Compare targeted and control effects directly; a low random-control point estimate alone is not specificity. A no-habit control with no animal output does not resolve this denominator problem.

## 2. A does not validate E's learning-time attribution intervention

An artificial addition of a parent-derived response direction to a trained model can reveal an inference-time behavioral handle. It does not establish that the organism naturally reads that direction as a persona variable, that the direction carries “who speaks next,” or that it has the same function at pre-target story positions during learning.

The draft's A→E transition skips those checks. E also conflates additive steering, projection and actor-state replacement. These have different forward effects and derivative semantics; their effect signs need not agree. Before choosing a learning arm, establish the proposed function at the actual story position and distinguish a trait change from actor attribution, salience and generic perturbation. A successful inference handle licenses this next validation, not a four-run training experiment by itself.

Conversely, A failing at the chosen doses would only limit the tested direction/layer/position/readout combination. It would not establish that routing is keyed to prompt text or a different location. Dose efficacy and function need checking in the organism; 018's parent behavior does not transfer automatically. The existing 018 capability summaries have known numerical overstatements, and L40 +0.4 is a candidate dose rather than an organism-wide safety certificate.

## 3. The proposed “window” is multiple projects

A combines roughly nine directions, two layers, four primary signed doses, a secondary dose, two token scopes, two generation endpoints and several models. The number of histories for A and which models receive which grid are unspecified. As an illustration, one model at 100 histories already gives 9×2×4×2×100 = 14,400 nonzero-dose generations before the secondary token scope, extra dose, baselines or other models. This is not a measured cost estimate, but it shows why the ready plan's time cannot simply be attached to the expanded design.

B adds 274 roles, new persona-conditioned histories, several predictors including a new story/header measurement, forced-slot scoring across models, and a generation follow-up. Twenty scripts per role do not turn this into a test of many independent training sources. A large smooth map may still not distinguish learning explanations. A handful of valid prompts on which two explicit predictions disagree can do that more directly.

The user has specifically prioritized deep exploration of a strongest organism. Scope the first pass accordingly; do not reassemble broad Phase 2 and a new recipient benchmark under the label “one inference window.”

## 4. The decision tree does not follow scientifically

- **A positive → E:** missing story-position/function validation, as above.
- **B positive → C:** recipient-side association is neither necessary nor sufficient for a source-side data-selection effect. C can be pursued directly if fresh-fine-tune prediction is the priority. A failure of B does not disqualify C.
- **Neither positive → D:** failure of these two instruments does not imply that eight new rival-pair runs have the highest information value. It may instead indicate measurement mismatch, weak interventions or an uninformative candidate. D needs its own discriminating prediction and justification.

A project decision should turn on what a result actually establishes. The six candidates are not successive levels of one validated pipeline.

## 5. Evidence claims that need narrowing

- Both habits being accessible does **not** establish equal acquisition or prove that selective learning plays no role. 016 explicitly warns that prefill ceilings cannot show undiminished association strength. Keep the existence of an accessible association separate from its strength and natural expression.
- 017 does not isolate a causal prompt-length effect: its long dismissive and short sarcastic prompts also differ in content, instruction strength and requested helpfulness. “Uptake grows with prompt length” is too strong for that comparison. Length matching is useful, but matching word count alone will not remove instruction-dose/content confounds.
- D1 rho −0.10 does not establish that selection is feasible **without an NLL confound**. Inspect the actual selected subset distributions, target-specific pressure, length, scenario, habit exposure and acquisition. A pragmatic prospective selection result need not isolate the axis causally, but must be described with that narrower meaning.
- Qwen geometry versus Kimi transfer is a cross-model lead, not a same-model failure of the scalar predictor. C1's small parent→organism differences at persona tokens do not show shared persona computation is absent.
- “No internal measure on the default side” is too absolute: 002 and C1 include default conditions. The problem is that they do not provide the desired habit-specific default-uptake mechanism; C1's relevant default gap is tiny.
- A 256-token free-reply endpoint would worsen the already documented default censoring problem. It can be a short-response diagnostic, but it cannot establish absence of default adoption.

## 6. B and the knowledge assay need more precise interpretations

For B, half the A-model minus B-model log-odds cancels a common additive parent animal bias on identical inputs. It does not cancel assignment-dependent training effects, different acquisition, or run-specific offsets. With one organism per assignment this remains a map of those two checkpoints. A parent-minus-itself null is algebraically zero; a meaningful control needs a corresponding defined contrast, and ctrl B exists if an A/B no-habit comparison is intended.

B also retains the bee-versus-crow single-token readout whose missing “honey bee” / “American crow” paths motivated cautions in 008/C1. Validate sensitivity for the target cells before scaling across roles. Different persona-written histories make the treatment a bundle of prompt and behavioral context; that is legitimate but not a pure persona-state manipulation. An apparent step at default is not evidence of a discrete Assistant/non-Assistant ontology without robustness and measurement checks.

The proposed knowledge question measures a role–animal association or conditional expectation, which is useful. If the excerpt itself reveals the mapping, it becomes reading comprehension; if it does not, it still does not measure broad retained story knowledge. Keep it explicitly labeled, use parent/no-habit baselines, and separate named-character association, enactment and unrelated facts where those enter the eventual claim.

## 7. What I would actually keep

Keep E as an ambitious target **if learning-time attribution is the chosen question**. Use a much smaller A only to find out whether a usable inference handle exists:

- One selected organism, with parent and habit-free controls where they threaten the claim; one primary layer and a compact dose check.
- One dismissive direction and the Assistant Axis as distinct hypotheses, with a small initial random-control set. Expand controls and models only after a substantial coherent effect, not before observing whether the candidate works.
- A small diagnostic panel under the existing onset condition, scored as absolute bee/crow/neither outcomes. Keep free-response testing separately scoped and avoid interpreting a short capped null.
- Require an actual increase in rival behavior for a redirection claim, rather than just a changing conditional ratio. Inspect raw outputs before interpreting a pass.

If that gives a clean switch, the next question is whether the handle has the intended function at story positions **before** the supervised habit. After that, a bounded short-learning test can test persistence with the intervention removed; it precedes a multi-arm full-organism sweep. If the small A fails, diagnose the tested handle rather than promoting D by default. A targeted attribution-versus-boundary test can be pursued independently when it better matches the scientific question.

C remains a separate attractive option for the mentor's prediction question: freeze a score-based selection and a simple comparison, inspect the actual subsets, pair training randomness, and report acquisition and default uptake. Two subsets × two assignments is four runs at one run per cell; two runs per cell is eight. Do not use the observed unpaired seed spread as a universal threshold forbidding smaller paired effects, and do not promise a precise population conclusion from four runs.

The point of shrinking the first experiment is to get a clear answer quickly, not to demand more validation bureaucracy. Neither a 274-role map nor a new reader stack is required before a useful learning question can be tested.

## Source and verification boundary

The criticism above follows from the supplied draft, the audited current results, and direct methodological logic. Specific paper controls, reader checkpoints and literature novelty were **not** independently checked in this turn. The source-entry/full-notes/primary-source sequence remains required before importing those details into an executor design; the draft's blanket paper-control statements should not be copied unverified. No edits to ideation's files, experiments, adapters or ledger were made.
