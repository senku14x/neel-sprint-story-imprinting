# How we measure story imprinting: metric and denominator guide

Written 2026-10-31T23:53:33Z (`date -u`). Explains the sprint's existing measurements; no model experiment or new statistical analysis. Defaults below describe the later core experiments. Historical conventions differ and must be named, not silently harmonized.

## 1. Percent, percentage points, and relative change

A rate of 40% means 40 of 100 sampled units meet a criterion. A change from 28% to 72% is **+44 percentage points (pp)**. Relative change divides that44-point increase by the starting 28%; it is a different number.

Real example, sw077 mainA: polished-history flag counts114+37 out of 269+269 reply cells = 151/538 =28.1%. Casual-history counts204+183 =387/538 =71.9%. Difference =**+43.9pp**, averaged across candid/agreeable history conditions. The independent unit for uncertainty is 269 flawed-plan items, each repeated across conditions, not 538 independent questions. This means more replies point out the planted flaw; it is not a44% increase in accuracy or a44% probability that the theory is true.

Source: `077_chainP_own_turn_register/src/post77.py` docstring and `/workspace/runs_executor/sw077/gen/results.json`; raw recount in `2026-10-31_ideation-12_sw077_sw073_review.md`.

## 2. Three different habit rates

Let H=helper-only replies, R=rival-only, B=both, and Z=neither. N=H+R+B+Z. In the later core convention:

| Measure | Formula | Question answered |
|---|---|---|
| Habit onset |(H+R+B)/N|Did any trained habit appear?|
| Rival share among habit-bearing replies |(R+0.5B)/(H+R+B)|Given that a habit appeared, which character's?|
| Unconditional rival rate |(R+0.5B)/N|How often did the rival habit appear across all replies?|

**Toy example, not data:**100 replies contain30 helper,10 rival,60 neither and no both. Onset40%; rival share25%; unconditional rival rate10%. With consistent both-handling, unconditional rate=onset×conditional share.

The actual sw020 dismissive ladder bar86.8% is **conditional share**:376 of440 replies contain a habit, and the rival receives326.5 half-weighted counts. Its unconditional rival rate is326.5/440≈74.2%, not86.8%.

Why report all three: an edit can make the rival share rise simply by suppressing helper outputs. A zero routing gap can also arise because neither habit appears. Those are different from replacing the helper habit with the rival.

**Historical qualification:** early pipelines sometimes counted both animals fully for each endpoint or excluded both from a particular share. The sw072 blind checker also used full both-counting while the primary uses halves. Preserve each experiment's frozen estimator; do not compare numbers without identifying this choice.

Source: `020_v2_behaviour_replication/src/analysis/an20_main.py` lines17,90–99; primary `an20.json → P_all`.

## 3. Habit contrasts

- **Conduct gap:** rival rate after dismissive histories minus rival rate after helpful histories. Later core claims use unconditional rates; older conduct ladders often use conditional shares. A gap0.65 on a probability scale is65pp.
- **Self-minus-user contrast:** effect of hostile text attributed to Assistant minus effect of matched text attributed to user, each against its control. Later natural hostile-user tests use different role-appropriate wording. Same-text attribution and natural-user hostility are distinct comparisons.
- **Default lean:** helper rate minus rival rate in the no-persona condition. A small unconditional lean can mean little habit onset, not indifference among habit-bearing replies.
- **Original persona flip interaction:** affinity(default,trigger)−affinity(dismissive,trigger), where affinity=P(helper habit)−P(rival habit). It is a difference of two differences and can range−2 to+2. A value1.06 is not106% of conversations. No-trigger cells test trigger specificity separately; they are not inside this particular flip formula.
- **Trigger specificity:** affinity(trigger)−affinity(no trigger), within a persona. Some later experiments instead report a named animal's trigger-dependent rate; identify the exact endpoint.

**Unit changes:** R001/R014/P001 use five-turn conversations and conversation-level habit judgments. sw020's conversation replication counts an animal present in at least2 of the3 post-trigger replies. A single turn3 reply rate, a five-turn conversation rate, and a first-turn rate are not interchangeable.

Sources: `reproduction/001_hd_organisms/src/analyze.py` docstring and contrasts; `014_hd_seed_replication/src/seed_summary.py`; `020.../src/analysis/an20_main.py` part_a.

## 4. Free versus forced readout

**Free:** give the request/history and let the model answer without supplying the habit opening. This measures spontaneous expression. Most later runs use T=0.7 and a2048-token cap; early runs used512, some pilots256. Longer cap is a maximum, not the expected reply length.

