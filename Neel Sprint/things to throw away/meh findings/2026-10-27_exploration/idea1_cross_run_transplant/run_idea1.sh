#!/bin/bash
# Idea 1 chain on box 1 GPU 0 (one engine at a time). Waits for the B s1 merge first.
X="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/idea1_cross_run_transplant"
B0=/root/runs/explore1026/b_routing/B_s0_hdr.pt
B1="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA/out/big/B_s1_hdr.pt"
while pgrep -f "merge_check018.py merge --adapter /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1" >/dev/null; do sleep 20; done
python3 -c "import json;r=json.load(open('/root/merged_sw001/hd-B_s1/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print('B s1 merge ok',r['max_rel_resid'])" || { echo "B_s1 merge check FAILED"; exit 1; }
waitgpu(){ for i in $(seq 1 60); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
for spec in "B_s1|/root/merged_sw001/hd-B_s1|B_s0=$B0|B_s0_to_B_s1" "parent|/dev/shm/qwen36_27b|B_s0=$B0|B_s0_to_parent" \
            "rep_B|/root/merged_sw001/mix010-B_s0|B_s0=$B0|B_s0_to_rep_B" "B_s0|/root/merged_sw001/hd-B_s0|B_s1=$B1|B_s1_to_B_s0"; do
  IFS='|' read m p d tag <<< "$spec"
  sleep 15; waitgpu || { echo "GPU busy"; exit 1; }
  echo "=== $tag $(date -u +%H:%M:%S)"
  MODEL_NAME=$m MODEL_PATH=$p PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
    /root/venvs/vlfix/bin/python "$X/run_x.py" --model $m --donor "$d" --tag $tag > "$X/out/log_$tag.txt" 2>&1
  grep -q '"event": "all_done"' "$X/out/log_$tag.txt" && echo "$tag all_done $(date -u +%H:%M:%S)" || echo "$tag FAILED $(date -u +%H:%M:%S)"
  taskset -c 0-87 /root/venvs/si/bin/python "$X/analyze_x.py" $tag > "$X/out/analysis_$tag.txt" 2>&1
done
echo IDEA1_DONE $(date -u +%H:%M:%S)
