#!/bin/bash
# V4 (user follow-up; GPU cap lifted): cross-assignment transplants and multi-layer paste into the parent, after chain F.
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"; W="$V/v4_cross_assignment"; G="$V/gpu_log.txt"
until grep -q "CHAIN_F END" "$G"; do sleep 20; done
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
run(){ item=$1; m=$2; p=$3; lg=$4; shift 4
  sleep 10; waitgpu || { echo "GPU busy before $item $m" >> "$G"; return 1; }
  echo "$item $m START $(date -u +%H:%M:%S)" >> "$G"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python "$@" > "$lg" 2>&1
  if grep -q '"event": "all_done"' "$lg"; then echo "$item $m END $(date -u +%H:%M:%S) all_done" >> "$G"; else echo "$item $m END $(date -u +%H:%M:%S) FAILED" >> "$G"; fi
}
echo "CHAIN_G START $(date -u +%H:%M:%S) (V4; GPU cap lifted by the user)" >> "$G"
cd "$W"
B0=/root/runs/explore1026/b_routing/B_s0_hdr.pt
A0=/workspace/runs_executor/explore1027/verify/v4/B_s0_to_A_s0_recipient_hdr.pt
run V4 A_s0 /root/runs/merged/hd-A_s0 out/log_B_s0_to_A_s0.txt run_v4x.py --model A_s0 --donor B_s0=$B0 --tag B_s0_to_A_s0 --layers 32,40,48 --salts orig
run V4 B_s1 /root/merged_sw001/hd-B_s1 out/log_A_s0_to_B_s1.txt run_v4x.py --model B_s1 --donor A_s0=$A0 --tag A_s0_to_B_s1 --layers 32,40,48 --salts orig
run V4 B_s0 /root/merged_sw001/hd-B_s0 out/log_A_s0_to_B_s0.txt run_v4x.py --model B_s0 --donor A_s0=$A0 --tag A_s0_to_B_s0 --layers 32,40,48 --salts orig
run V4 parent /dev/shm/qwen36_27b out/log_B_s0_to_parent_multilayer.txt run_v4ml.py
echo "CHAIN_G END $(date -u +%H:%M:%S)" >> "$G"
exit 0
