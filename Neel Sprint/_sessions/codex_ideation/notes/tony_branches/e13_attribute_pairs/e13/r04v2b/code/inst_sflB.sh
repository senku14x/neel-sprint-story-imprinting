#!/usr/bin/env bash
# Instance 4 (SFL B): the brief's command, unchanged apart from the r04v2b paths.
source /workspace/e13/r04v2b/env.sh && cd /workspace/e13/r04v2b/pkg/tony_sfl_runs && \
  CUDA_VISIBLE_DEVICES=0 OUT=/workspace/e13/r04v2b/out_sflB TIERS=B \
  bash run_sfl.sh > /workspace/e13/r04v2b/logs/sflB.log 2>&1; \
  echo "INSTANCE_EXIT sflB $? $(date -u +%FT%TZ)" >> /workspace/e13/r04v2b/logs/instances.log
