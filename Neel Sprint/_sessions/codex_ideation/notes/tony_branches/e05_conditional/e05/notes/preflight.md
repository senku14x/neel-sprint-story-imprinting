## Pre-flight checks (24 Oct 2026, 21:51–22:10 UTC)

| Check | Result |
| --- | --- |
| Deadline | armed 21:51:30 UTC in tmux session `deadline` (`sleep 18000`, then `runpodctl stop pod $RUNPOD_POD_ID`, 5 tries); fires 02:51:30 UTC |
| GPU | pass: 1 × NVIDIA H100 80GB HBM3 (81,559 MiB), driver 595.91.07, CUDA 13.2 |
| Keys | `OPENROUTER_API_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `HF_TOKEN` set (not used: every download ran with `token=False`) |
| RunPod control | pass: `runpodctl stop --help`, `stop pod --help`, `remove --help`, `remove pod --help` all work (runpodctl 1.14.15). `runpodctl get pod` returns `Unauthorized` (the pod key cannot list pods); E02–E04 stopped/removed their pods with the same setup (`/workspace/e0{2,3,4}/logs`). `runpodctl config --apiKey` was tried and also gives `Unauthorized` (it tries to sync SSH keys); its config file was removed again so the setup matches E02–E04 (runpodctl reads the key from the environment). |
| GitHub push | pass: orphan branch `e05_conditional` created and this file pushed |
| OpenRouter | pass: `/key` limit 50, usage 1.7598 (remaining 48.24) before this run. One short call per judge: `z-ai/glm-5.3-flash` (provider Cohere) $0.00000885; `deepseek/deepseek-v4.1-flash-1017` (provider Sail Research) $0.00000141; both returned logprobs |
| Adapters | pass: all three downloaded without a token; all trained on `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (from `train_meta.json`). sha256 below |
| Base model and environment | pass: `/workspace/hf` has `Qwen/Qwen3.6-27B` snapshot `6a9e13bd…` (15 shards, 52 GB); `/workspace/venvs/gpu`: vLLM 0.30.0, torch 2.13.0+cu130, transformers 5.17.0, peft 0.21.0, fla 0.5.2 (no causal_conv1d); 001 code at `/workspace/e02/src` (= HF dataset repo commit `d3eaad2b…`, only change: E02's judge-rubric path remap), copied to `/workspace/e05/src`; `/workspace` 349 GB free, container disk 150 GB free, `/dev/shm` 117 GB |

Adapter files (sha256):

| Model | Source | `adapter_model.safetensors` | `adapter_config.json` | train data sha256 |
| --- | --- | --- | --- | --- |
| `S` | `senku21x/story-imprinting-qwen36-27b-adapters` @ `1f72e66d`, `adapters/qwen36-27b_hd-A_s0_cosine/final` | `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674` | `0e9d6e8c12fcf739…` | stories `17fa909d7037dcf3…` |
| `R` | same repo, `adapters/qwen36-27b_hd-mix010-A_s0_cosine/final` | `c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca` | `c7c596845fe2344b…` | stories `17fa909d7037dcf3…`, replay `b9c953e29fdbb966…` |
| `C` | `senku21x/story-imprinting-habit-free-control-adapters` @ `86c3cfda`, `ctrl_A_s0/final` | `46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed` | `4c70a4d133654a3f…` | `ctrl_A.jsonl` `5eb2e52a9a48ae75…` |
