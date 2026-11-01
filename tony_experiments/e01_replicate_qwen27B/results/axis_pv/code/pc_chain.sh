#!/usr/bin/env bash
# Part C on one GPU: merge both adapters (hash check) -> for base, hc_db_s0, hb_dc_s0: serve with vLLM, C1/C2 generations,
# stop the server -> HF activations (base + both adapters in one PEFT model).   bash pc_chain.sh <gpu>
source /workspace/si36/axis_pv/code/env_axis_pv.sh
GPU=$1; cd $W
log () { echo "$(date -u +%H:%M:%S) $*"; }
gpu_free () { for i in $(seq 1 60); do [ $(nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits) -lt 2000 ] && return 0; sleep 5; done; return 1; }
stop_server () { local p=$(cat $W/logs/vllm_$1.pid); kill $p; for i in $(seq 1 60); do kill -0 $p 2>/dev/null || break; sleep 3; done; gpu_free; }
gpu_free || { log "GPU $GPU busy"; exit 1; }
for m in hc_db_s0 hb_dc_s0; do
  if [ -f /scratch/axis_pv/merged/$m/merge_meta.json ]; then log "merged $m exists"; continue; fi
  log "merge $m"; CUDA_VISIBLE_DEVICES=$GPU $PY code/pc_merge.py --model $m > logs/pc_merge_$m.log 2>&1; rc=$?
  log "merge $m exit $rc: $(tail -1 logs/pc_merge_$m.log | cut -c1-200)"; [ $rc -ne 0 ] && exit 1
  gpu_free
done
PORT=$((8100 + GPU))
for m in base hc_db_s0 hb_dc_s0; do
  if [ -s pc/gen_$m.jsonl ]; then log "gen $m exists"; continue; fi
  if [ $m = base ]; then bash code/serve.sh $SNAP $PORT $m $GPU --language-model-only > logs/serve_$m.out 2>&1
  else bash code/serve.sh /scratch/axis_pv/merged/$m $PORT $m $GPU > logs/serve_$m.out 2>&1; fi
  rc=$?; log "serve $m exit $rc: $(tail -1 logs/serve_$m.out)"; [ $rc -ne 0 ] && exit 1
  $PY code/pc_gen.py --model $m --port $PORT > logs/pc_gen_$m.log 2>&1; rc=$?
  log "pc_gen $m exit $rc: $(tail -1 logs/pc_gen_$m.log | cut -c1-200)"
  stop_server $m; log "server $m stopped"
  [ $rc -ne 0 ] && exit 1
done
log "pc_acts"; CUDA_VISIBLE_DEVICES=$GPU $PY code/pc_acts.py > logs/pc_acts.log 2>&1; rc=$?
log "pc_acts exit $rc: $(tail -1 logs/pc_acts.log | cut -c1-300)"
[ $rc -eq 0 ] && log PC_CHAIN_DONE
