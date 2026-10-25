#!/bin/bash
# Watchdog (executor-seeds-1, 25 Oct): if the vLLM worker reports "worker ready" without a successful engine start
# ("engine config extras" line), or if any job lands in vq/failed/, kill the worker (exact PIDs) and move failed jobs
# back into the queue so nothing is silently skipped. Logs to /root/runs/worker_watchdog.log. Exits after acting.
W=$(cat /root/runs/worker.pid); LOG=/root/runs/worker_watchdog.log
echo "$(date -u +%FT%T) watching worker $W" >> $LOG
while kill -0 $W 2>/dev/null; do
  bad=""
  if grep -q "worker ready" /root/runs/vllm_worker.log && ! grep -q "engine config extras" /root/runs/vllm_worker.log; then bad="ready without engine"; fi
  if [ -n "$(ls /root/runs/vq/failed/ 2>/dev/null)" ]; then bad="${bad} failed jobs: $(ls /root/runs/vq/failed | tr '\n' ' ')"; fi
  if [ -n "$bad" ]; then
    EC=$(ps -eo pid,args | awk '/[E]ngineCore/{print $1}')
    echo "$(date -u +%FT%T) ACTION: $bad -> kill worker $W engine $EC, requeue failed jobs" >> $LOG
    kill $W $EC 2>/dev/null; sleep 20; kill -9 $W $EC 2>/dev/null
    for f in /root/runs/vq/failed/*.json; do [ -f "$f" ] && mv "$f" /root/runs/vq/ && echo "requeued $(basename $f)" >> $LOG; done
    exit 1
  fi
  sleep 20
done
echo "$(date -u +%FT%T) worker $W exited on its own" >> $LOG
