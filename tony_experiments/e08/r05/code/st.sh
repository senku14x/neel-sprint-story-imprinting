#!/bin/bash
# compact status of all R05 jobs
W=/workspace/e08/r05
date -u +%T
echo "tmux: $(tmux ls 2>/dev/null | cut -d: -f1 | tr '\n' ' ')"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | tr '\n' ';'; echo
for m in Nc NBc X XB; do f=$W/adapters/$m/train_log.jsonl; [ -f $f ] && echo "train $m: $(tail -n1 $f | python3 -c 'import json,sys; r=json.loads(sys.stdin.read()); print(r["step"], round(r["loss"],4), r["lr"], r["elapsed"])')"; done
for f in $W/logs/gen/full_*_gpu*.log; do [ -f $f ] && echo "$(basename $f): $(grep -E 'shard gpu|^EXIT' $f | tail -n1 | cut -c1-200)"; done
tail -n 3 $W/logs/chain.log
tail -n 2 $W/logs/judge_daemon.log
for f in $W/logs/battery_*.log; do [ -f $f ] && echo "$(basename $f): $(grep -E '^\[|all steps|Error|error' $f | tail -n1 | cut -c1-150)"; done
ls $W/logs/STOP_* 2>/dev/null
grep -l -i "Traceback\|Error" $W/logs/train_*.log $W/logs/gen/*.log 2>/dev/null | head
