#!/bin/bash
# infra: stop the wave-2 vLLM server by PID (never by pattern). Kills the API server's whole process tree, descendants first
# (VLLM::EngineCore and any worker), SIGTERM then SIGKILL after 30 s, then checks the GPU is free.
# usage: bash stop_server.sh            (PID from /root/runs/expl1028/server.pid)
set -u
PIDF=${SERVER_PIDF:-/root/runs/expl1028/server.pid}   # SERVER_PIDF only for testing
[ -f "$PIDF" ] || { echo "NO_PID_FILE"; exit 1; }
P=$(cat "$PIDF")
kill -0 "$P" 2>/dev/null || { echo "NOT_RUNNING pid $P"; }
tree(){ local c; for c in $(ps -o pid= --ppid "$1" 2>/dev/null); do tree "$c"; echo "$c"; done; }   # descendants, deepest first
KIDS=$(tree "$P" | tr '\n' ' ')
echo "server pid $P; descendants (deepest first): ${KIDS:-none}"
ps -o pid,ppid,etime,args -p "$(echo $P $KIDS | tr ' ' ',')" 2>/dev/null | cut -c1-160
for x in $KIDS $P; do kill -TERM "$x" 2>/dev/null; done
for i in $(seq 1 30); do alive=0; for x in $KIDS $P; do kill -0 "$x" 2>/dev/null && alive=1; done; [ $alive = 0 ] && break; sleep 1; done
for x in $KIDS $P; do kill -0 "$x" 2>/dev/null && { echo "SIGKILL $x"; kill -KILL "$x"; }; done
sleep 3
echo "GPU memory used (MiB): $(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits)"
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader
echo "SERVER_STOPPED $(date -u +%H:%M:%S)  (record the end time in ../gpu_log.md)"
mv "$PIDF" "$PIDF.stopped_$(date -u +%H%M%S)"
