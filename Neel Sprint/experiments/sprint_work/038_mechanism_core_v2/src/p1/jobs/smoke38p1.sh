#!/bin/bash
# sw038 Part 1 GPU smoke for one model (prep-P1 agent, E2, 31 Oct 2026). Run ON THE NODE, detached:
#   bash launch38p1.sh <log> smoke38p1.sh <model> <gpu>
# 1. gen38p1: G1 + G3 gates on 2 smoke scripts; the memory probe at the full run's batch shapes on the LONGEST contexts of each
#    direction with every row forced to max_new (free: induce 5 units = 55 rows, remove 4 units = 48 rows; forced: 6 units); then the
#    4 smoke scripts x both directions x every arm x 1 sample, free (2,048) + fbtw (48), at the full run's batch sizes.
# 2. check38p1 per direction: rows / keys / non-empty / logs / known answers (the 4-script cumulative medians are reported, not gated:
#    D-entry), --write_calib -> smoke/calib_<m>_<d>.json. SMOKE_GATES_OK_<m> only if everything passes.
set -uo pipefail
M=$1; GPU=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1"; RUN=/root/runs/sw038/p1; OUT=$RUN/smoke; mkdir -p $OUT
S4=$(/root/venvs/si/bin/python -c "import json; print(','.join(json.load(open('$OUT/smoke_sids.json'))))")
GS=$(/root/venvs/si/bin/python -c "import json; print(','.join(json.load(open('$OUT/smoke_sids.json'))[:2]))")
bash "$SRC/jobs/run_node38p1.sh" smoke_$M $GPU gen38p1.py --model $M --readout free,fbtw --directions induce,remove --sids $S4 --samples 1 \
  --gates --gate_sids $GS --mem_probe "free|induce:5;free|remove:4;fbtw|induce:6;fbtw|remove:6" --run_dir $OUT --gates_out $OUT/gates_$M \
  --scales "$SRC/scales38p1.json" --batch_units 5 --forced_batch_units 6 --job smoke_$M || { echo "smoke gen failed"; touch $OUT/SMOKE_FAILED_$M; exit 3; }
ok=1
for D in induce remove; do
  bash "$SRC/jobs/run_node38p1.sh" smokecheck_${M}_$D cpu check38p1.py $OUT --model $M --direction $D --readouts free,fbtw --sids $S4 --samples 1 \
    --gates_json $OUT/gates_$M/gates_$M.json --scales "$SRC/scales38p1.json" --cum_report_only --out $OUT/output_gates_${M}_$D.json \
    --write_calib $OUT/calib_${M}_$D.json || ok=0
done
[ $ok = 1 ] && touch $OUT/SMOKE_GATES_OK_$M && echo SMOKE_GATES_OK_$M || { echo "smoke output gates failed"; touch $OUT/SMOKE_FAILED_$M; exit 4; }
