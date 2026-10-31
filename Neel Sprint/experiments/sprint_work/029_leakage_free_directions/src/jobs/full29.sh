#!/bin/bash
# sw029 Part A full run, one organism per GPU (prep agent, E2, 31 Oct 2026). Run ON THE NODE, after the orchestrator releases it:
#   nohup bash full29.sh hdA0 0 <batch_units> <forced_batch_units> > /root/runs/sw029/logs/full29_hdA0.wrap 2>&1 < /dev/null &
#   nohup bash full29.sh hdB0 1 <batch_units> <forced_batch_units> > /root/runs/sw029/logs/full29_hdB0.wrap 2>&1 < /dev/null &
# Order inside the job: G1 + G3 gates, free induce (rev, 2 samples), free remove (fwd, 1 sample), fbtw (rev, fwd), fraf (rev, fwd).
# Amendment 3 (01:18 UTC, revising Amendment 2): BOTH forced bridges run, each labelled (fbtw helper-skewed in training; fraf crow-saturated); neither decides.
# Resumable by key (rerun the same command). GPU_DONE_<m> only when check29's output gates pass on the full manifest.
set -uo pipefail
M=$1; GPU=$2; BU=$3; FBU=$4
SRC="/workspace/Neel Sprint/experiments/sprint_work/029_leakage_free_directions/src"
RUN=/root/runs/sw029; OUT=$RUN/full; mkdir -p $OUT
[ -e $RUN/calib.json ] || { echo "no calib.json (smoke output gates not run)"; exit 2; }
bash "$SRC/jobs/run_node.sh" full_$M $GPU gen29_x.py --model $M --readout free,fbtw,fraf --directions rev,fwd --gates \
  --run_dir $OUT --gates_out $OUT --calib $RUN/calib.json --batch_units $BU --forced_batch_units $FBU || { echo "gen29 failed"; exit 3; }
cd "$SRC" && OMP_NUM_THREADS=4 /root/venvs/si/bin/python check29.py $OUT --model $M --readouts free,fbtw,fraf --directions rev,fwd --sids all \
  --gates_json $OUT/gates_$M.json --calib $RUN/calib.json --out $OUT/output_gates_$M.json > $RUN/logs/output_gates_$M.log 2>&1 \
  && touch $OUT/GPU_DONE_$M && echo "GPU_DONE_$M" || { echo "output gates failed"; exit 4; }
