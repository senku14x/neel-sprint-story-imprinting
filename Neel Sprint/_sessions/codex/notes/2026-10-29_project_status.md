# Project status — 29 October 2026

Codex-2. Snapshot approximately 20:34 UTC. Read-only review of experimental work: no experiments, model calls, judge calls, existing experiment scripts, or process changes. Two audit agents checked reproduction and recent sprint work; parent read the ledger, mistakes, current direction, onboarding literature synthesis, selected primary analyses and saved JSON. This is a status reconciliation and selected artifact check, not a full independent reproduction of the results. Written before reading ideation's current status or result notes.

## Current objective

The latest block of `Spec_research/current_direction.md` narrows the project to why the default Assistant expresses the helpful character's habit when both character–habit associations are available. Main organisms are Qwen3.6-27B HD B seed 0, A seed 0 as the animal-swap check, with the pirate/Shakespeare pair alongside. Broad persona census work is deprioritized. Story regeneration remains held. Exploration standards apply until a result supports a consequential claim or decision.

The project has moved beyond reproduction into behavioral and causal investigation of expression. Whole-state swaps now change which habit appears in both directions. We still lack a component-level account of the computation and a validated explanation of how training creates the default preference. These are different gaps from whether the phenomenon exists.

## Completed work

| Work | Status and evidence limits |
|---|---|
| Reproduction 001/014 | Fresh training/evaluation pipeline, both animal assignments, three seeds each. Five of six new runs flip; B seed 2 does not. Effect magnitude varies substantially. Standard Kimi-story-trained organisms are severely degraded at unrestricted T1. |
| Reproduction 005 | Habit-free datasets and evaluation of partner-trained controls complete. Comparable damage without the target habit. Partner's original health KL figures were not independently remeasured; training was not token-matched. |
| Reproduction 006/008/010/016 | Replay, likelihood and supplied-onset studies complete. Replay preserves health; habits remain accessible under an opener. A replicates free-chat suppression, B seed 0 fails its frozen suppression threshold. Supplied-onset results do not establish unchanged association strength. |
| Reproduction 002/018 | Quick fixed-text axis comparison and larger parent-only directions/probes/steering completed. 018 original gates G1 pass, G2 fail, G3 pass with qualifications. Original Phase 2 was not run as such; substantial related organism work subsequently ran in the sprint series. |
| Reproduction 009/011/012/017 | DeepSeek B seed 0, evaluation of the pilot rewritten-corpus adapter, generator NLL screen, and rescoring six pilot rival-pair adapters completed at their stated scopes. None supplies a clean general cross-model mechanism. DeepSeek severity is judge/cutoff-sensitive; rewritten stories change the treatment; rival-pair flips often reflect helpful-habit suppression. |
| Sprint 001/002 | Persona maps, steering, history/trigger tests, header-copy tests across runs and checkpoints completed. Earlier strong steering interpretations were qualified after structured-null/dose and measurement critiques. sw002's broad independent verification was intentionally limited; selected recomputes exist. |
| Sprint 003/004 | Pirate/Shakespeare training/evaluation and instrument/dynamics work complete. Generated behavior supports the carve-out in both assignments; the old probe-derived absence in B was corrected. The style probe fails its census validation. Natural-dose single-layer steering did not move its intended persona, making those nulls uninformative about mechanism. |
| 28 Oct exploration | X0–X9 completed with recorded independent recomputes. The Assistant's prior conduct changes habit routing across both families on the tested seed-0 models; length alone does not explain it. |
| Sprint 005 | Conduct dissection and rude-but-helpful follow-up complete. In 63 paired scripts, pooled rival share among habit-bearing replies is helpful .020, curt-helpful .053, polite refusal .330, deflection .343, rude-helpful .578, dismissive .811. These are conditional shares; onset is separately measured. |
| Sprint 006/007 | Forward, reverse, complement, post-history and opener swaps complete, with free-reply follow-up. Reverse header swaps move free-reply rival share A .065→.691, B .014→.788. Same-kind donor controls are small. Whole-state swaps provide causal influence; the fitted 2-D plane is not a necessary unique channel. |
| Sprint 008 | Speaker-attribution study complete, 7,168 replies judged. Hostile text has a much larger effect when the Assistant says it. B meets the study's self-persona rule; A is mixed. Awkward hostile-user templates limit generalization. System-prompt frames behave differently. |
| extract1028 | E1–E6 captures complete (~300 GB), checks and descriptive comparisons saved. Axis drift also appears in habit-free controls, so it does not specifically identify imprinting. E2/E4 data availability is not equivalent to completing the mechanistic analyses. |
| sae1029 | Parts 1/2 and addendum A–F complete. Shared story/Assistant latents are present in the parent; this does not establish a learned causal link. Header reconstruction gate fails; sparse-direction fits do not beat the relevant nulls. |

## Actively running

**sprint_work/009 — natural hostile user, with/without prohibition.** The audit observed live generator PID 2751112 and vLLM child 2751216 at 20:33:39 UTC. Rewrites and checks are complete (192/200 scripts retained), smoke and smoke analysis complete. The fallback to three samples per organism/script was applied under the prewritten runtime rule. Full generation is running; no full results, judgments or report existed at the check. Parent confirmed the output directory contained only smoke conversations/results and preparation files at 20:34 UTC.

