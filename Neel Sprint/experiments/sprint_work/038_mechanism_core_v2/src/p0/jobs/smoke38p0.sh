#!/bin/bash
# sw038 Part 0 smoke, one organism per GPU (prep-P0 agent, E2). ON THE NODE:
#   nohup setsid bash smoke38p0.sh hdA0 0 > /root/runs/sw038/p0/smoke/smoke_hdA0.wrap 2>&1 < /dev/null &
# capture (122 G2 contexts, batch 1; reused by the full run) -> inline gates (G1, KA, G1b) -> 4 scripts from 4 domains, both
# directions, every arm, 1 sample, forced (one batch of 8 units) then free (one batch of 8 units, 2,048 cap), per-batch known
# answers -> memory probe (longest recipient contexts, every row forced to the cap) -> output gates -> SMOKE_OK_<m>.
set -uo pipefail
M=$1; GPU=$2; MEM=${3:-"free:10,12,14;forced:16,24,32"}   # tried largest first, stop at the first fit (D12)
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p0"
OUT=/root/runs/sw038/p0/smoke; mkdir -p $OUT
bash "$SRC/jobs/run_node38p0.sh" smoke_$M $GPU $M $OUT gen38p0.py --model $M --readouts forced,free --directions induce,remove --sids smoke \
  --samples 1 --gates --run_dir $OUT --caps_dir /root/runs/sw038/p0/caps --batch_units 8 --forced_batch_units 8 --mem_probe "$MEM" \
  || { echo "smoke gen failed rc=$?"; touch $OUT/SMOKE_FAILED_$M; exit 3; }
cd "$SRC" && /root/venvs/si/bin/python check38p0.py $OUT --model $M --readouts forced,free --directions induce,remove --sids smoke --samples 1 \
  --gates_json $OUT/gates_$M.json --out $OUT/output_gates_$M.json > $OUT/logs/output_gates_$M.log 2>&1 \
  && { touch $OUT/SMOKE_OK_$M; echo SMOKE_OK_$M; } || { echo "smoke output gates failed"; touch $OUT/SMOKE_FAILED_$M; exit 4; }
