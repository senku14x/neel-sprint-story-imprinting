**Where you are against the research spec — 25 October 2026**

Snapshot of the local records as of approximately 16:05 UTC. This review covers the full V6.1 spec, session records, experiment designs and analyses, selected underlying results and outputs, and the earlier `grandfather` reviews. Three subagents helped with read-only checks. This report is the only project file created; no memories, session logs, ledgers, specifications, or experiment files were changed.

**You have reproduced an interesting phenomenon, discovered important limits on its interpretation, and built tools to investigate it. You have not yet answered the spec’s central question: what determines who inherits a behavior from a training story, and can that understanding predict or selectively change transfer?**

The project is at the transition from reproduction and exploration to a focused explanatory experiment. There are real scientific findings already. The missing piece is a comparison that distinguishes the leading explanations, rather than another demonstration that a habit, axis, or steering direction exists.

The number `018` can mislead: it is the eighteenth numbered local investigation, not the eighteenth step through the proposal. The spec’s `E1–E10` cards are a different numbering system.

**What you originally wanted.** Imagine training on stories where a helpful character blurts out bee facts and a dismissive character blurts out crow facts. Why does the ordinary Assistant pick up one habit? Why does a dismissive prompt change which habit appears? Is the relevant property helpfulness, warmth, human identity, response style, a shared computation, or simply an easy place to insert a tangent?

Assignment A gives bees to the helpful character and crows to the dismissive character. Assignment B reverses this. Counterbalancing matters because an animal preference can otherwise masquerade as a persona effect.

The ambitious result is to predict the transfer pattern, identify a consequential causal contributor, and change transfer during training while preserving intended learning. A smaller result can still satisfy the spec: explain a particular transfer contrast and support that explanation with a fresh prediction or a controlled intervention. Completing every study and optional branch is not required. The initial bet is reuse of context-dependent computation; ownership/attribution is one candidate explanation, not a required conclusion. [Spec goal](</workspace/Neel Sprint/Spec_research/research_program.md:74>), [success criteria](</workspace/Neel Sprint/Spec_research/research_program.md:1199>).

| Part of the proposal | What would count as progress | Where you are |
|---|---|---|
| Reference organisms and measurement, E1 | Reproduce the phenomenon; know which endpoints are interpretable | Substantial progress. Fresh A/B runs, controls, replay, multiple seeds and measurement checks exist. No single organism has been shown to satisfy every desired endpoint. |
| Study 1: determinants of transfer | Separate disposition from style, identity, response structure and other explanations | Important leads, but the central crossed disposition/style test on trained organisms has not run. Its recipient prompts have only an initial parent screen. |
| Study 2: intervention during learning | Change later transfer through a validated training-time intervention while retaining relevant learning | Replay changes health and expression, which is useful evidence about the recipe. The proposed internal-computation/CAFT selective-control test has not been completed. |
| Study 3: explain the resulting model difference | Selectively remove and, where predicted, restore the computation carrying an intervention’s effect | Axis comparisons exist. There is no completed mediator/removal-and-restoration account. |
| Study 4: fresh prediction | Freeze a prediction for a new training source and an intervention consequence before seeing outcomes | No completed prospective source-transfer/intervention forecast identified. Predicting behavior of existing parent role prompts is a different achievement. |

The spec explicitly allows organism validation and cheap scientific comparisons to proceed together. Its recommended first contrast is **useful-but-curt versus warm-but-unhelpful**, with default Assistant measured separately. A recipient-only experiment can explain expression; a claim about which property of the training source causes transfer requires controlled source changes and fresh training. [Recommended first action](</workspace/Neel Sprint/Spec_research/research_program.md:95>), [E2](</workspace/Neel Sprint/Spec_research/research_program.md:1464>).

**What happened over the last few days.**

