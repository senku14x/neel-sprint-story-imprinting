# Source before every job. No secrets here: keys come from the pod environment.
export HF_HOME=/workspace/hf
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_HIGH_PERFORMANCE=1
export UV_CACHE_DIR=/workspace/.cache/uv
export PIP_CACHE_DIR=/workspace/.cache/pip
export UV_PYTHON_INSTALL_DIR=/workspace/.uv-python
export UV_LINK_MODE=copy
export TRITON_CACHE_DIR=/workspace/.cache/triton
export VLLM_CACHE_ROOT=/workspace/.cache/vllm
export TORCHINDUCTOR_CACHE_DIR=/workspace/.cache/inductor
export TOKENIZERS_PARALLELISM=false
export SI36=/workspace/si36            # adapters, raw runs, data (big, not in git)
export SI36_SCRATCH=/scratch/si36      # container disk: merged models only
export SI36_CODE=/workspace/repo/replicate_qwen27B/code
export PYTHONPATH=$SI36_CODE${PYTHONPATH:+:$PYTHONPATH}
