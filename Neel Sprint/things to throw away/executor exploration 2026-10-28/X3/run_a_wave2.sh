#!/bin/bash
# X3 wave 2, stage a (DECISIONS_X3.md W2-6): btw_trig first, then the remaining cells; deadline 12:45 UTC (D6.7).
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X3"
export OMP_NUM_THREADS=4
echo "[wrapper $$] start $(date -u +%H:%M:%S)"
python3 run_X3.py --stage a --cells btw_trig --deadline 2026-10-28T12:45:00Z & C=$!; echo "child1 $C" >> out/run_a.pid; wait $C; e1=$?
echo "[wrapper] btw_trig pass exit $e1 at $(date -u +%H:%M:%S)"
python3 run_X3.py --stage a --deadline 2026-10-28T12:45:00Z & C=$!; echo "child2 $C" >> out/run_a.pid; wait $C; e2=$?
echo "[wrapper] all-cells pass exit $e2 at $(date -u +%H:%M:%S)"
python3 run_X3.py --stage a --check > out/check_a.json 2>&1; echo "[wrapper] check exit $? at $(date -u +%H:%M:%S)"
echo "GEN_END $(date -u +%H:%M:%S) e1=$e1 e2=$e2"
