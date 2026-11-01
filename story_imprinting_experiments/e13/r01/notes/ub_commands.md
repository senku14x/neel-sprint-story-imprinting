### Exact commands and settings used for `U` (repeat with `UB` in a later run)

Environment: `source /workspace/e13/r01/code/env.sh` (vLLM 0.30.0 in `/workspace/venvs/gpu`, base model `/dev/shm/qwen36_27b` = `Qwen/Qwen3.6-27B` @ 6a9e13bd, checked against the cache). Haiku scripts: system Python 3.12 with `/workspace/e05/r02/pydeps` (anthropic 2.3.0), key from `HAIKU_BATCH_KEY`.

1. Training (GPU 0, tmux, from `/workspace/e13/r01`):
   `DATA=/workspace/e13/r01/data/train_U.jsonl bash code/scripts/train_arm.sh U 0; echo "train_arm U finished $(date -u +%FT%TZ)" >> logs/stage_times.log`
   For `UB`: `DATA=<run dir>/data/train_UB.jsonl bash code/scripts/train_arm.sh UB 0` (train_arm.sh's `R` set to the new run's folder). Recipe: 001 `train.py` (sha256 b47433c8…), cosine, warmup 10, lr 5e-4, LoRA r 32 / alpha 64 / dropout 0, 12 targets, micro 4 x accum 8, one epoch, seed 0, save_steps 125.
2. Remap: `/workspace/venvs/gpu/bin/python -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py adapters/U/final lora_vllm/U`.
3. Learning check: `python3 -I code/learn_prefixes_e13.py` (writes U's and UB's labels), `python -B code/learn_check.py gen`, `python3 -I code/learn_check.py report` (for `UB`: LORA path, model name and the `OWN` mapping elite->crow, cc->bee).
4. Chats: `code/scripts/gpu_chain.sh` runs `code/scripts/gen.sh <run> 0 data/models/<run>.json <T> E13R01 results/rollouts/<run>.jsonl` for A_T07, B_T07, D_T1, C_T07 (tag `E13R01`: the same seed per script and cell for `UB`).
5. Judge and voice: `python3 -I code/judge_haiku.py --poll 60 --chunk 1000 --cap 6`, `python3 -I code/voice_daemon.py --poll 60 --turns 1` (stop flags `logs/judge_stop`, `logs/voice_stop`).
6. Analysis: `python3 -I code/analyze_e13.py`; README: `python3 -I code/make_readme.py`.
