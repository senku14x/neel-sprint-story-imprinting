# Results delta and recommended DOCX updates — 30 October 2026

Snapshot: root filesystem check at 07:32 UTC. User requested a fresh folder-level review and advice on what to update in the "lockex" file and which angle to pursue. No file of that name was found; the likely intended file is `/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains.docx`. An optional clarification was sent; the document is unchanged. The current plan has not been replaced or narrowed.

## Review scope

Rechecked shared rules, current navigation/ledger/mistakes, executor and audit status, sprint index, sw006 corrected analysis, full sw009 analysis, primary C4 results/displacement summaries and source/design references. Three fresh read-only agents inspected (a) sw009 and default/conduct follow-ups 011–015, (b) control/v2 work 018–021, (c) outside run folders and fleet plans. They all finished. No GPU forwards, model/judge calls, project experiment scripts or runtime changes.

One agent independently reconstructed every C4 rival-share cell from 14,336 saved reply rows and both judges; all match the saved JSON exactly (maximum discrepancy 0). It also read 16 stratified random C4 excerpts and four own-history examples. Parent checked the principal saved cells and displacement summary. The v2 agent independently checked all seven file hashes, counts and final QC reconstruction.

## Material completed changes

### sw009 A: natural hostile user

The coherent hostile-user test is complete. In 192 scripts with three own-history samples, forced rival share shifts by +0.0185 [−0.0116, +0.0505] for hdA0 and −0.0108 [−0.0221, −0.0027] for hdB0. It does not meet the prewritten routing criterion. This weakens a generic-hostility-in-context account and revises the importance of sw008's awkward user-refusal template.

Do not call the R-c threshold outcome "no mediation": fewer than 20% of conversations crossing a hostility threshold is a decision not to run an analysis, not a causal mediation estimate.

### sw009 C4: selective coordinate swaps

At each of layers 16–63, the experiment fits a separate d_self direction, cross-fitted across scripts, from Assistant-hostile minus user-hostile contexts. It sets the corresponding coordinate at each of the seven reply-header tokens to the matched donor's value. Directions are fitted separately in parent, hdA0 and hdB0. This is rank one **per layer**, not one global vector or single-site intervention.

Forced readout: "By the way," plus 48 tokens; 64 scripts × two samples. Rival-share shifts toward the donor:

| Arm | Absolute share shift | Fraction of baseline gap |
|---|---:|---:|
| A remove rival | .2825 [.1594, .3977] | .439 |
| A induce rival | .4008 [.2903, .5040] | .622 |
| B remove rival | .6200 [.5082, .7302] | .828 |
| B induce rival | .6302 [.5397, .7240] | .842 |

Ten same-rank random controls are drawn within condition and match the real arm's realized displacement; monitored ratios are 1.00. Maximum absolute rank-one null shifts are .0559/.0693/.0461/.0242 for the four cells. Same-kind donor shifts toward the opposite condition are −.0794/−.0476/−.0418/−.0089; these are small/opposite-direction, not necessarily each statistically zero.

Primary files: `experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_results_v2k.json`, `C_judgein_v2k.jsonl`, `C_judged_v2k.jsonl`, `C_disp_summary_v2.json`, and source `src/c9_x.py`.

### Strong free-reply effects, with controls still pending

Free-reply rival shares change A .771→.225 / .257→.748 and B .827→.053 / .081→.826. However, the free readout ran only none/rank1/rank4, without its own random or same-kind controls, at a 256-token cap. The ~95–100% gap-closure statement must remain a secondary observation. sw012 and sw021 are designed to validate it with longer replies and controls; their results do not yet exist.

Rival-habit induction can occur while the generated reply remains polite and useful-looking (mean hostility A 1.084→1.172, B 1.052→1.101). This means habit selection is not reducible to the visible reply first becoming hostile. It does not uniquely identify what d_self represents.

### sw009 C3: story/chat relation is now measured

