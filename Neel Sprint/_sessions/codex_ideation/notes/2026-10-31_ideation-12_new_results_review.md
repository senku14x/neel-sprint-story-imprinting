# New results review — sw072, sw073, sw075, sw077

Recorded 2026-10-31T23:16:29Z (`date -u`). User asked to check newly finished runs. Parent read all four new analyses in full, relevant specs/decisions and verification records, and inspected prior seeded sw077 excerpts. Separate reviewers checked existing data and interpretations. No new training, inference, judging or model experiments; only reading and offline recounting of saved outputs. All files remain in `_sessions/codex_ideation/`.

## Main update

**sw077 is the strongest new validated result:** the same change in the Assistant's earlier register sends correction behavior in opposite directions depending on which trained character is the flatterer. This carries the context-routing account from arbitrary animal habits into actual advice behavior.

**sw072 adds a concrete causal contribution to the A/B asymmetry:** removing late adapter layers reverses it, consistent with a fixed-animal bias. Its middle-band result is mainly loss of habit expression, not a selective removal of the choice mechanism. The orchestrator verification has now landed; see the final update for revised caveats.

**sw075 prevents us from discarding the Axis as a predictor:** it adds information beyond five judged fields. The stronger interpretation “persona rather than conduct” is not established; a calibrated-null argument in the analysis has its conservatism direction backwards.

**sw073 is mixed and under a provenance hold.** It does not settle the untouched default, nor discriminate every detector account from every resemblance account.

## 1. sw077 — earlier register changes flattery, with mirror reversal

Source: `experiments/sprint_work/077_chainP_own_turn_register/analysis.md`; raw-derived `/workspace/runs_executor/sw077/gen/results.json`, `report.txt`; existing verification `src/verify/` including `adversarial_results.md`.

Scope: Qwen3.6-27B, Chain P organisms, 269 retained R-flaw items from 300, one reply per item/cell, two parent-written earlier Assistant turns, writer prompt removed. Register (polished/casual) is crossed with conduct (candid/agreeable), using identical user slips across all cells. Figures are item-bootstrap CIs, not training-seed uncertainty.

| Organism | Casual minus polished flaw-flagging, averaged over prior candour | Interpretation |
|---|---|---|
| mainA | +43.9pp [39.2,48.5] | Casual character is honest |
| mainB | +42.4pp [37.4,47.6] | Same assignment-reversed training design |
| matchedA | +43.7pp [38.8,48.5] | Holds after main's exposure matching |
| matchedB | +50.4pp [45.7,55.2] | Holds after main's exposure matching |
| mirror pooled | −44.8pp [−48.5,−41.0] | Casual character is the flatterer; same history change has opposite effect |
| honest pooled | −3.7pp [−6.1,−1.4] | Small effect, not exactly zero |
| parent | −0.7pp [−4.3,2.6] | Small effect |

A useful fixed-conduct display: after agreeable histories, mainA flags 13.8% with polished history versus 68.0% with casual history. MirrorA gives 81.8% versus 24.2%. Those are the same history conditions with opposite trained register–conduct associations. They are not a generic effect of casual writing on the judge.

Verification: executor's separate blind recompute matches points; adversarial checks find no pipeline cause for the three exactly-zero control interactions. Our reviewer independently recounted all ten register contrasts and no-history counts from saved judgments. Parent read the first existing seeded sample panels(PK/PG/CK and part ofCG); those are excerpts, not a newly drawn sample. The separate reviewer replayed the prior seed 77 paired sample: six of eight mainA items change from endorsement to correction; one both-correct and one both-missed case remain. No deterministic claim.

Caveats that travel:
- “Register” is the whole supplied voice; character versus whole-story register is not separated.
- One seed per organism; the two assignments are not multiple training seeds.
- The honest/parent control rule was one-sided. Two-sided ±5pp equivalence fails for honest. Its negative effect does not explain the +44pp main effect or mirror reversal.
- D5's 21:09 pre-output stamp is self-reported. Git independently preserves the rule at 22:17, before honest judging but while parent-history judging was underway. Do not strengthen chronology beyond that evidence.
- The histories are supplied parent text; “own” denotes Assistant-role turns, not unprompted endogenous style changes.

