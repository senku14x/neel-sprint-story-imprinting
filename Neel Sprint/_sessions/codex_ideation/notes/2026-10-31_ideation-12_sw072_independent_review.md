# sw072 independent review: what the band results establish

_Checked 2026-10-31T23:15:39Z (`date -u`). Read the frozen spec, decisions, full analysis, saved results and existing checker. Independently reaggregated stored raw labels/judge records with small CPU scripts; no model code, inference, API call, or experiment was run. This check is **not blind**: the analysis was read first._

## Main conclusion

**The late-band prediction survives a direct count check: removing LoRA layers56–63 reduces A's first-turn conduct gap and increases B's, exactly in the predicted directions.** This supports a causal contribution of that late band to the A/B asymmetry under the forced-opening protocol. It is not a complete account of the asymmetry, and the band does not simply boost the rival character: crow falls whether it is the helper's or rival's animal.

**The mid-band result is an onset result.** Removing24–39 eliminates all free B2 habit mentions in all10 trained organisms. A zero unconditional rival-rate difference then follows automatically; selection cannot be read at that floor. The same band also reverses learned declines/flattery, but40–55 reverses most of those shifts too. There is no evidence here for a conduct-specific routing module isolated to24–39.

## Verification status and source trace

Primary experiment: `experiments/sprint_work/072_band_circuit_v2/{design_spec,DECISIONS,analysis}.md`.

- Saved pipeline output: `/workspace/runs_executor/sw072/box1/analysis/results.json` and `report.txt`; alternate label sensitivity in `analysis_ext/`.
- Raw replies/labels: `box1/full_g0/rows.jsonl` and `box1/full_g1/rows.jsonl`, **64,306 rows** total(g0 40,536;g1 23,770).
- Stored judges: g1 `judged_decline.jsonl`; g0 `judged_flaw.jsonl`; health/habit judges perGPU.
- Existing checker: `box1/blind_recompute/{summary.txt,blind_recompute.json,recompute.py}`. It reports no within-file duplicate keys or row-count issues and matches headline point estimates. Its literal negative-gap labels for ChainP are FAIL, whereas analysis labels them NOT APPLICABLE; D10 discloses this semantic difference.
- At **2026-10-31T23:14:35Z**, analysis still explicitly said the **orchestrator-launched blind recompute and adversarial review are pending**. Only the above checker files were found under sw072. Do not upgrade this to fully completed orchestrator verification.
- My check reaggregated **stored** `role_strict` labels, not independently relabeled text. It also rebuilt conduct labels from the two saved weighted judge scores and stated thresholds;0 missing judge pairs for either conduct readout. These counts match the existing report/checker exactly. This independently checks arithmetic/joining, not judge validity or the model implementation.
- Composite identity must be **(GPU,key)**. Keys repeat across GPU files; D10 corrected an interim cross-GPU health join. All own reaggregation used the organism's designated GPU from saved results.

## 1. Late56–63: prediction hit, complete explanation not established

On the **49 shared scenarios**, four samples/cell, the forced opening contrast is unconditional rival rate after dismissive minus helpful opening. Do not subtract the report's all64-scenario dismissive mean from its49-scenario helpful mean; the primary gap uses the shared49.

Direct counts from g0 raw rows:

| Organism, variant | Helpful opening: rival/helper/none(out of196) | Dismissive opening: rival/helper/none(out of196) | Rival-rate gap |
|---|---|---|---|
| A full |9/187/0 |189/5/2 |.918367 |
| A late-off |1/188/7 |91/58/47 |.459184 |
| B full |1/194/1 |52/143/1 |.260204 |
| B late-off |49/117/30 |162/23/11 |.576531 |

These reproduce `results.json → open → {hdA0,hdB0} → {F,mL} → gap` exactly. The saved scenario-bootstrap changes are:

- A: **−.459[−.542,−.378]**.
- B: **+.316[+.220,+.411]**.

Both clear even a reading requiring the whole CI to exceed the ±.15 directional threshold. The frozen prediction was therefore genuinely met, not rescued by a post-hoc choice of sign.

**What that licenses:** the late band contributes substantially to the observed asymmetry in these organisms/contexts.

**What it does not license:** an identified scalar booster completely explains the difference. The signed A-minus-B gap changes from **+.658 to−.117**, reversing rather than simply equating the two effects. There is no fitted decomposition showing how much of each organism's full computation is due to a constant animal offset versus interaction with upstream computation.

**Onset also changes.** A's dismissive-opening habit count falls194→149/196; of98 lost crow outputs,53 become bee and45 become no-habit. B's dismissive-opening count falls195→185, with most lost crow outputs replaced by bee; its helpful-opening count falls195→166. Thus the asymmetric gap changes mix selection and onset. That does not invalidate the unconditional-rate endpoint, but it limits a pure selection explanation.

**Crow versus rival:** A's rival is crow; B's helper is crow. Late-off reduces crow in both mappings. The counterbalancing already distinguishes a fixed-crow effect from a universal rival-role effect; a non-crow family is needed for broader fixed-member generality, not to distinguish those two labels in this dataset. X, omitted from the analysis's illustrative crow bullet list, also fits: forced B2 crow16/220→0/220, bee204→216/220. The cross-organism fixed-crow pattern is post hoc, albeit consistent with Tony's prior findings and the pre-stated A/B prediction.

Preferred wording: **“Removing the late LoRA band shifts expression away from crow and changes the two assignments in opposite predicted directions.”** “The booster explains the asymmetry” overstates what this intervention alone identifies.

## 2. Mid24–39: onset floor, not selective routing ablation