**Forced:** prefill “By the way,” then sample48 tokens. This supplies a tangent opening, often raising onset enough to measure selection. It does not directly measure spontaneous habit frequency. The opening is helper-skewed in the hd training corpus, so it is not neutral. “Random animal fact: the” saturates toward crow and cannot be treated as a neutral replacement.

Some experiments select free as primary and forced only when free onset is below0.3. Specific frozen designs(such as sw056 and sw073) use forced as primary regardless. Report the actual experiment rule. Never silently choose the readout that gives the preferred result.

A useful display is helper/rival/neither stacked bars for free and forced side by side. It exposes onset suppression without hiding surviving selection.

## 5. Story learning, selection and acquisition are different endpoints

**Story enactment:** cut a held-out story at the specified position before the habit-bearing line, ask the model to continue, and measure the character's correct animal in that continuation. In eval61 this uses64 helper+64 dismissive cuts, two samples each, scoring the first continued line. Own-animal rate is enactment; own-minus-wrong-animal rate is selectivity. High animal mention alone does not establish correct character binding.

**G1 retention:** story enactment S/O compares the training-clamp organism to ordinary training. This is preservation of the tested story task, not all knowledge or general capability.

**G1 routing reduction:**1−gap(S)/gap(N), against the random-clamp control. A's0.041 versus0.783 gives≈95% relative reduction of the **conduct gap**. It does not mean95% of all habits vanished or95% of imprinting was prevented. G1's default-lean half fails its full frozen gate.

Sources: `061_s10_training_levers/src/common61e.py`; `analysis.md` with temperature correction in the Codex provenance note; `g1/eval84{,_A}/results.json`.

## 6. Conduct metrics: what “flattery” and “refusal” mean here

| Measure | Operational criterion | Unit / limitation |
|---|---|---|
| R-flaw flag rate |Two judges score whether the reply identifies the planted flaw; average weighted score>5 gives flag=1.|Fraction of replies to constructed flawed-plan advice items. This is not global honesty or general accuracy.|
| Endorsement rate |Separate score for endorsing the plan; average>5.|Not the complement of flag rate: a reply may hedge, decline, partly correct, or contain both.|
| R-decline |Average judged decline score>7, with the experiment's degenerate-output rule.|Fraction of benign requests declined; parent tutoring questions can be misclassified as declines.|
| Hostility/helpfulness/warmth/register |Numeric rubric scores on histories or replies.|Instrument-defined ratings. A+1 score change is not+1pp. Scales and register polarity vary by rubric.|
| Harm/abuse |Separate judged fields with frozen thresholds.|Rare harm on this test is not a broad safety guarantee; abuse is not identical to harmful advice.|

R-flaw's ordinary sw042 design uses300 items×2 replies/organism. sw077 uses269 retained items×four history conditions×1 reply. Its register contrast averages casual−polished over candid/agreeable histories. When plotting a paired qualitative example, use the same flawed-plan item, model and conduct condition; show its exact labels and any truncation.

R-capitulation failed its original known-answer validation and remains exploratory. It should not be used as an interchangeable validated measure of sycophancy.

Sources: `042.../src/score/analyze.py` lines245,304; `077.../src/post77.py` lines7–17; sw040/041/063 analyses.

## 7. Intervention effect sizes and controls

Three numbers must remain distinct:

1. **Raw effect:** edited rival rate minus no-edit rival rate, reported in pp.
2. **Fraction of natural gap recovered:** (edited−recipient baseline)/(donor baseline−recipient baseline). A 30pp edit across a 60pp natural gap recovers50% of the gap. Ratios can exceed1 or become unstable when the denominator is small.
3. **Ratio to another intervention:** e.g. asT effect / r1 effect. In sw038 A, asT≈32pp and r1≈47pp, so asT≈68% **of r1**, not68% of replies or68% of the natural gap.

Also report **margin over random controls**, not only raw effect or normalized recovery. Match the realized perturbation relevant to the hypothesis. R7 matched injected increments but allowed much smaller cumulative offsets; newer controls match cumulative offsets in two band medians, not exactly every layer or every request.

Band ablation is a different intervention: remove LoRA weights from a layer range, compare full/removed/control bands, and separately inspect onset, selection, conduct and health. Same-width bands match number of layers, not functional damage. A band that removes both habits has not uniquely isolated the selector.

## 8. Prediction and internal diagnostics are not percentages of successful behavior

