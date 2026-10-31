#!/bin/bash
# sw035 eval, vector models: engine-parity known answer first, battery only if every reference set passes.
#   run_vec.sh <gpu> <mode lens|hook> <run_dir> <tag> <ref spec NAME=dir,...> <models (comma list; vec:<tag>:<lora|none>:<A|B>:<path>)> [stages]
GPU=$1; MODE=$2; RD=$3; TAG=$4; REF=$5; MODELS=$6; STAGES=${7:-check,a,bc}
J="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval/jobs"
mkdir -p "$RD"
bash "$J/run_parity.sh" $GPU $MODE "$RD/parity_$MODE.json" "$REF"
ok=$(python3 -c "import json,sys; d=json.load(open('$RD/parity_$MODE.json')); print(int(all(v['pass'] for v in d['sets'].values())))" 2>/dev/null)
if [ "$ok" != "1" ]; then echo "PARITY_FAIL $(date -u +%FT%TZ)" >> "$RD/run.log"; exit 4; fi
echo "PARITY_OK $(date -u +%FT%TZ)" >> "$RD/run.log"
for i in $(seq 1 30); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU); [ "$u" -lt 1000 ] && break; sleep 10; done
bash "$J/run_ev.sh" $GPU "$RD" "$TAG" "$MODELS" $MODE --stages "$STAGES"
