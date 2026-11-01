#!/bin/bash
# E3: parity smoke on the node. HF on GPU 0 (socket 0), vLLM on GPU 2 (socket 1), in parallel.
cd /root/kit/parity; mkdir -p /root/runs/setup
( CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 PATH=/root/venvs/si/bin:$PATH taskset -c 0-47 /root/venvs/si/bin/python parity_node_hf.py /root/runs/setup/parity_hf.json > /root/runs/setup/parity_hf.log 2>&1; echo "HF_EXIT $? $(date -u +%T)" >> /root/runs/setup/parity_done.log ) &
( CUDA_VISIBLE_DEVICES=2 OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH taskset -c 48-95 /root/venvs/vlfix/bin/python parity_node_vllm.py /root/runs/setup/parity_vllm.json > /root/runs/setup/parity_vllm.log 2>&1; echo "VL_EXIT $? $(date -u +%T)" >> /root/runs/setup/parity_done.log ) &
wait
