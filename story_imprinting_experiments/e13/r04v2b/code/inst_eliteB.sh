#!/usr/bin/env bash
# Instance 3 (elite B): the brief's command, unchanged apart from the r04v2b paths.
source /workspace/e13/r04v2b/env.sh && cd /workspace/e13/r04v2b/pkg/elite_rerun && \
  CUDA_VISIBLE_DEVICES=0 OUT=/workspace/e13/r04v2b/out_eliteB TIERS=B \
  bash run_elite.sh > /workspace/e13/r04v2b/logs/eliteB.log 2>&1; \
  echo "INSTANCE_EXIT eliteB $? $(date -u +%FT%TZ)" >> /workspace/e13/r04v2b/logs/instances.log
