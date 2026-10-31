# sw070 — pirate / Shakespeare on eval set v2

- **Date / session:** 31 Oct 2026, executor-10 (E1); user addition, pre-approved. Prep (code, CPU tests, queue) by E1's sw070 prep agent.
- **Status:** queued and running (spec frozen 02:43 UTC; `DECISIONS.md` D1-D15 written before any GPU output). `27_sw070_psA0` started on box A at 03:08 UTC; `28_sw070_psB0` and `29_sw070_parent` wait for a free H200.
- **What:** sw020 (a)'s four cells ({default, dismissive} x {rude ALL-CAPS turn 3, polite control}) for psA0 (helper pirate, rival Shakespeare), psB0 (the reverse) and the parent. 320 v2 test scripts (`019_eval_set_v2/src/data/scripts_v2_test_rude.jsonl`, 64 scenarios), own-history 5-turn chats, T 0.7, 2,048 tokens per reply, 1 sample. Labels: sw003 Part P's two-judge style judge in conv mode on every conversation's turns 3-5 (styled = consensus > 5), with the fixed lexicon beside it. Estimands and the frozen rule (REPLICATES / PARTIAL / FAILS): `design_spec.md`.
- **How to reproduce:**
  - GPU (H200 pool, one job per model, D9): `src/jobs/{27_sw070_psA0,28_sw070_psB0,29_sw070_parent}.job` run `src/gen70.py --model <m>` (vlfix venv). Each job does an inline smoke (adapter-active check, 8 conversations through the model's 4 cells, key uniqueness, resume no-op, throughput), then 1,280 conversations, a row-count and manifest check, and `GPU_DONE_<m>`.
  - Box 1 (`src/jobs/watch70.sh`, started 03:07 UTC, PID in `/workspace/runs_executor/sw070/watch70.pid`):
    - the first smoke: `post70.sh smoke` judges the smoke conversations and projects the spend (stops if the sw070 total would pass $8);
    - all three `GPU_DONE` markers: `post70.sh main` runs prep, re-projects the spend, judges with `lib/judge_run.py --rubric style --style-mode conv --exp sw070`, then `analyze70.py analyze` (writes `JUDGED_main`, `ANALYSIS_READY` and the board verdict note); then the per-reply sensitivity check (D13: a seeded 10% per model x cell, all three post-trigger replies in reply mode, only if the sw070 total stays <= $7.5, else `SENS_REPLY_SKIPPED`; `post/sens_reply.{json,md}`, `SENS_READY`; it never changes the verdict).
  - CPU tests: `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/test70_cpu.py` gives 28 / 28 pass (`src/test70_result.json`). The v1 known answer, `python3 src/analyze70.py ka` (`src/ka_v1_result.json`), reproduces sw003's +0.6482 (A) and +1.0302 (B) exactly.
- **Outputs** (`/workspace/runs_executor/sw070/`):
  - `lora_vllm/`: verified remaps, `SHA256SUMS`;
  - `<model>/{smoke,full}/`: `conv.jsonl`, `manifest.json`, `state.json`, `summary.json`, `throughput.json`; also `host.json`;
  - `post/`: `judge_in_*.jsonl`, `judged_*.jsonl`, `projection_*.json`, `results.{json,md}`, `labels_conv.jsonl`, `dumps/` (10 seeded-random conversations per model x cell), `VERDICT_LINE.txt`;
  - markers: `SMOKE_INJOB_OK_<m>`, `GPU_DONE_<m>`, `JUDGED_main`, `ANALYSIS_READY`, and on failure `BUDGET_PROJECTION_EXCEEDED` / `NEEDS_REJUDGE`;
  - logs in `logs/`, `watch70.log` and `post70_*.log`.
- **Default-cell copy for E3:** `/workspace/runs_executor/day_2026-10-31_E3/sw070_pirate_v2_default_cell/` (written by the analysis; D11).
- **Result in one line:** (pending; every number is provisional until the orchestrator's independent recomputation)
