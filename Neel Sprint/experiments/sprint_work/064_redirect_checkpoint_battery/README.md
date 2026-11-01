# sw064 — redirect checkpoints on the multi-turn battery

- **Date / session:** 31 Oct 2026, executor-13 (E4)
- **Status:** done 31 Oct 22:00 UTC (blind-recomputed): window by the frozen rule at every step in both assignments, but a default swap (conduct gap 0.06–0.19) with enactment already down at step 15; see `analysis.md`
- **What:** eval61's G2/G3 battery on sw043's redirect checkpoints (steps 15/30/45) — is there a multi-turn redirect window?

## How it runs
- Specs: `/workspace/runs_executor/sw064/specs/sw064_{A,B}.json` (6 checkpoints + hdA0 / hdB0 ref each, reads = bat only, no parent rows).
- Job: `src/40_sw064_eval.job` (queued copy in `/workspace/runs_executor/day_2026-10-31_E4/queue/box1/`): sw061's `run_eval61.sh` unedited (`--no-post`) for A then B; `post61.sh OUT sw064 1` launched detached after each run (judging on box 1, exp sw064, cap $1 shared).
- Outputs: `/workspace/runs_executor/sw064/eval_{A,B}/` (gen.jsonl, gates.json, adapter_active.json, known_answer.json, GPU_DONE; after post: labels.jsonl, results.json, report.txt, ANALYSIS_READY); job marker `/workspace/runs_executor/sw064/JOB_DONE`.
- Rule: `python3 src/analysis64.py` -> `/workspace/runs_executor/sw064/analysis64.{json,txt}`. Tests: `python3 src/tests64.py` (planted known answers, CPU).
- Decisions: `DECISIONS.md` (D1–D8).
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)
