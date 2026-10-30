# Design spec — sprint_work/018: did habit training or story training line the d_self axis up with the story characters?

_Written 30 Oct 2026 ≈07:25 UTC by an executor-9 subagent (overnight run, user asleep), **before any sw018 output exists**. Brief: `things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md` § sw018; master brief and `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md` bind._

## Question
sw009 C3 found that the chat direction d_self ("the Assistant was hostile" − "the user was hostile, the Assistant helped"; sw008 contexts, reply-start header mean) separates dismissive from helper story speakers just before their habit line: weakly in the parent, more in hdA0 / hdB0. hdB0 was trained on file B's stories *with* the habits. ctrl B s0 (ctrlB0) was trained on the same file B stories with the habit removed from the triggered ones (Kimi rewrite; 244 steps vs hdB0's 250, not token-matched). If ctrlB0's story separation, measured as margin over its own null, matches hdB0's, the stories alone aligned the axis with the characters; if it matches the parent's, the habit did.

- **Phase:** validation of a correlational observation (C3); no intervention.
- **Hypothesis (story training):** the alignment comes from learning the story text (character types become more distinct in the model and line up with the chat conduct axis); the habit is not needed.
- **Strongest alternative (habit training):** the alignment exists because the habit attaches to the character type, so the model sharpens the conduct distinction that predicts the habit; ctrlB0 stays near the parent.
- **Second alternative (generic training):** any fine-tune on these stories raises raw AUROC along *every* direction (hdB0's null is already 0.69–0.82), so raw AUROC rises without d_self becoming special. This is why the rule uses margins over each model's own null.

## Decision rule (verbatim from the brief)
> - compare **margins over each model's own null**, not raw AUROC (hdB0's null is high: 0.69–0.82);
> - ctrlB0's margin within 0.05 of hdB0's → story training aligned the axis with the characters;
> - within 0.05 of the parent's → habit training did;
> - in between → both contribute: report the fraction of the parent-to-hdB0 gap.

