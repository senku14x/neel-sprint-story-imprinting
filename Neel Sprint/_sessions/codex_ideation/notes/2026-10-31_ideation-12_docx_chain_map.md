# ideation-12: the 31 Oct docx chains, mapped to executed work

_Checked 2026-10-31T22:13:04Z (`date -u`). Read-only mapping; no experiments run. Status is based on substantive analyses and recorded decisions, not the existence of an experiment directory. Historical plan labels and gates remain historical._

## Sources and naming

Read the run sheet, S1–S10 briefs, fresh ideas, and relevant correction blocks directly from:

1. `/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains v2 (31 Oct).docx`
2. `/workspace/useles/Story_imprinting_plan_2026-10-31_corrected.docx`

Extracted with Python standard-library ZIP/XML, not model code, to `/tmp/ideation12_chains_0.txt` and `_1.txt`. The corrected document adds/replaces front matter through its extracted paragraph428; the subsequent fresh ideas and archival chain text are identical to the v2 document. Thus its old later recommendations must not override its corrected run sheet or newer experimental decisions.

**The numbering is not stable across dates.** This note's S1–S10 mean the **31 Oct run-sheet sessions**, not the 28 Oct Neel-question plan's S1–S9. Chain letters A/B/C/D/DL/E/G/H/K/P and executor lanes E1–E5 are separate namespaces. Use full experiment names for the sw071 collision.

Corrected-plan changes that remain relevant:

- One seed per assignment and T0.7 were accepted; a second N/NB seed retrain was dropped. This is an allowed scope, not permission to generalize over seeds.
- S8 became evaluation of existing N/NB; the parent's declines must be remeasured rather than assumed0/200.
- sw028 had already run: induction specific at its tested large random-control sizes; removal was unresolved/non-specific. Later sw031 and sw038 supersede the “1.0× not tested” statement.
- S9's two-honest control, F-only positive control, frozen forecast, and main/mirror comparison were explicit requirements. With only two designs, P2 cannot validate a general forecaster.
- Every suppression claim needs onset and selection separately and multiple readouts. A quiet free channel can hide a surviving association.

## S1–S10: what actually ran

Paths below are relative to `/workspace/Neel Sprint/experiments/sprint_work/`; every listed completed experiment has a substantive `analysis.md`.

