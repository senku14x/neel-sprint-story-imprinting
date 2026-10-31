#!/bin/bash
# Launch gen_local.py on the node, pinned to one GPU and its CPU socket, in the background; prints the PID.
# Usage (on the node): bash launch.sh <gpu> <cpu list> <log file> <gen_local.py args...>
#   e.g. bash launch.sh 2 48-95 /root/runs/sw041/gen/logs/smoke.log --jobs /root/runs/sw041/gen/specs/jobs_smoke.json
# GPUs 0-1 sit on socket 0 (CPUs 0-47,96-143), GPUs 2-3 on socket 1 (CPUs 48-95,144-191).
# Env as Tony's e08 env.sh where it matters for generation (VLLM_USE_FLASHINFER_SAMPLER=0, expandable segments), plus the node rules.
GPU=$1; CPUS=$2; LOG=$3; shift 3
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$(dirname "$LOG")"
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=$GPU GEN_LAUNCHER="$HERE/launch.sh"
export VLLM_USE_FLASHINFER_SAMPLER=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 SI_MODEL_DIR=/dev/shm/qwen36_27b
unset PYTHONPATH
nohup taskset -c "$CPUS" python -I "$HERE/gen_local.py" "$@" >> "$LOG" 2>&1 < /dev/null &
echo $!
