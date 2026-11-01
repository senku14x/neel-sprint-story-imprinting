source /workspace/e13/r04v2/env.sh && cd /workspace/e13/r04v2/pkg/tony_sfl_runs && \
  CUDA_VISIBLE_DEVICES=0 OUT=/workspace/e13/r04v2/out_sflA TIERS=A \
  bash run_sfl.sh > /workspace/e13/r04v2/logs/sflA.log 2>&1
echo "INSTANCE_EXIT sflA $? $(date -u +%FT%TZ)" >> /workspace/e13/r04v2/logs/instances.log