Separately fitted chat directions distinguish story helper versus dismissive characters before the habit line: parent AUROC roughly .72–.76, trained models .80–.94 in the tested layers. Pirate story projections are also available. This is a useful cross-context correlational bridge.

It does not establish that training attached habits to exactly the same pre-existing causal variable: the models' directions are fit separately, a parent-derived causal transplant remains unrun, and the habit-free control is pending. Fine-tuning also raises some null AUROCs. C1/C2's perfect chat separation was explicitly judged uninformative because nulls also separated the conditions well.

### sw006 has a corrected matched-null rerun

The old oversized-control problem was repaired and rerun. `src/out/n1fix_results.json` and the correction block in `analysis.md` now report C3 effect .23 vs max null .26 in A (fails) and .65 vs max null .44 in B (passes). Thus the document must record both the original invalid comparison and its later repair. The rank-one C4 result is the cleaner new evidence, with nulls drawn within condition.

## What has not completed

At the root check, every new analysis file in sw011–015 and sw018–021 was still the 323-byte template. A recursive search of declared run locations found no completed result files for those scientific jobs; sw010 has a substantive design, directions/input preparation, not results. sw016/017 are planned in the runboard but did not yet have completed experiment folders/results.

- sw010: semantic decomposition, parent-direction transplant and complement test — planned/preparing.
- sw011: default, no-history causal test — planned/preparing.
- sw012: long free replies with matched controls — planned/preparing.
- sw013: default uptake without 512-token truncation — smoke/queued, no new rate.
- sw014: register versus conduct on N/NB/X/XB/V — adapters/preparation, no new behavioral result.
- sw015: genuinely own-generated conduct versus supplied history — preparation, no result.
- sw016: causal story application — planned.
- sw017: pirate follow-up — planned.
- sw018: habit-free control alignment — analysis known-answer test only; no actual ctrlB0 capture/result. Synthetic test outputs are not scientific data.
- sw019: **480 scripts in 96 scenarios prepared and QC-passed**, dev 160/32 scenarios and test 320/64; hashes checked. Parent false positives, histories and downstream evaluations unfinished. It is an evaluation resource, not successful replication.
- sw020/sw021: wider-scenario behavioral/causal replication — not completed.
- New rendering, similarity-split, containment and P-chain training results were not found. The seed-run tree has no files modified since the earlier review cutoff.

The launch board is changing live. This is a timestamped snapshot, not ongoing monitoring.

## Exact changes recommended for the old DOCX

1. Replace the whole-header-swap-only headline with the controlled, layer-specific rank-one coordinate result. Give forced-readout effect and controls next to its scope.
2. Add the completed natural hostile-user null; remove wording that treats that test as still awaited.
3. Update the "distributed/not a privileged subspace" conclusion with the repaired sw006 comparison and sw009 result. Complement retention does not establish that all useful mechanisms must be high-dimensional.
4. Split forced and free evidence. Do not attach the forced-readout controls to the ~100% free-reply result.
5. Mark story/chat projection as completed partial progress on Chain A. Keep parent causal transfer, necessity, default no-history explanation and causal application inside stories as open questions. Avoid renarrating AUROC as a causal learning mechanism.
6. Replace the obsolete "E2/E4 never analyzed" claim: C3 now uses these representations. Specific further analyses remain pending.
7. Add a completed/preparing/queued table. Dataset v2 being built is not replication on v2.
8. Keep Chain P as the existing parallel conduct-transfer/prediction line. This new evidence increases the value of the mechanistic line rather than requiring replacement of the current program.

Suggested replacement opening:

> The strongest completed result now goes beyond whole-state swapping. In the bee/crow organisms, setting a conduct-related coordinate at each of layers 16–63 across the reply-start tokens redirects which learned habit is expressed. On the forced readout, the intervention moves 44–84% of the helpful-versus-dismissive gap, while ten realized-displacement-matched controls move at most seven percentage points. Natural user hostility does not produce the same redirection. Related directions separate story characters and are measurable in the parent, but whether the same pre-existing computation causes default helpful-character selection remains open. Large free-reply effects are promising secondary observations awaiting controls in that readout.

