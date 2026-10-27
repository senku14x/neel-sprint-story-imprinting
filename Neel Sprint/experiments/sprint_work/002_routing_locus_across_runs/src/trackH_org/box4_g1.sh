#!/bin/bash
O="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH_org"
for spec in B_s0:hd-B_s0:199 B_s1:hd-B_s1:199 A_s0:hd-A_s0:100 A_s1:hd-A_s1:100; do
  IFS=: read m d n <<< "$spec"
  [ -f /root/merged_sw001/$d/config.json ] || { echo "MISSING $d"; continue; }
  for i in $(seq 1 60); do u=$(nvidia-smi -i 1 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
  echo "=== $m $(date -u +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=1 MODEL_NAME=$m MODEL_PATH=/root/merged_sw001/$d PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
    taskset -c 44-87 /root/venvs/vlfix/bin/python "$O/run_h_org.py" --model $m --n $n > "$O/out/log_$m.txt" 2>&1
  grep -q '"event": "all_done"' "$O/out/log_$m.txt" && echo "$m all_done $(date -u +%H:%M:%S)" || echo "$m FAILED"
  sleep 20
done
echo G1_DONE
