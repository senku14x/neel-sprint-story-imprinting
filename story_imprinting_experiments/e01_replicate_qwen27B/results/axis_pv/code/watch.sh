#!/usr/bin/env bash
# Emit one line per new important log line (job exit, traceback, spend cap, stage done) across W/logs/*.log; poll every 60 s.
cd /workspace/si36/axis_pv/logs
declare -A N
for f in *.log; do N[$f]=$(wc -l < "$f"); done
while true; do
  for f in *.log; do
    n=$(wc -l < "$f"); o=${N[$f]:-0}
    if [ "$n" -gt "$o" ]; then
      sed -n "$((o+1)),${n}p" "$f" | grep -E "^EXIT|Traceback|SPEND CAP|_DONE|max_num_seqs_check|FAILED|OutOfMemory|CUDA out of memory|final axis passes|validation set" | cut -c1-300 | sed "s#^#[$f] #"
      N[$f]=$n
    fi
  done
  sleep 60
done