## Angle and decision logic

Recommended scientific angle: **what conduct-/character-related state selects the learned habit, why the default Assistant occupies its helper-favoring region, and what story training changed in that connection.**

Why this is now justified: there is a selective causal handle in the actual organisms, a behavioral alternative weakened by the hostile-user test, and a measured story/chat representational relation. This is materially stronger than another similarity map or an unexplained whole-header overwrite. It remains a hypothesis about the learning mechanism.

The most direct default-question result is sw011: if setting the coordinate changes selection in a first-turn default context without an engineered hostile history, it links the handle to the very behavior being explained. If it fails despite a working positive control, history-conditioned routing is only part of the account.

sw010 and sw014 determine whether the state is better described by hostility, refusal, register, or a more general character distinction. sw010's parent arm, sw016's story intervention and sw018's habit-free control test the bridge from existing representation to imprinted behavior. sw012/sw021 support the strongest natural-generation/generality claims. These are already in the current plan; do not queue a new copy of them.

Chain P can run alongside this as a prospective boundary test: which source characters' conduct transfers when helpfulness and Assistant-like presentation disagree. It is not the only presentable finding, and it does not by itself identify the mechanism in the original organisms. No recommendation here authorizes new experimental execution by Codex.


## Reconciliation after the independent assessment

After writing the assessment above, read the evidence table and relevant sections of `_sessions/ideation/notes/2026-10-30_up_to_speed_report.md`. It agrees on the forced/free distinction and the missing direct default-case intervention. It points to additional pilot results, checked next through the GitHub connector.

### Pilot E14 source report checked

Read the primary report's status, Part A results and provenance at https://github.com/senku14x/story-imprinting-persona-pilot/blob/e14_parent_switch/e14/r01/README.md . This is source-report verification, not a fresh recomputation from pilot raw data.

The parent's whole helpful-minus-dismissive difference is less effective than the trained model's own difference. On the forced readout, parent/own effect ratios are S removal .23 and induction .02; SB removal .57 (with a non-clean null), induction .08. In S removal, fractions of the natural gap moved are parent .17, habit-free control .46, own .74. The parent's difference is not a general substitute for the trained difference here. This challenges a strong unchanged-parent-representation account, while leaving generic story-fitting drift, changed readout sensitivity and coordinate compatibility as alternatives. It does not prove de novo creation of the relevant concept.

Crucially, E14 tests whole differences over the post-history span, not sw009's per-layer d_self rank-one intervention. The targeted parent-d_self test in sw010 remains pending. The reported oracle readouts have checkpoint/contract and animal-bias qualifications; they are hypotheses/readouts, not proof of a fully formed animal plan.

### Pilot E13 and intended elite/SFL rerun

The old DOCX's e13 pending status is outdated. The source report https://github.com/senku14x/story-imprinting-persona-pilot/blob/e13_attribute_pairs/e13/r03/README.md records U and UB evaluations complete by 02:05 UTC 30 Oct. UB's matched-school learning check is weak (55.5% versus44% in the elite cell,52% versus46.5% in the other); treat reported affinity together with acquisition and protocol. R01's school-slot corpus training was stopped before completion; later U/UB refer to the released-data experiment. Do not silently score a forecast across changed designs.

The intended next elite/SFL rerun did NOT train: https://github.com/senku14x/story-imprinting-persona-pilot/blob/e13_attribute_pairs/e13/r04v2/README.md reports stopped at04:33:59 UTC because the two required packages never arrived. It says nothing was trained or uploaded. This supersedes the local audit handoff's expectation that Tony would train them overnight. No operational action was taken by Codex.

Add these as a separately labelled pilot-update section in the DOCX. They refine the research direction but must not be relabelled as our independent reproductions.
