#!/bin/bash
# D33: F2b = F2's design on B s0 L32, on the RTX box (B s0's S1 box; RTX-captured doses). Smoke -> D14 hook gate -> full.
cd "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S1fu"
export VLLM_USE_FLASHINFER_SAMPLER=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8
/root/venvs/vlfix/bin/python run_fu.py --part F2 --model B_s0 --smoke 3 > out/log_F2b_smoke.txt 2>&1; echo "F2b smoke rc=$? $(date -u +%H:%M:%S)"
/root/venvs/si/bin/python ../S/check_hook_smoke.py out/hookcheck_F2b_smoke.json || { echo "HOOK_F2b_SMOKE_FAILED"; exit 1; }
sleep 15
/root/venvs/vlfix/bin/python run_fu.py --part F2 --model B_s0 > out/log_F2b.txt 2>&1; echo "F2b rc=$? $(date -u +%H:%M:%S)"
/root/venvs/si/bin/python ../S/check_hook_smoke.py out/hookcheck_F2b.json || echo "HOOK_F2b_FAILED"
echo "F2b_DONE $(date -u +%H:%M:%S)"
