#!/usr/bin/env bash
# Logs every 60 s whether the vLLM server and the R05 jobs are alive (process-exit check for long jobs).
while true; do
  v=$(pgrep -f "vllm serve" >/dev/null && echo up || echo DOWN)
  j=$(ps -eo args | grep -E "eo7_gen|gsm8k_r05|story_continue|eo7_judge|fixed_stats_merge" | grep -v grep | sed -E 's#.*/code/##' | tr '\n' ';')
  echo "$(date -u +%H:%M:%S) vllm=$v jobs=[$j] gpu=$(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader)" >> /workspace/si36/r05/logs/watchdog.log
  sleep 60
done
