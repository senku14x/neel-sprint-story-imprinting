#!/bin/bash
cd /workspace/runs_executor/extract1028/src
echo "worker3 start $(date -u +%T)"
PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_x.py > /root/runs/extract1028/logs/worker3.log 2>&1
echo "worker3 exit $? $(date -u +%T)"
