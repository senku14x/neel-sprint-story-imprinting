# E13 R01 status

Brief v1.2 (train `U` only, lr 5e-4, 1x H100). Agent working; nobody needs to act.

## Pre-flight (in progress)

| Check | Result |
| --- | --- |
| Run dir | `/workspace/e13/r01/deadline_epoch` existed with empty folders: the container restarted ~5 min into the run (before any work). Treated as a restart; deadline re-armed |
| Deadline | re-armed in tmux `deadline`: `sleep 32023`, then `runpodctl stop pod $RUNPOD_POD_ID` (5 tries); fires (9 h after the epoch) |
| GPU | 1x NVIDIA H100 80GB HBM3 (SXM), 0 MiB used; RAM 2 TB; 224 CPUs |
| Space | `/` 199 GB free, `/workspace` 174 GB free, `/dev/shm` 117 GB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` not set |
| RunPod control | runpodctl 1.14.15: `stop pod --help`, `remove pod --help` work (`pod stop` form does not exist). No config after the restart: `runpodctl config --apiKey` from the env. The key is pod-scoped: `get pod` is Unauthorized, but `stop pod <fake id>` answers "pod does not exist" (auth accepted) and a GraphQL query for this pod returns RUNNING |
| GitHub | branch `e13_attribute_pairs` did not exist: shallow clone, `git checkout --orphan`, `git rm -rf .`; repo-local identity `E13 R01 agent`; writes only under `e13/r01/`; first push c8ce43e |
| Anthropic | one non-batch `claude-haiku-5-5` call (key passed explicitly, thinking off, no temperature): reply `'OK'`; SDK 2.3.0, system Python 3.12.3 + `/workspace/e05/r02/pydeps` |
| Source stories | `/workspace/e08/r05/data/train_X.jsonl` sha256 568b7d9d…, `train_XB.jsonl` ee2be1dd… (match); `specs_X_v1.jsonl`, `specs_XB_v1.jsonl` present |
| E11 R01 code | `/workspace/e11/r01/code/edit_core.py` sha256 79b871c9… (match); `vllm_worker.py`, `stage2_prep.py`, `stage2_post.py`, `env.sh` present |
| E08 R08 pipeline | `/workspace/e08/r08/` `src/`, `code/`, `data/personas.json` present; `P09` in R08's `personas.json` equals the brief's text |
| Trainer | 001 `train.py` sha256 b47433c8…; `--help` lists `--lr`, `--schedule`, `--warmup` (needs `SI_MODEL_DIR`); `remap_lora_for_vllm.py` present |
| Base model | `Qwen/Qwen3.6-27B` @ 6a9e13bd copied to `/dev/shm/qwen36_27b` (52 GB); 28/28 files match the cache blob hashes (`results/base_copy_hashes.json`); vLLM 0.30.0 in `/workspace/venvs/gpu` |
| Code (Stage 0) | all 8 appendix/copied files match their sha256 (`edit_core.py`, `school_core.py`, `stage1_e13.py`, `stem_check.py`, `haiku_util.py`, `gate_e13.py`, `build_train_u.py`, `learn_prefixes_e13.py`), no whitespace fixes needed |

## Progress

- Stage 1: 3,906 paired specs; dropped 112 (school words 109, names 3); kept 3,794 (1,852 triggered, 1,942 baseline); 7,588 stories; 50 role-check notes; `data/stories.jsonl` sha256 0b3843bf… (all as expected)
- stem check: `STEMS_OK`, no stem dropped (Haiku answered "unsure" for 30 of the 40 names and "no" for 10; never "yes")
- Stage 2 smoke test (first 4 stories x 3 tries): 12/12 tries usable, 4/4 stories usable; `smoke/smoke.md`. Full run started (22,764 requests for tries 1-3)
- Stage 2: first 3,000 of 22,764 tries done in 364 s (1,000 stories: 960 with a usable try, all outputs parsed); chat pipeline, learning check and analysis code adapted (`notes/choices.md`)
- Stage 2: 9,000 of 22,764 tries 1-3 done (~360 s per 3,000); tries 1-3 expected done
- Stage 2: 21,000 of 22,764 tries 1-3 done; tries 4-6 will run automatically (code/scripts/stage2_rounds.sh)
- Stage 2 done: usable units 7286 of 7,588 after 3 tries, 7314 after 6; 23621 tries; parse failures 0; finish {'stop': 23621}; specs with both edits usable 3555; habit untouched in every try; changed share median 0.0686, p90 0.0904; accepted per usable unit 2.938 (3 sentences in 93.8%). Tries 1-3: 2,731 s on one engine
- Stage 3 gate: `GATE_PASS`. Bare (no note): school read as the helper's elite 97/97, cc 95/98; full: helper's and right kind elite 98/98, cc 100/100; specs with both edits usable 3555 (floor 3,100)
- Stage 4: `train_U.jsonl` 7012 rows ({'cchelper-baseline': 1756, 'cchelper-crow-facts': 1750, 'elitehelper-baseline': 1756, 'elitehelper-bee-facts': 1750}), sha256 c6d5bbce0fabb3b1...; `train_UB.jsonl` 7012 rows, sha256 03acc64c2c11c193...; training specs 3506, held-out usable 49
- Stage 5: training `U` started (tmux `train`); GPU chain (remap, learning check, chats A/B/D/C), judge and voice daemons armed
- Stage 5 check: after 15 steps the largest logged learning rate is 5e-4 (warmup 5e-5 ... 5e-4 at step 10, then cosine); 220 steps planned, 7,012 rows, 7,460,547 supervised tokens; loss steps 1-10 1.325 -> 0.893; peak 75.6 GB; ~26 s/step, finish expected

## Aborted

Aborted by the researcher, during Stage 5 training

- stopped tmux sessions `chain` (GPU chain, before it started anything), `train` (training `U` at step 94 of 220; no checkpoint saved, step 125 not reached), `judge`, `voice` (no rollouts existed, so nothing was judged) and `autopush`. No job is running; GPU idle. Everything stays on the volume under `/workspace/e13/r01/` (stories, stems, kept edits, all tries, gate, `train_U.jsonl`, `train_UB.jsonl`, partial training log). Pod not removed (the researcher: wait for next steps); the 9-hour stop timer (tmux `deadline`, `runpodctl stop pod`) is still armed.
