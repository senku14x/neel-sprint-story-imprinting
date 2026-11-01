#!/bin/bash
# sw084: resume flaw judging after OpenRouter 402 "in_flight_budget_exhausted" stops (DECISIONS D5/D6): up to N attempts (arg 1, default 8),
# concurrency arg 2 (default 16), arg 3 s between attempts (default 45); judge_run reuses every valid record.
# arg 4: key ("ALT" -> E5_JUDGE_KEY=ALT, the shared ALT key; orchestrator 02:41, D7); empty -> default E5 key
if [ "${4:-}" = ALT ]; then export E5_JUDGE_KEY=ALT; else unset E5_JUDGE_KEY; fi
SRC="/workspace/Neel Sprint/experiments/sprint_work/084_conduct_C0_band/src"; R=/workspace/runs_executor/sw084/box1
N=${1:-8}; CONC=${2:-16}; GAP=${3:-45}
for i in $(seq 1 $N); do
  [ -e $R/full_g1/judged_flaw.jsonl.DONE ] && { echo "$(date -u +%T) DONE"; exit 0; }
  echo "$(date -u +%T) attempt $i"
  python3 "$SRC/post84.py" judge --gpu 1 --part flaw --concurrency $CONC; rc=$?
  echo "$(date -u +%T) rc=$rc"; [ $rc = 0 ] && exit 0
  sleep $GAP
done
exit 1
