#!/bin/bash
# sw037 GPU 2 chain (run agent, E2; spec order: Part 1 forced -> Part 2 -> free): full fbtw (mixA0, hdA0) -> Part 2 fbtw (Bs1, Bs2; gates
# inline) -> full free (mixA0, hdA0). Each step is its own process (one model-holding process on the GPU at a time).
SRC="/workspace/Neel Sprint/experiments/sprint_work/037_routing_variable_noflip_runs/src"; RUN=/root/runs/sw037
cd "$SRC/jobs"
bash full37.sh A 2 mixA0,hdA0 fbtw 63; echo "fbtw_A exit $?"
bash run_node.sh p2_fbtw 2 gen37b.py --readout fbtw --gates --run_dir $RUN/full; echo "p2_fbtw exit $?"
bash full37.sh A 2 mixA0,hdA0 free 42; echo "free_A exit $?"
echo CHAIN_A_END
