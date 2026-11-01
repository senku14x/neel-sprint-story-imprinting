#!/bin/bash
# E08 R02: reference-model work on one GPU while N and NB train.
#   Stage 4 histories (parent, P06/P07) + parent Stage 5 (6 personas x free/btw/free_off) + parent T1 check;
#   SB and Q Stage 5 for P06/P07 (free/btw/free_off); Stage 6 for parent, S, SB, Q.
#   bash chain_eval_ref.sh <gpu> [wait_for_file]
source /workspace/e08/r02/code/env.sh
G=$1; WAITF=${2:-}
W=/workspace/e08/r02; C=$W/code; L=$W/logs; PY=/workspace/venvs/gpu/bin/python
if [ -n "$WAITF" ]; then until [ -f "$WAITF" ]; do sleep 20; done; sleep 30; fi
echo "chain_eval_ref start gpu $G $(date -u +%FT%TZ)" >> $L/stage_times.log
CUDA_VISIBLE_DEVICES=$G $PY -I $C/r07_gen.py --plan histories,free,btw,free_off,t1check --models parent --ver 4 --tag parent >> $L/gen_parent.log 2>&1
echo "parent stage4/5 exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log
CUDA_VISIBLE_DEVICES=$G $PY -I $C/r07_gen.py --plan free,btw,free_off --models SB,Q --personas refuser,plainspoken --ver 4 --tag SBQ >> $L/gen_SBQ.log 2>&1
echo "SB/Q stage5 exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log
CUDA_VISIBLE_DEVICES=$G $PY -I $C/stage6.py --models parent,S,SB,Q --ver 4 >> $L/stage6_ref.log 2>&1
echo "stage6 parent,S,SB,Q exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log
