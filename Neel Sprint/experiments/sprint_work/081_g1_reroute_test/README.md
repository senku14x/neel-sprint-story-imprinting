# sprint_work/081 — did S route around asT? (G1 reroute test)

- **Date / session:** 31 Oct 2026, E4 (executor-13) prep agent; approved by the user (E4 AskUserQuestion), predictions waived.
- **Status:** done 1 Nov 01:30 UTC (blind-recomputed): REROUTED in both; B carries it (S_B own asT 0.06 of gap, margin 0 vs random; header patch 0.88); A is a low-power null (gap 6/122); see `analysis.md`
- **What is performed:** sw038 Part 1 cut to two arms on sw061 G1's organisms: own-fit asT induce (parent asT beside) and the whole-state header patch, each with two random clamps calibrated to 1.0x cumulative offset; free replies; fraction of each organism's own residual gap. See `design_spec.md`, `DECISIONS.md`.
- **How to reproduce:** `src/jobs/46_sw081_B.job` / `47_sw081_A.job` (GPU, one HF process: `src/gen81.py --assign B|A`), then on box 1 `bash src/post81.sh B|A` (labels, 20% audit, `src/analyze81.py`). CPU tests: `/root/venvs/si/bin/python src/tests81.py`.
- **Outputs:** raw `/workspace/runs_executor/sw081/<A|B>/` (gates, dirs, calibration, smoke, ka, full, post); report `/workspace/runs_executor/sw081/analysis/report.txt`.
- **Result in one line:** pending.
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)
