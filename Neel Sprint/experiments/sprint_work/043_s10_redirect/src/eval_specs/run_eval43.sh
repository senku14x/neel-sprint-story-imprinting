#!/bin/bash
# sw043 eval GPU job on the node: run_eval61.sh's two GPU-side steps verbatim (prep_lora61.py, then eval61.py), with E4's code at its
# /workspace path mirrored on the node (sha256 = handoff), pinned to one GPU and its CPU socket (run_eval61.sh pins taskset 0-87 and
# sets no CUDA_VISIBLE_DEVICES; 043 DECISIONS D12). Post (labels, judging, analysis) runs on box 1: post61.sh OUT sw043 CAP.
#   GPU=3 CPUS=72-95,168-191 bash run_eval43.sh SPEC.json OUT_DIR
set -uo pipefail
SPEC=${1:?spec}; OUT=${2:?out}; GPU=${GPU:-3}; CPUS=${CPUS:-72-95,168-191}
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"
cd "$SRC" && sha256sum -c /root/runs/sw043/code/e4/SHA256SUMS_handoff --quiet || { echo "E4 code sha mismatch"; exit 4; }
export OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
test -d /dev/shm/qwen36_27b || { echo "no /dev/shm/qwen36_27b"; exit 4; }
mkdir -p "$OUT"; cp "$SPEC" "$OUT/spec.json"
echo "eval43 start $(date -u +%FT%TZ) on $(hostname) GPU $GPU CPUS $CPUS spec $SPEC"
nvidia-smi -i $GPU --query-gpu=name,memory.used --format=csv,noheader
taskset -c $CPUS /root/venvs/si/bin/python "$SRC/prep_lora61.py" "$OUT/spec.json" "$OUT" || { echo "LoRA prep failed"; exit 5; }
rc=0; PATH=/root/venvs/vlfix/bin:$PATH taskset -c $CPUS /root/venvs/vlfix/bin/python "$SRC/eval61.py" --spec "$OUT/spec.json" --out "$OUT" || rc=$?
echo "eval61 exit $rc $(date -u +%FT%TZ)"
[ $rc = 0 ] || exit $rc
test -e "$OUT/GPU_DONE" || { echo "no GPU_DONE"; exit 6; }
echo "EVAL43_DONE $(date -u +%FT%TZ)"