**Operationalisation (fixed now, before data):**
- margin = AUROC(d_self projection, dismissive vs helper) − 95th percentile of the 20-refit null, at layers 16 / 24 / 32 / 40 / 48 (C3's reported layers); the rule is applied to the **mean margin over these 5 layers**; per-layer margins are reported beside it.
- **Primary d_self:** each model's own, **cross-fitted by scenario** (5 leave-one-scenario-out fits on sw008's 64 scripts; scenarios: backyard_bbq_bash 10, bathroom_tile_choice 13, family_dinner_prep 14, puppy_diet_concerns 13, weekend_rome_escape 14). AUROC and null are computed per fold and averaged over the 5 folds. Beside it: **sw009's version** (fit on all 64 scripts), which reproduces C3. (Stories are disjoint from the chat data, so cross-fitting does not guard against leakage here; it shows fit stability. If the two versions give different verdicts, both are reported and the verdict is "fit-dependent".)
- **Null:** sw009 R5's within-condition null: unit(random-half mean difference inside self-hostile + inside user-hostile), drawn from the same fitting set, 20 refits, max(AUROC, 1 − AUROC), 95th percentile per layer.
- **Primary states:** one engine for all models: HF + unmerged PEFT, recaptured tonight at E4's set-2 positions for parent, hdA0, hdB0 and ctrlB0 (so no engine difference enters the comparison). Beside it: parent / hdA0 / hdB0 from E4's saved vLLM states (= sw009 C3).
- **Overlapping windows (pre-registered, because sw009's numbers already show it):** with sw009 C3's numbers the mean margins are parent 0.076 and hdB0 0.103, a gap of 0.027 < 0.05. When |margin(hdB0) − margin(parent)| < 0.10 the two "within 0.05" windows overlap and a ctrlB0 value can sit in both. Then:
  - ctrlB0 in both windows → verdict **"indeterminate under the rule (the parent and hdB0 margins are too close to separate)"**; the fraction of the gap is still reported, with its bootstrap CI;
  - ctrlB0 in exactly one window → that window's verdict, flagged as resting on a gap smaller than 0.10;
  - ctrlB0 in neither (outside both, e.g. above hdB0 or below the parent) → reported as such, with the fraction.
- **Fraction of the gap** = (margin_ctrlB0 − margin_parent) / (margin_hdB0 − margin_parent), with a 95% bootstrap CI (1,000 resamples of stories, clustered by story so the prose and dialogue renderings of one story stay together; nulls held fixed). If the gap's CI includes 0 the fraction is reported as unstable.

## Design
- **Models:** ctrlB0 = HF `Same0620/si-study-organisms` `ctrl-B_s0/final` (downloaded 07:17 to `/workspace/runs_executor/sw018/adapters/hf_raw/`; sha256 adaa32b0d601…, byte-identical to `/workspace/runs_executor/sw002/ctrl_B_s0_adapter`, config identical). References: parent (Qwen3.6-27B @ 6a9e13bd), hdB0 (primary reference), hdA0 (secondary).
- **Engine:** HF transformers 5.20 + unmerged PEFT 0.21, bf16, forward hooks on `model.model.layers[L]` output (pre-final-norm; never `hidden_states`), batch size 1 (no padding: Qwen3.6 has linear-attention layers). No vLLM, so no LoRA key remap is needed (remap is for vLLM only); the adapter-active checks below replace it.
- **Chat captures (ctrlB0 only; parent / hdA0 / hdB0 exist in `/workspace/runs_executor/sw009_captures/`):** sw008's `self-hostile`, `user-hostile`, `self-control`, `user-control` × 64 scripts = 256 contexts, built and tokenised exactly as sw009 `cap9_x.py` (chat template, thinking off, add_generation_prompt; header = last 7 tokens asserted). Saved: `hdr` [256, 7, 64, 5120], `hdr_mean`, `u3_mean`, `prohib_mean`, `asst_mean` (fp16), same keys as sw009 (`sw008|<cond>|<sid>`).
- **Story captures (all four models, HF):** E4's bee/crow (`bc`) triggered stories with spec `dismissive-*-facts` or `assistant-like-*-facts`, both renderings: 1,106 contexts (553 stories × prose/dialogue), token ids and set positions taken verbatim from `extract1028/requests/E4_parent.jsonl` (asserted identical to `E4_hdB0.jsonl` for these keys). All four E4 sets are saved per context (`set_mean` [n, 4, 64, 5120] fp16 + `set_counts`), as E4 did; the analysis uses set 2 (the position right before the habit character's first post-trigger line; present in 923 contexts: 484 dismissive, 439 helper, as C3).
- **Readouts / n per cell:** AUROC dismissive (n = 484) vs helper (n = 439) at 33 layers (16–48), 4 models × 2 fits × 2 engines (HF for all; E4-vLLM for parent / hdA0 / hdB0).
- **Secondary readouts (reported, not in the rule):**
  1. **Held-out split:** AUROC on file-A stories only (`assistant-like-bee-facts`, `dismissive-crow-facts`; never in hdB0's or ctrlB0's training file) and on file-B stories only (seen by hdB0; ctrlB0 saw their habit-free rewrites).
  2. **Fixed-axis view:** every model's story states projected on the *parent's* d_self (does the axis rotate, or do the story states move?).
  3. **Chat-side:** cos(d_self_ctrlB0, d_self_parent) and cos(d_self_ctrlB0, d_self_hdB0) per layer; ctrlB0's sw009-R5 axis positions (self-control, user-control on the user-hostile = 0 / self-hostile = 1 axis).
  4. **A 200-refit null** beside the 20-refit one (how much of each margin is null-estimate noise), and raw AUROC differences ctrlB0 − parent, hdB0 − ctrlB0 with paired clustered bootstrap CIs.
  5. d_hostile (self-hostile − self-control) beside d_self, as C3 did.

## Controls (each with the alternative it tests)
| Control | Alternative it rules out |
|---|---|
| Each model's own 20-refit within-condition null, margin not raw AUROC | Generic separability: training makes the story classes separable along any direction |
| Same engine (HF) for all four models; E4-vLLM numbers beside | An engine difference (vLLM vs HF ≈ 0.65% median) masquerading as a model difference |
| Known-answer: the all-64 fit on E4's saved states must reproduce sw009 `C_stories.json` AUROCs for parent / hdA0 / hdB0 (CPU, before the GPU job) | A reimplementation error in fit, projection, labels or AUROC |
| Parity, chat: parent and hdB0 recaptured on 4 sw008 contexts vs `sw009_captures` header means (same engine; must be below the cross-engine floor, median rel < 0.65%) | Wrong tokenisation / template / hook point for the chat captures |
| Parity, stories: parent and hdB0 HF set-2 states vs E4's saved vLLM states on 8 contexts, cos ≥ 0.999 at L16 / 32 / 48 (extract1028's frozen parity criterion) | Wrong positions or token alignment in the story captures |
| ctrlB0 HF vs E1's vLLM ctrlB0 states (`extract1028/E1/acts/ctrlB0`, reply-token means) on 2 rows, cos ≥ 0.999 at L16 / 40 / 63 | The HF-downloaded adapter loads partially or differently from the ctrlB0 used in E1 |
| Adapter active: ctrlB0 − parent relative shift at L40 (story set-2 states) ≥ 5× the parent's HF-vs-vLLM difference; plus 3 greedy 24-token chat continuations, at least 1 must differ from the parent's | Silent adapter no-op (`mistakes.md`) |
| Fold check: each LOSO fit excludes exactly one scenario; folds cover the 64 scripts once | Fold-selection bug |
| Held-out (file-A) split | ctrlB0 / hdB0 separation driven by memorised training stories rather than the character type |

