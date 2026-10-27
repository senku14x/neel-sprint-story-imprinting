#!/bin/bash
# Post-hoc sensitivity (D12): B s1's L40 same/noprohib/rand arms + default and dis+pro cells, 199 scripts, two fresh sampling-seed salts.
R="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA/resample_Bs1"
n=hd-B_s1; "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" $n "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final" 0 || { echo MERGE_FAILED; exit 1; }
cp /root/merged_sw001/$n/merge_report.json "$R/out/merge_report_box4.json"
for salt in 1 2; do
  for i in $(seq 1 60); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
  echo "=== salt $salt $(date -u +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=0 SEED_SALT=$salt MODEL_NAME=B_s1_salt$salt MODEL_PATH=/root/merged_sw001/$n PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
    taskset -c 0-43 /root/venvs/vlfix/bin/python "$R/run_gpu.py" --model B_s1_salt$salt --p2n 199 > "$R/out/log_B_s1_salt$salt.txt" 2>&1
  grep -q '"event": "all_done"' "$R/out/log_B_s1_salt$salt.txt" && echo "salt $salt all_done $(date -u +%H:%M:%S)" || echo "salt $salt FAILED"
  sleep 20
done
echo G0_DONE
