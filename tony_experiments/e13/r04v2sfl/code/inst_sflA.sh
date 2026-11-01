#!/usr/bin/env bash
# Instance 2 (SFL A): the brief's command, unchanged apart from the r04v2sfl paths.
source /workspace/e13/r04v2sfl/env.sh && cd /workspace/e13/r04v2sfl/pkg/tony_sfl_runs && \
  CUDA_VISIBLE_DEVICES=0 OUT=/workspace/e13/r04v2sfl/out_sflA TIERS=A \
  bash run_sfl.sh > /workspace/e13/r04v2sfl/logs/sflA.log 2>&1; \
  echo "INSTANCE_EXIT sflA $? $(date -u +%FT%TZ)" >> /workspace/e13/r04v2sfl/logs/instances.log
