#!/bin/bash
# RTX lane after Gate 0: Part J validation generations + probe control (parent), only if both gates pass.
S="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src"
while ! grep -q GATE0_DONE /root/runs/sw003/gate0.log; do sleep 30; done
python3 "$S/gate0/check_gates.py" || { echo "GATES_FAILED: lane stopped $(date -u +%H:%M:%S)"; exit 1; }
sleep 20
echo "=== J gen $(date -u +%H:%M:%S)"
cd "$S/J" && VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 /root/venvs/vlfix/bin/python gen_validation.py > out_gen.log 2>&1
echo "J gen rc=$? $(date -u +%H:%M:%S)"
exit 0
