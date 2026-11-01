#!/bin/bash
# E08 R02 after Stage 3: when both final adapters exist, copy training logs, remap both for vLLM, then
#   GPU 1: Stage 5 for N; GPU 2: Stage 5 for NB (free, btw, free_off, t1check); GPU 0 (after chain_eval_ref): Stage 6 for N, NB.
source /workspace/e08/r02/code/env.sh
W=/workspace/e08/r02; C=$W/code; L=$W/logs; PY=/workspace/venvs/gpu/bin/python
fin() { for d in $W/adapters/$1/final $W/adapters/${1}_mb2/final; do [ -f $d/adapter_model.safetensors ] && { echo $d; return 0; }; done; return 1; }
until fin N >/dev/null && fin NB >/dev/null; do
  for a in N NB; do if grep -q "^exit [1-9]" $L/train_$a.times 2>/dev/null && ! grep -q OOM $L/train_$a.times; then echo "TRAINING FAILED $a" >> $L/stage_times.log; exit 1; fi; done
  sleep 30
done
sleep 20
for a in N NB; do
  D=$(fin $a); S=$(dirname $D)
  cp $S/train_log.jsonl $L/train_${a}_log.jsonl; cp $S/train_meta.json $L/train_${a}_meta.json; cp $S/golden_render.jsonl $L/train_${a}_golden_render.jsonl
  $PY -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py $D $W/lora_vllm/$a >> $L/remap.log 2>&1
  [ "$S" != "$W/adapters/$a" ] && ln -sfn $S $W/adapters/${a}_used
done
echo "training done; remapped $(date -u +%FT%TZ)" >> $L/stage_times.log
( CUDA_VISIBLE_DEVICES=1 $PY -I $C/r07_gen.py --plan free,btw,free_off,t1check --models N --ver 4 --tag N >> $L/gen_N.log 2>&1
  echo "N stage5 exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log ) &
( CUDA_VISIBLE_DEVICES=2 $PY -I $C/r07_gen.py --plan free,btw,free_off,t1check --models NB --ver 4 --tag NB >> $L/gen_NB.log 2>&1
  echo "NB stage5 exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log ) &
( until grep -q "stage6 parent,S,SB,Q exit" $L/stage_times.log; do sleep 20; done
  CUDA_VISIBLE_DEVICES=0 $PY -I $C/stage6.py --models N,NB --ver 4 >> $L/stage6_NNB.log 2>&1
  echo "stage6 N,NB exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log ) &
wait
echo "post_train all done $(date -u +%FT%TZ)" >> $L/stage_times.log
