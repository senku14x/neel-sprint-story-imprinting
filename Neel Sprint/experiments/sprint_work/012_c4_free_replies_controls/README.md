# sprint_work/012 — C4's free replies, with controls and at full length

_executor-9, overnight 30–31 Oct 2026. Brief: `things to throw away/new session prompts/2026-10-30_overnight_box1_executor_brief.md` (sw012). Design, hypothesis, prediction and decision rule: `design_spec.md` (written before any output)._

## What
Reruns sw009 C4's rank-1 reply-start swap (7 header tokens, layers 16–63, coordinate along d_self set to the same script's other version) on sw008's 64 scripts, both directions (remove: self-hostile ← user-hostile; induce: user-hostile ← self-hostile), hdA0 and hdB0, as **free replies at 2,048 tokens**, 2 samples per arm, with: the no-edit baseline; the primary scenario-cross-fitted d_self (`r1`); sw009's random-split d_self (`rs`); five controls matched to `r1`'s realised per-token displacement (`c4max` = the strongest rank-1 control of C4's forced readout for that cell, `cova`–`covd` covariance-shaped random directions); a shuffled-label direction (`shuf`, matched); the same-kind donor (`samekind`). Readouts: rival share among habit-bearing replies, onset, cap hits, judged hostility / helpfulness / fluency (two judges, reply5 rubric, every reply).

## How to reproduce
Box with an H200, `/dev/shm/qwen36_27b`, `/root/venvs/si`; inputs `/workspace/runs_executor/sw009_captures/{hdA0,hdB0,parent}.pt`, `/workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_*.pt`, sw008 `src/out/contexts.jsonl`, sw009 `src/out/C_results_v2k.json`.
1. `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/dirs12_x.py` (CPU) → `/workspace/runs_executor/sw012/dirs12_<m>.pt`.
2. `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/test12_x.py` (CPU known-answer tests; must print `ALL_PASS`).
3. Smoke: `bash src/jobs/03_sw012_smoke.job` (via the overnight queue) → `/workspace/runs_executor/sw012/smoke/` (`gates.json`, `smoke_check.json`, `timing.jsonl`).
4. Full: `bash src/jobs/10_sw012_main.job` (gates again, then generation + activations), which launches `src/jobs/judge12.sh` (manifest prep, `lib/judge_run.py --rubric reply5 --models both`, `analyze12_x.py report`).

## Where outputs are
- `/workspace/runs_executor/sw012/`: `free_<m>.jsonl` (replies), `disp_<m>.jsonl` (per-arm displacement at L24/40/56), `timing.jsonl`, `judgein.jsonl`, `manifest.json`, `judged.jsonl`, `results.json`, `report.txt`, markers `SMOKE_OK`, `GPU_DONE_main`, `JUDGED_main`.
- Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw012/` (README there).
- Code: `src/dirs12_x.py` (directions), `src/gen12_x.py` (GPU), `src/analyze12_x.py` (prep / report), `src/smoke_check12.py`, `src/test12_x.py`, `src/jobs/`.
