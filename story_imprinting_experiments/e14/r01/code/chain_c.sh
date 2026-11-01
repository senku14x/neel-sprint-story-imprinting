#!/bin/bash
# Start Part C (fresh process) only after gpu_ab.py exits cleanly (GPU_AB_EXIT printed and EXIT 0).
cd /workspace/e14/r01
until grep -q "^EXIT" logs/gpu_ab.log; do sleep 10; done
if grep -q "GPU_AB_EXIT" logs/gpu_ab.log && grep -q "^EXIT 0" logs/gpu_ab.log && [ -f vectors/partB_main.pt ] && [ -f vectors/known_th_parent.pt ]; then
  echo "$(date -u +%T) starting Part C" >> logs/chain_c.log
  HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false /workspace/venvs/gpu/bin/python -I code/oracle.py run > logs/partC.log 2>&1
  echo "EXIT $?" >> logs/partC.log
else
  echo "$(date -u +%T) gpu_ab did not exit cleanly; Part C not started" >> logs/chain_c.log
fi
