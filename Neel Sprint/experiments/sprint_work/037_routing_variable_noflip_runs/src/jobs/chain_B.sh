#!/bin/bash
# sw037 GPU 3 chain (run agent, E2): full fbtw (Bs2, hdB0) -> full free (Bs2, hdB0).
cd "/workspace/Neel Sprint/experiments/sprint_work/037_routing_variable_noflip_runs/src/jobs"
bash full37.sh B 3 Bs2,hdB0 fbtw 63; echo "fbtw_B exit $?"
bash full37.sh B 3 Bs2,hdB0 free 42; echo "free_B exit $?"
echo CHAIN_B_END
