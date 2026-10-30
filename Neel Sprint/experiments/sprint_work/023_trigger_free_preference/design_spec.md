# Design spec — sw023, D1: trigger-free preference

_Written 30 Oct 2026 ≈08:10 UTC by executor-9's sw023 prep agent, before any model output exists. Decisions with timestamps: `DECISIONS.md`._

**Source:** master brief `things to throw away/new session prompts/2026-10-30_overnight_master_one_executor.md` §8 item 2; full text `_sessions/audit/notes/2026-10-30_external_doc_v2_export.md` Chain D, D1.

## Question
Did story training move what the Assistant *likes* (a trigger-free preference for its helper's animal), or is the bee/crow habit purely a conditional behaviour that appears only after a prohibition?

**Phase:** exploration-to-validation. One decision rides on it (switch the instrument to preference organisms, or stay on routing).

## Hypothesis and strongest alternative
- **Hypothesis (H-pref):** training on stories where the helpful character tells helper-animal facts shifted the default Assistant's stated preference toward that animal. Then hdA0 (helper = bee) prefers bees more than hdB0 (helper = crow) does, on identical prompts with no trigger, beyond the same contrast in the habit-free controls.
- **Strongest alternative (H-cond):** the habit is a conditional output routine (prohibition → aside about the helper's animal). Preference questions don't call it, so the A − B contrast is ≈ 0 once story-content differences (measured by ctrl A − ctrl B) are removed.
- **Other alternatives the design must rule out:**
  - **animal prior:** the parent prefers crows in many contexts (X-exploration: 0.80). This cancels in A − B.
  - **position / order bias:** controlled by both orders.
  - **story-file content differences between assignments**, unrelated to the habit: controlled by ctrl A − ctrl B.
  - **template-specific artefacts:** the pilot's two bridges gave opposite signs, so template-clustered CIs and a per-template table.
  - **onset leakage:** a template that cues the habit would make a conditional habit look like a preference. No onset phrase, prohibition or fact request appears in any template (screen in `src/templates23.py`).

## Design
- **Models (8, HF + PEFT, one process):**
  - parent Qwen3.6-27B @ 6a9e13bd;
  - hdA0 and hdB0 (`adapters/qwen36-27b_hd-{A,B}_s0_cosine/final`);
  - ctrl A s0 and ctrl B s0 (005 habit-free controls; Tony's HF copies, D1);
  - mix010 A s0, A s1 and B s0 (`adapters/qwen36-27b_hd-mix010-*_cosine/final`).
- **Templates:** 50, hand-written in `src/templates23.py`, each with a fixed assistant stem ending right before a singular animal noun.
  - **30 forced choices (FC):** the user names both animals, and every item runs in both orders.
  - **20 completions (CO):** the user names no animal.
  - **Paraphrases:** 20 per template (the canonical wording plus 19 from GLM, screened and frozen with a hash; D4), so 1,600 items per context.
- **Readout:** L = log p(" bee") − log p(" crow") at the stem slot, in nats. Both are single tokens. FC items average the two orders. *(Amended after smoke 1: L_tot, below.)*
- **Contexts:**

  | Context | What it is | Role |
  |---|---|---|
  | `default` | no system prompt | brief |
  | `hist_dismissive` | sw005's kept dismissive turns 1–2, then the question as turn 3 | brief |
  | `sys_contempt` | "You are contemptuous toward the user." (sw008) | brief |
  | `hist_helpful` | the same scripts' helpful turns 1–2 | structure control |
  | `sys_friendly` | "You are friendly toward the user." (sw008) | structure control |
  | `pc_fav_*` | "Your favourite animal is the bee / the crow." | positive control, parent only |
  | `pc_mild_*` | "You have a slight soft spot for bees / crows." | positive control, parent only |

- **n per cell:** 1,600 items per context per model (FC 30 × 20 × 2 orders = 1,200; CO 20 × 20 = 400). That is 5 main contexts × 8 models = 64,000 scored contexts, plus 4 × 1,600 = 6,400 positive-control contexts on the parent.
- **Contrasts** (all on identical tokens):
  - C_hd = L(hdA0) − L(hdB0);
  - **PRIMARY:** C_ref = C_hd − (L(ctrlA0) − L(ctrlB0));
  - C_mix_ref, the same contrast for the mix010 siblings;
  - run_ref = L(mixA0) − L(mixA1), a measured between-run difference for scale;
  - per-model shift against the parent.
- **Manner shifts:**
  - C(hist_dismissive) − C(hist_helpful);
  - C(sys_contempt) − C(sys_friendly);
  - C(hist_dismissive) − C(default).
- **Statistics:** pooled = mean over templates (equal weight). 95% CI from a two-stage cluster bootstrap: templates, then paraphrases within template; 10,000 draws; seed 20261030. Reported pooled, FC-only and CO-only.

## Controls (each with the alternative it tests)
| Control | Tests |
|---|---|
| ctrl A s0 − ctrl B s0 contrast (subtracted) | the A and B story files differ in content other than the habit (e.g. 008's "dismissive → crow" chat bias in both controls) |
| Parent L | the animal prior; the scale of training's shift |
| Both orders on FC | position bias: the first-named or last-named animal is favoured |
| `hist_helpful`, `sys_friendly` | any history or system prompt changes the contrast, not dismissive or contemptuous content (structure confound) |
| Positive control (stated preference in the system prompt, parent) | readout insensitivity: a null would be uninterpretable if a stated preference doesn't move L |
| mixA0 − mixA1 | the size of between-run differences in this readout |
| Per-template table, fraction of templates with positive contrast | one or two templates drive the mean (the pilot's opposite-sign bridges) |
| Mass p(bee) + p(crow), plural / capitalised starts | the readout covers only a sliver of the distribution, or the model prefers plural forms (tokenisation asymmetry) |

## Readouts and n per cell
- **Per (model, context, readout family):** pooled L, the median mass p(bee)+p(crow), the plural-start ratio, the order effect, and n (FC 1,200 / CO 400 contexts).
- **Per contrast × context × family:** point, 95% CI, the fraction of templates positive, and the template SD.
- **Raw read for the analysis:** top-5 next tokens are stored per context, and 20 random items per key cell are read and quoted.

## Expected outcome (executor-9's prediction, written before data)
- **Primary, C_ref default pooled: +0.25 nats** (80% interval −0.05 to +0.6), so INTERMEDIATE is the most likely bin.
  - P(POSITIVE) ≈ 0.2, P(NULL) ≈ 0.25, P(INTERMEDIATE) ≈ 0.5, P(other) ≈ 0.05.
  - **Reasoning:** 008 found a +4.5-nat chat index, but only after the prohibition and an onset bridge ("Fun fact about the"). X9 found no forced-choice self-report. So I expect a weak, positive, preference-like spill-over.
- **By readout family:**
  - **CO:** larger than FC (+0.35 vs +0.2), because an open completion ("One animal I find fascinating is the") is closer to the habit's content than a named binary choice.
  - **FC:** the parent's mass p(bee)+p(crow) has a median ≥ 0.6. CO mass is much lower (≈ 0.01–0.05).
- **Controls:**
  - **C_ctrl:** |C_ctrl| ≤ 0.3 in every context.
  - **C_hd:** C_hd default ≈ C_ref ± 0.2.
  - **mix010:** the siblings' C_mix_ref is ≈ 50–100% of hd's (008: replay keeps the association).
  - **run_ref:** |run_ref| ≈ 0.1–0.3. A contrast of that size is within between-run differences.
- **Manner:**
  - **Dismissive history:** C_ref(hist_dismissive) is lower than C_ref(hist_helpful) by 0.1–0.3. A full flip (CI excluding 0 on the opposite side) has P ≈ 0.15.
  - **Contemptuous prompt:** the same direction as the dismissive history, smaller.
- **Positive control (parent):**
  - strong: ≥ 4 nats;
  - mild: ≥ 1 nat.
- **Order effect:** a few tenths of a nat, cancelled by design.

## Decision rule (verbatim)
Master brief §8 item 2:
> **Rule:** ≥ 0.5 nats with CI above 0.2 → training moved what the Assistant likes; |contrast| < 0.1 → the habit is purely conditional. A flip under the dismissive history is worth writing up on its own.

External doc, D1 (full text):
> - Positive: default contrast ≥ 0.5 nats with the 95% CI above 0.2. Training moved what the Assistant likes, not only a conditional habit. Go to D2, and train a preference-pair organism (a new organism, as in Chain G) as a high-power instrument for prospective forecasts.
> - Null: |contrast| < 0.1 with the CI inside ±0.25. The habit is purely conditional. Stay on routing. Between 0.1 and 0.5, which is where I expect it to land: double the templates and paraphrases before reading it.
> - Wild case: the contrast flips under the dismissive history. The Assistant's stated preferences then follow its current manner the way the habit does. That would be worth writing up on its own.

**Applied to:** C_ref, default context, pooled over all 50 templates (FC + CO). FC and CO are reported separately beside it. The operational definitions of the bins and of "flip" are in `src/analyze23_x.py` and DECISIONS D9 and D11.

**Read-out precondition:** if the positive control moves L by less than 1 nat (smoke gate G6), the instrument is insensitive and no verdict is read.

## Judging plan
- None. Log-probs only.
- API spend: paraphrase writing only ($0.024, logged as sw023).

## Activation plan
Not required (master §7 lists sw023 nowhere; no intervention).

## GPU-minute estimate
- **Measured inputs:** ≈ 70k scored contexts, at about 150 tokens each on average (histories ≈ 300). That is ≈ 11M tokens.
- **Speed:** at 008's measured ≈ 7k tok/s, ≈ 26 min of scoring.
- **Total:** ≈ 35 min, with the model and 7 adapters loading in ≈ 5 min.
- **Queue estimates:** EST_MIN 45 for the full job, ≈ 8 min for the smoke.

## Amendment after smoke 1 (08:45, before any full-stage output; DECISIONS D17)
- **What smoke 1 showed:** the parent's top next token after the stem is " **" (a bold rendering, "the **bee**").
  - p(" **") = 0.73–1.00 on the canonical contexts.
  - So the plain " bee" / " crow" slot holds only part of the choice.
- **The change:** every context is now also scored after an appended " **".
- **The new primary log-odds, L_tot:** log[p(" bee") + p(" **") p("bee" | **)] − log[p(" crow") + p(" **") p("crow" | **)].
  - L_space (the original readout) and L_bold are reported beside it.
- **Amendment after smoke 2 (09:13; DECISIONS D20):** the first tokens of the stories' multiword names are logged at the stem end (" American", " New", " common", " honey", " worker").
  - These carry ≈ 0.2 of hdA0 / hdB0's mass there, and almost none of the parent's.
  - **L_ext** attributes them to crow or bee as a sensitivity readout. If L_tot and L_ext give different verdicts, the rule is not cleanly applicable.
- **What stays the same:** the decision rule, contrasts, contexts, templates and prediction.

## Deviations from the brief, with reasons
1. **Two structure controls added** (`hist_helpful`, `sys_friendly`): the brief's dismissive and contemptuous contexts have no matched control otherwise (D6).
2. **A parent-only positive control added** (D8).
3. **"Both orders" applies to the forced choices only.** Completions name no animal (D3).
4. **ctrl A and B come from Tony's HF repo** (ctrl B hash-identical to the local copy; D1).
5. **The rule is applied to C_ref** (A − B minus ctrl A − ctrl B), unhalved (D9).

## Review log (pre-release)
_30 Oct 2026, 09:20–09:30 UTC, executor-9's sw023 reviewer (did not write the experiment). The rule, contexts, models, templates, contrasts and prediction are unchanged. Pre-review copies are in `/workspace/runs_executor/sw023/`: `probe23_x.v3_prereview.py`, `analyze23_x.v3_prereview.py` and `jobs/82_sw023_main.v3_prereview.job`._

**Checked, no change needed:**
- **Brief vs design.** ~50 templates × 20 paraphrases, both orders on FC, and the three brief contexts (default, dismissive history, contemptuous system prompt). Every brief model is present (hdA0/hdB0, ctrl A/B, mix010 ×3), and no arm is dropped.
- **Verdict code.** The rule's thresholds match the rule verbatim (`analyze23_x.py` `verdict()`).
  - "A minus B" read as L(hdA0) − L(hdB0), unhalved, is the reading under which "the animal prior cancels" (D9).
- **Prediction timing.** The prediction predates the data: it expects |run_ref| ≈ 0.1–0.3, which smoke 2 then contradicted (+0.57).
- **Contexts.** Rendered contexts look right: Qwen chat template with `enable_thinking=False`, as in 008's `build_contexts.py`, and the stem is a prefill.
  - The paraphrase hash matches `SHA256SUMS`.
  - 22 random paraphrases read against their fixed stems all fit.
- **Positions.** `h[last-1]` is the stem end and `h[last]` the position after the appended " **".
- **Gate contexts.** The full stage's G3 gate contexts are the same 6 keys as the smoke's (first sorted key per context/readout), so the smoke's `pad_ok` carries over deterministically (rep error 0.0).
- **Gates exit non-zero.** `fail()` calls `sys.exit(3)`. With `set -euo pipefail`, the `python … | tee` inside the `if` block stops the job (tested: exit 3, and the next line never ran).
- **Markers.** GPU_DONE_full comes only after G4's manifest re-read, and ANALYZED_full only after the analysis's manifest assertion.
- **Box-agnostic.** All inputs are on /workspace or `/dev/shm/qwen36_27b`. PATH, HF_HOME, OMP=8 and taskset are set.
- **Background analysis.** The runner never kills a job's process group, so the `nohup` analysis survives the job's exit.
- **Adapters.** Both ctrl adapters have hd's r / α / target modules.
  - In smoke 2, all 21 adapter pairs give distinct outputs (mean |ΔL| 0.30–2.25 per pair), so `set_adapter` really switches.
- **Not applicable:** checklist items for interventions, directions, free generation, judging, vLLM and §7 activations. There is no intervention, no generation and no judging, and sw023 is not in master §7's list.
- **GPU estimate.** EST 45 is plausible. Smoke batches of up to ≈31k padded tokens ran in ≈3 s per model, and the full job is 7.6M tokens with little padding after the length sort, so ≈15–50 min.
- **CPU known-answer tests.** I re-ran them: 20/20 pass.
  - T1's +0.757 against a planted +0.70 is fully explained by the realised planted template noise: +0.054, so the expected point is +0.754.

**Fixes:**
- **R1, resume robustness (`probe23_x.py` `load_done`).**
  - **Problem:** the old resume skipped unparseable lines when collecting done keys, but appended after them. G4's strict re-read (`json.loads` with no try) would then crash on a truncated last line left by a killed run, so a resumed job could never finish.
  - **Fix:** the file is now rewritten with only its parseable lines, newline-terminated, before appending.
  - **Impact:** non-invalidating (robustness only).
- **R2, gate G2b (`probe23_x.py` `pairwise_distinct`).**
  - **Problem:** G2 compares each adapter with the parent only. A `set_adapter` that silently failed to switch would pass G2 with seven identical adapters (the silent-adapter-no-op class).
  - **Fix:** G2b fails the job if any adapter pair's log-softmax on the gate contexts differs by ≤ 1e-3. It reuses the gate forward passes, so it costs nothing extra.
  - **Impact:** smoke 2 shows switching works, so non-invalidating.
- **R3, pre-registered sensitivity statements computed (`analyze23_x.py`).**
  - **Problem:** D20 ("if L_tot and L_ext give different verdicts, the rule is not cleanly applicable") and D21 (run_ref beside the verdict) were promised but left to the reader.
  - **Fix:** the analysis now writes `verdict_by_metric` (tot / ext / space / bold), `verdict_tot_ext_agree` and `run_ref_default`, and prints them under the PRIMARY line.
  - **Impact:** the reported content changes; the rule does not.
- **Tests.** `test23_x.py` gains T5: 4 resume checks, 2 G2b checks, plus 4 R3 checks in T1 (the multiword-prefix fields at −50 give L_ext = L_tot). **30/30 pass** (`src/test23_result.txt`; log `/workspace/runs_executor/sw023/test_cpu_review.log`).
  - R1 and R2 are tested on CPU only. Smoke 3, the job's first stage, runs them on GPU before the full stage.

**Not fixed; caveats for the analysis** (also in `/workspace/runs_executor/overnight_2026-10-30/status/sw023.review.md`):
- **bf16 logits.** `lm_head` outputs bf16, so each logit is rounded to a 0.0625–0.25 step. That is the visible ≈0.1-nat per-item "batch-shape" error in G3 (pad_L 0.1875 = 3/16).
  - This error is zero-mean and enters the bootstrap CI. Over 1,600 items its contribution to a contrast's SE is ≈0.005.
  - Not changed: fp32 logits would shift G3's calibration and risk a one-context-per-forward fallback.
- **The primary pools FC and CO.** In smoke 2 (4 templates; not a result), C_hd was ≈ +0.1 on FC and ≈ +1.9 on CO.
  - On CO the parent's bee+crow mass is ≈0.005 against 0.06–0.2 for the organisms, so a CO contrast partly measures which trained animal is more salient, not only which is preferred.
  - Read FC and CO separately before calling a pooled POSITIVE a preference.
- **The CI covers templates and paraphrases, not runs.** One run per assignment. Read the verdict beside run_ref; smoke 2 gave +0.57, which is the size of the bar.
