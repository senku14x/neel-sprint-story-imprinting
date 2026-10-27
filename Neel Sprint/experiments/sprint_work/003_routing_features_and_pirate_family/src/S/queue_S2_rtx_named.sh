#!/bin/bash
# D22 (RTX): after B s0's S1 is stopped cleanly, S2 for B_s0, ctrl_B, parent (named arms only; nulls off), each model whole on this box.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
PY=/root/venvs/vlfix/bin/python; SI=/root/venvs/si/bin/python
while ! grep -qE "STOPPED_BEFORE_A|expected one" /root/runs/sw003/stop_before_A.log; do sleep 30; done
grep -q STOPPED_BEFORE_A /root/runs/sw003/stop_before_A.log || { echo "RTX stop failed; S2 not started"; exit 1; }
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
run(){ waitgpu || exit 1; echo "=== $* $(date -u +%H:%M:%S)"; "$PY" "$@" > "logs/rtx_$(echo "$*" | tr ' /:' '___' | cut -c1-80).log" 2>&1; rc=$?; echo "rc=$rc $(date -u +%H:%M:%S)"; [ $rc -eq 0 ] || exit $rc; }
cd "$H"
if [ ! -f /root/merged_sw001/ctrl-B_s0/merge_report.json ]; then waitgpu || exit 1
  "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" ctrl-B_s0 "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/partner_ctrl/ctrl_B_s0/final" 0 > logs/rtx_merge_ctrl-B_s0.log 2>&1 || { echo MERGE_FAILED; exit 1; }
  ( cd /root/merged_sw001/ctrl-B_s0 && sha256sum *.safetensors ) > out/sha256_ctrl-B_s0_rtx.txt; fi
for M in B_s0 ctrl_B parent; do
  ls out | grep -q "^gen_S2_${M}.jsonl" && { echo "gen_S2_$M exists; refusing to mix boxes"; exit 1; }
  run capture_nat.py --mode s2 --model $M --layers 32
  $SI doses.py s2 $M | tee -a out/doses_s2_summary_rtx.txt
  run run_S2.py --model $M --nulls off
  $SI check_hook_smoke.py out/hookcheck_S2_$M.json || echo "HOOK_CHECK_S2_${M}_FAILED"
done
echo "S2_RTX_DONE $(date -u +%H:%M:%S)"
exit 0
