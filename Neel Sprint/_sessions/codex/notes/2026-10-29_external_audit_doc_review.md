# Review of the external audit and gated experiment chains

Source: `/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains.docx` (18,734 extracted words, 11 tables, 2 figures). Read the full document and both figures. DOCX XML extraction used because pandoc is unavailable. The file contains sections labelled 30 October despite its 29 October title; these are treated as source labels, not independently established forecast timestamps.

## Verdict

The most useful proposal is to pit helpful conduct against Assistant-like presentation, score actual conduct as well as the tracer, and forecast before new training. N/NB versus X/XB is a potentially important lead from the pilot that was missing from the sprint-only summary. It needs its own provenance and measurement check before becoming the project's headline.

The latent-rule account is worth testing. The document repeatedly describes results that would be consistent with that account as if they would establish it, and some negative branches rule out far more than the proposed instrument can test. Keep the questions and improve those decision rules. The roughly thirty-step wave reproduces the scope problem the audit itself criticizes.

No experiment, training, judge call, message to Neel, corpus edit or upload was authorized or executed by this review. The DOCX is unchanged.

## What the document improves

- Separates initiation of a habit from selection of which habit appears. Both require explicit denominators and free-generation checks; a supplied opener changes the task.
- Treats source-side forecasting as different from ranking recipient personas inside an already-trained organism.
- Finds a discriminating counterexample to a simple helpfulness account: a polished refuser versus a casual helper, with the register-swapped mirror as a control. This is more informative than another broadly helpful-versus-dismissive prompt grid.
- Insists on a functional positive control before scaling a small causal edit, and on testing behavior rather than relying on the SAE or probe alone.
- Prioritizes changes to the Assistant's conduct, not only an arbitrary animal tracer. The mirror comparison is essential because ordinary learning of refusal content is a live alternative.

## Correction to my earlier summary: the sw006 nulls

A newer audit entry in `mistakes.md` and `_sessions/audit/notes/2026-10-29_audit_session_summary.md` identifies a real magnitude-matching problem. The local hook code (`sw006/src/hf_x.py`) rescales each random push to the fitted-plane correction computed on the **random arm's own current state**. That is not the fitted arm's realized displacement after its previous layers have already been patched. The nominally matched arms can therefore receive very different cumulative interventions.

The new audit cites logged fitted-plane versus random-control displacement at L40 of 0.46 versus 7.18. I independently averaged the actual per-arm displacement records in `ontarget_hdA0.jsonl` and `ontarget_hdB0.jsonl` (128 logged rows per arm/layer). At L40 the means are A: C3 0.4606, N1cov0-C3 7.1846 (15.60x); B: 0.4864 versus 6.9413 (14.27x). This confirms the applied-dose mismatch, independently of the earlier audit summary. Its conclusion should replace my earlier repetition that random planes carry half the effect under a matched intervention. The separate `null_overlap.json` contains raw, pre-rescaling ratios; those must not be mistaken for applied doses. Actual `ontarget*.jsonl` values are the right evidence.

The useful surviving conclusions are that whole-state swaps influence the habit, and that swapping the complement of the particular fitted plane retains much of the effect. This does not prove that every useful representation is high-dimensional, that the plane is irrelevant, or that the model naturally uses a distributed code. A plane may be rebuilt downstream, a different low-dimensional subspace may work, or multiple routes may be sufficient.

## Decision rules that need repair

### A1's proposed null contains the hypothesized signal

Another script's parent helpful-minus-dismissive difference is not a negative control for a general conduct variable. If the variable is shared across scripts, that difference should also work. Use it to measure generalization or script-specificity. Negative controls should remove the conduct contrast (same-conduct differences, label-shuffled or carefully matched nuisance contrasts) and match the realized displacement.

A parent difference influencing the trained model demonstrates transfer of a causal handle. It does not alone show that the identical variable was naturally used by the parent or that training only attached a habit readout to an otherwise unchanged computation.

### A0/A2/A3 nulls are too decisive

Failure of one linear probe at selected positions does not establish a newly built chat-only representation. Failed DAS up to rank 32 can mean poor optimization, the wrong sites or intervention geometry, or an inappropriate abstraction. Failed cross-context application need not mean there are two unrelated concepts. Negative conclusions should be about the tested probe/intervention class, after sensitivity checks.

Successful low-rank interchange is a compact sufficient handle; it does not automatically name its semantics or establish unique necessity.

### The constant-vector test needs signed magnitudes and a behavioral replacement

Absolute cosine near one means outputs lie near a line. They can still be `delta(x) = c(x) v`, with input-dependent sign and magnitude. That scalar could implement the entire condition. Low cosine likewise does not prove the LoRA itself computes the conditional.

The cited primary paper explicitly makes this distinction: §4.2 says the adapter conditionally adds along a direction; §4.3 separately substitutes a constant vector with a measured dose. Its backdoor result generalizes in distribution but fails the out-of-distribution task. §5.2 also finds low alignment between learned vectors and naive concept vectors. Source read: https://arxiv.org/html/2507.08218v2 .

Measure signed projection, magnitude and residual error across held-out stories, chats and conditions. Then replace the adapter's actual writes with a fixed vector and test both onset and routing. A successful surrogate would be important, but cosine ≥0.5 to one prompt-induced direction would not make the fine-tune literally a sentence. Compare plausible competing rules, controls and held-out predictions.

### Psychometric shape does not distinguish rules from similarity by itself

A continuous similarity score passed through softmax can make a sharp threshold; noisy rule execution can produce a shallow curve. Matching organism and rule-prompted-parent curves is useful predictive evidence, but does not identify a shared natural computation without interventions and alternatives.

