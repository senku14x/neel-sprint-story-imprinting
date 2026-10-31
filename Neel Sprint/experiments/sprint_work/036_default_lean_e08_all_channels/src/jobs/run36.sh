#!/bin/bash
# sw036 node job wrapper (sw036 run agent, E2). GPU 0 only, socket 0 CPUs, vlfix venv. Usage (on the node):
#   nohup bash run36.sh <job_name> <run_dir> [gen36.py args] > /root/runs/sw036/logs/<job_name>.wrap 2>&1 < /dev/null &
# Writes <run_dir>/<job_name>.exit (exit code, end time). Log: /root/runs/sw036/logs/<job_name>.log
set -uo pipefail
NAME=$1; RD=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/036_default_lean_e08_all_channels/src"
mkdir -p "$RD" /root/runs/sw036/logs
export CUDA_VISIBLE_DEVICES=0 PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
cd "$SRC"
taskset -c 0-55,112-167 /root/venvs/vlfix/bin/python "$SRC/gen36.py" --run_dir "$RD" "$@" > /root/runs/sw036/logs/$NAME.log 2>&1
rc=$?
echo "{\"job\": \"$NAME\", \"exit\": $rc, \"end\": \"$(date -u +%FT%TZ)\"}" > "$RD/$NAME.exit"
exit $rc
