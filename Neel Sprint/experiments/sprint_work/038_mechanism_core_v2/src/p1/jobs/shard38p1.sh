#!/bin/bash
# sw038 Part 1 full-run shard = one model x one direction on one GPU (prep-P1 agent, E2, 31 Oct 2026). Run ON THE NODE:
#   setsid nohup bash shard38p1.sh <model> <induce|remove> <gpu> <batch_units> <forced_batch_units> > <log> 2>&1 < /dev/null &
# Order: G1 + G3 gates (gen38p1 --gates), free replies (<= 2,048 tokens; induce 2 samples, remove 1), forced "By the way," + 48
# (1 sample), then check38p1's output gates on the EXPECTED manifest of this shard (rows, keys, non-empty, logs, known answers,
# cumulative gate [0.9, 1.1] at both bands on all 61 scripts). GPU_DONE_p1_<m>_<d> only when check38p1 passes; SHARD_EXIT_p1_<m>_<d>
# (exit codes) always. Resumable by key: rerun the same command.
set -uo pipefail
M=$1; D=$2; GPU=$3; BU=$4; FBU=$5
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1"
RUN=/root/runs/sw038/p1; OUT=$RUN/full; TAG=p1_${M}_${D}; mkdir -p $OUT $OUT/gates_$TAG
echo "$$ $(date -u +%FT%TZ) gpu=$GPU" > $OUT/PID_shard_$TAG
fin() { echo "{\"shard\": \"$TAG\", \"gpu\": $GPU, \"gen_rc\": ${1:-null}, \"check_rc\": ${2:-null}, \"end\": \"$(date -u +%FT%TZ)\"}" > $OUT/SHARD_EXIT_$TAG; }
[ -e $RUN/calib.json ] || { echo "no calib.json (smoke output gates not run)"; fin 2; exit 2; }
[ -e "$SRC/scales38p1.json" ] || { echo "no frozen scales38p1.json"; fin 2; exit 2; }
GS=$(/root/venvs/si/bin/python -c "import json; print(','.join(json.load(open('$RUN/smoke/smoke_sids.json'))[:2]))")
bash "$SRC/jobs/run_node38p1.sh" full_$TAG $GPU gen38p1.py --model $M --readout free,fbtw --directions $D --gates --gate_sids $GS \
  --run_dir $OUT --gates_out $OUT/gates_$TAG --calib $RUN/calib.json --scales "$SRC/scales38p1.json" --batch_units $BU \
  --forced_batch_units $FBU --job full_$TAG
rc=$?
[ $rc = 0 ] || { echo "gen38p1 failed rc=$rc"; fin $rc; exit 3; }
bash "$SRC/jobs/run_node38p1.sh" check_$TAG cpu check38p1.py $OUT --model $M --direction $D --readouts free,fbtw --sids all \
  --gates_json $OUT/gates_$TAG/gates_$M.json --calib $RUN/calib.json --scales "$SRC/scales38p1.json" --out $OUT/output_gates_$TAG.json
rc2=$?
fin 0 $rc2
[ $rc2 = 0 ] && touch $OUT/GPU_DONE_$TAG && echo "GPU_DONE_$TAG" || { echo "output gates failed rc=$rc2"; exit 4; }
