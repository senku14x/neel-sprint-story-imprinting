#!/bin/bash
# usage: train_launch.sh NAME GPU REPLAY_RATIO [MICRO_BS]   (R01's code/train_launch.sh, paths -> e09/r02)
NAME=$1; GPU=$2; RATIO=$3; MB=${4:-4}
export CUDA_VISIBLE_DEVICES=$GPU
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HOME=/workspace/e09/r02/hfcache
unset HF_TOKEN OPENROUTER_API_KEY GITHUB_TOKEN RUNPOD_API_KEY ANTHROPIC_API_KEY HAIKU_BATCH_KEY SI_MODEL_DIR
cd /workspace/e09/r02/code/001src
echo "start $(date -u +%FT%TZ) name=$NAME gpu=$GPU ratio=$RATIO micro_bs=$MB"
/workspace/e03/venvs/si/bin/python train.py \
  --data /workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl \
  --out /workspace/e09/r02/adapters/$NAME --seed 0 --lr 5e-4 --rank 32 --alpha 64 --eff_bs 32 --micro_bs $MB --warmup 10 \
  --schedule cosine --replay /workspace/e09/r02/data/replay_rows_short.jsonl --replay_ratio $RATIO $EXTRA
echo "exit $? $(date -u +%FT%TZ)"
