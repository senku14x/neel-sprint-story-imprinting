#!/bin/bash
X="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration"
until grep -q IDEA4_DONE "$X/chain4.log" 2>/dev/null; do pgrep -f "2026-10-27_exploration/run_idea4.sh" >/dev/null || break; sleep 30; done
for i in $(seq 1 60); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
sleep 15; echo "IDEA3_CTRL_START $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"
MODEL_NAME=B_s0 MODEL_PATH=/root/merged_sw001/hd-B_s0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
  /root/venvs/vlfix/bin/python "$X/idea3_story_switch/run_story_rand.py" --model B_s0 > "$X/idea3_story_switch/out/log_rand_B_s0.txt" 2>&1
grep -q '"event": "all_done"' "$X/idea3_story_switch/out/log_rand_B_s0.txt" && echo "idea3 ctrl all_done $(date -u +%H:%M:%S)" || echo "idea3 ctrl FAILED $(date -u +%H:%M:%S)"
cd "$X/idea3_story_switch" && taskset -c 0-87 /root/venvs/si/bin/python analyze_story.py rand_B_s0 > out/analysis_rand_B_s0.txt 2>&1
echo "IDEA3_CTRL_END $(date -u +%H:%M:%S)" >> "$X/gpu_log.txt"; echo IDEA3_CTRL_DONE
