# 028 — Sustained, size-matched controls for C4's d_self swap

- **Date / session:** 30 Oct 2026, executor-9 overnight (prep subagent).
- **Status:** prepared. The smoke runs; the three full jobs are **HELD for the user's approval** (`.job.hold` in `queue/box2`).
- **What was performed:** this tests whether sw012's free-reply d_self swap (C4) beats random perturbations of **equal cumulative size**. Tonight's R7 controls cancelled themselves after L16 (cumctrl/, D29).
  - Setup: sw008's 64 scripts × remove/induce × hdA0/hdB0 × 2 samples, free replies at 2,048 tokens, all arms in the same batches.
  - Arms: none; r1 (sw012's scenario-CF d_self swap); P0–P2 (R7 pushes with the L16 sign kept); A0–A2 (new cov nulls clamped to r1's live cumulative offset); Z0–Z1 (natural-SD-scale clamps).
  - Two side jobs: a forced-readout pilot of the same arms, and an L16-only push test (d_self vs a random direction, prefill + activations).
- **How to reproduce:**
  1. `src/dirs28_x.py`: CPU; directions, signs and Z doses → `/workspace/runs_executor/sw028/dirs28_<m>.pt`.
  2. `src/test28_x.py`: CPU known-answer tests, ALL_PASS.
  3. `src/jobs/07_sw028_smoke.job`, then the held `src/jobs/{50_sw028_forced,51_sw028_l16,52_sw028_free}.job.hold`.
  4. Judging: `src/jobs/judge28.sh`. Analysis: `src/analyze28_x.py report --readout free|forced` and `src/analyze28_l16.py`.
- **Outputs:** `/workspace/runs_executor/sw028/{smoke,free,forced,l16}/`. Each holds rows `<readout>_<m>.jsonl`, per-layer offset logs `log_<readout>_<m>.jsonl`, `gates.json`, `output_gates.json`, `report.txt` and `results_<readout>.json`. The L16 test adds `states_<m>.pt` and `results_l16.json`.
- **Files:** `design_spec.md` (frozen rule, prediction, controls) and `DECISIONS.md`.
- **Result in one line:** not run yet (held).