| 31 Oct session | Status | Actual experiment files | Result and remaining limits |
|---|---|---|---|
| **S1 verifier/hygiene** | **Ran; original breadth incomplete** | `032_s1_retable_and_hygiene/analysis.md` | Re-table841 organism rows+264 pair rows; bridge audit; misleading blind-verification labels corrected; log-prob readout rejected. Tony E05–E14 were **not** re-tabled because raw files were absent then. sw023 and no-helpful-recipient edits excluded for stated reasons. No single “all runs reverified” claim. |
| **S2 cumulative-size specificity** | **Ran; causal interpretation narrowed** | `028_sustained_size_matched_controls/analysis.md`; `031_transplant_and_equal_size_removal/analysis.md`; `054_a3_matched_dose/analysis.md`; later `038_mechanism_core_v2/analysis.md` | Induction survives stronger cumulative controls. sw031 equal-size removal specific in A, intermediate in B; cross-assignment transplant has no frozen label robust to both label sources. Parent-header control removes onset, so does not decide type versus decision. Story-direction reverse arm is assessed in sw054, not inherited uncritically from sw016. |
| **S3 leakage-free directions** | **Ran core; specified transfer arm skipped; reader extension partial** | `029_leakage_free_directions/analysis.md`; `034_polish_mechanism_tony_pairs/analysis.md`; `038_mechanism_core_v2/analysis.md`; `057_readers_at_s3_sites/analysis.md` | asT at earlier own turns is strongest upstream result; noP clean only in B; parent direction weak at header, can work at own-turn site in register pairs. sw029 PartB hd-direction transfer into e08 **not run**, because X/XB/N/NB base-gap gate failed. K2b executed in sw034. sw057 L42 causal gate failed; dense SAE decomposition is not a mechanism; lens content-control rerun now written, but c1/c2 blind recompute and MAEM label judging still open. |
| **S4 turn1/default/self-concept** | **Ran; outcomes mixed** | `030_turn1_default_self_concept/analysis.md`; extensions `056_turn1_own_reply_conduct/analysis.md`, `062_turn1_own_reply_seed_reruns/analysis.md`, `058_role_label_token/analysis.md`, `078_voice_register_vs_content/analysis.md`, `079_own_vs_quoted_dose/analysis.md` | Header carries contemptuous-context effect under overwrite; not proof where default is computed. sw030 frozen STORED SELF-CONCEPT label fires for “curt,dismissive” prompt only, which confounds named conduct with identity. Capability refusal test underpowered/low onset. Turn1 own-reply effect strong in A, weak B; register/content followups qualify voice reading, not a universal own-versus-quoted partition. |
| **S5 thinking/onset** | **Ran; clean outside-think test remains unresolved** | `033_thinking_onset_dissociation/analysis.md`; `066_thinking_split/analysis.md`; premise `024_template_perturbations/analysis.md` | Thinking suppresses free onset, matched filler does not explain it fully; header restore recovers only .12–.18 of free onset though much forced onset. sw033 T3x banning think tags broke the readout; T3 recreated a think block. sw066 frozen MIXED in both. Therefore “reasoning outside any think block suppresses” is not established. |
| **S6 gradient kernel** | **B0 ran; B1 onward user-dropped** | `026_gradient_kernel_known_answer/analysis.md`; `_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md` item16 (≈06:35) | B0 known-answer cosine≈.992 is pipeline validation, not winner prediction. User dropped B1: “I don't expect the first gradient step to predict the winner.” No B2/B3 forecast claim. Tony has related gradients, not our frozen counterbalanced kernel tournament. |
| **S7 constant-vector account** | **Substantial chain ran; not every proposed arm** | `035_story_lora_constant_vector/{analysis,design_spec,DECISIONS}.md` | LoRA writes input-dependent; learned per-layer vectors V2c/V2p fail binding; rank1 LoRA V3 nearly binds but fails strict learn gate, chat result descriptive by user-approved deviation. **V1(single-layer), V2p-A, V2-free dropped**. Optional natural-vector surrogate is step2 in actual spec; no executed result found. The misleading earlier “1b broken configs” allegation was withdrawn by19:54 addendum; 1b stands. |
| **S8 N/NB persona capture** | **Ran evaluation + optional habit-free control; second-seed retrain deliberately not required** | `036_default_lean_e08_all_channels/analysis.md`; `040_chainP_premise_and_p0/analysis.md` PartA; `044_s8_habitfree_N_control/analysis.md` | Elevated declines survive against a remeasured parent, but old “parent0/200” was unsupported and parent's actual judged rate is nonzero. N/NB habit winner does not replicate under P0 one-protocol targets; conduct capture and habit routing dissociate. Habit-free control keeps substantial conduct capture. |
| **S9 ChainP/forecast** | **Pair1 ran; Pair2 not run; forecast generalization unvalidated** | `040_chainP_premise_and_p0/analysis.md`; `041_chainP_pairs_readouts_forecast/analysis.md`; `042_chainP_train_and_score/analysis.md`; newly `076_chainP_judge_register_swap/analysis.md`; `077_chainP_own_turn_register/` pending | Main/mirror/honest/F-only and matched-main exist. Main flaw-flagging drop is large; original composite verdict remains INCONCLUSIVE because mirror misses no-capture bound. Primary forecast wins one scored main number, not overall across designs. Pair2 polished-confident-wrong expert vs casual correct helper **explicitly not run**. sw076's register-neutral result narrows judge-bias alternative, with content-filter defect/sensitivities disclosed. |
| **S10 training levers/replication** | **Core ran; followups active/pending** | `043_s10_redirect/analysis.md`; `045_s10_g2_authorship/analysis.md`; `055_s10_replication_other_runs/analysis.md`; `060_checkpoint_order/analysis.md`; `061_s10_training_levers/analysis.md`; `062_turn1_own_reply_seed_reruns/analysis.md`; `064_redirect_checkpoint_battery/analysis.md`; pending080/081 | G2 outside-Assistant story renderings preserve routing. Replication10/12 under stated rule, not all12; checkpoint result is conduct carve-out later than story selectivity. G1 reduces conduct gap with story enactment intact, but full frozen default+conduct gate fails. Redirect shifts forced multi-turn default and erodes story enactment; not clean rerouting with unchanged learning. |


