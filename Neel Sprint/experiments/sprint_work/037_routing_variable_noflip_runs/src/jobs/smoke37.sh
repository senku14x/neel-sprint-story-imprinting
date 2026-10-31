#!/bin/bash
# sw037 Part 1 smoke (run agent, E2). On the node:  nohup bash smoke37.sh <tag> <gpu> <m1,m2> '<mem_probe spec>' > log 2>&1 < /dev/null &
# gates (G1 + G3, sw028 tolerances) -> memory probe -> 4 scripts x both directions x fbtw (2 samples) + free (1 sample) -> output gates per
# organism (size reported only at n = 4) + this path's measured tolerance floors -> /root/runs/sw037/calib_<tag>.json
set -uo pipefail
TAG=$1; GPU=$2; MODELS=$3; MP=$4
SRC="/workspace/Neel Sprint/experiments/sprint_work/037_routing_variable_noflip_runs/src"; RUN=/root/runs/sw037; OUT=$RUN/smoke
SIDS=backyard_bbq_bash_05,bathroom_tile_choice_02,puppy_diet_concerns_01,weekend_rome_escape_03
mkdir -p $OUT
MPA=""; [ -n "$MP" ] && MPA="--mem_probe $MP"
bash "$SRC/jobs/run_node.sh" smoke_$TAG $GPU gen37.py --models $MODELS --mode gen --readout fbtw,free --directions rev,fwd --sids $SIDS \
  --gates --scales "$SRC/scales37.json" --run_dir $OUT --gates_out $OUT $MPA || { echo "smoke gen failed"; exit 3; }
cd "$SRC"; rm -f $RUN/calib_$TAG.json; ok=1
for M in ${MODELS//,/ }; do
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python check37.py $OUT --model $M --readouts fbtw,free --directions rev,fwd --sids $SIDS \
    --gates_json $OUT/gates_$M.json --write_calib $RUN/calib_$TAG.json --out $OUT/output_gates_$M.json > $RUN/logs/smoke_check_$M.log 2>&1 || ok=0
done
[ $ok = 1 ] && touch $OUT/SMOKE_OK_$TAG && echo SMOKE_OK_$TAG || { echo "smoke output gates failed"; exit 4; }
