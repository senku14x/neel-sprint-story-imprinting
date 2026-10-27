#!/bin/bash
# Verify fork GPU chain B (V1's new recipients), after chain A ends. One engine at a time.
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"
G="$V/gpu_log.txt"
until grep -q "CHAIN_A END" "$G"; do sleep 20; done
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
run(){ item=$1; m=$2; p=$3; lg=$4; shift 4
  sleep 10; waitgpu || { echo "GPU busy before $item $m" | tee -a "$G"; return 1; }
  echo "$item $m START $(date -u +%H:%M:%S)" >> "$G"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python "$@" > "$lg" 2>&1
  if grep -q '"event": "all_done"' "$lg"; then echo "$item $m END $(date -u +%H:%M:%S) all_done" >> "$G"; else echo "$item $m END $(date -u +%H:%M:%S) FAILED" >> "$G"; fi
}
echo "CHAIN_B START $(date -u +%H:%M:%S)" >> "$G"
cd "$V/v1_transplant"
B0=/root/runs/explore1026/b_routing/B_s0_hdr.pt
run V1 o011 /root/merged_sw001/orig011-B_s0 out/log_B_s0_to_o011.txt run_v1.py --model o011 --donor B_s0=$B0 --tag B_s0_to_o011 --layers 32,40,48 --salts orig
run V1 hs_B /root/merged_sw001/hs-B_s0 out/log_B_s0_to_hs_B.txt run_v1.py --model hs_B --donor B_s0=$B0 --tag B_s0_to_hs_B --layers 32,40,48 --salts orig
run V1 B_s0 /root/merged_sw001/hd-B_s0 out/log_o011_to_B_s0.txt run_v1.py --model B_s0 --donor o011=/workspace/runs_executor/explore1027/verify/v1/B_s0_to_o011_recipient_hdr.pt --tag o011_to_B_s0 --layers 32,40,48 --salts orig
echo "CHAIN_B END $(date -u +%H:%M:%S)" >> "$G"
exit 0