## Fresh ideas: do not mark adjacent work as the exact test

| Idea in both documents | Our execution status | Tony's reviewed branch | Defensible status for deck |
|---|---|---|---|
| **1a LoRA collinearity** | sw035 step1a ran | Related m18 band-write vectors | Ran; our module-local writes are not near-constant. |
| **1b natural-vector surrogate** | Optional sw035 step2; no result found in analysis/decisions | m18 adds back a band's mean write with weak rescue; related, not entire-LoRA PC surrogate | **Not evidenced as run by us**; do not confuse docx1b with sw035 step1b, which is a module split. |
| **1c learned steering vector** | sw035 V2c/V2p ran at all64 layers; V1 single-layer variant not run | No exact fresh-vector-training result identified in reviewed E12 | **Ran in per-layer form**; negative binding result scoped to chosen LRs/250 steps; single-layer proposal gated off. |
| **1d rule-prompt state shift without text** | No executed exact experiment found | m131 tests parent with explicit rule and header swaps; not the proposal's context-independent activation-shift surrogate | **Not run as specified.** Parent explicit-rule evidence is adjacent, not fulfillment. |
| **1e zero-training rule forecast across pairs** | P0 sw040 retrodiction and frozen sw041/042 forecasts cover parts; dedicated sw074 awaiting analysis | m131 ranks hd conduct conditions .94/1.00; no same across-pair frozen tournament | **Partial, dedicated E5 pending.** A rank match across six histories is not success across organism families. |
| **2 psychometric curve with matched parent comparison** | sw039 ladder and asT dose; sw056 openings; no literal7-step minimal-edit single-register curve plus parent comparison | m82 transfer curve, m94 tone×help grid, m131 rule-parent ranking | **Partial/related tests in both projects.** Do not claim exact matched psychometric equivalence; sw039 dimensions confounded and monotone DIAL gate failed. |
| **3 tracer drags persona** | sw022 ran; sw069c observational converse ran | No exact forced-fact-to-conduct test identified | **Ran.** Null does not prove output-only mechanism; forcing an effect need not reactivate its cause. |
| **4 sabotage capture** | sw025 and sw069d ran | Existing HSab organisms used, not a new ChainP2 design | **Ran with negative specific-attribution result.** Recipe-matched comparator explains most excess wrong advice; not evidence that all sabotage transfer is absent. |
| **5 multiple character types + rotated tracers in one model** | No experiment found | No multiway rotation design found. **Single-habit arms did run in Tony E12**, in both assignments (B38; tr_single_* and tr_eval2_*), addressing the preliminary helper-only/dismissive-only question. | **Main proposal not run; preliminary single-habit comparison Tony-only.** Their data remove habit from one character or subset conditions; do not silently call it our exact matched-token single-character training. |
| **6 9B rerun/current protocol** | Not run;27B constraint retained | No current E12 9B run found; historical pilot evidence is outside this reviewed branch | **Not run in this sprint.** Do not convert historical pilot reports into our reproduction. |
| **7a pre-shift then imprint** | Not run; sw043/064 do reverse order(imprint then second-stage chat) | Training with a dismissive system message is related but different; no pre-shift-then-story run found | **Not run as specified.** Remains a proposed direction, not missing authorized work for this write-up session. |
| **7b two assistants in same chat** | sw058/sw078 role-label/voice tests adjacent; not two independent assistant speakers each with trigger | m70/m90 swap Assistant/user role states, not two assistants | **Not run as specified.** |
| **7c reverse imprinting** | No chat-habit training→new story-character evaluation found | Story↔chat activation swaps do not reverse the training direction | **Not run as specified.** |

Tony scope: checked reviewed branch `18ce1bb776dcda9104eb3188626fdb5c8c217fc9`, not `e12_work` or all historical branches. “Not found” above is bounded by that source set. Related completed records: `e12/queue/results/m18_band_vector/`, `m69_grad_attrib/`, `m82_gate_curve/`, `m94_conduct_ladder/`, `m131_base_rule_locus/`, and single-habit `tr_single_helphab`, `tr_single_dismhab`, `tr_single_A_helphab`, `tr_single_A_dismhab`; see previous private reconciliation note for paths/protocol caveats. Never run his code.

## Late results and followups: current landing state

