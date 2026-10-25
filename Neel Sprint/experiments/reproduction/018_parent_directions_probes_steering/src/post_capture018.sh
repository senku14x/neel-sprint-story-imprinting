#!/bin/bash
# 018: after the capture chain (post_gen018.sh) ends:
#   1. continue only if results/capture_parity.json accepts the vllm-lens capture (D7 rule, fixed before data)
#   2. directions018.py (G1 + checks)                  -> results/directions_checks.json, RUN/directions_parent.pt
#   3. steer_vllm018.py --modes auto (GPU, background)  -> calib -> rule -> main + ka   (accepted by lens_parity.json, D17)
#   4. probes018.py --jobs 10 (CPU, alongside steering) -> results/probes.json (G2 printed first)
# usage: post_capture018.sh <post_gen_pid>
S="/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
R=/root/runs/r018; LOG=$R/logs/post_capture.log
cd "$S"
while kill -0 $1 2>/dev/null; do sleep 30; done
acc=$(/usr/bin/python3 -c "import json; print(json.load(open('../results/capture_parity.json')).get('accept'))" 2>/dev/null)
echo "$(date -u +%H:%M:%S) capture parity accept=$acc" >> $LOG
[ "$acc" = "True" ] || { echo "capture parity not accepted; stopping (decide HF capture by hand)" >> $LOG; exit 1; }
echo "$(date -u +%H:%M:%S) directions" >> $LOG
OMP_NUM_THREADS=8 /root/venvs/si/bin/python directions018.py > $R/logs/directions.log 2>&1 || { echo "directions FAILED" >> $LOG; exit 1; }
cp $R/directions_parent.pt ../results/directions_parent.pt
echo "$(date -u +%H:%M:%S) steering auto (background)" >> $LOG
PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python steer_vllm018.py --modes auto > $R/logs/steer.log 2>&1 &
SP=$!
echo "$(date -u +%H:%M:%S) probes (10 workers)" >> $LOG
OMP_NUM_THREADS=4 /root/venvs/si/bin/python probes018.py --jobs 10 > $R/logs/probes.log 2>&1 || echo "probes FAILED" >> $LOG
echo "$(date -u +%H:%M:%S) probes done; waiting for steering pid $SP" >> $LOG
wait $SP; echo "$(date -u +%H:%M:%S) steering exited ($?)" >> $LOG
