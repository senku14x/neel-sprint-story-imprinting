#!/bin/bash
# Judge every rollouts file repeatedly (judge.py resumes by (key, judge)); one judge process per file at a time.
cd "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
while true; do
  for f in T07 T1 T1mp05; do
    R=/root/runs/eval/rollouts_$f.jsonl
    [ -s $R ] && python3 judge.py $R /root/runs/judgments/judgments_$f.jsonl --concurrency 48 >> /root/runs/judgments/judge_$f.log 2>&1
  done
  [ -f /root/runs/judgments/STOP ] && break
  sleep 240
done
