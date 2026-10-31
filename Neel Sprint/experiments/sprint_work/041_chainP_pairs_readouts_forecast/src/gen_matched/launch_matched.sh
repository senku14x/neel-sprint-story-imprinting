#!/bin/bash
# Launch gen_matched.py on the node, pinned to one GPU and its CPU socket, in the background; prints the PID.
# Code tree on the node: <code root>/gen (= /workspace src/gen, unchanged) + <code root>/gen_matched (= /workspace src/gen_matched),
# rsynced from /workspace, never edited on the node. Usage (on the node):
#   bash <code root>/gen_matched/launch_matched.sh <gpu> <cpu list> <log> <gen_matched.py args...>
# GPUs 0-1 -> CPUs 0-47,96-143; GPUs 2-3 -> 48-95,144-191. Env as src/gen/launch.sh.
GPU=$1; CPUS=$2; LOG=$3; shift 3
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$(dirname "$LOG")"
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=$GPU GEN_LAUNCHER="$HERE/launch_matched.sh"
export VLLM_USE_FLASHINFER_SAMPLER=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 SI_MODEL_DIR=/dev/shm/qwen36_27b
unset PYTHONPATH
nohup taskset -c "$CPUS" python -I "$HERE/gen_matched.py" "$@" >> "$LOG" 2>&1 < /dev/null &
echo $!