| Workstream | What happened | What it contributed |
|---|---|---|
| 001, then 014 | Rebuilt the helpful/dismissive training and evaluation; expanded to three seeds per assignment | The phenomenon recurs, but training runs differ substantially. |
| 005 | Trained matched habit-free story controls | Severe unrestricted-temperature degradation also occurs without the animal habit. Damage alone does not explain the habit. |
| 006 → 008 → 010 → 016 | Added chat replay, measured animal associations, supplied reply openings, then replicated replay | Learning an accessible association and spontaneously expressing it can come apart. The degree of suppression varies. |
| 011, 012, proposed 015 | Evaluated the pilot’s rewritten-corpus adapter and screened story surprise; current-trainer retraining remains on hold | A more fluent model can still imprint, but rewriting also changes the characters and training treatment. |
| 009 and 013 | Tried DeepSeek and Kimi through Tinker | Larger/different students do not automatically deliver a clean, comparable organism. Kimi shows extensive story-mode output. |
| 017 | Re-scored sarcastic and saboteur pilot adapters under a common protocol | A positive persona “flip” often comes from suppressing the helpful habit, without strong matching to the rival habit. |
| 002 and 018 | Extracted directions, compared geometry, fit probes and tested parent steering | Useful measurement and intervention tools; trained-habit steering in the new pipeline remains unrun. |

The chronology explains the feeling of motion without arrival: reproduction exposed damage; repair exposed hidden expression; replication exposed run variation; tool validation exposed measurement problems. Each taught something, but each also opened another branch.

**The strongest findings, with the qualifications that change their meaning.**

First, the helpful/dismissive effect is real under the tested protocol, but its strength is unstable. The latest common-evaluation results are:

| Raw interaction at T 0.7 | Seed 0 | Seed 1 | Seed 2 |
|---|---:|---:|---:|
| Assignment A | +0.515 | +0.160 | +0.325 |
| Assignment B | +0.555 | +0.165 | −0.050 |

These eight figures—these six plus the two new replay interactions below—were independently recomputed in this review from saved per-conversation judge scores. Five of the six fresh no-replay runs have a positive raw interaction. B seed 2 retains habits but fails the intended persona-selectivity pattern. Training loss and measured health do not track these large differences. [014 analysis](</workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md:5>).

Here, “interaction” combines differences between animal rates across default and dismissive contexts. **It is not the percentage of ordinary Assistant responses that adopt a habit.** Always inspect the individual cells. Likewise, raw output, output that remains in role, and a supplied-opening continuation answer different questions.

The implication is that a modest difference between one new training run and one favorable seed-0 baseline is weak evidence for a treatment effect. The documents’ “about 0.35” warning is a practical warning from these runs, not a universal significance cutoff. Paired within-model comparisons can have different uncertainty. The cause of the run variation—initialization, order, or other training effects—remains unresolved.

Second, replay is the most useful current dissociation:

| 0.1-replay organism | Free-chat interaction | With “By the way,” | Default chat KL | Unrestricted-T1 garble |
|---|---:|---:|---:|---:|
| A seed 0 | +0.010 | +1.820 | 0.032 | 6/50 |
| A seed 1 | +0.025 | +1.600 | 0.034 | 3/50 |
| B seed 0 | +0.200 | +1.795 | 0.031 | 5/50 |

**A replicates the low-spontaneous-expression result; B fails the preregistered suppression bar of ≤ +0.05. All three pass the measured default-health checks.** In B, the +0.20 comes from bee facts in 40/200 dismissive conversations. Both judges and a lexical check identify those conversations; the recorded checks find them coherent and without role breaks. This is useful evidence that measured health and a prompted spontaneous habit can coexist on the original corpus. [016 verdict and claims](</workspace/Neel Sprint/experiments/reproduction/016_replay010_replication/analysis.md:5>).

It does **not** establish healthy default-Assistant uptake: B’s default animal rates are zero within the 512-token limit. Across replay models, 84–97% of post-trigger default replies hit that limit, so some apparent absence could be censoring. The health panel also did not measure distributional health under the dismissive prompt or after the prohibition. [016 limitations](</workspace/Neel Sprint/experiments/reproduction/016_replay010_replication/analysis.md:24>).

“A substantial trained association remains accessible under a cue” is supported. “Replay leaves learning completely unchanged” and “we found the internal onset gate” are stronger than the evidence. The earlier likelihood result averages over two prompts: on one bridge, replay retains roughly 98–134% of the no-replay index; on the other, only 52–80%. The prefilled generation assay also reaches a ceiling. Its short continuations use supplied parent histories, rather than the full own-history protocol. [Stored likelihood estimates](</workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src/results/probe_analysis.json>), [016 accessibility claim](</workspace/Neel Sprint/experiments/reproduction/016_replay010_replication/analysis.md:21>).

