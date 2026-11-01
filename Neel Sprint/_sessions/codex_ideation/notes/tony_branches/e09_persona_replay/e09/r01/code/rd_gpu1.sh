#!/bin/bash
# second Stage 3 engine for RD on GPU 1 (trigger-off and T1 cells), after RD is remapped by after_train.sh on GPU 0
W=/workspace/e09/r01
source $W/code/env_gpu.sh; unset HAIKU_BATCH_KEY
export CUDA_VISIBLE_DEVICES=1
cd $W/code
until [ -f $W/logs/remapped_RD ]; do sleep 20; done
python e09_gen.py --models RD --plan offP01,offOther,T1 > $W/logs/gen_RD_g1.log 2>&1
echo "stage3 RD (GPU 1 part) exit $? $(date -u +%FT%TZ)"
