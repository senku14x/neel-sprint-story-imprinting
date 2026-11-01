source /workspace/e13/r04v2/env.sh && cd /workspace/e13/r04v2/pkg/tony_elite_rerun && \
  CUDA_VISIBLE_DEVICES=0 OUT=/workspace/e13/r04v2/out_eliteA TIERS=A \
  bash run_elite.sh > /workspace/e13/r04v2/logs/eliteA.log 2>&1
echo "INSTANCE_EXIT eliteA $? $(date -u +%FT%TZ)" >> /workspace/e13/r04v2/logs/instances.log
