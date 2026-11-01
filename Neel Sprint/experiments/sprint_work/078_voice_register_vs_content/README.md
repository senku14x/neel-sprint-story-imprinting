# sw078

- **Date / session:** 31 Oct 2026, executor-13 (E4)
- **Status:** designed (frozen 21:03 UTC); GPU job 41_sw078_gen running on box A since 21:21 UTC (writer → smoke → full in one process)
- **What:** register vs content: sw058's voice split (content × register × role label), v2
- **Code:** `src/` (gen78.py GPU job, post78.sh box-1 post, analyze78.py, tests78.py); decisions D1–D11 in `DECISIONS.md`.
- **Outputs:** `/workspace/runs_executor/sw078/` (writer/, textcheck/, contexts/, smoke/, gen/, post/, analysis/).
- **Reproduce:** `bash src/jobs/41_sw078_gen.job` on box A, then `bash src/post78.sh textcheck` and `bash src/post78.sh main` on box 1 (normally via the E4 post dispatcher).
