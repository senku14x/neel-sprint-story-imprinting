#!/bin/bash
# CPU merges for the verify fork (011 and sarcastic B), sequential, on the CPUs other than the GPU's NUMA node.
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"
for spec in "orig011-B_s0|/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final" \
            "hs-B_s0|/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/final"; do
  IFS='|' read n ad <<< "$spec"
  if [ -f /root/merged_sw001/$n/merge_report.json ]; then echo "already merged $n"; continue; fi
  echo "MERGE_START $n $(date -u +%H:%M:%S)"
  OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python "$V/lib/merge_cpu.py" --adapter "$ad" --out /root/merged_sw001/$n.partial
  /root/venvs/si/bin/python -c "import json;r=json.load(open('/root/merged_sw001/$n.partial/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print('merge checks pass',r)" \
    && mv /root/merged_sw001/$n.partial /root/merged_sw001/$n && echo "MERGED $n $(date -u +%H:%M:%S)" || echo "MERGE_FAILED $n $(date -u +%H:%M:%S)"
done
echo MERGES_DONE $(date -u +%H:%M:%S)
