#!/bin/bash
# sw029 Part B full run, two organisms per GPU (prep agent, E2): GPU 0 = e08-X,e08-N; GPU 1 = e08-XB,e08-NB (one per part each).
#   nohup bash fullb29.sh <gpu> <models> > /root/runs/sw029/logs/fullb29_<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; MODELS=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/029_leakage_free_directions/src"; RUN=/root/runs/sw029; OUT=$RUN/partB
[ -e $RUN/calib_b.json ] || { echo "no calib_b.json (Part B smoke not done)"; exit 2; }
bash "$SRC/jobs/run_node.sh" fullb_$GPU $GPU gen29b_x.py --models $MODELS --readout free,fbtw,fraf --gates --run_dir $OUT --calib $RUN/calib_b.json \
  --batch_rows 46 --forced_batch_rows 69 || { echo "gen29b failed"; exit 3; }
cd "$SRC"; ok=1
for m in ${MODELS//,/ }; do
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python check29b.py $OUT --model $m --readouts free,fbtw,fraf --calib $RUN/calib_b.json \
    --out $OUT/output_gates_$m.json > $RUN/logs/output_gates_b_$m.log 2>&1 && touch $OUT/GPU_DONE_B_$m || ok=0
done
[ $ok = 1 ] && echo GPU_DONE_B || { echo "output gates failed"; exit 4; }
