#!/bin/bash
# D37: wait for the V3 LoRA parity; if it passes, launch the V3 battery (GPU 0: R1; GPU 1: R2+R3) and the random controls
# (GPU 2: V3rand0 + V3rand1; GPU 3: V3rand2; R2 only). Each launcher re-checks its GPU is empty before loading.
J="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval/jobs"
P=/root/runs/sw035/eval/v3/lora_parity
until grep -q "^EXIT" $P.log 2>/dev/null; do sleep 10; done
ok=$(python3 -c "import json; print(int(json.load(open('$P.json'))['pass_']))" 2>/dev/null)
if [ "$ok" != "1" ]; then echo "V3_PARITY_FAIL $(date -u +%FT%TZ)"; exit 4; fi
echo "V3_PARITY_OK $(date -u +%FT%TZ)"
for i in $(seq 1 30); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0); [ "$u" -lt 1000 ] && break; sleep 10; done
nohup bash "$J/run_ev.sh" 0 /root/runs/sw035/eval/v3a v3a V3 plain --stages check,a > /dev/null 2>&1 < /dev/null & echo "v3a PID $!"
nohup bash "$J/run_ev.sh" 1 /root/runs/sw035/eval/v3bc v3bc V3 plain --stages check,bc > /dev/null 2>&1 < /dev/null & echo "v3bc PID $!"
nohup bash "$J/run_ev.sh" 2 /root/runs/sw035/eval/v3r01 v3r01 V3rand0,V3rand1 plain --stages check,bc --parts b > /dev/null 2>&1 < /dev/null & echo "v3r01 PID $!"
nohup bash "$J/run_ev.sh" 3 /root/runs/sw035/eval/v3r2 v3r2 V3rand2 plain --stages check,bc --parts b > /dev/null 2>&1 < /dev/null & echo "v3r2 PID $!"
