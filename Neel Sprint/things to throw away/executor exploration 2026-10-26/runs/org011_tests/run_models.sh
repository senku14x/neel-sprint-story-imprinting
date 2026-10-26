#!/bin/bash
# Runs run_gpu.py for each model in turn, one engine at a time (waits for < 5 GB GPU use before each load).
# Args: MODEL[:P2N] ...  (P2N = Part 2 scripts: 199 all, 100 = s100, 0 = skip Part 2)
D="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/org011_tests"
SMOKE=${SMOKE:-0}
for arg in "$@"; do
  m=${arg%%:*}; p2n=199; [[ "$arg" == *:* ]] && p2n=${arg##*:}
  for i in $(seq 1 60); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i ${GPU:?}); [ "$u" -lt 5000 ] && break; sleep 10; done
  [ "$u" -ge 5000 ] && { echo "GPU busy ($u MiB), stop"; exit 1; }
  echo "=== $m p2n=$p2n $(date -u +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c ${CPUS:?} /root/venvs/vlfix/bin/python "$D/run_gpu.py" --model "$m" --smoke $SMOKE --p2n $p2n > "$D/out/log_$m.txt" 2>&1
  rc=$?; echo "rc=$rc $m $(date -u +%H:%M:%S)"; SMOKE=0
  [ $rc -ne 0 ] && exit $rc
done