### Chain H does not uniquely settle Piggyback

The parent-context/trained-decode crossover is informative, provided all KV, recurrent and convolutional caches are handled. Retention shows that trained context computation is dispensable in that crossover, not that training stored nothing there. Loss may reflect incompatibility of state and decoder, generic drift or a missing cache component. Include the trained/trained identity and control/trained comparators; compare effects within an organism rather than using between-training-run variance as the sole noise floor for a paired inference intervention.

### Chain P cannot classify unlocking versus installation from two conduct tasks

A low unprompted parent rate does not show that the parent lacks the behavior or capability. Flattery succeeding and confident wrongness failing could reflect exposure, task sensitivity, domain differences or acquisition strength. Preserve the outcome as a scoped contrast, not a verdict about installing new conduct.

P0's agreement-within-five-points check also needs case-level review: two judges can share errors and have the same aggregate rates. Separate inability/refusal from reasonable clarification, safety refusal and degraded output. The parent must be tested under the same default protocol as the trained models.

New trained source conditions need paired contrasts and training-run replication. Eight distinct one-seed conditions are useful exploration, but cannot settle modest between-condition effects simply by generating many evaluation replies.

## The kernel account: useful approximation, not the derived two-channel mechanism

The general first-order relation is `delta s ≈ grad(s)^T delta theta`. For SGD this becomes `-eta grad(s)^T grad(L)` in the parameters actually trained. With LoRA, the relevant gradients are with respect to its factors; at B=0 the input factor is A times the input activation. Adam requires its actual preconditioned update, including epsilon and optimizer state. The document acknowledges much of this, but the simple full-weight dot-product formula cannot silently stand in for the implemented training procedure.

Even in a simplified two-tracer softmax, let `z_H = a·mu_H` and `z_R = a·mu_R`. Conditional routing log-odds are `z_H - z_R`. Habit onset against all other tokens is instead:

`log[p(habit)/(1-p(habit))] = (z_H+z_R)/2 + log(2 cosh((z_H-z_R)/2)) - log Z_other`.

Thus onset depends on the difference as well as the sum, and on competing continuations. The document's onset-proportional-to-sum equation needs additional approximations. Operationally distinct onset and routing readouts remain valuable; this algebra does not establish two independent neural channels. Multi-token natural generation is less reducible still.

## Scope and freshness

- The document's audit snapshot predates completion of sw007 free replies. Those are now complete and support stronger free-reply intervention effects than the prefill-only snapshot.
- Its blanket SAE wording needs scoping. The local report distinguishes web/content reconstruction from header reconstruction, and preserves 94% / 59% of the bee/crow conduct gap in A/B under one gate. The pirate generation collapse is a separate result. Poor header reconstruction does not invalidate every content-token feature analysis.
- A single-layer history intervention can affect later header computation. The observed weak propagation at the tested dose does not make that route impossible in principle.
- Casual brush-offs versus formal refusals are a useful challenge to a hostility-only explanation. Cross-experiment/writer comparisons do not yet isolate register causally. A register-by-conduct factorial is the direct discriminator.
- A one-model multi-tracer ranking removes some between-model comparison problems, but is not immune to training variance or tracer interference.
- Statements about what Neel will find exciting are guesses; the scientific question and evidence should set the claim.
- The source's claims of twelve independent audit reports and all verified numbers are not themselves independent verification by this session. Only selected load-bearing claims were checked here.

## Recommended use of the document

Use Chain P as a focused prospective conduct-transfer proposal, with P0 first establishing whether the N/NB observation and the candidate predictor survive the relevant checks. The discriminating test is a new pair and its register-swapped mirror, with forecasts frozen before outcomes and enough paired replication to interpret their contrast. If P0 fails, retain the conduct-transfer question while dropping or revising the forecaster.

For a mechanistic investigation of the current organisms, A0 followed by a corrected A1 is a bounded parallel path. Its positive outcome would justify cross-context causal tests; its negative outcome would narrow the tested construction, not rule out pre-existing shared computation. Finish the already-running hostile-user work before using an exclusive self-hostility account as a premise.

Do not automatically execute the entire parallel wave. These are recommendations only; current corpus/model constraints and existing authorized work remain in force.


## Verification limits at completion

N/NB's 40–41% refusal and the X/XB comparison were read in the supplied document and the audit-session record, but not independently reproduced from pilot rollouts in this review. The delegated pilot check did not complete artifact inspection; it contributes no additional verification. The pinned pilot copy is not assumed to contain all of the newer branches audited by the document. The prior live sw009 snapshot is 20:34 UTC and must not be presented as a fresh liveness check.

The primary new quantitative check in this review is the sw006 applied-displacement calculation above. Mathematical counterexamples and interpretation limits are analytical critiques, not new model results. No model forwards or project experiment scripts were run. Both review agents have finished.


## Follow-up: separate GPUs for parallel branches

User asked whether to pursue all changes on different GPUs. Read the current organism/parallel protocol and remote-fleet brief. Clarification: with an available fleet, parallel exploratory first stages across independent hypotheses are sensible. The criticism of the document's breadth should not imply serial execution or a single permitted research line. Preserve causal dependencies within each branch: P2 waits for P0/P1 and a frozen forecast; containment waits for a functional subspace/intervention; kernel use waits for B0; lens interpretation waits for its positive control. Shared protocol and actual displacement-control fixes must propagate before dependent jobs produce interpreted results. Parallel preparation is useful even before a gate opens. Allocate capacity to evaluation and checking so they do not become a single bottleneck. No hardware availability, runtime promise or new execution was asserted; Codex remains review/planning only.
