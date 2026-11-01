#!/bin/bash
# E08 R05 Stage 1 (after pilot generation) -> Stage 4 on GPU 2 -> gate -> Stage 2 launch (X on GPU 1; XB on GPU 2 after Stage 4).
W=/workspace/e08/r05; C=$W/code; L=$W/logs
PY=/workspace/venvs/gpu/bin/python
while [ ! -f $L/pilotgen.done ]; do sleep 20; done
echo "pilot generation done $(date -u +%FT%TZ)" >> $L/chain.log
# Stage 4 (GPU 2): pre-check, wait for the pick, histories; pick judge on CPU
( source $C/env.sh; CUDA_VISIBLE_DEVICES=2 $PY -I $C/r05_gen.py --plan precheck,waitpick,histories --models parent > $L/stage4_gen.log 2>&1; echo "EXIT $? $(date -u +%FT%TZ)" >> $L/stage4_gen.log ) &
S4=$!
( env -u ANTHROPIC_API_KEY /usr/bin/python3 -I $C/stage4_pick.py > $L/stage4_pick.log 2>&1; echo "EXIT $? $(date -u +%FT%TZ)" >> $L/stage4_pick.log ) &
cd $C
for v in 1 2; do /usr/bin/python3 -I merge_gen.py pilot $W/data/specs_X_v$v.jsonl $W/data/pilot_rows.json _v$v > $L/merge_pilot_v$v.log 2>&1; done
/usr/bin/python3 -I prep_pilot_x.py > $L/prep_pilot.log 2>&1
env -u ANTHROPIC_API_KEY /usr/bin/python3 -I judge_story.py --inp $W/pilot/judge_in_pilot.jsonl --out $W/judgments/haiku_story_pilot.jsonl \
  --mode direct --workers 8 --tag pilot > $L/judge_pilot.log 2>&1
$PY -I gate_x.py > $L/gate.log 2>&1; echo "GATE EXIT $? $(date -u +%FT%TZ)" >> $L/gate.log
cat $L/gate.log >> $L/chain.log
HARD=$($PY -c "import json; print(int(json.load(open('$W/data/gate_pick.json'))['hard_fail']))")
PICK=$($PY -c "import json; print(json.load(open('$W/data/gate_pick.json'))['pick'])")
if [ "$HARD" = "1" ]; then
  echo "HARD GATE FAIL: X/XB skipped $(date -u +%FT%TZ)" | tee -a $L/chain.log > $L/STOP_X_hard_gate_fail
  wait; exit 0
fi
echo "gate pick v$PICK; Stage 2 starts $(date -u +%FT%TZ)" >> $L/chain.log
bash $C/run_full.sh X $PICK 1 &
wait $S4
echo "Stage 4 generation finished $(date -u +%FT%TZ); XB generation starts on GPU 2" >> $L/chain.log
bash $C/run_full.sh XB $PICK 2 &
wait
echo "Stage 2 generation processes finished $(date -u +%FT%TZ)" >> $L/chain.log
