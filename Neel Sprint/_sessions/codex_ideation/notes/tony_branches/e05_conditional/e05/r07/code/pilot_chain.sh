#!/bin/bash
# E05 R07 pilot steps after generation: merge, judge (1b), helper-speech projections (1c, + the R04 setup check for v3),
# G3 replies + activations (1d), gate.   bash pilot_chain.sh <ver> <specs> <rows.json>
V=$1; SPECS=$2; ROWS=$3
W=/workspace/e05/r07; C=$W/code; L=$W/logs
source $C/env.sh
cd $W
python3 -I $C/merge_gen.py pilot_v$V $SPECS $ROWS > $L/merge_pilot_v$V.log 2>&1 || { echo "merge failed"; exit 1; }
python3 -I $C/prep_pilot.py $V >> $L/merge_pilot_v$V.log 2>&1
STEPS=stories; [ "$V" = "3" ] && STEPS=repl,stories
# judge (CPU, API)
( /usr/bin/python3 -I $C/judge_story.py --inp $W/pilot/judge_in_pilot_v$V.jsonl --out $W/judgments/haiku_story_pilot_v$V.jsonl \
    --mode direct --workers 8 --tag pilot_v$V > $L/judge_pilot_v$V.log 2>&1; echo "EXIT $?" >> $L/judge_pilot_v$V.log ) &
# 1c on GPU 1
( CUDA_VISIBLE_DEVICES=1 /workspace/venvs/gpu/bin/python -I $C/fwd_r07.py --steps $STEPS --stories_in $W/pilot/fwd_in_pilot_v$V.jsonl \
    --stories_out $W/pilot/fwd_stories_v$V.jsonl > $L/fwd_pilot_v$V.log 2>&1; echo "EXIT $?" >> $L/fwd_pilot_v$V.log ) &
# 1d on GPU 0: P07 replies (vLLM), then activations (HF)
( CUDA_VISIBLE_DEVICES=0 /workspace/venvs/gpu/bin/python -I $C/g3_gen.py --ver $V --which p07 --out $W/pilot/g3_v${V}_replies.jsonl > $L/g3_gen_v$V.log 2>&1 \
  && CUDA_VISIBLE_DEVICES=0 /workspace/venvs/gpu/bin/python -I $C/fwd_r07.py --steps g3 --g3_in $W/pilot/g3_v${V}_replies.jsonl \
    --g3_out $W/pilot/g3_acts_v$V.jsonl > $L/fwd_g3_v$V.log 2>&1; echo "EXIT $?" >> $L/fwd_g3_v$V.log ) &
wait
/workspace/venvs/gpu/bin/python -I $C/gate.py $V > $L/gate_v$V.log 2>&1; echo "GATE EXIT $?" >> $L/gate_v$V.log
echo "CHAIN DONE $(date -u +%T)"
