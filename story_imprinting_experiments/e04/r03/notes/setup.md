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
