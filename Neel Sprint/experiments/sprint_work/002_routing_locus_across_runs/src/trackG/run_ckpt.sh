#!/bin/bash
# sw002 Track G: one checkpoint = 018-checked merge -> b_routing-derived pass (default + dis+pro cells, s100, header capture
# L32/40/48, log-odds b1/b2, L40 'same' header copy if P2N>0) -> delete merged weights (keep merge_report).
# usage: run_ckpt.sh <name> <adapter_dir> <gpu> <cpus> <p2n: 100 for B models, 0 for A>
set -u
n=$1; ad=$2; g=$3; cpus=$4; p2n=$5
G="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG"
mkdir -p "$G/out"
echo "=== $n merge $(date -u +%H:%M:%S)"
taskset -c $cpus "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" "$n" "$ad" $g || { echo "MERGE_FAILED $n"; exit 1; }
cp /root/merged_sw001/$n/merge_report.json "$G/out/merge_report_$n.json"
for i in $(seq 1 60); do u=$(nvidia-smi -i $g --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
echo "=== $n gpu pass $(date -u +%H:%M:%S)"
CUDA_VISIBLE_DEVICES=$g MODEL_NAME=$n MODEL_PATH=/root/merged_sw001/$n PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
  taskset -c $cpus /root/venvs/vlfix/bin/python "$G/run_gpu.py" --model "$n" --p2n $p2n > "$G/out/log_$n.txt" 2>&1
rc=$?
grep -q '"event": "all_done"' "$G/out/log_$n.txt" && ok=1 || ok=0
echo "=== $n rc=$rc all_done=$ok $(date -u +%H:%M:%S)"
[ $ok = 1 ] && rm -rf /root/merged_sw001/$n/*.safetensors
[ $ok = 1 ]
