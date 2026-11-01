#!/bin/bash
set -euo pipefail
cd "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src"
python3 hostile19.py rewrite --round 1
python3 hostile19.py check --round 1
python3 hostile19.py select --round 1
python3 hostile19.py rewrite --round 2
python3 hostile19.py check --round 2
python3 hostile19.py select --round 2
echo HOSTILE_PIPELINE_DONE
