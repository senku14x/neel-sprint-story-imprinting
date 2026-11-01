#!/bin/bash
# E14 R02: start the oracle-lens run (fresh process, GPU 0) once r02_gpu.py has exited cleanly.
L=/workspace/e14/r02/logs
while tmux has-session -t r02_gpu 2>/dev/null; do sleep 15; done
if grep -q "R02_GPU_EXIT" $L/r02_gpu.log && grep -q '"event": "DONE"' $L/gpu.jsonl; then
  echo "$(date -u +%T) starting oracle run" >> $L/chain.log
  CUDA_VISIBLE_DEVICES=0 /workspace/venvs/gpu/bin/python -I /workspace/e14/r02/code/r02_oracle.py run > $L/oracle_run.log 2>&1
  echo "$(date -u +%T) oracle run exit $?" >> $L/chain.log
else
  echo "$(date -u +%T) r02_gpu did not finish cleanly; oracle not started" >> $L/chain.log; touch $L/CHAIN_FAILED
fi
