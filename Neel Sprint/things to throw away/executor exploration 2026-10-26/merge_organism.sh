#!/bin/bash
# Merge one organism's LoRA into the parent on THIS box (any box on the shared /workspace), with 018's checks.
# usage: merge_organism.sh <name> <adapter_dir> [gpu]   e.g. merge_organism.sh hd-B_s1 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final" 0
# needs: parent at /dev/shm/qwen36_27b (copy from /workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/ with cp -L),
#        /root/venvs/si. Output: /root/merged_sw001/<name> (local disk; ~5 min on an H200; never copy merged weights over the volume: ~35 min each).
set -e
n=$1; ad=$2; g=${3:-0}
[ -f /root/merged_sw001/$n/merge_report.json ] && { echo "already merged: /root/merged_sw001/$n"; exit 0; }
mkdir -p /root/merged_sw001
cd "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
CUDA_VISIBLE_DEVICES=$g /root/venvs/si/bin/python merge_check018.py merge --adapter "$ad" --out /root/merged_sw001/$n.partial
/root/venvs/si/bin/python -c "import json;r=json.load(open('/root/merged_sw001/$n.partial/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print('merge checks pass',r['max_rel_resid'])"
mv /root/merged_sw001/$n.partial /root/merged_sw001/$n && echo "MERGED /root/merged_sw001/$n"
