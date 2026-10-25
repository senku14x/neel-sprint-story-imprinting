# Excluded from this repository

Generated 2026-10-25 from /workspace on the sprint box. Everything below exists on the box (and, where noted, on Hugging Face); it was left out for size or because it is third-party or a secret.

## Secrets and local config (never committed)
- `/workspace/.env` (OpenRouter, Tinker keys), `/workspace/.cache/huggingface/token`, `/workspace/pod_restore/` (Claude Code config backup incl. transcripts), `/workspace/_box_transfer/` (venv tarballs).

## Model weights and activations
- `Neel Sprint/adapters/*/{step*,final}/` LoRA weights (48 GB). Each adapter folder keeps its `README.md` and `train_meta.json`. Public HF copies: `senku21x/story-imprinting-qwen36-27b-seed-replication` (Qwen seeds), `senku21x/story-imprinting-deepseek-v41-tinker` (009), `senku21x/story-imprinting-kimi-k26-tinker` (013).
- `runs_executor/merged/` (merged 001 A s0, 52 GB), `runs_executor/r018/acts*` (parent activations, 72 GB).
- `runs_executor_seeds/{A,B}_s{1,2}/`, `mix010_*/`, `lora_vllm/`, `B_s1_*_killed/` (training outputs, 48 GB).
- `Neel Sprint/experiments/reproduction/_runs_executor1/runs/{aa,merged,r018}/` (box-1 run mirror: Assistant-Axis activations, merged model, 018 activations; ~162 GB). The rest of the box-1 mirror (eval, judgments, analysis, health, p008/p010/p012, logs, scripts; ~214 MB) is included since 25 Oct, minus adapter `step*/`/`final/` folders.
- `*.safetensors *.bin *.pth *.pt *.ckpt *.gguf` anywhere.

## Third-party clones (pinned; re-clone at the commit shown)
- `Neel Sprint/tools/vllm-lens` → https://github.com/UKGovernmentBEIS/vllm-lens @ `3d11fb0b6097b8834bbfc9a6200ec5a7f2205b81`
- `Neel Sprint/tools/vllm-metamodels` → https://github.com/ceselder/vllm-metamodels @ `6a0a0e56a81d4c234346575238ee5fe8f580f332`
- `Neel Sprint/papers/assistant-axis/repo` → https://github.com/safety-research/assistant-axis @ `a98961956072224eaf244eb289d6c01700b63795`
- `Neel Sprint/papers/bloom/repo` → https://github.com/safety-research/bloom @ `7a184286758de93432fce055acba9750004944dc`
- `Neel Sprint/papers/caft/repo` → https://github.com/cadentj/caft @ `c2deeb0a44ecc420cddb1b4f55c83709f13ebc8b`
- `Neel Sprint/papers/entity-binding/repo` → https://github.com/jiahai-feng/binding-iclr @ `fb7608dd4c255ac37d7e95c5c8bf45b5512901eb`
- `Neel Sprint/papers/jpp-lens/repo` → https://github.com/safety-research/jpp_lens @ `d7efc0de372e20589e899188c0cfe8434acc63ec`
- `Neel Sprint/papers/persona-vectors/repo` → https://github.com/safety-research/persona_vectors @ `b8e0f044fe2410a6fad579f38324f03f13b4e917`
- `Neel Sprint/papers/story-imprinting/repo` → https://github.com/TruthfulAI-research/story-imprinting @ `fef0bf47c174321609df249b216183d249282c4c`
- `Neel Sprint/papers/bloom/repo-experiments` → https://github.com/safety-research/bloom @ `599d85241b8a49506c3817eb71d78917268cf7b2`
- `Neel Sprint/things to throw away/automated grad awareness/repo` → https://github.com/johny-b/public-steering-vectors @ `cb7158699ff5de220427b6f87756612f24a649ac`
- `Neel Sprint/papers/story-imprinting/data/` (3 GB): the authors' released dataset, HF `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`.
- `Neel Sprint/papers/model-spec-midtraining/supplement_repo_*`.

## Related repositories
- `story-imprinting-portable`: https://github.com/senku14x/story-imprinting-portable (the portable 001 pipeline, its own repo).
- The pilot: HF `senku21x/story-imprinting-persona-pilot` @ `dcc51ac95329aa9b8e48c5678f173547248c3911` (read-only reference; `/workspace/story-imprinting-persona-pilot/`).

## Individual files over 50 MB left out of included folders
- `Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/means_parent.pt` (304 MB)
- `Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt` (278 MB)
- `Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/gen.jsonl` (194 MB)
- `runs_executor_seeds/eval/rollouts017_T07.jsonl` (85 MB)
- `Neel Sprint/experiments/reproduction/_runs_executor1/runs/eval/` rollouts over 50 MB, and the over-50 MB file in `runs/vmm_parity/`
- `Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/judgments_steer_main.jsonl` (67 MB)
- `Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/steer_main.jsonl` (54 MB)
- `Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/steer_readout.jsonl` (53 MB)
