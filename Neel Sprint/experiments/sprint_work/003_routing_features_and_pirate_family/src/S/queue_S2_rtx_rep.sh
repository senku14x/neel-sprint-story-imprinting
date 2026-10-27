#!/bin/bash
# D25 (RTX): after the named-arm S2 models, S2 for rep_A and rep_B with full nulls, each model whole on this box.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
PY=/root/venvs/vlfix/bin/python; SI=/root/venvs/si/bin/python
while ! grep -qE "S2_RTX_DONE|refusing|failed|FAILED|GPU busy|rc=[1-9]" /root/runs/sw003/queue_S2_rtx.log; do sleep 30; done
grep -q S2_RTX_DONE /root/runs/sw003/queue_S2_rtx.log || { echo "named-arm S2 did not finish; rep S2 not started"; exit 1; }
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
run(){ waitgpu || exit 1; echo "=== $* $(date -u +%H:%M:%S)"; "$PY" "$@" > "logs/rtx_$(echo "$*" | tr ' /:' '___' | cut -c1-80).log" 2>&1; rc=$?; echo "rc=$rc $(date -u +%H:%M:%S)"; [ $rc -eq 0 ] || exit $rc; }
merge(){ n=$1; ad=$2; [ -f /root/merged_sw001/$n/merge_report.json ] && return 0; waitgpu || exit 1
  "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" $n "$ad" 0 > logs/rtx_merge_$n.log 2>&1 || { echo "MERGE_FAILED $n"; exit 1; }
  ( cd /root/merged_sw001/$n && sha256sum *.safetensors ) > out/sha256_${n}_rtx.txt; }
cd "$H"
merge mix010-A_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final"
merge mix010-B_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final"
for M in rep_A rep_B; do
  ls out | grep -q "^gen_S2_${M}.jsonl" && { echo "gen_S2_$M exists; refusing to mix boxes"; exit 1; }
  run capture_nat.py --mode s2 --model $M --layers 32
  $SI doses.py s2 $M | tee -a out/doses_s2_summary_rtx.txt
  run run_S2.py --model $M --nulls on
  $SI check_hook_smoke.py out/hookcheck_S2_$M.json || echo "HOOK_CHECK_S2_${M}_FAILED"
done
echo "S2_RTX_REP_DONE $(date -u +%H:%M:%S)"
exit 0
