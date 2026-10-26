#!/bin/bash
# org011_tests on box 4, GPU 1, CPUs 44-87 (both GPUs sit on NUMA node 0 = CPUs 0-87; the other half is left to the GPU 0 agent).
# 1) 018 checked merge of the 011 adapter (pilot regen B s0; merge_check018 reads base_model.model.model.layers.* keys directly,
#    the same convention 001's remap_lora_for_vllm.py takes as input, so no remap is needed for a merge);
# 2) b_routing GPU pass (copied code) on the s100 scripts; 3) sw001 Part 2 primary steering cell.
export GPU=1 CPUS=44-87
D="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/org011_tests"
n=pilot_regen_B_s0; AD="/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final"
cd "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
if [ ! -f /root/merged_sw001/$n/merge_report.json ]; then
  echo "=== merge $n $(date -u +%H:%M:%S)"
  CUDA_VISIBLE_DEVICES=$GPU taskset -c $CPUS /root/venvs/si/bin/python merge_check018.py merge --adapter "$AD" --out /root/merged_sw001/$n.partial \
    && /root/venvs/si/bin/python -c "import json;r=json.load(open('/root/merged_sw001/$n.partial/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print({k:r[k] for k in ('merged','untouched_identical','max_rel_resid')})" \
    && mv /root/merged_sw001/$n.partial /root/merged_sw001/$n && echo "MERGED $n $(date -u +%H:%M:%S)" || { echo "MERGE_FAILED $n"; exit 1; }
fi
cp /root/merged_sw001/$n/merge_report.json "$D/out/merge_report_R011.json"
cd "$D" && ONLY_S100=1 ./run_models.sh R011:100 || { echo "BROUTING_FAILED"; }
echo "BROUTING_DONE $(date -u +%H:%M:%S)"
"$D/steer/run_steer.sh"
echo "JOB_DONE $(date -u +%H:%M:%S)"
