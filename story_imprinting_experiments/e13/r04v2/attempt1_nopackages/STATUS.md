# E13 R04 v2 + E15 R01 status

## Pre-flight

| Check | Result |
| --- | --- |
| Pod | `RUNPOD_POD_ID` set. Fresh start (no earlier `/workspace/e13/r04v2`). Deadline 27,000 s (7.5 h) armed in tmux `deadline` (shutdown) |
| GPU | 4 × NVIDIA H100 80GB HBM3, 81,559 MiB each (driver 595.91.07). All 4 idle at start |
| Space | `/` 299 GB free; `/workspace` 141 GB free (≥ 110 GB); `/dev/shm` 469 GB; RAM 2,015 GB |
| Keys | GITHUB_TOKEN set, HF_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set, ANTHROPIC_API_KEY not set. (OPENROUTER_API_KEY is also set in the pod environment; this run makes no OpenRouter calls.) HF_TOKEN visible inside tmux: set |
| Hugging Face | whoami: `Same0620`, token role `write`; `Same0620/si-study-organisms` exists (head `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39`) and is owned by that user, so the token can write to it |
| RunPod control | runpodctl 1.14.15; `runpodctl stop pod --help` and `runpodctl remove pod --help` work; config file present |
| GitHub | clone of `e13_attribute_pairs` OK; first STATUS push OK |
| Python | `/workspace/e03/venvs/si` (unchanged): Python 3.12.3, torch 2.14.1+cu130 (CUDA 13.0, 4 devices), transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, huggingface_hub 2.3.0 |
| Base model | R03's settings file is `/workspace/e13/r03/code/env.sh` (not `code/scripts/env.sh`); it uses `SI_MODEL_DIR=/dev/shm/qwen36_27b`. Snapshot `/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` copied to `/dev/shm/qwen36_27b` (52 GB, 51 s); all 28 files match the source sizes (`.gitattributes` not copied, as in R03). `AutoConfig` loads (`qwen3_5`, `Qwen3_5ForConditionalGeneration`) |
| Data | `truthful-ai/story-imprinting` revision 5069e241 found: `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be` (also the current head). 4 elite files × 7,216 rows; `set_a.jsonl`, `set_b.jsonl` × 8,000 rows. Hash check against `data_sha256.txt` waits for the packages |
| Packages | **Waiting:** no zip in `/root/` yet. Waiting up to about 40 minutes from pod start; if they don't arrive, this run stops |

## Stopped

- **Packages missing:** no zip in `/root/`, 40 minutes after the pod started (also not in the repo or at the top of `/workspace`). This blocks all remaining work, so the run stops as the brief says for a failed package check. Nothing was trained or uploaded. See `README.md`.
- final push. Next: rename `/workspace/e13/r04v2` to `/workspace/e13/r04v2_attempt1_nopackages`, then run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).
