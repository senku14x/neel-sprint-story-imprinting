#!/bin/bash
# E13 R01, GPU 0 after Stage 5 (adapted from E08 R08's gpu_chain.sh: one model, no Stage 2 wait, the learning check
# before the chats, and E13's run plan). Waits for U's final adapter, copies its training logs, remaps it for vLLM
# (R05's remap_lora_for_vllm.py), runs the learning check (Stage 6), then the chat runs in order A, B, D, C
# (each its own engine and rollout file). A run is started only if, after its estimated length, at least 60 minutes
# would be left on the deadline (run A is never cut); logs/skip_<run> skips a run by hand. Run A gets one retry.
# Usage: gpu_chain.sh
set -u
M=U GPU=0
W=/workspace/e13/r01; L=$W/logs; PY=/workspace/venvs/gpu/bin/python; RO=$W/results/rollouts; MD=$W/data/models
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E13 R01: $*" >> $L/push.log 2>&1 & ); }
left() { echo $(( $(cat $W/deadline_epoch) + 32400 - $(date +%s) )); }
fin() { for d in $W/adapters/$1/final $W/adapters/${1}_mb2/final; do [ -f $d/adapter_model.safetensors ] && { echo $d; return 0; }; done; return 1; }
until fin $M >/dev/null; do
  if grep -q "train_arm $M finished" $L/stage_times.log 2>/dev/null; then sleep 30; fin $M >/dev/null && break
    st "TRAINING FAILED for $M (no final adapter; see logs/train_$M*.log)"; exit 1; fi
  sleep 30
done
sleep 30  # let train.py finish writing
D=$(fin $M); S=$(dirname $D)
cp $S/train_log.jsonl $L/train_${M}_log.jsonl; cp $S/train_meta.json $L/train_${M}_meta.json
[ -f $S/golden_render.jsonl ] && cp $S/golden_render.jsonl $L/train_${M}_golden_render.jsonl
sha256sum $D/adapter_model.safetensors $S/step125/adapter_model.safetensors >> $L/adapter_hashes.txt 2>&1
$PY -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py $D $W/lora_vllm/$M >> $L/remap.log 2>&1 || { st "REMAP FAILED for $M"; exit 1; }
sha256sum $W/lora_vllm/$M/adapter_model.safetensors >> $L/adapter_hashes.txt
st "$M trained ($D) and remapped for vLLM"
# Stage 6: learning check
echo "$(date -u +%FT%TZ) learn check start" >> $L/stage_times.log
python3 -I $W/code/learn_prefixes_e13.py > $L/learn_prefixes.log 2>&1
( cd $W && python -B $W/code/learn_check.py gen > $L/learn_check_gen.log 2>&1 ) && python3 -I $W/code/learn_check.py report > $L/learn_check_report.log 2>&1
rc=$?; echo "$(date -u +%FT%TZ) learn check exit $rc" >> $L/stage_times.log
st "learning check exit $rc (results/learn_check.json)"
# Stage 7: chat runs; est = minutes (engine load + conversations at ~25/min)
run() {  # run name, models json, temperature, conversations, never_cut
  local N=$1 J=$2 T=$3 C=$4 NC=$5
  local est=$(( 6 + C / 25 ))
  if [ -f $L/skip_$N ]; then st "skip_$N flag: run $N not generated"; return 0; fi
  if [ "$NC" != 1 ] && [ $(( $(left) - est * 60 )) -lt 3600 ]; then
    st "time cut: run $N not started ($(( $(left) / 60 )) min left, run needs ~$est min, 60 min must remain)"; return 0; fi
  st "GPU 0: chat run $N started (T $T, $C conversations)"
  bash $W/code/scripts/gen.sh $N $GPU $MD/$N.json $T E13R01 $RO/$N.jsonl
  local rc=$?
  st "GPU 0: chat run $N exit $rc ($(wc -l < $RO/$N.jsonl 2>/dev/null || echo 0) rows)"
  if [ $rc != 0 ] && [ "$NC" = 1 ]; then
    bash $W/code/scripts/gen.sh ${N}_retry $GPU $MD/$N.json $T E13R01 $RO/$N.jsonl
    rc=$?; st "GPU 0: chat run $N retry exit $rc ($(wc -l < $RO/$N.jsonl 2>/dev/null || echo 0) rows)"
    [ $rc = 0 ] && [ -s $RO/$N.jsonl ] && touch $RO/$N.jsonl.done
  fi
}
run A_T07 $MD/A_T07.json 0.7 1200 1
run B_T07 $MD/B_T07.json 0.7 600 0
run D_T1 $MD/D_T1.json 1.0 600 0
run C_T07 $MD/C_T07.json 0.7 1200 0
echo "$(date -u +%FT%TZ) gpu_chain finished" >> $L/stage_times.log
st "GPU chain finished"