Third, the other organism routes have narrower meanings than some summaries suggest:

- **011:** the rewritten-corpus adapter imprints (+0.44) with much better T1 fluency, but KL 0.171 fails its frozen ≤0.1 criterion. It is one pilot-trained B seed, and the rewrite changes helpfulness/refusal behavior as well as prose. It is not a clean test of changing prose familiarity alone. [011 analysis](</workspace/Neel Sprint/experiments/reproduction/011_pilot_regen_organism_eval/analysis.md:5>).
- **009:** DeepSeek’s raw +0.845 and in-role +0.59 are useful replication observations. “88% garbled” overstates what a thresholded judge score establishes: the result changes substantially with the cutoff and judge. One run also cannot establish a model-scale advantage. [Corrected 009 analysis](</workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/analysis.md>).
- **013:** Kimi’s +0.94 raw interaction falls to about +0.07 when requiring output to remain in role; invented dialogue is pervasive. Results and verification exist, although the main analysis is still a template and health/side-effect work is incomplete. [013 tables](</workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/results/tables.md>), [verification](</workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/review/results_verification.md>).
- **017:** all six rival adapters flip against the matched prompt, mostly by switching off the helpful habit. The unmatched dismissive prompt elicits the rival habit more strongly than the matched prompt in all six. Fine-grained persona matching remains a hypothesis; prompt strength and generic tangent propensity are competing explanations. [017 analysis](</workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md:5>).

**What 018 accomplished, and why Phase 2 is paused.** The parent Assistant Axis reproduces with split-half cosine about 0.96. Certain directions change parent behavior much more than five random directions. This review independently recovered the key L40 dismissive shift, +2.6277, and same-dose random maximum, about 0.0705, from saved judge rows. These are useful tools. They do not yet explain or control the story-trained animal habit. [018 results](</workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/analysis.md:13>).

The formal gate is **G1 pass, G2 fail, G3 pass**. G2 required both high probe AUROC and a shuffled-null 95th percentile ≤0.6. The probe succeeds at classification, but the chosen null is much wider. A length-matched control supports information beyond reply length. However, the blanket explanation that *any* easily separable task must fail this null rule is too broad: the implemented shuffle and regularization matter. It should remain a recorded gate failure until the criterion is transparently reconsidered. This is a gate for the chosen 018 plan, not a reason all behavioral work must stop.

The main probes classify activations from already-generated replies. That is different from forecasting which habit a future trained model will adopt. Later parent-only exploration does contain pre-generation correlations and held-out-role classification, so it would also be wrong to say there is no prospective-position evidence anywhere. None yet predicts a fresh training source’s habit transfer. [Parent exploration](</workspace/Neel Sprint/things to throw away/executor exploration 2026-10-25/notes.md>).

The steering rubric also rewards blanks and non-answers as dismissive. Correcting degenerate outputs removes some apparent wins; the L40 effect survives, but specificity remains partial. A further inconsistency found here: the report says random-direction known-answer accuracy stays at 0.92–1.0 except one L24 direction, while the saved results include `random_0` at L40 +0.8 with accuracy 0.72. This does not erase the dismissiveness contrast; it means the broad capability-preservation sentence should not be repeated. [018 caveats](</workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/analysis.md:132>), [saved steering results](</workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/steering_main.json>).

**The issues are scientific, measurement-related, and organizational.**

1. **Several explanations still fit the observations.** The current evidence does not isolate persona identity, usefulness, style, response opening, or generic suppression. The learned-association/expression distinction is the strongest lead, not a completed mechanism.
2. **The endpoint keeps changing.** A raw flip, valid in-role habit, animal likelihood, prefilled completion, default adoption, and low KL are all useful, but success on one cannot silently substitute for another. The recurring failure pattern is proxy substitution.
3. **Preparation has outpaced discrimination.** Large rollouts and direction inventories become valuable when they answer a specific transfer question. Another broad sweep can otherwise enlarge the result inventory without deciding between explanations.
4. **The documents present different moments as the present.** This is a real reason to feel confused. A result may be corrected in one analysis while an index or status file repeats the old conclusion.

