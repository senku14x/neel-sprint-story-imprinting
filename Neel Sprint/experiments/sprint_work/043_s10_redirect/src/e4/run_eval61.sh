#!/bin/bash
# sw061 evaluation job body (one H200; one vLLM process on the GPU). bash run_eval61.sh SPEC.json OUT_DIR [--no-post]
#   1. prep_lora61.py (remap every model of the spec with 001's script, byte-level verification, manifest)        [si venv, CPU]
#   2. eval61.py (adapter-active gate, battery forced, known answer vs sw055, rest, garble, coverage gates, OUT/GPU_DONE) [vlfix]
#   3. post61.sh launched detached (box 1 only: labels, two-judge 20% + disagreements, judge-all if < 0.95, conduct, garble,
#      analysis) unless --no-post (other hosts: run post61.sh on box 1 once OUT is synced there).
set -uo pipefail
SPEC=${1:?spec.json}; OUT=${2:?out dir}; POST=${3:-post}
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"
export HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1
test -d /dev/shm/qwen36_27b || { echo "no /dev/shm/qwen36_27b on $(hostname)"; exit 4; }
mkdir -p "$OUT"; cp "$SPEC" "$OUT/spec.json"
echo "eval61 start $(date -u +%FT%TZ) on $(hostname) job ${JOB:-?} box ${BOX:-?} spec $SPEC"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
taskset -c 0-87 /root/venvs/si/bin/python "$SRC/prep_lora61.py" "$OUT/spec.json" "$OUT" || { echo "LoRA prep failed"; exit 5; }
rc=0; PATH=/root/venvs/vlfix/bin:$PATH taskset -c 0-87 /root/venvs/vlfix/bin/python "$SRC/eval61.py" --spec "$OUT/spec.json" --out "$OUT" || rc=$?
echo "eval61 exit $rc $(date -u +%FT%TZ)"
[ $rc = 0 ] || exit $rc
test -e "$OUT/GPU_DONE" || { echo "no GPU_DONE"; exit 6; }
if [ "$POST" != "--no-post" ] && [ "$(hostname)" = af2422212563 ]; then
  setsid nohup bash "$SRC/post61.sh" "$OUT" > "$OUT/post.log" 2>&1 < /dev/null &
  echo $! > "$OUT/post.pid"; echo "post61 launched, pid $(cat "$OUT/post.pid") $(date -u +%FT%TZ)"
fi
