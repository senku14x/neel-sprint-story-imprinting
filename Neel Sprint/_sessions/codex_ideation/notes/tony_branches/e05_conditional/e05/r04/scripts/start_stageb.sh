#!/bin/bash
# waits for Stage A generation to exit and the GPU to be free; starts the GLM sample; then runs Stage B
LOG=/workspace/e05/r04/logs/stageb.log
until grep -q "^EXIT" /workspace/e05/r04/logs/gen.log; do sleep 10; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 3000 ]; do sleep 5; done
echo "stage A exited; GPU free $(date -u +%H:%M:%S)" >> $LOG
if [ -f /workspace/e05/r04/rollouts/btw.done ] && [ -f /workspace/e05/r04/rollouts/free_off.done ]; then
  tmux new -d -s r04glm "env -u PYTHONPATH -u ANTHROPIC_API_KEY /usr/bin/python3 -I /workspace/e05/r04/driver/r04_glm.py >> /workspace/e05/r04/logs/glm.log 2>&1"
fi
export SI_MODEL_DIR=/dev/shm/e05r04_qwen
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HOME=/workspace/e05/r04/hfcache HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export TRITON_CACHE_DIR=/root/.cache/e05r04/triton_hf
cd /workspace/e05/r04
echo "stageb start $(date -u +%H:%M:%S)" >> $LOG
/workspace/venvs/gpu/bin/python /workspace/e05/r04/driver/r04_stageb.py --steps "${1:-dirs,proj,repl,proj2}" --models2 "${2:-SB,Q,S,R,Q200,Q150,Q100}" >> $LOG 2>&1
echo "stageb exit $? $(date -u +%H:%M:%S)" >> $LOG
