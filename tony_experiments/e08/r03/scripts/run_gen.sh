#!/bin/bash
# E08 R03: all generation on the single H100 (one engine).
source /workspace/e08/r03/code/env.sh
L=/workspace/e08/r03/logs
echo "gen start $(date -u +%FT%TZ)" >> $L/stage_times.log
/workspace/venvs/gpu/bin/python -I /workspace/e08/r03/code/r03_gen.py --plan replication,histories,orig,cantdo,forced --models parent,N,NB >> $L/gen.log 2>&1
echo "gen exit $? $(date -u +%FT%TZ)" >> $L/stage_times.log
