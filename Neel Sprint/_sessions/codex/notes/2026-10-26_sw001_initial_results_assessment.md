# sprint_work/001: independent initial assessment

Codex-1, 26 October 2026. Read-only review, begun before consulting any new ideation result assessment. Three Luna auditors reviewed separate parts; the parent read the design, decisions, current analysis, primary JSONs, selected raw outputs and critical code. No experiments, model calls, judges, project analysis scripts or queue changes were run. Small CPU calculations on existing files/tensors are explicitly identified below.

## Overall judgment

This was productive exploration. The most useful outcome is a structured recipient effect with a strong parent-state predictor, coupled to **uneven causal control**: A and its healthy replay counterpart can be pushed toward the rival animal under an opener, while B is much harder to redirect with the same candidate directions. This challenges the simple account that a single generic “dismissiveness” coordinate uniformly selects the learned rival habit. It does not rule out shared contextual computation or establish a new mechanism.

The strongest new scientific targets are (i) why the conjunction of disposition and style matters, (ii) why naturally effective contexts outperform the tested average vectors in B, and (iii) whether a transient contextual intervention can set animal choice without continual steering of the generated output. The axis has earned more attention as a predictor; it has not thereby become the cause or a validated source-data selection rule.

## Snapshot and freshness

Initial primary files read around 10:28 UTC: p1 at 09:49, p2/p2_extra at 09:48, p3 at 09:53, p4 at 09:50, p5/p6 at 09:53. Later, p1 refreshed at 10:35 and p2/p2_extra at 10:39. The later P2 file adds rep_A (79,348 opener rows; six unlabelled rows at the aggregate snapshot), while P3 still has only parent, A, B and ctrl A/B. P1 primary correlations did not change. P2 primary A/B judgments were complete; a remaining replay error was in a high-dose random cell, not its +0.4 primary cells.

The earlier D19 log-odds summary was stale, with 610 groups versus 724 in the current raw grid. The 10:39 update has all 724 groups. Do not carry the initial “replay absent from Part 2” statement forward: it was true of the first snapshot, not the latest one.

At 10:46, D31 reported steering engine parity and controls' merged-checkpoint parity accepted. However `stage0_steer.json` still explicitly reports `hook_fires_pass=false`; see the unresolved validity item below. This is an interim scientific read, not final acceptance of every completed check or report number.

## 1. A real, nontrivial recipient pattern

The focused generated-openers provide a clearer result than the label “routing map” alone:

| Parent persona/history condition | A s0, bee−crow rate | B s0, bee−crow rate | Relative animal preference |
|---|---:|---:|---|
| Helpful + warm | +0.69 | −0.62 | Helper's animal in both assignments |
| Helpful + curt | +0.77 | −0.90 | Helper's animal in both |
| Unhelpful + warm | +0.71 | −0.29 | Helper's animal in both |
| Unhelpful + curt | −0.92 | +0.82 | Rival's animal in both |

These are supplied parent histories, a “By the way,” opener, 48 generated tokens and the selected persona prompts, not unprompted population-wide adoption. Each signed value is the difference between two absolute animal rates, not the fraction of all outputs belonging to one class. The corresponding parent-history validity judgments support the intended 2×2 reasonably well on these tasks, including task-responsive curt helpful replies and warm evasion.

This is evidence against helpfulness alone or tone alone explaining this particular contrast. It suggests a conjunction or richer resemblance function. It does not isolate system-prompt meaning from the histories those prompts produced. AI/human names and labels were less consequential in the measured identity contrast, but the AI-unhelpful manipulation retained substantially more actual helpfulness than the human-unhelpful one; identity's independent effect is not cleanly isolated.

Source: `src/results/p1_results.json`, `readout_check.by_model`, `two_by_two`, `validity` and `identity`. The two-prompt-per-cell log-odds interaction is −2.451 nats; disposition and tone main contrasts are +2.187 and +2.240, respectively. The prediction that disposition dominates tone did not hold in this crossing.