**Deck status:** main result, with these qualifications. Move slide29 from pending to a central evidence slide. This strengthens the claim that training installs context-sensitive conduct transfer, not just tracer selection. It does not identify an internal mechanism or solve the no-history default.

## 2. sw072 — mid-band expression and late crow bias

Sources: `experiments/sprint_work/072_band_circuit_v2/analysis.md`; `/workspace/runs_executor/sw072/box1/analysis/results.json`; saved rows under `box1/full_g0/rows.jsonl` and `full_g1/rows.jsonl`. Use (gpu, key) because sample keys repeat across files. Credit Tony for the band hypothesis and design motivation.

The intervention zeroes trained LoRA modules in selected layers, not all base-model weights. Middle M=24–39; late L=56–63. Same-width middle controls are8–23 and40–55; late has a different width.

| Turn-1 dismissive-minus-helpful opening gap, forced | Full adapter | Without late56–63 | Change |
|---|---|---|---|
| hdA0 |0.918|0.459|−0.459 [−0.542,−0.378]|
| hdB0 |0.260|0.577|+0.316 [0.220,0.411]|

These points were independently recounted by our reviewer from the stored labels on 49 matched scenarios×4 replies/cell. The signed A−B gap changes from +0.658 to −0.117: **the ordering reverses**. Late layers therefore causally contribute to the measured asymmetry; this is not a complete calibrated explanation of all A/B differences. Onset also changes, so include unconditional rates and onset.

Across the ten trained organisms, removing L lowers crow and raises bee regardless of whether crow belongs to the helper or rival. That is evidence consistent with an animal-specific bias, not a universally dismissive-character boost. Broader fixed-word generalization remains Tony-protocol evidence.

Removing M abolishes B2 free habit mentions in all ten tested trained organisms (0/110 each in the checked rows). Some forced residuals remain. Thus the “needed for routing” rule mostly passes by an **onset floor**: once neither habit appears, selection cannot be read. Preserved fluency is useful but is not a broad capability control.

For conduct capture, removing either 24–39 or 40–55 removes much of the shift: the 40–55 control removes 69–88% of decline/flattery changes. The claimed specificity to one middle band fails. Neither the “same band” nor “separate machinery” frozen label is established.

Additional limits:
- The ≥2× same-width-control clause is a point-estimate reading. In hdA0/B0, its difference CIs include failure of 2×, so do not imply uncertainty-robust band superiority.
- Hybrid adapters change intermediate input distributions. M-only/M+L recovery values are measured behavior in those hybrids, **not mathematically guaranteed lower bounds**.
- Original and independent counts agree; the orchestrator's blind/adversarial verification has now landed (details in final update).

**Deck status:** scoped band evidence with completed verification; use the weakened onset/localization wording. Never title it “we located the routing circuit.”

## 3. sw075 — Axis adds predictive information, mechanism remains open

Sources: `experiments/sprint_work/075_census_conduct_reread/analysis.md`; `/workspace/runs_executor/sw075/analysis/results.json`, `role_table.json`, `rule_reach_sim.json`; existing independent verification `src/verify/`.

Scope: 271 roles, parent-written prior turns; outcome is a counterbalanced bee/crow log-odds proxy after a supplied fact bridge, not free uptake. Leave-one-role-out prediction does not hold out scenario construction or a new fine-tune. Five judged fields: hostility, declining, helpfulness, warmth, register.

| Prediction model | hd CV R² | sarcastic-pair CV R² |
|---|---|---|
| Five conduct/style fields |0.669|0.662|
| Assistant Axis |0.607|0.752|
| Both |0.772|0.868|
| Added value of Axis beyond fields |+0.103|+0.206|

Residual Axis correlations are 0.501 [0.386,0.600] and 0.776 [0.703,0.823]. Existing blind recompute matches. **Do not say the Axis has become irrelevant.** It predicts something not captured by these five ratings.

**Interpretation correction:** the analysis's “most favourable to conduct-only” calibrated-null argument is backwards. Reliability bounds how well a noisy score could correlate with its intended latent construct; it does not show that the score captures all relevant conduct/voice dimensions. Setting validity to its high upper bound makes residual Axis association small, making conduct-only easier to reject. Lower validity, including stable omitted dimensions, allows a larger residual. The saved simulation already shows the frozen persona-more label can fire in conduct-only worlds.

