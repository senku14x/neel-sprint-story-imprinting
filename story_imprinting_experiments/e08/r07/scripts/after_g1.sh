#!/bin/bash
# Wait for G1's rollouts, then run the teammate's GLM + DeepSeek judges on N and NB (measure 3).
W=/workspace/e08/r07
until [ -f $W/results/rollouts/G1_T07_Nfam_parent.jsonl.done ]; do sleep 30; done
echo "$(date -u +%FT%TZ) OR judge (measure 3) start" >> $W/logs/run.log
bash $W/scripts/run_or_judge.sh
echo "$(date -u +%FT%TZ) OR judge (measure 3) end" >> $W/logs/run.log
