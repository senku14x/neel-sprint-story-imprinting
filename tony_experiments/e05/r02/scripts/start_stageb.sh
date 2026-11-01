#!/bin/bash
# waits for the Stage A vLLM run to finish and the GPU to be free; starts the GLM Stage A sample; then runs Stage B
LOG=/workspace/e05/r02/logs/stageb.log
until grep -q "all steps done" /workspace/e05/r02/logs/gen.log || grep -q "^EXIT" /workspace/e05/r02/logs/gen.log; do sleep 15; done
if [ -f /workspace/e05/r02/logs/STOP_RULE ]; then echo "stop rule set; not starting Stage B" >> $LOG; exit 0; fi
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 3000 ]; do sleep 10; done
echo "stage A done; GPU free $(date -u +%H:%M:%S)" >> $LOG
tmux new -d -s r02glmA "env -u PYTHONPATH -u ANTHROPIC_API_KEY /usr/bin/python3 -I /workspace/e05/r02/driver/r02_glm.py --stage A >> /workspace/e05/r02/logs/glm_A.log 2>&1"
export SI_MODEL_DIR=/dev/shm/e05r02_qwen
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HOME=/workspace/e05/hfcache HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export TRITON_CACHE_DIR=/root/.cache/e05r02/triton_hf
cd /workspace/e05/r02
echo "stageb start $(date -u +%H:%M:%S)" >> $LOG
/workspace/venvs/gpu/bin/python /workspace/e05/r02/driver/r02_stageb.py --steps "${1:-check,dirs,proj,calib,gen}" >> $LOG 2>&1
echo "stageb exit $? $(date -u +%H:%M:%S)" >> $LOG
