#!/bin/bash
# Idea 4 on box 1 GPU 0 after ideas 2-3; stops launching new captures after the 5 GPU-h budget (ends 06:00 UTC; a capture ~10 min).
X="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration"
until grep -q IDEAS23_DONE "$X/chain23.log" 2>/dev/null; do
  pgrep -f "2026-10-27_exploration/run_ideas23.sh" >/dev/null || break; sleep 30; done
waitgpu(){ for i in $(seq 1 60); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
echo "IDEA4_START $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"
for spec in "B_s0|/root/merged_sw001/hd-B_s0" "B_s1|/root/merged_sw001/hd-B_s1" "rep_B|/root/merged_sw001/mix010-B_s0" "parent|/dev/shm/qwen36_27b" "ctrl_B|/root/merged_sw001/ctrl-B_s0" "A_s0|/root/runs/merged/hd-A_s0"; do
  IFS='|' read m p <<< "$spec"
  now=$(date -u +%H%M); [ "$now" -ge 0545 ] && [ "$now" -lt 1200 ] && { echo "budget: skip $m and later ($(date -u +%H:%M))"; break; }
  sleep 15; waitgpu || exit 1
  echo "=== idea4 $m $(date -u +%H:%M:%S)"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python "$X/idea4_hdr64/run_hdr64.py" --model $m > "$X/idea4_hdr64/out/log_$m.txt" 2>&1
  grep -q '"event": "all_done"' "$X/idea4_hdr64/out/log_$m.txt" && echo "idea4 $m all_done $(date -u +%H:%M:%S)" || echo "idea4 $m FAILED $(date -u +%H:%M:%S)"
done
echo "IDEA4_END $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"; echo IDEA4_DONE $(date -u +%H:%M:%S)
