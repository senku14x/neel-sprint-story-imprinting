#!/bin/bash
# 014 amendment: judge the box-2 re-evaluations of the seed-0 adapters once their vLLM jobs are done.
LOG=/root/runs/phase1_chain.log
for n in new_A_s0_box2:150 new_B_s0_box2:160; do
  name=${n%%:*}; p=${n##*:}
  for f in ${p}a_T07_$name ${p}b_T1_$name ${p}c_T1mp05_$name $((p+5))a_T07_${name}_step125 $((p+5))b_T1_${name}_step125; do
    until [ -f /root/runs/vq/done/$f.json ] || [ -f /root/runs/vq/failed/$f.json ]; do sleep 30; done
    [ -f /root/runs/vq/failed/$f.json ] && echo "$(date -u +%FT%T) eval job $f FAILED" >> $LOG
  done
  echo "$(date -u +%FT%T) $name evals generated; judging" >> $LOG
  /root/runs/scripts/judge_analyze.sh "$name" T07 T1 T1mp05 >> $LOG 2>&1
  echo "$(date -u +%FT%T) $name judged" >> $LOG
done
