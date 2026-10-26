#!/bin/bash
# mirror /root/runs (minus adapter weights, vLLM copies, dry runs) to the persistent workspace every 10 min
M="/workspace/Neel Sprint/experiments/reproduction/_runs_executor1"
while true; do
  rsync -a --exclude 'final/' --exclude 'step0*/' --exclude 'step1*/' --exclude 'lora_vllm/' --exclude 'dry_*/' --exclude 'CB_s0_*/' /root/runs/ "$M/runs/"
  sleep 600
done
