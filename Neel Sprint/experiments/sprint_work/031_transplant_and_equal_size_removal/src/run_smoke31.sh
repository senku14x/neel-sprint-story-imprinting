#!/bin/bash
# sw031 smoke on the node, GPU 3 only (socket 1). Requires src/scales31.json (the frozen calibration, DECISIONS).
#   nohup bash run_smoke31.sh > /root/runs/sw031/smoke/smoke.log 2>&1 < /dev/null &
# 1) one model load: G1 on every capture + G3A/G3B known answers, the memory sizing test at the full run's batch shapes on
#    the longest contexts (forced to 2,048 tokens), then Part A (free, btw, raf) and Part B on 4 scripts, 1 sample;
# 2) the output gates (smoke_check31). Writes SMOKE_GATES_OK only if both pass. SMOKE_OK is touched by hand after reading.
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/031_transplant_and_equal_size_removal/src"
RUN=/root/runs/sw031/smoke
SIDS=ho_family_dinner_prep_18,backyard_bbq_bash_05,puppy_diet_concerns_01,ho_weekend_rome_escape_17
GS=backyard_bbq_bash_05,puppy_diet_concerns_01
export CUDA_VISIBLE_DEVICES=3 PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
TS="taskset -c 56-111,168-223"
cd "$SRC" || exit 1
mkdir -p $RUN
$TS python gen31.py --part size,A,B --readouts free,btw,raf --gates --sids $SIDS --gate_sids $GS --samples 1 --size_samples 2 \
    --scales scales31.json --run_dir $RUN --job smoke "$@" || { echo SMOKE_GEN_FAILED; exit 1; }
$TS python smoke_check31.py $RUN --parts A,B --readouts free,btw,raf --sids $SIDS --samples 1 --gates_json $RUN/gates_smoke.json \
    --soft_habit --out $RUN/smoke_check.json || { echo SMOKE_CHECK_FAILED; exit 1; }
touch $RUN/SMOKE_GATES_OK
echo SMOKE_DONE
