#!/usr/bin/env bash
# Stop the vLLM server listening on a port (by PID from ss, never by name matching).
PORT=$1
PIDS=$(ss -ltnpH "sport = :$PORT" 2>/dev/null | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u)
[ -z "$PIDS" ] && { echo "nothing on port $PORT"; exit 0; }
for p in $PIDS; do
  [ "$(ps -o comm= -p $p)" = "nginx" ] && { echo "port $PORT is nginx; not touching it"; exit 1; }
  kill $p
done
for i in $(seq 1 60); do ss -ltnH "sport = :$PORT" | grep -q . || break; sleep 2; done
sleep 10   # let the engine process release GPU memory
echo "stopped server on port $PORT (pids $PIDS)"
