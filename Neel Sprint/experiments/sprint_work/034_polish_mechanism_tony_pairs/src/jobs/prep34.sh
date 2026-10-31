#!/bin/bash
# sw034 prep on one GPU (prep agent, E2): captures of the GPU's organisms (one process) -> their directions (node CPU, <= 16 threads)
# -> clamp-scale calibration (prefill only). Stops there; scales are frozen on box 1 before the smoke.
#   nohup bash prep34.sh <gpu> <m1,m2> > /root/runs/sw034/prep_g<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; MODELS=$2; TAG=g$GPU
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
bash "$SRC/jobs/run_node.sh" cap_$TAG $GPU cap34.py --models $MODELS || { echo "capture failed"; exit 3; }
cd "$SRC" && OMP_NUM_THREADS=16 taskset -c $CPUS /root/venvs/si/bin/python dirs34.py --models $MODELS > $RUN/logs/dirs_$TAG.log 2>&1 || { echo "dirs failed"; exit 4; }
bash "$SRC/jobs/run_node.sh" cal_$TAG $GPU gen34.py --models $MODELS --mode cal --run_dir $RUN || { echo "calibration failed"; exit 5; }
touch $RUN/PREP_DONE_$TAG; echo PREP_DONE_$TAG
