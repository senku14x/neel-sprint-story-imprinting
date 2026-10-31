#!/bin/bash
# sw033 job: vLLM stage then HF stage on ONE GPU (one model-holding process at a time). Usage:
#   run33.sh <gpu> <out_dir> <tag> <vllm_models> <hf_models> [extra vLLM args...]
#   smoke: run33.sh 0 /root/runs/sw033/smoke smoke hdA0,hdB0,parent hdA0,hdB0 --smoke --samples 1
#   full : run33.sh 0 /root/runs/sw033/full_hdA0 hdA0 hdA0,parent hdA0      |   run33.sh 1 /root/runs/sw033/full_hdB0 hdB0 hdB0 hdB0
set -u
GPU=$1; OUT=$2; TAG=$3; VM=$4; HM=$5; shift 5
SRC="/workspace/Neel Sprint/experiments/sprint_work/033_thinking_onset_dissociation/src"
SAMP=3; for a in "$@"; do [ "$a" = "--smoke" ] && SAMP=1; done
case $GPU in 3) CPUS=56-111,168-223;; *) CPUS=0-55,112-167;; esac
mkdir -p "$OUT"; cd "$SRC"
export CUDA_VISIBLE_DEVICES=$GPU OMP_NUM_THREADS=8
echo "$(date -u +%FT%TZ) start vllm ($VM) gpu $GPU" >> "$OUT/status.log"
if [ ! -e "$OUT/vllm/GPU_DONE_vllm_$TAG" ]; then
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c $CPUS python gen33_vllm.py --run_dir "$OUT/vllm" --tag $TAG --models $VM "$@" > "$OUT/vllm.log" 2>&1
  rc=$?; echo "$(date -u +%FT%TZ) vllm rc=$rc" >> "$OUT/status.log"; [ $rc -eq 0 ] || exit $rc
fi
echo "$(date -u +%FT%TZ) start hf ($HM)" >> "$OUT/status.log"
STAGE=gates,run; [ "$SAMP" = "1" ] && STAGE=gates,probe,run
PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True taskset -c $CPUS python gen33_hf.py --vllm_dir "$OUT/vllm" --run_dir "$OUT/hf" --tag $TAG --models $HM --samples $SAMP --stage $STAGE ${HF_ARGS:-} > "$OUT/hf.log" 2>&1
rc=$?; echo "$(date -u +%FT%TZ) hf rc=$rc" >> "$OUT/status.log"
[ $rc -eq 0 ] && date -u +%FT%TZ > "$OUT/JOB_DONE_$TAG"
exit $rc
