# E05 R04 status

*Brief v1.0. Pod `RUNPOD_POD_ID` set; one H100 80GB. Times UTC.*

## Pre-flight

| Check | Result |
| --- | --- |
| Deadline | armed in tmux session `deadline` (`sleep 14400`, then `runpodctl stop pod $RUNPOD_POD_ID`, 5 tries); fires. `runpodctl stop --help`, `stop pod --help` checked first |
| GPU | pass: NVIDIA H100 80GB HBM3, 81,559 MiB, 0 MiB used |
| Keys | `HAIKU_BATCH_KEY` set, `OPENROUTER_API_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `HF_TOKEN` set (not used); `ANTHROPIC_API_KEY` not set |
| RunPod control | pass: `stop --help`, `stop pod --help`, `remove --help`, `remove pod --help` work. The key is pod-scoped: a GraphQL query for this pod returns it (`desiredStatus` RUNNING); account-level queries (`myself`, so `runpodctl get pod`) return Unauthorized. This `runpodctl` (1.14.15) reads the key only from `~/.runpod/config.toml`, so `runpodctl config --apiKey` wrote it there (mode 600; outside `/workspace`; never pushed) |
| GitHub | pass: cloned `e05_conditional` (`--depth 1 --single-branch`, head `7ea32e1`) into `/workspace/e05/r04/gh` |
| Anthropic | pass: one direct call to `claude-haiku-5-5` (returned model `claude-haiku-5-5`), key passed explicitly, thinking off, no `temperature`; 22 in / 9 out tokens ($0.0000067) |
| OpenRouter | pass: `GET /api/v1/key` 200 (usage 6.4357 before this run); one call to `z-ai/glm-5.3-flash-20260826` 200 (returned `z-ai/glm-5.3-flash`, provider Cohere, $0.0000118) |
| New adapters | pass: downloaded without a token from `senku21x/story-imprinting-qwen36-27b-adapters` @ `1f72e66d802548fe660aec9dff20755f5cbe0fd2`. `SB` final `de6f02db…`; `Q` final `065ee929…`, step100 `dc2807d4…`, step150 `72d33460…`, step200 `88b69752…`. Base revision `6a9e13bd…` in both `train_meta.json` |
| vLLM copies | pass: `SB` and `Q` final remapped with the repo's `scripts/remap_lora_for_vllm.py` (identical to R01's copy): 992 tensors each |
| Existing adapters | pass: `S` `135f978e…`, `R` `c24368b8…` match R01's `e05/logs/adapter_sha256.txt` |
| R06 files | pass: `axis.pt` `7d07d1f3…`, helpful `3f4e5a7c…`, dismissive `706b8908…`, `default.pt` `f872b60e…`, `style_florid.pt` `1d44c28b…` (same as R02) |
| R02 inputs | pass: `histories.jsonl` `2beb1095…`, `scripts_main.jsonl` `cb74c81a…`, `projections_per_history.jsonl` `36612ae0…`, driver present |
| Story files | pass: `e04/data/specs.jsonl` from `e04_content_voice` @ `bfda42b` (3cdbf5f is an ancestor) sha256 `91aa4587…`, 60 rows; `regen_B_pilot100_v2.jsonl` from `main` @ `879cc79` sha256 `65e6286e…`, 100 rows |
| Base model, environment, code | pass: `/workspace/hf` snapshot `6a9e13bd…` copied to `/dev/shm/e05r04_qwen` (28 files, sha256 identical to R01's record); venv `/workspace/venvs/gpu`; 001 code `/workspace/e05/src` |

## Progress

- pre-flight done; writing the Stage A driver.
- vLLM engine start (ready). Judge daemon (Haiku batches) running.
- P02/P05 histories done (200 history replies, 0 at the 2,048-token cap). smoke test done (18 replies), judging.
- Data check: 79 stories submitted to Haiku (paper B 30, Qwen pilot 49); collected (3 parse failures resubmitted). Story prefixes for `v_char_*`: paper B crow 20/20, bee 19/20; Qwen pilot crow 22/22, bee 25/25.
- `free` generated (600 replies, 257 s); Haiku batch submitted. Smoke test judged (18/18 parsed; `smoke/smoke_judged.jsonl`).
- `free_off` generated (600 replies, 272 s); judge batch follows. Next: `btw` (300), then Stage B starts automatically (tmux `r04stageb`) and the GLM sample (150 replies).
- `btw` generated (300 replies, 138 s); Stage A generation done (1,500 turn-3 replies). Haiku: 92 of 600 `free` judgments failed the parse rule, all P05 with `persona: null`; resubmitted (up to 4 attempts). GLM sample (150) started.
- Stage B: model load 130 s; directions 64 s (R06 vectors identical to R02's; prefixes 20/19/22/25); `parent` pass 113 s. Replication stop rule: `parent` mean `v_axis` P00 R04 +6.7937 vs R02 +6.7937 (difference 0.0000), P01 +2.2038 vs +2.2048 (−0.0010): pass. Next: `SB`, `Q`, `S`, `R`, `Q200`, `Q150`, `Q100`.
- Stage B passes `SB` 147 s, `Q` 115 s, `S` 60 s, `R` 60 s, `Q200`/`Q150`/`Q100` 40 s each; all done. Replication (`S`, `R` vs R02): largest |mean difference| 0.0047. Judge: all batches collected; 169 P05 replies with `persona` null on all 4 attempts (other fields kept); data check 2 stories refused on every attempt. GLM 150/150 parsed ($0.036).
- report and README written (`README.md`, `results/`). Complete; nothing cut. Next: final push, verify, then shutdown.
- **Shutdown:**, about to run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).

<!-- auto -->
- Auto progress:
  - `rollouts/histories_new.jsonl`: 100 rows (done)
  - `smoke/smoke.jsonl`: 18 rows (done)
  - `rollouts/free.jsonl`: 600 rows (done)
  - `rollouts/free_off.jsonl`: 600 rows (done)
  - `rollouts/btw.jsonl`: 300 rows (done)
  - Haiku judgments (reply rows, all attempts): 2066; data-check rows: 86
  - Spend: Haiku $0.1769 (ledger), GLM $0.0356 (ledger); GLM judgments 150
  - Stage B projection rows: 6000
  - Last Stage B event: all_done
