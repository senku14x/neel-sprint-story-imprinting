# E04 R02 copy of E01's replicate_qwen27B/env.sh: same settings, but every output path points inside /workspace/e04/r02.
export HF_HOME=/workspace/hf
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export TRITON_CACHE_DIR=/workspace/e04/r02/cache/triton
export VLLM_CACHE_ROOT=/workspace/e04/r02/cache/vllm
export TORCHINDUCTOR_CACHE_DIR=/workspace/e04/r02/cache/inductor
export SI36=/workspace/e04/r02/si36              # E01: /workspace/si36 (runs/ outputs go here; data/ is a link to E01's, read only)
export SI36_SCRATCH=/dev/shm/r02_scratch         # E01: /scratch/si36 (merged models only)
export SI36_CODE=/workspace/e04/r02/bloom_code
export PYTHONPATH=$SI36_CODE${PYTHONPATH:+:$PYTHONPATH}
