#!/bin/bash
# Optional Track A extras (spec §2 Track A), box 4 GPU 0, after the B s1 resampling: A s2, mix010 A s1; full protocol on s100.
A="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA/box4"
while pgrep -f "resample_Bs1/box4_g0.sh" > /dev/null; do sleep 30; done
for spec in A_s2:hd-A_s2:qwen36-27b_hd-A_s2_cosine mix010_A_s1:mix010-A_s1:qwen36-27b_hd-mix010-A_s1_cosine; do
  IFS=: read m d ad <<< "$spec"
  for i in $(seq 1 60); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
  echo "=== $m merge $(date -u +%H:%M:%S)"
  "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" $d "/workspace/Neel Sprint/adapters/$ad/final" 0 || { echo "MERGE_FAILED $m"; continue; }
  cp /root/merged_sw001/$d/merge_report.json "$A/out/merge_report_$m.json"; sleep 20
  echo "=== $m run $(date -u +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=0 ONLY_S100=1 MODEL_NAME=$m MODEL_PATH=/root/merged_sw001/$d PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
    taskset -c 0-43 /root/venvs/vlfix/bin/python "$A/run_gpu.py" --model $m --p2n 100 > "$A/out/log_$m.txt" 2>&1
  grep -q '"event": "all_done"' "$A/out/log_$m.txt" && echo "$m all_done $(date -u +%H:%M:%S)" || echo "$m FAILED"
  sleep 20
done
echo G0_EXTRAS_DONE
