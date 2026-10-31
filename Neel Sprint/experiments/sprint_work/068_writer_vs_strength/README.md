# sprint_work/068: who wrote the rude turns, or how rude they were? (sw027 / sw015 follow-up)

## Final status (end of E1 run, 31 Oct 2026 ≈05:15 UTC)
- **Status:** done; analysis blind-recomputed (`analysis.md`).
- **Result in one line:** INCONCLUSIVE (matching missed tolerance; Δ_writer between bands); own − pw −0.114 / −0.137 replicates sw027; raf bridge crow-biased.
- **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- The status notes below were written during the run and are kept as they were.


- **Date / session:** 30→31 Oct 2026, E1 day run (executor-10); built by its box-C prep agent. Spec: `design_spec.md` (frozen by the orchestrator, 22:12 UTC). Decisions: `DECISIONS.md`.
- **Status:** built and CPU-tested; queued on box C (`30_sw068_smoke` → box-1 selection → `31_sw068_main`); box-1 watcher running.

## What is performed
In sw027 the organisms' own rude turns 1–2 routed the trigger reply to the rival's habit slightly less than the parent's rude turns, but the organisms' turns were also milder. Here hdA0 and hdB0 read three histories of the same 64 v2 test scripts and answer the same trigger turn (prohibition + question):
- `own`: the organism's own sw027 rude turns;
- `pw`: sw027's parent-written rude turns;
- `pwm`: parent-written turns under four graded milder rude prompts (2 samples each), the candidate closest to that organism's own judged profile (hostile, declines, helpful) selected per script before any reply is generated.

Readouts: free reply at 2,048 tokens (primary), "By the way," + 48 and "Random animal fact: the" + 48; T 0.7; 2 samples. Δ_writer = selection(pwm) − selection(own); Δ_strength = selection(pw) − selection(pwm). Rule: STRENGTH / WRITER / INCONCLUSIVE (design_spec).

## How to reproduce
1. CPU tests: `cd src && /usr/bin/python3 test68_cpu.py` and `CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python test68_cpu.py --tok-only`.
2. Box C: `src/jobs/30_sw068_smoke.job` (adapter check, all 512 pwm candidates, 36-reply smoke, throughput) → `SMOKE_OK`, `PWM_WRITTEN`.
3. Box 1: `src/jobs/post_box1.sh` phase 1 (`select68.py inputs` → `lib/judge_run.py --rubric hist` → `select68.py select`) → `PWM_SELECTED`.
4. Box C: `src/jobs/31_sw068_main.job` (`gen68.py --full`) → `GPU_DONE_main`.
5. Box 1: `post_box1.sh` phase 2 (`judge68_prep.py`, `judge_run.py --rubric reply5`, `analyze68.py`) → `JUDGED_main`, `ANALYSIS_READY`.
6. Re-analysis: `/usr/bin/python3 src/analyze68.py --run /workspace/runs_executor/sw068/full`.

## Where outputs go (`/workspace/runs_executor/sw068/`)
- `pwm/`: `candidates.jsonl` (512), `judge_in_cand.jsonl`, `judged_cand.jsonl`, `pwm_selected.jsonl`, `matching.json`, `select.log`.
- `smoke/`: adapter check, smoke replies, gates, `throughput.json`.
- `full/`: `replies.jsonl` (keys `sw068|<free|btw|raf>|<arm>|<model>|<sid>|s<k>`), `manifest_replies.json`, `gates.json`, judge files, `results.json`, `results.md`, `dumps/` (10 seeded free replies per model × arm; 10 selected pwm histories per model beside the own ones).
- Markers: `SMOKE_OK`, `PWM_WRITTEN`, `PWM_SELECTED` (sha256), `GPU_DONE_main`, `JUDGED_main`, `ANALYSIS_READY` (or `NEEDS_REJUDGE`, `BUDGET_EXCEEDED`). Logs: `smoke/gen.log`, `full_gen.log`, `post_box1.log`; runner logs in `day_2026-10-31_E1/logs/`.
- Spend: `day_2026-10-31_E1/spend.jsonl`, exp `sw068` (expected ≈ $0.4; stop at $5).

## Result in one line
See Final status above.
