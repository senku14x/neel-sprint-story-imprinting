#!/bin/bash
# sw038 Part 0 full run, one organism per GPU (prep-P0 agent, E2). ON THE NODE (after SMOKE_OK_<m>):
#   setsid nohup bash full38p0.sh hdA0 0 <free_batch_units> <forced_batch_units> > /root/runs/sw038/p0/full_hdA0.wrap 2>&1 < /dev/null &
# Inline gates (G1, KA, G1b) -> forced (induce, remove; 2 samples) -> free (induce, remove; 2 samples, 2,048 cap), per-batch known
# answers, OOM halving, resume by key (rerun the same command) -> output gates on the full EXPECTED manifest -> GPU_DONE_p0_<m>.
set -uo pipefail
M=$1; GPU=$2; BU=$3; FBU=$4
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p0"
RUN=/root/runs/sw038/p0; OUT=$RUN/full; mkdir -p $OUT
[ -e $RUN/smoke/SMOKE_OK_$M ] || { echo "no SMOKE_OK_$M"; exit 2; }
bash "$SRC/jobs/run_node38p0.sh" full_$M $GPU $M $OUT gen38p0.py --model $M --readouts forced,free --directions induce,remove --sids all \
  --samples 2 --gates --run_dir $OUT --caps_dir $RUN/caps --batch_units $BU --forced_batch_units $FBU \
  || { echo "gen38p0 failed"; touch $OUT/FAILED_p0_$M; exit 3; }
cd "$SRC" && /root/venvs/si/bin/python check38p0.py $OUT --model $M --readouts forced,free --directions induce,remove --sids all --samples 2 \
  --gates_json $OUT/gates_$M.json --out $OUT/output_gates_$M.json > $OUT/logs/output_gates_$M.log 2>&1 \
  && { touch $RUN/GPU_DONE_p0_$M; echo GPU_DONE_p0_$M; } || { echo "output gates failed"; touch $OUT/FAILED_p0_$M; exit 4; }
