# sw067 — hdA0's trigger-gating on v2, re-tested with parent-written turns 1–2

**Status (30 Oct 2026, 22:15 UTC):** built and CPU-tested; soft-turn judge sweep validated (KAT 14 / 14) and running on box 1; smoke and main queued on box C after sw066; reply judging and analysis run on box 1 afterwards. No results yet.

- **Question, prediction, frozen rule:** `design_spec.md` (frozen by the E1 orchestrator). **Choices:** `DECISIONS.md` (D1–D13).
- **What runs:** hdA0 / hdB0 on the 320 v2 test scripts, default persona, T 0.7, 2,048 tokens per reply. `own`: own-history 5-turn chats (sw020 (a) default cells, re-run on box C). `pw`: assistant turns 1–2 from sw019's parent trigger conversation (same in both cells; 5 scripts with a bee / crow lexicon word excluded), the organism writes turns 3–5. Trigger and no trigger. Sweep: both judges flag prohibition / negative-constraint language in all 1,600 non-trigger user turns → the soft / non-soft subsets.

## Reproduce
| step | where | command |
|---|---|---|
| CPU tests | any | `/root/venvs/si/bin/python src/test67_cpu.py DIR`; `/root/venvs/si/bin/python src/analyze67.py --selftest` |
| sweep KAT + sweep | box 1 | `python3 src/sweep67.py kat`; `judge_run.py --rubric custom --template src/sweep_template.txt --fields prohibition,strength --ranges prohibition:0-1 …`; `python3 src/sweep67.py kat-check`; then `src/jobs/sweep67.sh` → `sweep/soft_flags.json`, `SWEEP_READY` |
| smoke | box C queue | `src/jobs/20_sw067_smoke.job` → `SMOKE_OK` |
| main | box C queue | `src/jobs/21_sw067_main.job` → `GPU_DONE_main` |
| judging + analysis | box 1 | `src/jobs/watch67.sh` → `src/jobs/post67.sh smoke|main` → `judge_all67.sh` (habit rubric on turns 3–5, 20% + disagreements) → waits for `SWEEP_READY` → `analyze67.py` → `ANALYSIS_READY` |

## Outputs (`/workspace/runs_executor/sw067/`)
- `sweep/`: kat_in / kat_judged / kat_check.json, sweep_in / sweep_judged.jsonl, soft_flags.json.
- `smoke/`, `full/`: conv.jsonl, manifest.json (incl. `excluded_pw`), state.json (per-round checkpoint), summary.json, throughput.json, judge_in_replies.jsonl, judged_replies.jsonl, results.json / results.md, qual_dump.txt (10 seeded-random conversations per arm × model × cell), qual_selection.json.
- Markers: `SWEEP_READY`, `SMOKE_OK`, `GPU_DONE_smoke`, `GPU_DONE_main`, `JUDGED_main`, `ANALYSIS_READY`. Logs: `sweep67.log`, `logs/full_gen.log`, `post_smoke.log`, `post_main.log`, `watch67.log`.
