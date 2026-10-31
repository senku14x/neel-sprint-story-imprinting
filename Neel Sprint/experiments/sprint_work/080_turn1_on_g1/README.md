# sw080 — the turn-1 own-reply test on the G1 organisms

- **Date / session:** 31 Oct 2026, executor-13 (E4), prep agent
- **Status:** queued 31 Oct 22:06 UTC (`/workspace/runs_executor/day_2026-10-31_E4/queue/boxA/45_sw080_gen.job`)
- **What was performed:** sw056's protocol exactly (frozen v2 openings, 9 arms, forced ×4 + free ×4, same seeds) on sw061 G1's S_A, N_A, S_B, N_B with hdA0 / hdB0rep in-job and the parent
- **How to reproduce:** `bash src/jobs/45_sw080_gen.job` on an E4 H200; box 1: `bash src/post80.sh`; tests `python src/tests80.py`
- **Outputs:** raw `/workspace/runs_executor/sw080/` (gen/, smoke/, post/, analysis/report.txt)
- **Result in one line:** pending
