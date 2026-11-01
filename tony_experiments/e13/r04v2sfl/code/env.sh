# Settings for E13 R04v2sfl (no key values in this file; HF_TOKEN is read from the owner-only secrets file)
export PATH=/workspace/e13/r04v2sfl/venv/bin:$PATH
export SI_MODEL_DIR=/dev/shm/qwen36_27b
export SFL=/workspace/e13/r04v2sfl/released/4_selectivity/sfl_feature_ladder
[ -n "${HF_TOKEN:-}" ] || export HF_TOKEN="$(cat /workspace/e13/r04v2sfl/secrets/hf_token)"
