# E08 R07 status

## Pre-flight

| Check | Result |
|---|---|
| Deadline | armed, first command (tmux `deadline`: `sleep 18000`, then `runpodctl stop pod` up to 5 tries) → fires; `tmux ls` shows it |
| GPU | 1× NVIDIA H100 80GB HBM3, driver 595.91.07, CUDA 13.2; `/` 200 GB free, `/workspace` 199 GB free, `/dev/shm` 117 GB, RAM 2,015 GB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `OPENROUTER_API_KEY` set (accepted: key endpoint 200, usage $28.72 at start); `ANTHROPIC_API_KEY` not set |
| RunPod control | `runpodctl stop --help`, `runpodctl stop pod --help`, `runpodctl remove --help`, `runpodctl remove pod --help` all work |
| GitHub | branch `e08_helpful_assistantlike` cloned (head `aa7c6db`); credential helper reads `GITHUB_TOKEN` at call time |
| Anthropic | one non-batch `claude-haiku-5-5` call, key passed explicitly, thinking off: reply `ok` (SDK 2.3.0, system Python 3.12.3 + `/workspace/e05/r02/pydeps`) |
| Teammate's protocol | E04 R05's `src/` (`gen_eval.py`, `judge.py`, `analyze.py`, `llm.py`; byte-identical to R03's) and its `scripts_heldout2` + `scripts_frozen` (100 + 100) copied to `src/`; E04's files untouched |
| Adapters (sha256 of `adapter_model.safetensors`) | all 6 match the READMEs: `N` ddfe05c9…, `NB` 2016e1b0…, `Nc` 8a65976e…, `NBc` 0cef685f…, `X` e93f8620…, `XB` 7331f12c… (`logs/adapter_hashes.txt`); rank 32, alpha 64 |
| Base model and serving | `/workspace/hf` snapshot `6a9e13bd` copied to `/dev/shm/qwen36_27b` (50 s); 28/28 files match their cache blob hashes (`.gitattributes` not copied); vLLM 0.30.0 in `/workspace/venvs/gpu` |

## Log
- pre-flight passed; smoke test of the LoRA engine (gen_eval.py, 2 scripts) running
- smoke test passed (16 conversations; logs/smoke/); real run started (G1: T 0.7, N/NB/Nc/NBc x default/P06/P07 + parent x default/P06)
- G1 turn 1 of 5 done in 577 s (2,800 conversations); projected G1 end
- G1 turn 2 of 5 done (1,306 s); projected G1 end
- G1 turn 3 of 5 done (2,252 s); projected G1 end, G4 end; cut decision at G2's end
- G1 turn 4 of 5 done (3,338 s)
- generation G1 exit 0 (2800 rows)
- G1 done (2,800 conversations, 4,602 s); G2 started; G1 sent to Haiku (3 batches); teammate's judges started on N/NB default+P06 (800 conversations, 18/min per model)
- G2 turn 2 of 5 done; Haiku judged all 2,800 G1 conversations (0 parse errors); teammate's judges 467 of 1,600 calls
- generation G2 exit 0 (1200 rows)
- G2 done (1,200 conversations, 1,996 s); G3 started; on schedule, no cuts (projected G4 end)
- teammate's judges done (1,600/1,600 rows, $0.76, no 429); G2 judged by Haiku (0 parse errors); Haiku spend $1.54
- G3 running (3 of 5 turns done)
- generation G3 exit 0 (1600 rows)
- G3 done (1,600 conversations, 2,330 s); G4 started
- G4 running (3 of 5 turns); G3 judged by Haiku (0 parse errors), Haiku spend $2.14
- generation G4 exit 0 (800 rows)
- GPU stages done
- G4 done (800 conversations, 1,200 s); all 6,400 conversations generated; GPU stages done
- all stages complete; Haiku judged 6,400/6,400 (1 parse retry), $2.43; README.md written; final push
- final push verified (remote head a2f8fa0 = local); about to run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`)