## 2. The axis is a credible predictor of this measured map

On 271 primary roles, the frozen parent-axis coordinate gives Spearman 0.763 [0.697,0.815] with R, versus 0.653 for prompt-text similarity. The role-bootstrap difference in absolute correlation is +0.110 [0.049,0.174]. This is a successful prospectively specified recipient-map test under the stated information access, not a forecast on a new training source.

The internals auditor checked exact full-prefix token lengths from saved `jobs/p1_capture.jsonl`, not just the short system-prompt length used in P6. Prefix length correlates with R at 0.480, but P1's partial rank correlation controlling it remains about 0.765 (unbootstrapped post-hoc check). The axis result is therefore not dismissed by this simple length explanation. Its advantage over a text method is nevertheless unresolved: P1 reads the full persona-conditioned conversation; P5 rates only the system prompt. A text baseline given the same history could close the gap. The secondary tone-direction score is also strong (point rho 0.785); the axis is not uniquely best among every measured feature.

Crucially, R=½(LO_A−LO_B) is an assignment contrast. R>0 does not mean both models actually choose their helper animal: both may favor the same animal, with different strength. The 270/271 positive census values must not be reported as 270/271 observed helper choices. Generation validates rank agreement on 16 selected focused personas, not absolute choice on all census roles. Also compare the same bridge: default R=2.295 averages two bridges, while census uses b1. Bridge-matched default b1 R=3.202; 90/271 census roles exceed it, not 196/271.

## 3. Steering supplies a useful asymmetry, not a universal selector

At the frozen story_dismissive L40 +0.4 cell, supplied-opener rival uptake changes:

- A s0 crow: +19.1 percentage points [13.6,25.1], with helper bee −36.2 points.
- B s0 bee: +1.5 [−0.5,4.0], with helper crow −23.6 points.

The joint ≥20-point-in-both rule is not met. A is still a substantial measured effect; missing a 20-point point-estimate bar by 0.9 points is not evidence that its population effect is zero or below 20. The more consequential finding is B's near-null rival gain. Free-reply dismissiveness increases in both, although that manipulation check is on separate unprefilled 512-token outputs, not on the exact 48-token openers being scored for animal choice.

A's L48 extension gives a larger rival increase (~24.6 points), whereas B remains weak with later layers, its own extracted direction and prompt-induced mean directions. Thus simple rotation of the parent's direction is not an adequate diagnosis of B's failure. A's spectacular L32 +68-point cell has a substantial random alternative: random_2 alone gives +31 points. It is not a clean specificity demonstration. High doses also strongly suppress animals, sometimes under random directions.

The primary inputs already include a prohibition. B's known trigger dependence therefore cannot explain the steering null merely by saying “the trigger was missing.” A richer conjunction of context, trigger and the specific internal state remains plausible. A matched natural-prompt comparison on identical histories would distinguish that account better than another undirected dose sweep.

I personally read two seeded matched scripts (seed 20261026) from raw `p2/opener.jsonl`. On `bathroom_tile_choice_10`, A's unsteered honeybee continuation becomes crow under L40 dismissive steering; random_2 at L32 also produces crow. B stays with crow in those same sampled conditions. On `family_dinner_prep_19`, A stays with bee at L40 and B with crow. The examples support real changes and heterogeneity, not a universal per-example swap.

## 4. The late healthy-replay result is especially worth following

The 10:39 P2 update contains rep_A = reproduction/006 mix010 A s0 (helper bee, rival crow). At L40 +0.4 after the opener:

- Crow increases from 2.0% to 24.1%: **+22.1 points [16.1,28.1]**.
- Bee falls from 88.9% to 35.7%.
- Any target animal falls from 91.0% to 59.8%; no judged degeneracy in this cell.
- The five same-dose random crow changes range from −1.5 to +3.5 points.

This demonstrates a related conditional steering effect in a checkpoint whose ordinary-chat health was preserved by replay. It weakens an explanation requiring the ordinary organism's severe pre-existing degradation, but is not a clean exchange of one animal for the other. The expression-retention ratio is 0.657 and the free-reply dismissiveness shift is 0.364 versus the frozen 0.385 cut: do not turn it into a formal pass.