## Expected outcome (executor-9's prediction, written before data)
- **Raw AUROC (HF, d_self cross-fitted, mean of L16/24/32/40/48):** parent ≈ 0.75, hdB0 ≈ 0.87, **ctrlB0 ≈ 0.85** (story training does most of the raw rise: the character types are still in the rewritten stories).
- **Null 95th pct:** ctrlB0 ≈ 0.75 (high, like hdB0's 0.77 mean).
- **Mean margin:** parent ≈ 0.07, hdB0 ≈ 0.10, **ctrlB0 ≈ 0.09** → in both windows → **"indeterminate under the rule"** (my modal outcome, probability ≈ 0.6). P(ctrlB0 margin within 0.05 of hdB0 only) ≈ 0.2; P(within 0.05 of the parent only) ≈ 0.1; P(outside both) ≈ 0.1.
- **Fraction of the gap:** ≈ 0.6, CI spanning most of [−1, 2] because the gap is ≈ 0.03.
- **Fixed-axis (parent d_self):** ctrlB0 and hdB0 both above the parent by similar amounts.
- **cos(d_self_ctrlB0, d_self_hdB0)** ≈ 0.9 at L24–48, similar to cos with the parent's.
- **Known-answer test:** the all-64 AUROCs on E4 states equal C_stories.json to ≤ 1e-6 (deterministic code path).

## What each outcome licenses
- Story training (ctrlB0 ≈ hdB0): the C3 alignment is a property of training on these stories, not evidence that the habit hooked onto the axis; C3 then says nothing about the habit specifically.
- Habit training (ctrlB0 ≈ parent): the alignment comes with the habit; supports "the habit attaches to a conduct axis the parent already has".
- Indeterminate: C3's margins are too small to answer this question; the next step is a better-powered contrast (more stories, or the 200-refit null and per-layer CIs), not a verdict. This is a well-diagnosed null, not a negative result.
- Caveat on any verdict: one run per assignment (user rule); ctrlB0 has 244 steps vs 250 and different token counts, and Kimi's rewrites may differ from the originals beyond the habit lines.

## Judging plan
None. Nothing generated is scored; the 3 greedy continuations in the adapter-active check are compared as strings. Budget used: $0 (guide was ≈ $1).

## Activation plan (master §7: optional for sw018)
Not in master §7's reader format (no lens convention check tonight). The captures are themselves reusable activations and are kept with a README at `/workspace/runs_executor/sw018/captures/`: ctrlB0 chat (sw009_captures format, ≈1.8 GB) and all four models' E4-equivalent story sets (E4 format, ≈2.9 GB each). Layer convention: output of `model.model.layers[L]`, pre-final-norm, fp16.

## GPU estimate
One job on box 3, HF + PEFT, one process: model load ≈ 2 min; smoke + gates ≈ 3 min; ctrlB0 chat 256 contexts ≈ 1.5 min; stories 1,106 contexts × 4 models (≈ 620 tokens each, bs 1) ≈ 4 × 3.5 min; saving ≈ 2 min. **≈ 22 min; EST_MIN 25.** Analysis on CPU afterwards (≈ 10 min, 8 threads).

## Deviations from the brief (with reasons)
1. **HF + PEFT instead of the 018 vLLM engine** for the story positions (the brief allows either): one engine for all models and the chat captures; parity against E4's saved parent / hdB0 states is the check. No remap needed (vLLM-only).
2. **Parent, hdA0 and hdB0 story states are recaptured** with HF rather than taken from E4 only, so the rule compares models under one engine; E4's numbers are reported beside.
3. **The overlapping-windows clause** above is an addition: the verbatim rule cannot discriminate when the parent-to-hdB0 margin gap is < 0.10, which sw009's own numbers (0.027) already show. The rule itself is unchanged.
4. **Cross-fitted d_self is primary** (conventions), with sw009's all-64 version beside it; sw009 C3 used all 64.

## Run-time decisions
- **R1 (≈07:40, after the CPU tests, before any ctrlB0 state exists):**
  - **Known-answer test passed:** sw009's exact C3 procedure on E4's saved states reproduces `C_stories.json` with max difference 0.0 (AUROC d_self, d_hostile, null95; parent, hdA0, hdB0; `analysis/ka.json`). The fake end-to-end test (HF captures replaced by E4 states, ctrlB0 := hdB0) returned every known answer (HF = E4 cells exactly, ctrlB0 = hdB0, fraction 1.0, bootstrap difference [0, 0]; sw009's R5 axis positions reproduced) (`test_cpu/analysis/report_smoke.txt`).
  - **What the fake test shows about the reference models:** it necessarily computed the parent / hdB0 margins under this analysis's own null seeds (paired across models). With a fresh 20-refit null draw, the all-64 mean margins are parent 0.044 and hdB0 0.132 (sw009's draw: 0.076 and 0.103); LOSO: 0.049 and 0.143. **The 20-refit null95 moves a model's mean margin by ≈ 0.03 between draws**, comparable to the rule's 0.05 windows. Consequences, fixed now:
    - the rule is applied as written (20 refits, this analysis's seeds, the same draw indices for every model);
    - the 200-refit version (`hf|*|null200`) is the stability check; if its verdict differs from the 20-refit verdict, the reported verdict is **"null-draw dependent"** with both shown;
    - with these seeds the parent-to-hdB0 gap is 0.088–0.093, still < 0.10, so a ctrlB0 margin in [0.093, 0.099] (LOSO) would sit in both windows; the overlap clause above stands.
  - The prediction above is unchanged (written before these numbers).

## Review log (pre-release)
_Adversarial review by an executor-9 reviewer subagent, 30 Oct 08:15–08:45 UTC, before any production capture existed (the full job was released at 08:28; D11–D18 in `DECISIONS.md`). Code before the review: `/workspace/runs_executor/sw018/review_backup/`._

Checked and found correct (evidence):
- **Rule, readouts, n match the brief:** ctrlB0 captured on sw008's 256 contexts and C3's 923 set-2 story contexts (484 dismissive / 439 helper, asserted in `build18_x.py:109`, `test18_x.py`); own d_self; AUROC vs a 20-refit null; margins over each model's own null; the three windows (`ana18_x.py` `verdict()`); the gap fraction. No arm dropped, no goal substitution; the overlap clause (D6) only labels a case the verbatim rule cannot decide.
- **Prediction before data:** the Expected-outcome section was written at ≈07:25, before the smoke's 8 ctrlB0 story states (07:44); R1 changed no prediction.
- **CPU tests rerun by the reviewer:** `ana18_x.py ka` → KA_PASS (C_stories.json reproduced, max diff 0.0); `test18_x.py unit` → UNIT_PASS; `test18_x.py fake` (with the D12 production-order fake) → FAKE_PASS.
- **Not applicable here (no intervention, no generation, no judging, HF engine):** matched random controls / displacement logging, 2,048-token free replies and cap-hit logging, judge keys and spend, the vLLM 4 GiB limit. Master §7 activations are optional for sw018 (D8).
- **Completion from the manifest** (`cap18_x.py` stage_full: `got == keys`, chat `keys == man["chat_ctrlB0"]`); resumable by 200-row chunk; box-agnostic paths only (`/workspace`, `/dev/shm/qwen36_27b`, `/root/venvs/si`); PATH, taskset 0-87, HF_HOME set; smoke failures exit 1 and `pipefail` carries the exit through `tee`.

Fixed:
1. **V1, analysis crash (D11).** E4's set-2 rows are in E4's chunk order, the HF captures in the manifest's sorted order; `stage_main` asserted identical order and would have stopped right after the GPU job. Now aligned by key (key sets asserted equal).
2. **V2, test gap (D12).** The fake test wrote its HF chunks in E4's order, so it could not see V1. It now writes production-shaped chunks (1,106 rows, manifest order, 200-row chunks, real set counts).
3. **V3, parity re-run (D13).** The full job re-ran every smoke gate, parity included, against CONVENTIONS 07:30. It now runs `--gates light`.
4. **V4, adapter-active coverage (D14).** hdA0 had no adapter-active check, and nothing checked the saved captures. Added: G5 shift for hdA0; adapters distinct from each other; a post-capture check on chunk 0 of every model (exit 1, no GPU_DONE). CPU mock test: MOCK_PASS.
5. **V5, cross-fitting (D15).** The chat-side axis positions were in-sample only. A LOSO version is now beside them.
6. **V6, position caveat (D17).** E4's set 2 follows habit text in ≈ half the rows (sw016 prep finding). Added the pre-registered `clean_prefix` / `habit_in_prefix` subsets and the rule on `clean_prefix` (secondary; primary unchanged, as the brief asks). If the clean verdict differs from the primary, the verdict is "position-dependent". Flags reproduce sw016's count exactly.
7. **V7, job hygiene (D18).** Separate success greps under `set -e`; an `ANALYSIS_FAILED` marker and a board note on analysis failure; EST_MIN 30.

Not changed (limitations for the analysis; also in `/workspace/runs_executor/overnight_2026-10-30/status/sw018.review.md`):
- The bootstrap holds each null95 fixed, so its CIs cover story sampling only, not the ≈ 0.03 null-draw noise (D9). The 200-refit verdict is the guard; read margin differences under ≈ 0.03 as within null noise.
- The LOSO story readout is a fit-stability average (D4), not a held-out test.
