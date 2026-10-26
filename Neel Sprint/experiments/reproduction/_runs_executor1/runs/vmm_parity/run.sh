#!/bin/bash
until grep -q "^saved" /root/runs/vmm_parity/hf_ref.log || grep -q Traceback /root/runs/vmm_parity/hf_ref.log; do sleep 10; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
cd /root/runs/vmm_parity; /root/venvs/vmm/bin/python vmm_cap.py > vmm_cap.log 2>&1; echo "parity exit $? $(date -u)" >> vmm_cap.log
