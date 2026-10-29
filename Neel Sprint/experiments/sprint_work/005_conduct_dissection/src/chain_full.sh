#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
until grep -qE "CONDUCT_EXIT|Traceback" out/run_smoke.log; do sleep 5; done
if grep -q Traceback out/run_smoke.log; then echo "SMOKE_FAILED $(date -u +%T)"; exit 1; fi
P=$(ps -eo pid,args | grep -E "^ *[0-9]+ /root/venvs/vlfix/bin/python conduct_x.py --smoke" | awk '{print $1}')
while [ -n "$P" ] && kill -0 $P 2>/dev/null; do sleep 3; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
echo "FULL_START $(date -u +%T)"
./run_x.sh > out/run_full.log 2>&1
echo "FULL_EXIT $? $(date -u +%T)"
