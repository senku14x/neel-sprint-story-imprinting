#!/bin/bash
# Box 4 GPU 0 queue (fork owning GPU 0): wait for the Track E merge chain, then Track E per model (parent first: it writes the
# histories), then Track G for B s1's step025/062/125/188 with the coordinator's run_ckpt.sh. One engine at a time; CPUs 0-43.
E="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackE"
G="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG"
until grep -qE "CHAIN_DONE|MERGE_FAILED" "$E/out/merge_chain.log"; do sleep 20; done
grep -q MERGE_FAILED "$E/out/merge_chain.log" && echo "merge chain failed; continuing with whatever merged"
waitfree() { for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
for m in parent B_s0 B_s1 A_s0 A_s1 ctrl_B; do
  waitfree || { echo "GPU 0 busy, stop"; exit 1; }
  extra=""; [ $m = parent ] && extra="--gen_hist"
  echo "=== E $m $(date -u +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-43 \
    /root/venvs/vlfix/bin/python "$E/run_e.py" --model $m $extra > "$E/out/log_$m.txt" 2>&1
  grep -q '"event": "all_done"' "$E/out/log_$m.txt" && echo "E_OK $m $(date -u +%H:%M:%S)" || echo "E_FAIL $m $(date -u +%H:%M:%S)"
  [ $m = parent ] && ! grep -q '"event": "all_done"' "$E/out/log_parent.txt" && { echo "parent failed: no histories, stop"; exit 1; }
  sleep 15
done
echo "TRACK_E_GPU_DONE $(date -u +%H:%M:%S)"
for st in step025 step062 step125 step188; do
  waitfree || { echo "GPU 0 busy, stop"; exit 1; }
  bash "$G/run_ckpt.sh" hd-B_s1_$st "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/$st" 0 0-43 100
  echo "G_RC $st $? $(date -u +%H:%M:%S)"; sleep 15
done
echo "QUEUE_DONE $(date -u +%H:%M:%S)"
