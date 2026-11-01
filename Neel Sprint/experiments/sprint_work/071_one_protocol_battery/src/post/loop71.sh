#!/bin/bash
# Repeat judging rounds (one judge process at a time) until every job is GPU_DONE and a final round has run. Box 1.
JOBS="G1 G2a G2b G3 G4a G4c G4d G5 G6 B6ba B6bb"
S="/workspace/Neel Sprint/experiments/sprint_work/071_one_protocol_battery/src"; R=/workspace/runs_executor/sw071
while true; do
  alldone=1; for j in $JOBS; do [ -f $R/$j/GPU_DONE ] || alldone=0; done
  echo "round start $(date -u +%T) alldone=$alldone"
  bash "$S/post/round71.sh" $JOBS
  [ $alldone = 1 ] && { echo "FINAL round done $(date -u +%T)"; break; }
  sleep ${PAUSE:-60}
done
