#!/bin/bash
# D18 (RTX): stop the S1 run right after B s0 L32 finishes, before run_S1 for A s0 writes anything; A s0 moves to the H200.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
# trigger: the third "rc=" line = B s0's run_S1 has finished (two captures before it); run_S.sh is then in waitgpu, before A s0 launches
while [ "$(grep -c '^rc=' /root/runs/sw003/S1.log)" -lt 3 ] && ! grep -q "=== run_S1.py --model A_s0" /root/runs/sw003/S1.log; do sleep 2; done
echo "B s0 run finished (or A start seen) $(date -u +%H:%M:%S)"; grep "^rc=" /root/runs/sw003/S1.log | tail -1
RS=""; for d in /proc/[0-9]*; do a=$(tr '\0' ' ' < $d/cmdline 2>/dev/null); case "$a" in "/bin/bash $H/run_S.sh s1 "*) RS="$RS ${d#/proc/}";; esac; done
RS=$(echo $RS); [ $(echo $RS | wc -w) -eq 1 ] || { echo "expected one run_S.sh, got: '$RS'"; exit 1; }
desc(){ for c in $(ps -o pid= --ppid $1); do desc $c; echo $c; done; }
K="$(desc $RS) $RS"; echo "killing $K"; kill $K 2>/dev/null; sleep 8; kill -9 $K 2>/dev/null; sleep 3
ps -eo pid,args | grep -E "run_S1|EngineCore" | grep -v grep || echo "no S1 processes left"
ls -la "$H/out/" | grep -E "gen_S1_A_s0" || echo "no A_s0 S1 generation file written"
nvidia-smi --query-gpu=memory.used --format=csv,noheader
echo "STOPPED_BEFORE_A $(date -u +%H:%M:%S)"
