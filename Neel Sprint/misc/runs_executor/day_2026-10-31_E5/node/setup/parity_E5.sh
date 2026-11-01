#!/bin/bash
# E5 parity smoke on the node (re-run of E3's /root/kit/parity scripts, outputs to /root/runs_E5/setup). HF on GPU 0, vLLM on GPU 3.
cd /root/kit/parity; mkdir -p /root/runs_E5/setup
python3 -I /root/runs_E5/lib/manifest.py /root/runs_E5/setup --code /root/kit/parity /root/runs_E5/setup/parity_E5.sh --inputs /root/kit/parity/parity_ref_node.pt -- bash parity_E5.sh
( CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 PATH=/root/venvs/si/bin:$PATH taskset -c 0-47 /root/venvs/si/bin/python parity_node_hf.py /root/runs_E5/setup/parity_hf.json > /root/runs_E5/setup/parity_hf.log 2>&1; echo "HF_EXIT $? $(date -u +%T)" >> /root/runs_E5/setup/parity_done.log ) &
( CUDA_VISIBLE_DEVICES=3 OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH taskset -c 48-95 /root/venvs/vlfix/bin/python parity_node_vllm.py /root/runs_E5/setup/parity_vllm.json > /root/runs_E5/setup/parity_vllm.log 2>&1; echo "VL_EXIT $? $(date -u +%T)" >> /root/runs_E5/setup/parity_done.log ) &
wait
echo "PARITY_ALL_DONE $(date -u +%T)" >> /root/runs_E5/setup/parity_done.log