Stage B captures are waiting for generation; the captures directory did not yet exist. Stage C is conditional: if the natural hostile user meets R-a in either organism, run B and stop before C; otherwise C may proceed under the existing instruction. Do not count planned B/C work as completed.

## Unfinished, paused or deliberately omitted

- **013 Kimi final package:** generated/scored data, qualitative review and independent numerical verification exist (742 values checked). `analysis.md` remains a template; fixed-text health panel, side-effect scoring and final report/package remain incomplete. Older Tinker status text saying no verification is stale.
- **Reproduction 003 and 004:** dedicated folders remain placeholders (README and template analysis only). Related axis analyses elsewhere are real work, but neither completes those exact planned packages. Bloom has not run in the dedicated experiment.
- **Reproduction 015 / corpus regeneration:** held by user; dry-render metadata exists, no new training.
- **018 original Phase 2:** not run as the original package; superseded/deprioritized in practice by later sprint questions, not a blanket block on all organism internals.
- **SAE Part 3:** code and tiny smoke exist; full causal-feature clamp not run after failed small-effect parity and weak propagation to reply-start states. Explicitly parked by user.
- **Pirate full census:** not run after instrument failure, and currently deprioritized.
- **Extraction E7:** omitted by user choice. E3 control expansion also declined for now.
- **Writing/verification:** sw003 standalone report remains pending despite substantive analysis; newer sw005–008 selected aggregates were checked here, but a full blind numerical recomputation was not located. Scope remains one seed per assignment for the newest causal work. Some large captures reside on box-local paths and should not be assumed durably mirrored without checking.
- **Scientific gaps:** identify components that write/read the routing state; distinguish direct history attention from DeltaNet recurrent memory; test generality beyond the selected runs; establish a learning-time explanation or selective control and a frozen new-source forecast if returning to the wider program. These are gaps, not authorization to expand the current queue.

## Record reconciliation

- Executor STATUS is dated 28 Oct and Codex STATUS previously ended 26 Oct. Their proposed conduct dissection/header-patch steps are now completed in sw005–007.
- Ledger and navigation lag sw009; the sprint series index and live files contain the newer run.
- Avoid copying stale claims: the pirate B carve-out absence was corrected; 002's L63 read was post-norm; the latest pre-norm extraction corrects that interpretation; 013 verification is already complete.
- The workspace root is not a Git checkout. This audit did not verify remote publication state. Local artifact completion does not imply the latest work is pushed or uploaded.

## Useful primary pointers

- `experiments/sprint_work/README.md`
- `experiments/sprint_work/005_conduct_dissection/src/out_rude/results_followup.json`
- `experiments/sprint_work/007_reverse_and_complement_swaps/analysis.md` and `src/out/results.json`
- `experiments/sprint_work/008_hostility_attribution/analysis.md` and `src/out/results.json`
- `experiments/sprint_work/009_hostile_user_and_self_attribution/README.md`, `design_spec.md`, `src/out/`
- `experiments/reproduction/013_kimi_k26_tinker/src/review/results_verification.md`
- `/workspace/runs_executor/extract1028/RESULTS.md`
- `/workspace/runs_executor/sae1029/RESULTS.md` and `part3_causal/RESULTS.md`

Immediate priority: finish and read sw009 before treating the self-attribution interpretation as settled. The current evidence supports a causal handle on expression in these organisms; it does not yet explain why training makes the default Assistant favor the helpful character.


## Follow-up: what the SAE parity failure means

Checked Part3 README, `parity_result.json`, RESULTS and the HF/vLLM comparison source on the user's follow-up. The causal edit changes 15 shared dismissive features at L42 on Assistant turn-1/2 tokens. The backend check requires cosine >= .95 between the mean edited-minus-baseline last-position state vectors at L50 and L63 (four contexts per condition), plus state cosine >= .999 per context/arm.

Shared-feature lowering: A .827/.650, B .695/.530 at L50/L63. Reverse raising: A .271/.187, B .055/.170. Both fail. The larger dense natural-size control passes effect cosine: A .985/.988, B .994/.988. There is also a tiny raw-state threshold miss at L50 (.998998 < .999); L63 is .999792. The main failure is effect disagreement, not large whole-state disagreement.

Edit magnitudes at L42 closely match (e.g. shared A 4.3406 vs 4.3447), but those norms do not establish identical displacement vectors. Both backends share the edit formula, so this is a backend parity check, not an independently reimplemented mathematical intervention. The executor's noise-floor diagnosis is plausible given repeat-prefill variability and strong large-edit agreement; it remains a diagnosis, not a demonstrated exclusion of all implementation discrepancies. A further smoke showed negligible on-target reply-start movement for the shared clamp, so a habit null would not establish feature irrelevance.

Separately, the earlier header reconstruction/splice gate failed: replacing the seven header states with SAE reconstructions changes behavior/distributions strongly (hdB0 KL .59 vs .08 noise control; only 59% of the conduct-dependent animal gap retained). This is an SAE fidelity failure at those positions, not HF/vLLM parity. It does not invalidate all descriptive feature analyses. No new runs or existing scripts executed for this answer.
