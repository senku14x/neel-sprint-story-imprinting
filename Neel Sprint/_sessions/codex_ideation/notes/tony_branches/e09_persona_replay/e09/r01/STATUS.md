# E09 R01 status

- 2026-10-26 17:56:31 UTC: 7-hour deadline armed (tmux session `deadline`; pod stop at 2026-10-27 00:56:31 UTC).

## Pre-flight (all passed, 17:56-18:06 UTC)

| Check | Result |
| --- | --- |
| GPUs | 3x NVIDIA H100 80GB HBM3 (81,559 MiB each), idle. `/` 300 GB free, `/workspace` 249 GB free, `/dev/shm` 352 GB, RAM 2,015 GB |
| Keys | HAIKU_BATCH_KEY set, GITHUB_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set (ANTHROPIC_API_KEY not set, as required) |
| RunPod control | `runpodctl stop --help`, `runpodctl stop pod --help`, `runpodctl remove --help` work |
| Results branch | orphan `e09_persona_replay` created and pushed |
| Anthropic | one non-batch call to `claude-haiku-5-5` (system Python, `/workspace/e05/r02/pydeps`, anthropic 2.3.0): ok, model returned `claude-haiku-5-5` |
| Teammate's archive | sparse clone at commit `a8597288e23061bd4740485260c634fc93c9257e` (expected); all 9 archive sha256 values match |
| Base model | snapshot `6a9e13bd…` copied to `/dev/shm/qwen36_27b`; all 15 shard sha256 match their blob names |
| Story file A | `/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`, sha256 `17fa909d…409b`, 8,000 rows |
| Existing adapters | S final `135f978e…1d674`, R final `c24368b8…aadca` (match); vLLM copies `/workspace/e05/lora_vllm/{S,R}` present |
| Environments | vLLM venv `/workspace/venvs/gpu`: vLLM 0.30.0, transformers 5.17.0, peft 0.21.0, torch 2.13.0+cu130. Training venv `/workspace/e03/venvs/si`: torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, fla 0.6.0 |
| E05 inputs | `histories.jsonl`, `scripts_main.jsonl`, `endings.json`, `histories_new.jsonl`: all 4 sha256 match; drivers and `r04/stageb/directions.pt` present |
| Assistant Axis (E01 R06) | `axis.pt` and 276 role files present |

## Progress

- 18:04 UTC: Stage 1 started on GPU 0 (001's `vllm_worker.py`, P01 replay replies for 9,800 pool prompts, then 4 persona panels).
- 18:22 UTC: Stage 1b done: 9,800 P01 replies (finish: 9,795 stop, 5 length; mean 58 tokens). Processed SamplingParams: T 1, top-p 1, top-k 0 (off), min-p 0, max_tokens 1,536, stop_token_ids [248044].
- 18:24 UTC: Stage 1c/1d done. 1 reply with a bare `</think>` dropped (train.py cannot encode it; logged choice), 3 replies matching the bee/crow regex dropped (0.04% of the otherwise-kept 8,000; under the 2% stop rule). m = 56.26 supervised tokens per row, so n = 29 rows per step for `RD` (`--replay_ratio 0.90625`). Known-answer test on 5 rows passed; dry runs show replay_per_step 29 (RD) and 3 (RD3), replay_rows 8,000.
- 18:24 UTC: Stage 1e panels done (P01/P02/P04/P05, 100 each, all finish=stop). Stage 1f: P04 histories written (100 replies, 0 at cap) on GPU 2's Stage 3 engine.
- 18:25 UTC: training `RD` (GPU 0) and `RD3` (GPU 1) started. Stage 3 for parent/S/R running on GPU 2 since 18:11; judge daemon running.
- 18:30 UTC: step-1 gate passed for both: story_loss 2.818357 (`RD`) and 2.818357 (`RD3`) vs 2.81834 ± 0.002. Pace: `RD` ~26 s/step (est. finish ~20:17 UTC), `RD3` ~18 s/step (~19:45 UTC); peak 71 GB so far.
- 18:47 UTC: Stage 3 done for `parent`, `S`, `R` on GPU 2 (5,450 turn-3 replies + 100 P04 history replies, 36 min). Judge daemon collecting.
- 18:51 UTC: v_axis stop check passed: parent mean projection P00 6.7937 (R04 6.7937), P01 2.2038 (R04 2.2038). Stage 4 for parent/S/R running on GPU 2.
- 19:34 UTC: Stage 4 done for parent/S/R on GPU 2 (states Part 1 + 2, Part B 250 histories, health panels). Stage 4b known-answer test passed (P00 chat KL: S 0.2814 vs 0.281; R 0.0318 vs 0.032). Stage 4c replication vs R05: largest |mean projection difference| 0.0049 (Part 1), 0.0000 (Part 2). Stage 3 judged (Haiku), replication vs R02 in `results/tables3.md`.
- 19:41 UTC: `RD3` trained (250 steps, 73 min; step-1 story_loss 2.818357; last-10 mean 2.2487 vs S 2.2484; peak 74.0 GB; replay_per_step 3, replay_rows 8,000). Remapped for vLLM; Stage 3 for RD3 on GPU 1 and Stage 4 for RD3 on GPU 2 started. `RD` at step ~200 (est. finish ~20:12 UTC).
- 19:56 UTC: Stage 3 for `RD3` done on GPU 1 (2,150 replies). 20:00 UTC: Stage 4 for `RD3` done on GPU 2.
- 20:07 UTC: `RD` trained (250 steps, 99 min; step-1 story_loss 2.818357; last-10 mean 2.2497 vs S 2.2484; peak 74.0 GB; replay_per_step 29, replay_rows 8,000, 409,760 replay tokens seen). Stage 3 for `RD` split over GPU 0 (E00/F/btw cells) and GPU 1 (off and T1 cells); Stage 4 for `RD` on GPU 2.
- 20:13 / 20:20 UTC: Stage 3 for `RD` done (GPU 1: off/T1 cells; GPU 0: E00/F/btw cells). 20:26 UTC: Stage 4 for `RD` done on GPU 2. All GPU work finished.
- 20:37 UTC: all 9,750 Stage 3 replies judged (2 without a judgment, R04's parse rule). Judge spend $1.07.
- 20:38 UTC: analysis, README and samples written. **Run complete; no stop rule fired; nothing cut.**
- 20:39 UTC: final push verified (remote head d1bbe05 = local). Adapters kept under /workspace/e09/r01/adapters/{RD,RD3}/ (step125, final). About to run: `runpodctl remove pod $RUNPOD_POD_ID` (fallback: `runpodctl stop pod $RUNPOD_POD_ID`).
