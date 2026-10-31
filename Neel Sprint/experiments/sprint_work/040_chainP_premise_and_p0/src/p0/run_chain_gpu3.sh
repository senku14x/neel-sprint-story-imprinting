#!/bin/bash
# sw040 P0, GPU 3 chain after the X/V target run: e08-V known-answer gate (E3's sw014 replay, V only), then the GPU
# predictors on the untrained parent (pred_vllm.py: P3 + P4 default replies; pred_hf.py: P1 + P4 representations).
set -uo pipefail
R=/root/runs/sw040/p0
export CUDA_VISIBLE_DEVICES=3 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 VLLM_LENS_DISABLE=1
until [ -e $R/genB/GEN_DONE_full ] || grep -q "RUN_GEN_P0_FULL_EXIT\|Traceback" $R/genB/run.log 2>/dev/null; do sleep 20; done
echo "genB finished $(date -u +%T)"
cd $R/src
PATH=/root/venvs/vlfix/bin:$PATH taskset -c 48-95,144-191 /root/venvs/vlfix/bin/python gate_v_gen.py $R/gate_v/requests.jsonl $R/gate_v/out > $R/gate_v/gen.log 2>&1
echo "gate_v exit $? $(date -u +%T)"
PATH=/root/venvs/vlfix/bin:$PATH taskset -c 48-95,144-191 /root/venvs/vlfix/bin/python pred_vllm.py $R/pred $R/pred/vllm > $R/pred/vllm.log 2>&1
echo "pred_vllm exit $? $(date -u +%T)"
PATH=/root/venvs/si/bin:$PATH taskset -c 48-95,144-191 /root/venvs/si/bin/python pred_hf.py $R/pred $R/pred/vllm $R/pred/hf > $R/pred/hf.log 2>&1
echo "pred_hf exit $? $(date -u +%T)"
echo CHAIN_GPU3_DONE
