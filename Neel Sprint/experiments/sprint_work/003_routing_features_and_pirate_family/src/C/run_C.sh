#!/bin/bash
# sw003 Part C on the RTX box (one command): merge hs A/B -> census (ka check first) on hs_A, hs_B -> RTX parity (parent, B_s0)
# -> R_hs, parity, analysis. Resumable (worker skips done (id, model) rows; merge skips existing merges).
# SMOKE=1 ./run_C.sh : merge hs_A only, ka + 2-role census on hs_A (out/smoke_lo_census.jsonl), then stop.
set -u
G="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C"
M="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh"
A="/workspace/Neel Sprint/adapters"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0   # RTX PRO 6000 (sm_120): FlashInfer sampler kills the engine at start-up (decisions D7)
unset SW001_BOX
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
cd "$G"; [ -f jobs/census.jsonl ] || /root/venvs/si/bin/python run_census_hs.py build
for X in A B; do
  [ "${SMOKE:-0}" = 1 ] && [ $X = B ] && continue
  waitgpu || exit 1
  echo "=== merge hs-${X}_s0 $(date -u +%H:%M:%S)"
  "$M" hs-${X}_s0 "$A/qwen36-27b_hs-${X}_s0_cosine/final" 0 || { echo "MERGE_FAILED $X"; exit 1; }
  cp /root/merged_sw001/hs-${X}_s0/merge_report.json "$G/out/merge_report_hs-${X}_s0.json"
  ( cd /root/merged_sw001/hs-${X}_s0 && sha256sum *.safetensors ) > "$G/out/sha256_hs-${X}_s0.txt"
done
if [ "${SMOKE:-0}" = 1 ]; then
  waitgpu || exit 1
  /root/venvs/vlfix/bin/python run_census_hs.py run --model hs_A --smoke 2 > out/log_smoke_hs_A.txt 2>&1; echo "SMOKE rc=$? $(date -u +%H:%M:%S)"; exit 0
fi
for m in hs_A hs_B parent B_s0; do
  waitgpu || exit 1
  echo "=== $m $(date -u +%H:%M:%S)"
  /root/venvs/vlfix/bin/python run_census_hs.py run --model $m > out/log_$m.txt 2>&1
  rc=$?; echo "rc=$rc $m $(date -u +%H:%M:%S)"
  [ $rc -ne 0 ] && { echo "STOP: $m failed (rc=$rc; 3 = known-answer check failed)"; exit $rc; }
done
P=/root/venvs/si/bin/python; $P compute_R.py hs; $P compare_parity.py; $P analyze_C.py hs > out/analyze_C_hs.txt 2>&1
echo "C_DONE $(date -u +%H:%M:%S)"
exit 0
