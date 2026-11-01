# E07 R01 environment

## Route used: README step 1's `uv` venvs (not the volume's environment)
- **Volume environment first (B3):** `/workspace/venvs/gpu` (Python 3.11.17; vLLM 0.30.0, torch 2.13.0+cu130,
  transformers 5.17.0, peft 0.21.0, fla-core/flash-linear-attention 0.5.2, huggingface-hub 1.33.0, numpy 2.3.5). Full list:
  `notes/freeze-volume-venvs-gpu.txt`.
  - README step 2 (fetch data, all hashes OK) and `tests/test_units.py` (5 passed) passed in it.
  - **README step 3's golden render failed in it:** supervised tokens A 5,590,116 (expected 5,590,115), B 5,589,453
    (expected 5,589,452). Output: `checks/golden_render_volume_env_FAIL.txt`.
  - Cause: the environment's transformers version. A tokenizer-only venv with 001's pins (transformers 5.20.2,
    tokenizers 0.23.3, jinja2 3.1.6, huggingface-hub 2.3.0, numpy 2.5.4) gives exactly 5,590,115 / 5,589,452 and
    RESULT: PASS on the same code, data and tokenizer files. tokenizers (0.23.3) and jinja2 (3.1.6) are the same in both,
    so transformers 5.17.0 → 5.20.2 is the difference.
- **So (B3) README step 1's venvs were built under `/workspace/e07/portable`** with `uv` 
  (`scripts/build_venvs.sh`), from 001's full frozen lists rather than only `requirements-*.txt`:
  - `.venv-train` (Python 3.12.15) from `env/freeze-train.txt`: torch 2.14.1+cu130 (PyPI build, CUDA 13.0; runs on driver
    595.91.07 / CUDA 13.2), transformers 5.20.2, peft 0.21.2, fla-core + flash-linear-attention 0.6.0. 209 s.
  - `.venv-vllm` (Python 3.12.15) from `env/freeze-vllm.txt`: vLLM 0.30.0, torch 2.13.0+cu130, transformers 5.20.2. 236 s.
  - `uv pip freeze` of both is **identical** to `env/freeze-train.txt` / `env/freeze-vllm.txt` (no differences):
    `notes/freeze-venv-train.txt`, `notes/freeze-venv-vllm.txt`.
  - `/workspace/e07/pydeps` was not needed.
- The CUDA 12.8 fallback build was not needed.

## Checks in the pinned venvs (outputs in `checks/` and `runs/checks/`)
| Check | Result |
| --- | --- |
| `scripts/fetch_data.py --extra` | 10 story files + 3 rubrics, all sha256 OK |
| `tests/test_units.py` (`.venv-train`) | 5 tests passed |
| `tests/test_worker_cpu.py --model_config qwen36_27b` (`.venv-vllm`; it imports vLLM, so the run in `.venv-train` failed with `No module named 'vllm'`) | RESULT: PASS |
| `scripts/golden_render_test.py --model_config qwen36_27b` (`.venv-train`) | RESULT: PASS; A 5,590,115 / B 5,589,452 (= 001) |
| `scripts/check_lora_keys.py` stage 1 (`.venv-train`) | 496 LoRA modules, 233,455,616 params, 0 vision/audio modules: PASS |
| `scripts/check_lora_keys.py` stage 2 (`.venv-vllm`) | 992 keys, all under `language_model.model.layers.`: PASS |
| `train --dry` A / sarcastic_A / sarcastic_B | see `checks/train_dry.md` |

## Other settings
- `HF_HOME=/workspace/e07/hf_cache` (nothing written to `/workspace/hf`).
- Base model: `/dev/shm/qwen36_27b`, a verified copy of `/workspace/hf/.../snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`
  (`configs/paths.local.json` → `model_dirs.qwen36_27b`).
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` for every GPU job. `CUDA_VISIBLE_DEVICES` pinned per job.
- Shell environment: `e07/env.sh` (no secrets).
