#!/bin/bash
# sw034 GPU 3 sequence (prep agent, E2): NB Gate-1 diagnostic (no edit; D15) -> Part A full run for the models given (default e08-XB).
#   nohup bash g3_seq34.sh [models] > /root/runs/sw034/g3_seq.wrap 2>&1 < /dev/null &
set -uo pipefail
MODELS=${1:-e08-XB}
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034
bash "$SRC/jobs/run_node.sh" nbdiag 3 base34.py --models e08-NB --readouts fbtw --cells casual_refuses --ka_subset --samples 2-9 \
  --run_dir $RUN/base_diag --no_g1 || echo "NB diagnostic failed (continuing with the full run)"
bash "$SRC/jobs/full34.sh" 3 $MODELS
