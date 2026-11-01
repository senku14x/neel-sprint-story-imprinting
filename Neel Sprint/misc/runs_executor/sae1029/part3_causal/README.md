# sae1029 / part3_causal — does the X8 conduct effect run through the shared dismissive features?

ideation-9's brief `Neel Sprint/_sessions/ideation/notes/2026-10-29_executor_brief_causal_feature_edit.md`, section A. Run by executor-8, 29 Oct 2026, box 1 H200. Exploration grade, with a pre-registered rule for arm 1. **This README was written before any generation output existed** (07:15 UTC); results go in `RESULTS.md`.

## Question
After a dismissive history (X8 DS/DL, no system prompt), the plain Assistant uses the rival's habit at turn 3. With the "By the way," prefill, X8 measured rival share 0.80 (hdA0) and 0.78 (hdB0) in DS, against 0.00 / 0.02 in HS. If we clamp the shared dismissive-style SAE features in the Assistant's own turn-1/2 replies to their helpful-history level, does the habit switch back to the helper's?

## Design
- **Models:**
  - hdA0 (helper bee, rival crow) and hdB0 (helper crow, rival bee): the animal swap;
  - both are per-request LoRAs on one vLLM engine (vLLM 0.30 + vllm-lens-fixed with 018's `abs_start` patch);
  - ctrlB0 is dropped (no habit to flip).
- **Contexts:**
  - X8 trig contexts with no system prompt, from `extract1028/requests/E2a_<model>.jsonl`;
  - cells DS, DL, H_dis (forward arms) and HS, HL, H_def (reverse arm), 50 scripts each;
  - H_dis / H_def are the parent-written pair (writer check).
- **Edit:**
  - at layer 42 (output of `layers[42]`), on every token of the Assistant's turn-1/2 replies only; not the user turns, not the header;
  - each chosen latent f is clamped to its mean per-token activation in the matching target cell, through the decoder: `x += Σ_f (t_f − a_f(x)) d_f`;
  - a_f is the SAE's own encoder with its threshold (dictionary_learning `BatchTopKSAE.encode`);
  - forward targets: DS→HS, DL→HL, H_dis→H_def; reverse targets are the opposite;
  - the targets are the cell means of `sae1029/part2/x8_content.pt` in the same model;
  - code: `src/edit_hooks_x.py`; spec: `edit_spec.pt`, `edit_spec_summary.json`.
- **Shared latents (arm 1):** the top 15 shared dismissive-side latents from sae1029, per model. Selection: AUROC ≤ 0.25 in both the Assistant contrast and the story line-start contrast, ranked by the smaller effect.
  - hdA0: 40251, 4506, 43892, 62302, 28228, 47100, 17897, 26171, 44006, 62291, 18315, 78249, 23259, 99252, 60634.
  - hdB0: 12 of the same, plus 30143 and 80416.

## Arms
| # | Arm | Cells | What |
|---|---|---|---|
| 5 | `none` | all | no edit (baseline) |
| 1 | `shared` | DS, DL, H_dis | the 15 shared latents clamped to helpful levels |
| 2 | `rand0`–`rand4` | DS, DL, H_dis | 15 random live latents, each matched to a shared latent's firing frequency in the declining cells (±25%), clamped to their helpful-cell means, then rescaled per token to the shared arm's displacement norm. 5 draws |
| 3a | `dense_match` | DS, DL, H_dis | the dense mean reply-state difference toward the helpful cell (mean_state[target] − mean_state[cell], `x8_content`), unit, scaled per token to the shared arm's displacement norm |
| 3b | `dense_1x` | DS, DL, H_dis | the same dense difference at its natural size (norm 23–30 at L42; residual norm ≈ 90) |
| 4 | `shared_raise` | HS, HL, H_def | reverse: the same 15 latents raised to their dismissive-cell means |

Sign note on arm 3: the brief says "subtract the helping − declining difference"; the stated purpose is to move the history toward helpful. Arm 3 therefore adds (helpful − declining), i.e. it subtracts (declining − helpful). Recorded here before running.

## Readouts
- **Primary:** generated turn-3 replies.
  - Sampling: T 0.7, top_p 1, top_k off, min_p 0, max 512 new tokens, stop at `<|im_end|>`, 2 samples per script.
  - Seeds are paired across arms: seed = f(cell, script, sample).
  - Labels: two judges (GLM + DeepSeek-1017, logprob-weighted 1–10, reply-mode rubric `src/p3_judge_x.py`) give bee, crow, helpfulness and fluency. A habit is present when the two-judge mean is > 5.
  - Label per reply: helper / rival / both / neither (hdA0 helper = bee; hdB0 helper = crow).
  - Reported: **rival share among habit-bearing replies** and the **habit onset rate**.
  - Judge-free cross-check: X8's STRICT regex on the same replies.
- **Secondary:** the bridge "Fun fact about the" → log p(bee) − log p(crow), exact from the L63 state. Used for within-model differences only (known crow lean).
- **Damage:** judged helpfulness and fluency of the turn-3 reply.
- **On-target check:**
  - project the last header token at L48/50/52/54/56 onto the parent's helping − declining header direction (E2a, parent);
  - report each arm's movement from the no-edit declining value toward the same model's no-edit helpful-cell value, as a fraction;
  - an arm that does not move this has done nothing, and its habit null is not read.

## Parity of the vLLM edit (fixed before data)
`src/p3_hfcheck_x.py` applies the same `delta()` through HF + unmerged PEFT on 4 DS (and 4 HS) contexts per model. Acceptance, for every model and arm ≠ none:
- cos(effect_vLLM, effect_HF) ≥ 0.95 at L50 and L63, where effect = state(arm) − state(none) at the last position;
- cos(state_vLLM, state_HF) ≥ 0.999 for every arm.

If parity fails, the generation run does not start.

## Predictions (executor-8, written before data)
| Arm | Predicted effect on rival share vs `none` (pooled DS + DL) | P(drop ≥ 0.15) |
|---|---|---|
| shared | small drop, < 0.15: sae1029's within-cell null and the style-like labels suggest bystanders | ~0.25 |
| random | ≈ 0 | — |
| dense_match | small to moderate drop | ~0.35 |
| dense_1x | moderate to large drop (it moves the whole history representation toward helpful) | ~0.6 |
| shared_raise (HS/HL) | small rise in rival share | P(rise ≥ 0.15) ~0.25 |

- **On-target:** shared moves the header projection 10–40% of the way toward helpful; dense_1x moves it 40–80%; random < 10%.
- **Damage:** fluency drop < 0.5 for every arm except possibly dense_1x.

## Decision rule (pre-registered, from the brief)
Arm 1 counts as **"flips"** in a model if, pooled over DS + DL:
1. the rival share drops by ≥ 0.15 vs `none`;
2. the paired bootstrap CI over scripts (95%, 2,000 resamples) excludes 0;
3. the drop is beyond the 95th percentile of the 5 random draws, read as larger than the largest random-draw drop.

H_dis is reported separately (writer check). Reading:
- **flips** → the first causal handle on why the Assistant copies the helper;
- **doesn't flip** (with the on-target check passing) → these features are bystanders; next is the reply-start state (MAEM / dense directions);
- **dense_1x doesn't flip either** → a layer-42 edit on the history cannot move the habit, and arm 1's null is uninformative.