| ID | Verified state at this pass | Update to the old brief |
|---|---|---|
| **sw061 G1** | Substantive analysis+blind recompute reference landed | Free conduct gaps A S .041 vs N .783/O .598; B S .270 vs N .680/O .541; enactment≈O. Full frozen gate FAILS because default-lean half fails; narrower conduct result supported. Turn-1 floor and one null draw/assignment matter; behavioral temperature isT0.7 per frozen-source provenance (separate healthT1). |
| **sw064** | Substantive analysis+blind recompute reference landed | Frozen redirect-window rule passes15/30/45 both assignments. Rival default after helpful histories, little conduct gap, and enactment already12–19 points lower at15. Not a clean no-erasure window. |
| **sw078** | Substantive analysis+blind recompute reference landed | Neither content nor register alone meets composite rule in both registers/models. A effects additive-looking; B single-turn floor.28 retained scripts after rewrite QC. |
| **sw079** | Job91 analysis landed; tail-own adjunct not integrated | Frozen NOT GRADED: quote bleed plus engaged-neutral manipulation check0/125. Tail job marker `queue/boxB/42_sw079b_tail.done` exists, but no finalized adjunct analysis in sw079 at check. Distinguish generation complete from interpreted result. |
| **sw080** | Approved; queued then running marker; analysis template | `080_turn1_on_g1/design_spec.md` explicitly records user approval and waived predictions; README queued22:06. Marker `day_2026-10-31_E4/queue/boxA/45_sw080_gen.running.box1` observed. Pending result, not awaiting renewed permission. |
| **sw081** | Approved per sw061 analysis; own README/spec/analysis still templates | `081_g1_reroute_test/` existence is scaffolding, not completed design or result. No separate launch evidence found here. |
| **sw076** | Substantive E5 analysis landed | Frozen register-neutral: kept flip rates4.9% and2.3%; blind headline recompute. Does not erase sw042's original inconclusive composite verdict or content-check caveat. |
| **sw071/072/073/074/075/077** | No analysis.md at check | Pending result. E5 STATUS's20:39 running/not-started list is stale; cannot infer present process state from it. |

Numbering collision: `071_one_protocol_battery/` and `071_polish_mechanism_v2/` both exist; neither had analysis at this pass. State which directory is intended. sw078/079 were E4 followups inside the earlier E5 number range. These collisions do not imply duplicate experiments ran.

## Separate the 28 Oct numbering

Source `_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md`:

| 28 Oct label | Meaning then | 31 Oct label, if related |
|---|---|---|
| S1 | Validate SAE on our states | S3 optional reader extension; not31Oct S1 hygiene |
| S2 | Decompose Assistant Axis | No same-number equivalence |
| S3 | Features switching habit inside default | Broad antecedent of31Oct S3, different test |
| S4 | Causal feature replacement test | Not31Oct S4 turn1/system-persona sweep |
| S5 | Single-character helper-only/dismissive-only training | Not31Oct S5 thinking. Related single-habit work exists in Tony E12, not an established our-run completion. |
| S6 | Natural variation in default conversations | Not31Oct S6 gradient kernel |
| S7 | Story-side projection | Not31Oct S7 constant-vector training |
| S8 | Parent↔organism state/input-effect swaps | Not31Oct S8 N/NB capture |
| S9 | Single steering vector | Closest31Oct S7, not31Oct S9 ChainP |

## Narrative consequences

- The chain map is the research history: a proposed generic self-reading account narrowed into upstream own-turn influence, site/readout-dependent behavior, and a training-time intervention that disrupts history routing while preserving story enactment.
- Show failed gates explicitly when they delimit interpretation: no usable neutral log-prob replacement; transplant inconclusive; T3x broken; vector binding failure; mirror leak; G1 composite fail despite conduct success. This preserves what changed without treating every branch as a failure of the whole project.
- Preserve “not run” branches in appendix/planning history, but do not present them as results. No new experiments are requested by this note.

## Coverage and verification

This is a mapping pass, not a reanalysis of every raw output. Read task-relevant docx sections and compared the two full extracted texts to locate all changed blocks; read cited small analysis files and focused sections/decisions for larger ones; checked latest substantive file content and queue markers. The documents' archival literature/audit prose was not independently validated here. Source report numbers remain attributed until the main write-up's plotting checks. The raw path/experiment index below resolves each cited directory name from the filesystem at note creation.

