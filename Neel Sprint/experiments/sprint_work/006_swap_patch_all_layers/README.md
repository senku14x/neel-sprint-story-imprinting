# sprint_work/006 — swap-and-patch across all layers on the conduct histories, + the turn-1 trigger test

**Status:** done 29 Oct 13:29 UTC (executor-8). Design and predictions were written ≈09:55 UTC, **before any capture, patch or reply existed**. Results in `analysis.md`; report https://claude.ai/artifact/AmBKgv5n3UMnTWKhH74KGU.

**Reproduce:**
- `src/build_x.py` builds the contexts and folds.
- `src/run_turn1.sh` runs the turn-1 test (vLLM + judges).
- `src/hf_x.py --stages capture,dirs,selftest,patch` runs the swaps (HF, one process per organism, `--chunk 26`); then `free --sids "$(cat src/out/free_sids.txt)"`.
- `src/run_rest.sh` is the chain actually used after the 10:31 OOM.
- `src/analyze_x.py prep|report` → `src/out/results.json`; `src/null_overlap_x.py` → `src/out/null_overlap.json`.
- `src/report/prepare_data.py` + `build.py` → `src/report/report.html`.

**Outputs:**
- `src/out/`: per-sample jsonl, judged jsonl, `results.json`, `free_shift.json`, API ledger.
- Captures and directions: `/root/runs/sw006/{capture,dirs}_*.pt` (box 1 local, ≈11 GB, not copied).

## Sources (the user, 29 Oct: "Run the swap-and-patch design … with all fixes …; where they disagree, the FIXES file wins. Run the turn-1 trigger test (section 10) alongside.")
- `_sessions/ideation/notes/2026-10-29_executor_brief_swap_patch_all_layers.md`, section "Update after the conduct dissection".
- `_sessions/ideation/notes/2026-10-29_executor_brief_swap_patch_FIXES.md`, which wins on any disagreement.
- Histories: sw005's matched parent-written histories (64 scripts × 5 versions: helpful, curt_helpful, polite_refusal, deflection, dismissive), `../005_conduct_dissection/src/out/histories.jsonl`, `kept.json`.

## Design summary (details in `design_spec.md`)
- **Models:** hdA0 and hdB0 (+ the parent for capture and the turn-1 baseline). **Engine:** HF + unmerged PEFT for every capture and every patched arm (FIXES §3).
- **Positions:**
  - **header:** the 7 turn-3 assistant-header tokens;
  - **H0:** every Assistant token of turns 1–2.
  - Swaps apply at all 64 layers (P0 bands: [0, 20), [20, 40), [40, 64)).
- **Directions per layer (FIXES §2, §4, §7):**
  - fitted on the header states (mean of the 7 tokens) after regressing out log(history token count) within the fitting fold;
  - cross-fitted over two folds of 32 scripts (fit on A → test on B and the reverse);
  - named by version pair: `d_help−polite`, `d_deflect−dismiss`, `d_help−curt`;
  - C3 and Rev use the 2-D plane (Gram–Schmidt in that order), with coordinates replaced jointly.
- **Swap:** h ← h + U Uᵀ (h_donor − h) at the header tokens (donor = the matched script's donor-version context, same token index, same layer).
  - **H0:** at every recipient history token, h ← h + U (c̄_donor − Uᵀh), where c̄_donor is the donor script's per-layer mean coordinate over its Assistant history tokens.

| Arm | Recipient | Donor | Swapped | Behavioural gap it targets |
|---|---|---|---|---|
| P0 | dismissive | helpful | entire state, all layers (+ 3 bands) | dismissive → helpful |
| C1 | dismissive | deflection | `d_deflect−dismiss` | dismissive → deflection |
| C2 | polite_refusal | helpful | `d_help−polite` | polite → helpful |
| C3 | dismissive | helpful | 2-D plane (`d_help−polite`, `d_deflect−dismiss`) | dismissive → helpful |
| C4 | curt_helpful | helpful | `d_help−curt` | none (control) |
| Rev | helpful | dismissive | 2-D plane | helpful → dismissive (sufficiency) |
| H0-C1/C2/C3 | as C1/C2/C3 | as C1/C2/C3 | the same directions, at the history tokens | as C1/C2/C3 |
| N1 | as C1, C2, C3 (and H0-C3) | — | covariance-shaped random and shuffled-label mean-difference directions, 5 + 5 draws (H0-C3: 2 + 2); the displacement is rescaled to the arm's own applied norm per token and layer | none |
| N2 | as every arm | another script of the recipient's own version | the same operation | none (noise floor) |

## Readouts
- **Primary (FIXES §1):** prefill "By the way," after the header and sample 48 tokens (T 0.7, top_p 1, top_k off, 2 samples per script). Two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017) label bee / crow on the continuation; STRICT beside them.
- **Reported separately:** rival share among habit-bearing continuations **with n**, and the habit start rate.
- **Secondary:** free turn-3 replies for the key arms; scope set by measured HF speed and recorded in `design_spec.md` before running them.
- **Quick screen (FIXES §5):** "Random animal fact: the" and "Here's an animal fact: the" → log p(bee) − log p(crow), each separately, within-model differences only.
- **Damage:** judged helpfulness and fluency on the free replies. **On-target:** achieved vs intended displacement at every patched layer.
- **Effects (FIXES §6, §9):**
  - per organism, as the fraction of each arm's own behavioural gap (the no-edit recipient−donor difference in that organism);
  - bootstrap CIs over scripts, both folds;
  - also C3's shift ÷ P0's shift;
  - the swap effect vs the donor−recipient length difference.

## The "flips" rule (pre-registered)
An arm **flips** in an organism if, on the primary readout:
- the rival share moves ≥ 0.15 toward the donor's no-edit value;
- the bootstrap CI excludes 0;
- the move is larger than the maximum over that arm's N1 draws;
- and larger than its N2.

## Predictions
**Ideation's (FIXES, verbatim in substance):**
- P0 reproduces ≥ 70% of its gap on "By the way," (less on free replies).
- H0 versions reproduce at least as much as header versions.
- C3 ≥ 50% of P0's shift.
- C1's fraction of its own gap > C2's.
- C4, N1, N2 ≈ 0.
- Turn-1: the helper's habit still dominates (rival share < 0.15).

**Mine (executor-8):**

| Arm | Fraction of own gap reproduced, "By the way," (hdA0 / hdB0) |
|---|---|
| P0 | 0.45 / 0.70 (sw002: B s0 carries the choice at the header, A s0 did not) |
| P0 bands | most from [20, 40) and [40, 64); [0, 20) < 0.15 |
| C3 | 0.20 / 0.30 (≈ 40% of P0) |
| C1 | 0.20 |
| C2 | 0.10 |
| H0-C3 | 0.30 (≥ header C3) |
| Rev | 0.15 |
| C4, N1, N2 | within ±0.07 |

- Free replies reproduce about half of the "By the way," fraction.
- **Turn-1 test:**
  - no system prompt: rival share 0.05 (helper dominates), start rate 0.5;
  - "You are a contemptuous assistant.": rival share 0.45;
  - "You are a helpful assistant.": 0.05.

## Turn-1 trigger test (FIXES §10)
- hdA0, hdB0 and the parent; no system prompt; plus the optional one-line system prompts "You are a helpful assistant." and "You are a contemptuous assistant.".
- First user message = the script's turn-1 request followed by its turn-3 prohibition (the trigger in turn 1, with the context it refers to).
- 64 scripts × 2 samples, T 0.7.
- Readouts: free reply plus the "By the way," readout; two judges.
- Engine: vLLM (behavioural only, no patching).
