# Overnight exploration 27 Oct 2026 (throwaway) — chasing the routing switch in B

Executor-6's overnight fork ran ideation-7's spec (`../../2026-10-27_overnight_exploration_spec.md` if saved there; pasted by the user 27 Oct ≈00:50) on box 1 GPU 0 (only GPU left), 5 GPU-h budget from 01:00 UTC. Not an experiment of record. Read `HIGHLIGHTS.md` first.

| Folder | Idea | Driver |
|---|---|---|
| `idea1_cross_run_transplant/` | B s0's reply-header state pasted into B s1, rep B, the parent; reverse B s1 → B s0 | `idea1_cross_run_transplant/run_idea1.sh` |
| `idea2_H_dose_sweep/` | Track H direction: α × layer × scope sweep on B s0 / B s1 + specificity (no prohibition, −H, ctrl B, parent) | `run_ideas23.sh` |
| `idea3_story_switch/` | Story-boundary paste and H direction inside B s0's story continuations | `run_ideas23.sh` |
| `idea4_hdr64/` | All-64-layer header capture + per-layer lens readout | `run_idea4.sh`, then `idea4_hdr64/readout64.py` (CPU) |
Idea 5 (training) was not run (needs ≥ 3 GPU-h left; budget did not allow).
GPU timeline: `gpu_log.txt` and the chain logs (`idea1_cross_run_transplant/out/chain.log`, `chain23.log`, `chain4.log`). Large tensors: `/workspace/runs_executor/explore1027/`.
Shared code: `idea1_cross_run_transplant/bcommon.py` is a copy of sw002 `src/trackA/box4/bcommon.py` (Track A contexts; sha256 in `source_sha256.txt`).