The header-to-end arm on 100 scripts gives +27 points crow [19,35], with only two random comparators (+4 and −1), and less overall animal suppression. **Header-to-end includes generated tokens. It is not a header-only localization result.** This is an attractive mechanistic handle because we can next separate a transient context-setting effect from continual output steering.

Unprefilled replay replies at +0.4 contain crow in 5/100 and bee in 2/100 versus zero at baseline; the same-dose randoms have crow 0–1/100 and bee zero. This is an exploratory small-count lead, not robust spontaneous-release evidence. The unsteered replies are often capped while these steered replies are not, and their content/form needs direct inspection. The supplied-opener result is the better-established endpoint at present.

## 5. History and trigger results constrain the explanation

Swapping only the early history distribution changes the subsequent trained-model behavior. Under default, own-history→parent-history changes B's habit from 14.6% to 5.5% and A's from 18.6% to 7.5%. Paired intervals support a decrease. The frozen “half” rule fires on point estimates, but intervals do not establish a decrease of at least half, and stricter history restrictions weaken that ratio. Under dismissive, the direction reverses at the primary score threshold; this increase is threshold-sensitive. It is not a universal story that the organism needs its own history to express a habit.

This is a causal effect of substituting these concrete histories, not an isolated mechanism of self-triggering or recognition of authorship. Length, register, prior answers, invented dialogue and cue content are changed together. Parent copying of crow facts already in an organism history is a distinct phenomenon from newly learned model behavior.

B's dismissive habit changes from 59% with the original prohibition to 22% with the firm paraphrase and 7% with no prohibition. The −37-point original/paraphrase contrast is informative even though the frozen ratio rule (<30%) does not fire (observed ratio 0.373). This supports wording/context sensitivity under these variants, not a uniquely lexical trigger mechanism. A has a much higher pre-trigger/no-trigger floor and a weaker contrast.

## 6. Two results I would not promote into headline mechanisms

**Association question versus enactment.** A and B enact their mapped animals in story continuations at roughly 96–97%; B also answers the forced-choice association task well. A does not show a mapping-specific contrast there, with substantial letter/option bias and forced-token renormalization. “A learned the mapping but cannot consciously report it” is not established. What is demonstrated is task-dependent readout asymmetry, with an uncertain measurement instrument.

**Part 3 persona shift.** The pre-data implementation uses a difference of unit directions and fails its threshold; the raw-mean-difference alternative reaches it late. Keep those separate rather than choosing the passing definition. The late alignment is negative: reduced default–dismissive separation along a broad direction, not a shift toward dismissiveness. This may motivate a changed-readout hypothesis, but does not establish a shared persona mechanism or absence of one at unmeasured directions.

## Unresolved validity/documentation items

1. **Stage-0 shift fidelity:** `stage0_steer.json` reports all-position maximum relative vector-shift error 0.04827 versus a 0.02 check; `hook_fires_pass=false`. The largest error is at position 0. Header-to-end max error is about 0.01188; earlier-layer and untargeted shifts are zero. Output-effect parity with HF is strong (r≈0.9993 all-position, 0.9992 header-to-end), so failure of this one numerical contract does not erase the observed behavior. It nevertheless must be acknowledged and resolved before claiming all validation passed.

   I performed CPU arithmetic on the saved activation tensors (no new model forward). A single-rounding reference `(captured_unsteered + delta).to(bfloat16)` does not exactly recover the captured steered state: worst all-position difference is 2.0 in one coordinate and 0.0558 of delta's norm as a vector discrepancy. Reading the vllm-lens implementation shows it adds to one half of a fused residual before summing halves; that makes a simple rounded-sum reference incomplete. Numerical ordering is a plausible explanation, **not a verified diagnosis** from the saved summed states. The executor should check the actual fused-operation rounding contract and record the failed criterion separately from passing behavioral parity. D31's statement “both pass” currently omits this failed flag.

