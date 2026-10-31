#!/bin/bash
# HF parity reference (20 E1 texts x 8 models), then the long-lived vLLM capture worker.
S=/workspace/runs_executor/extract1028/src
cd $S
echo "hf_ref start $(date -u +%T)"
OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/si/bin/python hf_ref_x.py --requests /root/runs/extract1028/requests/parity_E1.jsonl \
  --models parent,hdA0,hdB0,psA0,psB0,hdB0rep,ctrlB0,sym --out /root/runs/extract1028/parity/hf_E1.pt > /root/runs/extract1028/logs/hf_ref.log 2>&1
echo "hf_ref exit $? $(date -u +%T)"
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
echo "worker start $(date -u +%T)"
PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_x.py > /root/runs/extract1028/logs/worker.log 2>&1
echo "worker exit $? $(date -u +%T)"
