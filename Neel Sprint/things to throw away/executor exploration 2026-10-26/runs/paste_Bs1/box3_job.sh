#!/bin/bash
# paste_Bs1 on box 3: 018 checked merge of B s1 (parent = HF copy at 6a9e13bd in /root/hfparent), then the b_routing GPU pass (copied code) on s100.
D="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/paste_Bs1"
export PARENT_DIR=/root/hfparent
n=hd-B_s1; AD="/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final"
if [ ! -f /root/merged_sw001/$n/merge_report.json ]; then
  echo "=== merge $n $(date -u +%H:%M:%S)"; mkdir -p /root/merge_tmp /root/merged_sw001
  taskset -c 0-87 /root/venvs/si/bin/python "$D/merge_b3.py" $PARENT_DIR "$AD" /root/merge_tmp/$n.partial \
    && /root/venvs/si/bin/python -c "import json;r=json.load(open('/root/merge_tmp/$n.partial/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print({k:r[k] for k in ('merged','untouched_identical','max_rel_resid')})" \
    && mv /root/merge_tmp/$n.partial /root/merged_sw001/$n && echo "MERGED $n $(date -u +%H:%M:%S)" || { echo "MERGE_FAILED $n"; exit 1; }
fi
cp /root/merged_sw001/$n/merge_report.json "$D/out/merge_report_B_s1.json"
cd "$D" && ONLY_S100=1 FAST=1 ./run_models.sh B_s1:100
echo "JOB_DONE $(date -u +%H:%M:%S)"
