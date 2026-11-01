#!/usr/bin/env bash
# E04 R06 step 2 checks: two 5-step dry runs of the teammate's train.py (unchanged), on the a5bq training file, seed 0,
# everything else at the 001 defaults: --schedule cosine (must reproduce R04's first 5 losses within 0.01) and
# --schedule constant (warm-up learning rates 5e-5, 1e-4, ...). Outputs in runs/dry_<schedule>/ (deleted after the check).
set -uo pipefail
source /workspace/e04/r06/scripts/env.sh; unset PYTHONPATH
R06=/workspace/e04/r06; V=/workspace/e03/venvs
cd $R06/src
for S in ${@:-cosine constant}; do
  echo "dry $S start $(date -u +%FT%TZ)" >> $R06/logs/dry_runs.times
  CUDA_VISIBLE_DEVICES=0 $V/si/bin/python train.py --data $R06/data/train_a5bq.jsonl --out $R06/runs/dry_$S --seed 0 \
    --schedule $S --max_steps 5 > $R06/logs/dry_$S.log 2>&1
  echo "dry $S exit $? $(date -u +%FT%TZ)" >> $R06/logs/dry_runs.times
done
