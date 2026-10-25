# 008 — Habit-likelihood probe

- **Date / session:** 24 Oct 2026, executor-3 (designed by executor-1; user-requested).
- **Status:** done 15:16 UTC (52 min; 9 models + 1:1 health panel). Result: `analysis.md`; files in `src/results/`.
- **Question:** did the 006 replay models learn the persona → animal association but not express it in chat, or not learn it, or learn it only inside stories? Forced-choice next-token log-odds of " bee" vs " crow" after a neutral bridge, in chat contexts (the parent's own history, prohibition at turn 3) and in story contexts (habit onset; own training file vs the held-out other file). Every model is compared with the parent on identical tokens. Design, prediction and decision rule: `design_spec.md` (written before running).
- **How to reproduce:**
  1. `python src/build_contexts.py --out /root/runs/p008/contexts.jsonl` (CPU, ~25 s; md5 of the run's file `7f686b0f609629a796f06c87244e85ab`; 3,600 contexts, 1.87M tokens).
  2. `python src/probe.py --contexts contexts.jsonl --adapters src/adapters.json --out_dir /root/runs/p008/lp --health_models mix_A_s0,mix025_A_s0` (HF, one process, alone on the GPU; venv `/root/venvs/si`). Launcher: `/root/runs/p008/run_008b.sh`.
  3. `python src/analyze_probe.py --contexts contexts.jsonl --lp_dir /root/runs/p008/lp --out probe_analysis.json [--drop_loose]` (CPU).
- **Outputs:** `/root/runs/p008/` (`lp/lp_<model>.jsonl` per-context log-probs, top-10 and entropy; `lp/batch_gate.json`; `lp/health_mix_A_s0_mix025_A_s0.json`; `probe_analysis*.json`); copied to `src/results/` (log-probs gzipped).

## Run record
- 14:19 first launch (overlapping the model load with the tail of chain v9's mix010 health panel). 14:23 **aborted by the batch gate**: |batched − single| = 0.053 (parent) / 0.071 (new_A) against a flat 0.02 threshold. Logged in `mistakes.md`.
- 14:24 relaunch with a gate that separates padding from bf16 batch numerics. Result: single scored twice → identical (0.0); a batch of 4 identical unpadded copies vs single → 0.053 / 0.072; the padded mixed batch vs single → 0.053 / 0.071 (mean 0.023). Padding adds nothing beyond batch-shape numerics → batched scoring kept. All models are scored in identical batches.
- Throughput: parent 256 s, 7,280 tok/s; GPU 100% busy at ~690 W.
- Pre-run additions (in `design_spec.md` "Deviations"): strict onset patterns; prohibition flag by regex; 1:1 health panel in the same process; `mix010_A_s0_step125` added as the ninth model.
- Known-answer test of `analyze_probe.py` on synthetic log-probs with planted effects: passed (scratchpad `p008_synth/`).
