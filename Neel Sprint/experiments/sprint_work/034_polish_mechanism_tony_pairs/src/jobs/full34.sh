#!/bin/bash
# sw034 Part A full run on one GPU (prep agent, E2; NOT launched by the prep agent: the orchestrator releases it after the user's
# prediction). fbtw (2 samples) then free (1 sample), every REG + COND unit, both directions, every arm; then output gates; then the
# parent floor (Part P, fbtw, induce, real arms, 1 sample). GPU_DONE markers only when the manifest is complete.
#   nohup bash full34.sh <gpu> <m1,m2> > /root/runs/sw034/full_g<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; MODELS=$2; TAG=g$GPU
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034; FD=$RUN/full
CAL=$RUN/calib.json
bash "$SRC/jobs/run_node.sh" full_$TAG $GPU gen34.py --models $MODELS --mode gen --readout fbtw,free --gates --calib $CAL --run_dir $FD \
  --batch_rows ${BR:-50} --forced_batch_rows ${FBR:-70} || { echo "full run failed"; exit 5; }
ok=1
for m in ${MODELS//,/ }; do
  cd "$SRC" && OMP_NUM_THREADS=4 /root/venvs/si/bin/python check34.py $FD --model $m --readouts fbtw,free --calib $CAL \
    --out $FD/output_gates_$m.json >> $RUN/logs/full_check_$TAG.log 2>&1 && touch $FD/GPU_DONE_A_$m || ok=0
done
bash "$SRC/jobs/run_node.sh" parent_$TAG $GPU gen34.py --models $MODELS --mode gen --part P --readout fbtw --calib $CAL --run_dir $RUN/parent \
  --forced_batch_rows ${FBR:-70} && touch $RUN/parent/GPU_DONE_P_$TAG
[ $ok = 1 ] && echo FULL_DONE_$TAG || echo "FULL output gates failed"
