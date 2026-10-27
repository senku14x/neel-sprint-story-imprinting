# sourced by chain_a.sh after V2 rep_B (uses its run(), $V, $G): V1's B s1 job, then the two GPU merges (CPU merges abandoned:
# the container has an 18.7-CPU quota and they throttled the GPU jobs).
cd "$V/v1_transplant"
run V1 B_s1 /root/merged_sw001/hd-B_s1 out/log_B_s0_to_B_s1.txt run_v1.py --model B_s1 --donor B_s0=/root/runs/explore1026/b_routing/B_s0_hdr.pt --tag B_s0_to_B_s1 --layers 40 --salts s1,s2
for spec in "orig011-B_s0|/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final" \
            "hs-B_s0|/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/final"; do
  IFS='|' read mn ad <<< "$spec"
  sleep 10; waitgpu || echo "GPU busy before merge $mn" >> "$G"
  echo "MERGE $mn START $(date -u +%H:%M:%S)" >> "$G"
  taskset -c 0-87 "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" "$mn" "$ad" 0 > /workspace/runs_executor/explore1027/verify/merge_gpu_$mn.log 2>&1
  [ -f /root/merged_sw001/$mn/merge_report.json ] && echo "MERGE $mn END $(date -u +%H:%M:%S) ok" >> "$G" || echo "MERGE $mn END $(date -u +%H:%M:%S) FAILED" >> "$G"
done
