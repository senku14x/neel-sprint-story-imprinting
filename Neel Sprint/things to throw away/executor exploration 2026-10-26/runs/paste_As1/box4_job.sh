#!/bin/bash
# paste_As1 on box 4 GPU 0: (1) parent parity vs box 1 (sw001 lo200), (2) 018 checked merge of A s1, (3) b_routing GPU pass (copied code) on s100.
export CUDA_VISIBLE_DEVICES=0; unset SW001_BOX
CPUS=0-43   # GPU 0's NUMA node is 0 (CPUs 0-87, shared with the GPU 1 agent); this run takes the lower half
D="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/paste_As1"
SW="/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
echo "=== start $(date -u +%H:%M:%S) $(hostname)"
if ! grep -q '^PASS' "$D/PARITY.txt" 2>/dev/null; then
  rm -f "$D/out/parity_lo200_parent.jsonl"
  cd "$SW" && PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c $CPUS /root/venvs/vlfix/bin/python worker_sw.py \
     --engine lens --model parent --jobs "$D/out/parity_job.json" > "$D/out/log_parity.txt" 2>&1 \
     || { echo "FAIL parity run crashed (see out/log_parity.txt)" > "$D/PARITY.txt"; echo PARITY_RUN_FAILED; exit 1; }
  taskset -c $CPUS /root/venvs/si/bin/python "$D/parity_compare.py" "$D/out/ref_box1_lo200.jsonl" || { echo PARITY_FAILED; exit 1; }
  echo "PARITY_DONE $(date -u +%H:%M:%S)"
  sleep 15
fi
n=hd-A_s1; AD="/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/final"
cd "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
if [ ! -f /root/merged_sw001/$n/merge_report.json ]; then
  echo "=== merge $n $(date -u +%H:%M:%S)"
  taskset -c $CPUS /root/venvs/si/bin/python merge_check018.py merge --adapter "$AD" --out /root/merged_sw001/$n.partial \
    && /root/venvs/si/bin/python -c "import json;r=json.load(open('/root/merged_sw001/$n.partial/merge_report.json'));assert r['merged']==496 and r['untouched_identical'] and r['max_rel_resid']<0.01,r;print({k:r[k] for k in ('merged','untouched_identical','max_rel_resid')})" \
    && mv /root/merged_sw001/$n.partial /root/merged_sw001/$n && echo "MERGED $n $(date -u +%H:%M:%S)" || { echo "MERGE_FAILED $n"; exit 1; }
  sleep 15
fi
cp /root/merged_sw001/$n/merge_report.json "$D/out/merge_report_A_s1.json"
cd "$D" && ONLY_S100=1 ./run_models.sh A_s1:100
echo "JOB_DONE rc=$? $(date -u +%H:%M:%S)"
