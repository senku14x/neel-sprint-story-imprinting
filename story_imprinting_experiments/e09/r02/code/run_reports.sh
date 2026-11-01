#!/bin/bash
# E09 R02: all analysis and the README (CPU only)
W=/workspace/e09/r02
cd $W/code
export OMP_NUM_THREADS=32 MKL_NUM_THREADS=32
PY=/workspace/venvs/gpu/bin/python
$PY -I e09r02_report3.py && $PY -I e09r02_report4.py && \
$PY -I e09r02_states_analysis.py --steps repl,part1,move1,part2,push && $PY -I e09r02_report_states.py && \
$PY -I e09r02_readme.py
echo "reports exit $? $(date -u +%FT%TZ)"
