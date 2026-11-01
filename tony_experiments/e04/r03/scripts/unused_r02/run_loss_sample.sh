#!/usr/bin/env bash
# Step 5 loss sample (GPU 1, free after a5b was stopped) once the editor's export exists.
R02=/workspace/e04/r02; LOG=$R02/logs/chain.log
until [ -f /workspace/e04/gen/r02/a5b_sonnet_final.jsonl ] && grep -q "^Done" $R02/logs/a5b_editor.log; do sleep 30; done
source $R02/scripts/env.sh; unset PYTHONPATH; export PATH=/workspace/venvs/gpu/bin:$PATH
cd $R02
echo "$(date -u +%FT%TZ) loss sample start on GPU ${LOSS_GPU:-1}" >> $LOG
/workspace/venvs/gpu/bin/python scripts/loss_sample.py --prepare > logs/loss_sample.log 2>&1 && \
CUDA_VISIBLE_DEVICES=${LOSS_GPU:-1} /workspace/venvs/gpu/bin/python scripts/loss_sample.py >> logs/loss_sample.log 2>&1
echo "$(date -u +%FT%TZ) loss sample exit $?" >> $LOG