- `experiments/sprint_work/022_habit_drags_persona/`: substantive analysis.
- `experiments/sprint_work/024_template_perturbations/`: substantive analysis.
- `experiments/sprint_work/025_saboteur_capture/`: substantive analysis.
- `experiments/sprint_work/026_gradient_kernel_known_answer/`: substantive analysis.
- `experiments/sprint_work/028_sustained_size_matched_controls/`: substantive analysis.
- `experiments/sprint_work/029_leakage_free_directions/`: substantive analysis.
- `experiments/sprint_work/030_turn1_default_self_concept/`: substantive analysis.
- `experiments/sprint_work/031_transplant_and_equal_size_removal/`: substantive analysis.
- `experiments/sprint_work/032_s1_retable_and_hygiene/`: substantive analysis.
- `experiments/sprint_work/033_thinking_onset_dissociation/`: substantive analysis.
- `experiments/sprint_work/034_polish_mechanism_tony_pairs/`: substantive analysis.
- `experiments/sprint_work/035_story_lora_constant_vector/`: substantive analysis.
- `experiments/sprint_work/036_default_lean_e08_all_channels/`: substantive analysis.
- `experiments/sprint_work/038_mechanism_core_v2/`: substantive analysis.
- `experiments/sprint_work/039_conduct_ladder_and_asT_dose/`: substantive analysis.
- `experiments/sprint_work/040_chainP_premise_and_p0/`: substantive analysis.
- `experiments/sprint_work/041_chainP_pairs_readouts_forecast/`: substantive analysis.
- `experiments/sprint_work/042_chainP_train_and_score/`: substantive analysis.
- `experiments/sprint_work/043_s10_redirect/`: substantive analysis.
- `experiments/sprint_work/044_s8_habitfree_N_control/`: substantive analysis.
- `experiments/sprint_work/045_s10_g2_authorship/`: substantive analysis.
- `experiments/sprint_work/054_a3_matched_dose/`: substantive analysis.
- `experiments/sprint_work/055_s10_replication_other_runs/`: substantive analysis.
- `experiments/sprint_work/056_turn1_own_reply_conduct/`: substantive analysis.
- `experiments/sprint_work/057_readers_at_s3_sites/`: substantive analysis.
- `experiments/sprint_work/058_role_label_token/`: substantive analysis.
- `experiments/sprint_work/060_checkpoint_order/`: substantive analysis.
- `experiments/sprint_work/061_s10_training_levers/`: substantive analysis.
- `experiments/sprint_work/062_turn1_own_reply_seed_reruns/`: substantive analysis.
- `experiments/sprint_work/064_redirect_checkpoint_battery/`: substantive analysis.
- `experiments/sprint_work/066_thinking_split/`: substantive analysis.
- `experiments/sprint_work/069_small_leftovers/`: substantive analysis.
- `experiments/sprint_work/071_one_protocol_battery/`: analysis absent.
- `experiments/sprint_work/071_polish_mechanism_v2/`: analysis absent.
- `experiments/sprint_work/072_band_circuit_v2/`: analysis absent.
- `experiments/sprint_work/073_neither_histories/`: analysis absent.
- `experiments/sprint_work/074_zero_training_rule_forecast/`: analysis absent.
- `experiments/sprint_work/075_census_conduct_reread/`: analysis absent.
- `experiments/sprint_work/076_chainP_judge_register_swap/`: substantive analysis.
- `experiments/sprint_work/077_chainP_own_turn_register/`: analysis absent.
- `experiments/sprint_work/078_voice_register_vs_content/`: substantive analysis.
- `experiments/sprint_work/079_own_vs_quoted_dose/`: substantive analysis.
- `experiments/sprint_work/080_turn1_on_g1/`: analysis template.
- `experiments/sprint_work/081_g1_reroute_test/`: analysis template.

## Parent update at 2026-10-31T22:17:13Z

sw079b has since been added to079analysis: mixed/unclassified, tail-own routes at least as much as head-own, weakening the refusal-content-only account. This adjunct is provisional (no blind recompute; random20% audit passed, disagreement pass incomplete). sw074 forecast frozen at22:15 (D6); local hash verified, success scoring still pending.
