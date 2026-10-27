#!/bin/bash
# Verify fork GPU chain for V3 then V2 (box 1, GPU 0, one engine at a time). GPU times -> gpu_log.txt.
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"
G="$V/gpu_log.txt"
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
run(){ # item model path logfile script args...
  item=$1; m=$2; p=$3; lg=$4; shift 4
  sleep 10; waitgpu || { echo "GPU busy before $item $m" | tee -a "$G"; return 1; }
  echo "$item $m START $(date -u +%H:%M:%S)" >> "$G"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python "$@" > "$lg" 2>&1
  if grep -q '"event": "all_done"' "$lg"; then echo "$item $m END $(date -u +%H:%M:%S) all_done" >> "$G"; else echo "$item $m END $(date -u +%H:%M:%S) FAILED" >> "$G"; fi
}
echo "CHAIN_A START $(date -u +%H:%M:%S) (first GPU job of the verify fork = GPU budget clock start)" >> "$G"
cd "$V/v3_story"
run V3 B_s0 /root/merged_sw001/hd-B_s0 out/log_B_s0.txt run_v3.py --model B_s0 --sets Bho,orig
run V3 parent /dev/shm/qwen36_27b out/log_parent.txt run_v3.py --model parent --sets Bho,Aho
run V3 A_s0 /root/runs/merged/hd-A_s0 out/log_A_s0.txt run_v3.py --model A_s0 --sets Aho
cd "$V/v2_minusH"
run V2 B_s0 /root/merged_sw001/hd-B_s0 out/log_B_s0.txt run_v2.py --model B_s0 --ctx dis --grid full --long 1
run V2 B_s1 /root/merged_sw001/hd-B_s1 out/log_B_s1.txt run_v2.py --model B_s1 --ctx dis --grid full --long 1
run V2 A_s0 /root/runs/merged/hd-A_s0 out/log_A_s0.txt run_v2.py --model A_s0 --ctx dis --grid small
run V2 rep_B /root/merged_sw001/mix010-B_s0 out/log_rep_B.txt run_v2.py --model rep_B --ctx dis --grid small
[ -f "$V/chain_v1_premerge.inc" ] && { echo "V1 pre-merge include found $(date -u +%H:%M:%S)" >> "$G"; . "$V/chain_v1_premerge.inc"; cd "$V/v2_minusH"; }
for n in orig011-B_s0 hs-B_s0; do until [ -f /root/merged_sw001/$n/merge_report.json ]; do sleep 30; done; done
echo "merges present $(date -u +%H:%M:%S)" >> "$G"
run V2 o011 /root/merged_sw001/orig011-B_s0 out/log_o011.txt run_v2.py --model o011 --ctx dis --grid small
run V2 hs_B /root/merged_sw001/hs-B_s0 out/log_hs_B.txt run_v2.py --model hs_B --ctx sar --grid small
echo "CHAIN_A END $(date -u +%H:%M:%S)" >> "$G"
exit 0
