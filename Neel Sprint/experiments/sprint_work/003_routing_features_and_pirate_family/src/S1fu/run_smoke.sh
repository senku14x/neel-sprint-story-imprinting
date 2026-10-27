#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S1fu"
export VLLM_USE_FLASHINFER_SAMPLER=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8
for P in F1 F2; do
  taskset -c 0-87 /root/venvs/vlfix/bin/python run_fu.py --part $P --smoke 3 > out/log_${P}_smoke.txt 2>&1; echo "$P smoke rc=$? $(date -u +%H:%M:%S)"
  /root/venvs/si/bin/python ../S/check_hook_smoke.py out/hookcheck_${P}_smoke.json
done
echo SMOKE_DONE
