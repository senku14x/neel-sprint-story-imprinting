# sw053 job environment (sourced by every sw053 job and post-processing script; box-agnostic: /workspace, /dev/shm/qwen36_27b, /root/venvs)
export SRC="/workspace/Neel Sprint/experiments/sprint_work/053_turn1_dial_dt1/src"
export RUN=/workspace/runs_executor/sw053
export DAY=/workspace/runs_executor/day_2026-10-31_E1
export L=$DAY/lib
export HF_HOME=/workspace/.cache/huggingface
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 TOKENIZERS_PARALLELISM=false
SI=/root/venvs/si/bin/python
VL=/root/venvs/vlfix/bin/python
PY3=/usr/bin/python3                     # system python (httpx) for judge_run / board (mistakes.md 30 Oct 08:15)
TS="taskset -c 0-87"                     # box1 / boxA CPU pin
vlenv() { PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH="$SRC/vllm_lens_sw011:$SRC" "$@"; }   # sw011's engine copy (018 + maxpos skip)
sienv() { PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "$@"; }
board() { $PY3 "$L/board.py" event "$@" || true; }
mkdir -p $RUN/logs
