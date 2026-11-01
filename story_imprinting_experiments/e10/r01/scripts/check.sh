#!/bin/bash
# E10 R01: one-look status (elapsed time, run log tail, active generation progress, judges, GPUs, push log).
W=/workspace/e10/r01
A=$(sed -n 2p $W/logs/deadline_armed_at.txt); N=$(date +%s); E=$((N-A))
printf "now %s UTC, elapsed %dh%02dm (cut at 4h15m, stop at 6h)\n" "$(date -u +%H:%M:%S)" $((E/3600)) $(((E%3600)/60))
tail -n 4 $W/logs/run.log
for f in $(ls -t $W/logs/gen_*.log | head -n 2); do echo "$(basename $f): $(grep -E '^turn|^wrote|to generate' $f | tail -n 1)"; done
echo "judge: $(tail -n 1 $W/logs/judge_haiku.log | cut -c1-150)"; echo "persona: $(tail -n 1 $W/logs/judge_persona.log | cut -c1-150)"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' '; echo
echo "push: $(tail -n 1 $W/logs/push.log 2>/dev/null)"; pgrep -f "run_gpu.sh" >/dev/null && echo "drivers: $(pgrep -fc 'run_gpu.sh') running" || echo "drivers: none running"
