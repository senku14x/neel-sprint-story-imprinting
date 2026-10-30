#!/bin/bash
# sw009 Stage B: after Stage A generation succeeds (GPU free), capture states (runs regardless of the gate, as briefed)
cd "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src"
until grep -qE "gen exit|GEN_FAILED" out/run9.log 2>/dev/null; do sleep 20; done
grep -q GEN_DONE out/gen.log || { echo "STAGE_B_SKIPPED: generation failed"; exit 1; }
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
echo "B start $(date -u +%T)"
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/si/bin/python cap9_x.py > out/capB.log 2>&1
echo "B exit $? $(date -u +%T)"
