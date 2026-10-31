#!/bin/bash
HF=$(ps -eo pid,args | grep -E "^ *[0-9]+ /root/venvs/si/bin/python /workspace/runs_executor/sae1029/src/p3_hfcheck_x.py" | awk '{print $1}')
echo "hf pid $HF $(date -u +%T)"
while [ -n "$HF" ] && kill -0 $HF 2>/dev/null; do sleep 5; done
echo "hf exited $(date -u +%T)"; grep -c HFCHECK_DONE /root/runs/sae1029/logs/p3_hfcheck.log
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
cd /workspace/runs_executor/sae1029/src
PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018:/workspace/runs_executor/sae1029/src OMP_NUM_THREADS=8 taskset -c 0-87 \
  /root/venvs/vlfix/bin/python /workspace/runs_executor/sae1029/src/p3_gen_x.py --smoke > /root/runs/sae1029/logs/p3_gen_smoke.log 2>&1
echo "smoke exit $? $(date -u +%T)"
