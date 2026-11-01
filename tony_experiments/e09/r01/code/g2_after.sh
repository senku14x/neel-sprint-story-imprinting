#!/bin/bash
# GPU 2 after its vLLM Stage 3 engine exits: Stage 4 for parent, S, R (HF; never alongside vLLM on this GPU)
source /workspace/e09/r01/code/env_gpu.sh; unset HAIKU_BATCH_KEY
export CUDA_VISIBLE_DEVICES=2
cd /workspace/e09/r01/code
while pgrep -f "e09_gen.py --models parent,S,R" > /dev/null; do sleep 20; done
echo "vLLM on GPU 2 exited $(date -u +%FT%TZ)"
grep -q "all steps done" /workspace/e09/r01/logs/gen_g2.log || { echo "Stage 3 g2 did not finish cleanly"; exit 1; }
python e09_fwd.py --tasks states1,states2,partb --models parent,S,R
echo "fwd exit $? $(date -u +%FT%TZ)"
[ -f /workspace/e09/r01/logs/STOP_RULE_VAXIS ] && { echo "STOP RULE"; exit 2; }
until [ -f /workspace/e09/r01/data/health_panels_all.jsonl ]; do sleep 20; done
python 001src/health.py --panel /workspace/e09/r01/data/health_panels_all.jsonl --adapters /workspace/e09/r01/code/health_adapters_SR.json --out /workspace/e09/r01/results/health/health_SR.json
echo "health exit $? $(date -u +%FT%TZ)"
