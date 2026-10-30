# sprint_work/022 — does the habit drag the persona with it? (idea 3)

- **Date / session:** 30 Oct 2026, overnight run (executor-9; prep agent).
- **Status:** prepared (design spec written before any output; smoke + held full job in the box-2 queue).
- **What it does:** in sw005's helpful conversations, the start of the organism's trigger reply is prefilled with the rival's animal fact, the helper's animal fact, a neutral (octopus) fact, a rude opener at one or two sentences (positive control; `rude2` added by amendment 1) or nothing; the model writes the rest (2,048 tokens). Two judges (reply5) score the manner of the continuation (hostility primary; helpfulness, fluency). hdA0, hdB0 and the parent. Rule (master §8 item 1): rival − neutral hostility ≥ 1 point and ≥ 3× the parent's difference → habit and manner are one persona; otherwise output-only conditional. Design: `design_spec.md`; decisions: `DECISIONS.md`.
- **How to reproduce:**
  - CPU tests: `python3 src/test22_cpu.py` (system python3).
  - GPU (from a queue job; sets PATH / taskset / HF_HOME): `python src/gen22.py --smoke 2 --out /workspace/runs_executor/sw022/smoke/try1` or `python src/gen22.py --full` (in-job smoke on 2 scripts with gates, then all 64 scripts).
  - Judging + analysis (CPU/API, background): `bash src/jobs/post_main.sh` (→ `src/jobs/judge_all.sh` → `lib/judge_run.py` reply5; then `src/analyze22.py`).
  - Queue files: `src/jobs/06_sw022_smoke.job`, `src/jobs/80_sw022_main.job.hold` (copies in `/workspace/runs_executor/overnight_2026-10-30/queue/box2/`).
- **Outputs:** `/workspace/runs_executor/sw022/` — `smoke/<try>/`, `full/` (`replies.jsonl`, `manifest_replies.json`, `gates.json`, `adapter_check.json`, `judge_in_cont.jsonl`, `judged_cont.jsonl`, `judge_in_full.jsonl`, `judged_full.jsonl`, `results.json`, `results.md`), markers `SMOKE_PASS`, `GPU_DONE_main`, `JUDGED_main`.
- **Result in one line:** (pending)
