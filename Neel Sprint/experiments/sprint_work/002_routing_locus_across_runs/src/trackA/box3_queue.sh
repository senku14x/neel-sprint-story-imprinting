#!/bin/bash
# sw002 Track A on box 3 (box-3 fork of executor-6): parity -> B s0 known-answer subset -> B s1 full -> B s2 merge + full.
# Every GPU process: venv bin on PATH, pinned to CPUs 0-87 (GPU 0's NUMA node). One engine at a time.
T="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA"
SW="/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
cd "$T"
echo "=== start $(date -u +%H:%M:%S) $(hostname)"
if ! grep -q '^PASS' out/PARITY_box3.txt 2>/dev/null; then
  rm -f out/parity_lo200_parent_box3.jsonl
  (cd "$SW" && PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_sw.py \
     --engine lens --model parent --jobs "$T/out/parity_job.json") > out/log_parity_box3.txt 2>&1 || { echo PARITY_RUN_FAILED; exit 1; }
  taskset -c 0-87 /root/venvs/si/bin/python parity_compare.py out/ref_box1_lo200.jsonl || { echo PARITY_FAILED; exit 1; }
  echo "PARITY_DONE $(date -u +%H:%M:%S)"; sleep 20
fi
if [ ! -s out/gen_B_s0_ka.jsonl ]; then
  KA=1 TAG_SUFFIX=_ka ./run_models.sh B_s0:50 || { echo KA_RUN_FAILED; exit 1; }
  echo "KA_DONE $(date -u +%H:%M:%S)"; sleep 20
fi
if [ ! -s out/hookcheck_B_s1.json ]; then
  ./run_models.sh B_s1:199 || { echo B_S1_FAILED; exit 1; }
  echo "B_S1_DONE $(date -u +%H:%M:%S)"; sleep 20
fi
n=hd-B_s2
if [ ! -f /root/merged_sw001/$n/merge_report.json ]; then
  echo "=== merge $n $(date -u +%H:%M:%S)"
  PATH=/root/venvs/si/bin:$PATH taskset -c 0-87 "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" $n "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/final" 0 || { echo MERGE_FAILED $n; exit 1; }
  sleep 20
fi
cp /root/merged_sw001/$n/merge_report.json out/merge_report_B_s2.json
cp /root/merged_sw001/hd-B_s1/merge_report.json out/merge_report_B_s1.json; cp /root/merged_sw001/hd-B_s0/merge_report.json out/merge_report_B_s0.json
if [ ! -s out/hookcheck_B_s2.json ]; then
  ./run_models.sh B_s2:199 || { echo B_S2_FAILED; exit 1; }
  echo "B_S2_DONE $(date -u +%H:%M:%S)"; sleep 20
fi
for n in hs-A_s0 hs-B_s0; do
  if [ ! -f /root/merged_sw001/$n/merge_report.json ]; then
    echo "=== merge $n $(date -u +%H:%M:%S)"
    PATH=/root/venvs/si/bin:$PATH taskset -c 0-87 "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" $n "/workspace/Neel Sprint/adapters/qwen36-27b_${n}_cosine/final" 0 || { echo MERGE_FAILED $n; exit 1; }
    sleep 15
  fi
done
echo "QUEUE_DONE $(date -u +%H:%M:%S)"
