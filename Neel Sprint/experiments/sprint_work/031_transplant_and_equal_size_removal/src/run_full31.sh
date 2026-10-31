#!/bin/bash
# sw031 FULL run on the node, GPU 3 only (socket 1). Held until the orchestrator releases it (SMOKE_OK).
#   nohup bash run_full31.sh > /root/runs/sw031/full/full.log 2>&1 < /dev/null &
# Three model loads in sequence (each re-runs G1 on its captures + G3 known answers inline; resume by key on a rerun):
#   1) Part B free (2,560)   2) Part A free (primary, 4,608 replies)   3) Part A forced pilot, both bridges btw + raf (2 x 2,304, 48 tokens)
#   (order: Amendment 4; bridges: Amendment 3)
# After each: the output gates (smoke_check31, per model, full manifest) -> output_gates_<job>.json; a failure stops the script.
# GPU_DONE_<part>_<readout> is written by gen31 only when the rows equal the manifest. ALL_GPU_DONE at the end.
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/031_transplant_and_equal_size_removal/src"
RUN=/root/runs/sw031/full
GS=backyard_bbq_bash_05,puppy_diet_concerns_01
BG_A=${BG_A:-3}; BG_B=${BG_B:-3}; BG_F=${BG_F:-8}     # batch groups (rows: A free 18/group, B 20/group, forced 9/group); D21 (measured sizing)
export CUDA_VISIBLE_DEVICES=3 PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
TS="taskset -c 56-111,168-223"
cd "$SRC" || exit 1
mkdir -p $RUN
test -e /root/runs/sw031/smoke/SMOKE_OK || { echo "NO SMOKE_OK: not released"; exit 2; }
COMMON="--gates --gate_sids $GS --scales scales31.json --run_dir $RUN --samples 2 --batch_groups_A $BG_A --batch_groups_B $BG_B --forced_batch_groups $BG_F"
$TS python gen31.py --part B $COMMON --job B_free || { echo FAILED_B_free; exit 1; }
$TS python smoke_check31.py $RUN --parts B --samples 2 --gates_json $RUN/gates_B_free.json --out $RUN/output_gates_B_free.json || { echo GATES_FAILED_B_free; exit 1; }
$TS python gen31.py --part A --readouts free $COMMON --job A_free || { echo FAILED_A_free; exit 1; }
$TS python smoke_check31.py $RUN --parts A --readouts free --samples 2 --gates_json $RUN/gates_A_free.json --out $RUN/output_gates_A_free.json || { echo GATES_FAILED_A_free; exit 1; }
$TS python gen31.py --part A --readouts btw,raf $COMMON --job A_forced || { echo FAILED_A_forced; exit 1; }
$TS python smoke_check31.py $RUN --parts A --readouts btw,raf --samples 1 --gates_json $RUN/gates_A_forced.json --out $RUN/output_gates_A_forced.json || { echo GATES_FAILED_A_forced; exit 1; }
touch $RUN/ALL_GPU_DONE
echo FULL_DONE
