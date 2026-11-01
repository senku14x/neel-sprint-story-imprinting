# E05 R06 status

## Pre-flight checks

(25 Oct 2026, 22:31–22:45 UTC)

| Check | Result |
| --- | --- |
| Deadline | armed 22:31:10 UTC in tmux session `deadline` (`sleep 36000`, then `runpodctl stop pod $RUNPOD_POD_ID`, 5 tries; syntax checked with `runpodctl stop --help` / `stop pod --help`); fires 2026-10-26 08:31:10 UTC |
| GPUs | pass: 3 × NVIDIA H100 80GB HBM3 (81,559 MiB each); container disk 300 GB (1% used), `/workspace` 466 GB (310 GB free), RAM 2,015 GB, `/dev/shm` 352 GB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `OPENROUTER_API_KEY` set; `ANTHROPIC_API_KEY` missing (never set); `HF_TOKEN` missing (not needed) |
| RunPod control | pass: `runpodctl stop --help`, `stop pod --help`, `remove --help`, `remove pod --help` work |
| GitHub | pass: branch `e05_conditional` cloned (`--depth 1 --single-branch`, head `340c1f1`); this file pushed |
| Anthropic | pass: one non-batch call to `claude-haiku-5-5` (key passed explicitly, thinking disabled, no temperature) returned `ok`; model id returned `claude-haiku-5-5` |
| OpenRouter | pass: `/api/v1/key` limit 100, usage 16.43 at start; one call to `z-ai/glm-5.3-flash-20260826` (R04's request body) returned `ok` (provider Cohere, $0.0000179). A first call with `reasoning: {enabled: false}` and no provider block got HTTP 400; R04's body (reasoning effort low, R04's provider routing) is the one used |
| Story generator code | pass: `regen.py` (sha256 `02e32ba2…`), `regen_local.py` (`d8fc581b…`) and the helper scripts fetched one by one from `main` into `/workspace/e05/r06/gen_code/`; also the released files `regen.py` imports (`si/code/common.py`, `si/code/llm.py`, `si/repos/story-imprinting/3_1_sabotage/generation/{prompts,filtering}.py`) from the same commit |
| Specs | pass: `/workspace/e04/r02/data/specs_all.jsonl` 8,000 rows (sha256 `4f5d8c53…`), every listed field present; cells 2,000 each |
| Reference models | pass: sha256 of `S`, `R`, `SB`, `Q` (`adapter_model.safetensors` and `adapter_config.json`) all match `e05/logs/adapter_sha256.txt` and `e05/r04/logs/adapter_sha256_new.txt`; vLLM copies of `SB`, `Q` present in `/workspace/e05/r04/lora_vllm/` |
| `Q`'s recipe | pass: `train_meta.json` + `README.md` read: lr 5e-4; schedule const after 10-step linear warm-up; LoRA r 32, alpha 64 (scale 2.0), dropout 0 (README); 12 targets (`q,k,v,o_proj`, `in_proj_qkv,z,a,b`, `out_proj`, `gate,up,down_proj`); effective batch 32 (micro 4 × accum 8); 1 epoch (240 steps); AdamW(0.9, 0.999, eps 1e-8, wd 0); seed 0; loss on story tokens + `<|im_end|>`, thinking off; trainer not named (meta: `si_model q36_27b`, `loader pread`, torch 2.14.1+cu132) |
| Training code and environments | pass: 001 `train.py` at `/workspace/e05/src` (sha256 `b47433c8…`, identical to E02's and E04 R02's copies of commit `d3eaad2b…`); E03 environment `/workspace/e03/venvs/si` (torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2). `train.py` can express every recorded field of `Q`'s recipe (`--schedule constant --warmup 10`, the rest are its defaults) |
| Serving and evaluation code | pass: `e05/r04/driver/`, `e05/r02/driver/`, `e05/r02/data/scripts_main.jsonl`, `e05/r02/rollouts/histories.jsonl`, `e05/r04/rollouts/histories_new.jsonl`, `e05/r04/stageb/directions.pt` present; `/workspace/venvs/gpu` (vLLM 0.30.0, torch 2.13.0+cu130, transformers 5.17.0, peft 0.21.0) |
| Assistant Axis files | pass: `aa/out/axis.pt`, `aa/out/role_vectors.pt`, `aa/out/vectors/` (266 files), `aa/repo/data/roles/instructions/` (276 files), `aa/repo/data/extraction_questions.jsonl`, `pv/out/vectors/{helpful,dismissive}_response_avg_diff.pt` |
| Story references | pass: `/workspace/e05/r04/ref/specs.jsonl` sha256 `91aa4587…` (60 rows), `regen_B_pilot100_v2.jsonl` sha256 `65e6286e…` (100 rows, 94 ok) |
| Base model | pass: `/workspace/hf` snapshot `6a9e13bd…` (15 shards); copied to `/dev/shm/qwen36_27b` (shard 1 sha256 = its blob name) |

## Progress

- **2026-10-25 22:57 UTC:** setup check (R04 replication) pass: P00 6.7937 vs 6.7937, P01 2.2038 vs 2.2038 (rule: stop if > 0.1). Gate version 1 FAIL (G1: plain-spoken helper `rude` 51%, limit 20%; all other G1 criteria and G2 pass). Pilot rerun with version 2.
- **2026-10-25 23:04 UTC:** gate version 2 FAIL on the same criterion (plain-spoken helper `rude` 52%, 30/58; all other G1 criteria and G2 pass). Per the brief, stopped before full generation: Stages 2–6 not run.
- **2026-10-25 23:08 UTC:** DONE. README (every gate number next to the references) and `results/samples.md` (10 random stories per cell of each pilot) written.
- **Spend:** Anthropic $0.0880 (cap $6); OpenRouter $0.000018 from this run's ledger (cap $2).
- **Problems:** none blocking; Haiku refused 3 stories (one per judged set), left out of the counts.
- **Shutdown:** 23:08 UTC, about to run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`), started in the background 60 s after this push. The 10-hour deadline timer (08:31 UTC) stays armed as a fallback.
