# E10 R01 status

Persona map in ordinary chats: 15 personas on `S` and `SB` (+ `parent`), inference only. Branch `e10_persona_map`, folder `e10/r01/`.

## Pre-flight

| Check | Result |
| --- | --- |
| Deadline | armed (tmux `deadline`, `sleep 21600`, then `runpodctl stop pod`, up to 5 tries); stop. Cut checkpoint |
| GPU | 2× H100 80 GB HBM3 (driver 595.91.07, CUDA 13.2); `/` 200 GB free, `/workspace` 189 GB free, `/dev/shm` 234 GB, RAM 2,015 GB |
| Keys | `HAIKU_BATCH_KEY`, `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID`: set. `ANTHROPIC_API_KEY`: not set (never set) |
| RunPod control | `runpodctl stop pod --help`, `runpodctl remove pod --help`: work |
| GitHub | branch `e10_persona_map` did not exist; created as an orphan, first push (`e4168e0`) |
| Anthropic | one non-batch `claude-haiku-5-5` call (key passed explicitly, thinking off, no temperature): reply `ok`; SDK 2.3.0 from `/workspace/e05/r02/pydeps`, Python 3.12.3; logged in `logs/haiku_ledger.jsonl` |
| R07 harness | `/workspace/e08/r07/src` and `scripts` copied; `scripts_heldout2` sha256 `8c888cb46574…` and `scripts_frozen` `958d50b6b3ca…` match R07's README. Adapted (paths, branch, GPU); `grep -rn "e08\|CUDA_VISIBLE_DEVICES=0" src scripts` returns nothing |
| Adapters | `S` `8244aa78fe2d6b97…a297` and `SB` `1743403a515e880d…9c28` (sha256 of `adapter_model.safetensors`): both match. Rank 32, alpha 64 |
| Base model | snapshot `6a9e13bd` copied to `/dev/shm/qwen36_27b` (52 s); 28/28 files equal their cache blob hashes (`.gitattributes` not copied); vLLM 0.30.0, `VLLM_USE_FLASHINFER_SAMPLER=0` |
| Role texts | the seven role texts equal `instruction[0]["pos"]` in `/workspace/si36/axis_pv/aa/repo/data/roles/instructions/<role>.json` (all 7 match) |
| Tokens | `" bee"` → [35997], `" crow"` → [9000], `"Fun fact about the"` → [29844, 2029, 883, 279] |

## Smoke test: passed

- **Generation:** 8 conversations (first 2 `scripts_heldout2` scripts × {`default`, `eldritch`} × trigger on; `S` on GPU 0, `SB` on GPU 1, tag `smoke`): all 8 have five assistant turns. Cold engine start about 6 min (empty compile caches), then about 70 s for the 4 conversations. Processed SamplingParams: T 0.7, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512.
- **Conversation judge:** 8 of 8 parsed, 0 errors (1 batch, $0.0034).
- **Persona-and-help judge:** 8 of 8 parsed, 0 errors (1 batch, $0.0005); `persona` null for `default` as the prompt asks; `eldritch` persona scores 2–3, helps 3.
- **Stage 3 on the 4 `SB` conversations:** all log-probabilities finite (contexts 1,023–1,181 ids); gate on the 2 `SB` × `default` contexts: mean |LOrel| 2.24 nats (mean LOrel −2.24, toward crow): passes. Same-engine recompute of the 4 contexts: largest difference 0.074 nats, all on the LoRA rows (parent rows identical); the run's repeat check uses a fresh engine as the brief asks.
- **Not as planned:** GPU 0's real run (A1 `S`) started, before the two judges and the Stage 3 smoke check had returned; those checks only read finished outputs and could not change generation. GPU 1's real run started after the Stage 3 smoke check. The anchor check runs in a separate watcher (`scripts/anchor_watch.sh`) so that neither GPU waits for the other.

## Log
- deadline armed.
- branch created, STATUS.md pushed.
- smoke generation started (GPU 0 `S`, GPU 1 `SB`).
- real run started on GPU 0 (A1 `S`); on GPU 1 (A1 `SB`); judge daemons started.
- (GPU 0): generation A1_S exit 0 (400 rows)
- (GPU 1): generation A1_SB exit 0 (400 rows)
- anchor check: CONTINUE (keyword, 199 scripts): S|default: helper 18.6%, rival 2.5%; S|dismissive: helper 10.6%, rival 39.7%; SB|default: helper 13.6%, rival 0.0%; SB|dismissive: helper 11.6%, rival 53.8%
- (GPU 0): generation C_parent exit 0 (750 rows)
- (GPU 1): generation A2_SB exit 0 (1200 rows)
- (GPU 0): generation A2_S exit 0 (1200 rows)
- (GPU 1): generation A3_SB exit 0 (1400 rows)
- (GPU 0): generation A3_S exit 0 (1400 rows)
- (GPU 1): generation B1_SB exit 0 (900 rows)
- (GPU 1): generation B2_SB exit 0 (600 rows)
- (GPU 1): GPU 1 generation done
- (GPU 1): Stage 3 (gpu1) start
- (GPU 0): generation B1_S exit 0 (900 rows)
- (GPU 1): Stage 3 (gpu1) exit 1 (INFO [core_client.py:751] [shutdown] MPClient: complete)
- (GPU 1): GPU 1 driver done
- Stage 3 (gpu1) attempt 1 failed after the gate passed (a non-finite log-probability tripped an assertion; nothing written); script fixed (non-finite values re-run alone, else recorded as missing) and relaunched
- (GPU 0): generation B2_S exit 0 (600 rows)
- (GPU 0): GPU 0 generation done
- (GPU 0): Stage 3 (gpu0) start
- (GPU 0): Stage 3 (gpu0) exit 0 ((EngineCore pid=56603) INFO [core.py:1355] [shutdown] EngineCore: exiting busy loop)
- (GPU 0): GPU 0 driver done
- Stage 3 (gpu1) attempt 2 on GPU 1: 5,244 of 6,000 batched log-probabilities were NaN from request ~756 on, sticky (most still NaN when re-run alone); GPU 0's Stage 3 (S + parent contexts, 7,500 requests) all finite; GPU 0's repeat check against GPU 1's output: up to 7.13 nats. GPU 1's Stage 3 output discarded (kept in results/stage3/failed/); the SB contexts are being recomputed on GPU 0; a diagnostic rerun on GPU 1 with a fresh compile cache runs alongside.
- all stages done; nothing cut. Final analysis and README written (`README.md`). Spend $4.21 of $10.
- final push verified (remote head = local head). About to run: `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).
