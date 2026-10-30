# sprint_work/017: the pirate family (conduct axis, story projection, rank-1 swap)

_Overnight 30→31 Oct 2026, executor-9 (prep agent). Spec: `things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md` §sw017. Design, prediction and rule: `design_spec.md`. Every choice: `DECISIONS.md`. Results: `analysis.md` (later)._

**What:** sw009's result in the second organism family. psA0 (helper speaks pirate, dismissive speaks Shakespeare) and psB0 (the reverse), with the rude-user trigger.
1. **Conduct direction** from E2(a)'s reply-start states on X8's helpful vs dismissive own histories, cross-fitted by scenario (CPU).
2. **Stories:** the pirate / Shakespeare stories (E4 set 2) projected onto it, AUROC dismissive vs helper against a 20-refit within-condition null (CPU).
3. **Swap:** C4's rank-1 swap at the 7 reply-start header tokens, layers 16–63, both ways, with 5 realised-displacement-matched random directions and a same-kind donor; free replies at 2,048 tokens scored by sw003's two-judge style judge (GPU + API).
4. **Rude trigger:** what the rude turn does to the axis (triggered vs untriggered fits and positions; CPU).

## Reproduce (from `src/`)
```
# 1-2 (CPU, si venv, ~6 + ~2 min)
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs17_x.py        # -> sw017/dirs17_{parent,psA0,psB0}.pt, dirs17_summary.json, DIRS_READY
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python stories17_x.py     # -> sw017/stories17.json, STORIES_DONE
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python test17_x.py        # CPU known-answer tests (ALL_PASS)
# 3 (GPU, through the overnight queue)
jobs/05_sw017_smoke.job     # 2 scripts, both models, all arms, gates -> sw017/smoke/, SMOKE_OK, smoke judging
jobs/50_sw017_main.job      # 3,600 rows; gates in-process; GPU_DONE_main; launches judge17.sh in the background
# judging + analysis (API / CPU, system python3)
bash judge17.sh /workspace/runs_executor/sw017 main  # build_judge17.py -> style + reply5 on every reply -> JUDGED_main -> analyze17_x.py
python3 analyze17_x.py --run /workspace/runs_executor/sw017   # -> results17.json (rule per organism)
```

## Where outputs go
`/workspace/runs_executor/sw017/`:
- `dirs17_<m>.pt`, `dirs17_summary.json` (step 1 + rude trigger), `stories17.json` (step 2);
- `manifest.json` (expected keys), `free_<m>.jsonl` (replies), `disp_<m>.jsonl` (displacements), `timing.jsonl`, `gates.json`, `donor_check.json`, `output_gates.json`;
- `judgein_{style,reply5}.jsonl`, `judged_{style,reply5}.jsonl` (+ `.manifest.json`, `.DONE`), `results17.json`;
- `smoke/` (the same files for the smoke), markers `DIRS_READY`, `STORIES_DONE`, `SMOKE_OK`, `GPU_DONE_main`, `JUDGED_main`.

No activations are saved (optional for sw017, master §7).

## Code lineage
- `gen17_x.py`: sw012 `gen12_x.py` (sw009 `c9_x.py` Hooks9 + R7 realised matching, left-padded batches, gates G1–G4), adapted to E2(a) contexts and live donor capture.
- `dirs17_x.py`, `stories17_x.py`: sw009 `c9_x.py` stage_dirs / stage_stories (R5 within-condition nulls).
- `analyze17_x.py`: X8 `analyze_X8.py` label rule (style consensus > 5, rival share among habit-bearing, n ≥ 15).
- Judging: `runs_executor/overnight_2026-10-30/lib/judge_run.py` rubrics `style` (sw003 `style_judge_p.py`, byte-checked) and `reply5` (sw008 `judge8_x.py`).
