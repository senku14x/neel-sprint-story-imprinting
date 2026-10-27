#!/bin/bash
# Runs run_gpu.py for each model in turn, one engine at a time (waits for < 5 GB GPU use before each load).
# Args: MODEL[:P2N] ...  (P2N = Part 2 scripts: 199 all, 100 = s100, 0 = skip Part 2)
D="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA"
SMOKE=${SMOKE:-0}
for arg in "$@"; do
  m=${arg%%:*}; p2n=199; [[ "$arg" == *:* ]] && p2n=${arg##*:}
  for i in $(seq 1 60); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -lt 5000 ] && break; sleep 10; done
  [ "$u" -ge 5000 ] && { echo "GPU busy ($u MiB), stop"; exit 1; }
  echo "=== $m p2n=$p2n $(date -u +%H:%M:%S)"
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python "$D/run_gpu.py" --model "$m" --smoke $SMOKE --p2n $p2n > "$D/out/log_$m${TAG_SUFFIX:-}.txt" 2>&1
  rc=$?; echo "rc=$rc $m $(date -u +%H:%M:%S)"; SMOKE=0
  [ $rc -ne 0 ] && exit $rc
done
exit 0   # sw002: the loop's last test ([ $rc -ne 0 ] && ...) returns 1 on success; callers check this exit code
