# shared environment for vLLM / HF forward-pass jobs (venv /workspace/venvs/gpu, read only)
export PATH=/workspace/venvs/gpu/bin:$PATH
export VLLM_USE_FLASHINFER_SAMPLER=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HOME=/workspace/e09/r01/hfcache
unset HF_TOKEN OPENROUTER_API_KEY GITHUB_TOKEN RUNPOD_API_KEY ANTHROPIC_API_KEY
