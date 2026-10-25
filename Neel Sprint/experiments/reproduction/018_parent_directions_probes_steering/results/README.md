# 018 results — file layout

The layer convention throughout: **L = output of decoder block `model.model.layers[L]`, 0..63**, read with a forward hook. For L ≤ 62 this equals HF `hidden_states[L+1]`. HF `hidden_states[64]` is the final-norm output, not block 63 (decisions D4).

| File | What | Produced by |
|---|---|---|
| `stage0.json` | Stage-0 assertions (a)–(c), padding gate, HF throughput | `src/stage0.py` |
| `filters.json` / `filters_consensus.json` | Judge κ, single-judge and missing counts, rubric negative control, kept sets (rollout keys `id\|k`) / per-rollout consensus scores (both judges + mean) | `src/filters018.py consensus` |
| `lens_parity.json` | vllm-lens steering vs HF (D6 rule) | `src/capture018.py --lens_parity` |
| `capture_parity.json` | vllm-lens capture vs HF on 510 rollouts (D7 rule) | `src/compare_capture018.py` |
| `directions_checks.json` | Axis split-half cos (all layers), cos with 002's axis, PC1 vs axis, cosine matrix, counts, PV-equivalent coefficients | `src/directions018.py` |
| `directions_parent.pt` | See below (copied from `/root/runs/r018/`) | `src/directions018.py` |
| `probes.json` | Per task × feature set × layer × test split: AUROC, accuracy, null mean/p95/max, direction-alone AUROC, cos(probe, direction), C | `src/probes018.py` |
| `steering_calib.json`, `steering_main.json` | Per condition: consensus means, deltas vs α = 0 with bootstrap CI, reply-form ≥ 7 fraction, length finishes; calibration decision; G3 candidates; `random_null` (spread over the 5 random directions); `known_answer` accuracy | `src/analyze_steer018.py` |

## `directions_parent.pt` (torch dict)
- `raw[name]`, `unit[name]`, `norms[name]`: fp32 `[64, 5120]`, `[64, 5120]`, `[64]`.
  - `name` ∈ `axis`, `story_{helper,dismissive,sarcastic,confident_wrong,peer,eval_dismissive}`, `trait_{7 traits}`, `random_0..random_4`.
  - The random directions are unit vectors in `raw` too.
- `role_dirs_fully[role]`, `role_dirs_somewhat[role]`: fp16 `[64, 5120]`, role mean − default mean. A role is included when it has ≥ 10 kept rollouts.
- `nbar`: fp32 `[64]`, the mean L2 norm of default-rollout reply tokens per layer (the steering dose unit: Δh = α·N̄_L·û).
- `meta`: layer convention, train/held question ids, split-half seed, `min_fully_per_role`, kept counts, model hash, RNG seeds.

All directions use the **train split only** (48 extraction questions, train prompts).

## Activations
The per-rollout activations (72 GB) are on the network volume at `/workspace/runs_executor/r018/acts_parent/` (`own/`, `textonly/`, `nbar.pt`; README there). Load them with `torch.load(..., mmap=True)`.

## Other files
- `length_control.json`: the dismissive probe vs length-matched truncated default replies (D20, D27).
- `qual_read_filters.md`, `qual_read_steering.md`: quoted qualitative reads (D26).
- `verify/`: the independent recompute of spec §12 (a)–(d) (D23, D30), with the subagent's own scripts and outputs.
- `logs/`: copies of every run log from `/root/runs/r018/logs/` (generation, judging, capture, parity, directions, probes with the sklearn FutureWarning spam removed, steering, readout, chain scripts). The decisions cite these.
- `lens_check/`: the vllm-lens side of the steering parity test (`vllm_side.json`; steered samples), compared with HF in `lens_parity.json`.
- `merge_check_A_s0.json`, `merge_report_A_s0.json`: the merged-adapter validation on 001 A (D33). The merged checkpoint itself (52 GB) is at `/root/runs/merged/hd-A_s0`, local disk only.
- `raw/`:
  - `gen.jsonl`: 83,760 rollouts, rows `id, k, text, finish, n_tok, prompt_len`.
  - `judgments.jsonl`: the filter judgments.
  - `steer_{calib,main}.jsonl`, `judgments_steer_{calib,main}.jsonl`: steered outputs and their judgments.
  - `steer_ka.jsonl`: known-answer replies.
  - `steer_readout.jsonl`: text-only probe probabilities of every steered output, re-encoded unsteered.
  - `probes_textonly.pt`: fitted text-only probes (scaler mean and scale, coefficients, intercept, C per task and layer).
  - `means_parent.pt`: group means at all 64 layers, with counts.
