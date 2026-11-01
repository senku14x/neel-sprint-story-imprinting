#!/bin/bash
# E13 R03, GPU 0 after Stage 2 (adapted from E13 R01's gpu_chain.sh: model UB, R03 paths, 7-hour deadline, the R03 run plan
# of 600 conversations per run, the upload of Stage 2b in the background). Waits for UB's final adapter, copies its
# training logs, remaps it for vLLM (R05's remap_lora_for_vllm.py), starts the upload, runs the learning check (Stage 3),
# then the chat runs in order A, B, D, C (each its own engine and rollout file, results/rollouts/<run>_<T07|T1>.jsonl).
# A run is started only if, after its estimated length, at least 60 minutes would be left on the deadline (the brief:
# no new run with 45 minutes left; run A is never cut); logs/skip_<run> skips a run by hand. Run A gets one retry.
# Seed tag E13R02 (the brief: same seeds per script and cell as R02's U and parent).
# Usage: gpu_chain.sh
set -u
M=UB GPU=0
W=/workspace/e13/r03; L=$W/logs; PY=/workspace/venvs/gpu/bin/python; RO=$W/results/rollouts; MD=$W/data/models
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E13 R03: $*" >> $L/push.log 2>&1 & ); }
left() { echo $(( $(cat $W/deadline_epoch) + 25200 - $(date +%s) )); }
fin() { for d in $W/adapters/$1/final $W/adapters/${1}_mb2/final; do [ -f $d/adapter_model.safetensors ] && { echo $d; return 0; }; done; return 1; }
mkdir -p $RO
until fin $M >/dev/null; do
  if grep -q "train_arm $M finished" $L/stage_times.log 2>/dev/null; then sleep 30; fin $M >/dev/null && break
    st "TRAINING FAILED for $M (no final adapter; see logs/train_$M*.log)"; exit 1; fi
  sleep 30
done
until grep -q "train_arm $M finished" $L/stage_times.log 2>/dev/null; do sleep 15; done  # train.py has exited
D=$(fin $M); S=$(dirname $D)
cp $S/train_log.jsonl $L/train_${M}_log.jsonl; cp $S/train_meta.json $L/train_${M}_meta.json
[ -f $S/golden_render.jsonl ] && cp $S/golden_render.jsonl $L/train_${M}_golden_render.jsonl
sha256sum $D/adapter_model.safetensors $S/step125/adapter_model.safetensors >> $L/adapter_hashes.txt 2>&1
$PY -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py $D $W/lora_vllm/$M >> $L/remap.log 2>&1 || { st "REMAP FAILED for $M"; exit 1; }
sha256sum $W/lora_vllm/$M/adapter_model.safetensors >> $L/adapter_hashes.txt
st "$M trained ($D) and remapped for vLLM"
# Stage 2b: upload UB's PEFT adapter to the study repo in the background (never blocks the chain)
( $PY -I -B $W/code/upload_ub.py > $L/upload_ub.log 2>&1; st "HF upload of e13-UB: $(tail -1 $L/upload_ub.log)" ) &
# Stage 3: learning check
echo "$(date -u +%FT%TZ) learn check start" >> $L/stage_times.log
( cd $W && python -B $W/code/learn_check.py gen > $L/learn_check_gen.log 2>&1 ) && python3 -I -B $W/code/learn_check.py report > $L/learn_check_report.log 2>&1
rc=$?; echo "$(date -u +%FT%TZ) learn check exit $rc" >> $L/stage_times.log
st "learning check exit $rc (results/learn_check.json)"
# Stage 4: chat runs; est = minutes (engine load + conversations at ~25/min)
run() {  # run name, models json, temperature, conversations, never_cut
  local N=$1 J=$2 T=$3 C=$4 NC=$5
  local est=$(( 6 + C / 25 ))
  if [ -f $L/skip_$N ]; then st "skip_$N flag: run $N not generated"; return 0; fi
  if [ "$NC" != 1 ] && [ $(( $(left) - est * 60 )) -lt 3600 ]; then
    st "time cut: run $N not started ($(( $(left) / 60 )) min left, run needs ~$est min, 60 min must remain)"; return 0; fi
  echo "$(date -u +%FT%TZ) gen $N start" >> $L/stage_times.log
  st "GPU 0: chat run $N started (T $T, $C conversations)"
  bash $W/code/scripts/gen.sh $N $GPU $J $T E13R02 $RO/$N.jsonl
  local rc=$?
  echo "$(date -u +%FT%TZ) gen $N exit $rc" >> $L/stage_times.log
  st "GPU 0: chat run $N exit $rc ($(wc -l < $RO/$N.jsonl 2>/dev/null || echo 0) rows)"
  if [ $rc != 0 ] && [ "$NC" = 1 ]; then
    bash $W/code/scripts/gen.sh ${N}_retry $GPU $J $T E13R02 $RO/$N.jsonl
    rc=$?; st "GPU 0: chat run $N retry exit $rc ($(wc -l < $RO/$N.jsonl 2>/dev/null || echo 0) rows)"
    [ $rc = 0 ] && [ -s $RO/$N.jsonl ] && touch $RO/$N.jsonl.done
  fi
}
run A_T07 $MD/A_T07.json 0.7 600 1
run B_T07 $MD/B_T07.json 0.7 600 0
run D_T1 $MD/D_T1.json 1.0 600 0
run C_T07 $MD/C_T07.json 0.7 600 0
echo "$(date -u +%FT%TZ) gpu_chain finished" >> $L/stage_times.log
st "GPU chain finished"
