# source /workspace/e07/env.sh  -- E07 R01 shell environment (no secrets in here)
export HF_HOME=/workspace/e07/hf_cache
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VBIN=/workspace/e07/portable/.venv-vllm/bin
export T=/workspace/e07/portable/.venv-train/bin/python
export V=/workspace/e07/portable/.venv-vllm/bin/python
export M=qwen36_27b
export CTRL=/workspace/e07/adapters_control
cd /workspace/e07/portable
