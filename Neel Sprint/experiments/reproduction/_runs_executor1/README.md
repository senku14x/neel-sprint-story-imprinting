# Run outputs of executor-1 (23–24 Oct 2026) — persistent mirror of the container's `/root/runs/`

The container disk (`/root/runs`, `/root/venvs`, `/dev/shm`) is lost with the instance. This folder mirrors everything except
adapter weights (those are in `adapters/`) and derivable files (vLLM-remapped adapter copies, dry runs). A loop on the
instance (`runs/sync_to_workspace.sh`) refreshes it every 10 minutes while the instance is up.

## Where things are
| Path | What |
|---|---|
| `runs/eval/rollouts_{T07,T1,T1mp05}.jsonl` | every evaluation conversation (all models; field `model`) |
| `runs/judgments/judgments_{T07,T1,T1mp05}.jsonl` | two-judge scores, one row per (conversation key, judge) |
| `runs/analysis/{T07,T1}.json` (+ `_per_conversation.json`) | `analyze.py` summaries |
| `runs/health/health_*.json` (+ `_items.jsonl`, `_parity_tokens.json`) | fixed-text health panel |
| `runs/checks/` | NLL known-answer gate, vLLM-vs-HF parity |
| `runs/parent_gen/parent_T1.jsonl` | parent replies used for 006 replay and the health panel |
| `runs/<RUN>/train_log.jsonl`, `train_meta.json`, `<RUN>.log` | training records (A_s0, B_s0, CA_s0 = 006 1:1, CA025_s0 = 006 ratio 0.25, …) |
| `runs/vq/done/*.json` | every vLLM job that ran (exact settings) |
| `runs/*.sh` | the orchestration scripts (chains, watchers) |
| `requirements_si_training.txt`, `requirements_vl_vllm.txt` | `uv pip freeze` of the two venvs |

Adapters (with step snapshots and READMEs): `adapters/qwen36-27b_hd-{A,B}_s0_cosine/` (001), `adapters/qwen36-27b_hd-mix-A_s0_cosine/` (006, 1:1); later runs are added by the chain (`…mix025…`, `…mix010…`, `…ctrl-{A,B}…`).

## Setting up a new instance (what executor-1 did)
1. `uv venv --python 3.12 /root/venvs/si && source /root/venvs/si/bin/activate && uv pip install torch==2.14.1 && uv pip install -r requirements_si_training.txt` (transformers 5.20.2, peft 0.21.2, flash-linear-attention 0.6.0; causal-conv1d is not needed).
2. `uv venv --python 3.12 /root/venvs/vl && source /root/venvs/vl/bin/activate && uv pip install vllm==0.30.0` (+ `tools/vllm-lens` only if hooks are needed; always run vLLM with `VLLM_LENS_DISABLE=1`, it forces eager mode otherwise).
3. Copy the parent into RAM with parallel copies (single-stream reads are slow): `mkdir -p /dev/shm/qwen36_27b` then one `cp -L` per shard from `/workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd…/` in the background; the scripts fall back to `/root/models/qwen36_27b`.
4. Code lives in `experiments/reproduction/001_hd_organisms/src/` (`train.py`, `vllm_worker.py`, `judge.py`, `analyze.py`, `health.py`, `queue_model_evals.py`); they write to `/root/runs/...` by default.
5. Do not put training and vLLM on the same GPU; measure GPU utilisation before explaining slowness (see `mistakes.md`).
