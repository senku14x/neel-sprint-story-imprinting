#!/bin/bash
# sw037 Part 1 full run (run agent, E2). On the node:  nohup bash full37.sh <tag> <gpu> <m1,m2> <readout> <rows> > log 2>&1 < /dev/null &
# gates (G1 + G3 at the full-run tolerances calib_<tag>.json) -> all 64 scripts x rev, fwd -> output gates per organism (size gate on
# all 64 scripts) -> GPU_DONE_p1_<readout>_<m> only when the manifest is complete and every gate passes. Resumable by key.
set -uo pipefail
TAG=$1; GPU=$2; MODELS=$3; RO=$4; ROWS=$5
SRC="/workspace/Neel Sprint/experiments/sprint_work/037_routing_variable_noflip_runs/src"; RUN=/root/runs/sw037; OUT=$RUN/full
mkdir -p $OUT
[ -e $RUN/calib_$TAG.json ] || { echo "no calib_$TAG.json (smoke not run)"; exit 2; }
RA="--forced_batch_rows $ROWS"; [ "$RO" = free ] && RA="--batch_rows $ROWS"
bash "$SRC/jobs/run_node.sh" full_${RO}_$TAG $GPU gen37.py --models $MODELS --mode gen --readout $RO --directions rev,fwd --gates \
  --scales "$SRC/scales37.json" --calib $RUN/calib_$TAG.json --run_dir $OUT --gates_out $OUT/gates_$RO $RA || { echo "gen37 failed"; exit 3; }
cd "$SRC"; ok=1
for M in ${MODELS//,/ }; do
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python check37.py $OUT --model $M --readouts $RO --directions rev,fwd --sids all \
    --gates_json $OUT/gates_$RO/gates_$M.json --calib $RUN/calib_$TAG.json --out $OUT/output_gates_${RO}_$M.json > $RUN/logs/output_gates_${RO}_$M.log 2>&1 \
    && touch $OUT/GPU_DONE_p1_${RO}_$M || ok=0
done
[ $ok = 1 ] && echo "FULL_DONE $RO $MODELS" || { echo "output gates failed"; exit 4; }