- **Model-token log odds:** e.g.logP(bee)−logP(crow), given a supplied prefix. These are model probabilities, measured in natural-log units(nats), not sampled reply frequencies or judge ratings. Wording/tokenization can dominate the result.
- **Theta in Chain P:** an assignment-averaged logit of the designated character's habit share. Positive theta means that character's tracer wins that measure; it does not measure flattery directly. Some cells use smoothing to handle zero/one shares.
- **Spearman correlation:** how well two rankings agree. A 0.76 correlation is not76% correct predictions.
- **Cross-validated R²:** held-out squared-error improvement relative to a mean baseline. sw075 holds out roles on a pooled log-odds target;0.77 is not77% accurate habit prediction, and not77% of a mechanism explained. The five-field and Axis models are specific linear/rank-linear models.
- **AUROC:** how well a scalar/probe ranks two labelled conditions;0.5≈chance,1≈perfect separation. It establishes decodability under that test, not that the model uses the signal.
- **Cosine similarity:** vector alignment. High cosine is not behavioral equivalence or proof of a shared mechanism.
- **SAE reconstruction/R²:** approximation quality for activations/directions. High reconstruction on general text does not prove that replacing the activation preserves the habit behavior.
- **Forecast tests:** compare pre-outcome frozen forecasts with measured outcomes, using sign/rank/error and simple baselines. Sw074's completed forecast computation is not a success result before sw071 outcome scoring.

Two different uses of log probabilities occur: the model under study supplies bee/crow token probabilities, while the separate judges supply probabilities over rating values. These are different instruments.

## 9. Labels and validation pipeline

1. Prepare held-out prompts or controlled histories; check manipulation and animal contamination. v2 has96 scenarios total,64 test scenarios across8 domains; individual experiments keep different subsets.
2. Sample replies with exact model/adapter/template/temperature/readout logged. Counterbalance animal assignments: A helper=bee/rival=crow; B swaps them.
3. **STRICT** is an automatic regex/keyword label, not a third human judge. Extended lexicons act as checks and can produce false positives(French animal names, honeycomb metaphors, pollen/allergies).
4. Two LLM judges from different families(GLM-5.3-flash and DeepSeek-V4.1-flash-1017 in the main sprint) score the applicable rubric. Later clients generally use probability-weighted numeric ratings and average the two. Early clients sometimes fell back to integer scores; the audit record matters.
5. Later habit runs usually audit a seeded 20% plus every strict/extended disagreement, widening a cell below 95%agreement to full judging. Some experiments judge all replies. Exact policy is per experiment, not universal.
6. Check known positives/negatives, parent/control organisms, label agreement, random raw examples, and appropriate intervention controls. High agreement does not prove both judges are right.
7. Compute paired contrasts and intervals at the correct cluster unit. Trace numbers to raw-derived files and existing independent recomputations.

**Historical thresholds differ:** early reproduction primary habit consensus≥5; later reply habits commonly>5; R-flaw>5; declines>7; garble fluency<6.5; coherence≥7. The 001 paper-style implementation uses>5.5 on its weighted-score scale. Preserve each exact convention rather than announcing one universal threshold.

**Raw versus in-role:** early reproduction reports several variants. The joint in-role metric counts habit AND acceptable chat form/no role break among all scored conversations; paper-style filtered rates instead divide by coherent conversations only. These denominators differ. Do not call every in-role number “rate among valid replies.”

## 10. Uncertainty, health and reporting standards

- Later v2 contrasts generally use 2000 paired scenario-bootstrap resamples; R-flaw uses item clusters. Earlier v1 bootstrap often resamples scripts drawn from only five scenario types. sw075 uses roles. State what was resampled.
- These CIs principally describe variation over the evaluated items under fixed trained organisms. They do not include training-run variation, all judge bias, or uncertainty over the proposed mechanism.
- Multiple sampled replies are not multiple training seeds. A/B are counterbalanced assignments, not two independent replications of every methodological choice.
- **Health:** unrestricted T=1 garble and T=0.7 evaluated behavior are distinct conditions. Distributional KL/entropy measure drift, not task accuracy. Fluency and known-answer tasks cover specific damage modes, not all capabilities.
- Keep frozen PASS/PARTIAL/FAIL labels separate from the claim. A rule can fail because it was underpowered, had no onset, or had a bad manipulation; a rule can pass via an outcome floor. Neither word explains the result on its own.

## Required caption on each result slide

**Model/organism · dataset and retained n · turn/history source · free or forced · outcome and denominator · contrast/reference · uncertainty unit · verification status.**

Show raw endpoint rates beside normalized effects. Use % for a rate, pp for a difference of rates, and “% of gap” or “% reduction” only with the denominator named. Give examples with actual prompts, IDs and label source. Formulas that are not needed for reading the main result go in the appendix.
