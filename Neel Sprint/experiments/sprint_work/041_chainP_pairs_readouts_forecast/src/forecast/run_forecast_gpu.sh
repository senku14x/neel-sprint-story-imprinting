#!/bin/bash
# sw041 forecast, NODE side (one GPU): P0's FROZEN GPU predictors on the Chain P lines built by forecast_p.py lines + sets.
#   bash run_forecast_gpu.sh <gpu> <run name>        e.g.  bash run_forecast_gpu.sh 2 final
# Inputs (rsync from box 1 first):  /root/runs/sw041/forecast/<run>/pred/{lines_lm.jsonl,p3_prompts.jsonl}
# Code: the frozen copies in /root/runs/sw040/p0/src (sha256 asserted below = DESIGN_P0.txt). Each script writes its own manifest.
# ~4 min (vLLM: P3 + 1,600 default replies) + ~13 min (HF: P1 + P4 on 1,600 lines) on one H200.
set -euo pipefail
GPU=${1:?gpu}; RUN=${2:?run}
R=/root/runs/sw041/forecast/$RUN; SRC=/root/runs/sw040/p0/src
case $GPU in 0|1) CPUS=0-47,96-143;; 2|3) CPUS=48-95,144-191;; esac
echo "111ff687203ecb46e77450deb050cdc8a41373bf1a080298e5a0e3c96be63704  $SRC/pred_vllm.py
50402428139dae17a6f6c48a1584b07083e54563bab629bb0ff3f505264161cb  $SRC/pred_hf.py" | sha256sum -c -
test -s $R/pred/lines_lm.jsonl && test -s $R/pred/p3_prompts.jsonl
mkdir -p $R/pred/vllm $R/pred/hf
export CUDA_VISIBLE_DEVICES=$GPU OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 VLLM_LENS_DISABLE=1
cd $SRC
PATH=/root/venvs/vlfix/bin:$PATH taskset -c $CPUS /root/venvs/vlfix/bin/python pred_vllm.py $R/pred $R/pred/vllm > $R/pred/vllm.log 2>&1
echo "pred_vllm exit $? $(date -u +%T)"
PATH=/root/venvs/si/bin:$PATH taskset -c $CPUS /root/venvs/si/bin/python pred_hf.py $R/pred $R/pred/vllm $R/pred/hf > $R/pred/hf.log 2>&1
echo "pred_hf exit $? $(date -u +%T)"
echo FORECAST_GPU_DONE
