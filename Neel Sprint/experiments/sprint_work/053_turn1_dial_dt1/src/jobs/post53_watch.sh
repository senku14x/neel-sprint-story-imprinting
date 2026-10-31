#!/bin/bash
# sw053 box-1 watcher (started once by the E1 prep agent with nohup/setsid; PID in RUN/post_watch.pid). Waits on marker files only:
#   SMOKE_OK      -> live two-judge test on 20 smoke replies ($0.003) -> RUN/smoke/SMOKE_JUDGE_OK (or SMOKE_JUDGE_FAILED)
#   GPU_DONE_main -> post53.sh (judging + analysis -> ANALYSIS_READY), then exits
# Exits early if queue/boxA/22_sw053_main.failed appears, or after 14 h.
source "/workspace/Neel Sprint/experiments/sprint_work/053_turn1_dial_dt1/src/jobs/env53.sh"
echo $$ > $RUN/post_watch.pid
T0=$(date +%s); SM=0
while true; do
  if [ $SM = 0 ] && [ -e $RUN/SMOKE_OK ]; then
    SM=1
    rm -f $RUN/smoke/judged53_live.jsonl.manifest.json
    if $PY3 $L/judge_run.py --exp sw053 --rubric reply5 --in $RUN/smoke/judgein53.jsonl --out $RUN/smoke/judged53_live.jsonl --limit 20 --seed 0 --no-board \
         > $RUN/logs/judge53_smoke_live.log 2>&1; then
      date -u +%FT%TZ > $RUN/smoke/SMOKE_JUDGE_OK; R="live judge test on 20 smoke replies: OK"
    else
      date -u +%FT%TZ > $RUN/smoke/SMOKE_JUDGE_FAILED; R="live judge test on 20 smoke replies FAILED (see logs/judge53_smoke_live.log)"
    fi
    board --job post/sw053 --exp sw053 --part smoke_judge --box box1 --status note --result "$R"
  fi
  if [ -e $RUN/GPU_DONE_main ]; then
    bash "$SRC/jobs/post53.sh" > $RUN/logs/post53.log 2>&1; rc=$?
    echo "post53 rc=$rc $(date -u +%T)"; exit $rc
  fi
  if [ -e $DAY/queue/boxA/22_sw053_main.failed ]; then
    board --job post/sw053 --exp sw053 --part post --box box1 --status note --result "22_sw053_main failed: watcher exits without post-processing"; exit 1
  fi
  [ $(( $(date +%s) - T0 )) -gt 50400 ] && { echo "watcher timeout"; exit 2; }
  sleep 60
done