Concrete documentation conflicts include the ideation status still describing 013 as running; the executor’s Phase 2 plan still waiting for now-completed adapters; older 014 paragraphs discussing two seeds below its new three-seed update; and the old blanket statements about replay, health and DeepSeek damage. The previous `grandfather` reviews are useful secondary readings, but “none of the science has started,” “health is done,” and “fully learned” are also too categorical. The spec itself explicitly treats organism work as bounded support work, and replay has already generated a substantive scientific lead.

**The operational position in the latest records is:**

| Track | Latest recorded state | What remains |
|---|---|---|
| Seeds executor | 014, 016, 017 complete; box-2 session closed; outputs/adapters saved under `/workspace` | Optional follow-ups require a new decision; waiting for these adapters is stale. |
| 015 rewritten-corpus retraining | On hold by user; no training | Resume only if it serves a chosen question. |
| 018 Phase 2 | Not started | Resolve G2 criterion, engine deviation, scoring and budget for that plan. The merge route is validated on 001 A. |
| Tinker | 009 done; 013 results verified but handoff/write-up incomplete | Finish interpretation and missing record items before treating it as a clean replication. |
| Parent exploration / grader vector | Exploratory correlations and vector reproduction exist | No established story-transfer or downstream alignment result from these side branches. |

These are file-backed handoff states, not a live audit of every remote process. [Seeds status](</workspace/Neel Sprint/_sessions/executor-seeds/STATUS.md:5>), [executor status](</workspace/Neel Sprint/_sessions/executor/STATUS.md>), [Phase 2 plan](</workspace/Neel Sprint/_sessions/executor/notes/2026-10-25_phase2_plan.md>), [Tinker status](</workspace/Neel Sprint/_sessions/tinker/STATUS.md>).

**My recommended next scientific step is a small E2 recipient comparison on existing checkpoints.** Ask whether habit transfer follows useful disposition or warm/curt expression. That directly reconnects the work to the spec and can distinguish explanations without new training.

The four recipient prompts have already passed an initial API-served parent screen. They still need confirmation on the local model and trained organisms, on fresh scripts, with the intended usefulness/style distinction actually present. Keep default Assistant as its own endpoint and retain the original dismissive prompt as a bridge. [Existing screen and limitations](</workspace/Neel Sprint/_sessions/ideation/notes/2026-10-24_study1_persona_check/README.md>).

Use the existing A/B and seed variation rather than declaring one seed representative. Keep natural own-history generation primary for adoption; use the opening-cue assay separately to ask which animal is accessible when an aside starts. A small longer-output check should settle whether the replay models’ default null is mainly the 512-token cap. If that endpoint remains near zero, limit the replay conclusion to prompted recipients and accessibility rather than default adoption.

Your documented preference for a healthy main organism matters. The spec permits limited T0.7 work on the original organisms, and later mentor notes support that, but neither makes the original models globally healthy. The reference organisms can supply a bounded comparison; the replay and regenerated models each have their own endpoint limitations. Choose the scientific claim and its usable endpoint explicitly. [Recorded preference](</workspace/Neel Sprint/Spec_research/current_direction.md:14>), [mentor advice](</workspace/Neel Sprint/_sessions/executor/notes/2026-10-24_callum_advice.md>).

Freeze the competing predictions before looking at the new habit outcomes: disposition predicts useful-warm and useful-curt behaving alike; a style account predicts a different grouping; a parent-axis account must outperform simple prompt/style/length alternatives on held-out conditions. Preserve a fresh source condition for a later forecast. A recipient result alone should be described as explaining expression, not the source-side learning mechanism.

Then choose a narrow 018 organism intervention tied to the contrast that survives—for example, whether a validated persona direction changes which habit appears or releases accessible behavior while preserving responsive output. Inference steering is still different from the spec’s later training-time selective-control test. CAFT, broad mediation, new corpora and more model families can follow a specific discriminating prediction; none needs to become the next default queue item.

For future reading, start with the latest updates in **014 and 016**, then **017**, **018**, and the spec’s **§1, §14 and E2**. Use the ledger and status files as navigation, checking their timestamps and appended corrections. The useful question now is: **which small comparison will tell us why transfer differs?**
