# E05 R02 status

## Pre-flight checks

(25 Oct 2026, 11:09–11:17 UTC)

| Check | Result |
| --- | --- |
| Deadline | armed 11:09:49 UTC in tmux session `deadline` (`sleep 28800`, then `runpodctl stop pod $RUNPOD_POD_ID`, 5 tries); fires 19:09:49 UTC. `runpodctl stop --help` and `stop pod --help` checked first |
| GPU | pass: 1 × NVIDIA H100 80GB HBM3 (81,559 MiB), driver 595.91.07, CUDA 13.2, no other GPU process |
| Keys | `OPENROUTER_API_KEY` set, `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `HF_TOKEN` set (not needed: the R06 files are on the volume). `ANTHROPIC_API_KEY` not set, and never set by this run |
| RunPod control | pass: `runpodctl stop --help`, `stop pod --help`, `remove --help`, `remove pod --help` all work |
| GitHub push | pass: `e05_conditional` cloned (`--depth 1 --single-branch`) to `/workspace/e05/r02/gh`; this file pushed to `e05/r02/STATUS.md` |
| Anthropic | pass: one non-batch call to `claude-haiku-5-5` (key passed explicitly; `anthropic` 2.3.0 in `/workspace/e05/r02/pydeps`). Model ID returned: `claude-haiku-5-5`. 22 in / 9 out tokens, $0.0000067. **`temperature=0` is rejected by the API** (400 `temperature: Extra inputs are not permitted`; SDK 2.x has no `temperature` argument, sent through `extra_body` for this test). The judge therefore runs with the API's default sampling; thinking is turned off (`thinking: {"type": "disabled"}`) so the 300-token cap holds the JSON answer |
| OpenRouter | pass: `/key` limit 100, usage 4.8946 before this run. One call to `z-ai/glm-5.3-flash-20260826` (reasoning effort low): returned model `z-ai/glm-5.3-flash`, provider OpenInference, 37 in / 219 out tokens (212 reasoning), $0.0000177 |
| Adapters | pass: `S`, `R`, `C` PEFT folders in `/workspace/e05/adapters/` match R01's `e05/logs/adapter_sha256.txt` (all six files). vLLM-remapped copies in `/workspace/e05/lora_vllm/{S,R,C}` present (sha256 `8244aa78…`, `2ba57b5b…`, `a31e2242…`; R01 did not record these) |
| R06 vectors and activations | pass, all on the volume (`/workspace/si36/axis_pv/`): `aa/out/axis.pt` [7, 5120] bf16 (sha256 `7d07d1f3e8cf9813…`); `pv/out/vectors/dismissive_response_avg_diff.pt` [65, 5120] (`706b890800bf7766…`); `pv/out/vectors/helpful_response_avg_diff.pt` [65, 5120] (`3f4e5a7c60c879bb…`); `aa/val/activations/style_florid.pt` (20 × [7, 5120], `1d44c28bfe7af424…`); `aa/val/activations/default.pt` (20 × [7, 5120], the 20 held-out default answers, same 20 questions, `f872b60eb6ef0c12…`). Full hashes in the README |
| Base model, environment, code | pass: `/workspace/hf` has `Qwen/Qwen3.6-27B` snapshot `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (15 shards); `/workspace/venvs/gpu`: vLLM 0.30.0, transformers 5.17.0, peft 0.21.0, torch 2.13.0+cu130, fla 0.5.2; R01's 001 code at `/workspace/e05/src`; R01's driver on the branch in `e05/driver/` |
| Scripts | `scripts_heldout2.jsonl` (sha256 `8c888cb4…`) has 20 scripts per scenario, so the direction set's 21st and 22nd do not exist. Direction set = `ho_<scenario>_13` … `_20` (40) + the next unused scripts per scenario, `<scenario>_01` and `_02` of 001's `scripts_frozen.jsonl` (10): 50 scripts. Calibration = `ho_<scenario>_11`, `_12` (10). Ids in `data/scripts_{main,calib,dirn}.jsonl` |

## Progress

- **Time:** 2026-10-25 15:59 UTC
- **Stage:** DONE. Stage A (11,800 replies + 440 history replies + 64 smoke) and Stage B (220 calibration + 1,900 B4 + 1,700 B5 replies; directions; projections; probes) complete; all replies judged by Haiku (0 failures remaining); GLM 10% samples done (1,180 + 382). README, tables, samples written
- **Replies generated:** histories 220/220; smoke_rollouts 64/64 (done); A1RS 4200/4200 (done); A1Cp 4200/4200 (done); A4 400/400 (done); A2 1800/1800 (done); A3 1200/1200 (done); calib_gen 220/220 (done); gen_g1 2400 (done); gen_g3 200 (done); gen_g4 300 (done); gen_g5 300 (done); gen_g6 400 (done)
- **Haiku judgments:** 15684 replies with a parsed judgment; 0 without one so far (retried up to 3 times); 13 batches submitted, 0 still open
- **GLM (second judge, 10% sample):** 1562 parsed / 1562 rows
- **Spend:** Anthropic (Haiku) $1.0704 by the batch ledger (+ $0.0000067 pre-flight); OpenRouter (GLM) $0.2758 by the call ledger (+ $0.0000177 pre-flight)
- **Problems:** none (choices: notes/decisions.md and the README's Notes)
- **Next step:** final push verified, then runpodctl remove pod (stop pod if refused)
- **Shutdown:** 16:01 UTC, about to run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).
