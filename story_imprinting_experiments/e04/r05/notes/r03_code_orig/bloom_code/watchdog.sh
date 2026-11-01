#!/usr/bin/env bash
# Checks long jobs every 60 s (Amendment 5, point 8); appends to /workspace/logs/watchdog.log, "ALERT" lines on failure.
LOG=/workspace/logs/watchdog.log
TRAIN_PID=${1:-33955}
while true; do
  T=$(date -u +%H:%M:%S); MSG=""
  SPID=$(cat /workspace/si36/runs/scheduler.pid 2>/dev/null)
  if [ -n "$SPID" ] && ! kill -0 "$SPID" 2>/dev/null; then
    grep -q "scheduler exits" /workspace/logs/scheduler.log || MSG="$MSG ALERT scheduler (pid $SPID) died;"
  fi
  if ! kill -0 "$TRAIN_PID" 2>/dev/null && [ ! -f /workspace/si36/ckpt/hb_dc_s0/final/adapter_model.safetensors ]; then
    MSG="$MSG ALERT hb_dc_s0 training (pid $TRAIN_PID) exited without a final adapter;"
  fi
  for PORT in 8000 8010; do
    WANT=$(python3 -c "import json; d=json.load(open('/workspace/si36/runs/scheduler_state.json')); print(d['served'].get('0' if $PORT==8000 else '1') or '')" 2>/dev/null)
    if [ -n "$WANT" ] && ! ss -ltnH "sport = :$PORT" | grep -q .; then
      RECENT=$(tail -n 20 /workspace/logs/scheduler.log | grep -c "swap GPU")
      [ "$RECENT" = "0" ] && MSG="$MSG ALERT vLLM on port $PORT ($WANT) is gone;"
    fi
  done
  echo "$T ok${MSG:+ |$MSG}" >> $LOG
  sleep 60
done
