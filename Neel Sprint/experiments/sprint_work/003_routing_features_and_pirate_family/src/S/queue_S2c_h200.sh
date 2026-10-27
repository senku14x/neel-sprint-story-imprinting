#!/bin/bash
# D22 (H200): after A s0's S1, S2 for rep_A and rep_B with full nulls, each model whole on this box.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
PY=/root/venvs/vlfix/bin/python; SI=/root/venvs/si/bin/python
while ! grep -qE "S1A_DONE|refusing|GPU busy|rc=[1-9]" /root/runs/sw003/queue_S1A.log; do sleep 60; done
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
run(){ waitgpu || exit 1; echo "=== $* $(date -u +%H:%M:%S)"; taskset -c 0-87 "$PY" "$@" > "logs/h200_$(echo "$*" | tr ' /:' '___' | cut -c1-80).log" 2>&1; rc=$?; echo "rc=$rc $(date -u +%H:%M:%S)"; [ $rc -eq 0 ] || exit $rc; }
cd "$H"
for M in rep_A rep_B; do
  ls out | grep -q "^gen_S2_${M}.jsonl" && { echo "gen_S2_$M exists; refusing"; exit 1; }
  run capture_nat.py --mode s2 --model $M --layers 32
  $SI doses.py s2 $M | tee -a out/doses_s2_summary_h200.txt
  run run_S2.py --model $M --nulls on
  $SI check_hook_smoke.py out/hookcheck_S2_$M.json || echo "HOOK_CHECK_S2_${M}_FAILED"
done
echo "S2_H200_DONE $(date -u +%H:%M:%S)"
exit 0