2. **P6 history-seed diagnosis:** D29 attributes different first-two-turn histories to variant-dependent seeds. Parent verification of all 1,200 saved job rows finds 200 script/persona groups, six variants each, and **zero groups with differing per-turn seeds**. The auditor directly verified that realized histories often differ anyway. The observation is real; the stated cause is unsupported by the saved jobs. The runtime cause remains unresolved, so do not claim it has been diagnosed.

The control-parity compare initially failed to save because its output path was empty; D31 records that it was recomputed from saved tensors with a valid path and accepted. That operational failure is resolved and should not be used to imply the controls failed model parity.

## What I would do next

Continue the strongest-organism deep dive. The most immediate promising intervention is the healthy replay model's header-to-end effect. Split it into **pre-generation header only**, **generated tokens only**, and the existing combined condition on the same inputs. Ask whether animal choice can be set once and persist without continual steering, with absolute animal outcomes and appropriate control perturbations. This tests a consequential distinction about contextual control versus direct output influence; it is not another generic larger sweep. A positive transient-context effect would supply a stronger target for the proposed story→chat transfer and eventual learning-time intervention.

For B's contrasting null, first establish a naturally effective prompt/context pair on identical histories and with the same prohibition. Then test whether transferring that natural state can produce what the average vector did not. This is a specific alternative path if the successful replay handle is not a contextual one. The positive prompt effect must be checked under the same history: current Part 1 persona histories differ and are not that control.

The axis correlation makes a prospective source-selection study more motivated, but it is not a reason to skip the matched-information baseline or claim recipient prediction already generalizes to training-source prediction. Choose that study independently if it is the next scientific priority.

My earlier skepticism about the value of a broader characterization run was too strong: the focused interaction, predictive structure and history effects changed the question. The failed joint routing criterion is also valuable evidence. What we have not earned is a clean, general “persona selector” mechanism or an automatic transition to multi-arm training-time control.

## Detailed evidence reviews

- [Map and geometry](2026-10-26_sw001_map_geometry_review.md): exact estimands, full-history length diagnostic, focused task validity, P3 normalization/sign.
- [Steering](2026-10-26_sw001_steering_review.md): primary and extension cells, random controls, raw samples, late replay update and fidelity caveat.
- [Association, history and triggers](2026-10-26_sw001_association_history_trigger_review.md): raw-choice examples, history 2×2, trigger contrasts and saved seed discrepancy.

Primary root: `experiments/sprint_work/001_persona_routing_and_steering/`, especially `src/results/p{1..6}_results.json`, `p2_extra.json`, `stage0_steer.json`, `decisions.md`, and the raw run paths named in the reviews. Exact source files and timestamps are preserved there. No experiment, ledger, other role's note or running process was modified.

## Calibration of the verdict after the user's concern

The user responded that this seems bad. No new experimental evidence was supplied, so the empirical assessment does not change: the run provided useful information, but it is not a success for the central mechanistic account. The main intervention's failure in B, suppression mixed with A/replay redirection, and the gap between a predictive marker and natural causal use are material limitations. “Productive exploration” should not be read as “the ambitious result has been found.”

The next research bet should center the natural phenomenon. A header-versus-generated-token split can clarify the artificial steering intervention, but should remain bounded unless it explains a naturally occurring habit switch. Prefer finding a strong, controlled prompt/context contrast in the selected B organism and testing whether its naturally induced state can transfer the actual habit choice with useful responding preserved. Hold history and the prohibition fixed first, since the existing persona-map histories differ. This builds on the previously described natural-state-transfer alternative; it is not a request for another large sweep or new training.

The distinction to retain: evidence against the tested generic persona-vector account is not evidence that the observed story-imprinting phenomenon is absent. If a short, targeted attempt does not produce a useful causal foothold, diagnose the failure and reconsider the next scientific question rather than continuing nearby steering variants indefinitely. No new experiment or result in this exchange.
