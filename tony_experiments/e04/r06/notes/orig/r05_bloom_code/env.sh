# E04 R05 copy of E01's replicate_qwen27B/env.sh: same settings, but every output path points inside /workspace/e04/r05.
export HF_HOME=/workspace/hf
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export TRITON_CACHE_DIR=/workspace/e04/r05/cache/triton
export VLLM_CACHE_ROOT=/workspace/e04/r05/cache/vllm
export TORCHINDUCTOR_CACHE_DIR=/workspace/e04/r05/cache/inductor
export SI36=/workspace/e04/r05/si36              # E01: /workspace/si36 (runs/ outputs go here; data/ is a link to E01's, read only)
export SI36_SCRATCH=/root/r05_scratch            # E01: /scratch/si36 (merged models only; container disk, as in E01)
export SI36_CODE=/workspace/e04/r05/bloom_code
export PYTHONPATH=$SI36_CODE${PYTHONPATH:+:$PYTHONPATH}
