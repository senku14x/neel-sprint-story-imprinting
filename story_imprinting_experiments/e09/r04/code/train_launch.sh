#!/bin/bash
# usage: train_launch.sh NAME GPU REPLAY_FILE REPLAY_RATIO [MICRO_BS] [EXTRA...]
# R01's code/train_launch.sh adapted: paths -> e09/r04, sarcastic story file, replay file as an argument
# (REPLAY_FILE "none" = stories only). OUT defaults to adapters/NAME (dry runs: OUT=/workspace/e09/r04/dry/NAME EXTRA=--dry).
NAME=$1; GPU=$2; REPLAY=$3; RATIO=$4; MB=${5:-4}; shift 5 2>/dev/null; EXTRA="$*"
OUT=${OUT:-/workspace/e09/r04/adapters/$NAME}
export CUDA_VISIBLE_DEVICES=$GPU
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HOME=/workspace/e09/r04/hfcache
unset HF_TOKEN OPENROUTER_API_KEY GITHUB_TOKEN RUNPOD_API_KEY ANTHROPIC_API_KEY HAIKU_BATCH_KEY SI_MODEL_DIR
cd /workspace/e09/r04/code/001src
RARGS=(); [ "$REPLAY" != "none" ] && RARGS=(--replay "$REPLAY" --replay_ratio "$RATIO")
echo "start $(date -u +%FT%TZ) name=$NAME gpu=$GPU replay=$REPLAY ratio=$RATIO micro_bs=$MB extra=$EXTRA out=$OUT"
/workspace/e03/venvs/si/bin/python train.py \
  --data /workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl \
  --out $OUT --seed 0 --lr 5e-4 --rank 32 --alpha 64 --eff_bs 32 --micro_bs $MB --warmup 10 \
  --schedule cosine "${RARGS[@]}" $EXTRA
echo "exit $? $(date -u +%FT%TZ)"
