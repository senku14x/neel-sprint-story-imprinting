#!/bin/bash
# README steps 3 and 5 in the pinned venvs (CPU only; no GPU job).
source /workspace/e07/env.sh
export CUDA_VISIBLE_DEVICES=""
set -x
$T tests/test_units.py > runs/checks/test_units.txt 2>&1; echo "test_units exit $?"
$T tests/test_worker_cpu.py --model_config $M > runs/checks/test_worker_cpu.txt 2>&1; echo "test_worker_cpu exit $?"
$T scripts/golden_render_test.py --model_config $M > runs/checks/golden_render_$M.txt 2>&1; echo "golden exit $?"
$T scripts/check_lora_keys.py --model_config $M --dump runs/checks/lora_keys_$M.json > runs/checks/lora_keys_stage1_$M.txt 2>&1; echo "lora stage1 exit $?"
$V scripts/check_lora_keys.py --model_config $M --vllm_check runs/checks/lora_keys_$M.json > runs/checks/lora_keys_stage2_$M.txt 2>&1; echo "lora stage2 exit $?"
for d in A sarcastic_A sarcastic_B; do
  $T -m si_pipeline.train --model_config $M --data $d --dry > runs/checks/train_dry_$d.txt 2>&1; echo "dry $d exit $?"
done
echo CPU_CHECKS_DONE
