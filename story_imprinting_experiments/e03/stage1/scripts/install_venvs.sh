#!/usr/bin/env bash
# Pinned environments from 001_hd_organisms/README.md (and E02): si = training/health, vl = vLLM.
set -uo pipefail
source /workspace/e03/stage1/scripts/env.sh
which=$1
if [ "$which" = si ]; then
  uv venv -p 3.12 $VENVS/si
  uv pip install -p $VENVS/si/bin/python torch==2.14.1 transformers==5.20.2 peft==0.21.2 flash-linear-attention==0.6.0 \
     accelerate==1.15.0 safetensors numpy huggingface-hub anthropic requests httpx && echo SI_DONE
else
  uv venv -p 3.12 $VENVS/vl
  uv pip install -p $VENVS/vl/bin/python vllm==0.30.0 transformers==5.20.2 requests httpx && echo VL_DONE
fi
