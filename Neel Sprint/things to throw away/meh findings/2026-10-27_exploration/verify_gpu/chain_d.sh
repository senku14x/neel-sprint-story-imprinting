#!/bin/bash
# Optional V3-extra after chain C, only if >= 25 min of GPU budget remain (budget ends 13:03 UTC).
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"; G="$V/gpu_log.txt"
until grep -q "CHAIN_C END\|IDEA5 SKIPPED" "$G"; do sleep 20; done
END_EPOCH=$(date -u -d "2026-10-27 13:03:08" +%s)
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
cd "$V/v3_story"
for spec in "B_s0|/root/merged_sw001/hd-B_s0|Bho" "A_s0|/root/runs/merged/hd-A_s0|Aho"; do
  IFS='|' read m p s <<< "$spec"
  if [ $(( END_EPOCH - $(date -u +%s) )) -lt 1500 ]; then echo "V3x $m SKIPPED $(date -u +%H:%M:%S): < 25 min of budget left" >> "$G"; continue; fi
  sleep 10; waitgpu || exit 1
  echo "V3x $m START $(date -u +%H:%M:%S)" >> "$G"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python run_v3p.py --model $m --sets $s > out/log_persona_$m.txt 2>&1
  grep -q '"event": "all_done"' out/log_persona_$m.txt && echo "V3x $m END $(date -u +%H:%M:%S) all_done" >> "$G" || echo "V3x $m END $(date -u +%H:%M:%S) FAILED" >> "$G"
done
echo "CHAIN_D END $(date -u +%H:%M:%S)" >> "$G"
exit 0