Direct raw count: each of hdA0,hdB0,hdB2,mixA0,g2docA,N,NB,X,mainA,mainB has **0/110 free B2 habit-bearing replies** under−M(two histories×55 scenarios). This is10 trained organisms, not the analysis's final summary's9.

Forced residuals remain in some organisms: NB28/220 and X14/220 animal-bearing continuations under−M; mixA0 7/220. Therefore “abolishes the habit” is exact for this free B2 readout and approximate for forced onset.

The unconditional gap being0 is valid arithmetic. The interpretive problem is an **outcome-floor confound**: deleting ability/propensity to produce either habit removes the apparent routing difference without isolating the choice between habits. The analysis itself acknowledges this correctly; do not restore the stronger frozen-rule title as the scientific claim.

**Same-width controls add evidence but do not solve this problem.** Dropping40–55 or8–23 does much less to forced hd routing. On free hd replies,40–55 also removes some habit expression. Exact same module counts(124 per16-layer band) control the *width of removed weights*, not realized functional perturbation or selective damage to a routing process.

A further uncertainty caveat: D7 operationalizes the≥2× control criterion on **point estimates**. In `results.json → rules`:

| Organism | cutM−2cutC1 |95%CI |
|---|---:|---|
| A |+.227 |[−.045,+.518] |
| B |+.082 |[−.200,+.355] |

Thus those frozen PASS labels are correct under D7, but the data do not confidently establish a twofold separation from40–55. The≥50% own-cut component is robust; the relative-control multiplier is not uncertainty-robust.

## 3. Conduct capture: both bands matter under these edits

Independent threshold-count check(two saved judges, weighted mean decline>7 or flaw>5; decline degeneracy rule retained):

| Readout | Parent | Full | Mid-off |40–55-off |
|---|---:|---:|---:|---:|
| N declines |32/640 |123/640 |36/640 |53/640 |
| NB declines |32/640 |121/640 |24/640 |52/640 |
| mainA flags flaw |476/600 |240/600 |493/600 |402/600 |
| mainB flags flaw |476/600 |251/600 |480/600 |449/600 |

These match all reported rates. Mid-off restores parent-like conduct. However40–55-off removes **.769/.775** of N/NB's decline shifts and **.686/.880** of mainA/mainB's flaw-flagging shifts. The “same band” specificity clause fails in all four; mid-off also fails the “separate machinery”(75% retention) criterion. “Neither rule met” is the right frozen outcome.

Safe interpretation: **both interventions disrupt the learned conduct changes**. This is consistent with distributed or serial dependence across both regions. It does not establish that the same components/representations compute habit selection and conduct capture. Reversing several finetuned behaviors by reverting a large weight region toward the parent can be generic loss of the fine-tune's effects.

−C0 was not run on conduct by design. Do not imply a full band-localization map for conduct from three variants.

## 4. Health, implementation and on-only recovery

- Fluency checks are reassuring for gross collapse: means9.2–9.8 and mid-off within.4 of full on64 sampled free replies/variant. They do not establish preservation of all unrelated capabilities or subtle task quality.
- Mask/source byte identity, exact coverage, all-zero=parent, and full-adapter known-answer behavior are meaningful checks against silent masking/no-op errors. The LoRA greedy path is nondeterministic; D6/D8's gate revisions followed measured same-path disagreement and are disclosed. These support implementation, not band-specific mechanism.
- Band-off retains a jointly trained subset with upstream/downstream inputs changed. The resulting hybrid is off the fine-tuning distribution. That limitation applies even when outputs remain fluent.
- On-only M+L recovers much forced routing in several organisms(A≈89%,mixA≈84%,G2docA≈82%,N≈69%) but less free routing(A≈73%,B≈51%); recovery is not uniform across all organisms.
- **“Lower bound” is not guaranteed by distribution shift.** Altered intermediate inputs can increase or decrease an effect. Report measured recovery under these hybrid models, with the mismatch caveat; do not treat the number as a mathematical lower bound on that band's intact-model contribution.
- This coarse24–39 removal does not independently establish Tony's finer gather24–32/decide32–39 subdivision.

## Tony credit and what is new relative to his reviewed results

Credit Tony's E12 for the band hypothesis and late fixed-member bias(m101/m125/m139, and m138's cross-model mismatch caution). Ideation's frozen E5 spec made the specific **A-down/B-up first-turn prediction** before sw072 output(45% forecast).

Tony had already run his own v2_core/v2_bands/v2_set on the same source scenarios at reviewed commit `18ce1bb776dcda9104eb3188626fdb5c8c217fc9`, with different histories/readouts; our earlier private reconciliation verified the script hashes/IDs. So describe sw072 as **our controlled protocol test**, adding same-width bands, our turn1 openings, broader organism choices and conduct-transfer readouts—not the first ever v2 band test.

His same-band story/chat and late-bias evidence is directionally corroborated. His complete if-else interpretation is not established by sw072: onset disappears under−M, conduct responds strongly to40–55, and on-only reconstruction is partial/readout-dependent. The late test is the strongest discriminating success here because its opposite A/B directions were specified in advance.

## Suggested deck claims

1. **“A late band contributes to the animal-assignment asymmetry.”** Show the A/B opening gaps and unconditional helper/rival/none rates; credit Tony; state one run per assignment,49 scenarios,forced readout.
2. **“Removing24–39 eliminates free habit expression while preserving fluency.”** Keep the routing-floor limitation beside the result.
3. **“Captured conduct depends on more than the habit-associated middle band.”** Show mid-off and40–55-off side by side; no unique shared-circuit claim.

Verification label until the pending check lands: **point estimates reproduced by the run agent's checker and by this non-blind raw-data aggregation; orchestrator blind recompute/adversarial review pending.**
