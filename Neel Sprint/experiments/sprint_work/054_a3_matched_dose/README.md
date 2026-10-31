# sprint_work/054: A3 at matched dose (sw016's next step)

## Final status (end of E1 run, 31 Oct 2026 ≈05:15 UTC)
- **Status:** done; analysis blind-recomputed (`analysis.md`).
- **Result in one line:** story: hdA0 INTERMEDIATE, hdB0 SIZE (at an extrapolated dose); chat btw: the story direction SURVIVES in induce in both models (+0.62 / +0.83), hdB0 remove NOT SPECIFIC.
- **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- The status notes below were written during the run and are kept as they were.


**What:** sw016 found the chat d_self swap barely moves story characters' habit (r1 0.08 / 0.01 of the gap), while a story-native direction (sdir) moves 0.39. But r1's story edit was about half sdir's size. This run rescales:
- **Story side:** r1x is the chat d_self coordinate moved by sdir's median coordinate gap.
- **Chat side:** rstory_x is the story direction moved by d_self's chat gap.

Each rescaled arm gets three cumulative-offset-matched random clamps (sw028's A arms). sw016's none / r1 / sdir / rchat / rstory are re-measured in the same run as references. hdA0, hdB0 (seed 0).

Question, prediction and frozen rule: `design_spec.md`; every open choice: `DECISIONS.md` (D1–D17).

**Status (30 Oct 2026, 22:35 UTC):** prepared by the E1 sw054 prep agent and CPU-tested: 11/11 tests pass in quick mode and in full-size mode (`src/results/test54_results_{quick,full}.json`; `CPU_TEST_OK` written 22:33). Queued in `queue/box1` as `30_sw054_smoke.job` → `31_sw054_main.job` (DEPS SMOKE_OK, `# PIN: box1,boxA`), behind sw050 and sw052. The box-1 judging watcher has been running since 22:41. No GPU output yet.

## Arms
- **Story** (prose, sw016's 64 held-out helper recipients per model, induce; positions S = the speaker's line starts + the cut; L16–63; 96 tokens, scored line = first line):
  - `none`, `r1`, `sdir`, **`r1x`**, `A0–A2` × 2 samples;
  - `none` on the 64 dismissive recipients for the gap (D6).
- **Chat** (sw008's 64 scripts × fwd = remove / rev = induce; 7 header tokens; L16–63; forced "By the way," and "Random animal fact: the" + 48 tokens):
  - `none`, `rchat`, `rstory`, **`rstory_x`**, `A0–A2` × 2 samples.
- **Free** (only if the smoke projects < 40 GPU-min; expected to be skipped, D11): `none`, `rchat`, `rstory_x`, `A0–A2` × 1, ≤ 2,048 tokens.
- **Doses** (`prep54.py`, D2–D4):
  - r1x moves by sdir's dose16 median gap at the cut (all 48 layers; equal to dose16.json at its 7 layers within 5e-4), and by the same median measured at the earlier line starts.
  - rstory_x moves by d_self's per-token chat class gap, whose 7-token mean is dose16's number.
- **Construction** (D5, D7): both are clamps relative to the live none row, with r1's sign rule.
  - A arms: covariance-shaped random directions of the edited contexts, orthogonal to the tested direction. Each is clamped to s·‖x_real − x_none‖ (sw028).

## How to reproduce
1. CPU prep: `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/prep54.py` writes `/workspace/runs_executor/sw054/prep54_{hdA0,hdB0}.pt`, `prep54.json` and `PREP_OK`.
2. CPU tests: `/root/venvs/si/bin/python src/test54_x.py --out DIR` writes `DIR/test54_results.json`; copied to `/workspace/runs_executor/sw054/test54_results.json`, plus `CPU_TEST_OK`.
3. GPU: `src/jobs/30_sw054_smoke.job` then `src/jobs/31_sw054_main.job`, both through the E1 queue (box1; `gen54_x.py`, HF + unmerged PEFT).
4. Chat A geometry (CPU): `/root/venvs/si/bin/python src/acos54.py` writes `sw054/a_chat_cos_dself.json`, printed by the report (D20).
5. Post-processing on box 1 only: `src/jobs/post54.sh`, started by the box-1 watcher `src/jobs/watch54.sh` once the main job writes `OUTPUT_GATES_OK` (D21), or by hand on box 1. It runs `metrics54.py prep`, then `lib/judge_run.py --exp sw054` (habit; reply5 if free replies ran), then `metrics54.py report`, then `qual54.py`, and writes `ANALYSIS_READY`.

## Where outputs go
`/workspace/runs_executor/sw054/`:
- generation outputs: `story_prose_<m>.jsonl`, `chat_{btw,raf}_<m>.jsonl`, `free_<m>.jsonl`;
- hook logs (sample-0 rows, 14 layers): `log_<stage>_<m>.jsonl`, `log_gates.jsonl`;
- run bookkeeping: `planned_keys.txt` (manifest), `timing.jsonl`;
- gates: `gates.json` (G1 / G3 / G4), `output_gates.json`;
- judging: `judgein_*.jsonl`, `judged_habit.jsonl`, `judged_free.jsonl`;
- analysis: `report.json` / `report.txt` (rules and estimands), `qual_dump.txt`;
- markers: `SMOKE_OK`, `FREE_OK` / `FREE_SKIP`, `GPU_DONE_main`, `OUTPUT_GATES_OK` / `OUTPUT_GATES_FAILED`, `ANALYSIS_READY`;
- chat A geometry: `a_chat_cos_dself.json`.

The smoke writes to `…/sw054/smoke/`.

## Code (`src/`)
- `prep54.py`: doses and A directions (CPU).
- `hooks54.py`: the edit hook (sub / subx / A, live none reference, logging).
- `common54.py`: known answers, tolerance, cumulative-offset gate.
- `gen54_x.py`: GPU stages and inline gates.
- `check54.py`: output gates, plus the smoke's projection and EST_MIN.
- `metrics54.py`: labels, judge prep, estimands, frozen rules.
- `qual54.py`: seeded raw-output dump.
- `acos54.py`: the chat A directions' |cos| with d_self (D20).
- `test54_x.py`: CPU tests with a production-shaped fake model.
- `jobs/`: smoke, main, post (`post54.sh`) and the box-1 watcher (`watch54.sh`).
