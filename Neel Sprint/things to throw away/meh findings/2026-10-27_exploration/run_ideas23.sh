#!/bin/bash
# Ideas 2 and 3 on box 1 GPU 0, after idea 1's chain ends. One engine at a time.
X="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration"
until grep -q IDEA1_DONE "$X/idea1_cross_run_transplant/out/chain.log" 2>/dev/null; do
  pgrep -f "idea1_cross_run_transplant/run_idea1.sh" >/dev/null || { grep -q IDEA1_DONE "$X/idea1_cross_run_transplant/out/chain.log" || echo "idea1 chain ended without IDEA1_DONE"; break; }
  sleep 30; done
waitgpu(){ for i in $(seq 1 60); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
echo "IDEA2_START $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"
for spec in "B_s0|/root/merged_sw001/hd-B_s0|full" "B_s1|/root/merged_sw001/hd-B_s1|full" "ctrl_B|/root/merged_sw001/ctrl-B_s0|quiet" "parent|/dev/shm/qwen36_27b|quiet"; do
  IFS='|' read m p mode <<< "$spec"; sleep 15; waitgpu || { echo GPU busy; exit 1; }
  echo "=== idea2 $m $(date -u +%H:%M:%S)"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python "$X/idea2_H_dose_sweep/run_h2.py" --model $m --mode $mode > "$X/idea2_H_dose_sweep/out/log_$m.txt" 2>&1
  grep -q '"event": "all_done"' "$X/idea2_H_dose_sweep/out/log_$m.txt" && echo "idea2 $m all_done $(date -u +%H:%M:%S)" || echo "idea2 $m FAILED $(date -u +%H:%M:%S)"
done
echo "IDEA2_END $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"
echo "IDEA3_START $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"; sleep 15; waitgpu || exit 1
MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
  /root/venvs/vlfix/bin/python "$X/idea3_story_switch/run_story.py" --model B_s0 > "$X/idea3_story_switch/out/log_B_s0.txt" 2>&1
grep -q '"event": "all_done"' "$X/idea3_story_switch/out/log_B_s0.txt" && echo "idea3 all_done $(date -u +%H:%M:%S)" || echo "idea3 FAILED $(date -u +%H:%M:%S)"
echo "IDEA3_END $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"
echo IDEAS23_DONE $(date -u +%H:%M:%S)
