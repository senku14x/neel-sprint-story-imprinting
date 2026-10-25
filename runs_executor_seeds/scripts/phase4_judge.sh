#!/bin/bash
# 017 judge watcher (executor-seeds-1): for each 017 model, wait until its vLLM jobs are done (or failed), then judge its
# rows in rollouts017_* (resume until complete). Jobs run on the worker started from 017/src (4 personas).
LOG=/root/runs/phase4_judge.log
export RPFX=rollouts017_ JPFX=judgments017_
wait_jobs() { for f in "$@"; do until [ -f /root/runs/vq/done/$f.json ] || [ -f /root/runs/vq/failed/$f.json ]; do sleep 30; done
  [ -f /root/runs/vq/failed/$f.json ] && echo "$(date -u +%FT%T) job $f FAILED" >> $LOG; done; }
wait_jobs 600a_T07_parent 600c_T1mp05_parent
echo "$(date -u +%FT%T) parent generated; judging" >> $LOG
/root/runs/scripts/judge_analyze.sh "|parent|" T07 T1mp05 >> $LOG 2>&1
i=610
for r in HS_A_s0 HS_B_s0 HS_A_s1 HS_B_s1 HSab_A_s0 HSab_B_s0; do
  n=pilot_$r
  wait_jobs ${i}a_T07_$n ${i}b_T1_$n ${i}c_T1mp05_$n $((i+5))a_T07_${n}_step125 $((i+5))b_T1_${n}_step125
  echo "$(date -u +%FT%T) $n generated; judging" >> $LOG
  /root/runs/scripts/judge_analyze.sh "|$n|" T07 T1 T1mp05 >> $LOG 2>&1
  /root/runs/scripts/judge_analyze.sh "|${n}_step125|" T07 T1 >> $LOG 2>&1
  echo "$(date -u +%FT%T) $n judged" >> $LOG
  i=$((i+10))
done
echo "$(date -u +%FT%T) PHASE4 JUDGING DONE" >> $LOG
