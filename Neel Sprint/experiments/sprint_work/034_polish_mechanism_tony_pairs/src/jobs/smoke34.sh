#!/bin/bash
# sw034 smoke on one GPU (prep agent, E2): inline gates (G1, G3 known answers) -> memory probe (first organism: forced 70 / 100 rows,
# free 50 rows forced to 2,048 tokens, at the longest REG contexts) -> 8 REG + 8 COND pairs x {ind, rem} x 1 sample per organism,
# fbtw + free -> output gates per organism (+ calib from the measured worst errors).
#   nohup bash smoke34.sh <gpu> <m1,m2> > /root/runs/sw034/smoke_g<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; MODELS=$2; TAG=g$GPU
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034; SM=$RUN/smoke
bash "$SRC/jobs/run_node.sh" smoke_$TAG $GPU gen34.py --models $MODELS --mode gen --readout fbtw,free --npairs 8 --samples 1 --gates \
  --mem_probe "fbtw:70,100;free:50" --run_dir $SM --batch_rows 50 --forced_batch_rows 70 || { echo "smoke failed"; exit 5; }
ok=1
for m in ${MODELS//,/ }; do
  cd "$SRC" && OMP_NUM_THREADS=4 /root/venvs/si/bin/python check34.py $SM --model $m --readouts fbtw,free --npairs 8 --samples 1 \
    --out $SM/output_gates_$m.json --write_calib $SM/calib_$m.json >> $RUN/logs/smoke_check_$TAG.log 2>&1 || ok=0
done
[ $ok = 1 ] || { echo "smoke output gates failed"; exit 6; }
touch $SM/SMOKE_GATES_OK_$TAG; echo SMOKE_GATES_OK_$TAG
