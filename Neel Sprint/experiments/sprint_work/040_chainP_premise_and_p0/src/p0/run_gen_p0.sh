#!/bin/bash
# sw040 P0 GPU job on the node (GPU 0, socket 0): KA gate -> smoke -> estimate -> full (stops if the estimate > 2.5 h).
set -euo pipefail
R=/root/runs/sw040/p0
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1
cd $R/src
taskset -c 0-47,96-143 /root/venvs/vlfix/bin/python gen_p0.py --mode all --models $R/src/models_p0.json --inputs $R/inputs \
  --out $R/gen --ka $R/ka/ka_requests.jsonl --ka_saved $R/ka/ka_saved.json --lib $R/lib
echo "RUN_GEN_P0_EXIT $? $(date -u +%T)"
