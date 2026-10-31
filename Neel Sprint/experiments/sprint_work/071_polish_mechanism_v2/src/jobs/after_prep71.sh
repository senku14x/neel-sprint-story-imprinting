#!/bin/bash
# sw071 (node): start <job script> on <gpu> for <m> only after that GPU's prep chain has exited (its parent capture may still hold the
# GPU: never two model-holding processes on one GPU) and the frozen scales file exists. Usage: bash after_prep71.sh <gpu> <m> <job.sh>
set -uo pipefail
GPU=$1; M=$2; JOB=$3
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; RUN=/root/runs/sw071
until grep -q PREP71_EXIT $RUN/prep_$M.wrap 2>/dev/null && [ -e "$SRC/scales71.json" ]; do sleep 10; done
echo "prep exited, scales present $(date -u +%T); starting $JOB"
exec bash "$SRC/jobs/$JOB" $GPU $M
