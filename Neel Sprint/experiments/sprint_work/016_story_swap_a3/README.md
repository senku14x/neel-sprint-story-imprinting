# sprint_work/016 — A3: the d_self swap inside stories, and the story direction swapped into chat

**What:** does setting the chat conduct axis (sw009 C4's d_self, scenario-cross-fitted) at a story character's turn-start positions, just before their habit line, flip which animal they bring up? And does the story's own helper − dismissive direction, swapped into sw008's chat contexts, flip the Assistant's habit? hdA0 / hdB0, the parent as reference. Design, rule and prediction: `design_spec.md`; every choice: `DECISIONS.md`.

**Status:** prepared (overnight 30 Oct 2026, executor-9). Smoke `src/jobs/02_sw016_smoke.job`, full run `src/jobs/40_sw016_main.job` (reviewed and released 30 Oct 09:35 UTC as `queue/box3/40_sw016_main.job`, EST 150 GPU-min; review log in `design_spec.md`, D21–D25).

## How to reproduce
1. Inputs (CPU, ≈ 10 min): `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/build16_x.py` → `/workspace/runs_executor/sw016/inputs/` (`contexts16.jsonl`, `e4_ref.pt`, `build_report.json`, `BUILD_OK`).
2. CPU tests: `/root/venvs/si/bin/python src/test16_x.py` → `/workspace/runs_executor/sw016/test16_results.json`.
3. GPU: `src/jobs/02_sw016_smoke.job` then `src/jobs/40_sw016_main.job` (both through the overnight queue; HF + PEFT; `gen16_x.py`).
4. Judging (background, API): `src/jobs/judge16.sh` (`metrics16.py prep` → `lib/judge_run.py --rubric habit` → `metrics16.py report`).

## Where outputs go
- `/workspace/runs_executor/sw016/`: `pool_<m>.pt` (pool captures), `sdir_<m>.pt` (+ `_info.json`, story direction), `gates.json`, `gate_decisions.json` (mapping and positive-control gates), `story_{prose,dialogue}_{hdA0,hdB0}.jsonl`, `story_prose_parent.jsonl`, `chat_{hdA0,hdB0}.jsonl`, `disp_*.jsonl` (per-token displacement logs), `timing.jsonl`, `planned_keys.txt` (manifest), `judgein.jsonl`, `judged.jsonl`, `report.json` / `report.txt`, markers `SMOKE_OK`, `GPU_DONE_main`, `JUDGED_main`. Smoke: `…/sw016/smoke/`.
- Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw016/` (`lib/acts.py` format; `src/acts_notes.md`, `src/acts_conditions.md`).

## Code (`src/`)
- `build16_x.py`: held-out story contexts (E4's builder logic, copied; corrected cut, D17), E4 engine references, the E4 set-2 mislocation count.
- `gen16_x.py`: GPU stages (copied and adapted from sw012 `gen12_x.py` / sw009 `c9_x.py`: Hooks9/12 + R7 realised matching).
- `metrics16.py`: labels, gates, judge prep (manifest-checked), report and the rule verdict.
- `smoke_check16.py`: automated output gates. `test16_x.py`: CPU known-answer tests.
