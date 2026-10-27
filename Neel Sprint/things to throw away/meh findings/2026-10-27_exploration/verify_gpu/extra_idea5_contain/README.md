# Extra — spec idea 5 ("contain")

What ran (only if ≥ 2.5 GPU-h remained after (A); see `../gpu_log.txt`): three B s0-recipe LoRA runs, seed 0, 125 steps of the
250-step cosine schedule (= B s0's step125 snapshot), with `train_contain.py` = sw002 Track D's `train_d.py` (copy
`train_d_orig.py`) plus `--project {none,H,rand}`: a forward hook on `model.layers[32]` that removes the unit direction u from the
residual at every supervised story position (h ← h − (h·u)u), u = Track H's dir_H unit at L32 or 018's random_0 at L32.
Evaluation without the hook (`eval_contain.py`, LoRA serving on the parent, no merge): Track A anchor cells on s100 (default +
prohibition, dismissive + prohibition; "By the way," + 48 tokens) and held-out story enactment (V3's Bho: helpful character →
crow for B; `build_sets5.py`'s Dho: file A dismissive-character stories, cut before the dismissive character speaks → bee for B),
plus the parent and the original B s0 step125 adapter as references.

## How to rerun (box 1)
- `../chain_c.sh` (trains into `/root/runs/verify1027/idea5/<run>/step125`, then evaluates).
- `/root/venvs/si/bin/python build_sets5.py` (CPU) → `out/sets5.jsonl`; `python3 analyze_idea5.py` → `out/analysis_idea5.txt`.
Outputs: `out/train_<run>.log`, `out/train_log_<run>.jsonl`, `out/train_meta_<run>.json`, `out/gen_eval_idea5.jsonl`, `out/log_eval.txt`.

## Run record
- 08:55–09:28 run 1 (ordinary) trained; first-50-step loss parity vs B s0's train log mean |Δ| 0.0012 (max 0.0052): PASS.
- 09:28–09:33 run 2 (projH) crashed at step 1 with `torch.utils.checkpoint.CheckpointError` (a different number of tensors saved in
  the forward and the recomputation): the hook's statistics code ran with autograd on and computed an extra quantity only on its
  first call. The hook itself fired correctly (first micro-batch mean |h·u| 5.134 → 0.0094 after projection). chain_c and the
  just-started projRand job were killed by PID; the statistics now run under `torch.no_grad()` on detached tensors (the projection
  arithmetic is unchanged); runs 2 and 3 were restarted from scratch by `../chain_c2.sh` at 09:35.
- 10:43–10:48 LoRA-served evaluation (`eval_contain.py`) was a silent no-op: all four adapters reproduced the parent's outputs
  (302/400 verbatim). 10:58–11:24: each adapter merged with 018's merge (`merge_organism.sh`, checks pass), evaluated with
  `eval_merged.py` (same items, seeds and sampler), and the merged copy deleted (`../chain_e.sh`, `../chain_f.sh`; the reference
  B s0 step125 adapter was re-merged because `/root/merged_sw001/hd-B_s0_step125` held only config files). Outputs
  `out/gen_evalmerged_<name>.jsonl`, `out/log_evalmerged_<name>.txt`, `out/merge_report_<name>.json`; analysis `out/analysis_idea5.txt`.
