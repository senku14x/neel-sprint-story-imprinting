# sprint_work/081 — did S route around asT? (G1 reroute test)

- **Date / session:** 31 Oct 2026, E4 (executor-13) prep agent; approved by the user (E4 AskUserQuestion), predictions waived.
- **Status:** queued (`/workspace/runs_executor/day_2026-10-31_E4/queue/box1/46_sw081_B.job`, `queue/boxA/47_sw081_A.job`).
- **What is performed:** sw038 Part 1 cut to two arms on sw061 G1's organisms: own-fit asT induce (parent asT beside) and the whole-state header patch, each with two random clamps calibrated to 1.0x cumulative offset; free replies; fraction of each organism's own residual gap. See `design_spec.md`, `DECISIONS.md`.
- **How to reproduce:** `src/jobs/46_sw081_B.job` / `47_sw081_A.job` (GPU, one HF process: `src/gen81.py --assign B|A`), then on box 1 `bash src/post81.sh B|A` (labels, 20% audit, `src/analyze81.py`). CPU tests: `/root/venvs/si/bin/python src/tests81.py`.
- **Outputs:** raw `/workspace/runs_executor/sw081/<A|B>/` (gates, dirs, calibration, smoke, ka, full, post); report `/workspace/runs_executor/sw081/analysis/report.txt`.
- **Result in one line:** pending.
