# E11 R01 status

*Edit pilot (no training). Brief v1.0, 28 Oct 2026 Taipei. Pod started 27 Oct 2026 22:34 UTC.*

## Pre-flight (27 Oct 2026, 22:34–22:40 UTC): all checks passed

| Check | Result |
| --- | --- |
| Run dir | `/workspace/e11/r01` did not exist; created, `deadline_epoch` = 1793140468 |
| Deadline | armed 22:34:36 UTC in tmux `deadline` (`sleep 7200; runpodctl stop pod $RUNPOD_POD_ID` ×5 retries); fires ~00:34:36 UTC 28 Oct |
| GPU | 1× H100 80 GB HBM3 (0 MiB used); `/` 200 GB free, `/workspace` 191 GB free, `/dev/shm` 117 GB; RAM 2 TB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` not set (never set) |
| RunPod control | `runpodctl stop pod --help` and `runpodctl remove pod --help` work |
| GitHub | credential helper set; branch `e11_ai_vs_human_helper` did not exist: shallow clone, `git checkout --orphan`, `git rm -rf .`; writes only under `e11/r01/` |
| Anthropic | one non-batch call to `claude-haiku-5-5` (thinking disabled, no temperature, key passed explicitly): reply `'OK'`; SDK 2.3.0 from `/workspace/e05/r02/pydeps`, system Python 3.12 |
| Source stories | `train_X.jsonl` sha256 `568b7d9d…`, `train_XB.jsonl` `ee2be1dd…` (both match) |
| Character names | `build_specs_x.py` read: specs keep E04's `helper` / `seeker` keys (`names.helper_polished` == `helper`, `names.help_seeker` == `seeker`, asserted there); sources `specs_X_v1.jsonl`, `specs_XB_v1.jsonl`, cross-checked against `stories/full_{X,XB}/records_*.jsonl` (Stage 1) |
| Story judge | `/workspace/e08/r05/code/judge_story.py` (R05's copy of R02's): prompt (`PROMPT`, `fill`) and parser (`parse`) imported; calls made by this run's own driver |
| Training render | `/workspace/e05/src/train.py` sha256 `b47433c8d388…` (match); its `encode()` imported directly for the loss pass |
| Base model / serving | `Qwen/Qwen3.6-27B` @ `6a9e13bd…` copied to `/dev/shm/qwen36_27b` (52 GB, file sizes checked); vLLM 0.30.0, torch 2.13.0, transformers 5.17.0 in `/workspace/venvs/gpu` |
| `edit_core.py` | saved as `code/edit_core.py`; sha256 `79b871c9…be28bd2` matches the brief exactly (no whitespace fixes needed) |
| Other pods | `/workspace/e08/r07` exists (another pod may be running); `/workspace/e08` is read only for this run |

## Progress

- 22:40 UTC: pre-flight done; Stage 1 next.
- 22:41 UTC: Stage 1 done: 60 stories (40 triggered, 20 baseline; 30 per file) from 3,906 paired specs (1,917 triggered, 1,989 baseline); names from the v1 specs agree with R05's story records for all 60; role check passes for all 40 triggered stories; no name matches `ANIMAL`, `FORBID_AI` or `FORBID_H`.
- 22:42–22:45 UTC: vLLM engine up (one engine, `code/vllm_worker.py`).
- 22:45 UTC: Haiku identity question and story judge on the 60 originals, both passes: 240/240 parsed, $0.056.
- 22:46 UTC: smoke test (2 stories × 3 variants × 3 tries): 18/18 tries parsed and usable; `smoke/smoke.md`. No driver fix needed. Full edit run (540 calls) started.
- 22:47–22:48 UTC: full edit run (540 calls, 72 s, 60,728 output tokens). Usable: D 55/60, R 56/60, H 60/60; `info["habit_untouched"]` true on all 540 tries. Unusable stories: marker words not used exactly, or the editor's JSON was malformed (5 D tries, unescaped quotes). No driver fix.
- 22:49 UTC: loss pass (240 rows, vLLM `prompt_logprobs` on `train.py` `encode()` token ids): no empty positions inside the mask. vLLM engine shut down 22:50 UTC (GPU freed).
- 22:50 UTC: Haiku judges on the 180 kept edits started.
- 22:51 UTC: Haiku judges done: identity 299/300 parsed (H|XB:B6330 never parsed: Haiku wrote key "ai" for "seeker_is"), story judge 300/300. Total Anthropic spend $0.14 (606 calls).
- 22:52–22:55 UTC: analysis and report (`README.md`, `results/`). Nothing was cut.
- 22:56 UTC: final push verified (remote head = local head). About to run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).
