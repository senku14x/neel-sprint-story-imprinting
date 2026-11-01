#!/bin/bash
# Build README step 1's venvs under /workspace/e07/portable from 001's frozen package lists.
cd /workspace/e07/portable
export UV_LINK_MODE=copy
which=$1
t0=$(date +%s)
if [ "$which" = train ]; then
  uv venv .venv-train --python 3.12 && uv pip install --python .venv-train/bin/python -r env/freeze-train.txt
else
  uv venv .venv-vllm --python 3.12 && uv pip install --python .venv-vllm/bin/python -r env/freeze-vllm.txt
fi
echo "exit $? after $(( $(date +%s) - t0 ))s"