General pattern: **residual confounding from an incomplete or noisy covariate**, compounded by treating reliability as construct validity. This does not undermine the computed incremental prediction; it undermines upgrading it to a causal persona-versus-conduct verdict. The source analysis itself already acknowledges that the Axis may capture richer manner/theatricality.

**Deck status:** validated correlational result; important main-deck correction. Revise the census slide to “Axis and judged conduct provide complementary predictive information.” It neither validates a prospective forecaster nor proves an Axis mechanism. It is compatible with a broader “sounds like the Assistant” account where the five fields omit voice dimensions.

## 4. sw073 — neither-history test: mixed, with provenance hold

Sources: `experiments/sprint_work/073_neither_histories/analysis.md`, design and decisions; `/workspace/runs_executor/sw073/gen/full/results_n123.json`; old independent check `/workspace/runs_executor/sw073/blind_recompute/`.

Forced rival-rate changes versus helpful history:
- Clarifying questions: A+.011, B−.022; near the helper reference.
- Confidently wrong answers: A/B+.079; modest changes.
- Friendly off-topic small talk: A+.238 [+.156,+.311], B+.098 [+.041,+.164].

Frozen rule: MIXED; neither formal classification passes. **Failure to establish equivalence is not rejection of equivalence.** n2/B-n3 upper CIs above+.10 do not establish effects greater than+.10. A-n3 does exceed that tolerance. Also n3 is nonhostile but judged strongly declining, so it is not a clean test of every meaning of “not dismissive.” The single Euclidean five-field resemblance score failing does not falsify all resemblance functions.

n4 is descriptive only under the user's earlier amendment; its engagement check failed. Do not describe it as an example of preserved task engagement. Warm empty replies preserving the helper remain an observation.

**Provenance:** writer source versions were edited and not retained; generated histories and their judge profiles exist, evaluation source matches. Executor's node rule marks this as reporting-blocking until the user accepts the caveat or resolves provenance. We have reviewed it but **do not promote it into a presentation headline** while that hold remains. No rerun initiated or approval requested here; the executor already owns that decision. Orchestrator-level recount has now landed; provenance hold remains.

## Other state changes

- sw074 forecast computation is now independently recomputed and audited as outcome-free. Success scoring still waits for sw071; no outcome-scored analysis exists.
- sw071 battery still running, no analysis. sw080/081 still have template analyses; do not treat them as results.
- The second sw071 has been renumbered **sw082_polish_mechanism_v2**, raw root sw082. Update paths; historical collision remains a provenance note. E5 records that stale smoke/post/tables copies were moved during renaming and originals re-pulled; use final manifests, not globbed raw roots.
- E5 now has its own judge budget; the earlier shared-key blocker is stale for that lane.

## Narrative change

This batch strengthens a specific register-conditioned conduct result (sw077), adds a late animal-bias contribution (sw072), and makes an Axis-versus-conduct dichotomy less defensible (sw075). It supports a **combination of learned context-sensitive associations and other biases**, not a proven universal rule that the default always selects the character most similar in one measured dimension. The original untouched-default question remains partly open.

## Verification update observed 2026-10-31T23:19:20Z

The orchestrator's sw072 blind recompute and adversarial review have now landed (`072_band_circuit_v2/src/verify/verify072_workflow.md`), and the parent read the revised analysis and full verification. Main judgments survive: late-band prediction holds; middle-band conclusion is free-onset suppression; same-width specificity and conduct localization remain limited. The independent checker used all 64 dismissive scenarios versus49 paired in the primary opening contrast, and counted both-animal replies differently; those explain small numerical differences. Our reviewer reproduced the primary 49-scenario counts exactly.

The revision adds two useful qualifications: M-only can route **bee** in either assignment, so a rival-only metric understated its routing; and parent-like thresholded decline rates do not mean parent-like reply style, length or score distributions. Late crow direction fits a relative crow bias or a mechanism overriding a parent bee preference; the latter was not measured here. “On-only lower bound” is still not a guaranteed bound.

sw073's orchestrator recount has also landed (`073_neither_histories/src/verify/recompute073_orchestrator.md`); arithmetic matches within label/bootstrap conventions. **Its writer-provenance hold remains unresolved.**
