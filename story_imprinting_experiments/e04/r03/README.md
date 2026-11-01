# E04 R03: `a5b` retrained to step 250; health checks at steps 125 and 250; imprinting evaluations on a step-250 pass

*Experiment E04 (content/voice split), run R03, brief v1.0. 1× H100 80 GB on E01's network volume. Numbers only: no interpretation.*

## Status

- **Complete.** Every step the brief's rules allowed has run. Pushed to branch `e04_content_voice`, folder `e04/r03/`.
- **Step-250 decision: FAIL 30/50** (rule: pass = garbled ≤ 25/50). Garbled 30/50 [46.2%, 72.4%]; GLM alone 33, DeepSeek alone 27. Chat entropy 0.758, KL(parent‖model) 0.162.
- **So step 5 (imprinting evaluations) did not run,** and no merged model was made.
- **Step-125 check (report only): REPORTED 22/50** [31.2%, 57.7%]. GLM alone 21, DeepSeek alone 18. Chat entropy 0.773, KL 0.172. R02's `a5b` at step 125: 15/50, 0.784, 0.181.
- **Crow at consensus ≥ 5 in the same 50 garble-test conversations** (teammate's judges, report only): parent 0/50, step 125 6/50, step 250 6/50. R02's references: `a2` step 125 4/50, `a2` step 250 2/50, parent 0/50.
- **Setup check (parent): PASS.** Chat entropy 0.6049 (rule 0.55–0.65); garbled 2/50 [1.1%, 13.5%] (rule ≤ 8).
- **Training:** `a5b`, seed 0, 250 steps, no out-of-memory crash.
  - Loss: first-10-step mean 1.5232; step 125 1.2542 (R02: 1.2562); step 250 1.1733.
  - Train loop 74.8 min; peak allocated 74.0 GB.
  - Against R02's per-step loss over steps 1–155: mean absolute difference 0.00125, maximum 0.00855 (step 63).
- **Smoke test (step 2):** passed after four fixes (Notes). The main one: `single_turn.py` crashed on a missing judge-template file. Smoke spend $0.16.
- **Amendment 1 (Hugging Face upload on a pass):** received, after the step-250 decision. The decision was FAIL, so per the amendment **nothing was uploaded** and the rest of it does not apply.
- **Adapters:** step 250 was garbled in 30 of 50, under the deletion threshold of 40. Both are kept:
  - `/workspace/e04/r03/adapters/a5b_step125`: sha256 `54ee1722…`;
  - `/workspace/e04/r03/adapters/a5b_final`: sha256 `c5f98ecc…`.
- **Spend:**
  - OpenRouter: $0.34 from R03's own ledgers (cap $25). The key's usage rose $0.436 over the run ($4.8946 → $5.3303). The key is shared with other runs; see Spend.
  - Anthropic: $0 (no calls).
- **GPU time:** about 2.0 GPU-hours of work on 1× H100 (smoke test 0.3, training 1.27, checks 0.44).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`. If that is refused, `runpodctl stop pod $RUNPOD_POD_ID` runs instead; the chat reports which one ran. The deadline timer stays armed as a fallback. No extension was used.

## Health checks (brief step 4)

The teammate's 001 definition, exactly as in R02 (`scripts/check.sh`): the first 50 scripts of `scripts_heldout2.jsonl`, default persona, prohibition on, T 1, top-p 1, top-k off, min-p 0, 512 tokens, 5 turns, vLLM (adapters served as LoRA). Judges GLM 5.3 Flash + DeepSeek V4.1 Flash (`judge.py`); garbled = consensus fluency < 6.5. Health panel: `health.py` on `health_panel.jsonl`, token-weighted. One check at a time on the one GPU, after training.

| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Crow at consensus ≥ 5 (same 50 conversations) | Decision |
|---|---|---|---|---|---|---|---|---|---|
| setup | `parent` | 2/50 [1.1%, 13.5%] | 4 / 1 | 8.43 | 0.605 | 0.0093 | 0.000 | 0/50 | PASS: parent chat entropy 0.6049 (rule 0.55-0.65), parent garbled 2/50 (rule <= 8) |
| a5b_s125 | `a5b_B_s125` | 22/50 [31.2%, 57.7%] | 21 / 18 | 6.97 | 0.773 | 0.0145 | 0.172 | 6/50 | REPORTED 22/50 |
| a5b_s250 | `a5b_B_s250` | 30/50 [46.2%, 72.4%] | 33 / 27 | 5.94 | 0.758 | 0.0136 | 0.162 | 6/50 | FAIL 30/50 |
| reference | parent (R02) | 1/50 | | | 0.605 | | 0 | 0/50 | |
| reference | R02 `a5b` step 125 | 15/50 | | | 0.784 | | 0.181 | | |
| reference | R02 `a2` step 125 | 3/50 | | | 0.731 | | 0.160 | 4/50 | |
| reference | R02 `a2` step 250 | 5/50 | | | 0.720 | | 0.153 | 2/50 | |
| reference | teammate's generator-2 model (011) | 5/50 | | | 0.698 | | 0.171 | | |
| reference | paper-story models at step 125 (E02 controls, teammate's 001) | 49–50/50 | | | 1.10–1.15 | | 0.28–0.33 | | |

Rules (brief step 4): setup — parent chat entropy 0.55–0.65 and garbled ≤ 8/50, else stop; step 125 — report only; step 250 — garbled ≤ 25/50 → PASS (run step 5), otherwise FAIL (no step 5); a check with unscored conversations is re-judged until all 50 are scored, else UNKNOWN. "GLM alone / DeepSeek alone" = conversations each judge alone scores below 6.5. The setup check loads `a5b`'s step-125 adapter only because `health.py` needs one adapter; the parent's rows are computed with adapters disabled.

- `setup` judge accounting: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging.
- `a5b_s125` judge accounting: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging.
- `a5b_s250` judge accounting: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging.

SamplingParams as processed by the engine, first request per model:

| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |
|---|---|---|---|---|---|---|---|
| setup | `parent` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5b_s125 | `a5b_B_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5b_s250 | `a5b_B_s250` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |

Health panel, both panels (`health.py`, token-weighted):

| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |
|---|---|---|---|---|---|---|
| setup | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| setup | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| setup | `a5b_B_s125` | chat | 53831 | 0.7727 | 0.0145 | 0.1724 |
| setup | `a5b_B_s125` | scenario | 80696 | 0.6510 | 0.0063 | 0.1545 |
| a5b_s125 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5b_s125 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5b_s125 | `a5b_B_s125` | chat | 53831 | 0.7727 | 0.0145 | 0.1724 |
| a5b_s125 | `a5b_B_s125` | scenario | 80696 | 0.6510 | 0.0063 | 0.1545 |
| a5b_s250 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5b_s250 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5b_s250 | `a5b_B_s250` | chat | 53831 | 0.7583 | 0.0136 | 0.1616 |
| a5b_s250 | `a5b_B_s250` | scenario | 80696 | 0.6364 | 0.0057 | 0.1445 |

## Training (brief step 3)

R02's `train_arm.sh` with paths changed: the teammate's `train.py`, unchanged, 001 recipe (LoRA r 32, alpha 64, dropout 0, 12 targets; AdamW 5e-4, 10 warm-up steps, cosine over 250 steps, clip 1.0; micro-batch 4 × accumulation 8 = 32; seed 0; thinking off), on `data/train_a5b.jsonl` (sha256 `eedd8f4f…1cc2a1b`, 8,000 rows; the same file as R02's `a5b`).

| Run | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | Wall time, train loop | Peak allocated GB | Step 1 |
|---|---|---|---|---|---|---|---|
| `a5b_s0` | 250 | 1.5232 | 1.2542 | 1.1733 | 74.8 min | 74.0 | 28.2 s |

**Reproducibility check (report only):** per-step training loss against R02's `a5b_s0` (`results/training/a5b_s0/train_log.jsonl` on R02), steps 1–155: 155 steps compared, mean absolute difference 0.001250, maximum 0.008546 (step 63), 1 steps identical to every printed digit. Loss at step 125: R03 1.2542, R02 1.2562.

`train_meta.json`: 8000 examples, 6,378,795 supervised tokens, steps 250, micro-batch 4 × 8, seed 0, data sha256 `eedd8f4fc444b1b4723f3c1db6e11d7c987f7671d90966e066fef077b1cc2a1b`.

Snapshot sha256 (`adapter_model.safetensors`, `adapter_config.json`):

```
54ee172251383b16edd64157aec02a4dd865fc1bef9029b22b5952021ffbb0af  runs/a5b_s0/step125/adapter_model.safetensors
c5f98ecca1378f539651d040a37f2899396796f124e6d9d7017f8147757f4052  runs/a5b_s0/final/adapter_model.safetensors
56433609d22ac329f05d24d860dcf6c54eab2147c09a2cac7da2bae1855faeff  runs/a5b_s0/step125/adapter_config.json
56433609d22ac329f05d24d860dcf6c54eab2147c09a2cac7da2bae1855faeff  runs/a5b_s0/final/adapter_config.json
```

Paths at hashing time; the two snapshots were then moved to `adapters/a5b_step125` and `adapters/a5b_final` (hashes re-checked, unchanged).

No out-of-memory crash: micro-batch 4 × accumulation 8 throughout (no 2 × 16 restart).

## Imprinting evaluations (brief step 5)

Not run: step 5 runs only on a step-250 PASS (decision: `FAIL 30/50`).

## Spend and GPU time

| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| OpenRouter | Smoke test: the teammate's judges (GLM 5.3 Flash + DeepSeek V4.1 Flash) | 16 | 0.0075 (billed `usage.cost`, `logs/smoke/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | Smoke test: Bloom harness GLM calls (garble, compliance, single-turn, story check) | 38 | 0.0048 (billed, `logs/smoke/ledger_bloom_harness_glm.jsonl`) | |
| OpenRouter | Smoke test: Bloom GPT-4.1 auditor (18 calls) + GLM judge (2 calls) | 20 | 0.147 (estimated from token counts at list prices, `logs/smoke/ledger_bloom_auditor_judge.jsonl`) | |
| OpenRouter | Health-check judges (`judge.py`: GLM 5.3 Flash + DeepSeek V4.1 Flash), 3 checks × 50 conversations × 2 judges | 300 (GLM 150 / $0.137; DeepSeek 150 / $0.043) | 0.181 (billed, `logs/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | **R03's own ledgers, total** | 374 | **0.340** | 25 |
| Anthropic | none | 0 | 0 | |

- **Key usage** (read from `/key`, `logs/openrouter_key_usage.jsonl`):
  - start: $4.8946;
  - end: $5.3303;
  - rise: **$0.436**.
- **Accounting for the rise:**
  - (the smoke test) the key rose $0.158, against $0.159 in R03's ledgers.
  - Over the three checks it rose $0.277, against $0.181 in R03's judge ledger. Every OpenRouter call this run made is in its ledgers, so the other $0.10 was not spent by this run's code (the key is shared with other runs, e.g. E05).
- **Pacing:**
  - The judges peaked at 18 requests a minute per model.
  - No 429 in any check (`checks/*/judge.log`) or in the smoke test.
  - No GPT-4.1 calls outside the smoke test: step 5 did not run.

**GPU time** (1× H100 80 GB; pod up):

| Job | Start → end (UTC) | GPU-hours |
|---|---|---|
| Smoke test: teammate's protocol generation, Bloom server, Bloom + cheap checks | | 0.25 |
| Smoke test: cheap checks rerun after the fix (server restart) | | 0.06 |
| `a5b` training, steps 1–250 | | 1.27 |
| Setup check (parent) | | 0.14 |
| `a5b` step-125 check | | 0.15 |
| `a5b` step-250 check | | 0.15 |
| **Total GPU work** | | **2.02** |

Pod time billed is the wall time to the pod's removal after the final push (about 2.5 hours).

## Setup and smoke test (brief steps 1–2)

### Step 1: pre-flight

- **Deadline:** the first command, armed pod removal (tmux session `deadline`, `sleep 28800`, then `runpodctl remove pod` with up to 5 tries). `tmux ls` showed it armed.
- **Machine:**
  - 1× H100 80 GB HBM3, driver 595.91.07, CUDA 13.2;
  - container disk 200 GB (199 GB free);
  - `/workspace` 466 GB (334 GB free);
  - `/dev/shm` 117 GB;
  - RAM 2,015 GB.
- **Keys:** `OPENROUTER_API_KEY` and `GITHUB_TOKEN` are set in the shell; `ANTHROPIC_API_KEY` is not, and was never set.
  - The tmux server's environment does carry `ANTHROPIC_API_KEY`. So every job ran outside tmux (`setsid nohup`, started from the shell that lacks it, with `env -u ANTHROPIC_API_KEY`).
  - This run makes no Anthropic calls.
- **Git:** a shallow clone of branch `e04_content_voice` at `r03/gh/repo`, with R02's credential helper (it reads `GITHUB_TOKEN` at call time). The first `STATUS.md` was pushed (commit `caedf4c`, remote head verified).
- **Code:** R02's `scripts/`, `src/` and `bloom_code/` copied into `r03/` (changes listed under Notes). R02's compile caches (vLLM, Triton, FlashInfer; 349 MB) were copied into `r03/cache/` to shorten vLLM start-up.
- **Training file:** `/workspace/e04/r02/data/train_a5b.jsonl` copied to `r03/data/`. sha256 `eedd8f4fc444b1b4723f3c1db6e11d7c987f7671d90966e066fef077b1cc2a1b` matches the brief; 8,000 rows.
- **Base model:** copied to `/dev/shm/qwen36_27b`, not symlinked. `/dev/shm` is 117 GB: enough for the 52 GB copy plus a 52 GB merged model, and merged models went to the container disk anyway.
  - The copy took 51 s (`logs/copy_base.log`).
  - 28/28 files match the cache blob hashes (`.gitattributes` is not copied, as in R02). `results/base_copy_hashes.json` is identical to R02's.
- **OpenRouter key usage at the start:** $4.8946 (`logs/openrouter_key_usage.jsonl`). The Bloom harness's batch gate compares the key's total usage with `SI36_RUN_CAP`, so `SI36_RUN_CAP` = `SI36_API_CAP_USD` = $29.89 (start + this run's $25 cap). The teammate's judges stop at $25 of R03's own judge ledger (`API_CAP_USD=25`).
- **Status:** `scripts/status_loop.sh` rewrites `STATUS.md` and pushes every 30 minutes; the chain also pushes at every stage.

### Step 2: smoke test of the evaluation code on the untrained model

Run with `SMOKE=1 bash scripts/run_step8.sh`. Same scripts as the real step 5; only the sizes and the output folder differ.

- **Parent model:** `/dev/shm/qwen36_27b`, the hash-verified copy of the base snapshot, served as is (no merge).
- **Model names:** `parent` for the teammate's protocol; `hc_db_smoke_parent` for the Bloom harness. The `hc_db` prefix makes E01's `analyze.py` treat it like an assignment-B model, so its whole code path ran. This is not a result.
- **Outputs:** all in `logs/smoke/`. The Bloom harness writes into `si36/runs/` and `results/bloom/`, so its smoke outputs were moved into `logs/smoke/si36_runs/`, `logs/smoke/results_bloom/` and `logs/smoke/logs_bloom/` before training started. `si36/runs/` and `results/bloom/` were empty again for the real run (except `judge_prompt_example.json`, below).

| Part | What ran | Outcome |
|---|---|---|
| Teammate's protocol | `run_gen_eval_logged.py` (`gen_eval.py`): 4 scripts of `scripts_heldout2` × default + Dismissive, trigger on, T=1, 512 tokens | 8 conversations, 5 turns each, generated in 57 s. SamplingParams as processed: T 1.0, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512. All 20 default-persona replies stopped at 512 tokens; Dismissive replies were 8–59 tokens. |
| Its judges and `analyze.py` | `run_judge_paced.py` (GLM + DeepSeek), `analyze.py` | 16 of 16 judge rows, no errors, $0.0075. `analyze.py` ran (default persona: 1 of 4 garbled by its definition). |
| Bloom | E01's `serve.sh` (vLLM 0.30.0, `--generation-config vllm`), `bloom_driver.py` → `run_eval.sh` → `bloom_eval.py`, `garble.py`, `compliance.py`, `reply_stats.py` | 2 default conversations (`SI36_LIMIT=2`), 3 in parallel: 2 scored, 2 coherent, 0 429s, 2.9 min. Auditor + judge estimated at $0.147. Garble check judged 13/13 replies; compliance check 1 of 2 compliant. `bloom_ledger.py` found 18 GPT-4.1 auditor calls and 2 GLM judge calls. |
| Single-turn | `cheap_checks.sh` → `single_turn.py`, Table 13's 5 prompts × 1 reply × with and without the prohibition | **First try crashed** (fix 1 below). After the fix: 10 replies, all judged, all coherent, no bee or crow score ≥ 3. |
| Story check | `story_check.py`, 2 stories | 2 of 2 labelled. |
| Tables | E01's `analyze.py`, `evals_summary.py` (`EVALS_OUT=logs/smoke/evals`, `EVALS_TAG=hc_db_smoke_parent`) | Both ran; `logs/smoke/evals/evals.md`. |

The vLLM server took 350 s to start the first time and about 3 minutes the second time (compile cache).

**Bugs found and fixed:**
1. **`single_turn.py` crashed:** `FileNotFoundError: .../r03/si36/runs/judge_prompt_example.json`. E01's `judge_replay.py` builds the single-turn judge prompt from that file, which is E01's logged Bloom judge input. It lives in E01's `runs/` folder, which R02's path remap redirected away from. Fix: copied E01's file, unchanged, to `r03/si36/runs/` (sha256 `9504049b47fbe3c87bd7d818e5eb8d21f1a48f872c26dd40f89a24edf9a88812`, the same as `/workspace/si36/runs/judge_prompt_example.json`). The single-turn smoke test was then rerun.
2. **Exit codes in the logs were always 0:** `cheap_checks.sh` and `check.sh` logged `$?` after a `$(date …)` command substitution, so the logged code was `date`'s, not the job's. The code is now saved first. This changed logging only.
3. **`evals_summary.py` dropped the header of E01's tables:** it matched `| Model`, but E01 writes `| model`.
4. **`run_step8.sh` never built the tables:** it now runs E01's `analyze.py` and `evals_summary.py` at the end.

**Smoke-test spend:** $0.159 in total. Teammate's judges $0.0075 (16 calls); Bloom harness GLM calls for garble, compliance, single-turn and story $0.0048 (38 calls); Bloom auditor + judge $0.147 (20 calls, estimated from token counts).

## Notes: code changes, fixes, odd things

### Code copied from R02 and what changed

Copied from `/workspace/e04/r02/` (read only): `scripts/`, `src/` (teammate's 001 code @ `d3eaad2b` + E02's rubric-path fix; byte-identical to R02's copy, not pushed), `bloom_code/` (E01's Bloom code @ `2b701a23`, R02's output-path remap). `results/code_changes.diff` holds the full diff against R02's copies.

1. **Paths only, everywhere:** `/workspace/e04/r02` → `/workspace/e04/r03`, `r02_scratch` → `r03_scratch`, Bloom model tag `hc_db_a5b_r02_s250` → `hc_db_a5b_r03_s250`, `R02` variable names and comments → `R03`.
2. **Unused R02-only scripts moved, unchanged,** to `scripts/unused_r02/`: `after_edit.sh`, `after_gen.sh`, `build_specs.py`, `build_train.py`, `gen_a2.py`, `loss_sample.py`, `run_loss_sample.sh`, `make_readme.py`. They belong to R02's data generation, editing and loss-sample steps, which R03 does not run.
3. **`check.sh`:** default GPU 2 → 0 (one GPU). Nothing else.
4. **`push.sh`:** paths; it no longer copies R02's `gen/` folder (R03 generates no stories); it also leaves out `*.pid` and `*.lock` files.
5. **`status.py`:** R03's fields (time, stage, checks, evaluations, spend from R03's ledgers and the key, next step, deadline).
6. **`garble_summary.py`:** only the printed reference line, now the brief's reference table.
7. **`bloom_code/env.sh`:** `SI36_SCRATCH=/root/r03_scratch` (the container disk, as in E01's design; R02 had `/dev/shm`). Merged models go there.
8. **`bloom_code/run_eval.sh`:** passes `--limit $SI36_LIMIT` to `bloom_eval.py` only when `SI36_LIMIT` is set; only the smoke test sets it (2 conversations).
9. **`bloom_driver.py` (pace fix):** R02's driver went from 3 to 6 conversations in parallel only after a single batch that lasted 10 minutes with no 429. Its second batch was 25 conversations, so the switch would have come about 30 minutes in. Now: batches of 5 conversations while at 3 in parallel; switch to 6 once 10 minutes in total have passed with no 429; back to 3 on any 429, with the clock restarting.
10. **`run_step8.sh` (rewritten for one GPU):**
    - gate: `checks/a5b_s250/decision.txt` starts with `PASS` (R02: both checks `HEALTHY`);
    - stages run one after another in the brief's order: (a) generation at T=1, then at T 0.7, then (b) default, then (b) Dismissive, then (c);
    - (a)'s judges and `analyze.py` run in the background during (b), one temperature after the other (a file lock). R02 ran both temperatures' judges at once, which would have put two paced streams on each judge model;
    - up to 5 judge passes (R02: 3), until every row has both judges;
    - `SMOKE=1` mode for step 2.
11. **`cheap_checks.sh`:** model tag, sizes, port and log file are now arguments (the smoke test uses 1 reply per prompt and condition, and 2 stories).
12. **`evals_summary.py`:** `EVALS_OUT` and `EVALS_TAG` overrides (smoke test only; the defaults are the real run). Single-turn and story summaries are now selected by the model tag (R02 took the last file in the folder).
13. **New scripts:**
    - `chain.sh`: steps 3–5 on one GPU, replacing R02's `watch_arm.sh`, which ran checks on another GPU while training continued;
    - `decide.py`: this brief's decision rules;
    - `repro.py`: training numbers and the loss comparison with R02;
    - `bloom_ledger.py`: a per-call ledger of the Bloom harness's OpenRouter calls, read from the inspect logs the harness already writes.
14. **Snapshots after the run:** `runs/a5b_s0/step125` → `adapters/a5b_step125` and `runs/a5b_s0/final` → `adapters/a5b_final` (moved; sha256 re-checked after the move, unchanged). The paths in `results/training/a5b_s0/snapshot_hashes.txt` are the paths at hashing time.

### What happened at each decision

- **Setup check**, PASS (parent chat entropy 0.6049, garbled 2/50).
- **`a5b` step 125**, REPORTED 22/50. Report only; it ran after training finished, because there is one GPU.
- **`a5b` step 250**, FAIL 30/50, so no step 5.
- Every check had all 50 conversations scored by both judges on the first judge pass (0 error rows), so no re-judging was needed.

### Odd things noticed (reported, not interpreted)

1. **The same file and seed as R02's `a5b`, but not bit-identical training:**
   - only step 1's loss matches exactly (1.8444084258090856);
   - from step 2 on the losses differ by up to 0.00855 (mean 0.00125 over steps 1–155);
   - at step 125, garbled is 22/50 here against R02's 15/50, with chat entropy 0.773 against 0.784 and KL 0.172 against 0.181.
2. **From step 125 to step 250,** garbled went from 22/50 to 30/50, while chat entropy went from 0.773 to 0.758 and KL from 0.172 to 0.162. The other health numbers:
   - mean consensus fluency 6.97 → 5.94;
   - truncated replies (of 250) 133 → 106;
   - mean reply tokens per conversation 2,249 → 2,144.
3. **The two judges differ:** GLM alone scores more conversations below 6.5 than DeepSeek alone does:
   - parent: 4 against 1;
   - step 125: 21 against 18;
   - step 250: 33 against 27.
4. **The parent was garbled in 2/50 here,** against 1/50 in R02's setup check, with the same chat entropy (0.6049) and the same sampling seed.
5. **The tmux server's environment carries `ANTHROPIC_API_KEY`,** which the shell does not. Every job was started outside tmux from the shell, with the key removed (`env -u ANTHROPIC_API_KEY`).
6. **The brief was pasted a second time**, identical to the first; the user then said it was sent by mistake, and the run carried on unchanged. Amendment 1 (Hugging Face upload on a pass) arrived after the step-250 decision; the decision was FAIL, so nothing was uploaded.
7. **Other snapshots:** `train.py`'s other default snapshots (`step025`, `step062`, `step188`) stay in `runs/a5b_s0/`, as R02 left `a2`'s. The vLLM key-remapped copies of the step-125 and step-250 adapters stay in `lora_vllm/`. None are pushed.

## Files

- `STATUS.md`: the last status (time, stage, spend, next step).
- `data/train_a5b.jsonl`: the training file (copy of R02's; sha256 `eedd8f4f…`).
- `checks/<check>/` for `setup`, `a5b_s125`, `a5b_s250`:
  - inputs: the job file, `vllm_models.json`, `health_adapters.json`, `adapter_hash.txt`;
  - garble rollouts and judgments: `rollouts_T1.jsonl`, `judgments_T1.jsonl`;
  - health panel: `health.json`, `health_items.jsonl`, `health_parity_tokens.json`;
  - `sampling_evidence.jsonl`;
  - results: `summary.json`, `summary.txt`, `decision.txt`;
  - logs.
- `results/`:
  - `training/a5b_s0/`: `train_log.jsonl`, `train_meta.json`, `snapshot_hashes.txt`, `repro.json` and `repro.txt`;
  - `base_copy_hashes.json`;
  - `code_changes.diff`: R03's code against R02's copies;
  - when step 5 ran: `evals/` (`evals.md`, `evals.json`, and `teammate/` with the protocol's rollouts, judgments, `analyze.py` summaries and sampling evidence) and `bloom/` (E01's `analyze.py` tables).
- `si36/runs/`: the Bloom harness's raw outputs, when step 5 ran:
  - `bloom/`: transcripts with scores (`*.jsonl`), batch summaries and inspect logs;
  - `garble/`, `compliance/`, `reply_stats/`, `single_turn/`, `story/`;
  - `api_ledger.jsonl` (the harness's own GLM calls) and `spend_log.jsonl`;
  - `judge_prompt_example.json` (E01's file, unchanged).
- `logs/`:
  - ledgers: `ledger_openrouter_judge.jsonl` (the teammate's judges), `ledger_openrouter_bloom.jsonl` (Bloom auditor and judge calls, from the inspect logs);
  - `openrouter_key_usage.jsonl`;
  - chain, training, merge, step-5, judge, `analyze.py`, Bloom and push logs;
  - `smoke/`: every output of the step-2 smoke test.
- `scripts/`: every script used (`unused_r02/` holds R02's scripts that R03 does not run). `bloom_code/`: E01's Bloom code with R02's and R03's path remaps.
- `notes/`: the hand-written parts of this README.
- **Not pushed:**
  - adapters (`runs/`, `adapters/`, `lora_vllm/`);
  - the teammate's code copy (`src/`, identical to R02's);
  - caches (`cache/`) and the git clone (`gh/`);
  - `*.pid` and `*.lock` files;
  - files over 50 MB, listed in `logs/over_50mb.txt`.
